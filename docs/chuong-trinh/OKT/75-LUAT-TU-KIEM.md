# OKT · 75 — Luật tự kiểm (I-8): mọi cặp blog → tenant phải tự chứng minh qua API

<!-- [2026-11-22 11:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ: "rule tối thượng trong việc luôn phải selftest selfcheck đảm bảo việc này diễn ra từ các open-pos blogid về từng tenant id qua api". Luật I-8 ở ADR-OKT-1; tệp này là đặc tả. -->

## 0. Luật

> **I-8 — Tự kiểm luôn xanh.** Một cặp **blog → tenant** chỉ được coi là "đang kết nối" khi **tự kiểm của chính cặp đó** xanh: chạy **qua đúng API** mà đường nối dùng, **bằng đúng khoá của blog**, đọc **đúng sổ của blog**. Không suy từ cấu hình, không lấy kết quả của blog khác, không lấy kết quả cũ quá 24 giờ.

Cùng hạng với I-0: không việc nào được bỏ qua tự kiểm vì "đã cấu hình đúng rồi". Bảng điểm [70](70-SCOREBOARD-KET-NOI.md) chỉ cho mức 5 khi tự kiểm của cặp đó xanh liên tục.

## 1. Khi nào chạy

| Lúc | Phần chạy | Đỏ thì |
|---|---|---|
| **Trước khi bật** gửi thật / chuyển nguồn `ketoan` / pilot một shop (I-6) | SC-1…SC-11 | **không bật** |
| **Mỗi ngày** 02:30, mọi blog có khoá riêng (cron site chính) | SC-1…SC-11 | báo đỏ ở Cổng kế toán + `wp tgs-acc status`; xem §3 |
| **Sau khi đổi** khoá / URL / tenant của blog | SC-1…SC-4 ngay lúc lưu | không lưu (khoá trỏ tenant khác) hoặc báo |
| **Sau mỗi deploy** bất kỳ repo nào trên máy chủ đó | SC-1…SC-11 cho mọi blog có khoá | dừng triển khai tiếp |
| **Mọi PR** ở open-pos, open-pos-backend, open-ketoan-bridge | SC-0 (ngoại tuyến) | PR không merge |

## 2. Các phép kiểm

Mỗi phép trả `pass` / `warn` / `fail` + dữ liệu. Phép "30 ngày" đọc sổ của blog trong 30 ngày gần nhất, chỉ đọc (I-0).

| # | Kiểm gì | Cách (API / sổ) | `fail` khi | `warn` khi |
|---|---|---|---|---|
| **SC-0** | Ngoại tuyến: test của repo + `--check=I0` | mỗi repo một lệnh `selfcheck` | test đỏ / I-0 đỏ | — |
<!-- [2026-11-23 04:10 PM Johnny Chu - Chu Hoàng Anh] OKT-TOPO-11 — SC-1 nhánh nhiều cửa hàng theo mã nối (ADR-0037, thi hành bridge 0.6.0). -->
| **SC-1** | Cấu hình của blog — **theo mô hình P-0** (82) | bizcity: khoá riêng, URL · nhiều cửa hàng: khoá cài đặt + blog **đã được kế toán nối** vào sổ (mã nối ở tenant đích) · một cửa hàng: khoá + URL | bizcity: thiếu khoá riêng mà nguồn `ketoan` · nhiều cửa hàng: blog bị thu hồi bên open-ketoan | bizcity: khoá chung (giai đoạn chuyển) · nhiều cửa hàng: blog chưa đăng ký / chờ mã nối — dừng ở SC-1, không gọi API, đơn giữ trong hàng chờ · chưa khai mô hình |
| **SC-2** | **Danh tính tenant** | `GET /api/v1/tenant` → `code`; so với mã tenant **đã lưu** của blog (`tgs_acc_tenant_code`) | khác mã đã lưu (khoá trỏ đơn vị khác) | chưa lưu mã (lần đầu: admin xác nhận rồi lưu) |
| **SC-3** | **Một tenant ↔ một blog** (cả ba mô hình) | so mã tenant của mọi blog có khoá | hai blog cùng tenant (G12) — tự tạm dừng; **trừ** blog dùng khoá chung `legacy` | blog khoá chung trùng tenant: vàng, **không** tự tạm dừng (OKT-TOPO-8) |
| **SC-4** | Quyền của khoá | `GET catalog/feed/meta`, `GET documents?search=`, `POST intake/preflight {save:false}` | một lời gọi 401 / 403 | — |
| **SC-5** | Phương thức thanh toán | mọi phương thức trên phiếu thu 30 ngày → mã sau ánh xạ có trong `GET posting/payment-methods` | có phương thức không ánh xạ được | chưa có bảng ánh xạ, đang suy từ nhãn |
| **SC-6** | Mã thuế | mọi thuế suất trên dòng bán 30 ngày → mã có trong `GET tax-codes` | có mã không tồn tại (vd `R04`) | — |
| **SC-7** | Chi nhánh + kho | `branchCode` của blog có trong `GET branches`; `GET warehouses` | chi nhánh không có | tenant không có kho |
| **SC-8** | Lý do + nhân viên | lý do xuất trên phiếu 30 ngày có trong `GET posting/reasons` | lý do không có | nhân viên chưa có ở kế toán |
| **SC-9** | **Chứng từ mẫu thật** | dựng N đơn gần nhất (mặc định 5) **bằng chính nguồn + mapper** → `POST intake/preflight {save:false}` | có phát hiện `block` | có `warn` |
| **SC-10** | Hàng chờ + trạng thái | `queue_of()`, nhật ký gửi: nhóm chờ, nhóm cũ nhất, `pending` > 24 h, `remote_error` | nhóm cũ nhất ≥ 6 ngày (sắp mất, giới hạn 7) | ≥ 3 ngày; có `pending` > 24 h; có `remote_error` |
| **SC-11** | Đồng hồ | `serverTime` của `feed/meta` so giờ máy chủ WP | lệch > 5 phút | lệch > 1 phút |
| SC-12 | Tồn (khi bộ kéo / đối chiếu có) | top 50 SKU: tồn WP ↔ `GET stock/levels` | — (giai đoạn đầu chỉ báo) | lệch |

Tự kiểm **không ghi** gì vào kế toán (preflight `save:false`) và **không ghi** vào sổ POS. Kết quả lưu theo blog (`tgs_acc_selfcheck_last`: thời điểm, từng phép, kết luận) và nhật ký.

## 3. Đỏ thì làm gì

| Phép đỏ | Hành động tự động | Người làm |
|---|---|---|
| SC-2, SC-3 (sai / trùng tenant) | **tự tạm dừng gửi** của blog (`tgs_acc_paused`); quầy **vẫn bán** (I-3), chứng từ xếp hàng | admin sửa khoá / tenant, chạy lại tự kiểm, bỏ tạm dừng |
| SC-4 (khoá bị từ chối) | không gửi lượt mới (đã có: lỗi thì thử lại) | admin cấp lại khoá |
| SC-5…SC-9 | không tự dừng; báo đỏ kèm mã thiếu | kế toán thêm mã / admin sửa ánh xạ |
| SC-10 `fail` | báo đỏ, kèm số nhóm sắp quá 7 ngày | PM / admin: gửi bù, hoặc nối lại kế toán |
| SC-0 | PR không merge | người làm PR |

## 4. Lệnh và đầu ra

```
wp tgs-acc selfcheck --shop=<id> | --all  [--samples=5] [--format=table|json]
```

- Thoát `0` = mọi phép `pass` / `warn`; `1` = có `fail`; `2` = không chạy được (thiếu bridge, lỗi tham số).
- `--format=json`: `{blog, tenant, at, verdict, checks:[{id, level, message, data}]}` — dán thẳng vào `evidence/`.
- Cổng kế toán: cột Kết nối hiện kết luận tự kiểm gần nhất + giờ chạy.

## 5. Ai làm

| Phần | Lane | Việc ([40](40-CHECKLIST.md)) |
|---|---|---|
| SC-1…SC-11, lệnh, lưu kết quả | BR | OKT-SC-1 |
| cron hằng ngày, Cổng kế toán, tự tạm dừng SC-2 / SC-3, cảnh báo, hàng chờ quá 7 ngày | BR | OKT-SC-2 |
| SC-0 mỗi repo: một lệnh chạy hết test + census | BR, TSM, POS | OKT-SC-3 |
| Bảng ánh xạ phương thức / lý do / kho để SC-5, SC-7, SC-8 hết `warn` | TSM | S001-MD3 |
| Đưa I-8 vào CANON open-ketoan (R-OKT-CONN-13) | PM / chủ | OKT-SC-4 |
