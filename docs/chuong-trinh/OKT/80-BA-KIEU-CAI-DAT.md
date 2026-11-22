<!-- [2026-11-23 01:30 AM Johnny Chu - Chu Hoàng Anh] OKT-TOPO — chủ hỏi: chuyển local_product_name → wp_global_product_name thế nào; bảng local / global có giống nhau không; bridge phải làm chủ ba kiểu cài (multisite + đệm global · một blog trên bizcity · localhost một site). Mọi số trong tài liệu là đo thật 23/11. -->
# OKT · 80 — Ba kiểu cài đặt: bridge phải chạy đúng ở cả ba

> **Đọc khi:** cài open-pos / open-pos-backend / open-ketoan-bridge ở nơi khác bizcity; viết mã đọc / ghi option, bảng, blog; review PR có `get_blog_option`, `switch_to_blog`, `get_sites`, `base_prefix`.
> **Trạng thái việc:** chỉ ở [40](40-CHECKLIST.md) (nhóm OKT-TOPO). **Câu chờ chủ:** [90](90-CAU-HOI-CHO-CHU.md) Q-OKT-3…5.

## 0. Trả lời ngắn

| Câu hỏi | Trả lời (đo 23/11) |
|---|---|
| Bảng `local_product_name` và `wp_global_product_name` có giống nhau không? | **Không.** 39 cột vs 43 cột; bỏ tiền tố `local_` / `global_` thì 35 cột trùng tên. Nhóm hàng khác hơn: `local_product_cat` 11 cột, **không có `code`, `path`**; `global_product_cat` 16 cột (§1) |
| Chuyển `wp_{N}_local_product_name` → `wp_global_product_name` được không? | Được về kỹ thuật nhưng **không nên làm**: phải đổi tên 35 cột, bỏ 4 cột, bù 10 cột; nhóm hàng phải dựng lại `code` / `path`; **id của các blog đụng nhau** trong một bảng chung → mọi dòng sổ kho cũ phải đánh lại khoá. Hướng đã chốt là ngược lại: global → bảng của blog `{prefix}tgs_catalog_*` (cùng cột global, giữ id — Q001-18, SW1-1) (§1.3) |
| Bridge có chạy ở cả ba kiểu cài không? | **Chưa.** Kiểu 2 (multisite, khoá theo blog) chạy thật hằng ngày trên `okt-wp`. Kiểu 3 (một site) **kích hoạt được nhưng gãy khi chạy**: tự kiểm, tạm dừng, trạng thái danh mục lỗi fatal (§3). Kiểu 1 (mạng một tenant + đệm global) chạy bằng đường cũ đang định gỡ (§2.1) |

## 1. Bảng local và global

### 1.1 Sản phẩm (WordPress thử `okt-wp`, MariaDB 10.11)

| | `wp_local_product_name` | `wp_global_product_name` | `wp_2_tgs_catalog_product` (SW1-1) |
|---|---|---|---|
| Số cột | 39 | 43 | 46 = global + 3 |
| Tiền tố cột | `local_product_*` | `global_product_*` | `global_product_*` |
| Chỉ bảng này có | `source_blog_id`, `product_quantity_no_tracking`, `…_logs`, `is_under_24m` | `product_is_kct`, `product_is_main`, `product_item_id` (ULID), `product_parent_item_id`, `product_variant`, `product_send_tax`, `product_htsoft_type`, `product_htsoft_bit1`, `id_sync_api`, `meta_sync_api` | `source`, `erp_synced_at`, `erp_hash` |
| Dòng (thử) | 0 | 1 | 0 |

10 cột chỉ global có chính là **định danh và cờ thuế kế toán cần** (`item_id`, `is_kct`, `send_tax`, `is_main` cho DM14). Bảng local cũ không chở được chúng.

### 1.2 Nhóm hàng

| `wp_local_product_cat` (11 cột) | `wp_global_product_cat` (16 cột) |
|---|---|
| `local_product_cat_id`, `global_product_cat_id`, `local_cat_parent_id`, `local_product_cat_name`, `global_product_cat_name`, `local_product_cat_status`, `user_id`, `is_deleted`, `deleted_at`, `created_at`, `updated_at` | `global_product_cat_id`, **`_code`**, `_name`, **`_path`**, `_note`, `_status`, `user_id`, `is_deleted`, `deleted_at`, `created_at`, `updated_at`, `blog_id_active`, `source_sync_htsoft`, `id_sync_api`, `meta_sync_api`, `global_product_cat_parent_id` |

Không có `code` / `path` thì không dựng được mã SKU theo nhóm cấp 3 (SW4) và không ánh xạ được nhóm sang kế toán.

### 1.3 Nếu vẫn muốn chuyển local → global

| Việc | Khó | Ghi chú |
|---|---|---|
| Đổi tên 35 cột `local_product_*` → `global_product_*` | thấp | đúng bảng `product_field_map` cũ của `TGS_Shop_Query` (đã gỡ ở SW1-3 vì là bẫy) |
| 4 cột chỉ local | trung bình | `source_blog_id` → `global_blog_id`; `quantity_no_tracking(_logs)` bỏ; `is_under_24m` → bảng `global_milk_under24m` |
| 10 cột chỉ global | trung bình | bù mặc định; `item_id` = NULL tới khi khớp với kế toán |
| Nhóm hàng | cao | dựng `code`, `path` từ cây `local_cat_parent_id`; trùng tên giữa các blog phải gộp hoặc tách |
| **Id** | **cao** | `wp_2_…` và `wp_5_…` đều có id 1, 2, 3… → vào một bảng chung phải **cấp id mới** → đánh lại `local_ledger_item.global_product_name_id` của mọi phiếu cũ. Trái Q001-13 (chép giữ id) |
| Trùng SKU giữa các blog | cao | bảng global có UNIQUE SKU → hai shop cùng SKU khác tên / giá thì một bên mất |

**Khuyến nghị:** không chuyển local → global. Bảng `local_product_name` cũ chỉ cần **đo** ở site thật (OKT-TOPO-1: đếm dòng theo blog, chỉ đọc). Blog nào có dữ liệu thì chép sang `{prefix}tgs_catalog_product` bằng tool chép (S001-C12 / SW1-6) có bảng ánh xạ cột ở §1.3, không qua bảng global.

## 2. Ba kiểu cài

| | **Kiểu 1 — "Chuỗi"** (lựa chọn 1 của chủ) | **Kiểu 2 — "Blog trên bizcity"** (lựa chọn 2) | **Kiểu 3 — "Một site"** (lựa chọn 3) |
|---|---|---|---|
| WordPress | multisite tự cài | multisite bizcity (92 blog) | một site, localhost hoặc host riêng |
| Một tenant ứng với | **cả mạng** (mỗi blog = một chi nhánh) | **một blog** (I-1) | **cả site** (blog 1) |
| Khoá kế toán | một khoá mạng (`key_legacy`, SC-1 🟡 hôm nay) | khoá riêng từng blog | khoá của site |
| Danh mục ở đâu | `wp_global_*` (bảng **đệm chung**, cờ `tgs_catalog_store = global`) | `{prefix}tgs_catalog_*` (cờ `local`) | `wp_tgs_catalog_*` hoặc `wp_global_*` — một site thì hai bảng cùng của một shop (Q-OKT-5) |
| Giá theo blog | bảng giá gán chi nhánh (`price_list_blog`) | bảng giá của blog | bảng giá của site |
| Ai kéo danh mục | **một** lượt kéo cho cả mạng, vào bảng global | `TGS_Acc_Catalog_Pull` theo blog (C8) | như kiểu 2, blog 1 |
| `prefix` / `base_prefix` | `wp_N_` / `wp_` | `wp_N_` / `wp_` | **`wp_` / `wp_` (trùng nhau)** |
| Hàm `get_blog_option`, `switch_to_blog`, `get_sites` | có | có | **không có** (WordPress chỉ nạp `ms-blogs.php`, `ms-functions.php` khi multisite — `wp-settings.php:154-158, 450-454`) |

### 2.1 Kiểu 1 và bất biến I-1

I-1 viết "một blog = một shop = một tenant". Kiểu 1 là **ngoại lệ có chủ đích**: một tenant cho cả mạng, blog là chi nhánh. Đây chính là cách bizcity đang chạy hôm nay (tenant `tgs`, `branches.external_ref = 'blog:N'` — doc 25 §9) và là đường mà bridge cũ phục vụ:
- khoá chung `key_legacy()` (`class-tgs-acc-config.php:133`);
- bộ kéo `TGS_Acc_Catalog_Sync` kéo **vào bảng global** (`class-tgs-acc-catalog-sync.php:10, 65`) — đang định gỡ (B001-C7).

Muốn giữ kiểu 1 thì ADR phải nói rõ (Q-OKT-3): "**một mạng = một tenant** được phép khi cả mạng là một pháp nhân"; khi đó tự kiểm đổi luật SC-3 (nhiều blog cùng tenant là **đúng** nếu cùng mạng và mỗi blog một chi nhánh khác nhau), `docKey` vẫn `btsoft:{blog}:…` (không đụng nhau), và **không gỡ** bộ kéo vào global mà chuyển nó thành chế độ `network` của bộ kéo C8.

### 2.2 Kiểu 3 khác kiểu 2 ở đâu

Một site là "mạng một blog". Bảng `wp_global_*` và `wp_tgs_catalog_*` đều chỉ của một shop, nên I-1 tự đúng. Khác biệt **chỉ ở API của WordPress**: mọi lời gọi hàm multisite phải đi qua một lớp bao (§4). `prefix = base_prefix` làm mọi phép "bảng của blog ≠ bảng mạng" thành sai: bảng của blog 1 và bảng mạng **trùng tên tiền tố** — với `tgs_catalog_*` thì không sao (tên khác `global_*`), nhưng mã nào suy "blog chính" từ tiền tố sẽ sai.

## 3. Đo thật kiểu 3 (23/11)

Dựng `okt-wp1`: `wordpress:php8.1-apache`, MariaDB 10.11, **không** `WP_ALLOW_MULTISITE`, cùng ba plugin (mã `main` + SW1-3 / SW1-4a đang review), nối mạng tới `okt-thu`.

| Bước | Kết quả |
|---|---|
| Cài WordPress, `is_multisite()` | `false`, `prefix = base_prefix = wp_` |
| Kích hoạt tsm (64 migration), tgs_pos, bridge | ✅ không lỗi |
| `wp tgs-acc status --shop=1` | ⚠ chạy, nhưng `Table 'wp_tgs_acc_push_log' doesn't exist` (bảng nhật ký chỉ tạo khi gửi lần đầu) |
| `wp tgs-catalog status --shop=1` (tsm SW1-1) | 🔴 **Fatal**: `Call to undefined function get_blog_option()` — `class-tgs-catalog-store.php:268` (lệnh CLI; `store()` thì có rẽ nhánh) |
| `TGS_Acc_Events::pause(1)` (bridge) | 🔴 **Fatal**: `update_blog_option()` — `class-tgs-acc-events.php:814` |
| `wp tgs-acc selfcheck --shop=1` (I-8) | 🔴 **Fatal**: `update_blog_option()` — `class-tgs-acc-selfcheck.php:456` (lưu kết quả). **Luật tối thượng không chạy được ở kiểu 3** |
| `wp tgs-acc reconcile --shop=1` | ✅ chạy (báo đỏ đúng: chưa khai URL vì bước khoá bị fatal trước) |

Mức phụ thuộc (đếm lời gọi trong mã chạy, `main` 23/11):

| Repo | `get_blog_option` | `update_blog_option` | `delete_blog_option` | `switch_to_blog` | `get_sites` | chỗ đã có kiểm `is_multisite` / `function_exists` |
|---|---|---|---|---|---|---|
| open-ketoan-bridge | 18 | 8 | 3 | 4 | 7 | 24 |
| open-pos-backend | 15 | 6 | 0 | 23 | 15 | 30 |
| open-pos | 24 | 4 | 0 | 21 | 14 | 36 |

## 4. Phương án để bridge làm chủ ba kiểu

| | A. Polyfill hàm WP | **B. Lớp bao riêng (khuyến nghị)** | C. Chỉ hỗ trợ multisite |
|---|---|---|---|
| Cách | định nghĩa `get_blog_option`… khi chưa có | `TGS_Acc_Site::opt($blog, $k)`, `set()`, `del()`, `in_blog($blog, fn)`, `blogs()`, `main()`, `topology()`; tsm / pos có bản cùng API | cài một site thì bật multisite một blog |
| Ưu | một chỗ, không sửa mã gọi | rõ ràng, test được, không lừa ai | không phải làm gì |
| Nhược | **lừa plugin khác**: `function_exists('switch_to_blog')` là cách phổ biến để đoán multisite — bridge tự dùng 24 chỗ | sửa ~40 lời gọi ở bridge, ~60 ở tsm, ~63 ở pos | shop nhỏ tự cài phải cấu hình multisite; không đúng chỉ đạo "standalone đầy đủ" |
| Kiểm bằng máy | khó | census `--check=MS0`: 0 lời gọi thẳng ngoài lớp bao | — |

**Khuyến nghị B**, làm ở bridge trước (bridge là đường nối, luật I-8 phải chạy ở mọi kiểu), rồi tsm, rồi pos. Thêm vào lớp bao:
- `topology()` = `single` | `multisite-blog-tenant` | `multisite-network-tenant` — tính từ `is_multisite()` và chế độ khoá (một khoá mạng = kiểu 1);
- tự kiểm **SC-0b "kiểu cài"**: in kiểu, cảnh báo cấu hình trái kiểu (vd kiểu 3 mà có khoá mạng; kiểu 2 mà một khoá dùng cho nhiều blog);
- SC-3 theo kiểu: kiểu 1 cho phép nhiều blog cùng tenant nếu **khác chi nhánh**, kiểu 2 thì đỏ như hôm nay.

## 5. Ma trận kiểm thử (mỗi ô = một ca chạy thật trên môi trường của cột)

Môi trường: **T1** = `okt-wp` với một khoá mạng cho shop-a + shop-b, hai chi nhánh CN01 / CN02 của cùng tenant · **T2** = `okt-wp` như hôm nay (khoá theo blog) · **T3** = `okt-wp1` (một site).
Ký hiệu: ✅ đã chạy đạt · 🔴 đã chạy, gãy · ⚠ chạy, có lỗi phụ · ☐ chưa chạy · — không áp dụng.

| # | Năng lực | T1 chuỗi | T2 blog bizcity | T3 một site |
|---|---|---|---|---|
| X1 | Kích hoạt 3 plugin, tạo bảng | ☐ | ✅ | ✅ |
| X2 | Khai khoá / URL / chi nhánh | ☐ | ✅ | ✅ P1 (`save_blog` ghi cấu hình site; chi nhánh đọc được) |
| X3 | Tự kiểm SC-0b…SC-12 | ☐ | ✅ (ma trận 65, chạy lại sau P1) | ✅ P1 (không đỏ; SC-9 vàng: chưa có đơn) |
| X4 | SC-3 trùng tenant | ☐ (phải **xanh** khi khác chi nhánh) | ✅ đỏ + tự tạm dừng | — |
| X5 | Bán POS cũ → gửi → định khoản | ☐ | ✅ | ☐ |
| X6 | Tạm dừng / nối lại, 0 lời gọi | ☐ | ✅ | ✅ P1 |
| X7 | Kế toán tắt giữa ca, gửi bù, 0 trùng | ☐ | ✅ | ☐ |
| X8 | Đối chiếu chứng từ + tồn (H4) | ☐ | ✅ | ✅ P1 (chưa có đơn) |
| X9 | Cron site chính: gửi lại, kéo trạng thái, tự kiểm hằng ngày | ☐ | ✅ (khi có cron hệ thống) | ☐ (`is_main_site()` luôn đúng) |
| X10 | Danh mục: `tgs-catalog status / ensure / store` | ☐ | ✅ | 🔴 fatal (status) |
| X11 | Tạo mã qua form ghi đúng bảng theo cờ | ☐ | ✅ (SW1-4a 9/9) | ☐ |
| X12 | Kéo danh mục từ kế toán (C8) | ☐ chế độ `network` → global | ☐ theo blog | ☐ |
| X13 | Ca bán chuẩn trước / sau giống hệt (I-0) | ☐ | ✅ | ☐ |
| X14 | Màn quản trị Cổng kế toán / Ánh xạ / Máy bán mở được | ☐ | ✅ | ☐ (bridge hết `get_sites` thẳng ở P1; trang nằm trong tsm — P2) |

Một kịch bản chạy cả ma trận: mở rộng `tools/lat-doc-docker/ma-tran.sh` (open-pos-backend) thêm tham số `--kieu=1|2|3`.

### 5.1 Kết quả P1 (bridge, 23/11 03:10 AM — open-ketoan-bridge PR #21)

- Lớp bao `TGS_Acc_Site`; 47 lời gọi thẳng → 0 (census MS0, đối chứng âm 47). SC-0b kiểu cài. Bảng nhật ký gửi tạo lúc kích hoạt.
- Lỗi tìm thêm khi chạy thật: mã chi nhánh của blog **không bao giờ được đọc** ở một site (điều kiện `function_exists('get_blog_option')` không có nhánh else) — đã sửa.
- Kiểu 3: X2, X3, X6, X8 ✅, 0 lỗi PHP. Kiểu 2: ma trận tuân thủ chạy lại xanh (M6 ba trạng thái dòng sổ giống hệt, 135 chứng từ = 135 docKey).

### 5.2 `docKey` của các bản cài một site — chủ chốt: không phải rủi ro (Q-OKT-6 ✅ 23/11)

Mọi bản cài một site đều là **blog 1** → `docKey` `btsoft:1:sale:N`. Chỉ đụng nhau khi hai bản cài nối **cùng một** tenant. Chủ chốt: chủ 23/11: mỗi chủ shop có phần mềm kế toán (tenant) riêng, API key nội bộ open-ketoan cấp riêng cho open-pos của shop đó → `btsoft:1:` không đụng nhau.
Đây chính là I-1 ở kiểu 3 (một bản cài = một shop = một tenant). Không đổi `docKey`, không thêm mã bản cài; OKT-TOPO-7 huỷ.

## 6. Lộ trình

| Mốc | Việc | Repo | Xong khi |
|---|---|---|---|
| **P0** (tài liệu này) | Đo, ghi, chia việc; môi trường T3 `okt-wp1` dựng lại được | open-setup, open-pos-backend (tools) | 80 merge; README docker có kiểu 3 |
| **P1** ✅ mã (PR #21) | Lớp bao `TGS_Acc_Site` ở bridge; thay 47 lời gọi; SC-0b; census MS0 (test); nhật ký gửi tạo bảng khi kích hoạt | open-ketoan-bridge | T3: X2, X3, X6, X8 ✅; T2 ma trận 65 chạy lại xanh — **đạt 23/11** |
| **P2** | Lớp bao cùng API ở tsm (sửa luôn lỗi `tgs-catalog status`); thay 59 lời gọi | open-pos-backend | T3: X10, X11 ✅ |
| **P3** | Lớp bao ở open-pos (63 lời gọi, **không** đụng tệp D002-6 — tệp nào trong danh mục cấm thì chỉ đổi theo D002-7 hoặc để nguyên nếu chỉ chạy ở multisite) | open-pos | T3: X5, X7, X13 ✅ |
| **P4** | Kiểu 1 sau khi chủ chốt Q-OKT-3: SC-3 theo kiểu, bộ kéo C8 chế độ `network` (thay `TGS_Acc_Catalog_Sync`), màn mạng | bridge, tsm | T1: cột đầy |
| **P5** | Ma trận 3 × 14 xanh; đưa vào ma trận tuân thủ 65 thành cột | open-setup | 65 có cột T1 / T2 / T3 |

Thứ tự với SW1: P1 làm **ngay** (bridge, không chạm danh mục). P2 làm trước SW1-5 (để mọi mã mới của SW1 dùng lớp bao từ đầu). P4 sau SW2 (C8).

## 7. Câu chờ chủ

- **Q-OKT-3** — Kiểu 1 (một mạng = một tenant, blog = chi nhánh) có được hỗ trợ chính thức không? Gợi ý: **có**, ghi thành ngoại lệ của I-1 trong ADR, chỉ khi cả mạng là một pháp nhân.
- **Q-OKT-4** — Phương án hỗ trợ kiểu 3: A polyfill / **B lớp bao (gợi ý)** / C bắt buộc multisite.
- **Q-OKT-5** — Kiểu 3 dùng bảng nào cho danh mục: **`wp_tgs_catalog_*` (cờ `local`, gợi ý — cùng đường với kiểu 2, chuyển lên bizcity được bằng chép bảng)** hay `wp_global_*` (cờ `global`).
