# Hướng dẫn cho AI agent (Claude Code, Copilot, Codex, Cursor…)
<!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] R-KEY-1 — câu 4: API key thuộc bizcity-llm-router. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — hướng dẫn chuẩn cho mọi agent làm việc trong repo Bizcity Open Setup. -->

Dự án: **Bizcity Open Setup** — nơi tạo và quản lý các site kế toán. Cùng hệ sinh thái với open-ketoan (lõi kế toán), open-kiot (bán lẻ) và Zalo Brain / Cell (trợ lý AI). Trước khi sửa gì, đọc [docs/00-CANON.md](docs/00-CANON.md) rồi [ADR-0001](docs/adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md).

> **Mô hình (Johnny Chu – Chu Hoàng Anh, 2026-11-21):**
> **Frappe** = giao diện điều hành và quản lý site. **Open Kế Toán** = ứng dụng kế toán dùng chung, độc lập với Frappe. **PostgreSQL** = mỗi site một database và một vai trò riêng. <!-- [2026-11-21 09:18 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — vai trò riêng từng site -->

> **Hiện trạng (2026-11-21):** repo có **tài liệu và script vận hành, chưa có mã app**. App Frappe `bizcity_site_manager` và Provisioning API của Open Kế Toán là **đích**; đừng giả định chúng đã tồn tại. Kiểm bằng cách đọc cây thư mục. Việc kế tiếp: [PHASE-001](docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN/README.md).

## Bốn câu không thương lượng

1. **Frappe không giữ dữ liệu kế toán.** Site Manager chỉ giữ danh sách site, khách hàng và nhật ký việc. Sổ sách nằm trong database của từng site bên Open Kế Toán.
2. **Một site kế toán không phải một Frappe site.** Tạo site kế toán = gọi Provisioning API của Open Kế Toán để cấp một database. Không `bench new-site` cho từng khách.
3. **Site Manager không chạm PostgreSQL.** Mọi việc tạo / khoá / sao lưu / xoá đi qua Provisioning API (`bizcity_site_provisioning@1`). Open Kế Toán là chủ của Site Registry.
4. **Khoá `biz-…` thuộc `bizcity-llm-router` và chỉ để cảnh báo.** Plugin đó cấp và quản lý khoá. Hết hạn thì site vẫn dùng, chỉ có dải đỏ. Site Manager không cấp, không lưu khoá của khách. <!-- [2026-11-21 07:46 PM Johnny Chu - Chu Hoàng Anh] D001-9 — khoá mềm --> Khoá Provisioning (máy chủ gọi máy chủ) nằm ở trường mật khẩu của Frappe.

## Bước 0: giữ chỗ trước khi nhận việc (R-FLOW)

Nhiều phiên (người và AI) làm cùng một kho. Trước dòng code đầu của một đợt việc: đọc [docs/phases/CLAIMS.md](docs/phases/CLAIMS.md) trên `origin/main`; phạm vi chồng dòng "đang làm" của người khác → **dừng**, báo người dùng. Đụng hợp đồng `bizcity_site_provisioning@N` → sửa ở repo `open-ketoan` trước (chủ hợp đồng), rồi mới sửa bên này. Sửa lỗi nhỏ một tệp, tài liệu thuần: không cần giữ chỗ.

## Đặt tên

- App Frappe: `bizcity_site_manager`. Module: `Bizcity Site Manager`.
- DocType: tiền tố `Bizcity ` (ví dụ `Bizcity Ketoan Site`). Hàm / hook / khoá cấu hình Python: tiền tố `bizcity_`.
- Tệp mới bắt đầu bằng dòng bản quyền: `# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.`

## Chữ ký và dấu thay đổi (R-SIG — bắt buộc)

Mỗi lần sửa **có chức năng** một tệp (mã app, script `ops/`, tài liệu luật / ADR / phase) thêm **một dấu** tại chỗ đổi:

```text
[YYYY-MM-DD HH:MM AM/PM Johnny Chu - Chu Hoàng Anh] <MÃ phase / luật> — <đổi gì, cụ thể>
```

- Người trong dấu là **người chỉ đạo / duyệt**. **Không bao giờ** ghi tên agent / model.
- Giờ lấy từ đồng hồ thật của máy lúc sửa (Windows: `Get-Date -Format "yyyy-MM-dd hh:mm tt"`). Không đoán, không cộng dồn từ dấu trước.
- Một dấu một mã. Không xoá, không sửa dấu cũ.

## Vận hành trên VPS dùng chung

VPS chạy chung với zalo-hub và WordPress. Ba điều cấm:

1. Không `systemctl restart docker`.
2. Không `restartsrv_httpd` khi `httpd -t` chưa đạt.
3. Không `csf -r` / `firewall-cmd --reload`. Tường lửa là **Imunify360**: container mới nghe cổng nào thì thêm cổng đó vào `FIREWALL.TCP_OUT_IPv4` ([sổ tay §6](docs/van-hanh/CAI-FRAPPE-TREN-VPS.md)).

## Khi review PR

Bị 0 là **KHÔNG ĐẠT**: vi phạm một trong bốn câu trên · bí mật trong git · lệnh shell ghép chuỗi từ đầu vào người dùng · xoá site không qua bước sao lưu (R-DATA-1). Mỗi phát hiện ghi: mức · mã luật · `tệp:dòng` · cách làm đúng.

<!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 — open-setup thêm vai trục điều phối chương trình OKT. -->
## Vai thứ hai: trục điều phối chương trình OKT

Repo này còn giữ **trục tài liệu của chương trình OKT** (open-pos ⇄ open-ketoan) ở [docs/chuong-trinh/OKT/](docs/chuong-trinh/OKT/README.md):
- canon: ADR-OKT-1, tám bất biến;
- roadmap;
- **checklist**, là nguồn trạng thái duy nhất;
- phân việc, đánh giá, câu hỏi chờ chủ.

Mã của chương trình nằm ở open-pos, open-pos-backend, open-ketoan-bridge, open-ketoan.

- **Đổi trạng thái việc OKT chỉ ở `docs/chuong-trinh/OKT/40-CHECKLIST.md`**, kèm dấu R-SIG và link bằng chứng. Checklist ở các repo kia không giữ trạng thái.
- **Bất biến I-0:** luồng bán, logic bán hàng và sổ của open-pos giữ nguyên. Khi review việc OKT, PR chạm tệp cấm sửa (ADR-OKT-1 D002-6) ngoài mẫu "chỉ đổi tên bảng" (D002-7) là **KHÔNG ĐẠT**.
