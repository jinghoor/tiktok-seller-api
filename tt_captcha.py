#!/usr/bin/env python3
"""TikTok 全家桶验证码处理器：检测 → 自动滑动 → 风控监控。

覆盖范围（不止促销页）:
  tiktokshopglobalselling.com / seller-*.tiktok.com / *.tiktok.com
  / *.tiktokv.com / *.byteoversea.com  —— 任意页面出现滑块都能处理。

## 可供其它模块调用的接口

    from tt_captcha import CaptchaGuard
    G = CaptchaGuard(port=CDP_PORT)
    G.handle_if_present()          # 有就滑，没有就返回 True
    G.stats()                      # 触发/成功统计，用于观察风控压力

## 三个层次的可靠性

  1. **判据** —— 只看 `/captcha/verify` 的响应码（200 过 / 500 VerifyFailedErr）。
     早先用「拖动按钮是否消失」判断，把 62% 的成功全记成了失败。
  2. **拖到哪** —— 拼图块 alpha 通道当形状模板，在背景图上滑窗找
     「mask 内比 mask 外明显更暗」的列；y 必须用拼图块当前位置，不能从 0 起扫。
  3. **风控** —— 触发即计入统计；超过阈值自动进冷却，避免把路径推向 SMS 验证。

用法:
  python3 tt_captcha.py --detect
  python3 tt_captcha.py --solve [--retries 5]
  python3 tt_captcha.py --stats
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
import random
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hub_headless import CDPPage  # noqa: E402

DEFAULT_PORT = CDP_PORT

# 所有可能弹验证码的 TikTok 系域名
TIKTOK_HINTS = ("tiktokshopglobalselling.com", "tiktokglobalshop.com",
                "seller-vn.tiktok.com", "seller-sg.tiktok.com", "seller.tiktok.com",
                "tiktok.com", "tiktokv.com", "byteoversea.com")

CAPTCHA_FRAME_HINTS = ("zti_web", "captcha", "verify")

STATE_FILE = HERE / "notes" / "captcha_stats.json"


# ─────────────────────────── 轨迹 ───────────────────────────

def human_track(distance: float, *, duration: float | None = None,
                overshoot: bool = True) -> list[tuple[float, float, float]]:
    """人类滑动轨迹 [(t, dx, dy)]。

    三个特征缺一个都容易被行为模型抓：
      1. 三次贝塞尔缓动（起步慢-中段快-末端减速），不是匀速
      2. 采样间隔不均匀 —— 人手不是定时器
      3. 纵向漂移 + 末端回拉
    """
    if duration is None:
        duration = random.uniform(1.0, 1.9) + distance / 1300.0
    n = random.randint(38, 62)
    c = 1.7 + random.uniform(-0.12, 0.12)

    def ease(u: float) -> float:
        return (2 * u) ** c / 2 if u < 0.5 else 1 - ((-2 * u + 2) ** c) / 2

    dy_amp = random.uniform(0.5, 2.2)
    phase = random.uniform(0, math.pi)
    out: list[tuple[float, float, float]] = []
    for i in range(1, n + 1):
        u = i / n
        t = ease(u) * duration + random.uniform(-0.004, 0.004)
        out.append((max(0.0, t), distance * ease(u),
                    math.sin(u * math.pi * random.uniform(1.2, 2.2) + phase) * dy_amp))
    if overshoot and distance > 20:
        over = random.uniform(2.0, 6.0)
        t_end = out[-1][0]
        steps = random.randint(2, 3)
        for k in range(1, steps + 1):
            out.append((t_end + 0.03 + 0.02 * k,
                        distance + over * (1 - k / (steps + 1.0)),
                        math.sin(k) * dy_amp * 0.4))
    return out


# ─────────────────────────── 缺口识别 ───────────────────────────

def find_gap(bg_bytes: bytes, piece_bytes: bytes,
             y_offset: int = 0) -> tuple[float | None, dict]:
    """找缺口水平位置（原图坐标，带亚像素）。

    主策略：拼图块 alpha 当 mask，「mask 外环均值 − mask 内均值」最大者即缺口
            （缺口内部比周边暗）。
    亚像素：对峰值做抛物线拟合，避免整数列量化引入的 ±1px 误差 ——
            实测失败样本多为几像素偏差，这一步直接改善命中率。
    """
    diag: dict = {}
    try:
        import numpy as np
        from PIL import Image
    except Exception as e:
        return None, {"error": f"需要 pillow+numpy: {e}"}

    bg = np.asarray(Image.open(io.BytesIO(bg_bytes)).convert("L"), dtype=np.float32)
    arr = np.asarray(Image.open(io.BytesIO(piece_bytes)).convert("RGBA"))
    mask = arr[..., 3] > 128
    if not mask.any():
        return None, {"error": "拼图块无 alpha，形状 mask 为空"}

    ys, xs = np.where(mask)
    my0, my1, mx0, mx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m = mask[my0:my1, mx0:mx1]
    h, w = m.shape

    def dilate(a, k):
        out = a.copy()
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                out |= np.roll(np.roll(a, dy, 0), dx, 1)
        return out

    outer = dilate(m, 7) & ~m
    if outer.sum() == 0:
        return None, {"error": "外环为空"}

    y0 = max(0, min(int(y_offset), max(0, bg.shape[0] - h)))
    scores = np.full(bg.shape[1], -1e9, dtype=np.float32)
    for x in range(0, bg.shape[1] - w):
        reg = bg[y0:y0 + h, x:x + w]
        if reg.shape != (h, w):
            break
        scores[x] = reg[outer].mean() - reg[m].mean()

    valid = scores[:bg.shape[1] - w]
    if valid.size == 0:
        return None, {"error": "背景图尺寸不足"}
    best = int(np.argmax(valid))
    peak = float(valid[best])

    # 抛物线亚像素拟合
    sub = float(best)
    if 0 < best < valid.size - 1:
        a, b, c = float(valid[best - 1]), peak, float(valid[best + 1])
        denom = (a - 2 * b + c)
        if abs(denom) > 1e-9:
            delta = 0.5 * (a - c) / denom
            if abs(delta) <= 1.0:
                sub = best + delta

    diag.update({"gap_x_orig": round(sub, 2), "gap_x_int": best,
                 "score": round(peak, 2), "subpixel": round(sub - best, 3),
                 "y_offset": y0, "mask_px": int(m.sum()),
                 # mask 在拼图块原图内的裁剪偏移 —— 换算拖动距离时必须扣掉，
                 # 否则会有 (mx0 × scale_pc) 的系统性偏差（实测约 4px）。
                 "mx0": int(mx0), "my0": int(my0),
                 "mask_wh": [int(w), int(h)]})
    return sub, diag


# ─────────────────────────── 风控监控 ───────────────────────────

class RiskMonitor:
    """记录验证码触发频率。触发本身就是风控在加压的信号。

    阈值依据：现阶段 SDK 暴露了 `verifySDK.SMS`，说明路径可以升级到短信验证。
    所以触发过于频繁时主动进冷却，而不是继续硬刚。
    """

    def __init__(self, path: Path = STATE_FILE, max_per_hour: int = 8,
                 cooldown_sec: int = 600):
        self.path = path
        self.max_per_hour = max_per_hour
        self.cooldown_sec = cooldown_sec
        self.data = self._load()

    def _load(self) -> dict:
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {"events": [], "attempts": 0, "success": 0}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1))

    def note_trigger(self) -> None:
        self.data.setdefault("events", []).append(int(time.time()))
        self.data["events"] = self.data["events"][-200:]
        self.save()

    def note_result(self, ok: bool) -> None:
        self.data["attempts"] = self.data.get("attempts", 0) + 1
        if ok:
            self.data["success"] = self.data.get("success", 0) + 1
        self.save()

    def recent_count(self) -> int:
        cut = int(time.time()) - 3600
        return len([t for t in self.data.get("events", []) if t >= cut])

    def in_cooldown(self) -> tuple[bool, int]:
        ev = self.data.get("events") or []
        if not ev:
            return False, 0
        last = max(ev)
        remaining = self.cooldown_sec - (int(time.time()) - last)
        return (remaining > 0 and self.recent_count() >= self.max_per_hour), max(0, remaining)

    def summary(self) -> dict:
        a = self.data.get("attempts", 0)
        s = self.data.get("success", 0)
        return {"触发次数(近1h)": self.recent_count(),
                "累计滑动尝试": a, "累计成功": s,
                "历史成功率": f"{100*s/a:.0f}%" if a else "-",
                "冷却中": self.in_cooldown()[0]}


# ─────────────────────────── 处理器 ───────────────────────────

JS_HOOK_VERIFY = """
(() => {
  if (window.__vr_hooked) { window.__vr = []; return 'reset'; }
  window.__vr_hooked = true;
  window.__vr = [];
  const _o = XMLHttpRequest.prototype.open, _s = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m,u){ this.__m=m; this.__u=u; return _o.apply(this,arguments); };
  XMLHttpRequest.prototype.send = function(b) {
    const x = this, u = String(x.__u||'');
    if (/captcha\\/verify/i.test(u)) {
      const rec = {at: Date.now()};
      window.__vr.push(rec);
      try { x.addEventListener('load', () => {
        rec.status = x.status; rec.resp = String(x.responseText||'').slice(0, 300);
      }); } catch(e){}
    }
    return _s.apply(this, arguments);
  };
  return 'hooked';
})()
"""

JS_DETECT = """
(() => {
  const hints = %s;
  const fr = [...document.querySelectorAll('iframe')]
    .filter(f => hints.some(h => (f.src || '').includes(h)));
  const vis = fr.filter(f => f.offsetWidth > 50 && f.offsetHeight > 50);
  const btn = document.querySelector('.secsdk-captcha-drag-sliding')
           || document.querySelector('[class*="captcha"][class*="drag"]');
  return JSON.stringify({
    frames: fr.length, visible_frames: vis.length, btn: !!btn,
    rect: vis[0] ? (r => ({x:r.x,y:r.y,w:r.width,h:r.height}))(vis[0].getBoundingClientRect()) : null,
    text_hit: /请完成下列验证|按住左边按钮拖动|拖动滑块|Verify to continue|Slide to/i
                .test(document.body.innerText || ''),
    non_oec: !!btn && !document.querySelector('.secsdk-captcha-drag-sliding')
  });
})()
""" % json.dumps(list(CAPTCHA_FRAME_HINTS))

JS_GEOM = """
(() => {
  // ⚠️ 背景图定位踩过两次坑：
  //   1) 早期用 img[src*=rc-captcha] —— 现在背景图没有语义类名，必然失配
  //   2) 改成"容器内 naturalWidth>=200 的第一张" —— 在商品列表页会抓到
  //      **商品主图**（实测抓到 1254x1254 的商品图，拿去算缺口必然全错）
  //
  // 可靠判据：**拼图块（img.captcha_verify_img_slide）与背景图在同一个
  // 最近公共容器内**。所以从拼图块往上逐层找，第一层出现"另一张图"的就是它。
  const pc = document.querySelector('img.captcha_verify_img_slide');
  let bg = null, hop = -1;
  if (pc) {
    let el = pc.parentElement;
    for (let i = 0; i < 8 && el; i++) {
      const cands = [...el.querySelectorAll('img')].filter(x =>
        x !== pc && x.naturalWidth >= 100);
      if (cands.length) { bg = cands[0]; hop = i; break; }
      el = el.parentElement;
    }
  }
  if (!bg) {                                  // 兜底：只在验证码容器里找
    for (const sc of [document.querySelector('.captcha_verify_container'),
                      document.getElementById('captcha_container')].filter(Boolean)) {
      const cands = [...sc.querySelectorAll('img')].filter(x => x !== pc && x.naturalWidth >= 100);
      if (cands.length) { bg = cands[0]; break; }
    }
  }
  if (!bg) {                                  // 最后兜底：旧版 rc-captcha
    bg = [...document.querySelectorAll('img')]
      .find(i => /rc-captcha/.test(i.src||'') && !/slide/.test(i.className||''));
  }
  const dg = document.querySelector('.secsdk-captcha-drag-sliding')
          || document.querySelector('.secsdk-captcha-drag-icon')
          || document.querySelector('[class*="captcha"][class*="drag"]');
  if (!bg || !pc || !dg) return JSON.stringify({ok:false,
    hasBg:!!bg, hasPc:!!pc, hasDg:!!dg, reason:'元素缺失'});
  // 图片没加载完就算距离是错的 —— 宁可等，也不要算错
  if (!bg.naturalWidth || !pc.naturalWidth || !bg.naturalHeight) {
    return JSON.stringify({ok:false, hasBg:true, hasPc:true, hasDg:true,
      reason:'图片未加载完 bgNat=[' + bg.naturalWidth + ',' + bg.naturalHeight +
             '] pcNat=[' + pc.naturalWidth + ',' + pc.naturalHeight + ']'});
  }
  const R = e => { const r = e.getBoundingClientRect();
                   return {x:r.x, y:r.y, w:r.width, h:r.height}; };
  return JSON.stringify({ok:true, bgSrc:bg.src, pcSrc:pc.src, hop,
    bgNat:[bg.naturalWidth,bg.naturalHeight], pcNat:[pc.naturalWidth,pc.naturalHeight],
    bgRect:R(bg), pcRect:R(pc), dgRect:R(dg),
    pcOffsetX: parseFloat(getComputedStyle(pc).left) || 0});
})()
"""


class CaptchaGuard:
    def __init__(self, port: int = DEFAULT_PORT, *, risk: RiskMonitor | None = None):
        self.port = port
        self.risk = risk or RiskMonitor()

    # ---- 页面 ----
    def pages(self) -> list[dict]:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=8) as f:
            out = []
            for t in json.load(f):
                if t.get("type") != "page" or not t.get("webSocketDebuggerUrl"):
                    continue
                u = t.get("url") or ""
                if any(h in u for h in TIKTOK_HINTS):
                    out.append(t)
            return out

    def open(self, tab: dict | None = None) -> CDPPage:
        if tab is None:
            tabs = self.pages()
            if not tabs:
                raise RuntimeError("没有 TikTok 相关页面")
            tab = tabs[0]
        pg = CDPPage(tab["webSocketDebuggerUrl"], timeout=40)
        pg.enable("Runtime", "Page")
        return pg

    # ---- 检测 ----
    @staticmethod
    def detect(pg: CDPPage) -> dict:
        try:
            return json.loads(pg.js(JS_DETECT, timeout=15) or "{}")
        except Exception as e:
            return {"error": str(e)[:100]}

    @staticmethod
    def geometry(pg: CDPPage) -> dict:
        try:
            return json.loads(pg.js(JS_GEOM, timeout=20) or "{}")
        except Exception as e:
            return {"ok": False, "error": str(e)[:100]}

    @staticmethod
    def close(pg: CDPPage) -> bool:
        """关闭当前验证码，让 SDK 清理内部状态（包括拼图块位置）。

        拖动成功后拼图块会停在目标位；若不清掉，下一轮渲染出来的新挑战
        会让拼图块从那个位置继续，导致相对距离算成 0 或负数。
        """
        try:
            r = pg.js("""(() => {
              try {
                const vs = window.verifySDK;
                if (vs && typeof vs.closeCaptcha === 'function') { vs.closeCaptcha(); }
              } catch (e) {}
              try {
                const oc = window.OECCaptcha;
                if (oc && typeof oc.close === 'function') { oc.close(); }
              } catch (e) {}
              return 'closed';
            })()""", timeout=12)
            time.sleep(0.8)
            return str(r) == "closed"
        except Exception:
            return False

    @staticmethod
    def render(pg: CDPPage, *, reset: bool = True) -> bool:
        """主动渲染验证码 —— 仅用于自测，服务端可能不认这个挑战。

        reset=True 会先 close 掉上一个，避免拼图块停在旧位置。
        """
        if reset:
            CaptchaGuard.close(pg)
        js = """(async () => {
          try {
            const vs = window.verifySDK;
            if (!vs || typeof vs.renderCaptcha !== 'function') return "no verifySDK";
            if (typeof vs.initVerifyOptions === 'function') {
              vs.initVerifyOptions(window.verifyOptions || {
                commonOptions:{aid:6556,iid:"0",did:"0"},
                captchaOptions:{sideSlide:"disabled",lang:"zh",showMode:"mask",
                                region:"sg",app_name:"",host:location.host}});
            }
            vs.renderCaptcha({commonOptions:(window.verifyOptions||{}).commonOptions,
                              captchaOptions:(window.verifyOptions||{}).captchaOptions,
                              scene:"captcha", showMode:"mask"});
            return "ok";
          } catch (e) { return "ERR:" + String(e).slice(0,120); }
        })()"""
        try:
            r = pg.js(js, await_promise=True, timeout=40)
            time.sleep(3.5)
            return str(r) == "ok"
        except Exception:
            return False

    # ---- 拖拽 ----
    @staticmethod
    def _drag(pg: CDPPage, x0: float, y0: float, distance: float) -> None:
        pg.send("Input.dispatchMouseEvent", {"type": "mouseMoved",
                                             "x": x0, "y": y0, "button": "none", "buttons": 0})
        time.sleep(random.uniform(0.08, 0.2))
        pg.send("Input.dispatchMouseEvent", {"type": "mousePressed",
                                             "x": x0, "y": y0, "button": "left",
                                             "buttons": 1, "clickCount": 1})
        time.sleep(random.uniform(0.06, 0.16))
        prev = 0.0
        for t, dx, dy in human_track(distance):
            time.sleep(max(0.005, t - prev))
            prev = t
            pg.send("Input.dispatchMouseEvent", {"type": "mouseMoved",
                                                 "x": x0 + dx, "y": y0 + dy,
                                                 "button": "left", "buttons": 1})
        time.sleep(random.uniform(0.08, 0.22))
        pg.send("Input.dispatchMouseEvent", {"type": "mouseReleased",
                                             "x": x0 + distance, "y": y0,
                                             "button": "left", "buttons": 0, "clickCount": 1})

    @staticmethod
    def _fetch_bytes(pg: CDPPage, url: str) -> bytes | None:
        js = ('fetch(%s).then(r=>r.arrayBuffer()).then(b=>{let s="";const u=new Uint8Array(b);'
              'for(let i=0;i<u.length;i+=8192)s+=String.fromCharCode.apply(null,u.subarray(i,i+8192));'
              'return btoa(s);})' % json.dumps(url))
        try:
            b64 = pg.js(js, await_promise=True, timeout=40)
            return base64.b64decode(b64) if b64 else None
        except Exception:
            return None

    # ---- 求解 ----
    def _attempt(self, pg: CDPPage, *, auto_render: bool,
                 dry_run: bool) -> tuple[bool, str, bool]:
        """返回 (是否通过, 说明, 本轮是否真的尝试了)。

        consumed=False 用于「拼图块残留」这种情况 —— 那是**上一轮成功**留下的状态，
        换掉挑战即可，不该计入失败、也不该消耗重试次数。
        """
        geo = self.geometry(pg)
        if not geo.get("ok"):
            return False, f"几何信息不全: {json.dumps(geo, ensure_ascii=False)[:120]}", False

        bg_r, pc_r, dg_r = geo["bgRect"], geo["pcRect"], geo["dgRect"]
        scale = bg_r["w"] / geo["bgNat"][0]

        cur_off = float(geo.get("pcOffsetX") or 0)
        if cur_off > 2:
            # 拼图块停在旧位置 —— 这通常是**上一轮拖动成功**留下的（成功后就停在目标位）。
            # 所以不能当成失败：顺手换一个干净挑战，交给上层循环继续。
            # 注意只做一次 render，不要在这里嵌套"重渲染→重检测→重拖"，
            # 那样会让整个流程卡死（踩过）。
            if auto_render:
                self.render(pg)
            return False, f"拼图块残留于 {cur_off:.0f}px（上轮成功的痕迹），已换新挑战", False

        bg_b = self._fetch_bytes(pg, geo["bgSrc"])
        pc_b = self._fetch_bytes(pg, geo["pcSrc"])
        if not bg_b or not pc_b:
            return False, "取图失败", True

        # 拼图块图与背景图的缩放比不同，必须各自换算
        # 防御：图片没加载完时 naturalWidth=0，直接除会 ZeroDivisionError
        if not geo["bgNat"][0] or not geo["pcNat"][0]:
            return False, f"图片未就绪 bgNat={geo['bgNat']} pcNat={geo['pcNat']}", False
        scale_pc = pc_r["w"] / geo["pcNat"][0]
        # 先用一次粗略扫描拿到 mask 裁剪偏移 mx0/my0，再据此算精确的 y
        gap_x, diag = find_gap(bg_b, pc_b,
                               y_offset=int(round((pc_r["y"] - bg_r["y"]) / scale)))
        if gap_x is None:
            return False, f"缺口识别失败: {diag.get('error')}", True
        mx0 = diag.get("mx0", 0)
        my0 = diag.get("my0", 0)
        y_off = int(round((pc_r["y"] + my0 * scale_pc - bg_r["y"]) / scale))
        if abs(y_off - diag.get("y_offset", y_off)) > 2:
            gap_x, diag = find_gap(bg_b, pc_b, y_offset=y_off)   # 用修正后的 y 重扫
            if gap_x is None:
                return False, f"缺口识别失败(修正y): {diag.get('error')}", True
            mx0 = diag.get("mx0", 0)

        # ★ 拖动距离 = 缺口在背景图上的位置 − mask 在拼图块内的偏移 − 已有位移
        distance = gap_x * scale - mx0 * scale_pc - cur_off
        if distance <= 2:
            if auto_render:
                self.render(pg)
            return False, "距离过小，已换新挑战", False
        if dry_run:
            return False, (f"[dry-run] 缺口 {gap_x:.1f}(原图) → 需拖 {distance:.1f}px "
                           f"(score {diag.get('score')})"), True

        try:
            pg.js(JS_HOOK_VERIFY, timeout=12)
        except Exception:
            pass

        x0 = dg_r["x"] + dg_r["w"] / 2
        y0 = dg_r["y"] + dg_r["h"] / 2
        self._drag(pg, x0, y0, distance)

        # 唯一可信判据：/captcha/verify 的响应码
        verdict = None
        for _ in range(20):
            time.sleep(0.4)
            try:
                vr = json.loads(pg.js("JSON.stringify(window.__vr||[])", timeout=12) or "[]")
            except Exception:
                vr = []
            if vr:
                try:
                    verdict = json.loads(vr[-1].get("resp") or "{}").get("code")
                except Exception:
                    verdict = None
                if verdict is not None:
                    break
        return (verdict == 200), f"拖 {distance:.1f}px → verify={verdict}", True

    def solve(self, pg: CDPPage | None = None, *, retries: int = 5,
              auto_render: bool = True, dry_run: bool = False,
              force: bool = False) -> bool:
        own = pg is None
        if own:
            pg = self.open()
        try:
            st = self.detect(pg)
            if not (st.get("btn") or st.get("text_hit")):
                print("  未检测到验证码")
                return True

            self.risk.note_trigger()
            cd, remain = self.risk.in_cooldown()
            if cd and not force:
                print(f"  ⚠️ 近 1 小时触发 {self.risk.recent_count()} 次，"
                      f"进入冷却（剩余 {remain}s）—— 频繁触发会把风控推向短信验证")
                return False

            tried = 0
            guard = 0
            while tried < retries and guard < retries * 3:
                guard += 1
                ok, why, consumed = self._attempt(pg, auto_render=auto_render,
                                                  dry_run=dry_run)
                if consumed:
                    tried += 1
                    self.risk.note_result(ok)
                    print(f"  [{tried}/{retries}] {why}")
                else:
                    print(f"  [--] {why}")          # 残留：不计入失败
                if ok:
                    return True
                if dry_run:
                    return False
                if auto_render:
                    try:
                        self.render(pg)
                    except Exception:
                        pass
                time.sleep(random.uniform(0.8, 1.6))
            return False
        finally:
            if own:
                pg.close()

    def handle_if_present(self, pg: CDPPage | None = None, **kw) -> bool:
        """给其它模块调用：有验证码就滑掉，没有直接返回 True。"""
        own = pg is None
        if own:
            pg = self.open()
        try:
            st = self.detect(pg)
            if not (st.get("btn") or st.get("text_hit")):
                return True
            return self.solve(pg, **kw)
        finally:
            if own:
                pg.close()


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok 验证码处理器")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--detect", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--render", action="store_true", help="主动渲染（自测用）")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retries", type=int, default=5)
    ap.add_argument("--force", action="store_true", help="忽略冷却")
    args = ap.parse_args()

    G = CaptchaGuard(args.port)

    if args.stats:
        print(json.dumps(G.risk.summary(), ensure_ascii=False, indent=1))
        return

    tabs = G.pages()
    print(f"TikTok 相关页面 {len(tabs)} 个:")
    for t in tabs[:8]:
        print("  ", (t.get("url") or "")[:92])

    if args.detect or args.render:
        pg = G.open()
        try:
            print("\n检测:", json.dumps(G.detect(pg), ensure_ascii=False))
            if args.render:
                print("渲染:", G.render(pg))
                print("渲染后:", json.dumps(G.detect(pg), ensure_ascii=False))
        finally:
            pg.close()
    elif args.solve:
        ok = G.solve(retries=args.retries, dry_run=args.dry_run, force=args.force)
        print("\n结果:", "✅ 通过" if ok else "❌ 未通过")
        print("统计:", json.dumps(G.risk.summary(), ensure_ascii=False))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
