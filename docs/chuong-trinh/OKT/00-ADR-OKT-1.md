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

## 1. Bối cảnh

Ngày 21/11, hướng kiến trúc đổi ba lần:
1. standalone khi không kết nối;
2. bắt buộc open-ketoan;
3. bảng local ở giữa, admin chọn nguồn theo blog.

Mỗi lần đổi, quyết định nằm thêm ở một tệp mới (PHASE-001 doc 26, 27, 28), còn tệp cũ chỉ được gắn banner. Bản đánh giá cuối ngày chỉ ra mười chỗ chưa ổn ở góc nhìn người dựng hệ thống: quyết định chưa đứng yên, hai máy bán với hai đường ghi, định danh suy đoán, nhất quán cuối cùng mà không có quan sát, và các chỗ khác. Kết luận: **dừng viết thêm, chốt bất biến, làm một lát dọc chạy được.**

## 2. Tám bất biến

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

## 4. Hệ quả

- PHASE-001 giữ vai **hồ sơ nghiên cứu và đặc tả** (doc 16 chuẩn hàng hoá, 25 bảng theo prefix, 29 bảng điểm, 81 bộ kéo). Phần **quyết định** của nó lấy theo tệp này.
- Mỗi PR mã từ nay ghi trong mô tả: chạm bất biến nào, kiểm bằng gì.
- Đo lại bảng điểm PHASE-001 doc 29 **sau** lát dọc, bằng bằng chứng (I-7).
