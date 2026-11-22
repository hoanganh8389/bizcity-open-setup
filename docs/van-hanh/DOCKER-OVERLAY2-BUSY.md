# Docker báo `overlay2 … device or resource busy` trên VPS
<!-- [2026-11-22 11:55 PM Johnny Chu - Chu Hoàng Anh] OPS-VPS — nguyên nhân + lệnh gỡ an toàn; script ops/vps/go-container.sh -->

> **Máy:** VPS cPanel `157.10.53.169` (zalo-hub, Open Kế Toán `/opt/ketoan`, Frappe `/opt/frappe-gitops`). Lỗi này đã gặp ở **mọi** lần thay container (zalo-hub 5/5, Frappe, Open Kế Toán — 2026-09 → 2026-11).

## 1. Nguyên nhân (đã bắt được 2026-11-22)

Docker gỡ container thì phải bỏ mount lớp overlay (`/var/lib/docker/overlay2/<lớp>/merged`). Trên máy cPanel / Imunify, một số tiến trình chạy trong **mount namespace riêng** (PHP của người dùng trong CageFS, con của Apache…). Namespace đó **sao chép mọi mount lúc nó được tạo** — kể cả lớp overlay của container đang chạy — và giữ lại. Docker bỏ mount ở máy thì được, nhưng bản sao trong namespace kia vẫn còn → `unlinkat … merged: device or resource busy`, container kẹt `Dead` / `Removal In Progress`.

Bằng chứng: khi lỗi, `grep <lớp> /proc/*/mountinfo` thấy hơn 500 tiến trình; lọc bỏ namespace của máy (PID 1) chỉ còn `httpd <defunct>` và các tiến trình sống rất ngắn. **Chỉ `restartsrv_httpd` là chưa đủ** (đã thử) — namespace của CageFS sống qua lần khởi động lại Apache.

Reboot luôn chữa được, nhưng sau reboot container `restart: unless-stopped` lên trước, Apache / PHP lên sau và **sao chép lại** — lần thay container kế tiếp lại kẹt.

## 2. Gỡ container đang kẹt — `ops/vps/go-container.sh`

```bash
cd /opt/open-setup && git pull
bash ops/vps/go-container.sh chan-doan ketoan-api-1     # chỉ đọc: namespace + tiến trình nào giữ; máy có CageFS không
bash ops/vps/go-container.sh go ketoan-api-1            # dừng + gỡ; bận thì giải phóng mount rồi thử lại
bash ops/vps/go-container.sh du-an ketoan               # mọi container của một project compose (ketoan / erp / zalo-hub)
```

`go` làm theo thứ tự, sau mỗi bước thử gỡ lại, gỡ được thì dừng:

1. `docker stop -t 20` → `docker rm -f`
2. `cagefsctl --remount-all` (chỉ khi máy có CageFS) — làm mới namespace của mọi người dùng
3. `/scripts/restartsrv_httpd`
4. `/scripts/restartsrv_apache_php_fpm`
5. Vẫn bận → in namespace / tiến trình còn giữ, **dừng** (mã 2). Gửi đoạn in ra cho người vận hành; cách cuối là reboot.

Script **không** restart Docker, **không** sửa `/var/lib/docker`, **không** kill tiến trình, **không** xoá volume. Nhật ký: `/var/log/bizcity-docker-go.log`. Bước 2–4 làm website nháy 1–2 giây.

## 3. Thay container (cập nhật một project) — trình tự

Thay vì `docker compose up -d` trực tiếp (Compose đổi tên container cũ rồi kẹt giữa chừng):

```bash
# Open Kế Toán
bash /opt/open-setup/ops/vps/go-container.sh du-an ketoan && (cd /opt/ketoan && docker compose up -d)

# Frappe (Site Manager) — image chỉ có trên máy
bash /opt/open-setup/ops/vps/go-container.sh du-an erp && docker compose -p erp -f /opt/frappe-gitops/erp.yaml up -d --pull never

# zalo-hub — theo runbook zalo-hub (thư mục /home/vibeyeuc/zalo-hub)
bash /opt/open-setup/ops/vps/go-container.sh du-an zalo-hub && (cd /home/vibeyeuc/zalo-hub && docker compose up -d --no-build zalo-hub)
```

Volume (dữ liệu Postgres, MariaDB, `sites` của Frappe, `zalo_hub_data`) không bị đụng — chỉ container bị gỡ.

## 4. Việc còn mở (sửa tận gốc)

- Xác nhận CageFS: `cagefsctl --cagefs-status`. Nếu bật: thử thêm `/var/lib/docker` vào danh sách loại trừ mount của CageFS (`/etc/cagefs/cagefs.mp`, dòng `!/var/lib/docker`) rồi `cagefsctl --remount-all` — để namespace người dùng không còn sao chép mount của Docker.
- `systemctl show httpd -p PrivateTmp -p ProtectSystem -p MountFlags` — nếu `PrivateTmp=yes`, cân nhắc drop-in `MountFlags=slave` cho httpd.
- Ghi kết quả vào đây khi làm.
