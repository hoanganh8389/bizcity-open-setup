# Canon chung và xương sống xuyên app — áp cho bizcity-open-setup

<!-- [2026-11-24 06:40 PM Johnny Chu - Chu Hoàng Anh] SPINE-3 — gieo canon theo Q-SPINE-4 (chủ duyệt 2026-11-24): chỗ trỏ tới canon chung (open-hub) và chuẩn bizcity_spine@1 (bizcity-platform); khai trục ở bizcity.app.json. Tài liệu thuần, không đổi mã; luật của repo vẫn ở docs/00-CANON.md. -->

| Tài liệu | Ở đâu | Quan hệ |
|---|---|---|
| **BIZCITY OPEN CANON** | [open-hub/docs/canon](https://github.com/hoanganh8389/open-hub/blob/main/docs/canon/README.md) | §2.1: open-setup là **repo điều phối thứ hai** — registry site → DB, vòng đời site, tên miền gốc |
| **`bizcity_spine@1`** — xương sống xuyên app | [bizcity-platform/docs/standard/BIZCITY-SPINE-v1.md](https://github.com/hoanganh8389/bizcity-platform/blob/main/docs/standard/BIZCITY-SPINE-v1.md) | trục `tenant` do repo này làm chủ |
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
