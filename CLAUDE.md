# CLAUDE.md

Đọc [AGENTS.md](AGENTS.md) — đó là hướng dẫn chuẩn cho mọi agent trong repo này. Tệp này không lặp lại nội dung.

Bốn điều không được quên:

1. Repo mới có **tài liệu và script vận hành**. App Frappe `bizcity_site_manager` và Provisioning API của Open Kế Toán (PHASE-039 bên `open-ketoan`) **chưa có mã**. Đừng giả định lớp hay lệnh nào đã tồn tại.
2. Bốn câu không thương lượng (AGENTS.md): Frappe không giữ dữ liệu kế toán · một site kế toán không phải một Frappe site · Site Manager không chạm PostgreSQL · API key thuộc `bizcity-llm-router`.
3. Sửa tệp thì thêm dấu R-SIG tại chỗ đổi, tên người chỉ đạo, giờ thật của máy; không ghi tên agent.
4. <!-- [2026-11-21 07:52 PM Johnny Chu - Chu Hoàng Anh] OKT-P0 --> Repo này cũng là **trục điều phối chương trình OKT** (`docs/chuong-trinh/OKT/`). Trạng thái việc OKT chỉ ghi ở `40-CHECKLIST.md` tại đây. Bất biến I-0: không đổi luồng bán, logic bán hàng, sổ của open-pos.
