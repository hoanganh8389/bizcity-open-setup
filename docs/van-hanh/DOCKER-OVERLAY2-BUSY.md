# Docker báo `overlay2 … device or resource busy` trên VPS
<!-- [2026-11-22 11:55 PM Johnny Chu - Chu Hoàng Anh] OPS-VPS — nguyên nhân + lệnh gỡ an toàn; script ops/vps/go-container.sh -->

> **Máy:** VPS cPanel `157.10.53.169` (zalo-hub, Open Kế Toán `/opt/ketoan`, Frappe `/opt/frappe-gitops`). Lỗi này đã gặp ở **mọi** lần thay container (zalo-hub 5/5, Frappe, Open Kế Toán — 2026-09 → 2026-11).

## 1. Nguyên nhân (đã bắt được 2026-11-22)

Docker gỡ container thì phải bỏ mount lớp overlay (`/var/lib/docker/overlay2/<lớp>/merged`). Trên máy cPanel / Imunify, một số tiến trình chạy trong **mount namespace riêng** (PHP của người dùng trong CageFS, con của Apache…). Namespace đó **sao chép mọi mount lúc nó được tạo** — kể cả lớp overlay của container đang chạy — và giữ lại. Docker bỏ mount ở máy thì được, nhưng bản sao trong namespace kia vẫn còn → `unlinkat … merged: device or resource busy`, container kẹt `Dead` / `Removal In Progress`.

Bằng chứng: khi lỗi, `grep <lớp> /proc/*/mountinfo` thấy hơn 500 tiến trình; lọc bỏ namespace của máy (PID 1) chỉ còn `httpd <defunct>` và các tiến trình sống rất ngắn. **Chỉ `restartsrv_httpd` là chưa đủ** (đã thử) — namespace của CageFS sống qua lần khởi động lại Apache.

**Lần chạy thật 2026-11-22 23:xx <!-- [2026-11-23 12:20 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — v2 sau lần chạy thật -->:** máy **không có CageFS**; sau khi restart httpd + php-fpm thì **không namespace nào khác còn giữ** — mà `docker rm` vẫn bận: `merged` vẫn là mount ở **chính namespace của máy** (Docker không bỏ được mount khi container chết; có thể còn tiến trình mồ côi của container dùng nó). Bản v2 của script xử lý thêm trường hợp này.

Reboot luôn chữa được, nhưng sau reboot container `restart: unless-stopped` lên trước, Apache / PHP lên sau và **sao chép lại** — lần thay container kế tiếp lại kẹt.

## 2. Gỡ container đang kẹt — `ops/vps/go-container.sh`

```bash
cd /opt/open-setup && git pull
bash ops/vps/go-container.sh chan-doan ketoan-api-1     # chỉ đọc: namespace + tiến trình nào giữ; máy có CageFS không
bash ops/vps/go-container.sh go ketoan-api-1            # dừng + gỡ; bận thì giải phóng mount rồi thử lại
bash ops/vps/go-container.sh du-an ketoan               # mọi container của một project compose (ketoan / erp / zalo-hub)
```

`go` làm theo thứ tự, sau mỗi bước thử gỡ lại, gỡ được thì dừng <!-- [2026-11-23 12:20 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — v2 sau lần chạy thật -->:

1. `docker stop -t 20` → `docker rm -f`
2. `merged` còn mount ở máy **và không tiến trình nào dùng** → `umount` (web không nháy)
3. `cagefsctl --remount-all` (chỉ khi máy có CageFS)
4. `/scripts/restartsrv_httpd`, rồi `/scripts/restartsrv_apache_php_fpm` — **chỉ khi** có namespace khác đang giữ lớp đó
5. `umount -l` (bỏ mount kiểu lười)
6. Còn tiến trình mồ côi của container (root / cwd nằm trong `merged`): **in ra, không đụng** — chạy lại với `--kill-orphans` thì gửi TERM, đợi 10 giây, KILL, rồi bỏ mount
7. Vẫn bận → in tình trạng (mount ở máy, tiến trình dùng, `fuser -m`, namespace khác), **dừng** (mã 2). Cách cuối là reboot.

```bash
bash ops/vps/go-container.sh go --kill-orphans ketoan-api-1     # chỉ khi bước 6 in ra tiến trình của chính container đó (vd node của api)
```

Script **không** restart Docker, **không** xoá gì trong `/var/lib/docker`, **không** xoá volume, **không** kill tiến trình nào ngoài tiến trình mồ côi của container đã chết (và chỉ khi có `--kill-orphans`). Nhật ký: `/var/log/bizcity-docker-go.log`. Bước 2–4 làm website nháy 1–2 giây.

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
