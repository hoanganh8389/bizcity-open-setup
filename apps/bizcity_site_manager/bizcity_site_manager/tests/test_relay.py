# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — ca kiểm phần chuyển tiếp cho trang dùng thử bizcity-web: bước từng lần, mật khẩu ban đầu nhặt đúng một lần, mã lỗi cố định
"""Chạy: `python -m unittest discover -s apps/bizcity_site_manager -p "test_*.py"` (không cần Frappe)."""

from __future__ import annotations

import unittest
import uuid

from bizcity_site_manager.provisioning import ProvisioningClient, ProvisioningError
from bizcity_site_manager.relay import error_body, owner_from_result, parse_steps, poll_job, public_job, ref_matches
from bizcity_site_manager.tests.fake_provisioning import serve

KEY = "prov_test_" + uuid.uuid4().hex[:8]


class RelayLiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server, cls.state = serve(KEY)
        cls.client = ProvisioningClient(f"http://127.0.0.1:{cls.server.server_address[1]}", KEY, timeout=5)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()

    def _create(self, slug: str) -> str:
        out = self.client.create_site({
            "slug": slug, "domain": f"{slug}.kt.bizcity.vn", "displayName": "An Phát",
            "owner": {"email": "chu@anphat.vn", "name": "Chu"}, "sample": True, "externalRef": "7",
        }, uuid.uuid4().hex)
        return out["jobId"]

    def test_bao_buoc_tung_lan_va_nhat_mat_khau_mot_lan(self) -> None:
        job_id = self._create("anphat-relay")
        seen: list[list[dict]] = []
        result = poll_job(self.client, job_id, 0, 30, on_progress=lambda j: seen.append(parse_steps(j.get("steps"))), sleep=lambda s: None)
        self.assertEqual(result["status"], "done")
        self.assertGreaterEqual(len(seen), 2, "mỗi lần đọc phải báo bước")
        self.assertEqual([s["status"] for s in seen[-1]], ["done"] * 4)
        owner = owner_from_result(result)
        self.assertIsNotNone(owner)
        self.assertEqual(owner[0], "chu@anphat.vn")
        self.assertTrue(owner[1].startswith("Pw-"))
        # Lần đọc sau không còn mật khẩu — bỏ lỡ lần đầu là mất (vì vậy Site Manager phải nhặt ngay).
        self.assertIsNone(owner_from_result(self.client.get_job(job_id)))

    def test_sample_va_external_ref_gui_sang(self) -> None:
        self._create("anphat-sample")
        site = next(s for s in self.state.sites.values() if s["slug"] == "anphat-sample")
        self.assertTrue(site["sample"])
        self.assertEqual(site["externalRef"], "7")

    # [2026-11-22 10:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 W1c — đặt lại mật khẩu chủ site: mật khẩu mới một lần; site khoá thì từ chối
    def test_dat_lai_mat_khau_chu_site(self) -> None:
        job_id = self._create("anphat-reset")
        poll_job(self.client, job_id, 0, 30, sleep=lambda s: None)
        site_id = next(s["siteId"] for s in self.state.sites.values() if s["slug"] == "anphat-reset")
        out = self.client.reset_owner_password(site_id, uuid.uuid4().hex)
        result = poll_job(self.client, out["jobId"], 0, 30, sleep=lambda s: None)
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["steps"], [{"key": "reset_password", "status": "done"}])
        owner = owner_from_result(result)
        self.assertIsNotNone(owner)
        self.assertEqual(owner[0], "chu@anphat.vn")
        self.assertIsNone(owner_from_result(self.client.get_job(out["jobId"])))

    def test_dat_lai_mat_khau_site_dang_khoa(self) -> None:
        job_id = self._create("anphat-khoa")
        poll_job(self.client, job_id, 0, 30, sleep=lambda s: None)
        site_id = next(s["siteId"] for s in self.state.sites.values() if s["slug"] == "anphat-khoa")
        self.state.sites[site_id]["status"] = "suspended"
        with self.assertRaises(ProvisioningError) as ctx:
            self.client.reset_owner_password(site_id, uuid.uuid4().hex)
        self.assertEqual(ctx.exception.code, "SITE_STATE_INVALID")

    def test_ma_loi_lenh_dat_lai(self) -> None:
        self.assertEqual(error_body("SITE_NOT_ACTIVE")[0], 409)
        self.assertEqual(error_body("SITE_NOT_FOUND")[0], 404)
        self.assertEqual(error_body("SITE_BUSY")[0], 409)

    def test_qua_gio(self) -> None:
        job_id = self._create("anphat-timeout")
        t = [0.0]

        class Stuck:
            def get_job(self, _id):  # việc không bao giờ xong
                return {"status": "running", "steps": []}

        def clock() -> float:
            t[0] += 10
            return t[0]

        with self.assertRaises(ProvisioningError) as ctx:
            poll_job(Stuck(), job_id, 0, 25, sleep=lambda s: None, clock=clock)
        self.assertEqual(ctx.exception.code, "JOB_TIMEOUT")


class RelayShapeTest(unittest.TestCase):
    def test_parse_steps_bo_rac(self) -> None:
        raw = '[{"key":"validate","status":"done"},{"key":"x","status":"weird"},{"status":"done"},"rac"]'
        self.assertEqual(parse_steps(raw), [{"key": "validate", "status": "done"}])
        self.assertEqual(parse_steps("không phải json"), [])
        self.assertEqual(parse_steps(None), [])

    def test_public_job_chi_co_owner_khi_trao(self) -> None:
        base = dict(status="done", kind="provision", site="anphat", domain="anphat.kt.bizcity.vn",
                    steps_raw="[]", error_code=None, error_message=None)
        self.assertNotIn("owner", public_job(**base))
        with_owner = public_job(**base, owner=("chu@anphat.vn", "Pw-1"))
        self.assertEqual(with_owner["owner"], {"email": "chu@anphat.vn", "initialPassword": "Pw-1"})

    def test_ma_loi_co_dinh(self) -> None:
        self.assertEqual(error_body("SITE_SLUG_TAKEN")[0], 409)
        self.assertEqual(error_body("TRIAL_EXISTS")[1]["error"]["code"], "TRIAL_EXISTS")
        self.assertEqual(error_body("JOB_NOT_FOUND")[0], 404)
        status, body = error_body("LA_LAM")
        self.assertEqual(status, 500)
        self.assertTrue(body["error"]["message"])

    def test_ref_phai_trung_va_khong_rong(self) -> None:
        self.assertTrue(ref_matches("7", "7"))
        self.assertFalse(ref_matches("7", "8"))
        self.assertFalse(ref_matches("", ""))
        self.assertFalse(ref_matches(None, None))
        self.assertFalse(ref_matches("7", None))


if __name__ == "__main__":
    unittest.main()
