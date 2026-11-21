# PHASE-001 — Site Manager: app Frappe `bizcity_site_manager` và cổng open.bizcity.vn
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] P001-INIT — mở phase 001: cổng tự tạo site kế toán. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — viết lại phase theo mô hình mới: Frappe chỉ quản lý site, Open Kế Toán cấp database qua Provisioning API; bỏ ERPNext, bỏ cổng Node + SQLite. -->

> **Trạng thái:** Đã chốt hướng ([ADR-0001](../../adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md)). Chưa có mã app.
> **Phụ thuộc:** PHASE-039 của repo `open-ketoan` (Site Registry, Database Router, Provisioner, Provisioning API). W2 trở đi của phase này chờ bước B5 bên đó.
> **Chủ phase:** chủ dự án (founder).

## 1. Mục tiêu (một câu)

Một thành viên vào **open.bizcity.vn**, điền form, và nhận một site kế toán Open Kế Toán chạy được ở tên miền riêng. Đội vận hành nhìn thấy mọi site, khách hàng, khoá và việc đang chạy trong **một** màn quản trị Frappe.

## 2. Ngoài phạm vi

- Mọi thứ thuộc PostgreSQL và Open Kế Toán: tạo database, migration, sao lưu, định tuyến theo tên miền. Đó là PHASE-039 bên `open-ketoan`.
- Thu tiền và gói trả phí: PHASE-002, đi qua ví Bizcity.
- Tên miền riêng của khách (`ketoan.congtya.vn`): PHASE-003.

## 3. App `bizcity_site_manager`

Một app Frappe nhỏ, cài trên **một** Frappe site quản trị (MariaDB). Năm DocType:

| DocType | Giữ gì | Trường chính |
|---|---|---|
| **Bizcity Site Customer** | Khách hàng | họ tên, công ty, email (đã xác nhận), số điện thoại, tỉnh/thành, `external_ref` (mã người dùng WordPress, để nối `bizcity-llm-router` sau này) |
| **Bizcity Ketoan Site** | Một site kế toán (bản điều hành) | `slug`, `domain`, khách hàng, `site_id` (do Open Kế Toán trả), trạng thái (`pending` · `provisioning` · `active` · `suspended` · `failed` · `deleted`), gói, hạn dùng, `app_version`, `schema_version`, `last_backup_at`, dung lượng |
| **Bizcity Site Api Key** | Dấu vết khoá API của một site | site, nhãn, **tiền tố** khoá, phạm vi, người xin, ngày cấp, ngày thu hồi. **Không lưu giá trị khoá** (R-KEY-1) |
| **Bizcity Provision Job** | Nhật ký một lệnh gửi sang Open Kế Toán | loại lệnh, `idempotency_key`, `job_id` bên kia, trạng thái, các bước, lỗi (mã + câu dễ hiểu) |
| **Bizcity Site Manager Settings** (Single) | Cấu hình | địa chỉ Provisioning API, khoá Provisioning (`Password`), tên miền gốc, số ngày dùng thử, trần số site, danh sách slug cấm |

Phần mã ngoài DocType:

| Thành phần | Việc |
|---|---|
| `provisioning_client.py` | Lớp gọi `bizcity_site_provisioning@1`: ký khoá, gắn `Idempotency-Key`, đổi lỗi thành mã + câu dễ hiểu |
| Việc nền (hàng đợi Frappe) | Gửi lệnh, hỏi trạng thái việc tới khi xong, cập nhật `Bizcity Ketoan Site` |
| Việc định kỳ (scheduler) | Đồng bộ trạng thái / phiên bản / sao lưu từ registry mỗi giờ; khoá site hết hạn dùng thử |
| Trang web `/dang-ky` (www của Frappe) | Form đăng ký công khai, kiểm slug, OTP email, màn tiến trình |
| REST cho WordPress | `bizcity_site_manager.api.*`: tạo khách, tạo site, xem site của một `external_ref` |

## 4. Luồng tạo site

```text
Người dùng (open.bizcity.vn/dang-ky)
   │ họ tên · công ty · email · số điện thoại · tên miền mong muốn · ☑ điều khoản
   ▼
Site Manager: kiểm slug (R-SLUG-1) + chống lạm dụng (R-ABUSE-1) → gửi OTP email
   ▼ (OTP đúng)
Tạo Bizcity Site Customer + Bizcity Ketoan Site (pending) + Bizcity Provision Job
   ▼ việc nền
POST {Open Kế Toán}/_sites/v1/sites     Idempotency-Key = mã việc
   ▼ 202 { jobId, siteId }
GET  /_sites/v1/jobs/{jobId}  (hỏi lại mỗi 2 giây)
   ▼ done
Bizcity Ketoan Site = active  →  email "Site của bạn đã sẵn sàng" + nút mở site
```

Open Kế Toán làm phần còn lại: tạo database, chạy migration, tạo đơn vị đầu và tài khoản quản trị mang email của khách, ghi `domain → database` vào Site Registry. Hợp đồng đầy đủ nằm ở `open-ketoan` · `docs/phases/PHASE-039-NHIEU-CSDL-SITE-REGISTRY/30-HOP-DONG-PROVISIONING.md`.

## 5. Quyết định đã chốt

| Mã | Quyết định | Vì sao |
|---|---|---|
| **D001-1** — vai của Frappe | Chỉ **một** Frappe site quản trị, cài `frappe` + `bizcity_site_manager`. Không ERPNext, không Frappe site cho từng khách | ADR-0001: tránh hai hệ multisite song song |
| **D001-2** — tên miền site kế toán | `<slug>.<tên miền gốc>`, với **một tên miền gốc riêng cho kế toán** có wildcard trỏ thẳng vào Open Kế Toán. Tạo site mới **không** đụng cPanel. Trong lúc chờ chọn tên miền: tạo từng subdomain trên `btnet.vn` để thử | `*.btnet.vn` đang phục vụ WordPress multisite, không đổi được. Wildcard riêng thì SSL Universal của Cloudflare phủ sẵn |
| **D001-3** — tên miền Site Manager | `open.bizcity.vn` → Frappe (subdomain cPanel + proxy, cách đã chạy được) | Một site duy nhất, tạo tay một lần |
| **D001-4** — CSDL của Site Manager | **MariaDB 10.6** (đổi từ 11.8 khi dựng site quản trị) | Frappe v15 cảnh báo chưa thử 11.8; cùng họ MySQL với WordPress |
| **D001-5** — image | Build image riêng từ `frappe_docker` với `apps.json` = `frappe` + `bizcity_site_manager` | Image `frappe/erpnext` không có app của mình |
| **D001-6** — xác nhận danh tính | Email OTP 6 số ở v1; đăng nhập qua tài khoản WordPress Bizcity ở v1.1 | Đơn giản, không phụ thuộc bên ngoài |
| **D001-7** — dùng thử | 30 ngày. Hết hạn thì gửi lệnh `suspend` (site chỉ đọc). Sau 90 ngày không gia hạn: `backup` → `delete` | R-DATA-1 |
| **D001-8** — trần | 1 site dùng thử / email / số điện thoại; 3 lượt / IP / ngày; trần tổng cấu hình được | R-ABUSE-1 |
| **D001-9** — khoá API của site | Site Manager **xin** Open Kế Toán cấp (`POST /_sites/v1/sites/{id}/api-keys`), hiện cho người dùng **một lần**, chỉ lưu tiền tố + nhãn | Một nơi cấp, một nơi kiểm; lộ CSDL quản trị không lộ khoá |
| **D001-10** — ai là chủ sự thật | Open Kế Toán là chủ Site Registry. Bảng `Bizcity Ketoan Site` là bản điều hành, đồng bộ lại mỗi giờ; lệch thì tin registry | Open Kế Toán phải chạy được khi không có Frappe |
| **D001-11** — nối WordPress | WordPress / `bizcity-llm-router` gọi REST của Frappe bằng khoá API Frappe; khách nối với người dùng WordPress qua `external_ref` | Site Manager là một cửa cho mọi kênh bán |

## 6. Câu còn mở

| Mã | Câu hỏi | Đề nghị |
|---|---|---|
| **Q001-1** | Tên miền gốc cho các site kế toán là gì? | Một tên miền riêng, ngắn, chỉ dùng cho kế toán |
| **Q001-2** | `bizcity-llm-router` giữ vai gì: chỉ là nơi người dùng bấm "tạo kế toán", hay cũng giữ danh sách site và khoá? | Chỉ là nơi bấm và hiển thị; danh sách và khoá ở Site Manager (một chủ) |

## 7. Các đợt việc

| Đợt | Việc | Xong khi |
|---|---|---|
| **W0 — Nền máy chủ** | ~~W0-1 sửa 502~~ ✅ (Imunify360 `TCP_OUT_IPv4` + `8080`) · W0-2 dựng image riêng + MariaDB 10.6 + site quản trị `open.bizcity.vn`, xoá `erp.btnet.vn` · W0-3 bật cPHulk / SSH key | Đăng nhập được Frappe ở `open.bizcity.vn` |
| **W1 — Khung app** | Tạo app `bizcity_site_manager`, 5 DocType, quyền (vai `Bizcity Site Operator`), `provisioning_client.py` chạy với **máy chủ giả** theo đúng hợp đồng | Tạo site trên màn quản trị → việc chạy → site `active` (với máy chủ giả); gửi trùng không tạo site thứ hai |
| **W2 — Nối Open Kế Toán thật** | Trỏ sang Provisioning API thật (sau B5 của PHASE-039); việc đồng bộ mỗi giờ; khoá / mở / sao lưu / xoá từ màn quản trị | Tạo một site thật, đăng nhập được Open Kế Toán bằng email của khách |
| **W3 — Cổng đăng ký** | Trang `/dang-ky`, kiểm slug, OTP, màn tiến trình, email xong | Người ngoài đội tự tạo site trên điện thoại, không hỏi ai |
| **W4 — Vận hành** | Hết hạn dùng thử tự khoá; cấp / thu hồi khoá API; REST cho WordPress | Đội vận hành không phải SSH cho việc thường ngày |

## 8. Nghiệm thu phase

1. Người ngoài đội, trên điện thoại: từ lúc mở `open.bizcity.vn` tới lúc vào màn kế toán **≤ 2 phút**.
2. Tạo 2 site cách nhau 1 phút: không bên nào thấy dữ liệu bên kia; mỗi bên một database.
3. Gửi cùng một lệnh tạo hai lần (cùng `Idempotency-Key`): chỉ có một site.
4. Tắt Frappe: các site kế toán đang chạy **vẫn dùng bình thường**.
5. Xem CSDL của Site Manager: không có giá trị khoá API nào ở dạng đọc được.
6. Lệnh xoá site chưa có bản sao lưu mới: bị từ chối.

## 9. Rủi ro

| Mã | Rủi ro | Cách giữ |
|---|---|---|
| R-1 | PHASE-039 chậm thì phase này đứng ở W1 | W1 dùng máy chủ giả theo hợp đồng; hai phía làm song song |
| R-2 | Hợp đồng đổi giữa chừng | Hợp đồng có số phiên bản `@1`; đổi phải qua PR ở `open-ketoan` |
| R-3 | VPS dùng chung với zalo-hub và WordPress | Ba điều cấm ở AGENTS.md; theo dõi RAM |
| R-4 | Lạm dụng tạo site hàng loạt | R-ABUSE-1, OTP, trần tổng |
