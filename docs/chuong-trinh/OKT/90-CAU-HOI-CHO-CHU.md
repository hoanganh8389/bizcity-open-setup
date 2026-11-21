# OKT · 90 — Câu hỏi chờ chủ

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — gom câu hỏi đang mở của chương trình OKT về một chỗ. Câu đã chốt giữ ở tài liệu gốc (open-pos-backend PHASE-001 doc 50, PHASE-002 doc 10). -->

<!-- [2026-11-21 08:10 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — Q-OKT-1 chốt: Site Manager không liên quan. -->

Mỗi câu có mặc định tạm, nên việc không bị chặn. Chủ trả lời thì PM ghi ✅ ở đây, rồi sửa thẳng tài liệu liên quan.

| # | Câu hỏi | Gợi ý | Mặc định tạm | Nguồn |
|---|---|---|---|---|
| ~~Q-OKT-1~~ | ~~Mô hình Site Manager của open-setup và luật "một blog = một tenant"~~ | — | ✅ 21/11 08:10 PM: **không liên quan**. Chương trình OKT không dùng Site Manager; R-OKT-CONN-6 giữ nguyên | chủ |
| **Q-OKT-2** | Ai nhận từng lane (BR, TSM, POS, OK, PM)? | — | ⛔ | [50 §1](50-PHAN-VIEC.md) |
| Q002-1 | Shop thật có dùng tgs-bc-tk không; nguồn đơn chính của bridge là sổ POS hay tgs-bc-tk? | 1. Sổ POS là chính | 2 (giữ Q001-15) | open-pos-backend PHASE-002 doc 10 §4 |
| Q002-2 | Một đơn = hai chứng từ (bán + thu) hay gộp vào `sale.payments` (chỉ ở bridge)? | 1. Gộp | 2 trong lát dọc | như trên |
| Q001-19 | Đơn tới trước mã, kế toán đã tự tạo mã trơn: shop có được gửi lần hai để điền đủ không? | 1. Có, khi mã chưa có ĐVT | 1 | open-pos-backend PHASE-001 doc 50 vòng 6 |
| Q001-20 | Một blog = một tenant: blog bán theo bảng giá nào của tenant? | 1. Bảng giá công ty | 1 | như trên |
| Q001-24 | Blog mới tạo mặc định nguồn `local` hay `ketoan`? | 1. `local` | 1 | PHASE-001 doc 50 vòng 8 |
| Q001-25 | Blog `ketoan` đang dự phòng: cho hoàn hàng / thao tác kho không? | Theo I-0: **giữ nguyên** như đang chạy. POS cũ hoàn hàng bình thường (ghi sổ local). Chế độ dự phòng của POS React không hoàn hàng, không thao tác kho (doc 16 §3.2). Gợi ý cũ "cho hoàn hàng ở React" sẽ đổi logic dự phòng, nên bỏ | giữ nguyên | như trên; ADR I-0 |
