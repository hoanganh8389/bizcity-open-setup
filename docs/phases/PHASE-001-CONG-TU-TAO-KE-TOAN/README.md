# PHASE-001 — Site Manager: app Frappe `bizcity_site_manager` và cổng open.bizcity.vn
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] P001-INIT — mở phase 001: cổng tự tạo site kế toán. -->
<!-- [2026-11-21 07:46 PM Johnny Chu - Chu Hoàng Anh] D001-2 — chủ dự án chốt Q001-1 (tên miền gốc động) và ý nghĩa khoá biz-… (khoá mềm cảnh báo hết hạn); D001-2, D001-7, D001-9 viết lại. -->
<!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] D001-9 — chủ dự án chốt Q001-2: bizcity-llm-router quản lý API key (khoá biz-…); bỏ DocType Bizcity Site Api Key, Site Manager không cấp và không lưu khoá. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — viết lại phase theo mô hình mới: Frappe chỉ quản lý site, Open Kế Toán cấp database qua Provisioning API; bỏ ERPNext, bỏ cổng Node + SQLite. -->

> **Trạng thái:** Đã chốt hướng ([ADR-0001](../../adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md)). Chưa có mã app.
> **Phụ thuộc:** PHASE-039 của repo `open-ketoan` (Site Registry, Database Router, Provisioner, Provisioning API). W2 trở đi của phase này chờ bước B5 bên đó.
> **Chủ phase:** chủ dự án (founder).

## 1. Mục tiêu (một câu)

Một thành viên vào **open.bizcity.vn**, điền form, và nhận một site kế toán Open Kế Toán chạy được ở tên miền riêng. Đội vận hành nhìn thấy mọi site, khách hàng và việc đang chạy trong **một** màn quản trị Frappe.

## 2. Ngoài phạm vi

- Mọi thứ thuộc PostgreSQL và Open Kế Toán: tạo database, migration, sao lưu, định tuyến theo tên miền. Đó là PHASE-039 bên `open-ketoan`.
- Thu tiền và gói trả phí: PHASE-002, đi qua ví Bizcity.
- Tên miền riêng của khách (`ketoan.congtya.vn`): PHASE-003.

## 3. App `bizcity_site_manager`

Một app Frappe nhỏ, cài trên **một** Frappe site quản trị (MariaDB). Bốn DocType:

| DocType | Giữ gì | Trường chính |
|---|---|---|
| **Bizcity Site Customer** | Khách hàng | họ tên, công ty, email (đã xác nhận), số điện thoại, tỉnh/thành, `external_ref` = mã người dùng WordPress (chủ khoá `biz-…` bên `bizcity-llm-router`) |
| **Bizcity Ketoan Site** | Một site kế toán (bản điều hành) | `slug`, `domain`, khách hàng, `site_id` (do Open Kế Toán trả), trạng thái (`pending` · `provisioning` · `active` · `suspended` · `failed` · `deleted`), gói, hạn dùng, `app_version`, `schema_version`, `last_backup_at`, dung lượng |
| **Bizcity Provision Job** | Nhật ký một lệnh gửi sang Open Kế Toán | loại lệnh, `idempotency_key`, `job_id` bên kia, trạng thái, các bước, lỗi (mã + câu dễ hiểu) |
| **Bizcity Site Manager Settings** (Single) | Cấu hình | địa chỉ Provisioning API, khoá Provisioning (`Password`), bảng **tên miền gốc** (tên miền · bật · cách nối), trần số site, danh sách slug cấm |

Phần mã ngoài DocType:

| Thành phần | Việc |
|---|---|
| `provisioning_client.py` | Lớp gọi `bizcity_site_provisioning@1`: ký khoá, gắn `Idempotency-Key`, đổi lỗi thành mã + câu dễ hiểu |
| Việc nền (hàng đợi Frappe) | Gửi lệnh, hỏi trạng thái việc tới khi xong, cập nhật `Bizcity Ketoan Site` |
| Việc định kỳ (scheduler) | Đồng bộ trạng thái / phiên bản / sao lưu / bản quyền từ registry mỗi giờ |
| Trang web `/dang-ky` (www của Frappe) | Form đăng ký công khai, kiểm slug, OTP email, màn tiến trình |
| REST cho WordPress | `bizcity_site_manager.api.*`: tạo khách, tạo site, xem site của một `external_ref`. `bizcity-llm-router` gọi vào đây khi người dùng bấm "tạo kế toán" |

**API key không nằm ở app này.** `bizcity-llm-router` cấp, thu hồi và kiểm khoá `biz-…` (bảng `bizcity_llm_api_keys`: băm SHA-256, theo người dùng WordPress, có `allowed_domain`). Site Manager chỉ biết "người dùng WordPress nào là chủ site nào".

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
| **D001-2** — tên miền site kế toán | **Tên miền gốc là cấu hình động** (chủ dự án chốt 2026-11-21): `btnet.vn`, `bizcity.vn` hoặc bất kỳ `*.<miền>` nào. Bảng con *Tên miền gốc* trong `Bizcity Site Manager Settings`, mỗi dòng: tên miền, bật / tắt, **cách nối** (`wildcard` = cả `*.<miền>` đã trỏ vào Open Kế Toán, tạo site không đụng máy chủ; `cpanel` = tạo từng subdomain + proxy, dùng cho miền có wildcard đang thuộc ứng dụng khác như `*.btnet.vn` của WordPress). Người dùng chọn tên miền gốc trên form | Thêm hoặc đổi tên miền gốc là sửa cấu hình, không sửa mã |
| **D001-3** — tên miền Site Manager | `open.bizcity.vn` → Frappe (subdomain cPanel + proxy, cách đã chạy được) | Một site duy nhất, tạo tay một lần |
| **D001-4** — CSDL của Site Manager | **MariaDB 10.6** (đổi từ 11.8 khi dựng site quản trị) | Frappe v15 cảnh báo chưa thử 11.8; cùng họ MySQL với WordPress |
| **D001-5** — image | Build image riêng từ `frappe_docker` với `apps.json` = `frappe` + `bizcity_site_manager` | Image `frappe/erpnext` không có app của mình |
| **D001-6** — xác nhận danh tính | Email OTP 6 số ở v1; đăng nhập qua tài khoản WordPress Bizcity ở v1.1 | Đơn giản, không phụ thuộc bên ngoài |
| **D001-7** — hết hạn | **Khoá mềm** (chủ dự án chốt 2026-11-21): hết hạn thì site **vẫn dùng đầy đủ**, chỉ có **dải đỏ cảnh báo** trên mọi màn. Không tự khoá, không tự xoá. Lệnh `suspend` / `delete` chỉ do người vận hành ra tay | Sổ kế toán không dừng vì chuyện gia hạn; dấu đỏ đủ khó chịu để nhắc |
| **D001-8** — trần | 1 site dùng thử / email / số điện thoại; 3 lượt / IP / ngày; trần tổng cấu hình được | R-ABUSE-1 |
| **D001-9** — khoá `biz-…` | `bizcity-llm-router` cấp và quản lý khoá `biz-…`. Với site kế toán, khoá này là **khoá bản quyền để cảnh báo hết hạn**, không phải cửa đăng nhập. Khi tạo site, Site Manager nhận khoá từ `bizcity-llm-router` và chuyển cho Open Kế Toán gắn vào site (`PUT /_sites/v1/sites/{id}/license`); Site Manager **không lưu** giá trị khoá. Trạng thái khoá (`ok` · `expiring` · `expired` · `missing`) đọc lại từ Open Kế Toán để hiện ở màn quản trị | Một nơi cấp và gia hạn cho cả hệ sinh thái |
| **D001-10** — ai là chủ sự thật | Open Kế Toán là chủ Site Registry. Bảng `Bizcity Ketoan Site` là bản điều hành, đồng bộ lại mỗi giờ; lệch thì tin registry | Open Kế Toán phải chạy được khi không có Frappe |
| **D001-11** — nối WordPress | `bizcity-llm-router` gọi REST của Frappe (máy chủ gọi máy chủ, một khoá hệ thống của Frappe đặt trong cấu hình plugin); khách nối với người dùng WordPress qua `external_ref`. Site Manager trả lời câu "người dùng này có những site nào" | Mỗi bên một việc: router giữ người dùng và khoá, Site Manager giữ site |

## 6. Câu còn mở

| Mã | Câu hỏi | Đề nghị |
|---|---|---|
| ~~Q001-1~~ | ~~Tên miền gốc cho các site kế toán~~ | **Đã chốt 2026-11-21:** động, theo cấu hình (D001-2) |
| ~~Q001-2~~ | ~~Vai của `bizcity-llm-router`~~ | **Đã chốt 2026-11-21:** `bizcity-llm-router` quản lý API key (D001-9). Danh sách site vẫn ở Site Manager |

## 7. Các đợt việc

| Đợt | Việc | Xong khi |
|---|---|---|
| **W0 — Nền máy chủ** | ~~W0-1 sửa 502~~ ✅ (Imunify360 `TCP_OUT_IPv4` + `8080`) · W0-2 dựng image riêng + MariaDB 10.6 + site quản trị `open.bizcity.vn`, xoá `erp.btnet.vn` · W0-3 bật cPHulk / SSH key | Đăng nhập được Frappe ở `open.bizcity.vn` |
| **W1 — Khung app** | Tạo app `bizcity_site_manager`, 4 DocType, quyền (vai `Bizcity Site Operator`), `provisioning_client.py` chạy với **máy chủ giả** theo đúng hợp đồng | Tạo site trên màn quản trị → việc chạy → site `active` (với máy chủ giả); gửi trùng không tạo site thứ hai |
| **W2 — Nối Open Kế Toán thật** | Trỏ sang Provisioning API thật (sau B5 của PHASE-039); việc đồng bộ mỗi giờ (kể cả trạng thái bản quyền); khoá / mở / sao lưu / xoá từ màn quản trị | Tạo một site thật, đăng nhập được Open Kế Toán bằng email của khách |
| **W3 — Cổng đăng ký** | Trang `/dang-ky`, kiểm slug, OTP, màn tiến trình, email xong | Người ngoài đội tự tạo site trên điện thoại, không hỏi ai |
| **W4 — Vận hành** | Bảng tên miền gốc (hai cách nối); cột trạng thái bản quyền; REST cho `bizcity-llm-router` (tạo site, hỏi site của một người dùng) | Đội vận hành không phải SSH cho việc thường ngày |

## 8. Nghiệm thu phase

1. Người ngoài đội, trên điện thoại: từ lúc mở `open.bizcity.vn` tới lúc vào màn kế toán **≤ 2 phút**.
2. Tạo 2 site cách nhau 1 phút: không bên nào thấy dữ liệu bên kia; mỗi bên một database.
3. Gửi cùng một lệnh tạo hai lần (cùng `Idempotency-Key`): chỉ có một site.
4. Tắt Frappe: các site kế toán đang chạy **vẫn dùng bình thường**.
5. Xem CSDL của Site Manager: không có bảng hay trường nào chứa API key của khách.
6. Lệnh xoá site chưa có bản sao lưu mới: bị từ chối.
7. Site hết hạn: vẫn ghi sổ được, mọi màn có dải đỏ; màn quản trị hiện `expired`.
8. Thêm một tên miền gốc mới trong cấu hình: form đăng ký có ngay lựa chọn đó, không sửa mã.

## 9. Rủi ro

| Mã | Rủi ro | Cách giữ |
|---|---|---|
| R-1 | PHASE-039 chậm thì phase này đứng ở W1 | W1 dùng máy chủ giả theo hợp đồng; hai phía làm song song |
| R-2 | Hợp đồng đổi giữa chừng | Hợp đồng có số phiên bản `@1`; đổi phải qua PR ở `open-ketoan` |
| R-3 | VPS dùng chung với zalo-hub và WordPress | Ba điều cấm ở AGENTS.md; theo dõi RAM |
| R-4 | Lạm dụng tạo site hàng loạt | R-ABUSE-1, OTP, trần tổng |
