#!/usr/bin/env python3
"""离线单元测试 —— 不联网,验证传输层的关键逻辑。

    python3 test_transport.py            # 全部
    python3 test_transport.py -v         # 带用例名
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api.transport import (  # noqa: E402
    AdflyAuthError,
    AdflyError,
    AdflyRouteError,
    Session,
    Transport,
    aes_encrypt_hex,
    load_config,
    md5_hex,
)


class FakeResponse:
    def __init__(self, status=200, text="", payload=None, headers=None):
        self.status_code = status
        self.text = text
        self._payload = payload
        self.headers = headers or {"Content-Type": "application/json"}

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class TestCrypto(unittest.TestCase):
    def test_md5_matches_frontend(self):
        # 前端:CryptoJS.MD5(password.trim()).toString()
        import hashlib
        self.assertEqual(md5_hex("abc"), hashlib.md5(b"abc").hexdigest())
        self.assertEqual(md5_hex("  abc  "), md5_hex("abc"), "必须 trim")
        self.assertEqual(len(md5_hex("x")), 32)

    def test_aes_cbc_hex_matches_known_vector(self):
        # 用 WebCrypto AES-CBC 算出的向量交叉验证(见 notes 记录)
        cfg = load_config()
        out = aes_encrypt_hex("test123456", cfg["aes"]["key_utf8"], cfg["aes"]["iv_utf8"])
        self.assertEqual(out, "80ce70d910ec2b6a4995c1d0ca5fa57a")
        self.assertEqual(len(out) % 32, 0)


class TestUrlVariants(unittest.TestCase):
    def test_join_avoids_double_ai_agent(self):
        self.assertEqual(
            Transport._join("https://ai-agent-v1.aiadfly.com/ai_agent", "/ai_agent/v1/x"),
            "https://ai-agent-v1.aiadfly.com/ai_agent/v1/x")

    def test_join_normal(self):
        self.assertEqual(Transport._join("https://front-v1.aiadfly.com/front_api", "/user/info"),
                         "https://front-v1.aiadfly.com/front_api/user/info")

    def test_variants_include_stripped_form(self):
        v = Transport._variants("https://front-v1.aiadfly.com/front_api", "/ai_agent/v1/user/profile")
        self.assertIn("https://front-v1.aiadfly.com/front_api/ai_agent/v1/user/profile", v)
        self.assertIn("https://front-v1.aiadfly.com/front_api/v1/user/profile", v)

    def test_variants_dedup_for_normal_path(self):
        v = Transport._variants("https://front-v1.aiadfly.com/front_api", "/advertiser/list")
        self.assertEqual(len(v), 1)

    def test_route_miss_fingerprint(self):
        self.assertTrue(Transport._is_route_miss(404, "404 page not found"))
        self.assertTrue(Transport._is_route_miss(404, "\n404 page not found\n"))
        self.assertFalse(Transport._is_route_miss(200, '{"code":404,"message":"x"}'))
        self.assertFalse(Transport._is_route_miss(404, '{"code":404}'))


class TestOverrideMap(unittest.TestCase):
    def test_path_rules(self):
        from backend_map import group_for
        self.assertEqual(group_for("finance", "/tt/auth/list"), "advertise")
        self.assertEqual(group_for("finance", "/kanban/google_adv_consume"), "advertise")
        self.assertEqual(group_for("finance", "/snapshots/campaign/list"), "finance")  # 死路径,保持原样
        self.assertEqual(group_for("ai_agent", "/notice/bell_list"), "front")
        self.assertEqual(group_for("ai_agent", "/ai_agent/v1/user/profile"), "ai_agent")
        self.assertEqual(group_for("finance", "/material/list"), "automation")

    def test_normalize_keeps_section(self):
        from backend_map import normalize_endpoints
        rows = [{"fn": "f", "path": "/tt/auth/list", "method": "POST", "backend": "finance"}]
        changed = normalize_endpoints(rows)
        self.assertEqual(rows[0]["backend"], "advertise")
        self.assertEqual(rows[0]["section"], "finance")
        self.assertEqual(len(changed), 1)


class TestSession(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            s = Session(token="tok", company_ex_id="100", country="CN")
            s.save(p)
            loaded = Session.load(p)
            self.assertEqual(loaded.token, "tok")
            self.assertEqual(loaded.company_ex_id, "100")
            self.assertTrue(loaded.valid)
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)

    def test_load_missing_or_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            self.assertFalse(Session.load(p).valid)
            p.write_text("not json")
            self.assertFalse(Session.load(p).valid)

    def test_unknown_fields_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            p.write_text(json.dumps({"token": "t", "legacy_field": 1}))
            self.assertEqual(Session.load(p).token, "t")


class TestRouteCache(unittest.TestCase):
    def _t(self, tmp: str) -> Transport:
        t = Transport(state_path=Path(tmp) / "s.json")
        t.cache_routes = True
        t._routes = {}
        return t

    def test_remember_and_reload_env_agnostic(self):
        """缓存要存 base_key|path,换环境后仍可复用。

        用一个不在预计算表里的路径,单独验证缓存落盘与重载。
        """
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            key = "advertise::/zz_not_in_builtin"
            t._remember(key, "advertise_bff|zz_not_in_builtin")
            raw = json.loads((HERE / "adfly_api/spec/routes.json").read_text())
            self.assertIn(key, raw)
            self.assertEqual(raw[key]["route"], "advertise_bff|zz_not_in_builtin")

            t2 = self._t(d)
            t2._routes = t2._load_routes()
            url = t2.resolve("advertise", "/zz_not_in_builtin")
            self.assertTrue(url.startswith("https://advertise-bff-v1.aiadfly.com/front_api/zz_not_in_builtin"),
                            url)

    def test_legacy_string_cache_upgraded(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            routes = HERE / "adfly_api/spec/routes.json"
            backup = routes.read_text() if routes.exists() else None
            try:
                routes.write_text(json.dumps({"advertise::/x": "front"}))
                t._routes = t._load_routes()
                self.assertEqual(t._routes["advertise::/x"], "front|")
            finally:
                if backup:
                    routes.write_text(backup)


class TestErrorMapping(unittest.TestCase):
    def _t(self, tmp: str) -> Transport:
        t = Transport(state_path=Path(tmp) / "s.json")
        t.session.token = "tok"
        t.session.company_ex_id = "100"
        return t

    def test_auth_code_raises_auth_error(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            t._routes["front::/user/info"] = "front|user/info"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(200, payload={"code": 2, "message": "无 token"})):
                with self.assertRaises(AdflyAuthError):
                    t.request("GET", "/user/info", group="front")

    def test_business_error_carries_code_and_request_id(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            t._routes["front::/x"] = "front|x"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(200, payload={"code": 999, "message": "广告账号有误",
                                                                           "request_id": "rid1"})):
                with self.assertRaises(AdflyError) as cm:
                    t.request("POST", "/x", json_body={}, group="front")
                self.assertEqual(cm.exception.code, 999)
                self.assertEqual(cm.exception.request_id, "rid1")

    def test_route_miss_raises_route_error(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            t._routes["front::/nope"] = "front|nope"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(404, text="404 page not found")):
                with self.assertRaises(AdflyRouteError):
                    t.request("GET", "/nope", group="front")

    def test_binary_response_hint(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            t._routes["advertise::/export"] = "front|export"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(200, text="PK\x03\x04binary",
                                                             headers={"Content-Type": "application/vnd.ms-excel"})):
                with self.assertRaises(AdflyError) as cm:
                    t.request("POST", "/export", json_body={}, group="advertise")
                self.assertIn("二进制响应", str(cm.exception))

    def test_success_returns_data_only(self):
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            t._routes["front::/ok"] = "front|ok"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(200, payload={"code": 0, "data": {"n": 1}})):
                self.assertEqual(t.request("GET", "/ok", group="front"), {"n": 1})
                env = t.request("GET", "/ok", group="front", raw=True)
                self.assertEqual(env["code"], 0)


class TestFailClosedWrites(unittest.TestCase):
    def test_write_blocked_when_route_unverifiable(self):
        """写操作在路由无法确证时必须抛错,而不是猜一个 host。"""
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            t.session.token = "tok"
            t._routes = {}
            t._builtin = {}          # 清空预计算表,强制走探测路径以验证 fail-closed
            t.cache_routes = False
            with mock.patch.object(t, "_probe_one", return_value=(t._MAYBE, "net:Timeout")):
                with self.assertRaises(AdflyRouteError) as cm:
                    t.resolve("advertise", "/tiktok/create_advertisement_new", tool="POST")
                self.assertIn("写操作已阻断", str(cm.exception))

    def test_read_falls_back_to_first_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            t._routes = {}
            t._builtin = {}
            t.cache_routes = False
            with mock.patch.object(t, "_probe_one", return_value=(t._MISS, "404")):
                url = t.resolve("front", "/user/info", tool="GET")
                self.assertTrue(url.startswith("https://front-v1.aiadfly.com/front_api"))

    def test_write_not_retried_but_get_is(self):
        """读阶段超时(可能已被服务端处理):写操作不重放,读操作重放。"""
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            t.session.token = "tok"
            t._routes["front::/x"] = "front|x"
            calls = {"n": 0}

            def boom(*a, **k):
                calls["n"] += 1
                raise __import__("requests").exceptions.ReadTimeout("t")

            with mock.patch.object(t.http, "request", side_effect=boom):
                with self.assertRaises(Exception):
                    t.request("POST", "/x", json_body={}, group="front")
                post_calls = calls["n"]
            calls["n"] = 0
            with mock.patch.object(t.http, "request", side_effect=boom):
                with self.assertRaises(Exception):
                    t.request("GET", "/x", group="front")
                get_calls = calls["n"]
            self.assertEqual(post_calls, 1, "读超时的 POST 不重放(避免重复建广告)")
            self.assertGreater(get_calls, post_calls, "GET 幂等,应重放")


class TestTimeoutReplaySafety(unittest.TestCase):
    """连接阶段超时可以重放(POST 也一样);读阶段超时不能盲重放写操作。"""

    def _t(self, d):
        t = Transport(state_path=Path(d) / "s.json")
        t.session.token = "tok"
        t._routes["front::/x"] = "front|x"
        t._builtin = {}
        return t

    def test_connect_timeout_replays_even_for_post(self):
        import requests as rq
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            calls = {"n": 0}

            def boom(*a, **k):
                calls["n"] += 1
                raise rq.exceptions.ConnectTimeout("connect timed out")

            with mock.patch.object(t.http, "request", side_effect=boom):
                with self.assertRaises(Exception):
                    t.request("POST", "/x", json_body={}, group="front")
            self.assertEqual(calls["n"], 2, "连接阶段超时的 POST 应重放一次")

    def test_read_timeout_does_not_replay_post(self):
        import requests as rq
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            calls = {"n": 0}

            def boom(*a, **k):
                calls["n"] += 1
                raise rq.exceptions.ReadTimeout("read timed out")

            with mock.patch.object(t.http, "request", side_effect=boom):
                with self.assertRaises(Exception):
                    t.request("POST", "/x", json_body={}, group="front")
            self.assertEqual(calls["n"], 1, "读阶段超时的 POST 不能重放(避免重复创建)")

    def test_read_timeout_replays_get(self):
        import requests as rq
        with tempfile.TemporaryDirectory() as d:
            t = self._t(d)
            calls = {"n": 0}

            def boom(*a, **k):
                calls["n"] += 1
                raise rq.exceptions.ReadTimeout("read timed out")

            with mock.patch.object(t.http, "request", side_effect=boom):
                with self.assertRaises(Exception):
                    t.request("GET", "/x", group="front")
            self.assertEqual(calls["n"], 3, "GET 幂等,应重放满 retries 次")


class TestCandidateOrdering(unittest.TestCase):
    def test_ai_agent_path_ordering(self):
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            self.assertEqual(t._candidates("ai_agent", "/ai_agent/v1/user/profile")[0], "ai_agent_root")
            self.assertEqual(t._candidates("ai_agent", "/notice/bell_list")[0], "front")

    def test_unknown_group_falls_back(self):
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            self.assertEqual(t._candidates("front"), ["front"])


class TestBuiltinPriority(unittest.TestCase):
    def test_builtin_wins_over_runtime_cache(self):
        """预计算表来自全量实测,不能被某次探测结果覆盖。"""
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            builtin = t._builtin.get("advertise::/advertiser/list")
            if not builtin:
                self.skipTest("没有 routes_builtin.json")
            t._routes["advertise::/advertiser/list"] = "advertise_bff|advertiser/list"
            url = t.resolve("advertise", "/advertiser/list")
            self.assertTrue(url.startswith("https://front-v1.aiadfly.com"),
                            f"应优先预计算表 front,实际 {url}")

    def test_probe_500_is_not_a_hit(self):
        """5xx 不能作为 host 归属证据。"""
        with tempfile.TemporaryDirectory() as d:
            t = Transport(state_path=Path(d) / "s.json")
            t.session.token = "tok"
            with mock.patch.object(t.http, "request",
                                   return_value=FakeResponse(500, text="boom")):
                verdict, detail = t._probe_one("https://front-v1.aiadfly.com/front_api/x")
                self.assertEqual(verdict, t._MAYBE, "500 必须是 maybe 而不是 hit")


class TestEndpointManifest(unittest.TestCase):
    def test_manifest_shape(self):
        from adfly_api.spec import load_endpoints
        rows = load_endpoints()
        self.assertGreaterEqual(len(rows), 291, "清单应为去重后的唯一接口数")
        for r in rows:
            self.assertIn(r["backend"], load_config()["groups"], f'{r["fn"]} 的 backend 未登记')
            self.assertTrue(r["path"].startswith("/"), r["path"])
            self.assertIn(r["method"], ("GET", "POST", "PUT", "DELETE", "PATCH"))
            self.assertIn("section", r, "缺少 section 字段(归一化未执行)")

    def test_no_duplicate_method_path(self):
        from adfly_api.spec import load_endpoints
        seen = set()
        for r in load_endpoints():
            key = (r["backend"], r["method"], r["path"])
            self.assertNotIn(key, seen, f"重复: {key}")
            seen.add(key)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
