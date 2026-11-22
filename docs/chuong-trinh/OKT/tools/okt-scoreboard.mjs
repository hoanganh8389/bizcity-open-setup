// [2026-11-22 11:00 AM Johnny Chu - Chu Hoàng Anh] OKT-P0 — dữ liệu chấm scoreboard 70 → bảng markdown + tổng. Chạy: node docs/chuong-trinh/OKT/tools/okt-scoreboard.mjs
// Thang: 0 chưa có · 1 thiết kế / tài liệu · 2 có mã · 3 có test chạy một lệnh · 4 chạy thật trên môi trường thử, có bằng chứng · 5 chạy shop thật, tự kiểm xanh liên tục.
// w = trọng số (tổng 100), p = mức cần cho pilot.
const D = [
  ['A', 'Định danh & kết nối', [
    ['A1', 'Khoá + URL theo blog; không khoá chung cả mạng (I-1)', 4, 3, 4, 'bridge `tests/config-test.php` (PR #2), `for_blog()` (PR #8)', 'chưa chạy trong WordPress thật', 'S002-C0'],
    ['A2', 'Chứng minh được khoá của blog trỏ **đúng tenant** (gọi `/api/v1/tenant`, so mã lưu)', 3, 3, 4, '`TGS_Acc_Selfcheck` SC-2, test 41/41; chạy thật okt-thu (bridge PR #12)', 'chưa chạy trong WP', 'OKT-SC-1'],
    ['A3', 'Một tenant ↔ một blog: phát hiện hai blog chung tenant (G12)', 3, 3, 4, 'SC-3 bản đồ blog → tenant, test 41/41 (bridge PR #12)', 'chưa chạy trong WP; tự tạm dừng ở OKT-SC-2', 'OKT-SC-1'],
    ['A4', 'Chi nhánh khai theo blog, mã sai thì báo, không tạo chi nhánh trống', 2, 3, 4, '`tests/branch-unit-test.php` 17 phép (PR #7)', '—', 'S002-C0'],
  ]],
  ['B', 'Danh mục hàng hoá', [
    ['B1', 'Định danh mặt hàng ổn định: `sku` + `itemId` lưu ở blog, đổi mã không mất dòng (I-4)', 4, 1, 3, '81 F1–F15', 'bộ kéo C8 chưa có; `itemId` chỉ khi có `TGS_Item_Variant`', 'S001-C8'],
    ['B2', 'ĐVT: gửi ĐVT gốc, SL theo ĐVT gốc, tỉ lệ quy đổi', 3, 3, 4, 'PR #7 (`unit = dvt_goc`), test 17', '—', 'S002-C5'],
    ['B3', 'Đơn tới trước mã (mã trơn): không mất barcode / ĐVT của shop', 2, 1, 3, 'Q001-19 chốt', 'S001-C8b chưa làm', 'S001-C8b'],
    ['B4', 'Kéo danh mục theo blog, chỉ cột `erp`, đối chứng lệch 0', 4, 1, 3, '81 đặc tả', 'chưa có mã', 'S001-C8'],
    ['B5', 'Nhóm hàng / nhóm hạch toán', 1, 1, 2, 'preflight IN-MD-004', 'chưa có ánh xạ', 'S001-C18'],
  ]],
  ['C', 'Giá', [
    ['C1', 'Giá gồm VAT → dòng trước VAT + thuế, tổng khớp tới đồng (I-5)', 5, 3, 4, '`line_money()` chép công thức POS, `tests/source-pos-test.php` 38 phép; preflight okt-thu 0 lỗi chặn', 'chưa chạy với đơn thật', 'S002-C5'],
    ['C2', 'Bảng giá theo chi nhánh khai theo blog, lùi bảng giá công ty, DM14 ở bộ kéo', 3, 1, 3, 'Q001-20, D002-8', 'chưa có mã', 'S001-C8c'],
  ]],
  ['D', 'Thuế', [
    ['D1', 'Mã thuế gửi đi **có trong danh mục tenant** (R00/R05/R08/R10/KCT)', 3, 3, 4, 'kind tax: R08 ↔ 8, không đoán R04; SC-6 báo đỏ trước khi gửi; trọn vòng okt-thu (bridge PR #13)', 'thuế 3,5 % chờ kế toán chốt mã; chưa chạy trong WP', 'OKT-SC-1'],
    ['D2', 'Đổi mã thuế sau 2026-12-31', 2, 1, 3, 'S001-K16', 'chưa làm, **hạn 2026-12-31**', 'S001-K16'],
  ]],
  ['E', 'Bán hàng', [
    ['E1', 'Nguồn phiếu bán đọc thẳng sổ POS, không cần tgs-bc-tk, chỉ đọc (I-0)', 4, 3, 4, 'PR #6, test 38', 'chưa chạy trong WP', 'S002-C2'],
    ['E2', '`docKey` bất biến + `version`; gửi lại không trùng', 4, 3, 4, 'nhật ký gửi + `tests/status-test.php` 21 phép', '—', 'S002-C9'],
    ['E3', 'Sửa / xoá đơn sau khi gửi → phiên bản mới / huỷ', 3, 2, 4, '`deleted_keys()`, `changed_before()`', 'chưa có test riêng', 'S002-C9'],
    ['E4', 'Lý do xuất POS → mã lý do tenant', 2, 3, 3, 'kind reason trong {p}tgs_okt_map; gợi ý XTA → XTA1.4 khi đúng một mã khớp; trọn vòng okt-thu (bridge PR #13)', 'chưa chạy trong WP', 'S001-MD3'],
    ['E5', 'Bill Z / chứng từ nội bộ (`internalOnly`)', 1, 2, 3, 'mapper `is_z`', 'nguồn sổ POS quyết `is_z` chưa kiểm', 'S002-C5'],
    ['E6', 'Không gọi HTTP trong request bán (I-3)', 4, 2, 4, 'sự kiện ghi JSONL, gửi sau', 'chưa đo; thiếu `fastcgi_finish_request` có thể treo 60 s', 'S002-C2'],
  ]],
  ['F', 'Thanh toán', [
    ['F1', 'Mã phương thức **lưu sẵn**, không suy từ nhãn (I-4)', 4, 3, 4, '{p}tgs_okt_map + TGS_Okt_Map (open-pos-backend PR #39, test 34/34); bridge dịch mã khi dựng (bridge PR #13, test 18/18); trọn vòng okt-thu: QR-VTB-CT → QR', 'chưa chạy trong WP; nhãn lạ (MOMO…) phải xác nhận tay', 'S001-MD3'],
    ['F2', 'Phiếu thu ghép đúng hoá đơn (`invoiceDocKey` = id phiếu loại 10)', 3, 2, 4, 'đọc mã 22/11 (doc 21 §1)', 'chưa chạy', 'S002-C6'],
    ['F3', 'Thanh toán tách nhiều phương thức', 2, 2, 3, '`split_parent`', 'chưa test', 'S002-17'],
    ['F4', 'Ghi nợ, thu sau, đúng ngày quỹ', 2, 2, 3, 'phiếu thu riêng theo ngày', 'chưa test', 'S002-17'],
    ['F5', 'Một đơn một chứng từ (`sale.payments`)', 2, 1, 2, 'doc 21 thiết kế', 'sau lát dọc', 'S002-17'],
    ['F6', 'Tiền mặt dư làm tròn', 1, 1, 3, 'Q002-3', 'chờ kết quả L7', 'S002-C7'],
  ]],
  ['G', 'Trả hàng / đổi trả', [
    ['G1', 'Phiếu hoàn (loại 11) → `sale_return`, trỏ đơn gốc', 3, 3, 4, 'test 38 gồm phiếu hoàn', '—', 'S002-C9'],
    ['G2', 'Đổi trả: đối trừ (`offsets`), không thành tiền thật', 2, 2, 3, '`offsets_by_sale()`', 'chưa test', 'S002-C9'],
  ]],
  ['H', 'Tồn kho', [
    ['H1', 'Tồn ở WP tính từ sổ local; bán / nhập đúng (POS không đổi, I-0)', 3, 2, 4, '`TGS_Global_Product_Source` stock SQL; seed nhập 10 qua đường nhập thật', 'chưa có bằng chứng của chương trình', 'S002-C2'],
    ['H2', 'Kho WP ↔ `warehouseCode` của tenant', 3, 1, 4, '`class-tgs-acc-warehouse-sync.php` có', 'tenant okt-thu **0 kho**; dòng gửi `warehouseCode` rỗng; định khoản giá vốn khi chi nhánh không kho chưa kiểm', 'OKT-SC-1'],
    ['H3', 'Nhập mua / trả NCC / chuyển kho / kiểm kê → chứng từ', 2, 2, 3, 'mapper `supplier_doc`, `adjust`, `gt-in/out`', 'ngoài lát dọc', 'PHASE-001'],
    ['H4', 'Đối chiếu tồn WP ↔ kế toán theo SKU', 2, 0, 3, 'kế toán có `/inventory/reconcile`', 'chưa có', 'OKT-SC-2'],
    ['H5', 'Thiếu tồn không chặn quầy; kế toán ghi cờ', 1, 1, 3, 'ADR D001-18, 28 §4', 'chưa kiểm', 'S002-C2'],
  ]],
  ['I', 'Khách hàng', [
    ['I1', 'Đối tượng theo **mã lưu**, không theo SĐT (I-4)', 2, 1, 3, 'mapper dùng SĐT làm `partner.code`', 'trái I-4; khách đổi SĐT tách hai đối tượng', 'S001-MD3'],
    ['I2', 'Danh bạ khách theo blog (Q001-14)', 1, 1, 3, 'Q001-14 chốt', 'chưa có mã', 'PHASE-001'],
  ]],
  ['J', 'Nhân viên', [
    ['J1', 'Nhân viên bán → `employee` của tenant', 1, 2, 3, 'mapper `employee()`', 'chưa đối chiếu danh mục tenant', 'OKT-SC-1'],
  ]],
  ['K', 'Độ bền khi kế toán tắt / dừng', [
    ['K1', 'Kế toán tắt: vẫn bán, hàng chờ 7 ngày, gửi bù theo thứ tự', 4, 3, 4, 'PR #8, #9; test 21 + 20', 'chưa chạy L10', 'S002-C10'],
    ['K2', 'Tạm dừng / bỏ tạm dừng theo shop, gửi bù không trùng', 2, 3, 4, '`tests/pause-cli-test.php` 20 phép; nút Cổng kế toán (PR #10)', '—', 'S002-C11'],
    ['K3', 'Kéo trạng thái `pending` → `posted` / `remote_error`', 2, 3, 4, '`tests/status-test.php`; `/documents?search` 200 trên okt-thu', '—', 'S002-C7'],
    ['K4', 'Dừng quá 7 ngày không mất chứng từ', 2, 3, 3, 'shop tạm dừng: cửa sổ đọc tới 90 ngày, bỏ tạm dừng chép nhóm còn mở sang hôm nay; tests/sc2-test.php 24/24 (bridge PR #14)', 'chưa chạy trong WP', 'OKT-SC-2'],
    ['K5', 'Chuyển máy bán React → POS cũ khi kế toán tắt trước ca', 2, 3, 4, '`tests/test-engine-switch.php` 14 phép (PR #23)', '—', 'S002-C12'],
  ]],
  ['L', 'Quan sát (I-6)', [
    ['L1', 'Năm số theo shop: hàng chờ, `pending` > 24 h, lỗi, lần gửi cuối, tạm dừng', 2, 3, 4, '`wp tgs-acc status` (PR #9), cột Kết nối (PR #10)', '—', 'S002-C0'],
    ['L2', 'Cảnh báo khi vượt ngưỡng', 2, 2, 3, 'tổng kết tự kiểm hằng ngày (cấp mạng) + chỉ báo ở Cổng kế toán và ô Kết nối kế toán (bridge PR #14, open-pos-backend PR #40)', 'chưa có thông báo đẩy (email / Zalo) khi vượt ngưỡng', 'OKT-SC-2'],
  ]],
  ['M', 'Bảo mật', [
    ['M1', 'Đóng REST công khai (C1), gỡ token demo (C2)', 2, 1, 4, 'PHASE-001 doc 31', 'chưa làm', 'PHASE-001'],
  ]],
  ['N', 'Kiểm chứng', [
    ['N1', 'I-0: census `--check=I0` + ca bán chuẩn', 3, 3, 4, 'PR #33, selftest 13, open-pos main xanh', 'ca bán chuẩn chưa chạy đơn thật', 'S002-C14'],
    ['N2', '**Tự kiểm theo cặp blog → tenant qua API** (luật I-8)', 4, 3, 4, '`wp tgs-acc selfcheck` SC-1…SC-11, test 41/41, chạy thật okt-thu 3 ca (bridge PR #12)', 'cron + Cổng kế toán (OKT-SC-2); chưa chạy trong WP', 'OKT-SC-1'],
    ['N3', 'Golden G0–G17 chạy lại được bằng script', 2, 1, 4, '01 viết lại 22/11; setup-lat-doc + seed', 'chưa có WP thử', 'S002-C0'],
  ]],
];
let W = 0, got = 0, pilotGap = [];
const rows = [];
const dom = [];
for (const [id, name, cs] of D) {
  let w = 0, g = 0;
  for (const [cid, text, cw, s, p, ev, gap, next] of cs) {
    w += cw; g += cw * s / 5; W += cw; got += cw * s / 5;
    if (s < p) pilotGap.push([cid, cw * (p - s) / 5, text, next]);
    rows.push(`| ${cid} | ${text} | ${cw} | **${s}** | ${p} | ${s >= p ? '✅' : '—'} | ${ev} | ${gap} | ${next} |`);
  }
  dom.push(`| ${id} | ${name} | ${w} | ${(100 * g / w).toFixed(0)} % |`);
}
console.log('TOTAL_W', W, 'SCORE', (100 * got / W).toFixed(1));
const pilotNeed = D.flatMap(([, , cs]) => cs).reduce((a, c) => a + c[2] * c[4] / 5, 0);
console.log('PILOT_TARGET', (100 * pilotNeed / W).toFixed(1));
console.log('\n#DOMAINS\n' + dom.join('\n'));
console.log('\n#ROWS\n' + rows.join('\n'));
pilotGap.sort((a, b) => b[1] - a[1]);
console.log('\n#GAP\n' + pilotGap.slice(0, 10).map((g, i) => `| ${i + 1} | ${g[0]} | ${g[2]} | ${(100 * g[1] / W).toFixed(1)} % | ${g[3]} |`).join('\n'));
