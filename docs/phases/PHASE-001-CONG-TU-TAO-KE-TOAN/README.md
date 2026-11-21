# PHASE-001 — Cổng tự tạo phần mềm kế toán (open.bizcity.vn)
<!-- [2026-11-21 06:33 PM Johnny Chu - Chu Hoàng Anh] P001-INIT — mở phase 001: cổng tự tạo site kế toán trên bộ máy Frappe/ERPNext đã cài. -->

> **Trạng thái:** Đã chốt hướng. Chưa có mã cổng. **Bộ máy đã chạy** (2026-11-21): ERPNext v15.125.0, `docker compose -p erp`, cổng `127.0.0.1:8090`. Site thử `erp.btnet.vn` đã tạo xong nhưng đang **502 qua Cloudflare**.
> **Chủ phase:** chủ dự án (founder). Quyết định theo [phương án tốt nhất](#5-quyết-định-đã-chốt), không chờ người ngoài.

## 1. Mục tiêu (một câu)

Người lạ vào **open.bizcity.vn** và trong **dưới 5 phút** (v1), dưới 1 phút (khi có kho site dựng sẵn ở W3), có một phần mềm kế toán riêng chạy được, đăng nhập bằng email của chính họ. Không cần ai trong đội phải làm gì.

## 2. Ngoài phạm vi phase này

- Thu tiền và gói trả phí: PHASE-002, đi qua ví Bizcity.
- Tên miền riêng của khách, ví dụ `ketoan.congtya.vn`: PHASE-003.
- Sửa nghiệp vụ kế toán: thuộc engine (ERPNext hoặc open-ketoan), không thuộc Open Setup.
- Bản địa hoá Việt Nam cho ERPNext (hệ thống tài khoản theo TT200/TT133, mẫu chứng từ): làm riêng, có thể là app Frappe `bizcity_vn`. Ghi ở rủi ro R-4.

## 3. Luồng và màn hình

| # | Màn | Nội dung | Ghi chú |
|---|---|---|---|
| 1 | **Đăng ký** | Họ tên · Tên công ty · Số điện thoại · Email · **Tên miền mong muốn** (`____.btnet.vn`, kiểm còn trống ngay khi gõ) · Tỉnh/thành · ☑ đồng ý điều khoản | Tự gợi ý slug từ tên công ty, bỏ dấu (`Công ty An Phát` → `anphat`). Ô đầu tiên luôn có sẵn gợi ý, theo tinh thần "ok = 1" |
| 2 | **Xác nhận email** | Nhập mã 6 số gửi qua email; mã hết hạn sau 15 phút | Chặn tạo site bằng email ảo |
| 3 | **Đang tạo** | Thanh tiến trình theo 5 bước ở §4, đẩy trạng thái bằng SSE; đóng tab rồi mở lại vẫn thấy tiến trình qua link trong email | Không hỏi thêm câu nào giữa chừng |
| 4 | **Xong** | Nút "Mở phần mềm kế toán" → `https://<slug>.btnet.vn`; email "Đặt mật khẩu" của Frappe đã được gửi | Lần đầu đăng nhập, Setup Wizard của ERPNext điền sẵn Việt Nam / VND / tên công ty |
| 5 | **Lỗi** | Câu dễ hiểu kèm mã việc (`JOB-…`) và nút "Thử lại" | Phía sau đã dọn phần tạo dở (R-JOB-1) |

## 4. Các bước tạo site (provisioner)

Script `ops/provision-tenant.sh <slug> <root> <email> <tên công ty>` chạy bằng root qua sudo. Mỗi bước in **một dòng JSON** `{"step":n,"ok":true|false,"msg":"…"}` để cổng đọc và hiển thị.

| Bước | Việc | Lệnh | Dọn khi hỏng |
|---|---|---|---|
| 1 | Kiểm tham số + slug còn trống | regex R-SLUG-1; `ls sites/`; `uapi DomainInfo list_domains` | — |
| 2 | Tạo site + cài ERPNext | `bench new-site … --install-app erpnext`; `set-config host_name`; `enable-scheduler` | `bench drop-site --no-backup --force` |
| 3 | Tạo tài khoản quản trị cho khách | `bench --site … add-system-manager <email> --first-name … --send-welcome-email` | (đi cùng bước 2) |
| 4 | Gắn tên miền trong cPanel | `uapi SubDomain addsubdomain` | `uapi SubDomain delsubdomain` |
| 5 | Proxy Apache | ghi `userdata/{std,ssl}/2_4/vibeyeuc/<site>/proxy.conf` → `rebuildhttpdconf` → **`httpd -t` phải đạt** rồi mới `restartsrv_httpd`; sau đó `curl` kiểm `/login` = 200 qua Host header | xoá 2 thư mục userdata, rebuild |

`Administrator` của mỗi site giữ cho đội vận hành, mật khẩu ghi vào `/root/frappe-sites.txt` (quyền 600). Khách dùng tài khoản System Manager mang email của mình.

## 5. Quyết định đã chốt

| Mã | Quyết định | Vì sao |
|---|---|---|
| **D001-1** — engine | **ERPNext v15** trên Frappe (đã chạy). Cổng gọi engine qua giao diện `provision / suspend / resume / backup / drop`, nên open-ketoan cắm vào được sau | Có ngay hôm nay; không khoá cổng vào một engine |
| **D001-2** — tên miền khách | **`<slug>.btnet.vn`** mỗi khách là một subdomain cPanel (đã kiểm: `uapi` trả `status: 1`). Thêm `bizcity.vn` làm tên miền gốc thứ hai **sau khi** xác nhận nó nằm trong tài khoản cPanel `vibeyeuc` và trên Cloudflare (W0-3) | Subdomain cPanel thắng wildcard WordPress; SSL Universal của Cloudflare phủ sẵn `*.btnet.vn`. **Không** dùng wildcard 2 cấp (`*.kt.btnet.vn`) vì cần chứng chỉ trả phí |
| **D001-3** — quyền | Cổng chạy user `opensetup`. Sudoers chỉ cho phép đúng `/opt/open-setup/ops/provision-tenant.sh` và `ops/tenant-ctl.sh` | R-PRIV-1: cổng web bị chiếm cũng không có root |
| **D001-4** — công nghệ cổng | **Node 20 + TypeScript + Fastify + SQLite** (`better-sqlite3`, WAL). Giao diện là HTML render từ server cộng một chút JS. Chạy bằng systemd ở `127.0.0.1:8095`, **không** chạy trong Docker | Cùng ngôn ngữ với open-ketoan; một tệp CSDL; tránh lỗi `overlay2 busy` của Docker trên VPS này; cổng cần gọi `sudo` trên máy chủ |
| **D001-5** — hàng đợi | Bảng `jobs` trong SQLite, **một worker, chạy tuần tự** | `bench new-site` tốn CPU/RAM; chạy song song dễ đụng khoá CSDL. 3–5 phút mỗi site là chấp nhận được cho v1 |
| **D001-6** — xác nhận danh tính | **Email OTP 6 số** ở v1. Zalo OTP qua zalo-hub ở v1.1 | Đơn giản, không phụ thuộc ZNS (đang chờ) |
| **D001-7** — dùng thử | **30 ngày** miễn phí. Hết hạn thì site chuyển **chỉ đọc** (maintenance mode + `allow_reads_during_maintenance`). Sau 90 ngày không gia hạn: sao lưu → kiểm bản sao lưu → xoá | Kế toán cần trọn một chu kỳ khoá sổ tháng mới đánh giá được; R-DATA-1 |
| **D001-8** — trần | Tối đa **1 site dùng thử / email / số điện thoại**; **3 lượt / IP / ngày**; trần tổng `MAX_TENANTS=200` (RAM trống 17 GB, mỗi site chủ yếu tốn CSDL và đĩa). Gần trần thì báo đội vận hành | R-ABUSE-1 |
| **D001-9** — slug cấm | `www mail webmail ftp cpanel whm api admin open erp ketoan kiot app apps static cdn ns1 ns2 smtp pop imap test demo` + mọi subdomain đang có trong cPanel | Tránh đè tên miền hệ thống |
| **D001-10** — MariaDB | Đổi image `mariadb:11.8` sang **`mariadb:10.6`** **trước khi** có khách thật (W0-2). Phải xoá volume `erp_db-data` và tạo lại `erp.btnet.vn` | Frappe v15 cảnh báo "11.8 not yet tested"; bây giờ mới có một site thử nên đổi rẻ, sau này rất đắt |
| **D001-11** — kho site dựng sẵn | W3: luôn giữ **3 site trống** (`pool-xx.local`). Khi có khách thì đổi tên thư mục site + `host_name`, thêm user, gắn tên miền | Thời gian giao từ 3–5 phút xuống dưới 1 phút |

## 6. Các đợt việc

| Đợt | Việc | Xong khi |
|---|---|---|
| **W0 — Gỡ chặn bộ máy** | W0-1 sửa 502 ở `erp.btnet.vn` (xem [CAI-FRAPPE §6](../../van-hanh/CAI-FRAPPE-TREN-VPS.md#6-sửa-502)) · W0-2 đổi sang MariaDB 10.6 (D001-10) · W0-3 kiểm `bizcity.vn` có trong cPanel `vibeyeuc` không · W0-4 bật cPHulk / SSH key (có dò mật khẩu root) | `https://erp.btnet.vn/login` = 200, đăng nhập được, Setup Wizard chạy xong |
| **W1 — Provisioner** | `ops/provision-tenant.sh` theo §4: JSON từng bước, `httpd -t` trước khi restart, dọn khi lỗi · `ops/tenant-ctl.sh suspend|resume|backup|drop` · sudoers | Tạo thử 3 site liên tiếp, giết giữa chừng 1 site → không còn gì mồ côi; các tham số độc đều bị từ chối |
| **W2 — Cổng v1** | Fastify + SQLite: form §3, kiểm slug trực tiếp, email OTP, bảng `tenants`/`jobs`, worker, SSE tiến trình, email "xong" · subdomain `open.bizcity.vn` + proxy → 8095 · systemd unit | Một người ngoài đội tự tạo được site từ điện thoại, không cần hỏi ai |
| **W3 — Nhanh + bền** | Kho site dựng sẵn (D001-11) · sao lưu hằng đêm `bench --site all backup --with-files` + đẩy ra ngoài VPS · cron hết hạn dùng thử (D001-7) | Giao site < 60 giây; có bản sao lưu ngoài VPS của đêm qua |
| **W4 — Trang quản trị** | `open.bizcity.vn/admin` (chỉ đội): danh sách site, trạng thái, hạn dùng, nút khoá/mở/sao lưu/xoá, nhật ký việc | Đội vận hành không phải SSH cho việc thường ngày |

## 7. Nghiệm thu phase

1. Người ngoài đội, trên điện thoại, từ lúc mở `open.bizcity.vn` tới lúc vào được màn kế toán: **≤ 5 phút**, không hỏi ai.
2. Hai doanh nghiệp tạo cách nhau 1 phút: không ai thấy dữ liệu của người kia; mỗi bên một CSDL riêng.
3. Thử `slug` = `abc;reboot`, `../x`, `www`, `ketoan`, một subdomain đã có → đều bị từ chối, cả ở cổng **và** ở script.
4. Tắt nguồn giữa bước 2 → hệ tự dọn; người dùng thấy câu "Chưa tạo xong, bấm thử lại" kèm mã việc.
5. Site hết hạn: vẫn đăng nhập và xem được, không ghi được; có bản sao lưu.

## 8. Rủi ro

| Mã | Rủi ro | Cách giữ |
|---|---|---|
| R-1 | VPS dùng chung với zalo-hub và WordPress. ERPNext ăn RAM | Giới hạn worker gunicorn; theo dõi `free -h`; trần D001-8; khi tải tăng thì tách VPS riêng cho bộ máy kế toán |
| R-2 | Docker `overlay2 busy` trên VPS này | **Không** `systemctl restart docker`; cổng không chạy trong Docker (D001-4) |
| R-3 | `restartsrv_httpd` hỏng thì **tất cả** website trên máy chết | Luôn `httpd -t` trước khi restart (W1) |
| R-4 | ERPNext chưa có chuẩn kế toán VN | Phase riêng: app `bizcity_vn` (hệ thống TK, mẫu chứng từ, hoá đơn điện tử), hoặc chuyển engine sang open-ketoan |
| R-5 | Lạm dụng tạo site hàng loạt | R-ABUSE-1, OTP, trần tổng |
