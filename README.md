# Bizcity Open Setup

<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] INIT — khởi tạo Bizcity Open Setup: cổng tự tạo phần mềm kế toán tại open.bizcity.vn. -->

**Cổng tự tạo phần mềm kế toán.** Người dùng mở **open.bizcity.vn**, điền một form ngắn, chờ vài phút, nhận một phần mềm kế toán riêng ở tên miền riêng (`congtya.btnet.vn`), đăng nhập bằng email của mình.

> Một bộ máy chạy chung, mỗi doanh nghiệp một site và một cơ sở dữ liệu riêng. Người dùng không cài gì, không gặp kỹ thuật viên.

> **Hiện trạng (2026-11-21):** giai đoạn 0. Đã có: bộ máy Frappe/ERPNext v15.125.0 chạy bằng Docker trên VPS cPanel và script tạo site bằng tay ([ops/new-tenant.sh](ops/new-tenant.sh)), đã tạo được site `erp.btnet.vn`. **Site này đang lỗi 502** khi truy cập qua Cloudflare (việc W0). **Chưa có cổng web.** Bước kế tiếp là [PHASE-001](docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN/README.md).

## Luồng người dùng

```text
open.bizcity.vn
  │  Họ tên · Tên công ty · Số điện thoại · Email · Tên miền mong muốn · Tỉnh/thành · ☑ điều khoản
  ▼
Xác nhận email (mã 6 số)
  ▼
Màn chờ có tiến trình  ──  tạo CSDL → cài kế toán → gắn tên miền → tạo tài khoản
  ▼
"Xong": https://congtya.btnet.vn  + email đặt mật khẩu
```

## Kiến trúc

```text
Internet ─ Cloudflare ─ Apache (cPanel)
                          ├─ open.bizcity.vn ──► Cổng Open Setup  127.0.0.1:8095  (user opensetup, không root)
                          │                          │ sudo chỉ một lệnh
                          │                          ▼
                          │                     ops/provision-tenant.sh  (root, tự kiểm tham số)
                          │                          │ bench new-site · uapi subdomain · proxy.conf
                          └─ <slug>.btnet.vn ───► Frappe/ERPNext  127.0.0.1:8090  (docker compose -p erp)
                                                     một bộ container, nhiều site, mỗi site một CSDL MariaDB
```

## Tài liệu

| Tệp | Nội dung |
|---|---|
| [docs/00-CANON.md](docs/00-CANON.md) | Tôn chỉ, bốn câu không thương lượng, danh mục luật |
| [docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN](docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN/README.md) | Phase đầu: cổng tự tạo, các đợt W0–W4, quyết định đã chốt |
| [docs/van-hanh/CAI-FRAPPE-TREN-VPS.md](docs/van-hanh/CAI-FRAPPE-TREN-VPS.md) | Cách cài bộ máy Frappe/ERPNext lên VPS cPanel (đã chạy thật ngày 2026-11-21) |
| [docs/phases/CLAIMS.md](docs/phases/CLAIMS.md) | Bảng giữ chỗ việc đang làm |

## Cùng hệ sinh thái

[open-ketoan](https://github.com/hoanganh8389) (sổ cái kế toán của Bizcity) · open-kiot (bán lẻ) · Zalo Brain / Cell (trợ lý AI). Open Setup chỉ là **cổng tạo và vận hành site**, không chứa nghiệp vụ kế toán. Bộ máy kế toán được cắm vào qua một giao diện chung (`engine`). v1 dùng ERPNext; open-ketoan có thể là engine thứ hai.
