# OKT · mockups — scoreboard, tự kiểm, trace dòng chảy

<!-- [2026-11-22 12:20 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — chủ: lưu mockup scoreboard / dashboard tự kiểm / trace vào tài liệu chương trình. Bản xem trực tiếp ở canvas Claude; tệp ở đây là mã nguồn để giữ cùng tài liệu. -->

**Xem trực tiếp:** canvas [OKT Connection Scoreboard](https://claude.ai/artifact/NSxgh5KUvmP5cq8gcGCDhu) (riêng tư — chủ chia sẻ từ menu Share cho người cần xem).

| Màn | Tệp | Nội dung | Dựa trên |
|---|---|---|---|
| 1 · Scoreboard kết nối | [Main.dc.html](Main.dc.html) | 4 số chính (41,4 % · pilot 72,5 % · trần không WP 59,5 % · 0/46 đạt pilot), thanh tới pilot, 14 thẻ miền → bảng tiêu chí (mức / pilot, bằng chứng, thiếu, việc), mười chỗ nâng điểm, lịch sử đo, thang điểm | [70](../70-SCOREBOARD-KET-NOI.md), `tools/okt-scoreboard.mjs` |
| 2 · Tự kiểm blog → tenant | [Selfcheck.dc.html](Selfcheck.dc.html) | Ma trận cặp blog → tenant × SC-1…SC-11 (✓ ! ✕ —), lọc theo kết luận, chi tiết từng phép + việc cần làm + lệnh CLI, "đỏ thì làm gì" | [75](../75-LUAT-TU-KIEM.md); kết quả chạy thật `tests/selfcheck-live.php` vào okt-thu 22/11 (bridge PR #12) |
| 3 · Trace dòng chảy hai chiều | [Trace.dc.html](Trace.dc.html) | Chiều bán (9 chặng, trạng thái quay về) · chiều danh mục (6 chặng, vòng shop tạo mã); mỗi chặng: mức, vào / ra / hỏng thì / trace ghi gì / bằng chứng; dịch một dòng sổ POS ↔ chứng từ; dòng thời gian một chứng từ | [70 §1](../70-SCOREBOARD-KET-NOI.md), PHASE-002 doc 10, 21 |

**Dữ liệu thật và minh hoạ:**
- Điểm số: từ `tools/okt-scoreboard.mjs` lúc đo 22/11 11:50 AM.
- Ba dòng tự kiểm của shop-a: kết quả chạy thật vào okt-thu 22/11 11:45 AM. Dòng shop-b (blog tự quản, không khoá): minh hoạ.
- Dòng thời gian trace: minh hoạ dựng từ mã (lát dọc chưa chạy trong WordPress); mốc thời gian theo thiết kế, không phải số đo.
- Nút "Chạy lại tất cả", "Xuất JSON": chỉ là mockup.

**Định dạng:** `.dc.html` là trang Design Component của canvas (cần runtime của canvas để chạy); `canvas.json` là bố cục ba màn. Sửa ở canvas rồi chép lại vào đây, hoặc sửa tệp ở đây rồi đăng lại canvas.

**Đích của mockup (chưa làm):** màn **Cổng kế toán** của bridge hiện kết luận tự kiểm từng shop (OKT-SC-2); scoreboard đo lại mỗi mốc ([70 §6](../70-SCOREBOARD-KET-NOI.md)).
