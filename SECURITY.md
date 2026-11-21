# Chính sách bảo mật
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — chính sách báo lỗ hổng, theo khuôn open-ketoan. -->

Open Setup tạo, khoá, sao lưu và xoá các site kế toán. Lỗ hổng ở đây có thể làm lộ sổ sách của doanh nghiệp này cho doanh nghiệp khác, hoặc xoá dữ liệu của khách. Xin báo **riêng tư**, đừng mở issue công khai.

*English: please report vulnerabilities privately via GitHub "Report a vulnerability" (Security tab). Do not open public issues.*

## Báo lỗ hổng

1. Vào tab **Security** của repo → **Report a vulnerability**.
2. Ghi rõ:
   - phiên bản hoặc commit;
   - các bước tái hiện;
   - ảnh hưởng: tạo / khoá / xoá được site của người khác? đọc được khoá Provisioning hay khoá API của site? gọi được Provisioning API mà không có khoá? chèn được lệnh vào script vận hành?
3. **Không** gửi dữ liệu thật của khách. **Không** thử trên bản cài của người khác.

## Cam kết

| Việc | Thời hạn |
|---|---|
| Xác nhận đã nhận | ≤ 3 ngày làm việc |
| Đánh giá mức độ | ≤ 7 ngày |
| Vá lỗi **critical** (chạm site của khách khác, lộ khoá, chạy lệnh từ xa, vượt xác thực) | ≤ 7 ngày |
| Vá lỗi **high** | ≤ 30 ngày |
| Công bố (GitHub Security Advisory, ghi công người báo nếu muốn) | sau khi có bản vá |

## Phiên bản được hỗ trợ

Dự án ở giai đoạn 0 (tài liệu và script vận hành, chưa có bản phát hành). Khi có mã, vá áp cho nhánh `main`.

## Trong phạm vi

- app Frappe `bizcity_site_manager` (khi có mã);
- script trong `ops/`;
- cách app giữ và dùng khoá Provisioning.

**Ngoài phạm vi:**
- lỗ hổng của Frappe Framework, của Open Kế Toán (báo ở repo `open-ketoan`), của cPanel / Imunify360;
- cấu hình sai của từng bản cài (lộ cổng CSDL, mật khẩu yếu);
- tấn công từ chối dịch vụ bằng lưu lượng.

Luật liên quan: R-PRIV-1, R-KEY-1, R-DATA-1 ở [docs/00-CANON.md](docs/00-CANON.md).
