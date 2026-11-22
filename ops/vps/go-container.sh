#!/usr/bin/env bash
# [2026-11-22 11:55 PM Johnny Chu - Chu Hoàng Anh] OPS-VPS — gỡ container khi Docker báo `overlay2 … device or resource busy`
# trên VPS cPanel 157.10.53.169 (zalo-hub, Open Kế Toán, Frappe chạy chung). Sổ tay: docs/van-hanh/DOCKER-OVERLAY2-BUSY.md
# [2026-11-23 12:20 AM Johnny Chu - Chu Hoàng Anh] OPS-VPS — v2: gặp thật trên VPS: không namespace nào khác giữ, máy KHÔNG có CageFS,
# restart httpd + php-fpm không đủ → `merged` vẫn là mount ở CHÍNH namespace của máy (Docker không bỏ mount được khi container chết).
# Thêm: chẩn đoán mount ở máy + tiến trình đang dùng; bỏ mount cũ (umount, rồi umount -l); tiến trình mồ côi của container chết chỉ
# bị dừng khi có --kill-orphans.
#
#   bash ops/vps/go-container.sh chan-doan <container>                  chỉ đọc: mount ở máy, tiến trình đang dùng, namespace khác giữ
#   bash ops/vps/go-container.sh go [--kill-orphans] <container> [...]   dừng + gỡ; bận thì giải phóng theo thứ tự rồi thử lại
#   bash ops/vps/go-container.sh du-an [--kill-orphans] <project>        `go` mọi container có nhãn com.docker.compose.project=<project>
#
# Không bao giờ: restart docker, xoá gì trong /var/lib/docker, xoá volume, kill tiến trình NGOÀI container đã chết.
# Bước giải phóng (dừng ngay khi gỡ được): umount `merged` của container đã chết (không ai dùng) → cagefsctl --remount-all (nếu có)
# → /scripts/restartsrv_httpd → /scripts/restartsrv_apache_php_fpm → umount -l → (--kill-orphans) dừng tiến trình mồ côi có root
# nằm trong `merged` của container đó. httpd / php-fpm làm web nháy 1–2 giây.
set -uo pipefail

LOG=/var/log/bizcity-docker-go.log
HOSTNS=$(readlink /proc/1/ns/mnt)
OVL=${BIZCITY_OVL_DIR:-/var/lib/docker/overlay2}   # biến chỉ để thử ở máy dev
KILL_ORPHANS=0

say() { printf '%s\n' "$*"; printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG" 2>/dev/null || true; }
die() { say "DỪNG: $*"; exit 1; }

[ "$(id -u)" = 0 ] || die "chạy bằng root"
command -v docker >/dev/null || die "không thấy docker"

# Thư mục lớp overlay của container (vd b35a3013…); container đã chết vẫn đọc được.
layer_of() {
  # containerd snapshotter (Docker Desktop) không có GraphDriver.Data → "<no value>": coi như không đọc được
  docker inspect -f '{{.GraphDriver.Data.MergedDir}}' "$1" 2>/dev/null | grep -F /merged | awk -F/ '{print $(NF-1)}'
}

merged_of() { printf '%s/%s/merged' "$OVL" "$1"; }

# `merged` còn là mount ở namespace của máy không.
host_mounted() { awk -v m="$1" '$5 == m { f = 1 } END { exit !f }' /proc/1/mountinfo; }

# Tiến trình có root / cwd nằm trong `merged` (tiến trình của container, kể cả mồ côi) — "pid comm".
users_of() {
  local m=$1 q r c
  for q in /proc/[0-9]*; do
    r=$(readlink "$q/root" 2>/dev/null) || continue
    c=$(readlink "$q/cwd" 2>/dev/null) || c=
    case "$r" in "$m"|"$m"/*) ;; *) case "$c" in "$m"|"$m"/*) ;; *) continue ;; esac ;; esac
    printf '%s %s\n' "${q#/proc/}" "$(cat "$q/comm" 2>/dev/null)"
  done
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
  local layer=$1 m ns q n=0 u
  m=$(merged_of "$layer")
  say "Lớp overlay: $layer"
  if host_mounted "$m"; then say "Mount ở máy: CÒN ($m)"; else say "Mount ở máy: không"; fi
  u=$(users_of "$m")
  if [ -n "$u" ]; then say "Tiến trình đang dùng (root/cwd trong merged):"; while IFS= read -r line; do say "   $line"; done <<< "$u"
  else say "Tiến trình đang dùng: không"; fi
  if command -v fuser >/dev/null && host_mounted "$m"; then
    say "fuser -m:"; fuser -vm "$m" 2>&1 | head -10 | while IFS= read -r line; do say "   $line"; done
  fi
  for ns in $(holder_ns "$layer"); do
    n=$((n + 1))
    say "== namespace khác $ns — tiến trình sống lâu nhất:"
    for q in /proc/[0-9]*; do
      [ "$(readlink "$q/ns/mnt" 2>/dev/null)" = "$ns" ] || continue
      ps -o pid=,user=,etime=,comm=,args= -p "${q#/proc/}" 2>/dev/null
    done | sort -k3 -r | head -5 | while IFS= read -r line; do say "   $line"; done
  done
  [ "$n" = 0 ] && say "Namespace khác giữ lớp này: không"
  if command -v cagefsctl >/dev/null; then say "CageFS: có (cagefsctl)"; else say "CageFS: không có"; fi
  return 0
}

try_rm() { docker rm -f "$1" >/dev/null 2>>"$LOG"; }

# Một bước giải phóng; trả 0 nếu đã làm gì đó (để thử gỡ lại), 1 nếu bỏ qua.
release_step() {
  local step=$1 layer=$2 m u pids
  m=$(merged_of "$layer")
  case $step in
    umount)
      host_mounted "$m" || return 1
      u=$(users_of "$m"); [ -z "$u" ] || { say "  · bỏ qua umount: còn tiến trình dùng merged"; return 1; }
      say "  → umount $m (mount cũ của container đã chết, không ai dùng)"; umount "$m" >>"$LOG" 2>&1 ;;
    cagefs)
      command -v cagefsctl >/dev/null || return 1
      say "  → cagefsctl --remount-all"; cagefsctl --remount-all >>"$LOG" 2>&1 ;;
    httpd)
      [ -x /scripts/restartsrv_httpd ] || return 1
      [ -n "$(holder_ns "$layer")" ] || return 1
      say "  → /scripts/restartsrv_httpd"; /scripts/restartsrv_httpd >>"$LOG" 2>&1 ;;
    phpfpm)
      [ -x /scripts/restartsrv_apache_php_fpm ] || return 1
      [ -n "$(holder_ns "$layer")" ] || return 1
      say "  → /scripts/restartsrv_apache_php_fpm"; /scripts/restartsrv_apache_php_fpm >>"$LOG" 2>&1 ;;
    lazy)
      host_mounted "$m" || return 1
      say "  → umount -l $m (bỏ mount kiểu lười: tách khỏi cây thư mục, kernel giải phóng khi không ai dùng)"; umount -l "$m" >>"$LOG" 2>&1 ;;
    orphans)
      u=$(users_of "$m"); [ -n "$u" ] || return 1
      if [ "$KILL_ORPHANS" != 1 ]; then
        say "  · còn tiến trình mồ côi của container trong merged — chạy lại với --kill-orphans để dừng chúng:"
        while IFS= read -r line; do say "      $line"; done <<< "$u"
        return 1
      fi
      pids=$(printf '%s\n' "$u" | awk '{print $1}' | tr '\n' ' ')
      say "  → dừng tiến trình mồ côi của container: $pids (TERM, 10 giây, rồi KILL)"
      # shellcheck disable=SC2086
      kill -TERM $pids 2>/dev/null; sleep 10
      # shellcheck disable=SC2086
      kill -KILL $pids 2>/dev/null; sleep 2
      host_mounted "$m" && { umount "$m" >>"$LOG" 2>&1 || umount -l "$m" >>"$LOG" 2>&1; } ;;
  esac
  return 0
}

go_one() {
  local c=$1 layer name step
  name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null) || { say "Không có container $c — bỏ qua"; return 0; }
  layer=$(layer_of "$c")
  say "Gỡ ${name#/} ($c), trạng thái $(docker inspect -f '{{.State.Status}}' "$c")"
  docker stop -t 20 "$c" >/dev/null 2>&1 || true
  if try_rm "$c"; then say "  ✔ đã gỡ"; return 0; fi
  say "  bận (overlay2 busy) — giải phóng mount"
  [ -n "$layer" ] || { say "  ✘ không đọc được lớp overlay — dừng"; return 2; }
  for step in umount cagefs httpd phpfpm lazy orphans; do
    release_step "$step" "$layer" || continue
    sleep 2
    if try_rm "$c"; then say "  ✔ đã gỡ sau bước $step"; return 0; fi
  done
  say "  ✘ vẫn bận — tình trạng:"
  report "$layer"
  say "  Gửi đoạn trên cho người vận hành. Cách cuối: reboot (sổ tay §2)."
  return 2
}

cmd=${1:-}; shift || true
if [ "${1:-}" = "--kill-orphans" ]; then KILL_ORPHANS=1; shift; fi
case $cmd in
  chan-doan)
    [ $# -ge 1 ] || die "thiếu tên / mã container"
    layer=$(layer_of "$1"); [ -n "$layer" ] || die "không đọc được lớp overlay của $1"
    report "$layer" ;;
  go)
    [ $# -ge 1 ] || die "thiếu tên / mã container"
    rc=0; for c in "$@"; do go_one "$c" || rc=$?; done; exit $rc ;;
  du-an)
    [ $# -eq 1 ] || die "dùng: du-an [--kill-orphans] <project> (vd ketoan, erp, zalo-hub)"
    ids=$(docker ps -aq --filter "label=com.docker.compose.project=$1")
    [ -n "$ids" ] || { say "Project $1 không còn container nào"; exit 0; }
    rc=0; for c in $ids; do go_one "$c" || rc=$?; done
    [ $rc = 0 ] && say "Xong project $1 — giờ chạy lại compose up của project đó (sổ tay §3)."
    exit $rc ;;
  *)
    sed -n '9,16p' "$0"; exit 2 ;;
esac
