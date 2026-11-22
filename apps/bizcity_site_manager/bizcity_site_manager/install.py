# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-22 10:20 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 W1d — vai "Bizcity Site Operator" (api.ALLOWED_ROLES) tự có sau khi cài / migrate; lệnh một lần tạo người dùng máy cho bizcity-web và in khoá `key:secret`
"""Cài đặt của app.

- `ensure_roles()` — chạy ở `after_install` và `after_migrate` (hooks.py): tạo vai `Bizcity Site Operator` nếu chưa có.
  Vai này chỉ gọi được REST `bizcity_site_manager.api.*` (create_site, job_status, sites_of, slug_available,
  reset_owner_password) — không vào màn quản trị (desk_access = 0).
- `create_operator_user(email)` — người vận hành chạy MỘT lần trên bench:

      bench --site open.bizcity.vn execute bizcity_site_manager.install.create_operator_user --kwargs "{'email': 'bizcity-web@bizcity.vn'}"

  In `<api_key>:<api_secret>` để đặt vào `BIZCITY_OPEN_SETUP_TOKEN` trong wp-config.php của bizcity.vn.
  Chạy lại thì cấp cặp khoá MỚI (khoá cũ hết dùng) — dùng khi lộ khoá.
"""

from __future__ import annotations

import frappe

OPERATOR_ROLE = "Bizcity Site Operator"


def ensure_roles() -> None:
	if not frappe.db.exists("Role", OPERATOR_ROLE):
		frappe.get_doc({"doctype": "Role", "role_name": OPERATOR_ROLE, "desk_access": 0}).insert(ignore_permissions=True)
		frappe.db.commit()


def create_operator_user(email: str) -> str:
	"""Tạo (hoặc lấy) người dùng máy có duy nhất vai Bizcity Site Operator; cấp cặp khoá API mới; trả `key:secret`."""
	ensure_roles()
	email = (email or "").strip().lower()
	if not email or "@" not in email:
		frappe.throw("Cần email cho người dùng máy (vd bizcity-web@bizcity.vn)")
	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
	else:
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": "bizcity-web",
			"user_type": "System User",
			"send_welcome_email": 0,
			"enabled": 1,
		}).insert(ignore_permissions=True)
	user.set("roles", [{"role": OPERATOR_ROLE}])
	user.api_key = user.api_key or frappe.generate_hash(length=15)
	secret = frappe.generate_hash(length=15)
	user.api_secret = secret
	user.save(ignore_permissions=True)
	frappe.db.commit()
	token = f"{user.api_key}:{secret}"
	print(token)
	return token
