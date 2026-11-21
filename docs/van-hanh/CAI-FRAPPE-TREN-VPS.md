# Cài Frappe/ERPNext trên VPS cPanel (nhiều site kế toán)
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] OPS-1 — ghi lại cài đặt đã chạy thật trên VPS 157.10.53.169 ngày 2026-11-21. -->

> **Máy:** VPS cPanel `157.10.53.169`, tài khoản cPanel `vibeyeuc`. Máy này **dùng chung** với zalo-hub (Docker) và WordPress multisite.
> **Cấm:** `systemctl restart docker` (zalo-hub đang chạy). `docker compose up` cho project khác `erp` cũng phải cẩn thận vì lỗi `overlay2 busy`.

## 1. Hiện trạng đã cài

| Thứ | Giá trị |
|---|---|
| Mã nguồn | `/opt/frappe` (clone `frappe/frappe_docker`) |
| Biến môi trường | `/opt/frappe/custom.env`: `ERPNEXT_VERSION=v15.125.0`, `DB_PASSWORD=…`, `HTTP_PUBLISH_PORT=127.0.0.1:8090`. **Phải `chmod 600`** |
| Compose đã gộp | `/opt/frappe-gitops/erp.yaml`, project `-p erp` |
| Container | backend, frontend, websocket, scheduler, queue-short, queue-long, redis-cache, redis-queue, db (`mariadb:11.8`, sẽ đổi sang 10.6 theo D001-10) |
| Cổng | frontend `127.0.0.1:8090 → 8080`, chỉ mở trong máy |
| Site | `erp.btnet.vn` (site thử) |
| Mật khẩu Administrator | `/root/frappe-sites.txt` |

## 2. Cài từ đầu

```bash
cd /opt && git clone https://github.com/frappe/frappe_docker.git frappe && cd frappe
\cp -f example.env custom.env          # \cp: bỏ qua alias cp -i của root

VER=$(git ls-remote --tags https://github.com/frappe/erpnext | grep -oE 'v15\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
PASS=$(openssl rand -hex 16)
sed -i '/^ERPNEXT_VERSION=/d;/^DB_PASSWORD=/d;/^HTTP_PUBLISH_PORT=/d' custom.env
cat >> custom.env <<EOF
ERPNEXT_VERSION=$VER
DB_PASSWORD=$PASS
HTTP_PUBLISH_PORT=127.0.0.1:8090
EOF
chmod 600 custom.env

mkdir -p /opt/frappe-gitops
docker compose --env-file custom.env -p erp \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > /opt/frappe-gitops/erp.yaml

docker compose -p erp -f /opt/frappe-gitops/erp.yaml up -d
docker compose -p erp -f /opt/frappe-gitops/erp.yaml ps   # configurator = Exited(0) là đúng
```

Bài học: **không gõ từng dòng cấu hình vào shell**. Các dòng `KEY=value` phải nằm trong `custom.env`. Dấu `<…>` trong ví dụ sẽ làm bash báo lỗi cú pháp.

## 3. Tạo một site kế toán

```bash
/opt/frappe-gitops/new-tenant.sh <slug> btnet.vn
```

Script ở [ops/new-tenant.sh](../../ops/new-tenant.sh) làm 3 việc: tạo site + cài ERPNext (3–5 phút), tạo subdomain cPanel bằng `uapi`, ghi proxy Apache. Đăng nhập bằng `Administrator` và mật khẩu script in ra; mật khẩu cũng được lưu ở `/root/frappe-sites.txt`.

Đặt lại mật khẩu:
```bash
docker compose -p erp -f /opt/frappe-gitops/erp.yaml exec backend bench --site <site> set-admin-password '<mật khẩu mới>'
```

Tạo subdomain bằng tay trên cPanel (nếu không dùng script): **Domains → Create A New Domain** → nhập `<slug>.btnet.vn` → **bỏ tick "Share document root"** → Document Root `frappe-placeholder` → Submit. Sau đó vẫn phải ghi proxy như bước [3/3] của script.

## 4. Vận hành

| Việc | Lệnh (với `DC="docker compose -p erp -f /opt/frappe-gitops/erp.yaml"`) |
|---|---|
| Danh sách site | `$DC exec backend ls sites` |
| Sao lưu một site | `$DC exec backend bench --site <site> backup --with-files` |
| Sao lưu tất cả | `$DC exec backend bench --site all backup --with-files` |
| Nâng cấp | đổi `ERPNEXT_VERSION` → tạo lại `erp.yaml` → `$DC up -d` → `$DC exec backend bench --site all migrate` |
| Khoá chỉ đọc | `$DC exec backend bench --site <site> set-config allow_reads_during_maintenance 1` rồi `set-maintenance-mode on` |
| Xoá site | `bench drop-site <site> --db-root-password …` rồi xoá subdomain cPanel và 2 thư mục `userdata/{std,ssl}/2_4/vibeyeuc/<site>` |

## 5. Bảo mật máy

- Nhật ký đăng nhập ngày 2026-11-21 có **12 lần đăng nhập root thất bại** (có người dò mật khẩu). Cần bật cPHulk trong WHM, chuyển sang SSH key và tắt đăng nhập root bằng mật khẩu.
- `custom.env` và `/root/frappe-sites.txt`: `chmod 600`.
- Mật khẩu DB root đã lộ trong ảnh chụp màn hình khi cài. Đổi mật khẩu này khi làm W0-2 (tạo lại CSDL bằng MariaDB 10.6).

## 6. Sửa 502

Triệu chứng (2026-11-21): `https://erp.btnet.vn` → trang **502 Bad gateway** của Cloudflare, ô "Host" báo Error. Nghĩa là Apache **có** trả lời nhưng trả 502. Kiểm từng chặng, từ trong ra ngoài:

```bash
DC="docker compose -p erp -f /opt/frappe-gitops/erp.yaml"
# A. Frappe tự trả lời?
curl -sI -H 'Host: erp.btnet.vn' http://127.0.0.1:8090/login | head -1
# B. Apache trên máy chuyển đúng?
curl -skI --resolve erp.btnet.vn:443:127.0.0.1 https://erp.btnet.vn/login | head -1
# C. Cấu hình Apache hợp lệ? Proxy có được nạp?
httpd -t; httpd -M 2>/dev/null | grep -E 'proxy_http|proxy_wstunnel|headers'
grep -n 'erp.btnet.vn' -A3 /etc/apache2/conf/httpd.conf | grep -i include
# D. Nhật ký
tail -30 /etc/apache2/logs/error_log | grep -iE 'proxy|8090|AH0'
$DC logs --tail 30 frontend backend
```

| A | B | Nguyên nhân thường gặp | Sửa |
|---|---|---|---|
| ≠ 200 | — | Frappe chưa nhận site, hoặc backend lỗi | xem `logs backend`; `$DC exec backend ls sites` phải có `erp.btnet.vn` |
| 200 | 502/503 | Apache không nối được 8090: tham số `upgrade=websocket` không được hỗ trợ, thiếu `mod_proxy_http`, hoặc SELinux chặn | bỏ `upgrade=websocket` khỏi `proxy.conf` rồi thêm khối websocket riêng (bên dưới); `setsebool -P httpd_can_network_connect 1` nếu SELinux bật |
| 200 | 200 | Lỗi ở chặng Cloudflare, ví dụ SSL mode | Cloudflare SSL/TLS = **Full**; xoá cache |

Khối proxy dự phòng, không dùng `upgrade=`:
```apache
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"
RewriteEngine On
RewriteCond %{HTTP:Upgrade} =websocket [NC]
RewriteRule ^/(socket\.io/.*) ws://127.0.0.1:8090/$1 [P,L]
ProxyPass / http://127.0.0.1:8090/
ProxyPassReverse / http://127.0.0.1:8090/
```
Sau khi sửa: `/scripts/rebuildhttpdconf && httpd -t && /scripts/restartsrv_httpd`.
