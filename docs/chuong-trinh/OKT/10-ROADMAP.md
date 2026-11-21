# OKT · 10 — Roadmap

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — roadmap chương trình OKT, gom từ open-pos-backend PHASE-001 doc 29 §5, PHASE-002 doc 20 §4 và ADR-OKT-1. Ngày là kế hoạch, chỉnh khi gán người (50). -->

## 0. Mục tiêu và điều kiện đạt

Mục tiêu (chủ, 21/11):
- open-pos **tự xoay xở khi open-ketoan tắt hoặc dừng kết nối**;
- **luồng bán, logic bán hàng và sổ giữ nguyên**.

Chương trình **đạt** khi:
1. Bốn tình huống K-A…K-D (mất kết nối giữa ca, trước khi mở ca, dừng chủ động, nối lại) đều có bằng chứng chạy ([60 §1](60-DANH-GIA.md)).
2. Ca bán chuẩn trước và sau mọi mốc cho cùng dòng sổ (I-0).
3. Pilot 1–3 shop thật chạy 10 ngày liền không lệch đối soát.

## 1. Mốc

| Mốc | Thời gian (kế hoạch) | Nội dung | Mã việc ([40](40-CHECKLIST.md)) | Đạt khi | Repo |
|---|---|---|---|---|---|
| **P0 Trục điều phối** | 21/11 | ADR, checklist, phân việc, đánh giá về open-setup | — | tài liệu này merge | open-setup |
| **L Lát dọc** (open-pos-backend PHASE-002) | 23/11 – 04/12 | Một đơn POS cũ → sổ → bridge → preflight → `documents/batch` → duyệt → `posted`; tạm dừng theo blog; chuyển React → POS cũ; ca dự phòng React; census I-0 | S002-0a…16, S002-C0…C14 | ca C0…C14 có bằng chứng | bridge, open-pos-backend, open-pos (script) |
| **M1 Danh mục theo blog** (PHASE-001 M1) | 07/12 – 18/12 | Bảng theo prefix + `tgs_catalog_table()` (POS **chỉ đổi tên bảng**, D002-7); màn ĐVT / bảng giá; `tgs_catalog_source`; thuế mặc định | S001-C11…C14, MD1, P001-T1…T3 (tên bảng), B001-C1 | blog `local` tạo và bán được; ca bán chuẩn trước–sau giống hệt | open-pos-backend, open-pos |
| **M2 Ánh xạ** (PHASE-001 M2 + M3) | 21/12 – 01/01 | Kết nối theo blog; bảng ánh xạ; bộ kéo C8 (có DM14, D002-8); ánh xạ thuế | B001-C2, C5, C6, C7, S001-C8, C18, MD2, MD3 | blog `ketoan` kéo đủ, đối chứng lệch 0 | bridge, open-pos-backend |
| **M3 Chứng từ + chuyển nguồn** (PHASE-001 M4) | 04/01 – 15/01 | Đơn lên đúng tenant cho mọi blog; chuyển `local` → `ketoan`; golden | B001-C3, C8, C10…C14, S001-C9, C16 | golden trọn bộ | bridge, open-pos-backend |
| **M4 Pilot** | 18/01 – 29/01 | 1–3 shop thật, đối soát hằng ngày | — | 10 ngày liền không lệch | cả năm repo |
| Rộng ra | từ 01/02 | Chuyển 92 blog theo lô | — | — | — |

## 2. Hạn cứng

| Hạn | Việc | Vì sao |
|---|---|---|
| **2026-12-31** | Ánh xạ thuế (S001-MD2) + open-ketoan mã thuế thay `8` (S001-K16) | mã `8` không ghi sổ được từ 2027 |
| trước pilot | open-ketoan cấp tenant cho shop (S001-K10), đơn POS tự ghi sổ (S001-K13) | không có tenant thì không bán theo kế toán được; đơn treo `pending` |

## 3. Đường găng

```
P0 ─► Lát dọc (S002) ─► M1 ─► M2 ─► M3 ─► M4
          │                     ▲
          │                     └── open-ketoan: K1 (con trỏ feed), K16 (thuế, hạn 31/12)
          └── open-setup PHASE-001 + open-ketoan PHASE-039: cấp site / tenant (K10) ─────► M4
```

## 4. Phụ thuộc giữa repo

| Bên cần | Bên cấp | Thứ | Mã |
|---|---|---|---|
| open-pos-backend (bộ kéo) | bridge | client theo blog `for_blog()`, `tgs_okt_connected()` / trạng thái | B001-C2, C6 |
| open-pos (đọc danh mục) | open-pos-backend | `tgs_catalog_table()` | S001-C11 |
| bridge (gửi chứng từ) | open-ketoan | tenant cho từng shop, `documents/batch`, `intake/preflight` | K10, K13 |
| cả chương trình | open-setup (Site Manager) | cấp site / tenant tự động | open-setup PHASE-001, open-ketoan PHASE-039 |
