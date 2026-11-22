#!/usr/bin/env bash
# [2026-11-23 01:40 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — khoá prov_… của Provisioning API (Open Kế Toán /opt/ketoan, SITE_MODE=multi)
# Sổ tay: docs/van-hanh/DUA-LEN-VPS.md §8. Gặp thật 2026-11-23: khoá in ra màn hình rồi bị dán vào chat → phải thu hồi 2 lần;
# lệnh thu hồi bằng cả khoá trả UPDATE 0 vì cột `prefix` chỉ giữ 11 ký tự đầu.
#
#   bash ops/vps/okt-prov-key.sh tao "<nhãn>"        tạo khoá, ghi THẲNG vào /root/prov-key-<giờ>.txt (chmod 600), màn hình chỉ in tiền tố
#   bash ops/vps/okt-prov-key.sh ds                   danh sách khoá: tiền tố, nhãn, ngày tạo, đã thu hồi chưa
#   bash ops/vps/okt-prov-key.sh thu-hoi <tiền tố>    thu hồi theo 11 ký tự đầu (vd prov_y3cKfi); dán cả khoá cũng được — tự cắt
#   bash ops/vps/okt-prov-key.sh kiem <tệp khoá>      gọi /_sites/v1/health bằng khoá trong tệp (không in khoá)
set -uo pipefail

KT=${KETOAN_DIR:-/opt/ketoan}
ADMIN_HOST=${SITE_ADMIN_HOST_CHECK:-admin.openketoan.com}
die() { echo "DỪNG: $*" >&2; exit 1; }
[ "$(id -u)" = 0 ] || die "chạy bằng root"
cd "$KT" || die "không thấy $KT"
psqlc() { docker compose exec -T db psql -U ketoan -d kt_control -v ON_ERROR_STOP=1 "$@"; }

case ${1:-} in
  tao)
    label=${2:-Site Manager}
    f=/root/prov-key-$(date +%Y%m%d-%H%M%S).txt
    umask 077
    docker compose run --rm --no-deps --entrypoint node db-migrate dist/cli/site.js key-create --label "$label" > "$f" 2>&1 || { cat "$f" >&2; die "tạo khoá lỗi"; }
    chmod 600 "$f"
    key=$(grep -oE 'prov_[A-Za-z0-9_-]{20,80}' "$f" | tail -1)
    [ -n "$key" ] || die "không thấy khoá trong đầu ra (xem $f)"
    echo "✔ Đã tạo khoá ${key:0:11}… — nhãn \"$label\" — lưu ở $f (chỉ root đọc được)"
    echo "  Dán vào Site Manager: xem bằng 'cat $f' NGAY TRÊN VPS. Không dán khoá vào chat / ticket."
    ;;
  ds)
    psqlc -c "SELECT prefix, label, to_char(created_at,'YYYY-MM-DD HH24:MI') AS tao, coalesce(to_char(revoked_at,'YYYY-MM-DD HH24:MI'),'— đang dùng') AS thu_hoi FROM provision_keys ORDER BY created_at" ;;
  thu-hoi)
    [ $# -eq 2 ] || die "dùng: thu-hoi <tiền tố 11 ký tự, vd prov_y3cKfi>"
    p=${2:0:11}
    [[ $p =~ ^prov_[A-Za-z0-9_-]{6}$ ]] || die "tiền tố lạ: $p"
    psqlc -c "UPDATE provision_keys SET revoked_at = now() WHERE prefix = '$p' AND revoked_at IS NULL" ;;
  kiem)
    [ $# -eq 2 ] && [ -r "$2" ] || die "dùng: kiem <tệp khoá do 'tao' ghi>"
    key=$(grep -oE 'prov_[A-Za-z0-9_-]{20,80}' "$2" | tail -1)
    curl -s -H "Host: $ADMIN_HOST" -H "Authorization: Bearer $key" http://127.0.0.1:8088/_sites/v1/health; echo ;;
  *) sed -n '6,9p' "$0"; exit 2 ;;
esac
