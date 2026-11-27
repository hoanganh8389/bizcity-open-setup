# Canon chung và xương sống xuyên app — áp cho bizcity-open-setup

<!-- [2026-11-24 06:40 PM Johnny Chu - Chu Hoàng Anh] SPINE-3 — gieo canon theo Q-SPINE-4 (chủ duyệt 2026-11-24): chỗ trỏ tới canon chung (open-hub) và chuẩn bizcity_spine@1 (bizcity-platform); khai trục ở bizcity.app.json. Tài liệu thuần, không đổi mã; luật của repo vẫn ở docs/00-CANON.md. -->

| Tài liệu | Ở đâu | Quan hệ |
|---|---|---|
| **BIZCITY OPEN CANON** | [open-hub/docs/canon](https://github.com/hoanganh8389/open-hub/blob/main/docs/canon/README.md) | §2.1: open-setup là **repo điều phối thứ hai** — registry site → DB, vòng đời site, tên miền gốc |
| **`bizcity_spine@1`** — xương sống xuyên app | [bizcity-platform/docs/standard/BIZCITY-SPINE-v1.md](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-SPINE-v1.md) | trục `tenant` do repo này làm chủ |
| **Ba vai nền** (R-CANON-17) | [canon §2.2](https://github.com/hoanganh8389/open-hub/blob/main/docs/canon/BIZCITY-OPEN-CANON-v1.md) · [bizcity-platform NC-003](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/research/NC-003-TACH-OPEN-CORE.md) | open-platform (chuẩn) → open-core (mã lõi `@bizcity/*`) → app = open-core + module → **repo này** cấp instance, ghi `core_version` <!-- [2026-11-27 11:03 PM Johnny Chu - Chu Hoàng Anh] NC-003 — chủ chốt Q-CORE-1…4: ba vai nền; open-setup cấp instance cho mọi app dựng trên open-core --> |
| Luật của repo | [docs/00-CANON.md](../00-CANON.md), [chương trình OKT](../chuong-trinh/OKT/00-ADR-OKT-1.md) | luật tối thượng P-0 của open-pos ⇄ open-ketoan |

## open-setup trong xương sống (`bizcity.app.json` ở gốc repo)

| | |
|---|---|
| Làm chủ | **`tenant`**: slug site `^[a-z][a-z0-9-]{1,30}$` = `tenants.code` ở open-ketoan = tên DB `kt_<slug>`, `cake_<slug>`; một site một khoá `biz-…` nhiều DB (R-CANON-13) |
| Dùng | `user` (`sub = wp:<id>` — WordPress bizcity là nguồn danh tính) |
| Mở cho app khác | `bizcity_site_provisioning@1` (`/_sites/v1`): cấp / khoá / sao lưu / xoá site; app đọc registry để biết site nào bật app nào |
| Không giữ | dữ liệu nghiệp vụ, kết nối PostgreSQL trực tiếp của app (R-ROLE-3), pháp nhân (thuộc sổ, không theo tenant — P-0) |

## Ba điều không làm

- Không suy tenant / pháp nhân từ khoá hay blog id; mô hình triển khai phải khai rõ (P-0).
- Không đổi slug site đã cấp (ID trục bất biến); ngừng = archive trong registry, không xoá khi còn tham chiếu (ECP-13).
- Không thêm trục mới ở repo này.

## Kiểm

```bash
node ../bizcity-platform/tools/spine-check.mjs --manifest bizcity.app.json   # SC-SPINE-1, phải ĐẠT
```

## Chuẩn nền của hệ (bizcity-platform)

<!-- [2026-11-25 10:04 AM Johnny Chu - Chu Hoàng Anh] STD-2 — trỏ về bản đồ chuẩn nền bizcity_standard_map@1 (bản nháp chờ duyệt) để repo này đi cùng hướng với cả hệ. Không đổi mã. -->

Repo này theo **[bản đồ chuẩn nền `bizcity_standard_map@1`](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/README.md)**: bốn trục dữ liệu (master data, chứng từ, khách 360, người dùng) và mười hai trụ cột kỹ thuật. Bức tranh toàn hệ: [ARCHITECTURE](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/ARCHITECTURE.md). Thứ tự luật: canon chung (open-hub) → chuẩn nền (bizcity-platform) → luật của repo này; luật của repo **không được nới** hai tầng trên.

| Việc ở repo này | Chuẩn |
|---|---|
| Khuôn repo, manifest, nếp làm việc | [APP-SKELETON](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-APP-SKELETON-v1.md) |
| API, kiểm đầu vào / đầu ra | [API-PROFILE](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-API-PROFILE-v1.md) |
| Người dùng, vai, quyền, đăng nhập một lần | [USERS-ROLES](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-USERS-ROLES-v1.md) · [IDENTITY](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-IDENTITY-v1.md) |
| Bảo mật · quan sát và truy lỗi · đệm | [SECURITY](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-SECURITY-v1.md) · [OBSERVABILITY](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-OBSERVABILITY-v1.md) · [CACHE](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-CACHE-v1.md) |
| Kiểm thử · phiên bản, migration, sao lưu, nâng cấp | [TESTING](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-TESTING-v1.md) · [RELEASE](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-RELEASE-v1.md) |
| Giao diện React (model · view · controller), mockup | [WEB](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-WEB-v1.md) |
| Nhiều site / nhiều CSDL · Hub, khoá, 1API | [MULTISITE](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-MULTISITE-v1.md) · [HUB](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-HUB-v1.md) |

Kiểm khuôn repo (mức S0–S3):

```bash
node ../bizcity-platform/tools/standard-check.mjs --repo .
```

Lần kiểm 2026-11-25 còn:

- SC-STD-3 (cảnh báo): `tests/` — không thấy selfcheck, script test hay tệp test nào
