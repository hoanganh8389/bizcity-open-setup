# Đóng góp cho Bizcity Open Setup
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — hướng dẫn đóng góp, theo khuôn open-ketoan. -->

Cảm ơn bạn muốn đóng góp. Repo này tạo, khoá, sao lưu và xoá site kế toán của khách. Một lệnh sai có thể chạm vào dữ liệu của doanh nghiệp khác, nên quy trình chặt hơn một dự án web thường.

> **Giấy phép:** đóng góp của bạn được phát hành theo **GPL-2.0-or-later** ([LICENSE](LICENSE)). Mở PR nghĩa là bạn đồng ý điều đó và có quyền đóng góp nội dung ấy. Không đưa mã chép từ nguồn có giấy phép không tương thích, không đưa dữ liệu thật của khách, không đưa bí mật (mật khẩu, khoá, IP nội bộ kèm mật khẩu). Tên app của bạn không dùng tiền tố `bizcity` ([TRADEMARK.md](TRADEMARK.md) §3).

> **Hiện trạng:** giai đoạn 0, mới có tài liệu và script vận hành. Đóng góp lúc này là góp ý tài liệu, luật, hợp đồng Provisioning.

Người mới: đọc [docs/00-CANON.md](docs/00-CANON.md). Agent AI: [AGENTS.md](AGENTS.md).

## Quy trình

1. **Giữ chỗ:** thêm một dòng ở [docs/phases/CLAIMS.md](docs/phases/CLAIMS.md) trước khi làm một đợt việc.
2. **Một PR, một việc nhỏ nhất** có giá trị (*small win*).
3. **Dấu R-SIG** ở chỗ đổi: `[YYYY-MM-DD HH:MM AM/PM <tên người chỉ đạo>] <MÃ> — <mô tả>`. Tên người, không phải tên agent; giờ thật.
4. **Hợp đồng `bizcity_site_provisioning@N`** do repo `open-ketoan` làm chủ. Muốn đổi thì mở PR bên đó trước.
5. **Script `ops/`** phải tự kiểm tham số, chạy lại không gây hại, và chạy `httpd -t` trước mọi lần khởi động lại Apache.

## Báo lỗ hổng

Không mở issue công khai: xem [SECURITY.md](SECURITY.md).
