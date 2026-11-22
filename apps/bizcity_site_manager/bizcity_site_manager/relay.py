# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — phần thuần Python cho trang dùng thử kế toán của bizcity-web (bizcity-web PHASE-02 §3.3–3.5): hỏi việc có báo bước từng lần, nhặt mật khẩu ban đầu một lần, hình dạng job_status công khai, mã lỗi cố định cho API
"""Không import frappe để chạy test bằng Python thuần; phần dán vào Frappe ở `site_manager.py` / `api.py`.

Luật giữ ở đây:
- Mật khẩu ban đầu của chủ site Open Kế Toán chỉ trả ở lần đọc `GET /jobs/{id}` đầu tiên sau khi xong
  (hợp đồng `bizcity_site_provisioning@1`, B5a). Site Manager là bên đọc nên phải **nhặt** nó, giữ mã hoá,
  trả **một lần** cho đúng `external_ref` của khách, rồi xoá.
- API trả lỗi có `code` cố định để phía gọi (bizcity-web) không phải đoán theo câu chữ.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable

from bizcity_site_manager.provisioning import FRIENDLY, GENERIC, ProvisioningError

STEP_KEYS = ("validate", "create_database", "seed_owner", "activate")
STEP_STATES = ("pending", "running", "done", "failed")

# Mã lỗi của API Site Manager → (HTTP, câu cho người dùng). Mã của hợp đồng dùng lại câu ở FRIENDLY.
API_ERRORS: dict[str, tuple[int, str]] = {
    "SITE_SLUG_INVALID": (400, FRIENDLY["SITE_SLUG_INVALID"]),
    "SITE_SLUG_TAKEN": (409, FRIENDLY["SITE_SLUG_TAKEN"]),
    "SITE_DOMAIN_TAKEN": (409, FRIENDLY["SITE_DOMAIN_TAKEN"]),
    "ROOT_DOMAIN_NOT_ALLOWED": (400, "Tên miền gốc này chưa được bật cho site kế toán."),
    "TRIAL_EXISTS": (409, "Email này đã có một phần mềm kế toán dùng thử."),
    "SITE_LIMIT_REACHED": (503, FRIENDLY["SITE_LIMIT_REACHED"]),
    "JOB_NOT_FOUND": (404, "Không tìm thấy việc."),
}


def error_body(code: str) -> tuple[int, dict[str, Any]]:
    """(HTTP, thân lỗi) cho một mã lỗi của API. Mã lạ → 500 + câu chung."""
    status, message = API_ERRORS.get(code, (500, GENERIC))
    return status, {"error": {"code": code, "message": message}}


def parse_steps(raw: Any) -> list[dict[str, str]]:
    """Đọc trường `steps` (JSON) của Provision Job; chỉ giữ `key` / `status` hợp lệ."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw or "[]")
        except ValueError:
            return []
    out = []
    for s in raw or []:
        if isinstance(s, dict) and s.get("key") and s.get("status") in STEP_STATES:
            out.append({"key": str(s["key"]), "status": str(s["status"])})
    return out


def owner_from_result(result: dict[str, Any]) -> tuple[str, str] | None:
    """(email, mật khẩu ban đầu) nếu lần đọc này của Open Kế Toán có `owner.initialPassword`."""
    owner = result.get("owner") if isinstance(result, dict) else None
    if isinstance(owner, dict) and owner.get("initialPassword"):
        return str(owner.get("email") or ""), str(owner["initialPassword"])
    return None


def poll_job(
    client: Any,
    remote_job_id: str,
    every: float,
    timeout: float,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Hỏi `GET /jobs/{id}` tới khi `done` / `failed`. Mỗi lần đọc gọi `on_progress(job)` để ghi bước ngay
    (trang dùng thử hiện console theo bước). Lần đọc cuối — lần duy nhất có `owner` — được trả nguyên cho bên gọi."""
    deadline = clock() + timeout
    while True:
        job = client.get_job(remote_job_id)
        if on_progress:
            on_progress(job)
        if job.get("status") in ("done", "failed"):
            return job
        if clock() > deadline:
            raise ProvisioningError("JOB_TIMEOUT", 0, f"việc {remote_job_id} quá {int(timeout)} giây")
        sleep(every)


def public_job(
    *,
    status: str,
    kind: str,
    site: str | None,
    domain: str | None,
    steps_raw: Any,
    error_code: str | None,
    error_message: str | None,
    owner: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Hình dạng `job_status` trả cho phía gọi. `owner` chỉ có khi bên gọi vừa nhận mật khẩu lần duy nhất."""
    out: dict[str, Any] = {
        "status": status,
        "kind": kind,
        "site": site,
        "domain": domain,
        "steps": parse_steps(steps_raw),
        "error_code": error_code or None,
        "error_message": error_message or None,
    }
    if owner:
        out["owner"] = {"email": owner[0], "initialPassword": owner[1]}
    return out


def ref_matches(stored: str | None, given: str | None) -> bool:
    """`external_ref` bên gọi đưa phải trùng đúng `external_ref` của khách (không rỗng)."""
    return bool(given) and bool(stored) and str(stored) == str(given)
