# OKT · 90 — Câu hỏi chờ chủ

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — gom câu hỏi đang mở của chương trình OKT về một chỗ. Câu đã chốt giữ ở tài liệu gốc (open-pos-backend PHASE-001 doc 50, PHASE-002 doc 10). -->

<!-- [2026-11-22 09:30 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ duyệt gợi ý cho mọi câu mở ("ok"): Q-OKT-2, Q002-1, Q002-2, Q001-16…20, 24, 25. Sinh việc S002-17, S002-18, S001-C8b, S001-C8c. -->

<!-- [2026-11-21 08:10 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — Q-OKT-1 chốt: Site Manager không liên quan. -->

Mỗi câu có mặc định tạm, nên việc không bị chặn. Chủ trả lời thì PM ghi ✅ ở đây, rồi sửa thẳng tài liệu liên quan.

| # | Câu hỏi | Gợi ý | Mặc định tạm | Nguồn |
|---|---|---|---|---|
| ~~Q-OKT-1~~ | ~~Mô hình Site Manager của open-setup và luật "một blog = một tenant"~~ | — | ✅ 21/11 08:10 PM: **không liên quan**. Chương trình OKT không dùng Site Manager; R-OKT-CONN-6 giữ nguyên | chủ |
| ~~Q-OKT-2~~ | ~~Ai nhận từng lane (BR, TSM, POS, OK, PM)?~~ | — | ✅ 22/11 09:30 AM theo gợi ý: PM = chủ; OK = Nguyễn Văn Thủy; POS = Võ Hoàng; BR, TSM = Claude Code theo từng PR, chủ duyệt. **Chờ hai người xác nhận nhận lane** | [50 §1](50-PHAN-VIEC.md) |
| ~~Q002-1~~ | ~~Shop thật có dùng tgs-bc-tk không; nguồn đơn chính của bridge là sổ POS hay tgs-bc-tk?~~ | — | ✅ 22/11 09:30 AM: **sổ POS là nguồn chính cho shop mới** (`tgs_acc_sale_source = pos` theo blog). Shop đang gửi bằng tgs-bc-tk **giữ** tới khi so khoá chứng từ hai nguồn trên một shop thật (S002-18). Có hoá đơn Viettel thì giữ tgs-bc-tk để đối chiếu số hoá đơn | open-pos-backend PHASE-002 doc 10 §4 |
| ~~Q002-2~~ | ~~Một đơn = hai chứng từ hay gộp vào `sale.payments`?~~ | — | ✅ 22/11 09:30 AM: **gộp** (một đơn một chứng từ, kế toán ghi bút toán thu trong cùng chứng từ, `sale.rule.ts:80`). Lát dọc giữ hai chứng từ; gộp làm ngay sau (S002-17), mã phương thức từ bảng ánh xạ lưu sẵn (I-4), chênh làm tròn theo Q002-3 | như trên |
| ~~Q001-19~~ | ~~Đơn tới trước mã, kế toán đã tự tạo mã trơn: shop có được gửi lần hai để điền đủ không?~~ | — | ✅ 22/11 09:30 AM: **có**, chỉ khi mã ở kế toán chưa có ĐVT; chỉ điền ô trống, không ghi đè tên / giá / thuế; có nhật ký. Bộ kéo không ghi rỗng đè barcode (S001-C8b); xin feed mang `sourceSystem` (S001-K12) | open-pos-backend PHASE-001 doc 50 vòng 6 |
| ~~Q001-20~~ | ~~Một blog = một tenant: blog bán theo bảng giá nào của tenant?~~ | — | ✅ 22/11 09:30 AM: bảng giá **gán cho chi nhánh khai theo blog** (`tgs_acc_branch_code`); không có gán → **bảng giá công ty**; DM14 áp ở bộ kéo (D002-8); bỏ dò `wp_blogs.tgs_site_code` (S001-C8c) | như trên |
| ~~Q001-24~~ | ~~Blog mới tạo mặc định nguồn `local` hay `ketoan`?~~ | — | ✅ 22/11 09:30 AM: **`local`**. 92 blog đang chạy chuyển `ketoan` chủ động theo ADR §5.3 | PHASE-001 doc 50 vòng 8 |
| ~~Q001-25~~ | ~~Blog `ketoan` đang dự phòng: cho hoàn hàng / thao tác kho không?~~ | — | ✅ 22/11 09:30 AM: **giữ nguyên** như đang chạy (I-0): POS cũ hoàn hàng bình thường; dự phòng của POS React không hoàn hàng, không thao tác kho | như trên; ADR I-0 |
| ~~Q001-16~~ | ~~Blog `ketoan`: mã shop vừa tạo có bán trước khi về lại từ kế toán không?~~ | — | ✅ 22/11 09:30 AM: **không**, về rồi mới bán (≤ 1 phút sự kiện, ≤ 5 phút cron); làm ở tầng dữ liệu, POS không thêm lọc (I-0) | PHASE-001 doc 50 vòng 5 |
| ~~Q001-17~~ | ~~Thứ tự xây smallwin?~~ | — | ✅ 22/11 09:30 AM: **SW1 → SW3 → SW4 → SW2** (SW3 phần lớn đã xong ở PHASE-002) | như trên |
| ~~Q001-18~~ | ~~Bảng sản phẩm của blog: bảng mới hay dùng lại `local_product_name`?~~ | — | ✅ 22/11 09:30 AM: **bảng mới** `{prefix}tgs_catalog_product` cùng cột bảng global — cách duy nhất khớp D002-7 (chỉ đổi tên bảng trong tệp đường bán) | như trên |
