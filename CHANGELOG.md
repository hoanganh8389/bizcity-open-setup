# Nhật ký thay đổi
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — mở nhật ký thay đổi. -->

Theo [Keep a Changelog](https://keepachangelog.com/); phiên bản theo SemVer khi có mã.

## [Chưa phát hành]

### Thêm (R-CORE-10 — Lõi trước)
- 2026-11-29 — <!-- [2026-11-29 01:19 AM Johnny Chu - Chu Hoàng Anh] R-CORE-10 --> khối chung "Lõi trước — bánh xe đóng góp" (`bizcity:loi-truoc@1`, chuẩn `bizcity_core_first@1`) trong AGENTS.md + mẫu PR có ô "Lõi hay app?".

### 2026-11-27 — ba vai nền (canon R-CANON-17)
- <!-- [2026-11-27 11:08 PM Johnny Chu - Chu Hoàng Anh] NC-003 — chủ chốt Q-CORE-1…4 --> AGENTS và `docs/canon/README`: open-setup cấp instance cho **mọi app trên open-core**; registry sẽ ghi `product`, `core_version`, `app_version` (bizcity-platform NC-003 C7).

### 2026-11-21 (khuya) — W1: khung app Frappe `bizcity_site_manager`
<!-- [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1 -->

- `apps/bizcity_site_manager/`: lớp gọi `bizcity_site_provisioning@1` (Idempotency-Key bắt buộc, kiểm slug, lỗi có mã + câu dễ hiểu), máy chủ Provisioning giả, 13 ca kiểm Python thuần.
- DocType `Bizcity Site Customer`, `Bizcity Ketoan Site`, `Bizcity Provision Job`, `Bizcity Site Manager Settings` + bảng con `Bizcity Site Root Domain`; việc nền gửi lệnh / hỏi trạng thái / đồng bộ mỗi giờ; REST `create_site`, `sites_of`, `job_status` cho `bizcity-llm-router`. Chưa thử trên bench.

### 2026-11-21 (tối) — vai trò PostgreSQL riêng từng site, luật nâng cấp

- Chủ dự án chốt: mỗi site một database **và một vai trò PostgreSQL riêng**, chung mã open-ketoan. Luật nâng cấp một bản mã cho mọi site ghi vào README, CANON, ADR-0001 (điểm 8). Bên open-ketoan: ADR-0036, luật R-SITE.

### 2026-11-21 (tối) — tên miền gốc động, khoá `biz-…` là khoá mềm

- Chủ dự án chốt Q001-1: tên miền gốc là cấu hình động (`btnet.vn`, `bizcity.vn`, `*.<miền>` bất kỳ), mỗi miền khai cách nối `wildcard` hoặc `cpanel` (D001-2, R-DOMAIN-1).
- Chủ dự án chốt: khoá `biz-…` chỉ để cảnh báo hết hạn. Hết hạn thì site vẫn dùng, có dải đỏ; không tự khoá, không tự xoá (D001-7, D001-9, câu 4 của CANON).

### 2026-11-21 (tối) — bizcity-llm-router quản lý API key

- Chủ dự án chốt Q001-2: `bizcity-llm-router` cấp, thu hồi và kiểm API key (`biz-…`). Bỏ DocType `Bizcity Site Api Key`; D001-9, D001-11, R-KEY-1 viết lại.

### 2026-11-21 (tối) — ADR-0001: Frappe là Site Manager, Open Kế Toán dùng chung, mỗi site một database

- Chủ dự án chốt mô hình: Frappe = giao diện điều hành và quản lý site; Open Kế Toán = ứng dụng kế toán dùng chung, độc lập với Frappe; PostgreSQL = mỗi site một database.
- Bỏ hướng "mỗi khách một Frappe site chạy ERPNext" và hướng "cổng Node + SQLite".
- Viết lại README, CANON (bốn câu mới, R-ROLE-1..3, R-KEY-1, R-IDEM-1), PHASE-001 (app `bizcity_site_manager`: 5 DocType, luồng tạo site, D001-1..11, Q001-1..2).
- Thêm LICENSE (GPL-2.0-or-later), TRADEMARK, SECURITY, CONTRIBUTING, AGENTS, CLAUDE.
- Phần việc bên Open Kế Toán: PHASE-039 của repo `open-ketoan`.

### 2026-11-21 (chiều) — khởi tạo, cài thử Frappe trên VPS

- Cài `frappe_docker` (ERPNext v15.125.0) trên VPS cPanel, tạo site thử `erp.btnet.vn`.
- Tìm ra nguyên nhân 502: Imunify360 chặn cổng đi ra 8080 (`port_blocking_mode: DENY`). Ghi ở sổ tay vận hành §6.
