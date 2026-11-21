# Bizcity Open Setup

<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] INIT — khởi tạo Bizcity Open Setup: cổng tự tạo phần mềm kế toán tại open.bizcity.vn. -->
<!-- [2026-11-21 09:18 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — vai trò PostgreSQL riêng từng site; luật nâng cấp một bản mã cho mọi site (open-ketoan ADR-0036, R-SITE). -->
<!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] D001-9 — bizcity-llm-router quản lý API key. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — đổi mô hình: Frappe chỉ là Site Manager; Open Kế Toán là ứng dụng dùng chung; mỗi site một database PostgreSQL. -->

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — thêm vai trục điều phối chương trình OKT. -->

**Nơi tạo và quản lý các site kế toán**, đồng thời là **trục điều phối chương trình OKT** (open-pos ⇄ open-ketoan, [docs/chuong-trinh/OKT/](docs/chuong-trinh/OKT/README.md)). Người dùng mở **open.bizcity.vn**, điền một form ngắn và nhận một phần mềm kế toán riêng ở tên miền riêng.

> **Frappe** = giao diện điều hành và quản lý site.
> **Open Kế Toán** = ứng dụng kế toán dùng chung, độc lập với Frappe.
> **PostgreSQL** = mỗi site một database và một vai trò PostgreSQL riêng. Một chuỗi có thể có hàng trăm cửa hàng trong một site.

> **Hiện trạng (2026-11-21):** giai đoạn 0. Đã có: Frappe chạy bằng Docker trên VPS ([sổ tay](docs/van-hanh/CAI-FRAPPE-TREN-VPS.md)), tài liệu kiến trúc và phase. **Chưa có** app `bizcity_site_manager`, **chưa có** Provisioning API bên Open Kế Toán (PHASE-039 của repo `open-ketoan`). Lần cài thử ERPNext cho từng khách (`erp.btnet.vn`) là hướng **đã bỏ**, xem [ADR-0001](docs/adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md).

## Mô hình triển khai

```text
┌──────────────────────────────────────────────────────────────────┐
│  FRAPPE — SITE MANAGER            (repo này)                     │
│  Một Frappe site quản trị · database MariaDB riêng               │
│  App bizcity_site_manager: khách hàng · danh sách site · việc    │
└──────────────────────────────┬───────────────────────────────────┘
                               │  Provisioning API  bizcity_site_provisioning@1
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  OPEN KẾ TOÁN — ỨNG DỤNG DÙNG CHUNG   (repo open-ketoan)         │
│  Một bản mã · React + Fastify + Accounting Kernel                │
│  Site Registry + Database Router                                 │
└───────────┬──────────────────────┬──────────────────────┬────────┘
            ▼                      ▼                      ▼
     SITE A  a.<miền>       SITE B  b.<miền>       SITE C  c.<miền>
     DB A · vai trò A       DB B · vai trò B       DB C · vai trò C
     chuỗi 500 cửa hàng     chuỗi 20 cửa hàng      1 cửa hàng
```

Tạo một site kế toán **không** tạo thêm Frappe site. Site Manager gọi Provisioning API; Open Kế Toán tạo database và một cặp vai trò PostgreSQL riêng cho site, chạy migration, ghi vào Site Registry và trả kết quả.

## Luật nâng cấp: một bản mã cho mọi site

Open Kế Toán nâng cấp theo đúng thứ tự này ([open-ketoan ADR-0036](https://github.com/hoanganh8389/open-ketoan/blob/main/docs/adr/ADR-0036-mot-ban-ma-moi-site-mot-database.md), luật R-SITE-8..10):

```text
GitHub: open-ketoan
        ↓
Kéo mã · build · test                 (bản đang chạy vẫn phục vụ)
        ↓
Một phiên bản Open Kế Toán mới
        ↓
Migration từng site DB                (kt_template trước; sao lưu trước mỗi site)
        ↓
Chuyển ứng dụng sang phiên bản mới
        ↓
Tất cả site dùng chung mã mới
```

Ứng dụng chỉ phục vụ site có lược đồ đúng bản nó cần. Site nâng lỗi dừng riêng, các site khác chạy tiếp. Site Manager hiện trạng thái `upgrading` / `migration_failed` của từng site và không tự chạy migration.

## Ai làm việc gì

| Việc | Site Manager (Frappe, repo này) | Open Kế Toán |
|---|---|---|
| Khách hàng, gói, hạn dùng | **chủ** | không biết |
| Danh sách site (bản điều hành) | **chủ** bản điều hành, đồng bộ từ registry | **chủ** Site Registry (domain → database) |
| Tạo / khoá / mở / xoá site | ra lệnh qua API | **thực hiện** |
| Database, migration, sao lưu | không chạm | **chủ** |
| Khoá bản quyền `biz-…` | chuyển tiếp khi tạo site, không lưu | gắn vào site; hết hạn thì hiện dải đỏ, **không chặn** |
| Tên miền gốc | **chủ** cấu hình (động: `btnet.vn`, `bizcity.vn`, `*.<miền>` bất kỳ) | nhận mọi tên miền |
| Sổ sách kế toán | không có | **chủ** |
| Nối WordPress | cửa REST của Frappe cho `bizcity-llm-router` gọi | không biết |

**`bizcity-llm-router` (plugin WordPress) là chủ khoá `biz-…`** và là nơi người dùng bấm "tạo kế toán". Nó giữ người dùng, ví và khoá; Site Manager giữ site; Open Kế Toán giữ sổ.

## Tài liệu

| Tệp | Nội dung |
|---|---|
| [docs/00-CANON.md](docs/00-CANON.md) | Tôn chỉ, bốn câu không thương lượng, danh mục luật |
| [ADR-0001](docs/adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md) | Vì sao Frappe chỉ là Site Manager và mỗi site một database |
| [PHASE-001](docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN/README.md) | App `bizcity_site_manager`: DocType, luồng, các đợt việc |
| [docs/chuong-trinh/OKT/](docs/chuong-trinh/OKT/README.md) | **Trục điều phối chương trình OKT** (open-pos ⇄ open-ketoan): ADR-OKT-1, roadmap, checklist (nguồn trạng thái duy nhất), phân việc, đánh giá |
| [docs/van-hanh/CAI-FRAPPE-TREN-VPS.md](docs/van-hanh/CAI-FRAPPE-TREN-VPS.md) | Cài Frappe trên VPS cPanel, các lỗi đã gặp |
| `open-ketoan` · `docs/phases/PHASE-039-NHIEU-CSDL-SITE-REGISTRY` | Phần việc bên Open Kế Toán và bản hợp đồng Provisioning |

## Giấy phép và nhãn hiệu

Mã nguồn: **GPL-2.0-or-later** ([LICENSE](LICENSE)). Tên và logo BizCity là nhãn hiệu, không đi kèm GPL ([TRADEMARK.md](TRADEMARK.md)). Kiến trúc do Johnny Chu (Chu Hoàng Anh) thiết kế.
