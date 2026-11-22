<!-- [2026-11-23 05:00 AM Johnny Chu - Chu Hoàng Anh] OKT-SET — chủ chốt Q-OKT-7 = (a); yêu cầu ma trận cài đặt trong bridge, mã đi đúng nhánh, open-ketoan thấy blog kết nối + ping, bridge thấy sơ đồ kết nối + ping. Mockup: mockups/okt-cai-dat-ket-noi.html. -->
# OKT · 82 — Cài đặt kết nối theo ba mô hình: ma trận lựa chọn, sơ đồ, ping

> **Luật tối thượng P-0** ([00 §0](00-ADR-OKT-1.md), [81](81-DOI-CHIEU-NGUYEN-TAC-TRIEN-KHAI.md)) + **Q-OKT-7 = (a)** (chủ, 23/11):
> **Một bản open-ketoan, một khoá chung, nhưng mỗi blog là một tenant riêng bên trong bản open-ketoan đó (tenant id ứng với blog_id). Mỗi cửa hàng có sổ riêng, cùng nằm trên một máy kế toán.**
>
> Mockup chạy được: [`mockups/okt-cai-dat-ket-noi.html`](mockups/okt-cai-dat-ket-noi.html) (4 tab: Cài đặt · Sơ đồ kết nối · Phía open-ketoan · Ma trận nhánh mã).

## 0. Một câu

Cả ba mô hình **cùng một mô hình dữ liệu: một blog = một tenant = một sổ**. Chúng chỉ khác **ai cầm khoá** và **ai đổi blog ra tenant**:

| | bizcity | Nhiều cửa hàng (selfhost) | Một cửa hàng (selfhost) |
|---|---|---|---|
| Khoá | một khoá **mỗi blog** | **một khoá cài đặt** cho cả mạng | một khoá |
| Blog → tenant | khoá của blog → tenant (như hôm nay) | open-ketoan tra **bảng đăng ký** (bản cài, blog) → tenant | khoá → tenant |
| Sổ | mỗi cửa hàng một sổ | mỗi cửa hàng một sổ, **cùng một máy kế toán** | một sổ |

**Pháp nhân (P-0 ý 3):** mỗi sổ (book) là một pháp nhân; không có pháp nhân theo tenant id. Màn Cài đặt, sơ đồ, màn Kết nối open-pos hiện **tên / mã số thuế của sổ** khi nói về pháp nhân; mã tenant chỉ hiện như mã kỹ thuật.

Vì dữ liệu giống nhau, mọi thứ đã làm theo "một blog một tenant" giữ nguyên: I-1, SC-3 (hai blog cùng tenant = đỏ), danh mục theo blog (`local`), bộ kéo C8 theo blog, đối chiếu H4, docKey `btsoft:{blog}:…`.

## 1. Ba câu hỏi của chủ

### 1.1 Trong mạng bizcity.vn, bridge cài API open-ketoan cho từng site thế nào?

1. Máy chủ bizcity đặt hằng `TGS_ACC_DEPLOYMENT = 'bizcity'` trong `wp-config.php`. Màn Cài đặt **khoá** lựa chọn ở "bizcity" — admin site không đổi được.
2. Mỗi site có một phần mềm kế toán (tenant) riêng. Kế toán của tenant đó tạo **khoá API của tenant** (open-ketoan: Hệ thống → Khoá API) rồi đưa cho admin site.
3. Admin site vào **Cổng kế toán → Cài đặt** (hoặc admin mạng ở bảng "Khai khoá của TỪNG cửa hàng"): nhập địa chỉ open-ketoan + khoá. Bridge gọi `GET /api/v1/tenant`, hiện mã tenant, admin bấm **Xác nhận tenant** (SC-2).
4. Tự kiểm chạy: SC-1 đòi khoá riêng (khoá chung = vàng trong giai đoạn chuyển 92 blog, ADR §5.3, rồi đỏ), SC-3 đỏ + tự tạm dừng nếu hai site cùng tenant.
5. Bridge ping 5 phút một lần **bằng khoá của từng site** → open-ketoan của tenant đó thấy site của mình ở màn "Kết nối open-pos".

### 1.2 Người dùng chọn "Tôi có nhiều cửa hàng" thì sao?

1. Màn Cài đặt chỉ cho chọn khi WordPress là multisite và không có hằng `bizcity`. Lựa chọn lưu ở option mạng `tgs_acc_deployment = 'chain'`.
2. Chủ chuỗi có **một** máy open-ketoan. Ở open-ketoan, quản trị tạo **khoá cài đặt** (mới — §3) và đưa cho admin mạng WordPress.
3. Admin mạng nhập địa chỉ + khoá cài đặt **một lần** ở Network Admin → Cổng kế toán. Bridge sinh **mã bản cài** (`inst_…`, lưu option mạng) và gửi kèm mọi lời gọi.
4. Bảng "Cửa hàng ↔ tenant": mỗi site một dòng. Bấm **Đăng ký** → bridge gửi `POST /api/v1/installation/blogs {blogId, name, url}` → open-ketoan ghi **Chờ duyệt**.
5. Kế toán ở open-ketoan (màn "Kết nối open-pos") **chọn tenant có sẵn hoặc tạo tenant mới** cho cửa hàng đó rồi **Duyệt**. Bridge không tự tạo tenant — tránh tạo sổ rác.
6. Từ đó mọi lời gọi của site N mang `X-Api-Key: <khoá cài đặt>` + `X-OKT-Blog: N` + `X-OKT-Install: inst_…`; open-ketoan đổi ra tenant của site N và đặt RLS đúng tenant đó. Site chưa được duyệt → `403 blog chưa nối` → bridge xếp hàng, không mất đơn (I-3).
7. Tự kiểm: SC-1 = khoá cài đặt hợp lệ + site đã được duyệt; SC-2 = tenant open-ketoan trả cho blog khớp tenant đã xác nhận; SC-3 như bizcity (hai site cùng tenant = đỏ).
8. Ping: **một** lượt cho cả bản cài (`POST /api/v1/installation/ping` liệt kê từng blog: phiên bản, hàng chờ, lần gửi cuối) → open-ketoan thấy cả chuỗi.

### 1.3 Người dùng cài một site thì sao?

1. WordPress một site → màn Cài đặt chỉ cho chọn "Tôi có một cửa hàng" (lớp bao `TGS_Acc_Site` đã chạy ở một site — bridge PR #21).
2. Nhập địa chỉ + **khoá API của tenant** (loại khoá như bizcity) → xác nhận tenant → tự kiểm. Blog luôn là #1, không cần đăng ký.
3. Muốn mở thêm cửa hàng: chuyển WordPress sang multisite rồi chọn "nhiều cửa hàng"; blog 1 giữ tenant đang có (đăng ký blog 1 vào bản cài bằng tenant đó).

## 2. Mockup (bản chữ — bản chạy được ở `mockups/okt-cai-dat-ket-noi.html`)

### 2.1 Bridge — Cổng kế toán → Cài đặt

```
Cài đặt kết nối kế toán                                         [Mockup — số liệu là ví dụ]
 1. Cài đặt │ 2. Sơ đồ kết nối │ 3. Phía open-ketoan │ 4. Ma trận nhánh mã
────────────────────────────────────────────────────────────────────────────────────────────
Bước 1  Bạn dùng mô hình nào?
  (WordPress: multisite) (Số site: 4) (TGS_ACC_DEPLOYMENT: (chưa khai))
 ┌───────────────────────────┐ ┌──────────────────────────────┐ ┌───────────────────────────┐
 │ ○ Cửa hàng trên bizcity.vn│ │ ● Tôi có nhiều cửa hàng      │ │ ○ Tôi có một cửa hàng     │
 │ Mỗi cửa hàng một phần mềm │ │ Tự cài, multisite. Một máy   │ │ Tự cài, WordPress một     │
 │ kế toán riêng, khoá riêng │ │ open-ketoan, một khoá cài    │ │ site. Một khoá, một sổ.   │
 │ từng site. Demo bizcity.  │ │ đặt; mỗi cửa hàng một sổ     │ │ ⚠ Bản cài này là multisite│
 │                           │ │ (tenant) riêng.              │ │   — chọn "nhiều cửa hàng" │
 └───────────────────────────┘ └──────────────────────────────┘ └───────────────────────────┘
Bước 2  Một máy open-ketoan, một khoá cài đặt
  Địa chỉ open-ketoan [https://ketoan.chuoi-cua-hang.vn]  Khoá cài đặt [okti_••••3a7c]  Mã bản cài [inst_01M8…QK4]
  ┃ Mỗi cửa hàng vẫn là một tenant riêng. Bridge gửi kèm X-OKT-Blog; open-ketoan đổi ra tenant.
  Blog │ Cửa hàng          │ Tenant │ Đăng ký              │ Ping   │
  #2   │ Shop A — Quận 1   │ shopa  │ ● Đã nối             │ 188 ms │
  #3   │ Shop B — Thủ Đức  │ shopb  │ ● Đã nối             │ 142 ms │
  #4   │ Shop C — Gò Vấp   │ —      │ ● Chờ kế toán duyệt  │ —      │ [Nhắc duyệt]
Bước 3  Kiểm rồi lưu
  • SC-0b mô hình nhiều cửa hàng · SC-1 khoá cài đặt + site đã đăng ký · SC-2 tenant khớp
  • SC-3 hai site cùng tenant = đỏ + tự tạm dừng · Ping 5 phút
  [Kiểm kết nối] [Lưu cài đặt]
```

### 2.2 Bridge — Sơ đồ kết nối

```
                                                             Ping lúc 08:42:10  [Ping tất cả]
┌ WordPress multisite ─────────┐
│ ● #2 Shop A   shop-a…   188ms ──┐
│ ● #3 Shop B   shop-b…   142ms ──┼──▶ ┌ open-ketoan-bridge ┐ ───▶ ┌ open-ketoan ─────────────────┐
│ ◐ #4 Shop C   shop-c…   chờ   ──┘    │ khoá cài đặt       │      │ ketoan.chuoi-cua-hang.vn     │
└──────────────────────────────┘       │ + X-OKT-Blog       │      │ tenant: shopa · shopb ·      │
                                       └────────────────────┘      │         (chờ: shop C)        │
                                                                   └──────────────────────────────┘
Từng cửa hàng:   Blog │ open-ketoan │ Tenant │ Ping │ Tự kiểm │ Hàng chờ
Từng open-ketoan: Máy │ Phiên bản │ Ping │ Đồng hồ lệch │ Số tenant nối (2 / 3)
```
bizcity: N site → N tenant (một hay nhiều máy, nhóm theo địa chỉ). Một cửa hàng: 1 → 1.

### 2.3 open-ketoan — Hệ thống → Kết nối open-pos

```
Bản cài đang nối
  Mã bản cài     │ Site                  │ Kiểu khoá             │ Cửa hàng │ Ping cuối         │ Bridge
  inst_01M8…QK4  │ chuoi-cua-hang.vn     │ khoá cài đặt          │ 3        │ 08:42:10 · 96 ms  │ 0.9.3
  —              │ shop-x.bizcity.vn     │ khoá riêng của tenant │ 1        │ 08:40:55 · 121 ms │ 0.9.3
Cửa hàng ↔ tenant
  Bản cài       │ Blog │ Cửa hàng         │ Tenant │ Trạng thái        │ Ping cuối │ Chờ định khoản │
  inst_01M8…    │ #2   │ Shop A — Quận 1  │ shopa  │ ● Đang nối        │ 08:42:10  │ 0              │
  inst_01M8…    │ #3   │ Shop B — Thủ Đức │ shopb  │ ● Đang nối        │ 08:42:10  │ 3              │
  inst_01M8…    │ #4   │ Shop C — Gò Vấp  │ —      │ ● Chờ duyệt       │ —         │ —              │ [Chọn / tạo tenant rồi duyệt]
  khoá riêng    │ #7   │ shop-x.bizcity   │ shopx  │ ● Ping trễ 26 ph  │ 08:16:02  │ 0              │
```

## 3. Việc phía open-ketoan (lane OK) — để (a) chạy được

Hôm nay một khoá API thuộc đúng một tenant (`api_keys.tenant_id`, RLS theo tenant của khoá — `packages/platform/src/core/auth.ts:266-285, :352`). (a) cần thêm, **không** bỏ luật đó:

| # | Việc | Ghi chú |
|---|---|---|
| K-1 | Bảng `installations` (id, mã `inst_…`, tên, site_url, key_hash, trạng thái, tạo bởi) — **khoá cài đặt** là loại khoá riêng, không thuộc tenant | quản trị hệ thống open-ketoan (không phải admin một tenant) tạo |
| K-2 | Bảng `installation_blogs` (installation_id, blog_id, tên, url, tenant_id NULL, trạng thái `pending/active/revoked`, last_ping_at, last_ping_ms, bridge_version, queue, pending_docs) — UNIQUE (installation_id, blog_id), UNIQUE tenant_id | một tenant chỉ nối một blog (I-1) |
| K-3 | Xác thực: `X-Api-Key` là khoá cài đặt + `X-OKT-Blog` → tra K-2 → nếu `active` đặt **tenant của dòng đó** cho yêu cầu (RLS như cũ); thiếu header → 400; chưa duyệt → 403 `BLOG_NOT_LINKED` | quyền = quyền khoá tích hợp của tenant đó |
| K-4 | `POST /api/v1/installation/blogs` (đăng ký), `GET /api/v1/installation/blogs` (bridge đọc trạng thái) | |
| K-5 | `POST /api/v1/installation/ping` (cả bản cài) và `POST /api/v1/connection/ping` (khoá tenant — bizcity / một cửa hàng) | lưu thời điểm, độ trễ, phiên bản, hàng chờ |
| K-6 | Màn **Hệ thống → Kết nối open-pos**: bản cài, cửa hàng ↔ tenant, duyệt (chọn / tạo tenant), thu hồi, ping trễ > 15 phút = vàng | §2.3 |
| K-7 | Sửa CANON R-OKT-CONN-2/3 + R-TEN: "tenant đi theo khoá **hoặc** theo (khoá cài đặt, blog) đã duyệt" | OKT-TOPO-10 |

## 4. Việc phía bridge

| # | Việc | Ghi chú |
|---|---|---|
| B-1 | `TGS_Acc_Profile::current()` = `bizcity` \| `chain` \| `single`: hằng `TGS_ACC_DEPLOYMENT` thắng → option mạng `tgs_acc_deployment` → một site thì `single`. **Không** đoán từ khoá | thay `TGS_Acc_Site::topology()` |
| B-2 | Màn Cài đặt theo §2.1 (Network Admin cho `chain`; site cho `bizcity` / `single`); khoá lựa chọn theo môi trường | mockup tab 1 |
| B-3 | `TGS_Acc_Api_Client::for_blog()` theo nhánh: `chain` → khoá cài đặt + `X-OKT-Blog` + `X-OKT-Install`; còn lại như hôm nay | một chỗ |
| B-4 | Đăng ký cửa hàng (`chain`): nút Đăng ký / Nhắc duyệt; đọc trạng thái từ K-4; `403 BLOG_NOT_LINKED` → xếp hàng, SC-1 vàng | |
| B-5 | Tự kiểm theo nhánh: SC-0b in mô hình; SC-1 theo bảng ở mockup tab 4; SC-3 **giữ** luật một blog một tenant ở cả ba | sửa đặc tả 75 |
| B-6 | Ping 5 phút: `chain` một lượt K-5 cho cả bản cài; `bizcity` mỗi blog bằng khoá của nó; `single` blog 1. Kết quả lưu để vẽ sơ đồ | |
| B-7 | Màn **Sơ đồ kết nối** (§2.2): site → bridge → máy open-ketoan → tenant, độ trễ từng cạnh, nút Ping tất cả, bảng từng cửa hàng và từng máy | mockup tab 2 |
| B-8 | **Lỗi trái P-0 đang chạy** (OKT-TOPO-8): hôm nay mạng dùng khoá chung (bizcity đang chuyển, hoặc selfhost trước khi có K-1…K-3) có **mọi blog cùng một tenant** → SC-3 + `enforce()` tự tạm dừng **cả mạng**. Sửa ngay: blog dùng khoá chung (key_mode `legacy`) không bị tự tạm dừng vì SC-3 — chỉ vàng "khoá chung đang dồn mọi site vào một tenant; chuyển sang khoá riêng (bizcity) hoặc khoá cài đặt (chuỗi)" | độc lập với K-1…K-7 |

## 5. Ma trận kiểm thử (mỗi ô một ca chạy thật)

| Ca | bizcity | Nhiều cửa hàng | Một cửa hàng |
|---|---|---|---|
| Chọn mô hình: lựa chọn bị khoá đúng theo môi trường / hằng | ☐ | ☐ | ☐ |
| Khai khoá → xác nhận tenant → tự kiểm xanh | ✅ (hôm nay, khoá theo blog) | ☐ (cần K-1…K-3) | ✅ (bridge #21) |
| Đăng ký cửa hàng → chờ duyệt → kế toán duyệt → gửi được | — | ☐ | — |
| Site chưa duyệt bán hàng → xếp hàng, duyệt xong gửi bù, 0 trùng | — | ☐ | — |
| Hai site cùng tenant → SC-3 đỏ + tự tạm dừng | ✅ (ma trận 65 M8) | ☐ | — |
| Khoá chung (legacy) không bị tự tạm dừng cả mạng (B-8) | ☐ | ☐ | — |
| Ping: open-ketoan thấy blog, trạng thái, lần ping cuối | ☐ | ☐ | ☐ |
| Sơ đồ kết nối: độ trễ từng site, từng máy; site hỏng hiện đỏ | ☐ | ☐ | ☐ |
| Ca bán chuẩn trước / sau giống hệt (I-0) | ✅ | ☐ | ☐ |

## 6. Lộ trình

| Mốc | Việc | Repo |
|---|---|---|
| **S0** (ngay) | B-8 sửa tự tạm dừng sai với khoá chung | bridge |
| S1 | B-1 hồ sơ khai rõ + B-5 SC-0b/SC-1 theo nhánh | bridge |
| S2 | K-1…K-5 khoá cài đặt, đăng ký blog, ping | open-ketoan |
| S3 | B-3, B-4, B-6 bridge theo nhánh `chain` | bridge |
| S4 | B-2, B-7 màn Cài đặt + Sơ đồ; K-6 màn Kết nối open-pos | bridge, open-ketoan |
| S5 | Ma trận §5 xanh cả ba cột; K-7 CANON | cả hai |
