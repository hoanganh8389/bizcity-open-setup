# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: khai báo app bizcity_site_manager; đồng bộ Site Registry mỗi giờ

app_name = "bizcity_site_manager"
app_title = "Bizcity Site Manager"
app_publisher = "Johnny Chu (Chu Hoàng Anh) / BizCity"
app_description = "Site Manager: khách hàng, danh sách site kế toán, việc gửi sang Provisioning API của Bizcity Open Kế Toán"
app_email = "noreply@bizcity.vn"
app_license = "GPL-2.0-or-later"
required_apps = ["frappe"]

# [2026-11-22 10:20 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 W1d — vai Bizcity Site Operator tự có (install.py)
after_install = "bizcity_site_manager.install.ensure_roles"
after_migrate = ["bizcity_site_manager.install.ensure_roles"]

scheduler_events = {
	# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — xoá mật khẩu ban đầu không ai nhận sau 24 giờ
	"hourly": ["bizcity_site_manager.site_manager.sync_all", "bizcity_site_manager.site_manager.purge_owner_passwords"],
}
