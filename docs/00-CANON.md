# CANON — Chỉ mục luật Bizcity Open Setup
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] INIT — khởi tạo chỉ mục luật Open Setup. -->

> **Phiên bản:** 0.1 · 2026-11-21 · **Trạng thái:** Đề xuất, chưa có mã cổng · **Người giữ:** chủ dự án
> **Cùng hệ quy ước** với CANON của open-ketoan / open-kiot: cấp luật Tier 0/1/2, phase `PHASE-NNN-*`, dấu R-SIG, bảng giữ chỗ R-FLOW.

## 0. Tôn chỉ

**Ai cũng tự tạo được phần mềm kế toán của mình trong vài phút, và dữ liệu của doanh nghiệp này không bao giờ chạm tới doanh nghiệp khác.**

## 1. Bốn câu không thương lượng

1. **Cổng web không có quyền root.** Cổng chạy bằng user `opensetup`. Việc cần root chỉ đi qua **một** script được phép trong sudoers. Script đó tự kiểm lại mọi tham số và không tin cổng (R-PRIV-1).
2. **Mỗi doanh nghiệp một site, một CSDL.** Không có bảng dùng chung giữa các doanh nghiệp. Mật khẩu root CSDL chỉ script root đọc được; cổng không bao giờ thấy (R-TENANT-1).
3. **Không xoá dữ liệu của khách mà không sao lưu trước.** Hết hạn thì khoá chỉ đọc. Xoá chỉ chạy sau khi có bản sao lưu đã kiểm (R-DATA-1).
4. **Việc tạo site chạy từng việc một, có nhật ký từng bước.** Bước nào hỏng thì dừng, ghi rõ hỏng ở đâu, báo người dùng bằng câu dễ hiểu, và dọn phần đã tạo dở (R-JOB-1).

## 2. Danh mục luật

| Mã | Cấp | Một câu | Kiểm bằng |
|---|---|---|---|
| R-PRIV-1 | 0 | Cổng không root; sudo chỉ một script; script kiểm `slug` bằng regex và danh sách cấm | đọc `/etc/sudoers.d/opensetup`; ca thử tham số độc (`; rm`, `../`, chữ hoa) phải bị từ chối |
| R-TENANT-1 | 0 | Một site một CSDL; bí mật CSDL chỉ root đọc | `stat` quyền `custom.env` = 600 root |
| R-DATA-1 | 0 | Khoá trước, sao lưu trước, xoá sau | nhật ký việc `drop` phải có dòng `backup ok` trước nó |
| R-JOB-1 | 1 | Hàng đợi tuần tự, nhật ký từng bước, dọn khi lỗi | ca thử: giết giữa chừng → không còn site / subdomain mồ côi |
| R-SLUG-1 | 1 | `^[a-z][a-z0-9-]{2,29}$`, không kết thúc bằng `-`, không trùng danh sách cấm hoặc subdomain đang có trong cPanel | unit test bộ kiểm slug |
| R-ABUSE-1 | 1 | Một email đã xác nhận và một số điện thoại chỉ tạo được 1 site dùng thử; mỗi IP tối đa 3 lượt/ngày; tổng số site có trần | unit test + đếm trong CSDL cổng |
| R-SIG | 2 | Mọi thay đổi tài liệu có dòng `<!-- [giờ thật Johnny Chu - Chu Hoàng Anh] MÃ — việc -->` | người duyệt nhắc |

## 3. Đổi X thì sửa Y (cùng một PR)

| Đổi | Phải sửa cùng |
|---|---|
| Cổng hoặc tên miền gốc của bộ máy | `ops/*.sh`, [CAI-FRAPPE-TREN-VPS](van-hanh/CAI-FRAPPE-TREN-VPS.md), README sơ đồ |
| Bước trong script tạo site | bảng bước ở PHASE-001 §4, thông điệp tiến trình trên cổng |
| Luật chống lạm dụng / hạn dùng thử | PHASE-001 §6, điều khoản trên form |
