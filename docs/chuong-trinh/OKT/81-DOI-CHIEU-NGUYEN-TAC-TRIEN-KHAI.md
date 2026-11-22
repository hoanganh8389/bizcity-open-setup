<!-- [2026-11-23 04:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P-0 — chủ đặt nguyên tắc tối quan trọng (bizcity: mỗi blog một phần mềm kế toán; selfhost: khoá chung cả mạng) và yêu cầu đối chiếu lại mọi tài liệu, câu hỏi mở theo nguyên tắc này. -->
# OKT · 81 — Đối chiếu mọi tài liệu và câu hỏi theo nguyên tắc P-0 (hai mô hình triển khai)

> **Nguyên tắc P-0** (chủ, 23/11 — "cực kỳ ghi nhớ"; ghi ở [00 ADR §0](00-ADR-OKT-1.md)):
> 1. "Với hệ thống multisite của bizcity.vn, mỗi một blog trên hệ thống multisite của bizcity sẽ yêu cầu một phần mềm kế toán tương ứng. Việc này để demo cho khách mô hình hệ thống chạy như nào."
> 2. "Bên ngoài hệ thống bizcity, người dùng cài selfhost, sẽ ưu tiên khóa chung cho cả mạng để người dùng có thể setup chuỗi nhiều cửa hàng dùng POS nhưng vẫn về 1 open-ketoan tương ứng mỗi tenant id = blog_id."
>
> Cùng ngày (Q-OKT-6): mỗi chủ shop có phần mềm kế toán riêng, API key nội bộ open-ketoan cấp cho open-pos của shop đó.

**Cách dùng tài liệu này:** mọi câu hỏi mới, mọi PR chạm khoá / tenant / danh mục / tự kiểm phải trả lời được "ở **bizcity** thì sao, ở **selfhost** thì sao" trước khi chốt.

## 1. Hai hồ sơ triển khai

| | **bizcity** (multisite bizcity.vn — nơi demo) | **selfhost** (khách tự cài) |
|---|---|---|
| Mục đích | cho khách **thấy** mô hình chạy: mỗi cửa hàng một phần mềm kế toán | khách **dùng**: một chủ, chuỗi nhiều cửa hàng, **một** open-ketoan |
| Khoá API | **riêng từng blog** (bắt buộc) | **một khoá chung cả mạng** (ưu tiên) |
| Một tenant ứng với | một blog | xem §2 — đề xuất: **cả mạng** (một chủ); blog = chi nhánh |
| WordPress | multisite | multisite (chuỗi) **hoặc** một site (một cửa hàng — kiểu 3) |
| Kiểu cài ở [80](80-BA-KIEU-CAI-DAT.md) | kiểu 2 | kiểu 1 (multisite) · kiểu 3 (một site) |

**Hồ sơ phải KHAI RÕ, không đoán.** Hôm nay bizcity cũng đang dùng khoá chung (giai đoạn chuyển, ADR §5.3) — đoán theo "có khoá chung" sẽ nhận bizcity thành selfhost. Đề xuất: hằng `TGS_ACC_DEPLOYMENT = 'bizcity' | 'selfhost'` trong `wp-config.php` (một lần cho máy chủ); thiếu → tự kiểm SC-0b vàng "chưa khai hồ sơ".

## 2. Tự hỏi lại: "về 1 open-ketoan tương ứng mỗi tenant id = blog_id" nghĩa là gì?

| | (a) một open-ketoan, **mỗi blog một tenant**, chung một khoá | (b′) một open-ketoan, **một tenant cho cả chuỗi**, mỗi blog một **chi nhánh** (`external_ref = blog:N`), tuỳ chọn mỗi blog một **đơn vị hạch toán** |
|---|---|---|
| Đọc theo chữ | sát chữ "tenant id = blog_id" | "= blog_id" thực hiện ở chi nhánh: `branches.external_ref = 'blog:N'` |
| open-ketoan hôm nay (đo 23/11) | **không làm được**: `api_keys.tenant_id` — một khoá thuộc đúng một tenant; mọi yêu cầu bị khoá vào tenant đó ở tầng CSDL (RLS, `packages/platform/src/core/auth.ts:266-285`, `:352`). Không có khái niệm nhóm tenant | **làm được ngay**: một tenant có nhiều `accounting_unit` (cây tổ chức) và nhiều chi nhánh; bridge đang chạy đúng đường này với khoá chung (bizcity hôm nay: tenant `tgs`, chi nhánh `blog:N`) |
| Một khoá chung ghi vào nhiều tenant | phải làm mới ở open-ketoan: khoá mạng + chỉ định tenant theo blog — **phá luật "tenant đi theo khoá" (R-TEN) và RLS** | không cần |
| Sổ của chủ chuỗi | N sổ rời; muốn báo cáo hợp nhất phải có tính năng hợp nhất liên tenant (chưa có) | một sổ, xem theo chi nhánh / đơn vị hạch toán; hợp nhất sẵn |
| Danh mục hàng | N danh mục ở kế toán (mỗi tenant một), chủ phải khai N lần | **một** danh mục, giá theo chi nhánh (bảng giá gán chi nhánh — đã có) |
| Khác gì bizcity | giống hệt bizcity, chỉ khác khoá | khác: bizcity mỗi blog một tenant |

**Đề xuất: (b′).** Lý do theo đúng mục đích chủ nói — "setup **chuỗi** nhiều cửa hàng … nhưng vẫn về **1** open-ketoan": một chủ chuỗi cần một sổ, một danh mục, xem theo cửa hàng. (a) đòi open-ketoan phá luật nền (khoá ↔ tenant, RLS) để rồi cho chủ chuỗi N sổ rời. "tenant id = blog_id" được giữ bằng ánh xạ **một-một blog ↔ chi nhánh** (`external_ref`), và nếu từng cửa hàng là pháp nhân riêng thì blog ↔ **đơn vị hạch toán**. **Cần chủ xác nhận — Q-OKT-7.**

## 3. Đối chiếu từng tài liệu

| Tài liệu / chỗ | Hiện viết | Theo P-0 | Việc |
|---|---|---|---|
| ADR **I-1** "Một blog = một shop = một tenant … không có option cả mạng nào trả lời blog nối tenant nào" | đúng một mô hình | đúng cho **bizcity**; sai cho **selfhost chuỗi** | thêm §0 P-0; I-1 viết lại theo hồ sơ (OKT-TOPO-11) |
| CANON open-ketoan **R-OKT-CONN-2/3** "Khoá theo blog, không dùng một khoá cho cả mạng" | luật nền, đứng trên ADR | trái P-0 ý 2 | sửa CANON (lane OK) — OKT-TOPO-10 |
| ADR §5.3 chuyển 92 blog bizcity sang tenant riêng | | đúng P-0 ý 1 | giữ |
| Q001-1 (bizcity: tenant theo blog) | ✅ | đúng P-0 ý 1 | giữ |
| [75](75-LUAT-TU-KIEM.md) **SC-1** "khoá chung = vàng (giai đoạn chuyển)" | một luật | bizcity: khoá chung vàng (đang chuyển) rồi đỏ; **selfhost: khoá chung xanh** | sửa đặc tả 75 theo hồ sơ |
| [75](75-LUAT-TU-KIEM.md) **SC-3** "hai blog cùng tenant = đỏ" → **tự tạm dừng** | một luật | bizcity: giữ; **selfhost: cùng tenant là ĐÚNG**; đỏ khi hai blog **trùng chi nhánh** | **lỗi đang chạy** — §4 |
| [70](70-SCOREBOARD-KET-NOI.md) tiêu chí **A1** "không khoá chung cả mạng (I-1)" | | chỉ đúng bizcity | sửa chữ tiêu chí theo hồ sơ (điểm giữ) |
| [80](80-BA-KIEU-CAI-DAT.md) kiểu 1 "chuỗi — trái I-1, cần ngoại lệ" | đề xuất ngoại lệ | P-0 ý 2 **chính là** kiểu 1: không còn là ngoại lệ mà là hồ sơ selfhost | Q-OKT-3 trả lời bằng P-0 |
| `TGS_Acc_Site::topology()` đoán theo khoá | suy luận | hồ sơ phải khai | OKT-TOPO-9 |
| Bridge `key_for()` "trên multisite KHÔNG BAO GIỜ trả khoá chung", chữ "khoá chung cũ / giai đoạn chuyển" | coi khoá chung là đồ cũ | selfhost: khoá chung là **đường chính** | đổi chữ + SC-1 theo hồ sơ (cùng OKT-TOPO-8) |
| **B001-C7** gỡ `TGS_Acc_Catalog_Sync` (kéo danh mục vào bảng global) | gỡ | selfhost (b′): một tenant ↔ **một** danh mục ↔ bảng **global** của mạng — đúng là việc bộ kéo này làm | **không gỡ**: thành chế độ `network` của bộ kéo C8 |
| S001-C8 bộ kéo theo blog vào `{prefix}tgs_catalog_*` | | đúng cho **bizcity** | giữ; selfhost dùng chế độ `network` |
| SW1 (bảng danh mục theo blog, cờ `tgs_catalog_store`) | | cần cho **bizcity** (mỗi blog một tenant, một danh mục) | giữ; selfhost để cờ `global` |
| D001-19 nguồn danh mục `tgs_catalog_source` **theo blog** | | bizcity: theo blog; selfhost chuỗi: một nguồn cho cả mạng | ghi rõ theo hồ sơ khi làm SW3 |
| `docKey` `btsoft:{blog}:…` | | bizcity: duy nhất trong tenant của blog; selfhost (b′): duy nhất trong tenant chuỗi vì blog_id khác nhau; selfhost một site: Q-OKT-6 ✅ | giữ |
| OKT-H2 kho theo kết nối của blog; SC-7 kho mặc định của chi nhánh | | (b′): một tenant, mỗi chi nhánh một kho mặc định — đúng sẵn | giữ |
| OKT-H4 đối chiếu lọc `branchCode` của blog | | (b′): đúng (một tenant, lọc theo chi nhánh) | giữ |
| ADR I-8 tự kiểm theo cặp blog → tenant | | bizcity: như cũ; selfhost: cặp **blog → (tenant, chi nhánh)** | đặc tả 75 theo hồ sơ |

## 4. Lỗi đang chạy, trái P-0: SC-3 tự tạm dừng cả chuỗi selfhost

`class-tgs-acc-selfcheck.php` SC-3 tính **mọi blog có khoá, kể cả khoá chung** (`key_mode !== 'none'`) và báo đỏ khi hai blog cùng tenant; `enforce()` **tự tạm dừng gửi** khi SC-3 đỏ; cron tự kiểm hằng ngày chạy cho mọi blog có khoá. Với chuỗi selfhost dùng khoá chung (P-0 ý 2), **mọi cửa hàng cùng một tenant** → lượt tự kiểm đầu tiên **tạm dừng gửi của toàn chuỗi**. Quầy vẫn bán (I-3), nhưng không chứng từ nào lên kế toán cho tới khi admin tự bỏ tạm dừng — rồi hôm sau lại bị dừng.

Sửa (OKT-TOPO-8, ưu tiên cao nhất): hồ sơ `selfhost` + khoá chung → SC-3 kiểm **chi nhánh không trùng** giữa các blog cùng tenant (trùng chi nhánh = đỏ + tự tạm dừng như cũ; cùng tenant khác chi nhánh = xanh). Hồ sơ `bizcity` giữ luật cũ. Chưa khai hồ sơ → SC-3 **không tự tạm dừng** blog dùng khoá chung (chỉ vàng), để không dừng nhầm chuỗi.

## 5. Câu hỏi mở — đề xuất lại theo P-0

| Câu | Đề xuất trước | **Đề xuất theo P-0** |
|---|---|---|
| Q-OKT-3 hỗ trợ kiểu 1 "chuỗi"? | có, như ngoại lệ I-1 | **Đã trả lời bằng P-0 ý 2: có — là hồ sơ selfhost chính thức**, không phải ngoại lệ. Chi tiết mô hình theo Q-OKT-7 |
| Q-OKT-4 cách hỗ trợ một site | B | **B** (càng cần: selfhost một cửa hàng thường là một site). Đã làm ở bridge (#21) |
| Q-OKT-5 kiểu 3 dùng bảng danh mục nào | `local` (đích), tạm `global` | **`global`** — kiểu 3 là **selfhost**; danh mục theo hồ sơ: **bizcity → `local` (`{prefix}tgs_catalog_*`), selfhost → `global`** (một tenant một danh mục; một site lớn lên thành chuỗi multisite thì bảng global sẵn là danh mục chung). Không phải chờ SW1-6/7/8 |
| **Q-OKT-7** (mới) nghĩa "tenant id = blog_id" | — | **(b′)** một tenant cả chuỗi, blog = chi nhánh (`external_ref`), tuỳ chọn blog = đơn vị hạch toán (§2) |
| **Q-OKT-8** (mới) khai hồ sơ ở đâu | — | hằng `TGS_ACC_DEPLOYMENT` trong `wp-config.php`; bizcity đặt `bizcity`; thiếu → SC-0b vàng, SC-3 không tự dừng blog khoá chung |

## 6. Câu hỏi về sau — câu tự hỏi bắt buộc

1. Ở **bizcity** (mỗi blog một tenant, khoá riêng) thì đúng không?
2. Ở **selfhost chuỗi** (một khoá, một tenant, blog = chi nhánh) thì đúng không?
3. Ở **selfhost một site** (một cửa hàng, blog 1) thì đúng không?
4. Có đoán hồ sơ từ dữ liệu (khoá nào đang có) không? → không được; đọc `TGS_ACC_DEPLOYMENT`.
5. Có làm demo bizcity khác với cái khách selfhost nhận không, theo cách khiến khách hiểu sai? → ghi rõ trong tài liệu bán hàng: bizcity demo **một cửa hàng = một phần mềm kế toán**; chuỗi selfhost là **một phần mềm kế toán cho cả chuỗi**.
