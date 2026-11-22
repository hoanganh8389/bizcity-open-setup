# OKT · 70 — Scoreboard kết nối open-pos → open-pos-backend → open-ketoan

<!-- [2026-11-22 11:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ yêu cầu scoreboard đánh giá kết nối open-pos (blog) qua open-pos-backend tới open-ketoan (tenant), từ góc kiến trúc / system builder / domain translator; chấm bằng bằng chứng (I-7), đo lại mỗi mốc. Luật tự kiểm ở 75. -->

> **Điểm hiện tại (22/11/2026 07:50 PM): 55,8 %** · **mức cần cho pilot: 72,5 %** · thang 0–5 có trọng số, chấm theo bằng chứng (I-7).
> Bảng này **không** giữ trạng thái việc (trạng thái ở [40](40-CHECKLIST.md)); nó đo **khả năng của đường nối** và trỏ việc sẽ nâng điểm. Đo lại sau mỗi mốc, ghi một dòng ở §6.

## 0. Thang điểm

| Mức | Nghĩa | Bằng chứng tối thiểu |
|---|---|---|
| 0 | chưa có | — |
| 1 | có thiết kế / quyết định | tài liệu đã merge |
| 2 | có mã | PR đã merge |
| 3 | có test chạy bằng một lệnh | tên test + số phép kiểm |
| 4 | chạy thật trên môi trường thử | bản ghi `evidence/` có lệnh, đầu ra, người, giờ |
| 5 | chạy trên shop thật, **tự kiểm (75) xanh liên tục** | lịch sử tự kiểm của cặp blog → tenant |

Điểm = Σ (mức ÷ 5 × trọng số) ÷ Σ trọng số. Trọng số theo **rủi ro sai tiền / sai sổ**: tiền, thuế, định danh nặng hơn tiện ích. Cột "Pilot" là mức cần trước khi bật một shop thật.

## 1. Ba góc nhìn

**Kiến trúc — ai sở hữu gì trên đường nối**

```
 open-pos (blog)                open-pos-backend (tsm)            open-ketoan-bridge                open-ketoan (tenant)
 ──────────────                 ──────────────────────            ──────────────────                ────────────────────
 POS cũ / POS React             danh mục, giá, thuế, ĐVT,         nguồn đọc sổ (chỉ đọc)            intake + preflight
 ghi local_ledger* (I-0)  ───►  bảng theo blog, bộ kéo C8   ◄───  mapper → chứng từ          ───►   định khoản (posting)
 tồn tính từ sổ local           bảng ánh xạ {p}tgs_okt_map        sự kiện → hàng chờ → gửi          feed danh mục / giá
                                quản trị shop                     kéo trạng thái, tạm dừng   ◄───   trạng thái chứng từ
```

Chiều **bán** (sổ → kế toán) đi qua bridge, **sau** khi đơn đã ghi. Chiều **danh mục** (kế toán → blog) đi qua bộ kéo của open-pos-backend, chỉ cho blog nguồn `ketoan`. POS **không** gọi kế toán khi bán (I-3).

**System builder — đường nối hỏng ở đâu thì ai thấy**

| Chỗ hỏng | Triệu chứng | Ai thấy hôm nay | Phải thấy bằng |
|---|---|---|---|
| Khoá trỏ nhầm tenant | chứng từ vào sổ của đơn vị khác | không ai | tự kiểm SC-2 (`/tenant`) |
| Hai blog chung tenant | sổ trộn hai shop | không ai | tự kiểm SC-3 |
| Mã phương thức / thuế / lý do / kho không có ở tenant | chứng từ `remote_error`, tiền treo | kế toán, muộn | tự kiểm SC-5…SC-8 trước khi gửi |
| Hàng chờ quá 7 ngày | mất chứng từ | không ai | tự kiểm SC-10, cảnh báo |
| Tồn lệch WP ↔ kế toán | giá vốn sai, kiểm kê vênh | kiểm kê cuối kỳ | đối chiếu SC-12 |

**Domain translator — một khái niệm, hai ngôn ngữ**

| open-pos (sổ local) | open-ketoan (chứng từ) | Luật dịch | Rủi ro |
|---|---|---|---|
| Đơn bán = phiếu **10** + phiếu xuất **2** (dòng hàng) + phiếu thu **7** | `sale` + `customer_payment` (hoặc `sale.payments`, S002-17) | khoá theo id phiếu 10; phiếu thu trỏ `invoiceDocKey` | gộp sai → tiền ghi hai lần (doc 21 B1) |
| Đơn giá **gồm VAT** trên kệ; sổ lưu trước thuế đã làm tròn | `unitPrice`, `amountBeforeTax`, `taxAmount` trước VAT | một hàm tiền, tổng khớp tới đồng (I-5) | lệch vài đồng |
| Thuế suất số (8, 10, 3,5…) | mã thuế (`R08`, `R10`, `KCT`…) | bảng mã cố định | 3,5 % → `R04` không có |
| ĐVT bán (thùng) + SL | ĐVT gốc + SL gốc + `unitRatio` | luôn gửi ĐVT gốc | mã tự tạo mang sai ĐVT |
| Nhãn hình thức thanh toán ("QR VTB CT") | mã phương thức (`QR`, `CK`…) | **bảng ánh xạ lưu sẵn** (I-4) | suy từ nhãn → mã không tồn tại |
| Khách = SĐT trên phiếu | đối tượng (`partner.code`) | mã đối tượng lưu (I-4) | đổi SĐT → hai đối tượng |
| Blog | tenant + chi nhánh (`branchCode`) | khoá theo blog, chi nhánh khai theo blog | trùng tenant |
| `warehouse_id` của WP | `warehouseCode` | bảng ánh xạ kho | tenant không có kho |
| Lý do xuất POS (`XBA`, `XTA`…) | lý do của tenant (`XBA`, `XTA1.4`…) | bảng ánh xạ lý do | mã lệch |
| Bill Z | `internalOnly` | cờ `is_z` | nguồn sổ POS chưa quyết |
| Phiếu hoàn **11**; đổi trả (phiếu thu kỹ thuật) | `sale_return`; `offsets` | trỏ đơn gốc; đối trừ không phải tiền | đối trừ thành tiền thật |
| Tồn = cộng dòng sổ đã duyệt | tồn sau định khoản | đối chiếu theo SKU | không có đối chiếu |

## 2. Điểm theo miền

| Miền | Tên | Trọng số | Điểm |
|---|---|---|---|
| A | Định danh & kết nối | 12 | 75 % |
| B | Danh mục hàng hoá | 14 | 29 % |
| C | Giá | 8 | 57 % |
| D | Thuế | 5 | 56 % |
| E | Bán hàng | 18 | 64 % |
| F | Thanh toán | 14 | 50 % |
| G | Trả hàng / đổi trả | 5 | 52 % |
| H | Tồn kho | 11 | 53 % |
| I | Khách hàng | 3 | 20 % |
| J | Nhân viên | 1 | 40 % |
| K | Độ bền khi kế toán tắt / dừng | 12 | 70 % |
| L | Quan sát (I-6) | 4 | 60 % |
| M | Bảo mật | 2 | 20 % |
| N | Kiểm chứng | 9 | 69 % |

## 3. Bảng tiêu chí

| # | Tiêu chí | Trọng số | Mức | Pilot | Đạt | Bằng chứng | Thiếu | Việc |
|---|---|---|---|---|---|---|---|---|
| A1 | Khoá + URL theo blog; không khoá chung cả mạng (I-1) | 4 | **4** | 4 | ✅ | setup-lat-doc gắn khoá + URL riêng blog A, blog B không khoá; feed/meta 200 trong WP — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | S002-C0 |
| A2 | Chứng minh được khoá của blog trỏ **đúng tenant** (gọi `/api/v1/tenant`, so mã lưu) | 3 | **4** | 4 | ✅ | wp tgs-acc selfcheck trong WP: SC-2 tenant shopa đúng mã đã xác nhận — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | OKT-SC-1 |
| A3 | Một tenant ↔ một blog: phát hiện hai blog chung tenant (G12) | 3 | **3** | 4 | — | SC-3 bản đồ blog → tenant, test 41/41 (bridge PR #12) | chưa chạy trong WP; tự tạm dừng ở OKT-SC-2 | OKT-SC-1 |
| A4 | Chi nhánh khai theo blog, mã sai thì báo, không tạo chi nhánh trống | 2 | **4** | 4 | ✅ | chứng từ mang CN01 (tgs_acc_branch_code), kế toán nhận + định khoản — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | S002-C0 |
| B1 | Định danh mặt hàng ổn định: `sku` + `itemId` lưu ở blog, đổi mã không mất dòng (I-4) | 4 | **1** | 3 | — | 81 F1–F15 | bộ kéo C8 chưa có; `itemId` chỉ khi có `TGS_Item_Variant` | S001-C8 |
| B2 | ĐVT: gửi ĐVT gốc, SL theo ĐVT gốc, tỉ lệ quy đổi | 3 | **3** | 4 | — | PR #7 (`unit = dvt_goc`), test 17 | — | S002-C5 |
| B3 | Đơn tới trước mã (mã trơn): không mất barcode / ĐVT của shop | 2 | **1** | 3 | — | Q001-19 chốt | S001-C8b chưa làm | S001-C8b |
| B4 | Kéo danh mục theo blog, chỉ cột `erp`, đối chứng lệch 0 | 4 | **1** | 3 | — | 81 đặc tả | chưa có mã | S001-C8 |
| B5 | Nhóm hàng / nhóm hạch toán | 1 | **1** | 2 | — | preflight IN-MD-004 | chưa có ánh xạ | S001-C18 |
| C1 | Giá gồm VAT → dòng trước VAT + thuế, tổng khớp tới đồng (I-5) | 5 | **4** | 4 | ✅ | đơn 11.000 gồm VAT → chứng từ 10.000 + 1.000, kế toán định khoản 0 lỗi, tổng 11.000 — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | mới một đơn, một thuế suất | S002-C5 |
| C2 | Bảng giá theo chi nhánh khai theo blog, lùi bảng giá công ty, DM14 ở bộ kéo | 3 | **1** | 3 | — | Q001-20, D002-8 | chưa có mã | S001-C8c |
| D1 | Mã thuế gửi đi **có trong danh mục tenant** (R00/R05/R08/R10/KCT) | 3 | **4** | 4 | ✅ | R10 có ở tenant; SC-6 trong WP khớp; định khoản 0 lỗi — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | thuế 3,5 % chờ kế toán chốt mã | OKT-SC-1 |
| D2 | Đổi mã thuế sau 2026-12-31 | 2 | **1** | 3 | — | S001-K16 | chưa làm, **hạn 2026-12-31** | S001-K16 |
| E1 | Nguồn phiếu bán đọc thẳng sổ POS, không cần tgs-bc-tk, chỉ đọc (I-0) | 4 | **4** | 4 | ✅ | đơn POS cũ → nguồn sổ POS dựng phiếu bán trong WP, không cần tgs-bc-tk — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | S002-C2 |
| E2 | `docKey` bất biến + `version`; gửi lại không trùng | 4 | **3** | 4 | — | nhật ký gửi + `tests/status-test.php` 21 phép | — | S002-C9 |
| E3 | Sửa / xoá đơn sau khi gửi → phiên bản mới / huỷ | 3 | **2** | 4 | — | `deleted_keys()`, `changed_before()` | chưa có test riêng | S002-C9 |
| E4 | Lý do xuất POS → mã lý do tenant | 2 | **3** | 3 | ✅ | kind reason trong {p}tgs_okt_map; gợi ý XTA → XTA1.4 khi đúng một mã khớp; trọn vòng okt-thu (bridge PR #13) | chưa chạy trong WP | S001-MD3 |
| E5 | Bill Z / chứng từ nội bộ (`internalOnly`) | 1 | **2** | 3 | — | mapper `is_z` | nguồn sổ POS quyết `is_z` chưa kiểm | S002-C5 |
| E6 | Không gọi HTTP trong request bán (I-3) | 4 | **4** | 4 | ✅ | đo request bán HTTP thật trên WP (Apache mod_php): trước 16–30 s khi kế toán tắt / treo → sau 250–1.491 ms, gửi nền (bridge PR #16) | máy chủ thật: kiểm loại PHP (FPM / LiteSpeed / mod_php) và loopback | S002-C2 |
| F1 | Mã phương thức **lưu sẵn**, không suy từ nhãn (I-4) | 4 | **3** | 4 | — | {p}tgs_okt_map + TGS_Okt_Map (open-pos-backend PR #39, test 34/34); bridge dịch mã khi dựng (bridge PR #13, test 18/18); trọn vòng okt-thu: QR-VTB-CT → QR | chưa chạy trong WP; nhãn lạ (MOMO…) phải xác nhận tay | S001-MD3 |
| F2 | Phiếu thu ghép đúng hoá đơn (`invoiceDocKey` = id phiếu loại 10) | 3 | **4** | 4 | ✅ | phiếu thu btsoft:2:receipt:3 trỏ btsoft:2:sale:2, kế toán định khoản thu tiền BT26-0000002 — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | S002-C6 |
| F3 | Thanh toán tách nhiều phương thức | 2 | **2** | 3 | — | `split_parent` | chưa test | S002-17 |
| F4 | Ghi nợ, thu sau, đúng ngày quỹ | 2 | **2** | 3 | — | phiếu thu riêng theo ngày | chưa test | S002-17 |
| F5 | Một đơn một chứng từ (`sale.payments`) | 2 | **1** | 2 | — | doc 21 thiết kế | sau lát dọc | S002-17 |
| F6 | Tiền mặt dư làm tròn | 1 | **1** | 3 | — | Q002-3 | chờ kết quả L7 | S002-C7 |
| G1 | Phiếu hoàn (loại 11) → `sale_return`, trỏ đơn gốc | 3 | **3** | 4 | — | test 38 gồm phiếu hoàn | — | S002-C9 |
| G2 | Đổi trả: đối trừ (`offsets`), không thành tiền thật | 2 | **2** | 3 | — | `offsets_by_sale()` | chưa test | S002-C9 |
| H1 | Tồn ở WP tính từ sổ local; bán / nhập đúng (POS không đổi, I-0) | 3 | **4** | 4 | ✅ | tồn WP 10 → 9 sau một đơn, nhập qua đường nhập thật — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa đối chiếu với tồn kế toán | S002-C2 |
| H2 | Kho WP ↔ `warehouseCode` của tenant | 3 | **4** | 4 | ✅ | warehouse-sync.php: phân kho chép theo kết nối của từng blog (I-1), SC-7 kiểm kho mặc định (bridge PR #18); đã chạy thật: đơn POS không ghi kho → kế toán ghi vào kho mặc định KCN01 (movement + bút toán) | chưa chạy ở site thật; Tính giá vốn tháng có kho chưa chạy (phiếu nhập lát dọc chưa lên kế toán); I-2: blog local chưa được miễn sync | OKT-SC-1 |
| H3 | Nhập mua / trả NCC / chuyển kho / kiểm kê → chứng từ | 2 | **2** | 3 | — | mapper `supplier_doc`, `adjust`, `gt-in/out` | ngoài lát dọc | PHASE-001 |
| H4 | Đối chiếu tồn WP ↔ kế toán theo SKU | 2 | **0** | 3 | — | kế toán có `/inventory/reconcile` | chưa có | OKT-SC-2 |
| H5 | Thiếu tồn không chặn quầy; kế toán ghi cờ | 1 | **1** | 3 | — | ADR D001-18, 28 §4 | chưa kiểm | S002-C2 |
| I1 | Đối tượng theo **mã lưu**, không theo SĐT (I-4) | 2 | **1** | 3 | — | mapper dùng SĐT làm `partner.code` | trái I-4; khách đổi SĐT tách hai đối tượng | S001-MD3 |
| I2 | Danh bạ khách theo blog (Q001-14) | 1 | **1** | 3 | — | Q001-14 chốt | chưa có mã | PHASE-001 |
| J1 | Nhân viên bán → `employee` của tenant | 1 | **2** | 3 | — | mapper `employee()` | chưa đối chiếu danh mục tenant | OKT-SC-1 |
| K1 | Kế toán tắt: vẫn bán, hàng chờ 7 ngày, gửi bù theo thứ tự | 4 | **4** | 4 | ✅ | kế toán tắt / treo trên WP thật: đơn vào hàng chờ, nối lại → hàng chờ 0, mọi chứng từ v1, 0 trùng (bridge PR #16) | chưa chạy cron thật (DISABLE_WP_CRON); chưa chạy trên shop thật | S002-C10 |
| K2 | Tạm dừng / bỏ tạm dừng theo shop, gửi bù không trùng | 2 | **3** | 4 | — | `tests/pause-cli-test.php` 20 phép; nút Cổng kế toán (PR #10) | — | S002-C11 |
| K3 | Kéo trạng thái `pending` → `posted` / `remote_error` | 2 | **4** | 4 | ✅ | kế toán định khoản → TGS_Acc_Events::pull_status đổi pending → posted — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy cron thật (DISABLE_WP_CRON) | S002-C7 |
| K4 | Dừng quá 7 ngày không mất chứng từ | 2 | **3** | 3 | ✅ | shop tạm dừng: cửa sổ đọc tới 90 ngày, bỏ tạm dừng chép nhóm còn mở sang hôm nay; tests/sc2-test.php 24/24 (bridge PR #14) | chưa chạy trong WP | OKT-SC-2 |
| K5 | Chuyển máy bán React → POS cũ khi kế toán tắt trước ca | 2 | **3** | 4 | — | `tests/test-engine-switch.php` 14 phép (PR #23) | — | S002-C12 |
| L1 | Năm số theo shop: hàng chờ, `pending` > 24 h, lỗi, lần gửi cuối, tạm dừng | 2 | **4** | 4 | ✅ | wp tgs-acc status --shop=2 trong WP: chờ định khoản 2, lỗi 0, lần gửi cuối — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa chạy trên shop thật | S002-C0 |
| L2 | Cảnh báo khi vượt ngưỡng | 2 | **2** | 3 | — | tổng kết tự kiểm hằng ngày (cấp mạng) + chỉ báo ở Cổng kế toán và ô Kết nối kế toán (bridge PR #14, open-pos-backend PR #40) | chưa có thông báo đẩy (email / Zalo) khi vượt ngưỡng | OKT-SC-2 |
| M1 | Đóng REST công khai (C1), gỡ token demo (C2) | 2 | **1** | 4 | — | PHASE-001 doc 31 | chưa làm | PHASE-001 |
| N1 | I-0: census `--check=I0` + ca bán chuẩn | 3 | **3** | 4 | — | PR #33, selftest 13, open-pos main xanh | ca bán chuẩn chưa chạy đơn thật | S002-C14 |
| N2 | **Tự kiểm theo cặp blog → tenant qua API** (luật I-8) | 4 | **4** | 4 | ✅ | wp tgs-acc selfcheck --shop=2 trong WP, trước và sau khi bán — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | cron 02:30 chưa chạy thật | OKT-SC-1 |
| N3 | Golden G0–G17 chạy lại được bằng script | 2 | **3** | 4 | — | setup-lat-doc + seed + sale-l2 chạy lại được (tools/lat-doc-docker) — lát dọc L0→L7 trên WP thật (open-pos-backend PR #41) | chưa đủ G0–G17; một blog, một máy chủ kế toán | S002-C0 |

**Mười chỗ nâng điểm nhiều nhất tới mức pilot** (điểm % thêm vào tổng nếu đạt mức pilot):

| # | Mã | Tiêu chí | + điểm | Việc |
|---|---|---|---|---|
| 1 | B1 | Định danh mặt hàng ổn định: `sku` + `itemId` lưu ở blog, đổi mã không mất dòng (I-4) | 1.4 % | S001-C8 |
| 2 | B4 | Kéo danh mục theo blog, chỉ cột `erp`, đối chứng lệch 0 | 1.4 % | S001-C8 |
| 3 | C2 | Bảng giá theo chi nhánh khai theo blog, lùi bảng giá công ty, DM14 ở bộ kéo | 1.0 % | S001-C8c |
| 4 | E3 | Sửa / xoá đơn sau khi gửi → phiên bản mới / huỷ | 1.0 % | S002-C9 |
| 5 | H4 | Đối chiếu tồn WP ↔ kế toán theo SKU | 1.0 % | OKT-SC-2 |
| 6 | M1 | Đóng REST công khai (C1), gỡ token demo (C2) | 1.0 % | PHASE-001 |
| 7 | B3 | Đơn tới trước mã (mã trơn): không mất barcode / ĐVT của shop | 0.7 % | S001-C8b |
| 8 | D2 | Đổi mã thuế sau 2026-12-31 | 0.7 % | S001-K16 |
| 9 | E2 | `docKey` bất biến + `version`; gửi lại không trùng | 0.7 % | S002-C9 |
| 10 | F1 | Mã phương thức **lưu sẵn**, không suy từ nhãn (I-4) | 0.7 % | S001-MD3 |

## 4. Tình huống ánh xạ dữ liệu (ca kiểm của đường nối)

Mỗi ca là một ca kiểm: lát dọc (L*), golden (G*) hoặc tự kiểm (SC-*). "Hôm nay" = hành vi đọc từ mã 22/11.

| # | Tình huống | Phải đạt | Hôm nay | Ca |
|---|---|---|---|---|
| M1 | Bán một mã chưa có ở kế toán | kế toán tạo mã trơn; lượt kéo không xoá barcode / ĐVT của shop | mã trơn được tạo; lượt kéo cũ ghi rỗng đè (81 F7) | G10, S001-C8b |
| M2 | Hai blog cùng SKU, giá khác | mỗi blog giá riêng; không đụng nhau | catalog global dùng chung | G4 |
| M3 | Đổi SKU ở kế toán | `itemId` giữ, dòng ở blog không đổi id | chưa có bộ kéo | G9, S001-C8 |
| M4 | Bán theo thùng (1 thùng = 24 lon) | gửi `Lon`, SL 24, `unitRatio` 24 | đúng từ PR #7 | L5 |
| M5 | Thuế 3,5 % | mã thuế có thật ở tenant, hoặc chặn trước khi gửi | gửi `R04` (không có) | SC-6 |
| M6 | Hàng không chịu thuế | `KCT` | đúng | L5 |
| M7 | Hàng tặng | dòng `isGift`, tiền 0, có giá vốn | mapper có cờ | L5 |
| M8 | Chiết khấu dòng / chiết khấu đơn | `discount` dòng; tổng khớp | chiết khấu dòng có; chiết khấu đơn phân bổ chưa kiểm | L5 |
| M9 | Voucher | phương thức `VOUCHER` | phụ thuộc ánh xạ phương thức | SC-5 |
| M10 | Thanh toán TM + QR | hai dòng tiền, tổng = tổng phiếu thu | `split_parent` có, chưa test | S002-17 T5 |
| M11 | QR có nhãn ngân hàng | mã phương thức lưu sẵn | suy `QR-VTB-CT` | SC-5, S001-MD3 |
| M12 | Ghi nợ, thu sau 2 ngày | phiếu thu riêng đúng ngày quỹ | đúng | S002-17 T3 |
| M13 | Tiền mặt dư làm tròn | quỹ kế toán = quỹ POS | chưa kiểm định khoản | L7, Q002-3 |
| M14 | Trả một phần đơn | `sale_return` trỏ đơn gốc, phần trả | có, test 38 | L9 |
| M15 | Đổi trả (đối trừ) | `offsets`, không thành tiền thật | có, chưa test | L9 |
| M16 | Sửa đơn sau khi gửi | cùng `docKey`, `version` + 1 | có | L9 |
| M17 | Xoá đơn sau khi gửi | huỷ chứng từ ở kế toán | có | L9 |
| M18 | Bill Z | `internalOnly: true` | nguồn sổ POS chưa quyết `is_z` | L5 |
| M19 | Khách lẻ không SĐT | không gửi `partner`; thu đủ thì kế toán nhận | đúng | L5 |
| M20 | Khách đổi SĐT | vẫn một đối tượng | thành hai đối tượng | S001-MD3 |
| M21 | Bán khi tồn local = 0 | quầy vẫn bán (luật cũ của POS); kế toán ghi cờ | theo POS cũ | H5 |
| M22 | Chi nhánh tenant không có kho | chặn bật kết nối, hoặc có kho mặc định | tenant okt-thu 0 kho, chưa kiểm | SC-7 |
| M23 | Kế toán tắt 2 phút / cả ca | vẫn bán; gửi bù không trùng | có, test | L10, G13 |
| M24 | Shop tạm dừng kết nối | 0 HTTP; bỏ tạm dừng gửi bù | có, test | L11, G14 |
| M25 | Hai blog dán cùng khoá | cả hai 🔴, không gửi | **không phát hiện** | SC-3, G12 |
| M26 | Blog đổi sang tenant khác | chứng từ cũ không gửi lại nhầm sang tenant mới | nhật ký gửi không biết tenant (cảnh báo khi đổi khoá) | SC-2 |
| M27 | Nhân viên chưa có ở kế toán | chứng từ vẫn nhận, nhân viên để trống / báo | chưa kiểm | SC-8 |
| M28 | Lý do xuất POS khác mã tenant | ánh xạ lưu sẵn | gửi thẳng mã POS | SC-8 |

## 5. Đọc bảng

- **Mạnh:** định danh & kết nối (A, 75 %), độ bền khi kế toán tắt / dừng (K, 70 %), trả hàng (G, 52 %), kiểm chứng (N, 69 %), bán hàng (E, 64 %). Đây là phần PHASE-002 và OKT-SC-1 đã làm, có test.
- **Yếu nhất và nặng nhất:** tồn kho (H, 53 %), danh mục (B, 29 %), thanh toán (F, 50 %), thuế (D, 56 %).
- **Mười chỗ nâng điểm nhiều nhất tới mức pilot** (§3 cuối): đứng đầu là **ánh xạ kho** (H2) và **bộ kéo danh mục** (S001-C8: B1, B4). Bảng ánh xạ mã (S001-MD3) đã làm 22/11 01:35 PM: tự kiểm phát hiện mã thiếu, bảng ánh xạ sửa chúng. Thứ tự code tiếp: OKT-SC-2 (bridge: cron, Cổng kế toán, tự tạm dừng) → lát dọc trên WP thử → S001-C8.
- Lần đo 11:00 AM xếp bốn chỗ đầu vào tự kiểm (OKT-SC-1); đã làm ở bridge PR #12, điểm 36,8 % → 41,4 %.
- Không tiêu chí nào lên **4** khi chưa có WordPress thử (S002-1 phần WP, chủ để sau). Nếu mọi tiêu chí lên mức test (3), trần là **59,5 %**; từ đó tới 72,5 % chỉ có bằng chạy thật.

## 6. Lịch sử đo

| Ngày | Điểm | Pilot | Ghi chú |
|---|---|---|---|
| 2026-11-22 11:00 AM | 36,8 % | 72,5 % | lần đo đầu; sau PHASE-002 S002-2…16, okt-thu chạy |
| 22/11/2026 11:50 AM | 41,4 % | 72,5 % | OKT-SC-1 (bridge PR #12): A2, A3, N2 lên mức 3 |
| 22/11/2026 01:35 PM | 43,6 % | 72,5 % | S001-MD3 (open-pos-backend #39, bridge #13): F1, E4, D1 lên mức 3 |
| 22/11/2026 02:55 PM | 44,6 % | 72,5 % | OKT-SC-2 (bridge #14, open-pos-backend #40): K4 lên 3, L2 lên 2 |
| 22/11/2026 04:40 PM | 52,2 % | 72,5 % | lát dọc L0→L7 trên WP thật (open-pos-backend #41): 11 tiêu chí lên mức 4 |
| 22/11/2026 05:50 PM | 54,2 % | 72,5 % | OKT-I3 (bridge #16): E6, K1 lên mức 4 — quầy không chờ kế toán, hàng chờ gửi bù được |
| 22/11/2026 06:50 PM | 54,7 % | 72,5 % | OKT-CAU-DAO (bridge #17): H2 lên 2 (đệm kho theo tenant); kế toán treo không làm đứng site FPM |
| 22/11/2026 07:50 PM | 55,8 % | 72,5 % | OKT-H2 (bridge #18): H2 lên 4 — đơn POS vào kho mặc định của chi nhánh (đo thật), phân kho theo kết nối của từng blog, SC-7 kiểm kho mặc định |

Cách đo lại: sửa dữ liệu chấm trong `tools/okt-scoreboard.mjs` (cột mức + bằng chứng), chạy `node tools/okt-scoreboard.mjs`, dán bảng, thêm một dòng ở đây.
