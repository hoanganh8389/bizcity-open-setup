# CANON — Chỉ mục luật Bizcity Open Setup
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] INIT — khởi tạo chỉ mục luật Open Setup. -->
<!-- [2026-11-21 07:46 PM Johnny Chu - Chu Hoàng Anh] R-DATA-1 — hết hạn chỉ cảnh báo (khoá mềm); tên miền gốc động (R-DOMAIN-1). -->
<!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] R-KEY-1 — bizcity-llm-router là chủ API key; Site Manager không cấp, không lưu khoá của khách. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — viết lại theo mô hình Frappe Site Manager + Open Kế Toán dùng chung + mỗi site một database. -->

> **Phiên bản:** 0.2 · 2026-11-21 · **Trạng thái:** Đề xuất, chưa có mã app · **Người giữ:** chủ dự án
> **Cùng hệ quy ước** với CANON của open-ketoan / open-kiot: cấp luật Tier 0/1/2, phase `PHASE-NNN-*`, dấu R-SIG, bảng giữ chỗ R-FLOW.

## 0. Tôn chỉ

**Ai cũng tự tạo được phần mềm kế toán của mình trong vài phút, và dữ liệu của doanh nghiệp này không bao giờ chạm tới doanh nghiệp khác.**

Ba vai, không lẫn:

- **Frappe** = giao diện điều hành và quản lý site.
- **Open Kế Toán** = ứng dụng kế toán dùng chung, độc lập với Frappe.
- **PostgreSQL** = mỗi site một database.

## 1. Bốn câu không thương lượng

1. **Frappe không giữ dữ liệu kế toán.** Site Manager chỉ giữ khách hàng, danh sách site và nhật ký việc (R-ROLE-1).
2. **Một site kế toán không phải một Frappe site.** Chỉ có một Frappe site quản trị. Tạo site kế toán là gọi Provisioning API để Open Kế Toán cấp một database (R-ROLE-2).
3. **Site Manager không chạm PostgreSQL.** Tạo / khoá / mở / sao lưu / xoá đều qua `bizcity_site_provisioning@1`. Open Kế Toán là chủ Site Registry (R-ROLE-3).
4. **Hết hạn không dừng sổ; không xoá dữ liệu của khách mà không sao lưu trước.** Hết hạn chỉ hiện dải đỏ cảnh báo, site vẫn dùng. Khoá và xoá chỉ do người vận hành ra lệnh; xoá chỉ chạy sau khi có bản sao lưu đã kiểm (R-DATA-1).

## 2. Danh mục luật

| Mã | Cấp | Một câu | Kiểm bằng |
|---|---|---|---|
| R-ROLE-1 | 0 | Không DocType nào của Site Manager chứa chứng từ, bút toán, số dư | đọc danh sách DocType của app |
| R-ROLE-2 | 0 | Không `bench new-site` cho từng khách | tìm `new-site` trong mã app và `ops/` (chỉ được có ở phần dựng site quản trị) |
| R-ROLE-3 | 0 | App không có chuỗi kết nối PostgreSQL, không gọi `psql` / `pg_dump` | tìm `postgres://`, `psycopg`, `pg_dump` trong mã app |
| R-DATA-1 | 0 | Khoá trước, sao lưu trước, xoá sau | lệnh xoá bị API từ chối khi chưa có bản sao lưu mới; nhật ký việc có dòng `backup ok` trước dòng `drop` |
| R-KEY-1 | 0 | **Khoá `biz-…` do `bizcity-llm-router` cấp và quản lý**; với site kế toán nó là khoá bản quyền để cảnh báo hết hạn, không chặn truy cập. Site Manager không có DocType khoá. Khoá Provisioning (máy chủ gọi máy chủ) ở trường `Password` của Frappe | đọc danh sách DocType; tìm `biz-` trong CSDL quản trị phải ra rỗng |
| R-PRIV-1 | 0 | Tiến trình web không có quyền root; script root tự kiểm tham số | đọc sudoers; ca thử tham số độc bị từ chối |
| R-IDEM-1 | 1 | Mọi lệnh ghi gửi sang Open Kế Toán có `Idempotency-Key`; gửi lại không tạo site thứ hai | ca thử gửi trùng |
| R-JOB-1 | 1 | Mỗi lệnh là một việc có nhật ký từng bước; hỏng thì dừng, báo câu dễ hiểu kèm mã việc | đọc `Bizcity Provision Job` |
| R-SLUG-1 | 1 | `^[a-z][a-z0-9-]{2,29}$`, không kết thúc bằng `-`, không nằm trong danh sách cấm | unit test bộ kiểm slug (cả hai phía) |
| R-ABUSE-1 | 1 | Một email đã xác nhận và một số điện thoại: 1 site dùng thử; mỗi IP tối đa 3 lượt/ngày; tổng số site có trần | unit test + đếm |
| R-DOMAIN-1 | 1 | Tên miền gốc lấy từ cấu hình, không ghi cứng trong mã; mỗi tên miền gốc khai cách nối `wildcard` hoặc `cpanel` | tìm `btnet.vn`, `bizcity.vn` trong mã app phải ra rỗng |
| R-NAME-1 | 2 | App `bizcity_site_manager`; DocType tiền tố `Bizcity `; hàm / hook Python tiền tố `bizcity_` | người duyệt nhắc |
| R-SIG | 2 | Mọi thay đổi có dòng `[giờ thật Johnny Chu - Chu Hoàng Anh] MÃ — việc`; không ghi tên agent | người duyệt nhắc |

## 3. Đổi X thì sửa Y (cùng một PR)

| Đổi | Phải sửa cùng |
|---|---|
| Hợp đồng `bizcity_site_provisioning@N` | sửa ở `open-ketoan` trước (chủ hợp đồng) → lớp gọi API của app → PHASE-001 §4 |
| DocType của app | PHASE-001 §3, bảng "Ai làm việc gì" ở README |
| Luật chống lạm dụng / cảnh báo hết hạn | PHASE-001 §5, điều khoản trên form |
| Cổng, tên miền, tường lửa của máy chủ | `ops/*.sh`, [CAI-FRAPPE-TREN-VPS](van-hanh/CAI-FRAPPE-TREN-VPS.md) |
