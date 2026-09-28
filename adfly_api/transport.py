"""传输层:多 host 自动路由、登录、会话保持、统一错误处理。

bundle 里的模块段是按页面分块的,不能直接当 host 用;这里按 spec/config.json 的
`groups` 定义候选 host 顺序,第一次调用时探测命中并缓存到 spec/routes.json,
之后直接用命中的 host,避免每次都试错。

认证完全走 header,不吃 cookie:
    AuthorizationFront: <JWT>
    CompanyExID:        <company_ex_id>
    country:            CN
    lang:               zh-CN
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence, Union

import requests

log = logging.getLogger("adfly.transport")

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "spec" / "config.json"
ROUTES_PATH = HERE / "spec" / "routes.json"
BUILTIN_ROUTES_PATH = HERE / "spec" / "routes_builtin.json"
DEFAULT_STATE = HERE / ".session.json"

# 这些 code 表示登录态失效,前端会跳登录页
AUTH_ERROR_CODES = {2, 8, 9, 10, 11}

Group = Union[str, Sequence[str]]


class AdflyError(RuntimeError):
    """业务错误:HTTP 通了但 code != 0。"""

    def __init__(self, code: Any, message: str, request_id: str = "", path: str = ""):
        super().__init__(f"[code={code}] {message} ({path} req_id={request_id})")
        self.code = code
        self.message = message
        self.request_id = request_id
        self.path = path


class AdflyAuthError(AdflyError):
    """登录态失效,需要重新登录。"""


class AdflyRouteError(AdflyError):
    """该路径在所有候选 host 上都不存在(404 page not found)。"""


def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if env:
        cfg["env"] = env
    cfg["base"] = cfg["backends"][cfg["env"]]
    return cfg


def md5_hex(text: str) -> str:
    """前端登录用的口令变换:CryptoJS.MD5(pwd.trim()).toString()。"""
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


def aes_encrypt_hex(plaintext: str, key: str, iv: str) -> str:
    """复现前端 encrypt():AES-128-CBC + PKCS7,输出 hex。当前登录链已不使用。"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return cipher.encrypt(pad(plaintext.encode("utf-8"), 16)).hex()


@dataclass
class Session:
    """登录态。token 与公司上下文分开存,便于多公司切换。"""

    token: str = ""
    company_ex_id: str = ""
    user: Dict[str, Any] = field(default_factory=dict)
    companies: list = field(default_factory=list)
    selected_company: Dict[str, Any] = field(default_factory=dict)
    country: str = "CN"
    lang: str = "zh-CN"
    saved_at: float = 0.0

    @classmethod
    def load(cls, path: Path = DEFAULT_STATE) -> "Session":
        if not path.exists():
            return cls()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in raw.items() if k in known})

    def save(self, path: Path = DEFAULT_STATE) -> None:
        self.saved_at = time.time()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.__dict__, ensure_ascii=False, indent=1), encoding="utf-8")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    @property
    def valid(self) -> bool:
        return bool(self.token)


class Transport:
    """HTTP 客户端。所有模块方法最终都落到 request()。"""

    def __init__(
        self,
        session: Optional[Session] = None,
        env: Optional[str] = None,
        state_path: Path = DEFAULT_STATE,
        timeout: float = 30.0,
        retries: int = 2,
        verbose: bool = False,
        cache_routes: bool = True,
        probe_attempts: int = 2,
        pool_size: int = 32,
    ):
        self.cfg = load_config(env)
        self.env = self.cfg["env"]
        self.base: Dict[str, str] = self.cfg["base"]
        self.groups: Dict[str, list] = self.cfg["groups"]
        self.session = session or Session.load(state_path)
        self.state_path = state_path
        # 可选:凭证失效时自动重登(填了才会启用)
        self._credentials: Optional[tuple] = None
        self._relogin_lock = threading.Lock()
        self.timeout = timeout
        self.retries = retries
        # GET 默认多一次重试(纯读,重放安全)
        self.verbose = verbose
        self.cache_routes = cache_routes
        self.probe_attempts = max(1, probe_attempts)
        self._lock = threading.Lock()
        # 预计算精确表(实测产出)优先:命中就不用探测,冷启动零开销
        self._builtin: Dict[str, str] = self._load_builtin()
        self._routes: Dict[str, str] = self._load_routes()
        self.stats: Dict[str, int] = {"requests": 0, "probes": 0, "retries": 0,
                                      "relogins": 0, "route_cache_hits": 0,
                                      "route_builtin_hits": 0, "errors": 0,
                                      "unsafe_timeouts": 0}
        self.http = requests.Session()
        # 默认 pool_maxsize=10,并发 32 时会反复建连(实测每次省 60% 延迟)
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max(10, pool_size),
            pool_maxsize=max(10, pool_size),
            max_retries=0,           # 重试逻辑自己控,不用 urllib3 的
            pool_block=False,
        )
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)
        self.http.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=UTF-8;",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
            ),
            "Origin": "https://ad.aiadfly.com",
            "Referer": "https://ad.aiadfly.com/",
        })
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    # ---------------- 路由解析 ----------------

    @staticmethod
    def _route_key(group: str, path: str) -> str:
        return f"{group}::{path}"

    def _load_builtin(self) -> Dict[str, str]:
        """加载 build_routes.py 由实测数据生成的精确路由表。"""
        if not BUILTIN_ROUTES_PATH.exists():
            return {}
        try:
            data = json.loads(BUILTIN_ROUTES_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return data if isinstance(data, dict) else {}

    def _load_routes(self) -> Dict[str, str]:
        """兼容两种缓存格式:v1 只有 host key;v2 是 {"cache_key": ..., "template": ...}。"""
        if not ROUTES_PATH.exists():
            return {}
        try:
            data = json.loads(ROUTES_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if not isinstance(data, dict):
            return {}
        out: Dict[str, str] = {}
        for k, v in data.items():
            if isinstance(v, str):
                # v1 只有 host key:不带路径变体,当作原路径处理
                out[k] = v if "|" in v else f"{v}|"
            elif isinstance(v, dict) and v.get("cache_key") == k and "route" in v:
                out[k] = v["route"]
        return out

    def _save_routes(self) -> None:
        if not self.cache_routes:
            return
        payload = {k: {"cache_key": k, "route": v}
                   for k, v in sorted(self._routes.items())}
        try:
            ROUTES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:
            log.debug("路由缓存写入失败: %s", exc)

    # ai_agent 段混装两类路径:自带 /ai_agent/ 段的走独立服务,其余走主网关。
    # 候选顺序按路径形态排序,把探测次数从"总是试两个"降到"通常一次命中"。
    _AI_AGENT_PREFIX = re.compile(r"^/ai_agent(/|$)")

    def _candidates(self, group: str, path: str = "") -> list:
        keys = self.groups.get(group)
        if not keys:
            # 未登记的组名:当成单个 host key
            return [group] if group in self.base else [next(iter(self.base))]
        keys = [k for k in keys if k in self.base]
        if group == "ai_agent" and path:
            wants_agent = bool(self._AI_AGENT_PREFIX.match("/" + path.lstrip("/")))
            keys.sort(key=lambda k: 0 if (wants_agent == k.startswith("ai_agent")) else 1)
        return keys

    @staticmethod
    def _join(base_url: str, path: str) -> str:
        """拼 URL。base 自带 /ai_agent 而路径也以 /ai_agent/ 开头时,避免叠成两段。"""
        p = "/" + path.lstrip("/")
        for suffix in ("/ai_agent",):
            if base_url.endswith(suffix) and p.startswith(suffix + "/"):
                return base_url[: -len(suffix)] + p
        return base_url + p

    @classmethod
    def _variants(cls, base_url: str, path: str) -> list:
        """一个 host 上可能成立的 URL 形态,按可能性排序。

        ai_agent 段的路径自带 /ai_agent/ 段,但同一段里也混了 /notice/* 这类主网关路径,
        所以要去前缀再试一次 —— 之前只试原路径,导致 bell_list 被静默打到错的服务上。
        """
        urls = [cls._join(base_url, path)]
        stripped = re.sub(r"^/ai_agent(?=/)", "", "/" + path.lstrip("/"))
        if stripped != "/" + path.lstrip("/"):
            alt = base_url + stripped
            if alt not in urls:
                urls.append(alt)
        return urls

    # 路由未命中时服务端返回的指纹:HTTP 404 + 纯文本 "404 page not found"(chi 路由风格)
    @staticmethod
    def _is_route_miss(status: int, text: str) -> bool:
        head = text[:200].lower()
        return status == 404 and "page not found" in head

    # 判定值:命中 / 明确未命中 / 已到达服务但 5xx(不确定) / 网络层失败(不确定)
    _HIT, _MISS, _MAYBE = "hit", "miss", "maybe"

    def _probe_one(self, url: str) -> tuple:
        """探测单个 URL 是否存在。返回 (verdict, detail)。"""
        self.stats["probes"] += 1
        headers = self._headers({"Content-Type": "application/json; charset=UTF-8;"})
        last: Optional[Exception] = None
        for attempt in range(self.probe_attempts):
            try:
                resp = self.http.request("POST", url, headers=headers, json={},
                                         timeout=min(self.timeout, 12))
            except requests.RequestException as exc:
                last = exc
                if attempt + 1 < self.probe_attempts:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                return self._MAYBE, f"net:{type(exc).__name__}"
            text = resp.text
            if self._is_route_miss(resp.status_code, text):
                return self._MISS, "404"
            self.stats["probes"] += 0
            if resp.status_code >= 500:
                # 5xx 不能作为归属证据:参数对但服务端内部错时,别的 host 也会同样报错。
                # 实测 automation 对 /advertiser/list 回 500,front 才是真身。
                return self._MAYBE, f"http{resp.status_code}"
            return self._HIT, f"http{resp.status_code}"
        return self._MAYBE, f"net:{type(last).__name__ if last else '?'}"

    def resolve(self, group: str, path: str, tool: str = "POST") -> str:
        """给出该路径的最终 URL(带模板缓存)。

        策略:
          - 已缓存模板 → 直接套用
          - 未缓存 → 按候选 host × URL 变体依次探测,命中即缓存
          - 读操作(非 POST/DELETE/PUT/PATCH)探测全灭时回退到首个候选,让业务错误自己暴露
          - 写操作 fail-closed:不确定就不猜,抛 AdflyRouteError 让调用方显式指定 group
        """
        cache_key = self._route_key(group, path)
        # 预计算表来自全量实测(202 条精确归属),可信度高于任何运行时探测结果,优先用。
        builtin = self._builtin.get(cache_key)
        if builtin:
            base_key, _, variant = builtin.partition("|")
            base_url = self.base.get(base_key)
            if base_url:
                self.stats["route_builtin_hits"] += 1
                return self._join(base_url, variant or path)
            log.debug("预计算表的 base_key=%s 不在当前环境,继续解析", base_key)

        cached = self._routes.get(cache_key)
        if cached:
            self.stats["route_cache_hits"] += 1
            base_key, _, variant = cached.partition("|")
            base_url = self.base.get(base_key)
            if base_url:
                return self._join(base_url, variant or path)
            log.debug("缓存的 base_key=%s 不在当前环境,重新探测", base_key)

        candidates = self._candidates(group, path)
        maybe: list = []
        for cand in candidates:
            base_url = self.base.get(cand)
            if not base_url:
                continue
            for url in self._variants(base_url, path):
                verdict, detail = self._probe_one(url)
                if verdict == self._HIT:
                    variant = url[len(base_url):].lstrip("/")
                    self._remember(cache_key, f"{cand}|{variant}")
                    log.debug("路由命中 %s -> %s (%s)", path, url, detail)
                    return url
                if verdict == self._MAYBE:
                    maybe.append(url)
        if maybe:
            # 有响应但不确定(5xx/超时):用第一个,并把模板记下来但标记未确证
            url = maybe[0]
            if self._writes_to_state(tool):
                raise AdflyRouteError(
                    0,
                    f"路由无法确证({len(maybe)} 个候选返回 5xx/超时),写操作已阻断,"
                    f"请显式传 group= 或先用读接口确认。候选: {maybe[:2]}",
                    "", path,
                )
            log.debug("路由未确证 %s,回退 %s", path, url)
            return url
        if self._writes_to_state(tool):
            raise AdflyRouteError(
                0, f"没有任何候选 host 命中该路径(候选 {candidates}),写操作已阻断",
                "", path,
            )
        # 读操作:回退第一个候选,让真实的业务错误(而不是路由错误)暴露出来
        return self._join(self.base[candidates[0]], path)

    def _remember(self, cache_key: str, route: str) -> None:
        with self._lock:
            self._routes[cache_key] = route
            self._save_routes()

    @staticmethod
    def _writes_to_state(method: str) -> bool:
        return method.upper() in ("POST", "PUT", "PATCH", "DELETE")

    def prewarm(self, routes: Iterable[tuple], workers: int = 8) -> Dict[str, int]:
        """并发预热路由缓存,消除批量任务的冷启动探测开销。

        routes 是 (group, path) 或 (group, path, method) 的可迭代对象。
        返回 {"resolved": n, "skipped": m}。
        """
        import concurrent.futures as _cf

        items = []
        for r in routes:
            group, path = r[0], r[1]
            method = r[2] if len(r) > 2 else "POST"
            if self._route_key(group, path) not in self._routes:
                items.append((group, path, method))
        if not items:
            return {"resolved": 0, "skipped": 0}

        done = {"n": 0}
        lock = threading.Lock()

        def work(item):
            group, path, method = item
            try:
                self.resolve(group, path, tool=method)
                with lock:
                    done["n"] += 1
            except Exception as exc:  # noqa: BLE001
                log.debug("预热 %s %s 失败: %s", group, path, exc)

        with _cf.ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(work, items))
        return {"resolved": done["n"], "skipped": len(routes) - len(items) if hasattr(routes, "__len__") else 0}

    def stats_report(self) -> str:
        """人类可读的运行统计。"""
        s = self.stats
        total = max(s["requests"] + s["probes"], 1)
        return (f"业务请求 {s['requests']} / 探测 {s['probes']} / 重试 {s['retries']} / "
                f"重登 {s['relogins']} / 路由命中(预计算 {s['route_builtin_hits']} + 缓存 "
                f"{s['route_cache_hits']}) / 错误 {s['errors']}  "
                f"(探测占比 {s['probes']/total*100:.1f}%"
                + (f", 写操作遇读超时 {s['unsafe_timeouts']} 次" if s.get("unsafe_timeouts") else "")
                + ")")

    # ---------------- 认证 ----------------

    def enable_auto_relogin(self, account: str, password: str) -> None:
        """记住凭证,遇到 code=2/9 等失效码时自动重登一次(默认不启用,不落盘)。"""
        self._credentials = (account, password)

    def login(self, account: str, password: str) -> Session:
        """account 为手机号或邮箱。前端对密码做 md5 后再提交。"""
        body = {"account": account.strip(), "password": md5_hex(password)}
        resp = self.request("POST", "/user/login", json_body=body, group="front", auth=False, raw=True)
        data = resp.get("data") or {}
        if not data.get("token"):
            raise AdflyError(resp.get("code", -1), resp.get("message", "登录失败"),
                             resp.get("request_id", ""), "/user/login")
        self.session.token = data["token"]
        self.session.user = data
        self._credentials = self._credentials or None
        self.session.save(self.state_path)
        self._load_companies()
        return self.session

    def _try_relogin(self) -> bool:
        """凭证失效时重登一次。并发下只让一个线程真正去登。"""
        if not self._credentials:
            return False
        with self._relogin_lock:
            account, password = self._credentials
            try:
                old = self.session.token
                self.stats["relogins"] += 1
                self.login(account, password)
                return self.session.token != old or bool(self.session.token)
            except AdflyError as exc:
                log.warning("自动重登失败: %s", exc)
                return False

    def check_fa(self, account: str, password: str) -> Dict[str, Any]:
        """探测账号是否开了双因素 / 图形验证码。"""
        body = {"account": account.strip(), "password": md5_hex(password)}
        return self.request("POST", "/user/check_fa", json_body=body, group="front", auth=False, raw=True)

    def _load_companies(self) -> None:
        # GET /company/list 返回公司数组(不是分页信封),公司上下文就取自这里
        for path in ("/company/list", "/company/list?yt_platform=1"):
            try:
                data = self.request("GET", path, group="front")
            except AdflyError as exc:
                log.debug("%s 失败: %s", path, exc)
                continue
            lst = data if isinstance(data, list) else (data or {}).get("list")
            if isinstance(lst, list) and lst:
                self.session.companies = lst
                if not self.session.company_ex_id:
                    self.session.company_ex_id = lst[0].get("company_ex_id", "")
                break
        if not self.session.user.get("user_id"):
            try:
                self.session.user = self.request("GET", "/user/info", group="front") or {}
            except AdflyError as exc:
                log.debug("/user/info 失败: %s", exc)
        self.session.save(self.state_path)

    def use_company(self, company_ex_id: str) -> None:
        self.session.company_ex_id = company_ex_id
        match = [c for c in self.session.companies if c.get("company_ex_id") == company_ex_id]
        self.session.selected_company = match[0] if match else {}
        self.session.save(self.state_path)

    def set_token(self, token: str, company_ex_id: str = "", country: str = "CN", lang: str = "zh-CN") -> None:
        """手工注入 token(例如从浏览器 localStorage 的 yt__userInfo 复制)。"""
        self.session.token = token
        if company_ex_id:
            self.session.company_ex_id = company_ex_id
        self.session.country = country
        self.session.lang = lang
        self.session.save(self.state_path)

    def whoami(self) -> Dict[str, Any]:
        return self.session.user

    # ---------------- 请求 ----------------

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h = {
            "AuthorizationFront": self.session.token,
            "CompanyExID": self.session.company_ex_id,
            "country": self.session.country,
            "lang": self.session.lang,
        }
        if extra:
            h.update({k: v for k, v in extra.items() if v is not None})
        return h

    def request(
        self,
        method: str,
        path_or_url: str,
        *,
        json_body: Any = None,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        group: Optional[str] = None,
        auth: bool = True,
        raw: bool = False,
        response_type: str = "json",
        timeout: Optional[float] = None,
        idempotent: Optional[bool] = None,
        _resolved: bool = False,
    ) -> Any:
        """发一次请求。

        path_or_url 以 "/" 开头时按 group 解析 host;是完整 URL 则直接用。
        幂等重试:默认 GET/HEAD 与显式 idempotent=True 才重试,避免重复创建广告。
        """
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            url = path_or_url
            group = group or "front"
        else:
            group = group or "front"
            if _resolved:
                url = path_or_url
            else:
                url = self.resolve(group, path_or_url, tool=method)

        if idempotent is None:
            idempotent = method.upper() in ("GET", "HEAD")
        kw: Dict[str, Any] = {"params": params, "timeout": timeout or self.timeout}
        if json_body is not None:
            kw["json"] = json_body
        if data is not None:
            kw["data"] = data
        if auth:
            kw["headers"] = self._headers(headers)
        elif headers:
            kw["headers"] = headers

        # 循环上界要覆盖"连接阶段失败可重放"的情况,所以对写操作也多留一次;
        # 真正的收紧在循环内按失败类型决定(见 hard 变量)。
        attempts = (self.retries + 1) if idempotent else 2
        relogin_tried = False
        last_exc: Optional[Exception] = None
        for attempt in range(attempts):
            try:
                resp = self.http.request(method.upper(), url, **kw)
            except requests.Timeout as exc:
                # 超时分两类,安全性不同:
                #   ConnectTimeout / TLS 握手超时 → 请求根本没发出去,重放绝对安全
                #   ReadTimeout                    → 服务端可能已处理,写操作不能盲重放
                self.stats["retries"] += 1
                last_exc = exc
                sent = isinstance(exc, requests.ReadTimeout)
                # 连接阶段失败(请求没出去)对任何方法都能安全重放;
                # 读阶段失败(可能已被服务端处理)只允许幂等方法重放。
                if sent and not idempotent:
                    self.stats["unsafe_timeouts"] = self.stats.get("unsafe_timeouts", 0) + 1
                    raise
                if attempt + 1 >= attempts:
                    raise
                time.sleep(0.6 * (2 ** attempt) + random.random() * 0.3)
                continue
            except requests.RequestException as exc:
                last_exc = exc
                if attempt + 1 >= attempts:
                    raise
                time.sleep(0.4 * (2 ** attempt) + random.random() * 0.2)
                continue

            self.stats["requests"] += 1
            if resp.status_code == 429 or resp.status_code == 503:
                retry_after = resp.headers.get("Retry-After", "")
                try:
                    wait = min(float(retry_after), 30.0) if retry_after else 1.0 * (2 ** attempt)
                except ValueError:
                    wait = 1.0 * (2 ** attempt)
                log.debug("限流(%s),等 %.1fs 重试", resp.status_code, wait)
                if attempt + 1 >= attempts and not idempotent:
                    raise AdflyError(resp.status_code, f"被限流,Retry-After={retry_after or '-'}",
                                     resp.headers.get("X-Request-Id", ""), url)
                time.sleep(wait + random.random() * 0.3)
                continue
            if resp.status_code >= 500 and attempt + 1 < attempts:
                time.sleep(0.6 * (2 ** attempt))
                continue

            if response_type == "blob":
                if resp.status_code >= 400:
                    raise AdflyError(resp.status_code, resp.text[:300], "", url)
                return resp.content

            text = resp.text
            stripped = text.strip()
            if stripped.lower().startswith("404 page not found") or "404 page not found" in stripped[:120]:
                raise AdflyRouteError(404, "404 page not found", "", url)
            if resp.status_code >= 400:
                raise AdflyError(resp.status_code, stripped[:300] or resp.reason, "", url)

            ctype = resp.headers.get("Content-Type", "")
            try:
                envelope = resp.json()
            except ValueError:
                if response_type == "json" and (
                    "spreadsheet" in ctype or "octet-stream" in ctype
                    or stripped[:2] == "PK" or stripped[:3] == "\xef\xbb\xbf"
                ):
                    raise AdflyError(
                        resp.status_code, "二进制响应(导出文件),请用 download() 或 response_type='blob'",
                        "", url,
                    )
                if "event-stream" in ctype:
                    raise AdflyError(resp.status_code, f"SSE 流式响应(content-type={ctype})", "", url)
                raise AdflyError(resp.status_code,
                                 f"非 JSON 响应(content-type={ctype or '?'}): {stripped[:160]}", "", url)

            if isinstance(envelope, dict) and "code" in envelope:
                code = envelope.get("code")
                if code in (0, 200):
                    return envelope if raw else envelope.get("data")
                if code in AUTH_ERROR_CODES and not relogin_tried and self._try_relogin():
                    relogin_tried = True
                    # 重登成功后重放一次,新 token 已经在 self.session 里
                    kw["headers"] = self._headers(headers) if auth else kw.get("headers")
                    resp2 = self.http.request(method.upper(), url, **kw)
                    try:
                        env2 = resp2.json()
                    except ValueError:
                        raise AdflyError(resp2.status_code, resp2.text[:200], "", url)
                    if env2.get("code") in (0, 200):
                        return env2 if raw else env2.get("data")
                    err_cls = AdflyAuthError if env2.get("code") in AUTH_ERROR_CODES else AdflyError
                    raise err_cls(env2.get("code"), env2.get("message") or env2.get("reason", ""),
                                  env2.get("request_id", ""), url)
                err_cls = AdflyAuthError if code in AUTH_ERROR_CODES else AdflyError
                raise err_cls(code, envelope.get("message") or envelope.get("reason", ""),
                              envelope.get("request_id", ""), url)
            # 非标准信封(ai_agent 的 {"code":400,"reason":...} 已在上面覆盖)
            return envelope

        raise last_exc if last_exc else RuntimeError("unreachable")

    # 便捷方法:group 可以是单 key 或候选列表
    def get(self, group: Group, path: str, **kw: Any) -> Any:
        return self.request("GET", path, group=self._as_group(group), **kw)

    def post(self, group: Group, path: str, body: Any = None, **kw: Any) -> Any:
        return self.request("POST", path, json_body=body, group=self._as_group(group), **kw)

    def _as_group(self, group: Group) -> str:
        """模块生成的代码传的是候选 key 元组;缓存时用它的稳定字符串形式做组名。"""
        if isinstance(group, str):
            return group
        keys = list(group)
        return next((k for k in keys if k in self.groups), "+".join(keys))

    # ---------------- 便捷封装 ----------------

    def download(self, group: Group, path: str, out_path: str, body: Any = None, method: str = "POST") -> str:
        """导出类接口:返回 xlsx/csv 二进制,直接落盘。"""
        content = self.request(method, path, json_body=body, group=self._as_group(group),
                               response_type="blob", idempotent=False)
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return str(p)

    def paginate(
        self,
        group: Group,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        max_pages: int = 200,
    ) -> Iterable[Dict[str, Any]]:
        """按 page/page_size 翻页,把 list 里的元素逐个吐出来。"""
        body = dict(body or {})
        g = self._as_group(group)
        page = 1
        while page <= max_pages:
            body.update({"page": page, "page_size": page_size})
            data = self.post(g, path, body) or {}
            items = data.get("list") or data.get("data") or []
            if not items:
                return
            for it in items:
                yield it
            if len(items) < page_size:
                return
            page += 1
