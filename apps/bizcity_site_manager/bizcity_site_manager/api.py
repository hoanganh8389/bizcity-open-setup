# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: REST cho bizcity-llm-router (D001-11) — tạo site, hỏi site của một người dùng WordPress, hỏi trạng thái việc; một site dùng thử mỗi email (R-ABUSE-1)
"""Gọi bằng khoá API Frappe của một người dùng có vai trò được phép (máy chủ gọi máy chủ):
`POST /api/method/bizcity_site_manager.api.create_site` …

Không có API key của khách ở đây: khoá `biz-…` thuộc bizcity-llm-router (R-KEY-1).
"""

from __future__ import annotations

import frappe
from frappe import _

from bizcity_site_manager import site_manager
from bizcity_site_manager.provisioning import FRIENDLY, check_slug

ALLOWED_ROLES = ("System Manager", "Bizcity Site Operator")


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
) -> dict:
	frappe.only_for(ALLOWED_ROLES)
	email = (email or "").strip().lower()
	slug = (slug or "").strip().lower()
	if check_slug(slug):
		frappe.throw(_(FRIENDLY["SITE_SLUG_INVALID"]))
	if frappe.db.exists("Bizcity Ketoan Site", slug):
		frappe.throw(_(FRIENDLY["SITE_SLUG_TAKEN"]))

	customer = frappe.db.get_value("Bizcity Site Customer", {"email": email}, "name")
	if customer and frappe.db.count("Bizcity Ketoan Site", {"customer": customer, "status": ["not in", ["failed", "deleted"]]}):
		frappe.throw(_("Email này đã có một phần mềm kế toán dùng thử."))
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

	site = frappe.get_doc({"doctype": "Bizcity Ketoan Site", "slug": slug, "root_domain": root_domain, "customer": customer})
	site.insert(ignore_permissions=True)
	job = site_manager.start(site.name, "provision")
	return {"site": site.name, "domain": site.domain, "job": job}


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
def job_status(job: str) -> dict:
	frappe.only_for(ALLOWED_ROLES)
	d = frappe.get_doc("Bizcity Provision Job", job)
	return {"status": d.status, "kind": d.kind, "site": d.site, "error_code": d.error_code, "error_message": d.error_message}
