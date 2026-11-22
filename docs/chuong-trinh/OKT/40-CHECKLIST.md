# OKT · 40 — Checklist chương trình: nguồn trạng thái duy nhất

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — gom trạng thái mọi việc của chương trình OKT từ checklist các repo (open-pos-backend PHASE-001 40 / 41, PHASE-002 40; open-pos PHASE-001 40; open-ketoan-bridge PHASE-001 40, đều ở main ngày 21/11) về một chỗ. Chủ chốt: trạng thái chỉ ghi ở đây. -->

> **Luật của tệp này:**
> 1. **Trạng thái chỉ ghi ở đây.** Checklist ở từng repo giữ mô tả kỹ thuật và trỏ về đây; không ai cập nhật trạng thái ở repo.
> 2. **✅ chỉ khi cột Bằng chứng có đường dẫn** (test có tên, ca chạy, tệp `evidence/` có ngày giờ và người chạy). ADR-OKT-1 I-7.
> 3. **Đổi trạng thái = một commit ở open-setup**, ghi dấu R-SIG, kèm link PR / bằng chứng ở repo làm việc.
> 4. Việc chạm tệp cấm sửa (ADR D002-6) mà không phải mẫu "chỉ đổi tên bảng" (D002-7) thì **không được** nhận.
>
> Ký hiệu: ☐ chưa làm · 🟡 có mã + test, chưa chạy thật · ✅ có bằng chứng chạy thật · ⛔ chờ chủ / repo khác.
> Cột "Việc" chép nguyên văn từ repo nguồn lúc gom (link đã đổi thành tuyệt đối). Chi tiết kỹ thuật đọc ở tài liệu phase của repo đó.

<!-- [2026-11-21 08:20 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-4 / B001-C10 sang 🟡 (bridge PR #6). -->

<!-- [2026-11-21 08:35 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-5, S002-6 sang 🟡 (bridge PR #7); S002-4 đã merge (bridge PR #6, 4701eef). -->

<!-- [2026-11-21 08:50 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-9, 10, 12 sang 🟡 (bridge PR #8); S002-5, 6 đã merge (bridge PR #7, 96a1f1c). -->

<!-- [2026-11-22 04:40 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — lát dọc L0 → L7 chạy trên WordPress multisite thật (Docker okt-wp): S002-C0, C2, C6, C7 sang 🟡 (open-pos-backend #41); sửa lỗi chỉ WP thật bắt được (open-pos-backend #40, bridge #15, open-pos #26); scoreboard 52,2 %. -->
<!-- [2026-11-22 02:55 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — OKT-SC-2 sang 🟡 (bridge #14, open-pos-backend #40); S001-MD3 đã merge (bf73d65, c4d8b38); scoreboard 44,6 %. -->
<!-- [2026-11-22 01:35 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S001-MD3 sang 🟡 (open-pos-backend #39, bridge #13); OKT-SC-1 đã merge (572b3ad); scoreboard 43,6 %. -->
<!-- [2026-11-22 11:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ: scoreboard kết nối (70) + luật tối thượng tự kiểm theo cặp blog → tenant qua API (I-8, đặc tả 75). -->
<!-- [2026-11-22 09:30 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ duyệt gợi ý cho mọi câu mở ("ok"): Q-OKT-2, Q002-1, Q002-2, Q001-16…20, 24, 25. Sinh việc S002-17, S002-18, S001-C8b, S001-C8c. -->
<!-- [2026-11-22 09:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-0b sang 🟡 (ADR §3b, §5 + open-pos-backend PR #34, open-pos PR #24, bridge PR #11); S002-16 đã merge (57785ec). -->
<!-- [2026-11-21 10:55 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-16 sang 🟡 (open-pos-backend PR #33); ghi merge open-pos #22, #23, open-pos-backend #32, bridge #10. -->
<!-- [2026-11-21 10:15 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-14 sang 🟡 (open-pos PR #23); S002-13 thêm nút ở Cổng kế toán (bridge PR #10). -->
<!-- [2026-11-21 09:40 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-2 (open-pos PR #22), S002-3 (open-pos-backend PR #32) sang 🟡; S002-8, 11, 13 đã merge (bridge PR #9, 1832956). -->
<!-- [2026-11-21 09:05 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — S002-8, 11, 13 sang 🟡 (bridge PR #9); S002-9, 10, 12 đã merge (bridge PR #8, 155c66e). -->

## 0. Số đếm (cập nhật 22/11 04:40 PM)

| Việc còn hiệu lực | ✅ | 🟡 | ⛔ | ☐ | Đã huỷ / chuyển |
|---|---|---|---|---|---|
| 170 | 6 | 39 | 17 | 108 | 16 |

- **Đối chiếu:** 175 dòng việc ở các repo nguồn = 159 còn hiệu lực + 16 đã huỷ / chuyển (P001-T3 còn hiệu lực phần đổi tên bảng; sửa lúc 08:10 PM).
- **Sáu việc ✅:** năm việc chủ trả lời / duyệt (S001-O1, O1b, O5, S002-0d, SW0-3) và **việc chạy thật đầu tiên**: S002-1 (open-ketoan thử `okt-thu`, bằng chứng trên `main`).
- **22/11 11:00 AM:** thêm 5 việc tự kiểm OKT-SC-0…4 (luật I-8) → 168 việc còn hiệu lực. **03:25 PM:** thêm OKT-TR-1, TR-2 (trace theo mockup màn 3) → 170. Điểm kết nối ở [70](70-SCOREBOARD-KET-NOI.md): **52,2 %** (04:40 PM, sau lát dọc L0→L7 trên WP thật), pilot cần 72,5 %.
- **22/11 09:30 AM:** thêm 4 việc sinh từ câu chủ chốt (S002-17, S002-18, S001-C8b, S001-C8c) → 163 việc còn hiệu lực.
- **Chưa có việc mã nào ✅.** Việc mã gần nhất là B001-C1 (bridge PR #2, đã merge, chưa chạy trong WordPress thật) ở mức 🟡.
- **Thứ tự làm** (chi tiết ở [10-ROADMAP](10-ROADMAP.md)): PHASE-002 lát dọc **trước**, rồi các mốc M1–M4 của PHASE-001.

## 1. Việc còn hiệu lực

### OKT — Tự kiểm theo cặp blog → tenant (I-8, [75](75-LUAT-TU-KIEM.md))

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| OKT-SC-0 | open-setup | Luật I-8 vào ADR; đặc tả 75; scoreboard 70 + `tools/okt-scoreboard.mjs` | 🟡 2026-11-22 11:00 AM — PR này | 70, 75 |
| OKT-SC-1 | open-ketoan-bridge | `wp tgs-acc selfcheck --shop=N\|--all`: SC-1…SC-11 qua API bằng khoá của blog; lưu `tgs_acc_tenant_code` khi admin xác nhận; kết quả `tgs_acc_selfcheck_last`; JSON cho `evidence/` _(bất biến I-8, I-1, I-4)_ | 🟡 2026-11-22 11:45 AM — mã + `tests/selfcheck-test.php` 41/41; `tests/selfcheck-live.php` chạy thật vào okt-thu: đơn TM xanh, đơn QR-VTB-CT + R04 + XTA đỏ đúng ba mã, khoá sai 401; chưa chạy trong WordPress | [bridge PR #12](https://github.com/hoanganh8389/open-ketoan-bridge/pull/12) |
| OKT-SC-2 | open-ketoan-bridge | Cron 02:30 mọi blog có khoá; Cổng kế toán hiện kết luận; SC-2 / SC-3 đỏ → tự tạm dừng gửi; cảnh báo hàng chờ ≥ 6 ngày; giữ hàng chờ quá 7 ngày _(I-8, I-3, I-6)_ | 🟡 2026-11-22 02:55 PM — cron 02:30; tự tạm dừng khi SC-2 sai tenant / SC-3 trùng tenant (không khi chỉ không gọi được); hàng chờ shop tạm dừng giữ tới 90 ngày; tab Tự kiểm ở Cổng kế toán; ô Kết nối kế toán ở open-pos-backend; tắt plugin gỡ lịch; tests/sc2-test.php 24/24; chạy thật okt-thu (nhầm tenant → tự dừng); chưa xem trong WordPress | [bridge PR #14](https://github.com/hoanganh8389/open-ketoan-bridge/pull/14), [open-pos-backend PR #40](https://github.com/hoanganh8389/open-pos-backend/pull/40) |
| OKT-SC-3 | cả ba repo mã | Mỗi repo một lệnh `selfcheck` ngoại tuyến (mọi test + `--check=I0`); ghi vào mẫu mô tả PR _(I-8, I-0)_ | ☐ |  |
| OKT-SC-4 | open-ketoan | Đưa I-8 vào CANON (R-OKT-CONN-13) | ⛔ chủ |  |
| OKT-TR-1 | open-ketoan-bridge | Trace chiều bán của một phiếu ở Cổng kế toán: sổ POS → sự kiện → hàng chờ → chứng từ (mã trước / sau ánh xạ, mã băm) → nhật ký gửi → kế toán; chỉ đọc (mockup màn 3) _(bất biến I-0, I-6, I-8)_ | 🟡 2026-11-22 03:25 PM — tab Trace + link từ Nhật ký chứng từ; tests/trace-test.php 27/27; hình dữ liệu documents của okt-thu khớp; chưa xem trong WordPress | [bridge PR #15](https://github.com/hoanganh8389/open-ketoan-bridge/pull/15) |
| OKT-TR-2 | open-pos-backend | Trace chiều danh mục: feed → bộ kéo C8 → bảng của blog → POS (mockup màn 3) _(I-2, I-4)_ | ☐ sau S001-C8 |  |

### PHASE-002 lát dọc — S0 — chuẩn bị

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S002-0a | open-pos-backend | ADR-OKT-1 (00) + research (10) + thiết kế (20) | 🟡 2026-11-21 | PR phase này |
| S002-0b | open-pos-backend | Gộp tài liệu: PHASE-001 doc 26, 27, 28 vào ADR; chuyển vào `PHASE-001-…/archive/`; viết lại 01, 06, 41 theo ADR; cập nhật mục lục | 🟡 2026-11-22 09:00 AM — ADR thêm §3b (D001-16…20), §5 (trạng thái blog, chuyển nguồn, chuyển 92 blog, rủi ro E1–E5); 26/27/28 → archive/; 01 golden G0–G17; 06, 41 theo ADR; banner open-pos, bridge trỏ ADR; 124 link, 0 gãy | [open-pos-backend PR #34](https://github.com/hoanganh8389/open-pos-backend/pull/34), [open-pos PR #24](https://github.com/hoanganh8389/open-pos/pull/24), [bridge PR #11](https://github.com/hoanganh8389/open-ketoan-bridge/pull/11), PR này (ADR) |
| S002-0c | chủ dự án | Báo đội dev đổi hướng (mẫu PHASE-001 doc 14 §5), xin tạm dừng việc mới chạm đường ghi đơn / danh mục trong lúc làm lát dọc | ⛔ chủ |  |
| S002-0d | chủ dự án | Chủ trả lời Q002-1…3 (doc 10 §4) | ✅ 22/11 09:30 AM theo gợi ý (Q002-3 đã chốt 21/11) | [90](90-CAU-HOI-CHO-CHU.md) |

### PHASE-002 lát dọc — S1 — lát dọc

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S002-1 | open-ketoan | open-ketoan Docker + tenant `shopa`, khoá riêng _(bất biến I-1)_ | ✅ 2026-11-22 11:00 AM (bằng chứng merge 78fa10f) — stack `okt-thu` (127.0.0.1:8098, DB 5444) chạy trên máy dev, open-ketoan `71fa48e2`; khoá `shopa` đọc feed / documents; preflight phiếu bán 0 lỗi chặn (1 cảnh báo hồ sơ kế toán chưa khai). WordPress thử: chủ để sau | [evidence/s002-1-okt-thu-2026-11-22.md](https://github.com/hoanganh8389/open-pos-backend/blob/main/docs/phases/PHASE-002-LAT-DOC-MOT-DON-BAN/evidence/s002-1-okt-thu-2026-11-22.md) |
| S002-2 | open-pos | `tests/setup-lat-doc.php`: 2 blog, ba plugin, bỏ bật React, khoá theo blog, cron thật _(bất biến I-1)_ | 🟡 2026-11-21 09:15 PM — script dựng blog A (nối kế toán, nguồn sổ POS, CN01) + blog B (tự quản), tạo bảng theo blog, kiểm feed/meta; cron thật chạy tay theo hướng dẫn đầu file; chưa chạy trên LocalWP thật | [open-pos PR #22](https://github.com/hoanganh8389/open-pos/pull/22) (đã merge 8f882a6) |
| S002-3 | open-pos-backend | `tools/lat-doc-seed.php`: nhóm, mã, bảng giá, gán blog, ĐVT, giá, nhập kho; chạy lại được _(bất biến —)_ | 🟡 2026-11-21 09:40 PM — seed blog A: nhóm LATDOC, SKU 900000001 (Cái, 10 %), bảng giá LATDOC gán blog A, 11.000 gồm VAT, nhập 10 qua create_import_ledger + duyệt; php -l sạch; chưa chạy trên LocalWP thật | [open-pos-backend PR #32](https://github.com/hoanganh8389/open-pos-backend/pull/32) (đã merge 93e477f) |
| S002-4 | open-ketoan-bridge | `TGS_Acc_Source_Pos` (= B001-C10) + `ready()` + test _(bất biến I-3)_ | 🟡 2026-11-21 08:11 PM — mã + test (tests/source-pos-test.php, 38 phép kiểm đạt); nguồn sổ POS mặc định tắt, bật theo blog; chưa chạy trong WordPress thật | [bridge PR #6](https://github.com/hoanganh8389/open-ketoan-bridge/pull/6) (đã merge 4701eef) |
| S002-5 | open-ketoan-bridge | Option `tgs_acc_branch_code` theo blog; `ensure_branch` không tạo trùng _(bất biến I-4)_ | 🟡 2026-11-21 08:30 PM — mã + test (tests/branch-unit-test.php, 17 phép kiểm); mã chi nhánh khai theo blog, mã khai sai thì báo lỗi, không tạo chi nhánh trống; chưa chạy trong WordPress thật | [bridge PR #7](https://github.com/hoanganh8389/open-ketoan-bridge/pull/7) (đã merge 96a1f1c) |
| S002-6 | open-ketoan-bridge | `TGS_Acc_Money::split_vat` + làm tròn dòng; `unit` = ĐVT nhỏ nhất _(bất biến I-5)_ | 🟡 2026-11-21 08:30 PM — phần ĐVT: dòng nguồn sổ POS gửi ĐVT nhỏ nhất ở unit; phần hàm tiền đã có ở S002-4 (công thức của TGS_POS_BCTK_Sales_Service); chưa chạy trong WordPress thật | [bridge PR #7](https://github.com/hoanganh8389/open-ketoan-bridge/pull/7) (đã merge 96a1f1c) |
| S002-7 | open-ketoan-bridge | Thuế lẻ không khớp 6 mã → lỗi rõ, không gửi _(bất biến I-5)_ | ☐ |  |
| S002-8 | open-ketoan-bridge | `wp tgs-acc preflight` _(bất biến I-5)_ | 🟡 2026-11-21 09:00 PM — wp tgs-acc preflight (test tests/pause-cli-test.php); chưa chạy với open-ketoan thật | [bridge PR #9](https://github.com/hoanganh8389/open-ketoan-bridge/pull/9) |
| S002-9 | open-ketoan-bridge | Nhật ký gửi giữ `pending` riêng _(bất biến I-4)_ | 🟡 2026-11-21 08:45 PM — nhật ký gửi giữ pending / remote_error riêng; không gửi lại cùng nội dung; test (tests/status-test.php, 21 phép kiểm); chưa chạy trong WordPress thật | [bridge PR #8](https://github.com/hoanganh8389/open-ketoan-bridge/pull/8) (đã merge 155c66e) |
| S002-10 | open-ketoan-bridge | Kéo trạng thái theo `docKey` → `posted` / `error` _(bất biến I-6)_ | 🟡 2026-11-21 08:45 PM — refresh_status theo docKey + cron tgs_acc_status_pull 5 phút; chưa chạy trong WordPress thật | [bridge PR #8](https://github.com/hoanganh8389/open-ketoan-bridge/pull/8) (đã merge 155c66e) |
| S002-11 | open-ketoan-bridge | `wp tgs-acc status` (5 số) _(bất biến I-6)_ | 🟡 2026-11-21 09:00 PM — wp tgs-acc status: năm số + cảnh báo; chưa chạy trong WordPress thật | [bridge PR #9](https://github.com/hoanganh8389/open-ketoan-bridge/pull/9) |
| S002-12 | open-ketoan-bridge | Cron gửi lại dùng `for_blog($blog)` _(bất biến I-1)_ | 🟡 2026-11-21 08:45 PM — TGS_Acc_Api_Client::for_blog; Events gửi tức thời + cron gửi lại theo blog; chưa chạy trong WordPress thật | [bridge PR #8](https://github.com/hoanganh8389/open-ketoan-bridge/pull/8) (đã merge 155c66e) |
| S002-13 | open-ketoan-bridge | Tạm dừng kết nối theo blog `tgs_acc_paused` + nút; vẫn ghi sự kiện, không gửi, không thử lại _(bất biến I-0, I-3)_ | 🟡 2026-11-21 09:00 PM — tgs_acc_paused theo blog + wp tgs-acc pause / resume; hàng chờ giữ 7 ngày; 10:15 PM nút Tạm dừng / Bỏ tạm dừng + cột Kết nối ở Cổng kế toán, danh sách shop gộp blog nguồn sổ POS; chưa chạy trong WordPress thật | [bridge PR #9](https://github.com/hoanganh8389/open-ketoan-bridge/pull/9) (đã merge 1832956), [bridge PR #10](https://github.com/hoanganh8389/open-ketoan-bridge/pull/10) (đã merge 67587a7) |
| S002-14 | open-pos-backend / open-pos | Admin của blog đổi `tgs_pos_engine` react ↔ legacy, có nhật ký; không sửa checkout _(bất biến I-0)_ | 🟡 2026-11-21 10:00 PM — màn POS → Máy bán của shop + nhật ký tgs_pos_engine_log (bắt cả Quản trị mạng, WP-CLI); test 14 phép kiểm; chưa bấm thử trên WordPress thật | [open-pos PR #23](https://github.com/hoanganh8389/open-pos/pull/23) (đã merge bc63819) |
| S002-16 | open-pos-backend | Census `--check=I0` theo danh mục D002-6 + ca bán chuẩn so dòng sổ _(bất biến I-0)_ | 🟡 2026-11-21 10:55 PM — census --check=I0 (selftest 13 ca; open-pos main sau PR #22, #23 xanh) + tools/lat-doc-sale-snapshot.php + --compare; ca bán chuẩn chưa chạy trên đơn thật (cần S002-1) | [open-pos-backend PR #33](https://github.com/hoanganh8389/open-pos-backend/pull/33) (đã merge 57785ec), [bằng chứng](https://github.com/hoanganh8389/open-pos-backend/blob/main/docs/phases/PHASE-002-LAT-DOC-MOT-DON-BAN/evidence/census-i0-2026-11-21.md) |
| S002-17 | open-ketoan-bridge | Gộp tiền vào `sale.payments` (một đơn một chứng từ); mã phương thức từ bảng ánh xạ lưu sẵn, không suy từ nhãn; tiền mặt theo Q002-3 (`min(tiền khách đưa, tổng đơn)` nếu kế toán cần); kiểm đơn thu 0đ / ghi nợ _(Q002-2; bất biến I-0, I-4, I-5)_ | ☐ sau lát dọc |  |
| S002-18 | open-ketoan-bridge | So khoá chứng từ nguồn tgs-bc-tk với nguồn sổ POS trên **một shop thật**: cùng đơn ra cùng `btsoft:{blog}:sale:{id}` thì mới đổi nguồn shop đang chạy _(Q002-1; bất biến I-4)_ | ☐ chủ chọn shop |  |

### PHASE-002 lát dọc — S2 — chạy ca và ghi bằng chứng

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S002-C0 | open-pos-backend | L0 môi trường | 🟡 2026-11-22 04:40 PM — WordPress multisite thật (Docker okt-wp) + okt-thu: 2 blog, 3 plugin, bảng theo blog, blog A nối kế toán; tools/lat-doc-docker dựng lại được | [open-pos-backend PR #41](https://github.com/hoanganh8389/open-pos-backend/pull/41) |
| S002-C2 | open-pos-backend | L2 bán 1 đơn, không gọi HTTP trong request bán | 🟡 2026-11-22 04:40 PM — bán 1 Cái × 11.000 qua AJAX tgs_pos_save_order của POS cũ (main, không sửa): phiếu 10 + 7 + 2, tồn 10 → 9. Phần "không gọi HTTP trong request bán" chưa đo (cần request HTTP thật) | [open-pos-backend PR #41](https://github.com/hoanganh8389/open-pos-backend/pull/41) |
| S002-C5 | open-pos-backend | L5 preflight 0 lỗi | ☐ |  |
| S002-C6 | open-pos-backend | L6 gửi → `pending` × 2 | 🟡 2026-11-22 04:40 PM — bridge tự gửi sau khi lưu đơn → btsoft:2:sale:2 + btsoft:2:receipt:3 pending v1 ở kế toán, tổng 11.000, CN01 (2 chứng từ như thiết kế lát dọc) | [open-pos-backend PR #41](https://github.com/hoanganh8389/open-pos-backend/pull/41) |
| S002-C7 | open-pos-backend | L7 duyệt → `posted` trong nhật ký gửi | 🟡 2026-11-22 04:40 PM — kế toán định khoản 0 lỗi (BT26-0000001, BT26-0000002; chi nhánh chưa có kho vẫn được) → pull_status đổi pending → posted | [open-pos-backend PR #41](https://github.com/hoanganh8389/open-pos-backend/pull/41) |
| S002-C9 | open-pos-backend | L9 gửi lại / sửa / huỷ | ☐ |  |
| S002-C10 | open-pos-backend | L10 K-A: tắt kế toán 2 phút (POS cũ) | ☐ |  |
| S002-C11 | open-pos-backend | L11 K-C + K-D: tạm dừng kết nối, bán 3 đơn, nối lại, gửi bù không trùng | ☐ |  |
| S002-C12 | open-pos-backend | L12 K-B: kế toán tắt trước khi mở ca, chuyển shop React → POS cũ | ☐ |  |
| S002-C13 | open-pos-backend | L13 K-A với POS React (chế độ dự phòng có sẵn), chỉ ghi nhận | ☐ |  |
| S002-C14 | open-pos-backend | L14 I-0: `--check=I0` xanh, ca bán chuẩn trước / sau giống nhau | ☐ |  |
| S002-CX | open-pos-backend | Đo lại bảng điểm PHASE-001 doc 29 bằng bằng chứng | ☐ |  |

### PHASE-001 danh mục theo site — OPS / chủ

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-O1 | open-pos-backend | Chủ trả lời Q001-1…9 | ✅ 2026-11-21 01:03 PM |  |
| S001-O1b | open-pos-backend | Chủ trả lời Q001-10…15 | ✅ 2026-11-21 01:51 PM: 15/15 |  |
| S001-O4 | open-pos-backend | Dừng hẳn bảng global catalog / giá sau khi mọi blog `tgs_catalog_store = local` qua một chu kỳ bán | ☐ (M5) |  |
| S001-O5 | open-pos-backend | Chủ duyệt bản đồ chương trình 3 repo (05) và ba PR tài liệu | ✅ 2026-11-21 04:04 PM: duyệt bản đồ; bắt đầu từ tsm, census trước; smallwin SW1–SW4 ([06](https://github.com/hoanganh8389/open-pos-backend/blob/main/docs/phases/PHASE-001-DANH-MUC-THEO-SITE-DONG-BO-KETOAN/06-SMALLWIN-SW1-SW4.md), tiến độ [41](https://github.com/hoanganh8389/open-pos-backend/blob/main/docs/phases/PHASE-001-DANH-MUC-THEO-SITE-DONG-BO-KETOAN/41-TIEN-DO-SMALLWIN.md)) |  |

### PHASE-001 danh mục theo site — B0 — tài liệu + census

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-W0a | open-pos-backend | Bộ hồ sơ phase | 🟡 2026-11-20 |  |
| S001-W0b | open-pos-backend | Tool census (manifest 46 hàm, `--check=B1/B2/B3`) | 🟡 baseline erp 35 · khoá cũ 9 · cổng 0 |  |
| S001-W0d | open-pos-backend | Vòng 1: doc 25, banner 20 / 30 | 🟡 21/11 12:36 PM |  |
| S001-W0e | open-pos-backend | Census `--check=G0` (tham chiếu bảng global catalog + giá, tsm + `--pos=`; mục tiêu 0) và `--check=T1` (không hằng `TGS_TABLE_LOCAL_PRODUCT_*` trong đường đọc mới) và `--check=T2` (không `'wp_` viết cứng ngoài `database/migrations`) | 🟡 2026-11-21 04:04 PM qua SW0-1: `--check=G0 / T1 / T2 / Q0` chạy được, cả 4 đỏ; mốc `evidence/sw0-baseline-2026-11-21.json` (G0 268 dòng / 57 file, T2 123 / 17, Q0 11) |  |
| S001-W0h | open-pos-backend | R-OKT-CONN vào CANON open-ketoan | 🟡 [PR #516](https://github.com/hoanganh8389/open-ketoan/pull/516) chờ duyệt |  |
| S001-G0 | open-pos-backend | Mục tiêu golden G1–G14, lỗ L-G1…12 | 🟡 21/11 01:48 PM |  |
| S001-G1d | open-pos-backend | Bản đồ chương trình 3 repo, hợp đồng giữa repo, mốc M1–M5; phase tgs_pos + bridge; khảo sát lần 2 (12 + evidence) | 🟡 2026-11-21 02:20 PM |  |

### PHASE-001 danh mục theo site — M1 — Standalone: bảng theo prefix (đạt G1–G4, G14 cùng P001 M1)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-C11 | open-pos-backend | `tgs_catalog_table($kind, $blog_id)` (`product \| cat \| price_list \| price_item \| unit_convert \| tax`), `tgs_catalog_sellable()`; DB_VERSION++: `sql_local_product_name` (`:820`) thêm cột `item_id`, `parent_item_id`, `variant`, `send_tax`, `is_kct`, `is_main`, `no_sale`, `is_active`, `source`, `erp_synced_at`, `erp_hash`, nhóm `site` (25 §3), `push_*`, `UNIQUE(local_product_sku)`; `local_product_cat` thêm `item_group_id`, `parent_id`, `source`; bảng mới `{p}local_price_list`, `_price_list_item`, `_unit_convert`, `tgs_acc_sync_state`, `tgs_acc_sync_log`; **`TGS_Item_Variant` đọc theo blog** | ☐ **merge đầu tiên** (P001-T1, B001-C13 chờ) |  |
| S001-C19 | open-pos-backend | Gỡ `TGS_Shop_Query::is_legacy_product_table` (`database/class-tgs-query.php:57-80`) cùng slice với C11, kèm test cho lớp query | ☐ |  |
| S001-C21 | open-pos-backend | Tên bảng viết cứng `wp_`: 3 hằng (`class-tgs-constants.php:236, 246, 252`) → `base_prefix`; 72 chỗ runtime (batch-distribution 20, ajax-ticket 15, ticket-base 8, api-sales 5, ajax-product 3, ajax-lot 2…), 13 `CREATE TABLE wp_global_…`, 9 fallback; `{p}global_loyalty_*` / `global_blogs` đặt tên sai để nguyên nhưng ghi chú | ☐ (M1; lô / batch ngoài phase nhưng phải không vỡ trên tiền tố khác) |  |
| S001-C12 | open-pos-backend | Tool `wp tgs catalog migrate-to-site [--blog\|--all] [--dry] [--backup-legacy]`: kiểm bảng legacy, chép giữ id, **`ALTER … AUTO_INCREMENT = max+1`**, kiểm `local_product_name_id = global_product_name_id` = 100 %, đánh `source`, đặt `tgs_price_list_id`, hash vào `evidence/` | ☐ |  |
| S001-C13 | open-pos-backend | Cờ `tgs_catalog_store = global \| local` (công tắc lùi); `tgs_catalog_table()` theo cờ | ☐ |  |
| S001-C20 | open-pos-backend | Tách `run_migrations` (83 file) thành `global` (một lần, site option) và `local` (theo blog); ghi `tgs_db_version` **sau** khi thành công (hiện ghi trước, `class-tgs-database.php:82`) | ☐ |  |
| S001-G1 | open-pos-backend | Móc `wp_initialize_site` → `switch_to_blog` → `create_tables()`; `maybe_auto_upgrade` cũng chạy ở `init` cho REST / AJAX khi thiếu `tgs_db_version`; POS kiểm bảng trước khi mở ➡ P001-T5 | ☐ |  |
| S001-C4 | open-pos-backend | Cổng ghi `tgs_catalog_write_gate()` ở đầu 35 hàm `erp` + 2 `tax` (MANIFEST), đích ghi → `tgs_catalog_table()`; chế độ tính từ `tgs_okt_connected()` (M1: luôn standalone); `--check=B2` xanh | ☐ |  |
| S001-C2 | open-pos-backend | `tgs_okt_connected()` **dự phòng** (chỉ khi bridge chưa định nghĩa, trả `false`); `tgs_catalog_mode()`; `tgs_catalog_readonly_guard()` thành vỏ. Bản thật ➡ B001-C6 | ☐ |  |
| S001-C5 | open-pos-backend | `do_action('tgs_catalog_changed', $blog, $table, $ids, $op)` sau mọi ghi (46 hàm + lượt kéo); option `tgs_catalog_version` theo blog; `TGS_Shop_Cache_Bridge::writes_by_table` thêm `local_product_name`, `local_product_cat`, `global_product_lots`, bulk ticket; xoá key `v3` chết (`admin-settings.php:975`) | ☐ (P001-CACHE chờ) |  |
| S001-C14 | open-pos-backend | `tgs_default_vat_rate()` (option, mặc định 8); product-add :83, excel-import :1760 dùng hàm này | ☐ |  |
| S001-C6 | open-pos-backend | Capability `tgs_catalog_site_edit`, `tgs_catalog_edit`, `tgs_catalog_connect` | ☐ |  |
| S001-C10 | open-pos-backend | REST `tgs-shop/v1/products*` đòi đăng nhập + blog hiện tại (bỏ `blog_id` đè); xoá token demo `api-customer-insights.php:18` | ☐ |  |
| S001-G2 | open-pos-backend | Khách theo blog: index `local_ledger_person_phone`; listener `tgs_sale_completed` (`class-tgs-global-customer-history.php:81`) chỉ chạy khi option mạng `tgs_customer_directory_enabled`; `api-customer-insights` quét site → mặc định blog hiện tại; bỏ `shop-helper.php:28-32` (`global_blogs`) | ☐ (Q001-14 ✅) |  |
| S001-G5 | open-pos-backend | Smoke test multisite chỉ 3 plugin (G1–G4) | ☐ (cùng P001-T6) |  |

### PHASE-001 danh mục theo site — M2 — Kết nối (đạt G5)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-C1 | open-pos-backend | `tgs_tenant_of_blog($blog)` = `tgs_okt_connection($blog)['tenant']`; `tgs_branch_of_blog()` giữ làm vỏ | ⛔ chờ B001-C6 |  |
| S001-C3 | open-pos-backend | Màn site **Đồng bộ kế toán** (trạng thái từ `tgs_okt_connection()`, link sang màn Kết nối của bridge, ánh xạ tự dựng, lần kéo, đối chứng, "thay đổi đã bị ghi đè"); màn Kết nối / khoá ➡ B001-C4 | ⛔ chờ B001-C6 |  |
| S001-C3b | open-pos-backend | Network "Danh mục & Kế toán": bảng tổng blog (chế độ, tenant, lần kéo, lỗi) | ⛔ chờ B001-C6 |  |
| S001-C17 | open-pos-backend | `{p}tgs_okt_offline_edit`: ghi sửa `erp` / giá / thuế lúc mất kết nối; lượt kéo ghi đè và đánh dấu | ☐ |  |

### PHASE-001 danh mục theo site — M3 — Đồng bộ (đạt G6, G7, G10–G13)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-C8 | open-pos-backend | `TGS_Acc_Catalog_Pull::run($blog, $opts)`: client `TGS_Acc_Api_Client::for_blog`; meta → products → prices; chỉ cột `erp`; khoá chạy; con trỏ ở `{p}tgs_acc_sync_state`; chống kẹt `FEED_CURSOR_STUCK`; `since − 2 phút`; N2 rải `blog_id mod 5`; N3 chặn 1 lần / phút; lắng `tgs_okt_catalog_changed` (N1); hợp đồng feed ở bridge doc 10 §4; **đặc tả trường + F1, F4–F7, F10, F12, F14 ở 81 §2–§3, §6** | ⛔ chờ B001-C2 |  |
| S001-C18 | open-pos-backend | Tự ánh xạ mặc định lần đầu (tenant, chi nhánh mặc định, bảng giá, nhóm, ĐVT, mã thuế, hình thức thanh toán từ `feed/meta` + lists) + đối chứng (đếm, hash) vào `tgs_acc_sync_log`; lắng `tgs_okt_connection_changed` | ⛔ chờ B001-C6 |  |
| S001-C8b | open-pos-backend | Bộ kéo: không ghi chuỗi rỗng đè barcode / ảnh / mô tả (81 F7); mã trơn (kế toán chưa có ĐVT) → gửi lại không `?new=1`, chỉ điền ô trống, không ghi đè tên / giá / thuế, có nhật ký _(Q001-19; I-2, I-4)_ | ☐ (cùng C8) |  |
| S001-C8c | open-pos-backend | Bộ kéo: bảng giá của blog = bảng gán cho chi nhánh `tgs_acc_branch_code`; không có gán → bảng giá công ty; áp DM14 (D002-8); bỏ dò `wp_blogs.tgs_site_code` (81 F11) _(Q001-20; I-4)_ | ☐ (cùng C8) |  |
| S001-C15 | open-pos-backend | `SYNC_TAX` bật: kéo `taxRate`; ảnh thuế trước lần đầu vào `evidence/` | ☐ |  |
| S001-C16 | open-pos-backend | Kết nối lần đầu: khớp mã `local` theo SKU / barcode, gắn `item_id`; không khớp → hàng gửi (C9) | ☐ |  |
| S001-BR2 | open-pos-backend | Tombstone `replacedByItemId` → chuyển cột `site`; tombstone `price_list` → xoá dòng giá; so cây nhóm | ☐ (trong C8) |  |
| S001-BR5 | open-pos-backend | N4 đối soát đêm 02:00 theo `erp_hash`; không đọc lại bằng con trỏ `after` (kẹt cùng L1, 81 F15) | ☐ |  |

### PHASE-001 danh mục theo site — M4 — Chứng từ (đạt G8, G9)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-C9 | open-pos-backend | Ở `connected`: tạo mã → `push_status = sent` → `PUT /catalog/products/:sku?new=1` + `Idempotency-Key` qua client blog; thử lại 1 → 5 → 30 phút; 409 / 422 → `rejected`; feed về khớp SKU → `accepted`; bán ngay | ⛔ chờ B001-C2; K8 |  |

### PHASE-001 danh mục theo site — M5 — Golden (G1–G14 trọn)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-P3 | open-pos-backend | Route `GET /tgs-shop/v1/catalog/snapshot` (blog hiện tại, cùng hình dạng `/pos/catalog/snapshot` của kế toán) cho blog standalone; POS React chọn nguồn ➡ P001-P3 | ☐ |  |
| S001-G6 | open-pos-backend | Script dựng multisite thử (3 blog, 2 open-ketoan thử `db:seed`) + chạy G1–G14; ghi `evidence/` | ☐ |  |

### PHASE-001 danh mục theo site — Phía open-ketoan (repo open-ketoan, theo R-FLOW; theo dõi ở đây)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-K1 | open-pos-backend | Sửa con trỏ µs feed + test + index | ☐ **chặn M3 rộng**; dòng CLAIMS PHASE-026 |  |
| S001-K2 | open-pos-backend | Chạm `products.updated_at` khi Gate A / activate | ☐ |  |
| S001-K3 | open-pos-backend | Sửa tài liệu feed / notify | ☐ |  |
| S001-K4 | open-pos-backend | `catalog-notify`: URL dạng `rest_route`, phát khi ghi qua `/items/*` và tự tạo từ chứng từ | ☐ |  |
| S001-K5 | open-pos-backend | Scope hẹp chỉ tạo mã mới | ☐ |  |
| S001-K6 | open-pos-backend | Feed giá lọc theo `branch` | ☐ |  |
| S001-K7 | open-pos-backend | Trường feed còn thiếu | ☐ |  |
| S001-K8 | open-pos-backend | Mã tự tạo từ đơn + mã shop gửi cùng SKU → cùng `item_id` | ☐ chặn G9 |  |
| S001-K9 | open-pos-backend | Tách 92 chi nhánh `tgs` thành tenant theo blog | ☐ **chặn bật kết nối trên mạng thật** |  |
| S001-K10 | open-pos-backend | **Cấp tenant** cho shop mới (hiện chỉ `db:seed`, `packages/kernel/src/db/seed.ts:132`) | ☐ chặn production; môi trường thử dùng `db:seed` |  |
| S001-K11 | open-pos-backend | Mỗi tenant một kết nối ngược (`PUT /api/v1/connections`) trỏ REST của blog; khoá tự đăng ký hoặc kế toán khai khi cấp tenant | ☐ chặn N1 (G7 ≤ 1 phút); không có thì cron 5 phút |  |
| S001-K12 | open-pos-backend | `feed/products` trả `sourceSystem` (hoặc `isPlaceholder`) để WP nhận ra mã tự tạo từ chứng từ | ☐ không chặn; WP tạm đoán bằng "không có ĐVT" |  |
| S001-K13 | open-pos-backend | Tenant đặt được `postingModes.sale = auto` (hoặc để shop chọn): đơn POS hiện lên `pending` | ☐ chặn pilot |  |
| S001-K14 | open-pos-backend | Route / feed giá DM14 đã phân giải theo chi nhánh cho khoá API | ☐ không chặn |  |
| S001-K15 | open-pos-backend | Tích điểm cho đơn đến qua `documents/batch` | ☐ ngoài phase |  |
| S001-K16 | open-pos-backend | Mã thuế thay `8` sau 2026-12-31; sửa ví dụ hợp đồng còn `R08` | ☐ **hạn 2026-12-31** |  |

### PHASE-001 danh mục theo site — Master data (từ [29](https://github.com/hoanganh8389/open-pos-backend/blob/main/docs/phases/PHASE-001-DANH-MUC-THEO-SITE-DONG-BO-KETOAN/29-DANH-GIA-MASTER-DATA-VA-LO-TRINH.md) §3)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-MD0 | open-pos-backend | Census `--check=MD`: chấm tự động bảng 19 nhóm (bảng theo blog, cổng ghi phủ bao nhiêu hàm, ánh xạ lưu mã hay suy ra); ghi mốc vào 41 | ☐ M0 |  |
| S001-MD1 | open-pos-backend | Màn ĐVT và màn bảng giá theo blog (chưa có ở đâu); ghi giá khi tạo mã | ☐ M1 |  |
| S001-MD2 | open-pos-backend | Một bảng ánh xạ thuế dùng chung tsm + bridge (bỏ R00 / R08 mâu thuẫn); xử lý mã `8` sau 2026-12-31 | ☐ **trước 2026-12-31** |  |
| S001-MD3 | open-pos-backend | `{p}tgs_okt_map(kind, local_code, remote_code)` tự dựng từ `/posting/payment-methods`, `/posting/reasons`, `/branches`, `/warehouses`, feed/meta; màn xem / sửa | 🟡 2026-11-22 01:35 PM — bảng {p}tgs_okt_map + TGS_Okt_Map + màn Ánh xạ kế toán (test 34/34); bridge dịch mã khi dựng chứng từ + `wp tgs-acc map` (test 18/18); trọn vòng okt-thu: QR-VTB-CT → QR, XTA → XTA1.4, R04 không đoán; chưa chạy trong WordPress | [open-pos-backend PR #39](https://github.com/hoanganh8389/open-pos-backend/pull/39), [bridge PR #13](https://github.com/hoanganh8389/open-ketoan-bridge/pull/13) |
| S001-MD5 | open-pos-backend | Sửa lỗi đứng: không repo nào tạo `wp_blogs.tgs_site_code`; danh bạ khách chung cả mạng | ☐ M0 |  |
| S001-MD6 | open-pos-backend | Môi trường thử (29 §6) + SEED-B 200 mã theo chuẩn doc 16 (29 §7) | ☐ M0 |  |

### PHASE-001 smallwin — Tổng

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW1 | open-pos-backend | census G0 / T1 / T2 / Q0 xanh (tsm + pos); G1–G4 đạt trên multisite mới; blog cờ `global` không đổi | ☐ |  |
| SW3 | open-pos-backend | G5, G14 đạt; `--check=B2` xanh; blog không kết nối sửa được mọi thứ, 0 lời gọi ra open-ketoan | ☐ |  |
| SW4 | open-pos-backend | điểm sẵn sàng blog thử 100 %; `dryRun` trên tenant thử 0 lỗi | ☐ |  |
| SW2 | open-pos-backend | G6–G13 đạt (tenant `db:seed`); lần đầu kết nối 1000 mã, 0 lệch đối chứng | ⛔ Q001-16, K11 (sự kiện), K10 (production) |  |

### PHASE-001 smallwin — SW0 — chuẩn bị

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW0-1 | open-pos-backend | Census mở rộng `--check=G0 / T1 / T2 / Q0`, `--files`, `--json` | 🟡 2026-11-21 04:04 PM — chạy được, cả 4 đỏ đúng; mốc đã ghi |  |
| SW0-2 | open-pos-backend | Doc 14 (tên bảng `wp_`), 15 (`TGS_Shop_Query`), 16 (chuẩn hàng hoá), 06 (kế hoạch), 41 (tiến độ) | 🟡 2026-11-21 04:04 PM |  |
| SW0-3 | open-pos-backend | Chủ trả lời Q001-16, Q001-17, Q001-18 | ✅ 22/11 09:30 AM: cả ba theo gợi ý 1 | [90](90-CAU-HOI-CHO-CHU.md) |
| SW0-4 | open-pos-backend | Thông báo điều chỉnh cho dev (doc 14 §5) dán vào kênh team khi SW1 mở | ☐ |  |

### PHASE-001 smallwin — SW1 — mỗi blog tự thêm / nhập và bán

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW1-1 | open-pos-backend | `tgs_catalog_table()`, cờ `tgs_catalog_store`, DDL 5 bảng `tgs_catalog_*`, tạo khi `wp_initialize_site`, cờ phiên bản ghi sau | ☐ ⛔ Q001-18 (mặc định tạm 1) |  |
| SW1-2 | open-pos-backend | 15 hằng + 62 chỗ `wp_` → `base_prefix` | ☐ |  |
| SW1-3 | open-pos-backend | Gỡ chuyển hướng `TGS_Shop_Query` + test | ☐ |  |
| SW1-4 | open-pos-backend | 6 đường tạo mã + update / tax / category → `tgs_catalog_table()`; kiểm SKU gồm dòng xoá; ĐVT bắt buộc; thuế qua hàm; hook `tgs_catalog_changed` | ☐ |  |
| SW1-5 | open-pos-backend | Ghi giá theo blog khi tạo mã; màn giá standalone; `TGS_Price_List` đọc bảng giá blog | ☐ |  |
| SW1-6 | open-pos-backend | Nhập: Excel (ĐVT, giá), "Nhập từ danh mục mạng" (`TGS_Shop_Sync_Product::sync`), tool chép giữ id | ☐ |  |
| SW1-7 | open-pos-backend | `TGS_Global_Product_Source::product_table()` → `tgs_catalog_table()` | ☐ |  |
| SW1-8 | tgs_pos | POS: P001-T1…T5, CACHE; danh sách theo catalog khi `local` | ☐ |  |
| SW1-9 | open-pos-backend | Bộ kiểm SW4a ở mức W cắm vào SW1-4 / SW1-6 | ☐ |  |
| SW1-10 | open-pos-backend | Ca G1–G4 trên site thử | ☐ |  |

### PHASE-001 smallwin — SW3 — bridge tắt: blog là gốc

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW3-1 | open-pos-backend | `tgs_okt_connected()` dự phòng, `tgs_catalog_mode()` | ☐ |  |
| SW3-2 | open-pos-backend | Cổng ghi ở 35 + 2 hàm; `--check=B2` | ☐ |  |
| SW3-3 | open-pos-backend | Gỡ bridge: không fatal (G14) | ☐ |  |
| SW3-4 | bridge | Bridge có, blog không khoá / kiểm lỗi → standalone (G5) | 🟡 phần C1: PR #2 (chưa merge, chưa chạy WP thật) |  |

### PHASE-001 smallwin — SW4 — chuẩn hàng hoá

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW4a-1 | open-pos-backend | `TGS_Catalog_Standard::check_product()` H-1…H-18 | ☐ |  |
| SW4a-2 | open-pos-backend | Bộ sinh SKU theo cây nhóm; 40 ĐVT chuẩn; ánh xạ mã thuế | ☐ |  |
| SW4a-3 | open-pos-backend | Điểm sẵn sàng + màn "Chuẩn hàng hoá" | ☐ |  |
| SW4b-1 | open-pos-backend | Dựng sẵn tenant: nhóm có `sku_code`, bảng giá công ty, chi nhánh | ☐ |  |
| SW4b-2 | open-pos-backend | Kiểm thử `dryRun` | ☐ |  |

### PHASE-001 smallwin — SW2 — kết nối: lên chuẩn hoá rồi về bán

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SW2-1 | bridge + tsm | Kết nối theo blog | ☐ |  |
| SW2-2 | open-pos-backend | Lần đầu bật: dựng sẵn → dryRun → đẩy lô → kéo về → gắn `item_id` → đối chứng | ☐ |  |
| SW2-3 | open-pos-backend | Lượt kéo theo blog, chỉ cột `erp`, tombstone, đối soát đêm | ☐ |  |
| SW2-4 | open-pos-backend | Thêm mã / sửa giá khi kết nối = gửi lên; chưa về chưa bán | ⛔ Q001-16 |  |
| SW2-5 | tgs_pos | Mã lạ → kéo → thử lại | ☐ |  |
| SW2-6 | cả ba | Ca G6–G13 | ☐ |  |

### PHASE-001 POS bảng theo blog — B0 — tài liệu

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| P001-W0 | open-pos | Bộ hồ sơ phase + khảo sát máy 21/11 | 🟡 2026-11-21 02:20 PM |  |
| P001-DOC | open-pos | Phụ chú D13 ở `docs/ke-hoach-react-api/*` (00, 10, 16, 08, 13 và các file ở 10 §9); `13-fake-api.md` đổi tên bảng sang theo blog | ☐ (M1) |  |

### PHASE-001 POS bảng theo blog — M1 — Standalone: đọc bảng theo blog

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| P001-T1 | open-pos | 10 helper tên bảng (`TGS_POS_Global_Products::*_table`, `TGS_POS_Price_List::*_table`, `TGS_POS_Material_Policy::*_table`, stock-max `global_product_table`) → `tgs_catalog_table($kind, $blog_id)`; bỏ `ensure_global_product_source()` `require_once` theo đường dẫn | ⛔ chờ tsm S001-C11 · ⚠️ **chỉ đổi tên bảng** (ngoại lệ D002-7 của ADR-OKT-1): không đổi truy vấn / lọc / tính; ca bán chuẩn trước–sau giống hệt; cờ lùi `tgs_catalog_store` |  |
| P001-T2 | open-pos | 9 chỗ vượt helper + 7 fallback `defined(...) ?: 'wp_global_*'` + `promo-migrate::TABLE` dùng helper; `wp_` viết cứng ở lô / policy / training → `$wpdb->base_prefix`; `--check=G0` (tsm) với `--pos=` ra 0 | ☐ · ⚠️ **chỉ đổi tên bảng** (D002-7), như T1 |  |
| P001-T3 | open-pos | `TGS_POS_Price_List`: đọc bảng giá theo blog — **chỉ đổi tên bảng** (D002-7); phần luật DM14 bỏ (áp ở bộ kéo, D002-8). Chi tiết: [open-pos checklist](https://github.com/hoanganh8389/open-pos/blob/main/docs/phases/PHASE-001-POS-BANG-THEO-BLOG/40-MASTER-CHECKLIST.md) | ⛔ chờ tsm S001-C11 · ⚠️ phần **tên bảng** theo D002-7; ❌ **bỏ phần luật DM14**: luật áp ở bộ kéo tsm, ghi sẵn vào bảng giá (D002-8) |  |
| P001-T4 | open-pos | 22 chỗ báo cáo dùng `get_blog_prefix($blog_id)` cho ledger phải truyền cùng `$blog_id` vào helper catalog / giá; 3 AJAX (`ajax-return:42`, `ajax-exchange-return:28`, `ajax-policy-stats:30`) kiểm quyền trên blog đích trước khi `switch_to_blog` | ☐ |  |
| P001-CACHE | open-pos | Lắng `tgs_catalog_changed($blog, …)`: xoá `tgs_pos_all_products_v9_<blog>_*`, `tgs_pos_search_rows_*`, `TGS_POS_Cache::invalidate('global.price'\|'global.pricing')`, `TGS_POS_Price_List::flush_cache()`; thêm `tgs_catalog_version` vào khoá v9 | ⛔ chờ tsm S001-C5 |  |
| P001-T6 | open-pos | Smoke test bộ 3 plugin trên multisite mới: G1–G4 không fatal khi thiếu Viettel / loyalty / tgs-bc-tk / `TTCK_API` (đường tiền mặt); liệt kê fatal còn lại ở thanh toán QR | ☐ · đổi nghĩa: gỡ bridge thì **không fatal**, màn quản trị báo chưa kết nối; POS vẫn bán (I-0) |  |

### PHASE-001 POS bảng theo blog — M3 — Đồng bộ: mã lạ thì kéo

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| P001-EVT | open-pos | `blog_for_branch()` thành vỏ: nhận `blog_id` do bridge (C5) truyền; không quét mọi site | ⛔ chờ bridge B001-C5 · ⚠️ chỉ đổi cách **tìm blog** cho sự kiện vào; cách ghi sổ giữ nguyên; ca đơn React → bản sao trước–sau giống hệt |  |

### PHASE-001 POS bảng theo blog — M5 — POS React cả hai chế độ

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| P001-G | open-pos | Chạy ca golden G2–G4, G7, G9, G14 trên multisite thử (script của tsm S001-G6) | ☐ |  |

### PHASE-001 kết nối theo blog — B0 — tài liệu

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-W0a | open-ketoan-bridge | `docs/CAU-HINH-KET-NOI.md` — bốn trường hợp, ba tầng, K1–K13, T-CFG-1…12 | 🟡 2026-11-21 01:39 PM · PR #1 chờ duyệt |  |
| B001-W0b | open-ketoan-bridge | Bộ hồ sơ phase + khảo sát máy 21/11 | 🟡 2026-11-21 02:20 PM |  |
| B001-DOC | open-ketoan-bridge | `docs/MO-RONG.md:57, 61, 141-155` và `includes/class-tgs-acc-catalog.php:86, 258-262` bỏ "branchCode = mã shop", "tự tạo chi nhánh"; `docs/LUONG-BAN-HANG-SANG-KE-TOAN.md` thêm mục nguồn thứ hai | ☐ (M4) |  |

### PHASE-001 kết nối theo blog — M1 — sửa ngay + cấu hình theo blog

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-FIX1 | open-ketoan-bridge | `require_once` tên file cũ → `open-ketoan-bridge.php` ở `tools/day-ke-toan.php:33`, `doi-chieu-ke-toan.php:36`, `danh-muc-hang.php:41`, `includes/class-tgs-acc-admin.php:106`; cron hint `admin/page-cong-ke-toan.php:277-279` | ☐ |  |
| B001-C1 | open-ketoan-bridge | Tầng cấu hình H → B → M: `key_for`, `key_legacy`, `url_for`, `key_mode`, `current_blog`, `save_blog`, `for_display_blog`; `key()` giữ hành vi cũ | 🟡 2026-11-21 01:52 PM · [PR #2](https://github.com/hoanganh8389/open-ketoan-bridge/pull/2), 8/8 kịch bản · 51 phép kiểm; **chưa chạy trong WordPress thật** |  |

### PHASE-001 kết nối theo blog — M2 — câu hỏi kết nối

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-C2 | open-ketoan-bridge | `TGS_Acc_Api_Client::for_blog($blog)` (WP_Error nếu không có khoá riêng); constructor mặc định = blog hiện tại; `health()` / `ping()` theo blog; nhật ký 60 lượt gọi thêm `blog_id`, xem theo blog | ☐ |  |
| B001-C6 | open-ketoan-bridge | `includes/class-tgs-acc-connection.php`: `tgs_okt_connected()` (4 điều kiện, transient 60 giây, timeout 3 giây, kiểm trùng tenant), `tgs_okt_connection()`, bản đồ tenant → blog (site option `tgs_okt_tenant_map`), hook `tgs_okt_connection_changed`; thay `TGS_Acc_Config::ready()` ở admin :121 / :250, events :76-87, catalog-sync :182, branch / warehouse / supplier `ready()` | ☐ |  |
| B001-C4 | open-ketoan-bridge | Màn Network "Khoá theo shop" (cột: blog, nguồn khoá, khoá che, tenant, trạng thái 🟢🟡⚪🔴, lần kéo) + nút Kiểm tất cả / dòng / Xuất CSV (không khoá); màn Kết nối của site (URL riêng, khoá, Kiểm tra, Xoá); AJAX `tgs_acc_blog_save` / `_check` / `_list`; `shops()` từ blog đã kết nối | ☐ |  |
| B001-T2 | open-ketoan-bridge | `tests/connection-test.php`: 4 điều kiện, transient, trùng tenant, site 0, bridge tắt | ☐ |  |

### PHASE-001 kết nối theo blog — M3 — sự kiện vào theo tenant, gỡ kéo catalog

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-C5 | open-ketoan-bridge | `/ketoan-events`: xác thực → `tenantId` → blog (bản đồ C6) → `switch_to_blog` → mirror; không tìm ra → 404; `/catalog-changed`: xác thực theo tenant (khoá của blog hoặc chữ ký), phát `tgs_okt_catalog_changed($blog, $payload)`, **không kéo**; `/pending`, `/sites`: blog theo tenant của khoá gọi, bỏ `?shops=` và `branchCode` | ⛔ chờ tsm S001-C8 (có người lắng hook) |  |
| B001-C7 | open-ketoan-bridge | Gỡ `includes/class-tgs-acc-catalog-sync.php` (require ở bootstrap :68 / :82), `tools/danh-muc-hang.php`, option `catalog_from_erp` (config :34 / :236-238 / :166-167, admin :390), 5 site option `tgs_acc_catalog_*`, filter `tgs_catalog_readonly` / `tgs_price_edit_locked`; giữ §4 doc 10 làm tham chiếu cho tsm | ⛔ chờ tsm S001-C8 chạy trên site thử · gỡ **cùng lúc** bộ kéo C8 chạy, không để khoảng trống ở bảng POS đọc (ADR-OKT-1 I-0) |  |
| B001-C9 | open-ketoan-bridge | `TGS_Acc_Lists` cache khoá `blog\|kind`, client theo blog; `TGS_Acc_Warehouse_Sync` map theo blog, `sync()` theo khoá blog; `TGS_Acc_Supplier_Sync` **tạm tắt** cho blog không có bảng NCC theo blog (mua hàng ngoài phase) | ☐ |  |

### PHASE-001 kết nối theo blog — M4 — chứng từ theo tenant

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-C3 | open-ketoan-bridge | `TGS_Acc_Pusher::send()` :403, `TGS_Acc_Events::deliver()` :453-457, `day-ke-toan.php:115`, `doi-chieu.php:91`: client theo blog; không khoá riêng → `key_legacy()` kèm nhãn `legacy` trên kết quả / màn hình; không có cả hai → bỏ qua, ghi lý do; `--all` lặp blog | ☐ |  |
| B001-C8 | open-ketoan-bridge | `tgs_acc_push_log(_tax)`: thêm `tenant VARCHAR(64)`, `server_url`; `UNIQUE(tenant, doc_key)`; `find_many` / `keys_in_range` / `search` / `stats` lọc theo tenant; DB_VERSION 4; bỏ cảnh báo admin :401-405 | ☐ |  |
| B001-C10 | open-ketoan-bridge | `includes/class-tgs-acc-source-pos.php`: `sale_rows` / `return_rows` từ `{B}local_ledger` 10 / 11 (đã duyệt, không `pg:`), dòng từ phiếu xuất con loại 2 / phiếu hoàn (khuôn `supplier_doc_items`), không `invoice`; `TGS_Acc_Source::for_blog($blog)` chọn tgs-bc-tk nếu có, không thì POS; thay guard `ready()` ở gate :200, events :426, admin :247, day-ke-toan :109; danh sách shop = blog đã kết nối | 🟡 2026-11-21 08:11 PM — mã + test (tests/source-pos-test.php, 38 phép kiểm đạt); nguồn sổ POS mặc định tắt, bật theo blog; chưa chạy trong WordPress thật | [bridge PR #6](https://github.com/hoanganh8389/open-ketoan-bridge/pull/6) |
| B001-C11 | open-ketoan-bridge | Bỏ `branchCode` chi nhánh (mapper 9 chỗ → chi nhánh mặc định của tenant từ `tgs_okt_connection()`), bỏ `ensure_branch` (pusher :405-424), gỡ `class-tgs-acc-branch-sync.php` + hook bootstrap :80, option `tgs_acc_known_branches(_tax)`, `tgs_acc_branch_sync_last`; chuyển kho / chuyển tiền chéo blog khác tenant → bỏ qua + log (00 §5) | ☐ |  |
| B001-C12 | open-ketoan-bridge | SSO: `tenant` và URL theo blog đang đứng; `sso_tenant` xuống tầng B; `safe_return()` so với `url_for($blog)` | ☐ · ⚠️ chạm vé đăng nhập của POS React (`react-shell.php` đọc `sso_secret()` / `sso_tenant()`): một tenant thì hành vi **giống hệt**; ca đăng nhập React trước–sau (ADR-OKT-1 I-0) |  |
| B001-C13 | open-ketoan-bridge | `TGS_Acc_Trade_Mapper::catalog()` :315-326 đọc `tgs_catalog_table('product', $blog)` | ⛔ chờ tsm S001-C11 |  |
| B001-T4 | open-ketoan-bridge | `tests/source-pos-test.php` (fixture sổ POS → chứng từ, không `invoice`), `tests/push-log-tenant-test.php` | ☐ |  |

### PHASE-001 kết nối theo blog — M5 — vận hành

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| B001-C14 | open-ketoan-bridge | Cron `tgs_acc_events_retry`, `warehouse_sync`: lặp blog, khoá của blog; `--all` bỏ `TGS_BCTK_Vat_Shops` | ☐ |  |
| B001-G | open-ketoan-bridge | Ca golden G5, G6, G8, G10–G13 trên multisite thử (script tsm S001-G6) | ☐ |  |

### PHASE-001 kết nối theo blog — Phía kế toán (theo dõi, làm ở repo open-ketoan theo R-FLOW)

| ID | Repo | Việc | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| S001-K11 | open-ketoan-bridge | Mỗi tenant một kết nối ngược trỏ REST của blog | ☐ |  |
| S001-K10 | open-ketoan-bridge | Cấp tenant cho shop mới | ☐ |  |
| S001-K8 | open-ketoan-bridge | Mã tự tạo từ đơn và mã shop gửi cùng SKU → cùng `item_id` | ☐ |  |

## 2. Đã huỷ / chuyển (giữ để tra)

| ID | Nơi cũ | Lý do |
|---|---|---|
| S001-O2 | PHASE-001 danh mục theo site | ❌ 21/11 — bridge đã vào git, tsm kéo |
| S001-O3 | PHASE-001 danh mục theo site | ❌ 21/11 — khung overlay bỏ |
| S001-W0c | PHASE-001 danh mục theo site | ☐ (phụ chú D13 ở tgs_pos ➡ P001-DOC) |
| S001-C7 | PHASE-001 danh mục theo site | ❌ 21/11 |
| S001-BR4 | PHASE-001 danh mục theo site | ➡ P001-N3 (POS gọi `TGS_Acc_Catalog_Pull::run`) |
| S001-BR6 | PHASE-001 danh mục theo site | ➡ B001-C7 |
| S001-BR7 | PHASE-001 danh mục theo site | ➡ B001-C1 (PR #2), C2, C6, C4 |
| S001-G4 | PHASE-001 danh mục theo site | ➡ B001-C11 + S001-C18 |
| S001-BR1 | PHASE-001 danh mục theo site | ❌ 21/11 |
| S001-G3 | PHASE-001 danh mục theo site | ➡ B001-C10 |
| S001-BR3 | PHASE-001 danh mục theo site | ❌ 21/11 |
| S001-P1 | PHASE-001 danh mục theo site | ➡ P001-T1…T5 |
| S001-P2 | PHASE-001 danh mục theo site | ➡ P001-T3 |
| P001-T5 | PHASE-001 POS bảng theo blog | ❌ **huỷ** 21/11 07:30 PM: đổi hành vi màn bán (I-0). Index do tsm tạo, không sửa `search_products()` / `get_all_products_for_search()` |
| P001-N3 | PHASE-001 POS bảng theo blog | ❌ **huỷ** 21/11 07:30 PM: `class-tgs-pos-order-mapper.php` thuộc danh mục cấm sửa (D002-6). Mapper giữ trả 422; kế toán tự gửi lại; bộ kéo 5 phút đưa mã về |
| P001-P3 | PHASE-001 POS bảng theo blog | ❌ **huỷ** 21/11 07:30 PM: React giữ nguồn danh mục hiện tại (I-0, D002-1) |
