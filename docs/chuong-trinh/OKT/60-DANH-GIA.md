# OKT · 60 — Đánh giá: mục tiêu đạt chưa, tiến độ thật, duyệt PR

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — khung đánh giá chương trình OKT: mục tiêu → tín hiệu đo, tiến độ chỉ tính bằng chứng (ADR I-7), mốc đo theo ngày, tiêu chí duyệt PR. -->

## 1. Mục tiêu → tín hiệu đo

| # | Mục tiêu (chủ, 21/11) | Tín hiệu đạt | Ca ([40](40-CHECKLIST.md)) |
|---|---|---|---|
| G-1 | Luồng bán, logic bán hàng và sổ **giữ nguyên** | census `--check=I0` xanh trên mọi PR; ca bán chuẩn trước–sau mọi mốc giống hệt dòng sổ | S002-16, S002-C14 |
| G-2 | open-ketoan tắt **giữa ca**: vẫn bán, không mất đơn | POS cũ bán được; POS React vào dự phòng; nối lại thì đơn lên đúng tenant, không trùng | S002-C10, C13 |
| G-3 | open-ketoan tắt **trước khi mở ca** / máy mới | admin chuyển shop React → POS cũ và bán ngay | S002-C12 |
| G-4 | **Dừng kết nối** chủ động rồi **nối lại** | tạm dừng: 0 lời gọi ra ngoài, hàng chờ tăng đúng số đơn; nối lại: hàng chờ về 0, không trùng | S002-C11 |
| G-5 | Một blog = một tenant | đơn của blog A chỉ vào tenant A; dán trùng khoá thì cả hai blog báo đỏ | S002-C6, C7; golden G8 |
| G-6 | Nguồn danh mục theo blog (`local` / `ketoan`) | blog `local` sửa được; blog `ketoan` chỉ đọc, kéo về đối chứng lệch 0 | M1, M2 |

**Chương trình đạt mục tiêu** khi G-1…G-6 đều có bằng chứng và pilot (M4) qua.

## 2. Cách tính tiến độ

- **Chỉ tính việc ✅** (có bằng chứng). 🟡 không tính.
- **% tiến độ của một mốc** = số việc ✅ / số việc còn hiệu lực của mốc đó.
- **% chương trình** = trung bình có trọng số của các mốc: Lát dọc 20 · M1 25 · M2 20 · M3 20 · M4 15.
- Không dùng thang tự chấm (như bảng điểm 0–5 của open-pos-backend PHASE-001 doc 29) để báo tiến độ. Thang đó chỉ để nhìn GAP master data, và được đo lại sau lát dọc.

## 3. Mốc đo (ghi mỗi thứ Sáu)

| Ngày | ✅ / còn hiệu lực | Lát dọc | M1 | M2 | M3 | M4 | Chương trình | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| 2026-11-21 | 3 / 158 (đều là việc chủ trả lời / duyệt) | 0 % | 0 % | 0 % | 0 % | 0 % | **0 %** | Mới có tài liệu; bridge PR #2 (B001-C1) đã merge, 🟡 vì chưa chạy trong WordPress thật |

## 4. Tiêu chí duyệt PR

Một PR ở repo làm việc **không đạt** nếu có một trong các điểm sau:
- chạm tệp D002-6 ngoài mẫu D002-7;
- có lời gọi kế toán mới trong đường checkout;
- đổi cột / loại phiếu ghi vào `local_ledger`;
- bí mật trong git;
- thiếu mục "Bất biến chạm tới" và "Kiểm" trong mô tả ([50 §4](50-PHAN-VIEC.md)).

Mỗi phát hiện ghi: mức · mã bất biến · `tệp:dòng` · cách làm đúng.

## 5. GAP đã biết (từ đánh giá 21/11)

Danh sách đủ ở open-pos-backend PHASE-001 doc 31 (32 GAP) và PHASE-002 doc 30 (rà soát theo I-0). Bốn GAP lớn còn mở:

| GAP | Việc |
|---|---|
| Bridge chỉ lấy đơn qua plugin ngoài tgs-bc-tk | S002-4 (= B001-C10) |
| REST danh mục công khai + token demo viết trong mã (open-pos-backend) | việc bảo mật, xem doc 31 C1 / C2 |
| Không có API cấp tenant cho shop | S001-K10 (open-ketoan) |
| GitHub Actions không chạy (tài khoản bị khoá thanh toán) | chủ xử lý |
