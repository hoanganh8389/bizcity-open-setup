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
git clone git@github-open-setup:hoanganh8389/bizcity-open-setup.git /opt/open-setup
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
cp /opt/frappe-gitops/erp.yaml /opt/frappe-gitops/erp.yaml.bak-$(date +%Y%m%d%H%M)
sed -i "s#frappe/erpnext:v15.125.0#$TAG#g" /opt/frappe-gitops/erp.yaml
grep -n "image:" /opt/frappe-gitops/erp.yaml          # backend, frontend, websocket, scheduler, queue-* phải là $TAG
$DC up -d                                             # chỉ project erp; overlay2 busy → dừng, báo lại
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
