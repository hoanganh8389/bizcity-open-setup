# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: cấu hình Site Manager — tên miền gốc động (D001-2), tên cấm thêm, khoá Provisioning ở trường mật khẩu (R-KEY-1)

import frappe
from frappe import _
from frappe.model.document import Document

from bizcity_site_manager.provisioning import ProvisioningClient


class BizcitySiteManagerSettings(Document):
	def validate(self):
		seen = set()
		for row in self.root_domains or []:
			row.domain = (row.domain or "").strip().lower().lstrip("*.").rstrip(".")
			if row.domain in seen:
				frappe.throw(_("Tên miền gốc {0} bị khai hai lần.").format(row.domain))
			seen.add(row.domain)
		if self.provisioning_url:
			self.provisioning_url = self.provisioning_url.strip().rstrip("/")
			if not self.provisioning_url.startswith("https://") and not frappe.conf.get("developer_mode"):
				frappe.throw(_("Địa chỉ Provisioning API phải là https://."))

	def enabled_root_domains(self) -> list[str]:
		return [r.domain for r in self.root_domains or [] if r.enabled]

	def extra_reserved(self) -> set[str]:
		return {x.strip().lower() for x in (self.reserved_slugs or "").splitlines() if x.strip()}

	def client(self) -> ProvisioningClient:
		if not self.provisioning_url:
			frappe.throw(_("Chưa cấu hình địa chỉ Provisioning API."))
		key = self.get_password("provisioning_key", raise_exception=False)
		if not key:
			frappe.throw(_("Chưa nhập khoá Provisioning."))
		return ProvisioningClient(self.provisioning_url, key)
