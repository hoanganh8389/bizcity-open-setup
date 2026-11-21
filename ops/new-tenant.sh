#!/bin/bash
# [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] OPS-1 — bản đã chạy thật trên VPS (tạo erp.btnet.vn), thêm kiểm slug + enable-scheduler.
# Tạo một site kế toán ERPNext + subdomain cPanel + proxy Apache.
# Dùng: ./new-tenant.sh <slug> [tên-miền-gốc]   vd: ./new-tenant.sh erp btnet.vn
# Sẽ được thay bằng ops/provision-tenant.sh (PHASE-001 W1).
set -euo pipefail
SUB=${1:?thiếu slug}; ROOT=${2:-btnet.vn}; SITE="$SUB.$ROOT"
[[ "$SUB" =~ ^[a-z][a-z0-9-]{2,29}$ && "$SUB" != *- ]] || { echo "slug không hợp lệ: $SUB" >&2; exit 2; }
[[ "$ROOT" =~ ^(btnet\.vn|bizcity\.vn)$ ]] || { echo "tên miền gốc không được phép: $ROOT" >&2; exit 2; }

CPUSER=vibeyeuc
DBPASS=$(grep ^DB_PASSWORD= /opt/frappe/custom.env | cut -d= -f2)
ADMINPASS=$(openssl rand -hex 8)
DC="docker compose -p erp -f /opt/frappe-gitops/erp.yaml"

echo ">> [1/3] Tạo site $SITE + cài ERPNext (3-5 phút)..."
$DC exec -T backend bench new-site "$SITE" \
  --mariadb-user-host-login-scope='%' \
  --db-root-password "$DBPASS" \
  --admin-password "$ADMINPASS" \
  --install-app erpnext
$DC exec -T backend bench --site "$SITE" set-config host_name "https://$SITE"
$DC exec -T backend bench --site "$SITE" enable-scheduler

echo ">> [2/3] Tạo subdomain cPanel..."
mkdir -p /home/$CPUSER/frappe-placeholder
chown $CPUSER:$CPUSER /home/$CPUSER/frappe-placeholder
uapi --user=$CPUSER SubDomain addsubdomain domain="$SUB" rootdomain="$ROOT" dir="frappe-placeholder" | grep -E 'status|errors' -A1

echo ">> [3/3] Apache proxy -> 127.0.0.1:8090..."
for T in std ssl; do
  D=/etc/apache2/conf.d/userdata/$T/2_4/$CPUSER/$SITE
  mkdir -p "$D"
  cat > "$D/proxy.conf" <<EOF
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"
ProxyPass / http://127.0.0.1:8090/ upgrade=websocket
ProxyPassReverse / http://127.0.0.1:8090/
EOF
done
/scripts/rebuildhttpdconf
httpd -t || { echo "Cấu hình Apache lỗi — KHÔNG restart. Xem docs/van-hanh/CAI-FRAPPE-TREN-VPS.md §6" >&2; exit 3; }
/scripts/restartsrv_httpd >/dev/null

touch /root/frappe-sites.txt && chmod 600 /root/frappe-sites.txt
echo "$SITE  Administrator  $ADMINPASS" >> /root/frappe-sites.txt
echo "=================================================="
echo "XONG: https://$SITE"
echo "User: Administrator   Pass: $ADMINPASS"
echo "(đã lưu vào /root/frappe-sites.txt)"
