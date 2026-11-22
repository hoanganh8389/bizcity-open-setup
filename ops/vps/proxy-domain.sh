#!/usr/bin/env bash
# [2026-11-23 01:40 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — chuyển một tên miền cPanel (kể cả *.tên-miền) về một cổng trên máy (container)
# Sổ tay: docs/van-hanh/DUA-LEN-VPS.md §8. Gặp thật 2026-11-23:
#   - vhost wildcard của cPanel đọc userdata ở thư mục `wildcard_safe.<miền>` — KHÔNG phải `_wildcard_.<miền>`;
#   - dòng `Include …/<thư mục>/*.conf` bị chú thích (#) tới khi thư mục có tệp + rebuildhttpdconf;
#   - tên miền phải TẠO TRƯỚC trong cPanel (Domains › Create A New Domain, bỏ tick "Share document root").
#
#   bash ops/vps/proxy-domain.sh <miền> <cổng>               vd: proxy-domain.sh open.bizcity.vn 8090
#   bash ops/vps/proxy-domain.sh --wildcard <miền> <cổng>    miền + *.miền, vd: proxy-domain.sh --wildcard openketoan.com 8088
#   bash ops/vps/proxy-domain.sh --kiem <miền>               chỉ đọc: vhost / Include / thư mục userdata của miền
set -uo pipefail

USERDATA=${APACHE_USERDATA:-/etc/apache2/conf.d/userdata}   # biến chỉ để thử ở máy dev
HTTPD=${APACHE_HTTPD_CONF:-/etc/apache2/conf/httpd.conf}
SCRIPTS=${CPANEL_SCRIPTS:-/scripts}
CPUSER=${CPUSER:-vibeyeuc}

die() { echo "DỪNG: $*" >&2; exit 1; }
[ "$(id -u)" = 0 ] || die "chạy bằng root"
[ -f "$HTTPD" ] || die "không thấy $HTTPD (máy không phải cPanel?)"

kiem() {
  local d=$1
  echo "== vhost:"; grep -nE "ServerName (www\.)?(_wildcard_\.)?${d//./\\.}$|ServerAlias .*${d//./\\.}" "$HTTPD" | head -8
  echo "== Include (dòng có # là CHƯA bật):"; grep -nE "Include .*/(${d//./\\.}|wildcard_safe\.${d//./\\.})/\*\.conf" "$HTTPD"
  echo "== thư mục userdata:"; ls -d "$USERDATA"/*/2_4/"$CPUSER"/*"$d"* 2>/dev/null
}

write_proxy() {
  local dir=$1 port=$2 t
  for t in std ssl; do
    mkdir -p "$USERDATA/$t/2_4/$CPUSER/$dir"
    printf 'ProxyPreserveHost On\nProxyPass        / http://127.0.0.1:%s/\nProxyPassReverse / http://127.0.0.1:%s/\nRequestHeader set X-Forwarded-Proto "https"\n' \
      "$port" "$port" > "$USERDATA/$t/2_4/$CPUSER/$dir/proxy.conf"
    echo "  ghi $USERDATA/$t/2_4/$CPUSER/$dir/proxy.conf → 127.0.0.1:$port"
  done
}

WILD=0
case ${1:-} in
  --kiem) [ $# -eq 2 ] || die "dùng: --kiem <miền>"; kiem "$2"; exit 0 ;;
  --wildcard) WILD=1; shift ;;
esac
[ $# -eq 2 ] || { sed -n '9,12p' "$0"; exit 2; }
DOM=$1; PORT=$2
[[ $DOM =~ ^[a-z0-9.-]+$ ]] || die "tên miền lạ: $DOM"
[[ $PORT =~ ^[0-9]+$ ]] || die "cổng lạ: $PORT"
grep -qE "ServerName ${DOM//./\\.}$|ServerAlias .*[ ]${DOM//./\\.}( |$)" "$HTTPD" \
  || die "Apache chưa có vhost cho $DOM — tạo tên miền trong cPanel (Domains › Create A New Domain, bỏ tick Share document root) rồi chạy lại"
if [ $WILD = 1 ]; then
  grep -qE "ServerName _wildcard_\.${DOM//./\\.}$" "$HTTPD" || die "chưa có vhost *.$DOM — tạo thêm tên miền *.$DOM trong cPanel rồi chạy lại"
fi
curl -s -m 3 -o /dev/null "http://127.0.0.1:$PORT/" || echo "  ⚠ 127.0.0.1:$PORT chưa trả lời — container đã chạy chưa? (vẫn ghi cấu hình)"

write_proxy "$DOM" "$PORT"
if [ $WILD = 1 ]; then
  write_proxy "wildcard_safe.$DOM" "$PORT"
  rm -rf "$USERDATA"/std/2_4/"$CPUSER"/_wildcard_."$DOM" "$USERDATA"/ssl/2_4/"$CPUSER"/_wildcard_."$DOM"   # tên sai đã thử trước đây
fi
"$SCRIPTS"/rebuildhttpdconf >/dev/null && "$SCRIPTS"/restartsrv_httpd >/dev/null || die "rebuildhttpdconf / restartsrv_httpd lỗi — chạy tay để xem"

ok=1
for d in "$DOM" $([ $WILD = 1 ] && echo "wildcard_safe.$DOM"); do
  n=$(grep -cE "^[[:space:]]*Include \"$USERDATA/(std|ssl)/2_4/$CPUSER/$d/\*\.conf\"" "$HTTPD")
  if [ "$n" -ge 2 ]; then echo "  ✔ Include $d đã bật (std + ssl)"; else echo "  ✘ Include $d chưa bật ($n/2)"; ok=0; fi
done
echo "Kiểm từ ngoài (qua Cloudflare):"
curl -s -m 15 -o /dev/null -w "  https://$DOM/ → %{http_code}\n" "https://$DOM/"
[ $WILD = 1 ] && curl -s -m 15 -o /dev/null -w "  https://thu-proxy.$DOM/ → %{http_code}\n" "https://thu-proxy.$DOM/"
[ $ok = 1 ] || exit 1
