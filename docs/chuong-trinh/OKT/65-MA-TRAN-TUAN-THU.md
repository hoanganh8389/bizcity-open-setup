<!-- [2026-11-22 09:20 PM Johnny Chu - Chu Hoàng Anh] OKT-MA-TRAN — ma trận tuân thủ: chín bất biến (00) × sáu mục tiêu (60), chấm bằng lượt chạy thật. -->
# OKT · 65 — Ma trận tuân thủ

Chấm **chín bất biến** ([00](00-ADR-OKT-1.md) §2) và **sáu mục tiêu** ([60](60-DANH-GIA.md) §1) bằng lượt chạy thật, không tự chấm (I-7).
Chạy lại: open-pos-backend `tools/lat-doc-docker/ma-tran.sh` (README §5). Bản chạy thô: open-pos-backend
`docs/phases/PHASE-002-LAT-DOC-MOT-DON-BAN/evidence/okt-ma-tran-2026-11-22.md`.

**Phạm vi lượt 22/11/2026**: môi trường thử `okt-wp` (multisite, shop-a nối tenant `shopa`, shop-b chưa nối) + `okt-thu`; POS **cũ**;
một SKU, thuế 10 %, tiền mặt. **Chưa** đo: POS React, site thật, nhiều SKU / thuế / phương thức. Vì vậy không ô nào lên "đạt ở site thật".

Mức: ✅ đạt (có bằng chứng chạy) · 🟡 đạt một phần / chỉ ở môi trường thử · ⛔ chưa có · — không đo được lượt này.

## 1. Bất biến

| # | Bất biến | Mức | Bằng chứng lượt này | Còn thiếu |
|---|---|---|---|---|
| **I-0** | Giữ nguyên luồng bán, logic bán, sổ | ✅ | census `--check=I0` cả chương trình (open-pos `e2e2778` → `9eace43`): 11 tệp, **0 tệp D002-6**, chỉ thêm 2 dòng nạp ở `bizgpt-pos.php` 🟢; ca bán chuẩn **M1 (kế toán sống) ↔ M2 (tạm dừng) ↔ M4 (kế toán tắt): dòng sổ giống hệt** | so ca bán trước / sau ở site thật khi deploy |
| **I-1** | Một blog = một shop = một tenant | 🟡 | M8: dán khoá shop-a sang shop-b → **cả hai** SC-3 🔴, tự tạm dừng, quầy vẫn bán; cấu hình, nhật ký, cầu dao, đệm kho theo blog (#16 #17 #18) | site thật đang dùng **khoá chung** (SC-1 🟡) — chuyển 92 blog (ADR §5.3) |
| **I-2** | Một nơi ghi cho mỗi loại dữ liệu | ⛔ | — | `tgs_catalog_source` chưa có trong mã; sync phân kho đang ẩn phân kho tự khai bất kể nguồn (ghi chú ở OKT-H2) |
| **I-3** | Kế toán tắt / dừng: quầy vẫn bán, không mất đơn | 🟡 | POS cũ: M2 tạm dừng 2 đơn (510 / 267 ms), M4 container kế toán **tắt** 2 đơn (1388 / 287 ms) — đều lưu; nối lại / bật lại: gửi đủ, **0 trùng** (108 chứng từ = 108 docKey); bão FPM 8 đơn: trang chủ 60 s → 0,18 s (#17) | POS React (dự phòng có sẵn) chưa đo; chuyển máy bán (G-3) chưa đo trực tiếp |
| **I-4** | Định danh lưu, không suy; docKey bất biến | 🟡 | M7 gửi lại cả ngày **105 unchanged**, 0 lỗi, không tăng version; bảng ánh xạ mã phương thức / lý do / thuế (MD3); kho theo kho mặc định của chi nhánh (H2) | ánh xạ `item_id` (bộ kéo C8); 6 chứng từ version > 1 từ trước #16 (lỗi băm rỗng, đã sửa) |
| **I-5** | Một hàm tiền | 🟡 | SC-9 preflight **5 đơn mới nhất: 0 lỗi chặn**; 84 + 20 chứng từ định khoản 0 lỗi | mới một SKU / 10 % / tiền mặt; chưa chạy bộ ví dụ chuẩn của open-ketoan; cảnh báo `IN-CFG-001` (tenant chưa khai hồ sơ kế toán) |
| **I-6** | Quan sát trước khi bật | 🟡 | `wp tgs-acc status`: hàng chờ · chờ định khoản · chờ > 24 h · lỗi · lần gửi cuối; SC-10 vàng / đỏ theo ngưỡng; Cổng kế toán có Kết nối / Tự kiểm / Trace | ~~kết quả đối chứng~~ → có: `wp tgs-acc reconcile` + SC-12 (bridge #20, 22/11 10:15 PM); cảnh báo chưa đẩy ra ngoài (chỉ hiện ở trang) |
| **I-7** | Xong = có bằng chứng chạy | ✅ | mọi ô trên có bản chạy thô có giờ; checklist chỉ ✅ khi có đường dẫn | — |
| **I-8** | Tự kiểm luôn xanh | 🟡 | SC-1…SC-11 chạy thật bằng khoá của blog; tự tạm dừng khi trùng tenant (M8); lịch hằng ngày 02:30 trên site chính; **lượt này tìm và sửa** SC-9 lấy mẫu cũ nhất | **máy chủ thật phải có cron hệ thống gọi site chính** (không có → không gửi lại, không kéo trạng thái, không tự kiểm hằng ngày — im lặng); chưa chạy ở site thật |

## 2. Mục tiêu

| # | Mục tiêu | Mức | Bằng chứng |
|---|---|---|---|
| G-1 | Luồng bán / logic / sổ giữ nguyên | ✅ (thử) | I-0 ở trên: census 🟢 + ba trạng thái kết nối cho cùng dòng sổ |
| G-2 | Kế toán tắt **giữa ca**: vẫn bán, không mất đơn | 🟡 | POS cũ ✅ (M4 → M5: lên đúng tenant, 0 trùng; nhóm xếp hàng khi cầu dao mở chờ hết cửa sổ 120 s rồi gửi); POS React — |
| G-3 | Kế toán tắt **trước khi mở ca** → chuyển POS cũ | 🟡 | màn POS → Máy bán + test 14/14; chưa chạy ca chuyển trên WP thử |
| G-4 | Dừng kết nối chủ động rồi nối lại | ✅ (thử) | M2: tạm dừng → **0 lời gọi API** tới kế toán, hàng chờ +2 đúng 2 đơn; M3: nối lại gửi 2/2, 0 trùng |
| G-5 | Một blog = một tenant | ✅ (thử) | M8: trùng tenant → hai blog đỏ + tự tạm dừng; trả lại → SC-3 xanh, admin bỏ tạm dừng (không tự bỏ) |
| G-6 | Nguồn danh mục theo blog | ⛔ | I-2 |

**Tồn theo SKU (H4 bằng tay)**: WP nhập 60 − bán 52 = **8**; kế toán **7**; lệch 1 = chứng từ thử `sale:900001` gửi thẳng ở S002-1, không có phiếu
gốc trên WP (đã xin huỷ, chờ kế toán duyệt). → H4 phải tự bắt **chứng từ mồ côi**, không chỉ lệch số.

## 3. Lượt này tìm ra

| # | Phát hiện | Loại | Xử lý |
|---|---|---|---|
| MT-1 | Công cụ chụp ca bán chuẩn (D002-7) báo đỏ nhầm: mã phiếu nằm trong tiêu đề / ghi chú ("Phiếu bán hàng CNTESBT10042") | lỗi công cụ đo — G-1 không đo được tự động | sửa: thay mã của mọi phiếu trong đơn bằng `{mã}` (open-pos-backend PR) |
| MT-2 | SC-9 preflight lấy **5 đơn cũ nhất** của khoảng quét (build_refs trả id tăng dần) | lỗi tự kiểm (I-8) — đơn mới mã lạ lọt | sửa: phiếu bán trước, mới nhất trước + test (bridge PR) |
| MT-3 | Gửi lại / kéo trạng thái / tự kiểm hằng ngày là lịch WP-Cron của **site chính**; `DISABLE_WP_CRON` mà không có cron hệ thống → không chạy, không báo | vận hành (I-8, I-3) | OKT-MT-3: SC-10 nay báo khi lịch site chính quá hạn (bridge #20); OPS còn cài cron hệ thống |
| MT-4 | Kéo trạng thái hỏi 50 chứng từ / lượt (5 phút) | ghi nhận | đủ cho ~600 chứng từ / giờ / mạng — theo dõi khi nhiều shop |
| MT-5 | Tenant thử chưa khai hồ sơ kế toán (`IN-CFG-001` trên mọi đơn) | cấu hình tenant | thêm vào bước nhận tenant trước khi bật gửi |
| MT-6 | Chứng từ mồ côi (có ở kế toán, không có phiếu gốc WP) | H4 | OKT-H4: đối chiếu theo docKey + tồn (bridge #20) — bắt đúng `sale:900001`; kế toán duyệt huỷ → tồn 8 = 8 |
