# PHASE-002 — Nơi lưu tệp của app: đọc cấu hình R2 của mạng WP đang cài, cấp cho app
<!-- [2026-11-26 11:30 PM Johnny Chu - Chu Hoàng Anh] PHASE-002 — chủ (2026-11-26): "open-setup nên nghiên cứu cách media của WP có R2 theo cấu hình R2 của WP đang setup; nếu là R2 thì không cần quan tâm giữ bao lâu". Cặp với open-cake PHASE-018. -->

> **Trạng thái:** ☐ nghiên cứu (đã có điểm xuất phát §1) · **Cặp với:** [open-cake PHASE-018](https://github.com/hoanganh8389/open-cake/blob/main/docs/phases/PHASE-018-NOI-LUU-TEP/README.md) · **Chuẩn đề xuất:** [open-cake 26-NOI-LUU-TEP](https://github.com/hoanganh8389/open-cake/blob/main/docs/architecture/26-NOI-LUU-TEP.md) (`bizcity_storage@1`, sẽ nộp bizcity-platform)
> **Bốn câu giữ nguyên:** Site Manager không chạm PostgreSQL, không chạm tệp của app; chỉ **cấu hình lúc cài** (biến môi trường) và **gọi Provisioning API**.

## 0. Một câu

Khi cài một app (Cake, Kế Toán…) trên mạng bizcity đã có WordPress dùng R2, open-setup lấy cấu hình R2 **của bản cài WP đó**, cấp cho app một **bucket / tiền tố riêng tư + khoá quyền hẹp** qua biến `STORAGE_*`; từ đó tệp của mỗi site app nằm dưới `<app>/sites/<slug>/…` như media WP nằm dưới `uploads/sites/{blog_id}/…`, và nhân bản site kéo theo tệp bằng chép theo tiền tố.

## 1. Điểm xuất phát đã đọc (2026-11-26)

| # | Ở đâu | Thấy gì |
|---|---|---|
| F-1 | `wp-content/mu-plugins/bizcity-r2.php` | Cấu hình R2 là hằng số trong `wp-config.php`: `BIZCITY_R2_ACCESS_KEY`, `BIZCITY_R2_SECRET_KEY`, `BIZCITY_R2_BUCKET`, `BIZCITY_R2_ENDPOINT`, `BIZCITY_MEDIA_CDN` (+ tuỳ chọn `BIZCITY_R2_DELETE_LOCAL`, `…_CACHE_CONTROL`, `…_SKEW_PAUSE_SEC`, `…_DEBUG`). Khoá R2 soi gương `uploads/`: site con `uploads/sites/{blog_id}/yyyy/mm/tệp`. Media **công khai** qua CDN, cache 1 năm immutable. Lệch giờ ⇒ R2 từ chối, plugin tạm dừng 15 phút |
| F-2 | `wp-content/mu-plugins/bizcity-web/lib/files.php` (`MUCD_Files`) | Nhân bản site WP chép **phía máy chủ R2** `uploads/sites/{nguồn}/` ⇒ `uploads/sites/{mới}/`, chia lượt có thẻ tiếp tục, ưu tiên tệp đang được nội dung tham chiếu, chép dự phòng từ URL CDN khi liệt kê R2 sót; không R2 thì chép thư mục `uploads` |
| F-3 | open-ketoan `core/documents.ts` | Đính kèm chứng từ chỉ lưu đĩa `DATA_DIR/attachments/<tenant_id>/…`, chưa có `sites/<slug>` — ở chế độ nhiều site các site cùng `tenant_id = 1` có thể ghi chung (rủi ro, cần kiểm ở platform) |

## 2. Việc nghiên cứu và chốt

| Mã | Câu hỏi | Đầu ra |
|---|---|---|
| OS-R2-1 | Đọc cấu hình R2 của mạng WP ở đâu, ai được đọc | cách lấy (đọc `wp-config.php` lúc cài, không lưu khoá WP vào Site Manager) + kiểm thiếu hằng số |
| OS-R2-2 | App dùng **chung bucket** media WP hay **bucket riêng** | kiểm tên miền công khai của bucket hiện tại (CDN trỏ cả bucket hay chỉ `uploads/`). Không chắc tiền tố app sẽ không bị CDN phục vụ ⇒ **bucket riêng tư riêng**, cùng tài khoản R2 |
| OS-R2-3 | Khoá cho app | token R2 **quyền hẹp** (chỉ bucket / tiền tố của app, đọc + ghi), không dùng lại khoá của WP; đưa vào `STORAGE_S3_ENDPOINT`, `STORAGE_S3_BUCKET`, `STORAGE_S3_ACCESS_KEY`, `STORAGE_S3_SECRET_KEY`, `STORAGE_DRIVER=s3` |
| OS-R2-4 | Nhân bản site có kèm tệp app không | site cấp từ mẫu ⇒ app chép tiền tố tệp mẫu (`copyPrefix`, như F-2) trong bước cấp site; site trắng ⇒ không chép. Site Manager chỉ truyền ý định qua Provisioning API, không tự chép |
| OS-R2-5 | Giờ máy chủ | bước cài kiểm NTP của VPS (R2 từ chối chữ ký khi lệch giờ — F-1) |
| OS-R2-6 | Hiện ở Site Manager | trạng thái bộ lưu của từng app (`local` / `s3`, lần tự kiểm cuối, dung lượng) đọc từ API chẩn đoán của app; **không** hiện khoá |
| OS-R2-7 | Hạn giữ | R2 ⇒ **app không đặt hạn** (chủ chốt 2026-11-26); cần dọn thì đặt luật vòng đời ở bucket, ngoài app |

## 3. Xong khi

Tài liệu §2 có câu trả lời đã kiểm trên VPS thật (bucket, tên miền công khai, token quyền hẹp thử được ghi / đọc / bị chặn ngoài tiền tố); `ops/` có bước sinh biến `STORAGE_*` cho app từ cấu hình WP; Site Manager hiện trạng thái bộ lưu từng app.

## Nhật ký

- 2026-11-26: mở phase (nghiên cứu), điểm xuất phát §1 đọc từ mã đang chạy; chủ chốt R2 không đặt hạn giữ.
