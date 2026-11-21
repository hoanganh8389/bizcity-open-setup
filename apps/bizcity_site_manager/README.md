# bizcity_site_manager
<!-- [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: khung app Frappe -->

App Frappe nhỏ của **Bizcity Open Setup** ([ADR-0001](../../docs/adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md)). Cài trên **một** Frappe site quản trị. Không giữ dữ liệu kế toán, không chạm PostgreSQL: mọi việc với site kế toán đi qua Provisioning API của Open Kế Toán.

| Phần | Tệp |
|---|---|
| Lớp gọi Provisioning API (`bizcity_site_provisioning@1`), không phụ thuộc Frappe | `bizcity_site_manager/provisioning.py` |
| Việc nền: gửi lệnh, hỏi trạng thái, đồng bộ mỗi giờ | `bizcity_site_manager/site_manager.py` |
| REST cho `bizcity-llm-router` | `bizcity_site_manager/api.py` |
| DocType `Bizcity Site Customer`, `Bizcity Ketoan Site`, `Bizcity Provision Job`, `Bizcity Site Manager Settings` (+ bảng con `Bizcity Site Root Domain`) | `bizcity_site_manager/bizcity_site_manager/doctype/` |
| Máy chủ Provisioning giả + ca kiểm | `bizcity_site_manager/tests/` |

Chạy ca kiểm (không cần Frappe):

```bash
cd apps/bizcity_site_manager
python -m unittest discover -s . -p "test_*.py" -v
```

Cài vào bench: `bench get-app <đường dẫn tới thư mục này>` rồi `bench --site <site quản trị> install-app bizcity_site_manager`. Cấu hình ở **Bizcity Site Manager Settings**: địa chỉ Provisioning API, khoá `prov_…`, bảng tên miền gốc.

Giấy phép GPL-2.0-or-later ([LICENSE](../../LICENSE)); nhãn hiệu BizCity: [TRADEMARK.md](../../TRADEMARK.md).
