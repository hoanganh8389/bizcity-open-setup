# Đưa Site Manager + openketoan.com lên VPS (từng lệnh)
<!-- [2026-11-22 11:00 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 W0-2 — sổ tay từng lệnh: vào VPS, git, image Site Manager, site open.bizcity.vn, tên miền openketoan.com; trình tự đã chạy thử trên MariaDB 10.6 + Redis + image này ở máy dev -->

> **Máy:** VPS cPanel `157.10.53.169`, tài khoản cPanel `vibeyeuc`, dùng chung với zalo-hub + WordPress. **Cấm:** `systemctl restart docker`, `docker compose up` cả cụm khác. Gặp `overlay2 … device or resource busy` thì **dừng**, không lặp lệnh.
> **Đã chạy thử ở máy dev (2026-11-22):** image ở §2, `new-site --install-app`, vai Operator tự có, `create_operator_user`, gọi REST bằng token, worker chạy việc tạo site.
> Thứ tự: §1 vào máy + git → §2 image → §3 site `open.bizcity.vn` → §4 Open Kế Toán nhiều site → §5 tên miền → §6 nối hai bên → §7 WordPress.

## 1. Vào VPS và lấy mã

```powershell
# Máy Windows của bạn (PowerShell)
ssh root@157.10.53.169
```

Trên VPS — khoá chỉ đọc cho repo riêng tư `bizcity-open-setup`:

```bash
ssh-keygen -t ed25519 -f /root/.ssh/open-setup-deploy -N "" -C "vps open-setup (chỉ đọc)"
cat /root/.ssh/open-setup-deploy.pub
# → GitHub: repo bizcity-open-setup › Settings › Deploy keys › Add deploy key (KHÔNG tick "Allow write access")

cat >> /root/.ssh/config <<'EOF'
Host github-open-setup
  HostName github.com
  User git
  IdentityFile /root/.ssh/open-setup-deploy
  IdentitiesOnly yes
EOF
git clone https://github.com/hoanganh8389/bizcity-open-setup.git /opt/open-setup   # repo công khai từ 2026-11-22 — không cần khoá
cd /opt/open-setup && git log --oneline -1
```

Cập nhật sau này: `cd /opt/open-setup && git pull`.

## 2. Build image Site Manager

```bash
cd /opt/open-setup
SHA=$(git rev-parse --short HEAD)
TAG=bizcity/site-manager:v15.125.0-$SHA
docker build -f ops/site-manager/Containerfile --build-arg ERPNEXT_VERSION=v15.125.0 -t $TAG .
docker run --rm --entrypoint bash $TAG -c "cat /home/frappe/frappe-bench/sites/apps.txt"   # phải 3 dòng: frappe, erpnext, bizcity_site_manager
```

`ERPNEXT_VERSION` = đúng bản trong `/opt/frappe/custom.env` (2026-11-21: `v15.125.0`).

## 3. Chuyển cụm Frappe `erp` sang image mới + tạo site `open.bizcity.vn`

```bash
DC="docker compose -p erp -f /opt/frappe-gitops/erp.yaml"
cp -f /opt/frappe-gitops/erp.yaml /opt/frappe-gitops/erp.yaml.bak-$(date +%Y%m%d%H%M)   # cp: root có alias cp -i
sed -i "s#frappe/erpnext:v15.125.0#$TAG#g" /opt/frappe-gitops/erp.yaml
grep -n "image:" /opt/frappe-gitops/erp.yaml          # backend, frontend, websocket, scheduler, queue-* phải là $TAG
$DC up -d --pull never                               # chỉ project erp; image chỉ có trên máy (compose của frappe_docker đặt pull_policy: always → thiếu --pull never là đi kéo Docker Hub, "pull access denied"); overlay2 busy → dừng, báo lại <!-- [2026-11-22 11:30 PM Johnny Chu - Chu Hoàng Anh] W0-2 — gặp thật trên VPS -->
$DC ps

# volume sites đã có từ trước: thêm app vào apps.txt MỘT lần (có xuống dòng)
$DC exec backend bash -c "cd sites && sed -i -e '\$a\\' apps.txt && (grep -qx bizcity_site_manager apps.txt || echo bizcity_site_manager >> apps.txt) && cat apps.txt"

# site quản trị — mật khẩu MariaDB root = DB_PASSWORD trong /opt/frappe/custom.env
DBP=$(grep ^DB_PASSWORD= /opt/frappe/custom.env | cut -d= -f2)
ADMINP=$(openssl rand -base64 18); echo "open.bizcity.vn Administrator: $ADMINP" >> /root/frappe-sites.txt
$DC exec backend bench new-site open.bizcity.vn --mariadb-root-password "$DBP" --admin-password "$ADMINP" \
    --mariadb-user-host-login-scope=% --install-app bizcity_site_manager
$DC exec backend bench --site open.bizcity.vn list-apps                     # có bizcity_site_manager
$DC exec backend bench --site open.bizcity.vn enable-scheduler
```

**Kiểm:** `$DC exec backend bench --site open.bizcity.vn execute frappe.db.exists --args '["Role", "Bizcity Site Operator"]'` → `"Bizcity Site Operator"`.

Lùi: `cp erp.yaml.bak-… erp.yaml && $DC up -d` (site `erp.btnet.vn` vẫn chạy với image cũ).

## 4. Open Kế Toán chế độ nhiều site (`/opt/ketoan`)

Chi tiết: open-ketoan `docs/ops/NHIEU-SITE.md` §1–§3, §7. Bản demo `ketoan.btnet.vn` đang chạy ở đây (web chạy ngoài compose vì overlay2 — xem ghi chú vận hành).

```bash
cd /opt/ketoan
cp .env .env.bak-$(date +%Y%m%d%H%M)
git fetch origin && git checkout origin/main          # có PR #590 (externalRef, sample, reset-password)
cat >> .env <<EOF
SITE_MODE=multi
CONTROL_DATABASE_URL=postgres://ketoan:<mật khẩu db>@db:5432/kt_control
SITE_TEMPLATE_DB=kt_template
SITE_SECRET_KEY=$(openssl rand -base64 48)
SITE_ADMIN_HOST=admin.openketoan.com
BIZCITY_SAMPLE=thuong-mai-ban-le
EOF
grep ^SITE_SECRET_KEY= .env >> /root/ketoan-site-secret.txt && chmod 600 /root/ketoan-site-secret.txt   # SAO LƯU RIÊNG: mất khoá = mất mật khẩu mọi site
```

Rồi theo `NHIEU-SITE.md`: tạo `kt_control` + `kt_template`, `db:migrate` vào `kt_template`, `bizcity site migrate --all` (§3, chạy trong ảnh theo §7), build lại `api` + `web` bằng mã mới, giữ demo bằng §3b. Khoá cho Site Manager:

```bash
docker compose run --rm --no-deps --entrypoint node -e CONTROL_DATABASE_URL -e SITE_SECRET_KEY -e SITE_TEMPLATE_DB \
  db-migrate dist/cli/site.js key-create --label "Site Manager" --ips 127.0.0.1,157.10.53.169
# → chép khoá prov_… (in MỘT lần)
```

## 5. Tên miền

### 5a. `openketoan.com` → Open Kế Toán (cổng 8088)

DNS Cloudflare đã có (2026-11-22): `openketoan.com` và `*.openketoan.com` → `157.10.53.169`, proxied.

1. cPanel › **Domains › Create A New Domain**: `openketoan.com`, **bỏ tick** "Share document root", thư mục `openketoan-placeholder`. Làm lại với `*.openketoan.com` (cPanel nhận tên miền con wildcard).
2. Cloudflare › SSL/TLS › Origin Server › **Create Certificate** cho `openketoan.com, *.openketoan.com` → cPanel › SSL/TLS › Install cho cả hai tên. Cloudflare SSL mode **Full (strict)**.
3. Proxy (cùng kiểu `ketoan.btnet.vn`):
   ```bash
   for H in openketoan.com _wildcard_.openketoan.com; do for T in std ssl; do
     D=/etc/apache2/conf.d/userdata/$T/2_4/vibeyeuc/$H; mkdir -p $D
     cat > $D/proxy.conf <<'EOF'
   ProxyPreserveHost On
   ProxyPass        / http://127.0.0.1:8088/
   ProxyPassReverse / http://127.0.0.1:8088/
   RequestHeader set X-Forwarded-Proto "https"
   EOF
   done; done
   /scripts/rebuildhttpdconf && /scripts/restartsrv_httpd
   grep -n "openketoan" /etc/apache2/conf/httpd.conf | head     # thấy ServerName / ServerAlias *.openketoan.com + Include proxy.conf
   ```

**Kiểm:** `curl -s https://admin.openketoan.com/_sites/v1/health -H "Authorization: Bearer prov_…"` → `{"contract":"bizcity_site_provisioning@1",…}`.

### 5b. `open.bizcity.vn` → Site Manager (cổng 8090)

1. DNS: bản ghi `open` (A) → `157.10.53.169` (bỏ qua nếu `*.bizcity.vn` đã trỏ máy này).
2. cPanel › Create A New Domain: `open.bizcity.vn`, bỏ tick share, thư mục `frappe-placeholder` (tên miền con tạo riêng thắng wildcard, như `ketoan.btnet.vn`).
3. Proxy như §5a nhưng `http://127.0.0.1:8090/` cho `open.bizcity.vn` (std + ssl), rồi `rebuildhttpdconf` + `restartsrv_httpd`.

**Kiểm:** mở `https://open.bizcity.vn` → trang đăng nhập Frappe; đăng nhập `Administrator` / mật khẩu ở `/root/frappe-sites.txt`.

## 6. Nối Site Manager ↔ Open Kế Toán, cấp khoá cho WordPress

Trên `https://open.bizcity.vn/app/bizcity-site-manager-settings`:
- `Provisioning URL` = `https://admin.openketoan.com`, `Provisioning Key` = khoá `prov_…` (§4);
- bảng tên miền gốc: `openketoan.com`, bật, `wildcard`.

```bash
$DC exec backend bench --site open.bizcity.vn execute bizcity_site_manager.install.create_operator_user --kwargs "{'email': 'bizcity-web@bizcity.vn'}"
# → in <api_key>:<api_secret> MỘT lần
curl -s "https://open.bizcity.vn/api/method/bizcity_site_manager.api.slug_available?slug=thu-mot" -H "Authorization: token <api_key>:<api_secret>"
# {"message":{"slug":"thu-mot","valid":true,"available":true}}
```

## 7. WordPress bizcity.vn

`wp-config.php`:

```php
define('BIZCITY_KETOAN_DRIVER', 'open-setup');
define('BIZCITY_OPEN_SETUP_URL', 'https://open.bizcity.vn');
define('BIZCITY_OPEN_SETUP_TOKEN', '<api_key>:<api_secret>');
define('BIZCITY_KETOAN_ROOT_DOMAINS', 'bizcity.vn=openketoan.com');
```

Trang `/dung-pm-ke-toan-mien-phi/` (`[bizcity_trial_ketoan]`, để Riêng tư) → tạo thử một phần mềm → nghiệm thu theo bizcity-web PHASE-02 `50-LEN-MAY-THAT.md` §5.

## 8. Kinh nghiệm thật khi dựng (2026-11-22 → 23) — tình huống, nguyên nhân, cách xử lý
<!-- [2026-11-23 01:40 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — ghi lại mọi tình huống gặp khi chủ dự án chạy sổ tay này trên VPS; script ở ops/vps/ -->

Script đi kèm (đứng ở `/opt/open-setup`, `git pull` trước):

| Script | Làm gì |
|---|---|
| `ops/vps/go-container.sh` | gỡ container khi `overlay2 … busy` (`chan-doan` / `go` / `du-an`) — xem [DOCKER-OVERLAY2-BUSY.md](DOCKER-OVERLAY2-BUSY.md) |
| `ops/vps/proxy-domain.sh` | chuyển tên miền cPanel (kể cả `*.miền`) về cổng container, rebuild Apache, kiểm `Include` đã bật, curl từ ngoài |
| `ops/vps/okt-prov-key.sh` | khoá `prov_…`: tạo thẳng vào tệp (màn hình chỉ in tiền tố), `ds`, `thu-hoi <tiền tố>`, `kiem <tệp>` |

| # | Tình huống | Nguyên nhân | Xử lý |
|---|---|---|---|
| 1 | `ssh: Could not resolve hostname github-open-setup` | chưa thêm `Host github-open-setup` vào `~/.ssh/config` | repo đã công khai → clone HTTPS (§1) |
| 2 | `Permission denied (publickey)` khi clone | khoá deploy chưa thêm vào GitHub | như trên |
| 3 | Lệnh sau chạy ở sai thư mục, `TAG` thiếu mã commit, `sed` đã sửa `erp.yaml` sang image không tồn tại | dán cả khối khi lệnh đầu lỗi | **chạy từng khối**, xem kết quả rồi mới chạy tiếp; lùi `erp.yaml` bằng bản `.bak` |
| 4 | `cp: overwrite …?` nuốt dòng kế tiếp | root có alias `cp -i` | dùng `\cp -f` |
| 5 | `pull access denied for bizcity/site-manager` | `erp.yaml` của frappe_docker có `pull_policy: always` | `docker compose … up -d --pull never` |
| 6 | `bench: command not found` | `bench` chỉ có trong container | `$DC exec backend bench …` |
| 7 | `ModuleNotFoundError: bizcity_site_manager` khi `new-site` | container vẫn chạy image cũ (bước `up` chưa xong) nhưng `apps.txt` đã có app | `up -d --pull never` cho xong → `install-app`; nếu thiếu DocType thì `bench --site … migrate` |
| 8 | `install-app` không in "Updating DocTypes" | lần cài trước hỏng giữa chừng | `bench --site … migrate` (tạo đủ DocType, chạy `after_migrate`) |
| 9 | `overlay2 … device or resource busy` (mọi lần thay container) | **cPanel virtfs**: jail `/home/virtfs/vibeyeuc/` bind-mount `/var/lib` → chép mount overlay của container | `ops/vps/go-container.sh du-an <project>` trước `compose up`; sửa tận gốc ở DOCKER-OVERLAY2-BUSY.md |
| 10 | Sau reboot `curl :4000/healthz` từ chối | zca-bridge **đã gỡ** 2026-10-14 | bỏ qua; chỉ kiểm zalo-hub `:3900/api/health` |
| 11 | `getaddrinfo ENOTFOUND db` (api lặp khởi động) | container `db` kẹt `Removal In Progress` (busy) | như #9 rồi `compose up -d` |
| 12 | `/_sites/v1/health` trả HTML (`<title>ERP`) | nginx của ảnh `web` thiếu `location /_sites/` | đã sửa open-ketoan PR #602 → `git pull` + `docker compose build web` + thay container `web` |
| 13 | `git pull` "Already up to date" ngay sau khi merge | kéo trước lúc merge xong | kéo lại; kiểm `grep -c "location /_sites/" docker/nginx.conf` = 1; build mà dòng `COPY docker/nginx.conf` còn `CACHED` là chưa có mã mới |
| 14 | `createdb kt_template` không chạy | dán nhiều dòng, dòng bị nuốt | chạy từng dòng; kiểm `select datname … like 'kt_%'` |
| 15 | `*.openketoan.com` → 403 / 500, `openketoan.com` → 200 | vhost wildcard của cPanel đọc userdata ở **`wildcard_safe.<miền>`**, không phải `_wildcard_.<miền>` | `ops/vps/proxy-domain.sh --wildcard openketoan.com 8088` |
| 16 | `Include …/*.conf` có `#` đằng trước | thư mục userdata chưa có tệp lúc rebuild | ghi tệp rồi `rebuildhttpdconf` (script làm sẵn) |
| 17 | Khoá `prov_…` / khoá Frappe / khoá `kt_…` lộ vì dán ảnh / chat | lệnh in khoá ra màn hình | `okt-prov-key.sh tao` (ghi vào tệp); khoá Frappe: chạy lại `create_operator_user` (khoá cũ hết dùng) |
| 18 | `UPDATE provision_keys … WHERE prefix = '<cả khoá>'` → `UPDATE 0` | cột `prefix` chỉ giữ **11 ký tự đầu** | `okt-prov-key.sh thu-hoi prov_xxxxxx` |
| 19 | `cap-nhat.sh` xong, db-migrate in `+ Đơn vị demo` | database `ketoan` của bản demo đang trống | bình thường cho bản demo; bản có dữ liệu thật thì kiểm bản sao lưu `backups/ketoan-*.sql.gz` trước |
| 20 | `cap-nhat.sh` / compose `web` tranh cổng 8088 với `ketoan-web-run` | web từng chạy ngoài compose (cách né busy cũ) | gỡ `ketoan-web-run` trước (`go-container.sh go ketoan-web-run`) |
| 21 <!-- [2026-11-23 02:05 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS --> | Site Manager gọi `https://admin.openketoan.com/_sites/v1/health` → `HTTP_403` (curl trên VPS thì 200/401) | **Cloudflare** (Browser Integrity Check) chặn User-Agent mặc định `Python-urllib/3.x` — `error code: 1010`; Open Kế Toán không bao giờ trả 403 | `provisioning.py` gửi `User-Agent: bizcity-site-manager/…` (PR sửa); tạm thời: Cloudflare › Security › WAF › Custom rule *Hostname = admin.openketoan.com → Skip* Browser Integrity Check / Bot Fight |
