#!/usr/bin/env bash
# [2026-11-22 11:55 PM Johnny Chu - Chu Hoàng Anh] OPS-VPS — gỡ container khi Docker báo `overlay2 … device or resource busy`
# trên VPS cPanel 157.10.53.169 (zalo-hub, Open Kế Toán, Frappe chạy chung). Sổ tay: docs/van-hanh/DOCKER-OVERLAY2-BUSY.md
#
#   bash ops/vps/go-container.sh chan-doan <container>        chỉ đọc: tiến trình / mount namespace nào đang giữ lớp overlay
#   bash ops/vps/go-container.sh go <container> [...]          dừng + gỡ; bận thì giải phóng mount theo thứ tự rồi thử lại
#   bash ops/vps/go-container.sh du-an <project compose>       `go` mọi container có nhãn com.docker.compose.project=<project>
#
# Không bao giờ: restart docker, sửa /var/lib/docker, kill tiến trình, xoá volume. Lệnh giải phóng dùng: cagefsctl --remount-all
# (CloudLinux CageFS), /scripts/restartsrv_httpd, /scripts/restartsrv_apache_php_fpm (cPanel) — mỗi lệnh làm web nháy 1–2 giây.
set -uo pipefail

LOG=/var/log/bizcity-docker-go.log
HOSTNS=$(readlink /proc/1/ns/mnt)

say() { printf '%s\n' "$*"; printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG" 2>/dev/null || true; }
die() { say "DỪNG: $*"; exit 1; }

[ "$(id -u)" = 0 ] || die "chạy bằng root"
command -v docker >/dev/null || die "không thấy docker"

# Thư mục lớp overlay của container (vd b35a3013…); container đã chết vẫn đọc được.
layer_of() {
  # containerd snapshotter (Docker Desktop) không có GraphDriver.Data → "<no value>": coi như không đọc được
  docker inspect -f '{{.GraphDriver.Data.MergedDir}}' "$1" 2>/dev/null | grep -F /merged | awk -F/ '{print $(NF-1)}'
}

# Mount namespace (khác của máy) còn giữ lớp $1 — mỗi dòng một namespace.
holder_ns() {
  local layer=$1 f p ns
  for f in /proc/[0-9]*/mountinfo; do
    grep -q "$layer" "$f" 2>/dev/null || continue
    p=${f#/proc/}; p=${p%%/*}
    ns=$(readlink "/proc/$p/ns/mnt" 2>/dev/null) || continue
    [ "$ns" = "$HOSTNS" ] || echo "$ns"
  done | sort -u
}

report() {
  local layer=$1 ns q n=0
  say "Lớp overlay: $layer"
  for ns in $(holder_ns "$layer"); do
    n=$((n + 1))
    say "== namespace $ns — tiến trình sống lâu nhất:"
    for q in /proc/[0-9]*; do
      [ "$(readlink "$q/ns/mnt" 2>/dev/null)" = "$ns" ] || continue
      ps -o pid=,user=,etime=,comm=,args= -p "${q#/proc/}" 2>/dev/null
    done | sort -k3 -r | head -5 | while IFS= read -r line; do say "   $line"; done
  done
  [ "$n" = 0 ] && say "Không namespace nào ngoài máy giữ lớp này."
  if command -v cagefsctl >/dev/null; then say "CageFS: có (cagefsctl)"; else say "CageFS: không có"; fi
  return 0
}

try_rm() { docker rm -f "$1" >/dev/null 2>>"$LOG"; }

go_one() {
  local c=$1 layer name
  name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null) || { say "Không có container $c — bỏ qua"; return 0; }
  layer=$(layer_of "$c")
  say "Gỡ ${name#/} ($c), trạng thái $(docker inspect -f '{{.State.Status}}' "$c")"
  docker stop -t 20 "$c" >/dev/null 2>&1 || true
  if try_rm "$c"; then say "  ✔ đã gỡ"; return 0; fi
  say "  bận (overlay2 busy) — giải phóng mount"
  local step
  for step in cagefs httpd phpfpm; do
    case $step in
      cagefs) command -v cagefsctl >/dev/null || continue; say "  → cagefsctl --remount-all"; cagefsctl --remount-all >>"$LOG" 2>&1 ;;
      httpd)  [ -x /scripts/restartsrv_httpd ] || continue; say "  → /scripts/restartsrv_httpd"; /scripts/restartsrv_httpd >>"$LOG" 2>&1 ;;
      phpfpm) [ -x /scripts/restartsrv_apache_php_fpm ] || continue; say "  → /scripts/restartsrv_apache_php_fpm"; /scripts/restartsrv_apache_php_fpm >>"$LOG" 2>&1 ;;
    esac
    sleep 3
    if try_rm "$c"; then say "  ✔ đã gỡ sau bước $step"; return 0; fi
  done
  say "  ✘ vẫn bận — còn giữ:"
  [ -n "$layer" ] && report "$layer"
  say "  Gửi đoạn trên cho người vận hành. Cách cuối: reboot (xem sổ tay — sau reboot gỡ container ngay, trước khi httpd/PHP chạy lâu)."
  return 2
}

cmd=${1:-}; shift || true
case $cmd in
  chan-doan)
    [ $# -ge 1 ] || die "thiếu tên / mã container"
    layer=$(layer_of "$1"); [ -n "$layer" ] || die "không đọc được lớp overlay của $1"
    report "$layer" ;;
  go)
    [ $# -ge 1 ] || die "thiếu tên / mã container"
    rc=0; for c in "$@"; do go_one "$c" || rc=$?; done; exit $rc ;;
  du-an)
    [ $# -eq 1 ] || die "dùng: du-an <project> (vd ketoan, erp, zalo-hub)"
    ids=$(docker ps -aq --filter "label=com.docker.compose.project=$1")
    [ -n "$ids" ] || { say "Project $1 không còn container nào"; exit 0; }
    rc=0; for c in $ids; do go_one "$c" || rc=$?; done
    [ $rc = 0 ] && say "Xong project $1 — giờ chạy lại compose up của project đó (sổ tay §3)."
    exit $rc ;;
  *)
    sed -n '4,10p' "$0"; exit 2 ;;
esac
