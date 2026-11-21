# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: ca kiểm lớp gọi Provisioning API trên máy chủ giả (R-SLUG-1, R-IDEM-1, R-DATA-1, R-KEY-1)
"""Chạy: `python -m unittest discover -s apps/bizcity_site_manager -p "test_*.py"` (không cần Frappe)."""

from __future__ import annotations

import socket
import unittest
import uuid

from bizcity_site_manager.provisioning import ProvisioningClient, ProvisioningError, check_slug
from bizcity_site_manager.tests.fake_provisioning import serve

KEY = "prov_test_" + uuid.uuid4().hex[:8]


def ulid() -> str:
    return uuid.uuid4().hex


class SlugTest(unittest.TestCase):
    def test_hop_le(self) -> None:
        for s in ("anphat", "cong-ty-a", "abc", "a" * 30, "kt2026"):
            self.assertIsNone(check_slug(s), s)

    def test_khong_hop_le(self) -> None:
        for s in ("ab", "a" * 31, "Anphat", "1abc", "abc-", "a--b", "-abc", "abc;reboot", "../x", "an phat", "anphát", "", "www", "ketoan", "admin"):
            self.assertEqual(check_slug(s), "SITE_SLUG_INVALID", s)

    def test_danh_sach_cam_them(self) -> None:
        self.assertEqual(check_slug("riengtoi", {"riengtoi"}), "SITE_SLUG_INVALID")


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.server, self.state = serve(KEY)
        self.c = ProvisioningClient(f"http://127.0.0.1:{self.server.server_address[1]}", KEY, timeout=5)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def _body(self, slug: str = "anphat") -> dict:
        return {"slug": slug, "domain": f"{slug}.btnet.vn", "displayName": "Công ty An Phát",
                "owner": {"email": "chu@anphat.vn", "name": "Nguyễn Văn A"}, "externalRef": "wp:12345"}

    def _wait(self, job_id: str) -> dict:
        for _ in range(5):
            job = self.c.get_job(job_id)
            if job["status"] in ("done", "failed"):
                return job
        self.fail("việc không xong")

    def test_tao_site_viec_bat_dong_bo(self) -> None:
        out = self.c.create_site(self._body(), ulid())
        self.assertIn("jobId", out)
        self.assertEqual(self.c.get_job(out["jobId"])["status"], "running")
        self.assertEqual(self._wait(out["jobId"])["status"], "done")
        site = self.c.get_site(out["siteId"])
        self.assertEqual(site["status"], "active")
        self.assertEqual(site["externalRef"], "wp:12345")
        self.assertNotIn("dbName", site)  # R-ROLE-3: không lộ thông tin database

    def test_gui_lai_cung_idempotency_key_khong_tao_site_thu_hai(self) -> None:
        k = ulid()
        a = self.c.create_site(self._body(), k)
        b = self.c.create_site(self._body(), k)
        self.assertEqual(a, b)
        self.assertEqual(len(self.c.list_sites()["items"]), 1)

    def test_cung_khoa_khac_than_lenh_bi_tu_choi(self) -> None:
        k = ulid()
        self.c.create_site(self._body("anphat"), k)
        with self.assertRaises(ProvisioningError) as e:
            self.c.create_site(self._body("binhminh"), k)
        self.assertEqual(e.exception.code, "IDEMPOTENCY_KEY_REUSED")
        self.assertEqual(e.exception.http_status, 422)

    def test_slug_trung_co_cau_de_hieu(self) -> None:
        self.c.create_site(self._body(), ulid())
        with self.assertRaises(ProvisioningError) as e:
            self.c.create_site(self._body(), ulid())
        self.assertEqual(e.exception.code, "SITE_SLUG_TAKEN")
        self.assertIn("chọn tên khác", e.exception.message)

    def test_slug_doc_bi_chan_truoc_khi_goi_mang(self) -> None:
        with self.assertRaises(ProvisioningError) as e:
            self.c.create_site(self._body("abc;reboot"), ulid())
        self.assertEqual(e.exception.code, "SITE_SLUG_INVALID")
        self.assertEqual(self.state.sites, {})

    def test_lenh_ghi_thieu_idempotency_key(self) -> None:
        with self.assertRaises(ProvisioningError) as e:
            self.c.suspend("S1", "")
        self.assertEqual(e.exception.code, "IDEMPOTENCY_KEY_REQUIRED")

    def test_khoa_provisioning_sai(self) -> None:
        bad = ProvisioningClient(self.c.base_url, "prov_sai", timeout=5)
        with self.assertRaises(ProvisioningError) as e:
            bad.health()
        self.assertEqual(e.exception.code, "PROVISION_KEY_INVALID")
        self.assertEqual(e.exception.http_status, 401)

    def test_xoa_can_khoa_va_sao_luu_truoc(self) -> None:  # R-DATA-1
        out = self.c.create_site(self._body(), ulid())
        self._wait(out["jobId"])
        sid = out["siteId"]
        with self.assertRaises(ProvisioningError) as e:
            self.c.delete(sid, ulid())
        self.assertEqual(e.exception.code, "SITE_NOT_SUSPENDED")
        self._wait(self.c.suspend(sid, ulid())["jobId"])
        with self.assertRaises(ProvisioningError) as e:
            self.c.delete(sid, ulid())
        self.assertEqual(e.exception.code, "SITE_BACKUP_REQUIRED")
        self._wait(self.c.backup(sid, ulid())["jobId"])
        self._wait(self.c.delete(sid, ulid())["jobId"])
        self.assertEqual(self.c.get_site(sid)["status"], "deleted")

    def test_gan_khoa_ban_quyen(self) -> None:
        out = self.c.create_site(self._body(), ulid())
        site = self.c.set_license(out["siteId"], "biz-" + "0" * 32, ulid())
        self.assertEqual(site["license"]["status"], "ok")

    def test_mat_mang_bao_cau_de_hieu(self) -> None:
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        dead = ProvisioningClient(f"http://127.0.0.1:{port}", KEY, timeout=2)
        with self.assertRaises(ProvisioningError) as e:
            dead.health()
        self.assertEqual(e.exception.code, "NETWORK")
        self.assertIn("Thử lại", e.exception.message)


if __name__ == "__main__":
    unittest.main()
