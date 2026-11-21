# ADR-0001 — Frappe là Site Manager; Open Kế Toán là ứng dụng dùng chung; mỗi site một database
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — chủ dự án chốt mô hình triển khai, thay hướng cài ERPNext cho từng khách. -->

> **Trạng thái:** Chấp nhận (chủ dự án, 2026-11-21) · **Thay thế:** các quyết định D001-1, D001-2, D001-10, D001-11 của PHASE-001 bản đầu.

## Bối cảnh

Ngày 2026-11-21 đã cài thử Frappe + ERPNext trên VPS và tạo `erp.btnet.vn` theo kiểu "mỗi khách một Frappe site chạy ERPNext". Hướng đó sai với mục tiêu:

- Sản phẩm kế toán của Bizcity là **Open Kế Toán** (React + Fastify + Accounting Kernel, PostgreSQL), không phải ERPNext.
- Nếu Frappe cũng tạo site cho từng khách thì phải vận hành **hai hệ multisite song song** (Frappe site và site kế toán) cho cùng một khách.

## Quyết định

1. **Frappe = giao diện điều hành và quản lý site.** Chỉ có **một** Frappe site quản trị, database MariaDB riêng. Không cài ERPNext.
2. **Open Kế Toán = ứng dụng dùng chung, độc lập với Frappe.** Một bản mã từ GitHub phục vụ mọi site. Open Kế Toán chạy được khi không có Frappe.
3. **PostgreSQL = mỗi site một database và một vai trò riêng** (vai trò riêng chốt 2026-11-21; open-ketoan ADR-0036). <!-- [2026-11-21 09:18 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — vai trò riêng từng site --> Một site là một doanh nghiệp hoặc một chuỗi; bên trong vẫn có nhiều đơn vị và chi nhánh như hôm nay.
4. **Mượn cơ chế của Frappe, không mượn dữ liệu.** Open Kế Toán tự có Site Registry (domain → database), Database Router, Site Provisioner, Migration Runner, Backup Manager — đây là PHASE-039 của repo `open-ketoan`.
5. **Một app Frappe nhỏ `bizcity_site_manager`** giữ khách hàng, danh sách site, nhật ký việc và gọi **Provisioning API** của Open Kế Toán. Khi một thành viên tạo kế toán mới, app yêu cầu Open Kế Toán cấp database mới; **không** tạo thêm Frappe site.
6. **Site Manager dùng MariaDB** để sau này nối với WordPress và `bizcity-llm-router` (cùng họ MySQL, cùng máy chủ).
7. **API key do `bizcity-llm-router` quản lý** (chủ dự án chốt 2026-11-21). Plugin WordPress này cấp, thu hồi và kiểm khoá `biz-…`. Site Manager và Open Kế Toán không cấp khoá riêng cho khách. <!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — thêm điểm 7 -->
8. **Luật nâng cấp một bản mã cho mọi site** (open-ketoan R-SITE-8): kéo mã → build → test → một phiên bản mới → migration từng site → chuyển ứng dụng → mọi site dùng chung mã mới. Site Manager không chạy migration; chỉ đọc trạng thái từ registry. <!-- [2026-11-21 09:18 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — điểm 8 -->

## Hệ quả

**Được:**
- Một hệ multisite duy nhất (của Open Kế Toán). Tạo site là tạo database, không dựng thêm ứng dụng.
- Cập nhật một lần: kéo mã → build → test → migration từng site → chuyển ứng dụng sang bản mới → mọi site dùng mã mới.
- Frappe cho sẵn màn quản trị, phân quyền, REST, hàng đợi nền; không phải viết cổng quản trị từ đầu.

**Phải trả:**
- Open Kế Toán phải làm PHASE-039 trước khi Site Manager tạo được site thật.
- Hai kho, một hợp đồng: `bizcity_site_provisioning@1` do `open-ketoan` làm chủ; đổi hợp đồng phải đổi cả hai phía.
- Cần image Frappe riêng có app `bizcity_site_manager` (image `frappe/erpnext` đang chạy không có app này).

## Số phận phần đã cài ngày 2026-11-21

| Thứ | Xử lý |
|---|---|
| Bộ container `-p erp` (Frappe + ERPNext v15.125.0) | Giữ làm chỗ thử cho đến khi có image riêng; sau đó thay bằng image `frappe` + `bizcity_site_manager` |
| Site `erp.btnet.vn` | Site thử, **không** dùng cho khách; xoá khi dựng site quản trị |
| `ops/new-tenant.sh` | Không dùng để tạo site cho khách nữa; giữ làm mẫu dựng **một** site quản trị |
| Bài học tường lửa Imunify360, `httpd -t`, proxy Apache | Vẫn đúng, giữ ở sổ tay vận hành |

## Phương án đã cân nhắc và bỏ

| Phương án | Vì sao bỏ |
|---|---|
| Mỗi khách một Frappe site chạy ERPNext | Sai sản phẩm; ERPNext chưa có chuẩn kế toán Việt Nam |
| Mỗi khách một Frappe site **và** một site Open Kế Toán | Hai hệ multisite song song, gấp đôi việc vận hành |
| Viết lại Open Kế Toán thành app Frappe | Bỏ Accounting Kernel đã có; khoá vào Frappe |
| Cổng quản trị tự viết (Node + SQLite) như bản PHASE-001 đầu | Phải tự làm phân quyền, màn quản trị, hàng đợi; Frappe có sẵn |
| Một database chung, tách bằng `tenant_id` cho mọi khách | Đã có RLS theo đơn vị, nhưng sao lưu / khôi phục / chuyển máy riêng từng khách rất khó; chuỗi lớn ảnh hưởng chuỗi nhỏ |
