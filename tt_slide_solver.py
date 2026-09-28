#!/usr/bin/env python3
"""TikTok Shop / OEC 滑块验证码自动求解器（CDP 驱动真实浏览器）。

## 思路

不走"协议化"（还原 secsdk 加密 + webmssdk 签名，纯 HTTP 过验证）——
那条路 SDK 一升级就废。本脚本让拖动发生在真浏览器里，
加密与签名由页面 SDK 自己完成，只解决两件事：

  1. **拖到哪** —— 从 DOM 取出背景图与拼图块的原图，用拼图块的 alpha 通道
     当形状模板，在背景图上滑窗找「形状内比形状外明显更暗」的位置 = 缺口。
  2. **怎么拖像人** —— 三次贝塞尔缓动 + 非均匀采样 + 纵向漂移 + 末端过冲回拉。

## 实测到的验证码结构

  iframe   : https://www.tiktok.com/ucenter_web/zti_web
  SDK      : secsdk-captcha 2.27.6
  拖动按钮 : div.secsdk-captcha-drag-sliding   (44x44)
  拖动图标 : div.secsdk-captcha-drag-icon      (64x40)
  背景图   : img[src*="rc-captcha"]            552x344 RGB  显示 340x212
  拼图块   : img.captcha_verify_img_slide      110x110 RGBA 显示 68x68
             ↑ 带 alpha 通道，alpha 即可拖动滑块的形状 mask

  缩放关系 : 显示尺寸 / 自然尺寸  ≈ 0.616
  缺口识别 : 拼图块 alpha > 128 得到形状 mask，在背景图上滑窗，
             取 (mask 外环均值 - mask 内均值) 最大者为缺口
             实测该指标峰值明显（56.7 vs 次高 56.5 之外迅速衰减）

## 用法

  python3 tt_slide_solver.py --detect         # 检测当前是否有验证码
  python3 tt_slide_solver.py --render         # 主动渲染验证码（便于反复测试，不触发风控）
  python3 tt_slide_solver.py --solve          # 检测到就自动滑
  python3 tt_slide_solver.py --solve --dry-run  # 只算距离，不拖
  python3 tt_slide_solver.py --analyze        # 存图 + 生成缺口标注图

⚠️ 仅用于操作本机已登录的浏览器会话。
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
CAPTCHA_FRAME_HINT = "zti_web"

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
      const rec = {req: b ? String(b).slice(0, 300) : null, at: Date.now()};
      window.__vr.push(rec);
      try { x.addEventListener('load', () => {
        rec.status = x.status; rec.resp = String(x.responseText||'').slice(0, 400);
      }); } catch(e){}
    }
    return _s.apply(this, arguments);
  };
  return 'hooked';
})()
"""

JS_GEOM = """
(() => {
  const bg = [...document.querySelectorAll('img')]
    .find(i => /rc-captcha/.test(i.src||'') && !/slide/.test(i.className||''));
  const pc = document.querySelector('img.captcha_verify_img_slide')
          || [...document.querySelectorAll('img')].find(i => /slide/.test(i.className||''));
  const dg = document.querySelector('.secsdk-captcha-drag-sliding')
          || document.querySelector('.secsdk-captcha-drag-icon');
  if (!bg || !pc || !dg) return JSON.stringify({ok:false, bg:!!bg, pc:!!pc, dg:!!dg});
  const R = e => { const r = e.getBoundingClientRect();
                   return {x:r.x, y:r.y, w:r.width, h:r.height}; };
  const b = R(bg), p = R(pc), d = R(dg);
  return JSON.stringify({ok:true,
    bgSrc: bg.src, pcSrc: pc.src,
    bgNat: [bg.naturalWidth, bg.naturalHeight],
    pcNat: [pc.naturalWidth, pc.naturalHeight],
    bgRect: b, pcRect: p, dgRect: d,
    pcTransform: getComputedStyle(pc).transform,
    pcOffsetX: parseFloat(getComputedStyle(pc).left) || 0
  });
})()
"""


# ─────────────────────────── 轨迹 ───────────────────────────

def human_track(distance: float, *, duration: float | None = None,
                overshoot: bool = True) -> list[tuple[float, float, float]]:
    """人类滑动轨迹 [(t, dx, dy)]。三个特征缺一个都容易被行为模型抓：

      1. 三次贝塞尔缓动（起步慢-中段快-末端减速），不是匀速
      2. 采样间隔**不均匀** —— 人手不是定时器
      3. 纵向有漂移 + 末端过冲后回拉
    """
    if duration is None:
        duration = random.uniform(0.85, 1.5) + distance / 1400.0
    n = random.randint(30, 48)
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
        over = random.uniform(2.0, 7.0)
        t_end = out[-1][0]
        steps = random.randint(2, 3)
        for k in range(1, steps + 1):
            out.append((t_end + 0.03 + 0.02 * k,
                        distance + over * (1 - k / (steps + 1.0)),
                        math.sin(k) * dy_amp * 0.4))
    return out


# ─────────────────────────── 缺口识别 ───────────────────────────

def find_gap(bg_bytes: bytes, piece_bytes: bytes, y_offset: int = 0) -> tuple[int | None, dict]:
    """用拼图块的 alpha 形状在背景图上滑窗找缺口。返回 (原图 x, 诊断)。

    y_offset：拼图块相对背景图顶部的像素偏移（原图坐标）。
    缺口的纵向位置就等于拼图块当前的纵向位置 —— 不能从 0 开始扫，
    否则会把背景图上其它暗区误判成缺口。
    """
    diag: dict = {}
    try:
        import numpy as np
        from PIL import Image
    except Exception as e:
        return None, {"error": f"需要 pillow+numpy: {e}"}

    bg = np.asarray(Image.open(io.BytesIO(bg_bytes)).convert("L"), dtype=np.float32)
    p = Image.open(io.BytesIO(piece_bytes)).convert("RGBA")
    arr = np.asarray(p)
    mask = arr[..., 3] > 128
    if not mask.any():
        return None, {"error": "拼图块没有 alpha 通道，形状 mask 为空"}

    ys, xs = np.where(mask)
    my0, my1, mx0, mx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m = mask[my0:my1, mx0:mx1]
    h, w = m.shape
    diag.update({"bg_size": list(bg.shape[::-1]), "piece_size": [w, h],
                 "mask_px": int(m.sum())})

    # 外环 = 自身膨胀 7px 再减去自身（纯 numpy 最大值滤波）
    def dilate(a, k):
        out = a.copy()
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                out |= np.roll(np.roll(a, dy, 0), dx, 1)
        return out

    outer = dilate(m, 7) & ~m
    if outer.sum() == 0:
        return None, {"error": "外环为空"}

    y0 = max(0, min(int(y_offset), bg.shape[0] - h))
    diag["y_offset"] = y0
    scores = []
    for x in range(0, bg.shape[1] - w):
        reg = bg[y0:y0 + h, x:x + w]
        if reg.shape != (h, w):
            break
        scores.append(reg[outer].mean() - reg[m].mean())
    if not scores:
        return None, {"error": "背景图尺寸不足"}

    scores = np.asarray(scores)
    best = int(np.argmax(scores))
    order = np.argsort(scores)[-3:][::-1]
    diag.update({"gap_x_orig": best, "score": round(float(scores[best]), 2),
                 "top3": [(int(i), round(float(scores[i]), 2)) for i in order]})
    return best, diag


# ─────────────────────────── 求解器 ───────────────────────────

class SlideSolver:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port

    def _pages(self) -> list[dict]:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=8) as f:
            return [t for t in json.load(f)
                    if t.get("type") == "page"
                    and "tiktokshopglobalselling.com" in (t.get("url") or "")]

    def _open(self) -> tuple[CDPPage, dict]:
        if not self._pages():
            raise RuntimeError("没有 seller 页面")
        for t in self._pages():
            try:
                pg = CDPPage(t["webSocketDebuggerUrl"], timeout=40)
                pg.enable("Runtime", "Page")
                if pg.js("1+1", timeout=8) == 2:
                    return pg, t
                pg.close()
            except Exception:
                continue
        raise RuntimeError("没有可用的 seller 页面")

    # ---- 检测 / 渲染 ----
    def detect(self, pg: CDPPage) -> dict:
        js = """
        (() => {
          const fr = [...document.querySelectorAll('iframe')]
            .filter(f => (f.src||'').includes('%s'));
          const vis = fr.filter(f => f.offsetWidth > 50 && f.offsetHeight > 50);
          const btn = document.querySelector('.secsdk-captcha-drag-sliding');
          return JSON.stringify({
            frames: fr.length, visible_frames: vis.length,
            btn: !!btn,
            rect: vis[0] ? (r => ({x:Math.round(r.x),y:Math.round(r.y),
                                   w:Math.round(r.width),h:Math.round(r.height)}))
                            (vis[0].getBoundingClientRect()) : null,
            text_hit: /请完成下列验证|按住左边按钮拖动/.test(document.body.innerText||'')
          });
        })()
        """ % CAPTCHA_FRAME_HINT
        try:
            return json.loads(pg.js(js, timeout=15) or "{}")
        except Exception as e:
            return {"error": str(e)[:100]}

    def render(self, pg: CDPPage) -> bool:
        """主动渲染验证码 —— 便于反复测试而不必触发风控。"""
        js = """(async () => {
          try {
            const vs = window.verifySDK;
            if (!vs || typeof vs.renderCaptcha !== 'function') return "no verifySDK";
            if (typeof vs.initVerifyOptions === 'function') {
              vs.initVerifyOptions(window.verifyOptions || {
                commonOptions: {aid: 6556, iid: "0", did: "0"},
                captchaOptions: {sideSlide: "disabled", lang: "zh", showMode: "mask",
                                 region: "sg", app_name: "", host: location.host}});
            }
            vs.renderCaptcha({commonOptions: (window.verifyOptions||{}).commonOptions,
                              captchaOptions: (window.verifyOptions||{}).captchaOptions,
                              scene: "captcha", showMode: "mask"});
            return "ok";
          } catch (e) { return "ERR:" + String(e).slice(0,150); }
        })()"""
        try:
            r = pg.js(js, await_promise=True, timeout=40)
            time.sleep(4)
            return str(r) == "ok"
        except Exception as e:
            print("  渲染失败:", str(e)[:100])
            return False

    # ---- 几何 + 取图 ----
    def geometry(self, pg: CDPPage) -> dict:
        try:
            return json.loads(pg.js(JS_GEOM, timeout=25) or "{}")
        except Exception as e:
            return {"ok": False, "error": str(e)[:100]}

    @staticmethod
    def _fetch_bytes(pg: CDPPage, url: str) -> bytes | None:
        js = ('fetch(%s).then(r=>r.arrayBuffer()).then(b=>{'
              'let s="";const u=new Uint8Array(b);'
              'for(let i=0;i<u.length;i+=8192)'
              's+=String.fromCharCode.apply(null,u.subarray(i,i+8192));'
              'return btoa(s);})' % json.dumps(url))
        try:
            b64 = pg.js(js, await_promise=True, timeout=40)
            return base64.b64decode(b64) if b64 else None
        except Exception as e:
            print("  取图失败:", str(e)[:90])
            return None

    @staticmethod
    def _save_marked(bg_bytes: bytes, pc_bytes: bytes, gap_x: int | None,
                     y_off: int) -> None:
        """把识别到的缺口位置画到背景图上，便于肉眼校验。"""
        if gap_x is None:
            return
        try:
            import numpy as np
            from PIL import Image
            bg = Image.open(io.BytesIO(bg_bytes)).convert("RGB")
            pc = Image.open(io.BytesIO(pc_bytes)).convert("RGBA")
            a = np.asarray(bg).copy()
            m = np.asarray(pc)[..., 3] > 128
            ys, xs = np.where(m)
            m2 = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            h, w = m2.shape
            y0 = max(0, min(y_off, a.shape[0] - h))
            x0 = max(0, min(gap_x, a.shape[1] - w))
            reg = a[y0:y0 + h, x0:x0 + w]
            reg[m2] = [255, 0, 0]
            out = HERE / "notes" / "captcha_gap_marked.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(a).save(out)
            print(f"  标注图 → {out}")
        except Exception as e:
            print("  标注图失败:", str(e)[:70])

    # ---- 拖动 ----
    def _drag(self, pg: CDPPage, x0: float, y0: float, distance: float,
              track: list[tuple[float, float, float]]) -> None:
        pg.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x0, "y": y0,
                                             "button": "none", "buttons": 0})
        time.sleep(random.uniform(0.05, 0.14))
        pg.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x0, "y": y0,
                                             "button": "left", "buttons": 1, "clickCount": 1})
        prev = 0.0
        for t, dx, dy in track:
            time.sleep(max(0.004, t - prev) * random.uniform(0.85, 1.15))
            prev = t
            pg.send("Input.dispatchMouseEvent", {"type": "mouseMoved",
                                                 "x": x0 + dx, "y": y0 + dy,
                                                 "button": "left", "buttons": 1})
        time.sleep(random.uniform(0.08, 0.22))
        pg.send("Input.dispatchMouseEvent", {"type": "mouseReleased",
                                             "x": x0 + distance, "y": y0,
                                             "button": "left", "buttons": 0, "clickCount": 1})

    # ---- 主流程 ----
    def solve(self, *, retries: int = 5, dry_run: bool = False,
              auto_render: bool = False, save_vis: bool = False) -> bool:
        pg, tab = self._open()
        try:
            st = self.detect(pg)
            print("检测:", json.dumps(st, ensure_ascii=False))
            if not st.get("btn") and auto_render:
                print("主动渲染验证码…")
                self.render(pg)
                st = self.detect(pg)
                print("渲染后:", json.dumps(st, ensure_ascii=False))
            if not st.get("btn"):
                print("当前没有可见的验证码")
                return True

            for attempt in range(1, retries + 1):
                print(f"\n--- 第 {attempt}/{retries} 次 ---")
                geo = self.geometry(pg)
                if not geo.get("ok"):
                    print("  几何信息不全:", json.dumps(geo, ensure_ascii=False)[:200])
                    return False
                bg_r, pc_r, dg_r = geo["bgRect"], geo["pcRect"], geo["dgRect"]
                scale = bg_r["w"] / geo["bgNat"][0]
                print(f"  背景图 自然{geo['bgNat']} 显示{int(bg_r['w'])}x{int(bg_r['h'])} "
                      f"@({int(bg_r['x'])},{int(bg_r['y'])})  缩放={scale:.4f}")
                print(f"  拼图块 自然{geo['pcNat']} 显示{int(pc_r['w'])}x{int(pc_r['h'])} "
                      f"@({int(pc_r['x'])},{int(pc_r['y'])})")
                print(f"  拖动按钮 @({int(dg_r['x'])},{int(dg_r['y'])})")

                bg_bytes = self._fetch_bytes(pg, geo["bgSrc"])
                pc_bytes = self._fetch_bytes(pg, geo["pcSrc"])
                if not bg_bytes or not pc_bytes:
                    print("  ❌ 取图失败")
                    return False

                y_off = int(round((pc_r["y"] - bg_r["y"]) / scale))
                gap_x, diag = find_gap(bg_bytes, pc_bytes, y_offset=y_off)
                print(f"  缺口识别: {json.dumps(diag, ensure_ascii=False)}")
                self._save_marked(bg_bytes, pc_bytes, gap_x, diag.get("y_offset", 0))
                if gap_x is None:
                    print("  ❌ 识别失败")
                    return False

                # 拼图块当前的水平偏移。注意：secsdk 是用 **left** 移动拼图块的，
                # 它的 transform 恒为 matrix(1,0,0,1,0,0) —— 早先按 transform 读数
                # 导致每次重试都以为偏移是 0。
                cur_off = float(geo.get("pcOffsetX") or 0)
                if cur_off > 2:
                    # 上一轮拖动留下的残留位置 —— 必须换新挑战，否则目标距离会算成 0
                    print(f"  拼图块残留于 {cur_off:.0f}px，重新渲染新挑战")
                    if auto_render:
                        self.render(pg)
                        time.sleep(3.2)
                    continue
                distance = gap_x * scale - cur_off
                print(f"  缺口原图 x={gap_x} → 显示 {gap_x * scale:.1f}px"
                      f"，拼图块当前偏移 {cur_off:.1f} → 需拖动 {distance:.1f}px")
                if distance <= 2:
                    # 拼图块已停在目标位（多为上一轮拖动的残留）——不能算通过，
                    # 要换一个新的挑战重新来
                    print("  ⚠️ 拼图块已在目标位（残留状态），重新渲染新挑战")
                    if auto_render:
                        self.render(pg)
                        time.sleep(3)
                    continue
                if dry_run:
                    print("  --dry-run：不实际拖动")
                    return False

                # 从拖动按钮中心起拖
                x0 = dg_r["x"] + dg_r["w"] / 2
                y0 = dg_r["y"] + dg_r["h"] / 2
                print(f"  起点 ({x0:.0f},{y0:.0f})  轨迹点 {len(human_track(distance))} 个")
                # 装 verify 响应监听（唯一的可信判据）
                try:
                    pg.js(JS_HOOK_VERIFY, timeout=12)
                except Exception:
                    pass

                self._drag(pg, x0, y0, distance, human_track(distance))

                # 判据：/captcha/verify 的响应码。**不要去等拖动按钮消失** ——
                # 实测通过后按钮并不消失，早先按按钮判断会把 62% 的成功全记成失败。
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
                if verdict == 200:
                    print("  ✅ verify 返回 200 —— 通过")
                    return True
                print(f"  ✗ verify 返回 {verdict}，重试")
                time.sleep(1.0)
                if auto_render:
                    self.render(pg)
            return False
        finally:
            pg.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok 滑块验证码求解器")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--detect", action="store_true")
    ap.add_argument("--render", action="store_true", help="主动渲染验证码（便于测试）")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--analyze", action="store_true", help="存图并输出缺口标注图")
    ap.add_argument("--dry-run", action="store_true", help="只算距离不拖动")
    ap.add_argument("--retries", type=int, default=5)
    args = ap.parse_args()

    S = SlideSolver(args.port)
    if args.detect or args.render:
        pg, tab = S._open()
        try:
            print("页面:", tab["url"][:88])
            print("初始:", json.dumps(S.detect(pg), ensure_ascii=False))
            if args.render:
                print("渲染:", S.render(pg))
                print("渲染后:", json.dumps(S.detect(pg), ensure_ascii=False))
        finally:
            pg.close()
    elif args.solve:
        ok = S.solve(retries=args.retries, dry_run=args.dry_run, auto_render=True)
        print("\n结果:", "✅ 通过" if ok else "❌ 未通过")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
