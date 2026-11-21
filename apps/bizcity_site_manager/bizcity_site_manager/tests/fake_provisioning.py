# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: máy chủ Provisioning giả theo bizcity_site_provisioning@1 (bản nháp), để làm W1 song song với PHASE-039 B5 bên open-ketoan
"""Máy chủ Provisioning API giả, chỉ dùng thư viện chuẩn. Làm đúng các luật của hợp đồng mà phía gọi phải xử lý:
khoá, Idempotency-Key, slug, việc bất đồng bộ (lần hỏi đầu `running`, lần sau `done`), khoá trước khi xoá, sao lưu mới.

Chạy tay: `python -m bizcity_site_manager.tests.fake_provisioning 8765 prov_test`
"""

from __future__ import annotations

import json
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from bizcity_site_manager.provisioning import API_PREFIX, check_slug


class FakeState:
    def __init__(self, key: str):
        self.key = key
        self.sites: dict[str, dict[str, Any]] = {}
        self.jobs: dict[str, dict[str, Any]] = {}
        self.idem: dict[str, tuple[str, dict[str, Any]]] = {}  # Idempotency-Key → (thân lệnh, kết quả)
        self.lock = threading.Lock()


def _err(code: str, status: int) -> tuple[int, dict[str, Any]]:
    return status, {"error": {"code": code, "message": code}}


def handle(state: FakeState, method: str, path: str, headers: dict[str, str], body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    if headers.get("authorization") != f"Bearer {state.key}":
        return _err("PROVISION_KEY_INVALID", 401)
    if not path.startswith(API_PREFIX):
        return _err("NOT_FOUND", 404)
    p = path[len(API_PREFIX):].split("?")[0].strip("/").split("/")
    idem = headers.get("idempotency-key")
    if method != "GET":
        if not idem:
            return _err("IDEMPOTENCY_KEY_REQUIRED", 400)
        raw = json.dumps([method, path, body], sort_keys=True, ensure_ascii=False)
        prev = state.idem.get(idem)
        if prev:
            return (200, prev[1]) if prev[0] == raw else _err("IDEMPOTENCY_KEY_REUSED", 422)

    with state.lock:
        status, out = _route(state, method, p, body or {})
        if method != "GET" and 200 <= status < 300:
            state.idem[idem] = (json.dumps([method, path, body], sort_keys=True, ensure_ascii=False), out)  # type: ignore[index]
        return status, out


def _new_job(state: FakeState, site_id: str, kind: str) -> str:
    job_id = "J" + uuid.uuid4().hex[:12]
    state.jobs[job_id] = {"jobId": job_id, "siteId": site_id, "kind": kind, "status": "queued", "polls": 0, "error": None}
    return job_id


def _route(state: FakeState, method: str, p: list[str], body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    if p == ["health"] and method == "GET":
        return 200, {"contract": "bizcity_site_provisioning@1", "sites": len(state.sites)}
    if p == ["sites"] and method == "GET":
        return 200, {"items": list(state.sites.values()), "next": None}
    if p == ["sites"] and method == "POST":
        slug = str(body.get("slug", ""))
        if check_slug(slug):
            return _err("SITE_SLUG_INVALID", 400)
        if any(s["slug"] == slug for s in state.sites.values()):
            return _err("SITE_SLUG_TAKEN", 409)
        domain = str(body.get("domain", "")).lower()
        if any(d["domain"] == domain for s in state.sites.values() for d in s["domains"]):
            return _err("SITE_DOMAIN_TAKEN", 409)
        site_id = "S" + uuid.uuid4().hex[:12]
        state.sites[site_id] = {
            "siteId": site_id, "slug": slug, "displayName": body.get("displayName", slug), "status": "provisioning",
            "domains": [{"domain": domain, "primary": True}], "schemaVersion": None, "appVersion": "0.39.0",
            "externalRef": body.get("externalRef"), "license": {"status": "missing"}, "lastBackupAt": None,
        }
        return 202, {"jobId": _new_job(state, site_id, "provision"), "siteId": site_id}
    if len(p) == 2 and p[0] == "jobs" and method == "GET":
        job = state.jobs.get(p[1])
        if not job:
            return _err("NOT_FOUND", 404)
        job["polls"] += 1
        if job["status"] != "done":
            job["status"] = "running" if job["polls"] == 1 else "done"
            if job["status"] == "done":
                site = state.sites[job["siteId"]]
                if job["kind"] == "provision":
                    site.update(status="active", schemaVersion="0177_…")
                elif job["kind"] == "suspend":
                    site["status"] = "suspended"
                elif job["kind"] == "resume":
                    site["status"] = "active"
                elif job["kind"] == "backup":
                    site["lastBackupAt"] = "2026-11-21T22:00:00+07:00"
                elif job["kind"] == "delete":
                    site["status"] = "deleted"
        return 200, {k: v for k, v in job.items() if k != "polls"}
    if len(p) >= 2 and p[0] == "sites":
        site = state.sites.get(p[1])
        if not site:
            return _err("SITE_NOT_FOUND", 404)
        if len(p) == 2 and method == "GET":
            return 200, site
        if len(p) == 3 and method == "POST" and p[2] in ("suspend", "resume", "backups"):
            return 202, {"jobId": _new_job(state, site["siteId"], {"backups": "backup"}.get(p[2], p[2]))}
        if len(p) == 3 and method == "PUT" and p[2] == "license":
            site["license"] = {"status": "ok" if str(body.get("key", "")).startswith("biz-") else "missing"}
            return 200, site
        if len(p) == 2 and method == "DELETE":
            if site["status"] != "suspended":
                return _err("SITE_NOT_SUSPENDED", 409)
            if not site["lastBackupAt"]:
                return _err("SITE_BACKUP_REQUIRED", 409)
            return 202, {"jobId": _new_job(state, site["siteId"], "delete")}
    return _err("NOT_FOUND", 404)


def serve(key: str, port: int = 0) -> tuple[ThreadingHTTPServer, FakeState]:
    """Mở máy chủ giả trên 127.0.0.1 (port 0 = cổng ngẫu nhiên). Trả (máy chủ, trạng thái); gọi server.shutdown() để dừng."""
    state = FakeState(key)

    class H(BaseHTTPRequestHandler):
        def _do(self) -> None:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"null") if n else None
            hdrs = {k.lower(): v for k, v in self.headers.items()}
            status, out = handle(state, self.command, self.path, hdrs, body)
            data = json.dumps(out, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_DELETE = _do

        def log_message(self, *_: Any) -> None:  # im lặng khi chạy test
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, state


if __name__ == "__main__":
    srv, _ = serve(sys.argv[2] if len(sys.argv) > 2 else "prov_test", int(sys.argv[1]) if len(sys.argv) > 1 else 8765)
    print(f"Provisioning giả: http://127.0.0.1:{srv.server_address[1]}{API_PREFIX}")
    threading.Event().wait()
