# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: khai báo app bizcity_site_manager; đồng bộ Site Registry mỗi giờ

app_name = "bizcity_site_manager"
app_title = "Bizcity Site Manager"
app_publisher = "Johnny Chu (Chu Hoàng Anh) / BizCity"
app_description = "Site Manager: khách hàng, danh sách site kế toán, việc gửi sang Provisioning API của Bizcity Open Kế Toán"
app_email = "noreply@bizcity.vn"
app_license = "GPL-2.0-or-later"
required_apps = ["frappe"]

scheduler_events = {
	"hourly": ["bizcity_site_manager.site_manager.sync_all"],
}
