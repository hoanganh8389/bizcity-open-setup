# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: site kế toán — kiểm slug (R-SLUG-1), tên miền gốc từ cấu hình (D001-2, R-DOMAIN-1), trần số site (D001-8)

import frappe
from frappe import _
from frappe.model.document import Document

from bizcity_site_manager.provisioning import FRIENDLY, check_slug


class BizcityKetoanSite(Document):
	def validate(self):
		self.slug = (self.slug or "").strip().lower()
		self.root_domain = (self.root_domain or "").strip().lower()
		settings = frappe.get_cached_doc("Bizcity Site Manager Settings")
		if check_slug(self.slug, settings.extra_reserved()):
			frappe.throw(_(FRIENDLY["SITE_SLUG_INVALID"]))
		if self.is_new():
			if self.root_domain not in settings.enabled_root_domains():
				frappe.throw(_("Tên miền gốc {0} chưa được bật trong cấu hình Site Manager.").format(self.root_domain))
			if settings.max_sites and frappe.db.count("Bizcity Ketoan Site", {"status": ["!=", "deleted"]}) >= settings.max_sites:
				frappe.throw(_(FRIENDLY["SITE_LIMIT_REACHED"]))
		self.domain = f"{self.slug}.{self.root_domain}"
