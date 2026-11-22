# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: REST cho bizcity-llm-router (D001-11) — tạo site, hỏi site của một người dùng WordPress, hỏi trạng thái việc; một site dùng thử mỗi email (R-ABUSE-1)
# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — phía gọi là trang dùng thử của bizcity-web (bizcity-web PHASE-02 D02-1/D02-2): lỗi có `code` cố định (relay.API_ERRORS), `sample`, `slug_available`, `job_status` trả bước ngay + mật khẩu ban đầu MỘT lần cho đúng `external_ref`
"""Gọi bằng khoá API Frappe của một người dùng có vai trò được phép (máy chủ gọi máy chủ):
`POST /api/method/bizcity_site_manager.api.create_site` …

Lỗi: HTTP 4xx/5xx, thân `{"message": {"error": {"code": "…", "message": "…"}}}` (Frappe bọc kết quả trong `message`).

Không có API key của khách ở đây: khoá `biz-…` thuộc bizcity-llm-router (R-KEY-1).
"""

from __future__ import annotations

import frappe

from bizcity_site_manager import site_manager
from bizcity_site_manager.provisioning import check_slug
from bizcity_site_manager.relay import error_body, public_job, ref_matches

ALLOWED_ROLES = ("System Manager", "Bizcity Site Operator")


def _fail(code: str) -> dict:
	status, body = error_body(code)
	frappe.local.response["http_status_code"] = status
	return body


def _reserved() -> set[str]:
	raw = frappe.db.get_single_value("Bizcity Site Manager Settings", "reserved_slugs") or ""
	return {s.strip().lower() for s in raw.replace(",", "\n").splitlines() if s.strip()}


def _root_allowed(root_domain: str) -> bool:
	"""Tên miền gốc phải có trong bảng tên miền gốc đang bật; bảng rỗng thì nhận mọi tên (đang dựng)."""
	rows = frappe.get_all("Bizcity Site Root Domain", filters={"parenttype": "Bizcity Site Manager Settings"}, fields=["domain", "enabled"])
	if not rows:
		return True
	return any(r.enabled and (r.domain or "").strip().lower() == root_domain for r in rows)


@frappe.whitelist(methods=["POST"])
def create_site(
	full_name: str,
	company_name: str,
	email: str,
	slug: str,
	root_domain: str,
	phone: str | None = None,
	province: str | None = None,
	external_ref: str | None = None,
	sample: int | str | bool | None = None,
) -> dict:
	frappe.only_for(ALLOWED_ROLES)
	email = (email or "").strip().lower()
	slug = (slug or "").strip().lower()
	root_domain = (root_domain or "").strip().lower()
	if check_slug(slug, _reserved()):
		return _fail("SITE_SLUG_INVALID")
	if not _root_allowed(root_domain):
		return _fail("ROOT_DOMAIN_NOT_ALLOWED")
	if frappe.db.exists("Bizcity Ketoan Site", slug):
		return _fail("SITE_SLUG_TAKEN")

	customer = frappe.db.get_value("Bizcity Site Customer", {"email": email}, "name")
	if customer and frappe.db.count("Bizcity Ketoan Site", {"customer": customer, "status": ["not in", ["failed", "deleted"]]}):
		return _fail("TRIAL_EXISTS")
	if not customer:
		customer = frappe.get_doc({
			"doctype": "Bizcity Site Customer",
			"full_name": full_name,
			"company_name": company_name,
			"email": email,
			"phone": phone,
			"province": province,
			"external_ref": external_ref or None,
		}).insert(ignore_permissions=True).name

	site = frappe.get_doc({
		"doctype": "Bizcity Ketoan Site",
		"slug": slug,
		"root_domain": root_domain,
		"customer": customer,
		"sample": 1 if str(sample).lower() in ("1", "true", "yes") else 0,
	})
	site.insert(ignore_permissions=True)
	job = site_manager.start(site.name, "provision")
	return {"site": site.name, "domain": site.domain, "job": job}


@frappe.whitelist(methods=["GET"])
def slug_available(slug: str) -> dict:
	"""Cho ô "địa chỉ" của trang dùng thử: hợp lệ không, còn trống không (theo sổ Site Manager)."""
	frappe.only_for(ALLOWED_ROLES)
	slug = (slug or "").strip().lower()
	if check_slug(slug, _reserved()):
		return {"slug": slug, "valid": False, "available": False}
	return {"slug": slug, "valid": True, "available": not frappe.db.exists("Bizcity Ketoan Site", slug)}


@frappe.whitelist(methods=["GET"])
def sites_of(external_ref: str) -> list[dict]:
	frappe.only_for(ALLOWED_ROLES)
	customers = frappe.get_all("Bizcity Site Customer", filters={"external_ref": external_ref}, pluck="name")
	if not customers:
		return []
	return frappe.get_all(
		"Bizcity Ketoan Site",
		filters={"customer": ["in", customers], "status": ["!=", "deleted"]},
		fields=["slug", "domain", "status", "license_status", "last_backup_at"],
		order_by="creation asc",
	)


@frappe.whitelist(methods=["GET"])
def job_status(job: str, external_ref: str | None = None) -> dict:
	"""Trạng thái việc, đọc ngay từ bản ghi (việc nền ghi bước sau mỗi lần hỏi Open Kế Toán).

	Có `external_ref`: phải trùng khách của site, không trùng → JOB_NOT_FOUND; việc provision xong thì lần
	hỏi đầu tiên kèm `owner` (mật khẩu ban đầu) rồi xoá. Không có `external_ref`: không bao giờ kèm mật khẩu.
	"""
	frappe.only_for(ALLOWED_ROLES)
	if not frappe.db.exists("Bizcity Provision Job", job):
		return _fail("JOB_NOT_FOUND")
	d = frappe.get_doc("Bizcity Provision Job", job)
	site = frappe.db.get_value("Bizcity Ketoan Site", d.site, ["domain", "customer"], as_dict=True) or frappe._dict()

	owner = None
	if external_ref is not None:
		stored = frappe.db.get_value("Bizcity Site Customer", site.customer, "external_ref") if site.customer else None
		if not ref_matches(stored, external_ref):
			return _fail("JOB_NOT_FOUND")
		if d.kind == "provision" and d.status == "done":
			owner = site_manager.take_owner(d.name)

	return public_job(
		status=d.status,
		kind=d.kind,
		site=d.site,
		domain=site.domain,
		steps_raw=d.steps,
		error_code=d.error_code,
		error_message=d.error_message,
		owner=owner,
	)
