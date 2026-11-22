# ADR-OKT-1: tám bất biến của hệ open-pos ⇄ open-ketoan

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chuyển ADR-OKT-1 từ open-pos-backend PHASE-002/00 sang open-setup (trục điều phối chương trình OKT). Nội dung giữ nguyên bản đã merge ở open-pos-backend 627b2f3; link tương đối đổi thành link tuyệt đối. -->

<!-- [2026-11-21 06:19 PM Johnny Chu - Chu Hoàng Anh] PHASE-002 S0 — ADR kiến trúc theo đánh giá system builder (21/11): gom quyết định rải ở PHASE-001 (00 D001, 26, 27, 28, 50) và CANON R-OKT-CONN về một chỗ; chủ chốt máy bán đích và môi trường lát dọc. -->

> **Trạng thái:** Chấp nhận 2026-11-21 (chủ dự án).
> **Phạm vi:** ba repo `open-pos` · `open-pos-backend` · `open-ketoan-bridge`, cùng phía open-ketoan.
> **Luật nền:** CANON open-ketoan R-OKT-CONN-1…12 (`docs/rules/RULE-OPEN-POS-CONNECTION.md`, merge 21/11 qua PR #516 và #520).

**Nơi giữ:** open-setup `docs/chuong-trinh/OKT/` (từ 21/11 07:52 PM). Bản ở open-pos-backend chỉ còn dòng trỏ.

**Thứ tự ưu tiên khi có mâu thuẫn:**
1. CANON R-OKT-CONN.
2. Tệp này.
3. Mọi tài liệu khác, kể cả PHASE-001.

Không gắn banner thay thế nữa: tệp nào lệch với tệp này thì **sửa thẳng** tệp đó, hoặc chuyển vào `archive/` (việc S002-0b).

<!-- [2026-11-23 04:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P-0 — chủ đặt nguyên tắc tối quan trọng: hai mô hình triển khai. Đối chiếu đầy đủ: 81. -->
## 0. Nguyên tắc P-0 — hai mô hình triển khai (chủ, 23/11, "cực kỳ ghi nhớ")

1. **bizcity** — "Với hệ thống multisite của bizcity.vn, mỗi một blog trên hệ thống multisite của bizcity sẽ yêu cầu một phần mềm kế toán tương ứng. Việc này để demo cho khách mô hình hệ thống chạy như nào." → khoá **riêng từng blog**, mỗi blog một tenant.
2. **selfhost** — "Bên ngoài hệ thống bizcity, người dùng cài selfhost, sẽ ưu tiên khóa chung cho cả mạng để người dùng có thể setup chuỗi nhiều cửa hàng dùng POS nhưng vẫn về 1 open-ketoan tương ứng mỗi tenant id = blog_id." → **khoá chung cả mạng** là đường chính.

P-0 đứng trên mọi bất biến bên dưới. Bất biến nào viết cho một mô hình (vd I-1 "một blog = một tenant") thì chỉ áp cho mô hình đó; đối chiếu từng chỗ ở [81](81-DOI-CHIEU-NGUYEN-TAC-TRIEN-KHAI.md). Hồ sơ triển khai phải **khai rõ** (`TGS_ACC_DEPLOYMENT`, Q-OKT-8), không suy từ khoá đang có. Mọi câu hỏi về sau trả lời qua năm câu tự hỏi ở 81 §6. Chỗ CANON R-OKT-CONN-2/3 trái P-0 ý 2 được sửa theo P-0 (OKT-TOPO-10).

## 1. Bối cảnh

Ngày 21/11, hướng kiến trúc đổi ba lần:
1. standalone khi không kết nối;
2. bắt buộc open-ketoan;
3. bảng local ở giữa, admin chọn nguồn theo blog.

Mỗi lần đổi, quyết định nằm thêm ở một tệp mới (PHASE-001 doc 26, 27, 28), còn tệp cũ chỉ được gắn banner. _(22/11: ba tệp đã gộp vào §3b, §5 và chuyển `archive/`.)_ Bản đánh giá cuối ngày chỉ ra mười chỗ chưa ổn ở góc nhìn người dựng hệ thống: quyết định chưa đứng yên, hai máy bán với hai đường ghi, định danh suy đoán, nhất quán cuối cùng mà không có quan sát, và các chỗ khác. Kết luận: **dừng viết thêm, chốt bất biến, làm một lát dọc chạy được.**

<!-- [2026-11-22 11:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ: scoreboard kết nối (70) + luật tối thượng tự kiểm theo cặp blog → tenant qua API (I-8, đặc tả 75). -->

## 2. Chín bất biến

<!-- [2026-11-21 06:55 PM Johnny Chu - Chu Hoàng Anh] PHASE-002 D2 — chủ: "luồng bán hàng, logic bán hàng, ledger như cũ vẫn phải giữ nguyên; mục tiêu là để open-pos linh hoạt, chủ động hơn khi open-ketoan không hoạt động, dừng kết nối". Thêm I-0, sửa I-3, D002-1; thêm D002-5, D002-6. -->

| # | Bất biến | Kiểm bằng gì |
|---|---|---|
| **I-0** | **Giữ nguyên luồng bán, logic bán hàng và sổ.** Không đổi: đường checkout của POS cũ và POS React, cách tính giá / khuyến mại / thuế khi bán, các loại phiếu và cột ghi vào `{prefix}local_ledger*`, chế độ dự phòng hiện có của POS React. Mọi việc của chương trình là **bổ sung bên ngoài** đường bán: bridge đọc sổ, dựng và gửi chứng từ; quản trị; công cụ; script. Lỗi ở phần bổ sung **không bao giờ** được chặn một đơn bán | danh mục tệp cấm sửa (D002-6); census `--check=I0` báo đỏ khi PR chạm tệp trong danh mục; ca bán hàng trước / sau mỗi mốc cho ra **cùng** dòng sổ |
| **I-1** | **Một blog = một shop = một tenant.** Khoá API, URL kế toán, khoá ký vé của máy bán, nhật ký gửi đều **theo blog**. Không có hằng hay option cả mạng nào trả lời câu "blog này nối tenant nào" | test cấu hình của bridge (`tests/config-test.php`, PR #2); ca G8 "trùng tenant" |
| **I-2** | **Mỗi loại dữ liệu của một blog có đúng một nơi được ghi tại mỗi thời điểm.** Nguồn danh mục do admin chọn theo blog: `tgs_catalog_source` = `local` \| `ketoan`. `local` → `ketoan` là đường chuẩn. `ketoan` → `local` là **thủ tục khôi phục**: có người duyệt, có nhật ký, không phải nút dùng hằng ngày | cổng ghi duy nhất; census đếm hàm ghi chưa qua cổng = 0 |
| **I-3** | **Kế toán tắt hay dừng kết nối thì quầy vẫn bán, không mất đơn.** Giữ đúng đường ghi hiện có của từng máy bán (I-0):<br>• **POS cũ** ghi sổ local; bridge gửi **sau** khi đơn đã ghi, không bao giờ trong lúc bán.<br>• **POS React** ghi ở kế toán (D1). Kế toán không trả lời thì **chế độ dự phòng có sẵn** ghi đơn vào máy + WP (`pos/react/src/features/fallback/store.ts`, `pos/includes/class-tgs-pos-fallback.php`), phát lại khi kế toán sống.<br>Ca mà hai đường trên không đỡ được (kế toán tắt **trước** khi mở ca, máy mới chưa có bản lưu danh mục, dừng kết nối dài ngày) thì shop **chuyển sang POS cũ** bằng cờ có sẵn `tgs_pos_engine` (D002-5) | ca L10–L13 ở 20; grep không có lời gọi HTTP mới trong đường checkout |
| **I-4** | **Định danh lưu, không suy.** Mọi ánh xạ sang kế toán lưu **mã đích ổn định** trong bảng ánh xạ của blog (`item_id`, mã phương thức thanh toán, mã lý do, mã chi nhánh, mã kho, mã bảng giá, mã thuế), không suy theo tên, nhãn hay SĐT. Khoá chứng từ (`docKey`) bất biến: nội dung đổi thì lên `version` | test: đổi mã ở kế toán thì id dòng ở WP không đổi; gửi lại cùng đơn → `unchanged` |
| **I-5** | **Một hàm tiền.** Một hàm duy nhất tách VAT và làm tròn cho mọi chứng từ: giá bảng giá **gồm VAT**, dòng chứng từ gửi **trước VAT** + tiền thuế, tổng khớp tuyệt đối; số lượng gửi theo **ĐVT gốc** | test với các ví dụ chuẩn `docs/api/vi-du/ban-hang.json`, `ban-noi-bo.json`, `tra-hang-ban.json` của open-ketoan; preflight 0 lỗi |
| **I-6** | **Quan sát trước khi bật.** Không bật gửi hay kéo cho blog nào khi chưa có: nhật ký từng lượt, đếm hàng chờ, đếm đơn `pending` quá 24 giờ, kết quả đối chứng, cảnh báo khi vượt ngưỡng | màn Đồng bộ hiện đủ năm số; cảnh báo thử bắn được |
| **I-7** | **Xong = có bằng chứng chạy.** Tiến độ chỉ tính việc có tín hiệu đo: test có tên, ca chạy được, hoặc bản ghi trong `evidence/` có ngày giờ và người chạy. Không tính % bằng thang tự chấm khi đã có lát dọc | checklist chỉ cho ✅ khi cột bằng chứng có đường dẫn |
| **I-8** | **Tự kiểm luôn xanh** (luật tối thượng, cùng hạng I-0). Một cặp **blog → tenant** chỉ được coi là đang kết nối khi tự kiểm của **chính cặp đó** xanh: chạy qua **đúng API** đường nối dùng, bằng **đúng khoá của blog**, đọc **đúng sổ của blog**; không suy từ cấu hình, không lấy kết quả của blog khác, không cũ quá 24 giờ. Chạy trước khi bật, mỗi ngày, sau khi đổi khoá, sau mỗi deploy; phần ngoại tuyến (test + `--check=I0`) trong mọi PR. Sai / trùng tenant thì tự tạm dừng gửi, quầy vẫn bán | `wp tgs-acc selfcheck` SC-1…SC-11 ([75](75-LUAT-TU-KIEM.md)); scoreboard [70](70-SCOREBOARD-KET-NOI.md) chỉ cho mức 5 khi tự kiểm xanh liên tục |

## 3. Quyết định đi kèm

| # | Quyết định | Lý do |
|---|---|---|
| **D002-1** | **Máy bán đích: POS React, giữ nguyên đường ghi của nó (D1 + dự phòng).** Lát dọc chạy **POS cũ** để chứng minh đường gửi qua bridge. **Không** mở phase đổi React sang ghi local trước: kế hoạch đó (PHASE-001 D001-20 phần React, Q001-26) bị huỷ theo I-0. POS cũ được giữ làm **đường chạy khi mất kết nối** (D002-5), không đóng băng hẳn | chủ 21/11 (chỉnh 06:55 PM) |
| **D002-2** | **Môi trường lát dọc:** máy dev, LocalWP (multisite) + open-ketoan Docker trên cùng máy. Không chạm máy chủ thật | chủ 21/11 |
| **D002-3** | **Lát dọc dùng bảng hiện có** (global `wp_global_product_*`, `wp_global_htsoft_*`, `{prefix}local_ledger*`). Tách bảng theo prefix là việc của PHASE-001 M1, sau lát dọc. Lát dọc chứng minh **đường ống**, không chứng minh lược đồ | tránh chờ việc lớn mới có bằng chứng đầu tiên |
| **D002-5** | **Mục tiêu của phase: open-pos chủ động khi open-ketoan không hoạt động hoặc dừng kết nối.** Đạt bằng phần bổ sung, không đổi đường bán:<br>(a) bridge xếp hàng và gửi bù đúng tenant;<br>(b) **tạm dừng kết nối theo blog** (hôm nay công tắc `TGS_ACC_REALTIME` / `realtime` là cả mạng);<br>(c) admin shop chuyển nhanh máy bán React ↔ POS cũ bằng cờ `tgs_pos_engine` (hôm nay chỉ quản trị mạng đổi được);<br>(d) blog `local` sửa được danh mục khi đã dừng kết nối (PHASE-001 doc 28) | chủ 21/11 06:55 PM |
| **D002-6** | **Danh mục tệp cấm sửa** (đường bán và sổ của open-pos). Chỉ sửa khi có lỗi bán hàng thật, có PR riêng ghi rõ lý do:<br>• `pos/functions/class-tgs-pos-order-handler.php`;<br>• `pos/functions/ajax/class-tgs-pos-ajax-order.php`;<br>• `pos/assets/js/pos-order.js`;<br>• `pos/functions/class-tgs-pos-price-list.php`;<br>• `pos/includes/class-tgs-pos-fallback.php`;<br>• `pos/includes/class-tgs-pos-ledger-mirror.php`;<br>• `pos/react/src/features/checkout/*`;<br>• `pos/react/src/features/fallback/*`;<br>• `pos/react/src/api/orders.ts`;<br>• `pos/includes/class-tgs-pos-order-mapper.php`, `pos/includes/class-tgs-pos-ketoan-events.php` (ghi sổ cho đơn React qua bản sao);<br>• `pos/functions/class-tgs-pos-global-products.php` (danh sách hàng của màn bán).<br>Thêm tệp vào danh mục khi tìm thấy đường ghi sổ khác | I-0; rà soát 30 |
| **D002-7** | **Ngoại lệ có kiểm soát cho tách bảng theo prefix.** Trong các tệp ở D002-6 chỉ được đổi **tên bảng** đọc / ghi qua `tgs_catalog_table()`. Không đổi câu truy vấn, điều kiện lọc, cách tính, thứ tự. Mỗi PR loại này: (a) chỉ chứa đổi tên bảng; (b) chạy ca bán chuẩn trước và sau, dòng sổ giống hệt (trừ id, giờ); (c) có cờ lùi `tgs_catalog_store = global`. Census `--check=I0` cho phép đúng mẫu đổi tên này, mọi thay đổi khác vẫn đỏ | chủ 21/11 07:30 PM |
| **D002-8** | **Luật giá DM14 áp ở bộ kéo, ghi thành dữ liệu.** Bộ kéo C8 tính giá đã áp luật (hàng chính lấy giá công ty; thiếu giá chi nhánh thì lùi về giá công ty), rồi ghi sẵn vào bảng giá của blog. POS đọc giá như cũ, **không** sửa `TGS_POS_Price_List`. Thay Q001-7 / D001-13 | chủ 21/11 07:30 PM |
| **D002-4** | **Một nguồn quyết định.** Bất biến ở tệp này. **Trạng thái mọi việc của chương trình chỉ ở [open-setup 40-CHECKLIST](40-CHECKLIST.md)** (chủ chốt 21/11 07:52 PM); checklist ở từng repo giữ mô tả kỹ thuật, không giữ trạng thái. Câu hỏi chờ chủ ở [90](90-CAU-HOI-CHO-CHU.md). PHASE-001 doc 26, 27, 28 gộp vào đây, tệp cũ chuyển `archive/` | đánh giá 21/11, mục 1 |

## 3b. Quyết định gộp từ PHASE-001 doc 26, 27, 28 (S002-0b)

<!-- [2026-11-22 09:00 AM Johnny Chu - Chu Hoàng Anh] S002-0b — gộp phần còn hiệu lực của open-pos-backend PHASE-001 doc 26, 27, 28 vào ADR; ba tệp cũ chuyển archive/. -->

Ba tệp cũ nằm ở `open-pos-backend/docs/phases/PHASE-001-…/archive/`, chỉ để truy vết. Mọi chỗ còn hiệu lực ở dưới đây.

| # | Quyết định | Nguồn |
|---|---|---|
| ~~D001-15~~ | ~~open-ketoan bắt buộc, bỏ standalone~~. **Đã thay** bởi D001-18…20 | 26 → 28 |
| **D001-16** | Repo GitHub: `tgs_pos` → **`open-pos`**, `tgs_shop_management` → **`open-pos-backend`**. Thư mục plugin giữ tên cũ (`tgs_pos`, `tgs_shop_management`, `open-ketoan-bridge`) | 26, chủ 21/11 |
| **D001-17** | `bizcity-open-kiot` **dừng** (đã archive). Phần đáng giữ (khảo sát tgs_pos, ý sổ bán lẻ ADR-0010) chỉ để tham khảo | 26, chủ 21/11 |
| **D001-18** | **Bảng local ở giữa, luôn có.** Mỗi blog có bảng danh mục và sổ bán của riêng nó. Mọi màn bán và quản trị **chỉ đọc / ghi bảng local**; không màn bán nào đọc thẳng kế toán | 28, chủ 21/11 05:18 PM |
| **D001-19** | **Admin chọn nguồn danh mục theo blog**: `tgs_catalog_source = local \| ketoan` (= I-2). Blog mới mặc định `local` (Q001-24, mặc định tạm). `tgs_catalog_source` (ai là gốc) **khác** `tgs_catalog_store` (đọc bảng global hay theo prefix, chỉ để lùi lúc chuyển bảng) | 28 |
| **D001-20** | **Kế toán tắt thì quầy vẫn bán, không mất đơn; giữ nguyên đường ghi của từng máy bán** (= I-0, I-3). POS cũ ghi `local_ledger`, bridge gửi sau. POS React giữ D1 + chế độ dự phòng có sẵn. Ca dự phòng không đỡ được thì chuyển shop sang POS cũ | 28, sửa theo I-0 21/11 06:55 PM |

## 4. Hệ quả

- PHASE-001 giữ vai **hồ sơ nghiên cứu và đặc tả** (doc 16 chuẩn hàng hoá, 25 bảng theo prefix, 29 bảng điểm, 81 bộ kéo). Phần **quyết định** của nó lấy theo tệp này.
- Mỗi PR mã từ nay ghi trong mô tả: chạm bất biến nào, kiểm bằng gì.
- Đo lại bảng điểm PHASE-001 doc 29 **sau** lát dọc, bằng bằng chứng (I-7).

## 5. Trạng thái một blog và chuyển nguồn

### 5.1 Bảng trạng thái

| `tgs_catalog_source` | Kết nối | Trạng thái | Máy bán | Quản trị danh mục |
|---|---|---|---|---|
| `local` | không cần | 🔵 **Tự quản** | Bán bình thường | CRUD đầy đủ: sản phẩm, nhóm, giá, ĐVT, thuế |
| `local` | có khoá riêng, kiểm được | 🔵 **Tự quản, có gửi chứng từ** | Như trên; chứng từ gửi lên tenant sau khi ghi sổ | Như trên; có nút "Chuyển sang theo open-ketoan" (§5.2) |
| `ketoan` | kiểm thành công | 🟢 **Theo kế toán** | Bán từ bản sao local | Trường gốc chỉ đọc + link sửa ở kế toán; thêm mã = gửi lên, **về rồi mới bán** (Q001-16) |
| `ketoan` | lỗi mạng (hết giờ, 5xx), đã từng thành công | 🟡 **Dự phòng** | **Vẫn bán** (I-3); hàng chờ gửi dài ra, giữ 7 ngày | Không sửa danh mục, không thêm mã (Q001-21) |
| `ketoan` | khoá bị từ chối, trùng tenant, bridge tắt, chưa từng thành công | 🔴 **Hỏng kết nối** | **Vẫn bán** từ bản sao, đơn xếp hàng (Q001-22 = 1); báo đỏ, quá 24 giờ báo cấp trên | Sửa khoá, hoặc chuyển về `local` theo thủ tục §5.2 |
| bất kỳ | admin **tạm dừng** (`tgs_acc_paused`, R-OKT-CONN-12) | ⏸ **Tạm dừng kết nối** | Vẫn bán; sự kiện vẫn ghi, không gửi, không thử lại; bỏ tạm dừng thì gửi bù, không trùng | Như dòng tương ứng ở trên |

Máy bán: **POS cũ** bán ở mọi trạng thái vì đơn ghi sổ local. **POS React** đăng nhập qua kế toán; ở 🟡 / 🔴 / ⏸ nó dựa vào chế độ dự phòng có sẵn, không đỡ được (kế toán tắt **trước** khi mở ca, máy mới) thì admin shop chuyển máy bán sang POS cũ ở **POS → Máy bán** (S002-14). Hoàn hàng / chuyển kho ở 🟡: Q001-25, mặc định **giữ nguyên** như đang chạy (I-0): POS cũ hoàn hàng bình thường (ghi sổ local); chế độ dự phòng của POS React không hoàn hàng, không thao tác kho.

### 5.2 Chuyển nguồn

**`local` → `ketoan`** (admin bấm, kết nối phải 🟢):
1. Dựng ánh xạ mặc định (R-OKT-CONN-5).
2. Khớp mã local theo SKU rồi barcode (Q001-12): khớp thì gắn `item_id`; không khớp thì gửi lên như mã mới, chỉ mã blog đã dùng (Q001-23).
3. Kéo đầy đủ về bảng local, đối chứng lệch 0.
4. Đặt `tgs_catalog_source = ketoan`. Từ đây kế toán thắng.

**`ketoan` → `local`** là **thủ tục khôi phục** (I-2): có người duyệt, có nhật ký; không phải nút hằng ngày. Dữ liệu đã kéo ở lại và thành của blog. Chứng từ đang chờ vẫn gửi nếu còn kết nối.

Mỗi lần chuyển ghi nhật ký kết nối: ai, lúc nào, kết quả đối chứng.

### 5.3 Chuyển 92 blog đang chạy (một lần)

1. Kế toán tách tenant theo blog (S001-K9), cấp tenant (S001-K10).
2. Mỗi blog: dựng dữ liệu nạp từ bảng global (`TGS_Acc_Catalog_Sync::build_import`, lệnh `tools/danh-muc-hang.php nap`), lọc theo mã blog đã dùng (Q001-23), `dryRun`, rồi nạp vào tenant của blog.
3. Kéo về bảng của blog, khớp id cũ theo SKU để sổ kho giữ khoá (D001-9), đối chứng lệch 0.
4. Đặt `tgs_catalog_source = ketoan` cho blog đó.

`nap` / `build_import` của bridge **không gỡ** (B001-C7) cho tới khi bước này xong.

### 5.4 Điểm rủi ro đã biết ở vỏ POS React (doc 27 §2)

| # | Điểm | Ở đâu | Xử lý theo ADR |
|---|---|---|---|
| E1 | Vỏ React không kiểm kết nối trước khi mở màn bán | `react-shell.php:84-106` | **Giữ** (Q001-22 = vẫn bán; I-0) |
| E2 | Thiếu `TGS_POS_API_BASE` → `/api/v1` của API giả; bản build mặc định `mock` | `react-shell.php:15, 235`; `react/src/app/env.ts:1` | Kiểm khi deploy: bản build thật, có `TGS_POS_API_BASE` (95 deploy list) |
| E3 | Địa chỉ API, khoá ký vé SSO, tenant chung cả mạng | `react-shell.php:367-404` | B001-C12 / P001-CFG: lấy theo blog; một tenant thì hành vi giống hệt, có ca đăng nhập trước / sau |
| E4 | Mã chi nhánh lùi về `wp_blogs.tgs_site_code` | `react-shell.php:340-359` | Q001-20; chi nhánh khai theo blog `tgs_acc_branch_code` (S002-5) |
| E5 | POS cũ không có cổng kết nối | — | **Giữ**: đúng D001-20 / I-3 |
