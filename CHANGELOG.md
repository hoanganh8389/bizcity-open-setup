# Nhật ký thay đổi
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — mở nhật ký thay đổi. -->

Theo [Keep a Changelog](https://keepachangelog.com/); phiên bản theo SemVer khi có mã.

## [Chưa phát hành]

### 2026-11-21 (tối) — ADR-0001: Frappe là Site Manager, Open Kế Toán dùng chung, mỗi site một database

- Chủ dự án chốt mô hình: Frappe = giao diện điều hành và quản lý site; Open Kế Toán = ứng dụng kế toán dùng chung, độc lập với Frappe; PostgreSQL = mỗi site một database.
- Bỏ hướng "mỗi khách một Frappe site chạy ERPNext" và hướng "cổng Node + SQLite".
- Viết lại README, CANON (bốn câu mới, R-ROLE-1..3, R-KEY-1, R-IDEM-1), PHASE-001 (app `bizcity_site_manager`: 5 DocType, luồng tạo site, D001-1..11, Q001-1..2).
- Thêm LICENSE (GPL-2.0-or-later), TRADEMARK, SECURITY, CONTRIBUTING, AGENTS, CLAUDE.
- Phần việc bên Open Kế Toán: PHASE-039 của repo `open-ketoan`.

### 2026-11-21 (chiều) — khởi tạo, cài thử Frappe trên VPS

- Cài `frappe_docker` (ERPNext v15.125.0) trên VPS cPanel, tạo site thử `erp.btnet.vn`.
- Tìm ra nguyên nhân 502: Imunify360 chặn cổng đi ra 8080 (`port_blocking_mode: DENY`). Ghi ở sổ tay vận hành §6.
