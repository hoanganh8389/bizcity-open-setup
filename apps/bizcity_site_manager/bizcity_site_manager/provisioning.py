# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: lớp gọi Provisioning API bizcity_site_provisioning@1 (bản nháp ở open-ketoan PHASE-039 §30); kiểm slug R-SLUG-1; không import frappe để chạy test bằng Python thuần
"""Lớp gọi Provisioning API của Open Kế Toán (`bizcity_site_provisioning@1`).

Không phụ thuộc Frappe: phần dán vào Frappe (đọc cấu hình, hàng đợi, DocType) nằm ở `site_manager.py`.

Luật của hợp đồng mà lớp này giữ:
- Mọi lệnh ghi gửi kèm `Idempotency-Key`; gửi lại cùng khoá thì Open Kế Toán trả đúng việc cũ (R-IDEM-1).
- Không gửi và không nhận chuỗi kết nối, tên database, mật khẩu database (R-ROLE-3).
- Lỗi có `code` cố định; `message` là câu tiếng Việt dễ hiểu để hiện cho người dùng.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

CONTRACT = "bizcity_site_provisioning@1"
# [2026-11-23 02:05 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — Cloudflare (Browser Integrity Check) chặn User-Agent mặc định "Python-urllib/3.x" bằng 403 error code 1010 trước khi tới Open Kế Toán (gặp thật: admin.openketoan.com qua Cloudflare). Gửi tên riêng.
USER_AGENT = "bizcity-site-manager/0.1 (+https://github.com/hoanganh8389/bizcity-open-setup)"
API_PREFIX = "/_sites/v1"

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{2,29}$")
RESERVED_SLUGS = frozenset(
    "www mail webmail ftp cpanel whm api admin open erp ketoan kiot app apps static cdn ns1 ns2 smtp pop imap test demo".split()
)

# Câu cho người dùng theo mã lỗi của hợp đồng (§5). Mã lạ → câu chung.
FRIENDLY = {
    "SITE_SLUG_INVALID": "Tên miền chỉ gồm chữ thường không dấu, số và dấu gạch, dài 3–30 ký tự, bắt đầu bằng chữ.",
    "SITE_SLUG_TAKEN": "Tên này đã có người dùng. Hãy chọn tên khác.",
    "SITE_DOMAIN_TAKEN": "Tên miền này đã có người dùng. Hãy chọn tên khác.",
    "SITE_BUSY": "Site đang có một việc khác chạy. Thử lại sau ít phút.",
    "SITE_NOT_SUSPENDED": "Phải khoá site trước khi xoá.",
    "SITE_BACKUP_REQUIRED": "Cần một bản sao lưu mới (trong 24 giờ) trước khi làm việc này.",
    "SITE_LIMIT_REACHED": "Hệ thống tạm đủ số site. Đội vận hành đã được báo.",
    "SITE_NOT_FOUND": "Không tìm thấy site.",
    "PROVISION_KEY_INVALID": "Site Manager chưa được phép gọi Open Kế Toán (khoá Provisioning sai hoặc đã thu hồi).",
    "IDEMPOTENCY_KEY_REUSED": "Lệnh này trùng mã với một lệnh khác. Tạo lại từ đầu.",
    "NETWORK": "Không nối được tới Open Kế Toán. Thử lại sau ít phút.",
}
GENERIC = "Có lỗi khi gọi Open Kế Toán. Đội vận hành đã được báo."


def check_slug(slug: str, extra_reserved: frozenset[str] | set[str] = frozenset()) -> str | None:
    """Kiểm slug theo R-SLUG-1. Trả None khi hợp lệ, hoặc mã lỗi `SITE_SLUG_INVALID`."""
    if not isinstance(slug, str) or not SLUG_RE.match(slug) or slug.endswith("-") or "--" in slug:
        return "SITE_SLUG_INVALID"
    if slug in RESERVED_SLUGS or slug in extra_reserved:
        return "SITE_SLUG_INVALID"
    return None


class ProvisioningError(Exception):
    """Lỗi từ Provisioning API hoặc đường mạng. `message` luôn là câu hiện được cho người dùng."""

    def __init__(self, code: str, http_status: int = 0, detail: str = ""):
        self.code = code
        self.http_status = http_status
        self.detail = detail  # chỉ để ghi nhật ký vận hành; không hiện cho người dùng
        super().__init__(FRIENDLY.get(code, GENERIC))

    @property
    def message(self) -> str:
        return str(self)


Transport = Callable[[urllib.request.Request, float], tuple[int, bytes]]


def _urllib_transport(req: urllib.request.Request, timeout: float) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:  # noqa: S310 — địa chỉ lấy từ cấu hình của quản trị
            return res.status, res.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


@dataclass
class ProvisioningClient:
    base_url: str
    key: str
    timeout: float = 15.0
    transport: Transport = _urllib_transport

    # ── lệnh đọc
    def health(self) -> dict[str, Any]:
        return self._call("GET", "/health")

    def get_site(self, site_id: str) -> dict[str, Any]:
        return self._call("GET", f"/sites/{_seg(site_id)}")

    def list_sites(self, updated_after: str | None = None, cursor: str | None = None) -> dict[str, Any]:
        q = {k: v for k, v in (("updatedAfter", updated_after), ("cursor", cursor)) if v}
        return self._call("GET", "/sites" + (("?" + urllib.parse.urlencode(q)) if q else ""))

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self._call("GET", f"/jobs/{_seg(job_id)}")

    # ── lệnh ghi (bắt buộc Idempotency-Key)
    def create_site(self, body: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        err = check_slug(str(body.get("slug", "")))
        if err:
            raise ProvisioningError(err, 400, "kiểm ở phía gọi")
        return self._call("POST", "/sites", body, idempotency_key)

    def suspend(self, site_id: str, idempotency_key: str) -> dict[str, Any]:
        return self._call("POST", f"/sites/{_seg(site_id)}/suspend", {}, idempotency_key)

    def resume(self, site_id: str, idempotency_key: str) -> dict[str, Any]:
        return self._call("POST", f"/sites/{_seg(site_id)}/resume", {}, idempotency_key)

    def backup(self, site_id: str, idempotency_key: str) -> dict[str, Any]:
        return self._call("POST", f"/sites/{_seg(site_id)}/backups", {}, idempotency_key)

    def delete(self, site_id: str, idempotency_key: str) -> dict[str, Any]:
        return self._call("DELETE", f"/sites/{_seg(site_id)}", None, idempotency_key)

    # [2026-11-22 10:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 W1c — lệnh mới của open-ketoan PR #590 (S039-22): mật khẩu ban đầu mới cho chủ site, trả một lần ở GET /jobs
    def reset_owner_password(self, site_id: str, idempotency_key: str) -> dict[str, Any]:
        return self._call("POST", f"/sites/{_seg(site_id)}/owner/reset-password", {}, idempotency_key)

    def set_license(self, site_id: str, license_key: str, idempotency_key: str) -> dict[str, Any]:
        """Gắn khoá bản quyền `biz-…` cho site (chỉ để cảnh báo hết hạn, D039-17). Site Manager không lưu khoá này."""
        return self._call("PUT", f"/sites/{_seg(site_id)}/license", {"key": license_key}, idempotency_key)

    # ── nội bộ
    def _call(self, method: str, path: str, body: Any = None, idempotency_key: str | None = None) -> dict[str, Any]:
        if method != "GET" and not idempotency_key:
            raise ProvisioningError("IDEMPOTENCY_KEY_REQUIRED", 0, f"{method} {path} thiếu Idempotency-Key")
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json", "X-Contract": CONTRACT, "User-Agent": USER_AGENT}
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        req = urllib.request.Request(self.base_url.rstrip("/") + API_PREFIX + path, data=data, method=method, headers=headers)
        try:
            status, raw = self.transport(req, self.timeout)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            raise ProvisioningError("NETWORK", 0, f"{method} {path}: {e}") from e
        payload: dict[str, Any] = {}
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
            except ValueError:
                payload = {}
        if 200 <= status < 300:
            return payload
        code = str((payload.get("error") or {}).get("code") or payload.get("code") or f"HTTP_{status}")
        raise ProvisioningError(code, status, f"{method} {path} → {status}")


def _seg(value: str) -> str:
    """Một đoạn đường dẫn an toàn (mã site / mã việc là ULID hoặc chuỗi do Open Kế Toán trả)."""
    return urllib.parse.quote(str(value), safe="")
