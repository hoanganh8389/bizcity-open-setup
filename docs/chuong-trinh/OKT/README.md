# Chương trình OKT — open-pos ⇄ open-ketoan: trục điều phối

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ giao open-setup làm trục điều phối chương trình OKT: canon từng phase, roadmap, checklist (nguồn trạng thái duy nhất), phân việc, đánh giá việc. open-setup vẫn giữ vai Site Manager (PHASE-001 của repo này). -->

<!-- [2026-11-21 08:10 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ: open-setup nắm giữ phase điều phối này; mô hình Site Manager không liên quan tới chương trình OKT. -->

**open-setup nắm giữ phase này** để điều phối mọi việc của chương trình. Ràng buộc gốc: luồng bán hàng, logic bán hàng và sổ của open-pos **giữ nguyên**; phần bổ sung chỉ để open-pos linh hoạt, chủ động hơn khi open-ketoan không hoạt động hoặc dừng kết nối.

**Mục tiêu của chương trình (chủ, 21/11):**
- open-pos **tự xoay xở được khi open-ketoan tắt hoặc dừng kết nối**;
- **luồng bán, logic bán hàng và sổ của open-pos giữ nguyên**;
- mỗi blog là một shop, ứng với một tenant kế toán;
- admin chọn nguồn danh mục cho từng blog (`local` / `ketoan`).

**Vai trò của open-setup trong chương trình:**
- giữ **canon từng phase**: ADR, bất biến, quyết định;
- giữ **roadmap**;
- giữ **checklist**, là nguồn trạng thái duy nhất;
- **phân việc** và **đánh giá việc**.

Mã nằm ở các repo làm việc. Repo này không chứa mã của open-pos.

## Năm repo

| Repo | Vai trong chương trình | Tài liệu kỹ thuật (research, thiết kế, bằng chứng) |
|---|---|---|
| **open-setup** (repo này, `bizcity-open-setup`) | **nắm giữ phase điều phối này**: canon, roadmap, checklist, phân việc, đánh giá. Không có mã của chương trình; vai Site Manager của repo **không liên quan** tới OKT | `docs/chuong-trinh/OKT/` |
| [open-pos](https://github.com/hoanganh8389/open-pos) (trước `tgs_pos`) | máy bán: POS cũ + POS React. **Đường bán và sổ giữ nguyên** (I-0) | `docs/phases/PHASE-001-POS-BANG-THEO-BLOG/` |
| [open-pos-backend](https://github.com/hoanganh8389/open-pos-backend) (trước `tgs_shop_management`) | quản trị danh mục / giá / thuế, bộ kéo catalog, công cụ | `docs/phases/PHASE-001-…`, `PHASE-002-LAT-DOC-MOT-DON-BAN/` |
| [open-ketoan-bridge](https://github.com/hoanganh8389/open-ketoan-bridge) | kết nối theo blog, đọc sổ POS, dựng và gửi chứng từ, tạm dừng / gửi bù | `docs/phases/PHASE-001-KET-NOI-THEO-BLOG/` |
| [open-ketoan](https://github.com/hoanganh8389/open-ketoan) | kế toán; **chủ luật** R-OKT-CONN (CANON) và hợp đồng API | `docs/rules/RULE-OPEN-POS-CONNECTION.md` |

## Đọc theo thứ tự

| Tệp | Nội dung |
|---|---|
| [00-ADR-OKT-1](00-ADR-OKT-1.md) | **Canon chương trình:** tám bất biến I-0…I-7 (I-0 giữ nguyên đường bán), quyết định D002-1…8, danh mục tệp cấm sửa |
| [10-ROADMAP](10-ROADMAP.md) | Các phase và mốc, đường găng, hạn cứng, phụ thuộc giữa repo |
| [40-CHECKLIST](40-CHECKLIST.md) | **Nguồn trạng thái duy nhất** của 158 việc (S002, S001, SW, P001, B001, K) |
| [50-PHAN-VIEC](50-PHAN-VIEC.md) | Lane, người nhận, luật nhận việc, định nghĩa xong, mẫu mô tả PR |
| [60-DANH-GIA](60-DANH-GIA.md) | Mục tiêu → tín hiệu đo; cách tính tiến độ (chỉ có bằng chứng); mốc đo theo ngày; tiêu chí duyệt PR |
| [70-SCOREBOARD-KET-NOI](70-SCOREBOARD-KET-NOI.md) | Điểm kết nối open-pos → open-pos-backend → open-ketoan: 14 miền, 46 tiêu chí, 28 tình huống ánh xạ; 44,6 % / pilot 72,5 % (22/11 02:55 PM) |
| [75-LUAT-TU-KIEM](75-LUAT-TU-KIEM.md) | **Luật tối thượng I-8**: tự kiểm theo cặp blog → tenant qua API, SC-0…SC-12, khi chạy, đỏ thì làm gì |
| [mockups/](mockups/README.md) | Mockup 3 màn: scoreboard, tự kiểm blog → tenant, trace dòng chảy hai chiều ([canvas](https://claude.ai/artifact/NSxgh5KUvmP5cq8gcGCDhu)) |
| [90-CAU-HOI-CHO-CHU](90-CAU-HOI-CHO-CHU.md) | Câu hỏi đang mở của cả chương trình |

**Thứ tự ưu tiên khi tài liệu mâu thuẫn:**
1. CANON R-OKT-CONN ở open-ketoan.
2. [00-ADR-OKT-1](00-ADR-OKT-1.md).
3. Các tệp khác ở đây.
4. Tài liệu phase ở từng repo.

## Cách làm việc

1. **Nhận việc:** chọn việc ☐ ở [40](40-CHECKLIST.md), giữ chỗ theo R-FLOW **ở repo làm việc**. Ghi tên người nhận vào [50](50-PHAN-VIEC.md).
2. **Làm:** một việc một PR ở repo làm việc. Mô tả PR theo mẫu ở [50 §4](50-PHAN-VIEC.md).
3. **Đổi trạng thái:** một commit ở **repo này**, đổi ô trạng thái và bằng chứng ở [40](40-CHECKLIST.md), kèm dấu R-SIG. Không cập nhật trạng thái ở repo làm việc.
4. **Đánh giá:** mỗi thứ Sáu ghi một dòng mốc đo ở [60 §3](60-DANH-GIA.md).
