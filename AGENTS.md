# Hướng dẫn cho AI agent (Claude Code, Copilot, Codex, Cursor…)
<!-- [2026-11-21 07:36 PM Johnny Chu - Chu Hoàng Anh] R-KEY-1 — câu 4: API key thuộc bizcity-llm-router. -->
<!-- [2026-11-21 07:25 PM Johnny Chu - Chu Hoàng Anh] INIT — hướng dẫn chuẩn cho mọi agent làm việc trong repo Bizcity Open Setup. -->

Dự án: **Bizcity Open Setup** — nơi tạo và quản lý các site kế toán. Cùng hệ sinh thái với open-ketoan (lõi kế toán), open-kiot (bán lẻ) và Zalo Brain / Cell (trợ lý AI). Trước khi sửa gì, đọc [docs/00-CANON.md](docs/00-CANON.md) rồi [ADR-0001](docs/adr/ADR-0001-frappe-site-manager-open-ketoan-ung-dung-chung.md).

> **Mô hình (Johnny Chu – Chu Hoàng Anh, 2026-11-21):**
> **Frappe** = giao diện điều hành và quản lý site. **Open Kế Toán** = ứng dụng kế toán dùng chung, độc lập với Frappe. **PostgreSQL** = mỗi site một database và một vai trò riêng. <!-- [2026-11-21 09:18 PM Johnny Chu - Chu Hoàng Anh] ADR-0001 — vai trò riêng từng site -->

> **Hiện trạng (2026-11-21):** repo có **tài liệu và script vận hành, chưa có mã app**. App Frappe `bizcity_site_manager` và Provisioning API của Open Kế Toán là **đích**; đừng giả định chúng đã tồn tại. Kiểm bằng cách đọc cây thư mục. Việc kế tiếp: [PHASE-001](docs/phases/PHASE-001-CONG-TU-TAO-KE-TOAN/README.md).

<!-- [2026-11-27 11:03 PM Johnny Chu - Chu Hoàng Anh] NC-003 — chủ chốt Q-CORE-1…4: ba vai nền; open-setup cấp instance cho mọi app dựng trên open-core -->
> **Ba vai nền (canon R-CANON-17, 2026-11-27):** **open-platform** = repo `bizcity-platform` (chuẩn `BIZCITY-*`, bộ kiểm) quy định → **open-core** = repo `open-core` (mã lõi `@bizcity/*`, semver chung; trong đó có máy nhiều site `db/site-*.ts` phục vụ `/_sites/v1`) hiện thực → mỗi app (open-ketoan, open-cake, open-pos, open-hrm, open-mrp…) = open-core + module → **open-setup (repo này)** giữ registry Workspace × app = instance và gọi `/_sites/v1` của app. Hệ quả cho repo này:
> - Site Manager phục vụ **mọi app trên open-core**, không chỉ Kế Toán: DocType `Bizcity Ketoan Site` sẽ tổng quát thành `Bizcity App Instance` (thêm `product`, `core_version`, `app_version`, `root_domains`) — NC-003 bước C7, NC-002 OC-6.
> - Mỗi instance ghi `core_version` (bản open-core đang chạy) + `app_version`; nâng cấp = app chạy migration **lõi trước, module sau** — Site Manager chỉ gọi API, không tự chạy migration.
> - Sửa máy nhiều site / hợp đồng `bizcity_site_provisioning@N`: mã ở **open-core** (từ NC-003 C2), văn bản hợp đồng vẫn ở open-ketoan tới khi chủ chốt nơi ở mới (NC-003 Q-CORE-5).

<!-- [2026-11-28 12:24 AM Johnny Chu - Chu Hoàng Anh] NC-004 — tenant ↔ blog_id (canon R-CANON-18) -->
> **Tenant ↔ blog (canon R-CANON-18, bizcity-platform NC-004 Q-PIL-2):** một cửa hàng = một blog WordPress = **một tenant**; một chuỗi nhiều cửa hàng = nhiều tenant trong cùng Workspace. Registry ghi ánh xạ `blog_id ↔ tenant` một-một (`tenants.external_ref = wp-blog:<id>` ở app) — không suy tenant từ khoá hay tên. **Workspace chỉ ghi chép trạng thái** — trạng thái hoạt động gốc (thành viên, blog, gói, khoá) nằm ở phía WordPress bizcity hub; Site Manager đọc / nhận từ hub rồi ghi lại, không tự quyết bật / tắt (Q-PIL-5, chủ chốt 2026-11-28 02:15 PM).

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

<!-- bizcity:loi-truoc@1 — khối chung do bizcity-platform phát (bizcity_core_first@1). Sửa ở bizcity-platform/templates/loi-truoc/AGENTS-khoi.md rồi chép lại nguyên khối; SC-STD-4 kiểm dấu này. -->
## Lõi trước — bánh xe đóng góp (R-CORE-10)

Làm app thì lõi lớn lên: tối ưu open-ketoan, open-cake, open-kiot… là đồng thời hoàn thiện **open-core**; app làm sau hưởng toàn bộ thành quả.

```text
① App phát triển (nghiệp vụ mới) ─► ② Phát hiện năng lực chung ─► ③ Rút lên lõi (test · release) ─► ④ App dùng lại, xoá bản trùng ─┐
        ▲                                                                                                                      │
        └──────────────────────────────── app sau viết ít hơn ◄────────────────────────────────────────────────────────────────┘
```

1. **Trước khi viết thứ phổ thông** (danh sách, form, nhập / xuất, cài đặt, meta, quyền, chứng từ, sự kiện, đồng bộ, thông báo, báo cáo, CLI…): tra lõi — `bizcity doctor --tim <từ khoá>` (khi chưa có lệnh: đọc `open-core/packages/*/src` + `open-core/CHANGELOG.md`). Lõi có ⇒ **dùng**, không viết lại.
2. **Lõi chưa có ⇒ chọn đúng một đường**, ghi vào ô **"Lõi hay app?"** của mẫu PR:
   - **A — vào lõi:** ≥ 2 app cần, hoặc là hạ tầng chung ⇒ mở PR ở open-core trước (nhãn `rut-len-loi`); app dùng chế độ `core-dev` (`bizcity dev link-core`) trong lúc chờ bản phát hành.
   - **B — ứng viên lõi:** mới một app cần nhưng rõ là phổ thông ⇒ viết trong `src/core-candidate/`, đầu tệp `@bizcity-core-candidate <mô tả>`, không chuỗi nghiệp vụ cứng — để rút lên được nguyên tệp.
   - **C — nghiệp vụ:** chỉ app này có nghĩa ⇒ viết ở app như thường.
3. **Phát hiện tự động:** `open-core/tools/ung-vien-loi.mjs` dò ứng viên đã đánh dấu + mã trùng giữa các app ⇒ bảng "Ứng viên lõi" trong scoreboard của open-core.
4. **Rút lên lõi** có test chạy thật, CHANGELOG lõi ghi app nguồn ⇒ **app xoá bản riêng** khi lên bản lõi kế tiếp (codemod `open-core/tools/doi-nguon/` nếu đổi đường import).

App PHP / WordPress (open-kiot, plugin bizcity-*): "lõi" = hợp đồng + vector chung ở bizcity-platform và PHP SDK chung; cùng bốn bước.
Giữ chỗ việc ở lõi: `open-core/docs/phases/CLAIMS.md` · chia lane: `open-core/docs/phases/LANES.md` · chuẩn: [`bizcity_core_first@1`](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-CORE-FIRST-v1.md).
<!-- /bizcity:loi-truoc -->
