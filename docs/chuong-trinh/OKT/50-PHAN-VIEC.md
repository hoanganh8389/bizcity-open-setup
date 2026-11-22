# OKT · 50 — Phân việc

<!-- [2026-11-22 09:30 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ duyệt gợi ý cho mọi câu mở ("ok"): Q-OKT-2, Q002-1, Q002-2, Q001-16…20, 24, 25. Sinh việc S002-17, S002-18, S001-C8b, S001-C8c. -->

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — lane, người nhận, luật nhận việc, định nghĩa xong, mẫu mô tả PR cho chương trình OKT. -->

## 1. Lane

| Lane | Repo | Phạm vi | Không được đụng | Người nhận |
|---|---|---|---|---|
| **BR** | open-ketoan-bridge | kết nối theo blog, nguồn sổ POS (chỉ đọc), dựng / gửi chứng từ, tạm dừng / gửi bù, trạng thái, lệnh `wp tgs-acc` | ghi vào sổ POS | Claude Code theo từng PR, chủ duyệt (Q-OKT-2) |
| **TSM** | open-pos-backend | quản trị danh mục / giá / thuế, bảng theo prefix, bộ kéo C8, seed, census | đường bán (ADR D002-6) | Claude Code theo từng PR, chủ duyệt (Q-OKT-2) |
| **POS** | open-pos | **chỉ** đổi tên bảng theo D002-7, script dựng môi trường thử, màn quản trị chuyển máy bán | mọi logic bán / sổ (I-0) | Võ Hoàng — chờ xác nhận (Q-OKT-2) |
| **OK** | open-ketoan | việc S001-K* theo R-FLOW của repo đó (giữ chỗ trong `docs/phases/CLAIMS.md` bên đó) | — | Nguyễn Văn Thủy — chờ xác nhận (Q-OKT-2) |
| **PM** | open-setup (nắm giữ phase này) | trục điều phối: cập nhật [40](40-CHECKLIST.md), mốc đo [60](60-DANH-GIA.md), [90](90-CAU-HOI-CHO-CHU.md) | — | chủ dự án (Q-OKT-2) |

## 2. Luật nhận việc

1. Chỉ nhận việc ☐ trong [40](40-CHECKLIST.md) mà mọi việc phụ thuộc đã ✅ hoặc 🟡.
2. Giữ chỗ R-FLOW ở repo làm việc **trước** dòng mã đầu tiên.
3. Việc chạm tệp trong danh mục cấm sửa (ADR D002-6) chỉ được nhận nếu đúng mẫu "chỉ đổi tên bảng" (D002-7). Khi đó PR phải có ca bán chuẩn trước–sau.
4. Một việc = một PR nhỏ, merge độc lập.

## 3. Định nghĩa xong (✅)

- Mã đã merge vào `main` của repo làm việc.
- Có test chạy được bằng một lệnh, hoặc ca chạy thật có bản ghi trong `evidence/` của phase ở repo đó (lệnh, đầu ra, người chạy, giờ).
- Nếu chạm D002-6: có ca bán chuẩn trước–sau giống hệt dòng sổ.
- Ô Bằng chứng ở [40](40-CHECKLIST.md) có đường dẫn.

## 4. Mẫu mô tả PR ở repo làm việc

```
## Việc
<mã việc ở open-setup OKT/40>, <một câu>

## Bất biến chạm tới
I-… (ADR-OKT-1) — kiểm bằng …

## I-0 (đường bán)
☐ không chạm tệp D002-6
☐ có chạm, đúng mẫu D002-7 — ca bán chuẩn: <link evidence>

## Kiểm
<lệnh test / ca chạy + kết quả>
```
