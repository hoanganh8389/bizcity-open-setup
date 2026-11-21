# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: việc nền gửi lệnh sang Provisioning API, hỏi trạng thái tới khi xong (R-JOB-1, R-IDEM-1); đồng bộ mỗi giờ từ Site Registry (D001-10)
"""Phần dán vào Frappe: tạo `Bizcity Provision Job`, đẩy vào hàng đợi, chạy, cập nhật `Bizcity Ketoan Site`.

Site Manager không chạy migration, không chạm PostgreSQL (R-ROLE-3): mọi việc đi qua Provisioning API.
"""

from __future__ import annotations

import json
import time

import frappe
from frappe.utils import get_datetime, now_datetime

from bizcity_site_manager.provisioning import ProvisioningError

JOB = "Bizcity Provision Job"
SITE = "Bizcity Ketoan Site"
SETTINGS = "Bizcity Site Manager Settings"
POLL_TIMEOUT = 600  # giây
WRITE_KINDS = ("provision", "suspend", "resume", "backup", "delete")
LICENSE_STATES = ("ok", "expiring", "expired", "missing", "unknown")


def start(site_name: str, kind: str) -> str:
	"""Tạo một việc và đẩy vào hàng đợi `long`. Trả tên việc."""
	if kind not in WRITE_KINDS:
		frappe.throw(f"Lệnh không hợp lệ: {kind}")
	job = frappe.get_doc({
		"doctype": JOB,
		"site": site_name,
		"kind": kind,
		"status": "queued",
		"idempotency_key": frappe.generate_hash(length=32),
	}).insert(ignore_permissions=True)
	frappe.enqueue(
		"bizcity_site_manager.site_manager.run",
		job_name=job.name,
		queue="long",
		timeout=POLL_TIMEOUT + 120,
		enqueue_after_commit=True,
	)
	return job.name


def run(job_name: str) -> None:
	"""Chạy một việc. Chạy lại được: cùng Idempotency-Key nên Open Kế Toán trả đúng việc cũ, không tạo site thứ hai."""
	job = frappe.get_doc(JOB, job_name)
	site = frappe.get_doc(SITE, job.site)
	settings = frappe.get_single(SETTINGS)
	job.db_set("attempts", (job.attempts or 0) + 1)
	try:
		client = settings.client()
		if job.kind == "provision":
			out = client.create_site(_create_body(site), job.idempotency_key)
			site.db_set({"site_id": out["siteId"], "status": "provisioning", "last_error": None})
		else:
			if not site.site_id:
				raise ProvisioningError("SITE_NOT_FOUND", 404, "site chưa có mã bên Open Kế Toán")
			out = getattr(client, job.kind)(site.site_id, job.idempotency_key)
		job.db_set({"remote_job_id": out["jobId"], "status": "running"})
		frappe.db.commit()

		result = _poll(client, out["jobId"], max(1, settings.poll_seconds or 2))
		job.db_set({"steps": json.dumps(result.get("steps") or [], ensure_ascii=False, indent=1), "status": result["status"]})
		if result["status"] != "done":
			err = result.get("error") or {}
			raise ProvisioningError(str(err.get("code") or "JOB_FAILED"), 0, str(err.get("message") or ""))
		refresh(site, client.get_site(site.site_id))
	except ProvisioningError as e:
		job.db_set({"status": "failed", "error_code": e.code, "error_message": e.message})
		site.db_set("last_error", f"{e.code}: {e.message}")
		if job.kind == "provision" and site.status in ("pending", "provisioning"):
			site.db_set("status", "failed")
		frappe.log_error(title=f"Site Manager: {job.kind} {site.name} lỗi {e.code}", message=e.detail)
	frappe.db.commit()


def _create_body(site) -> dict:
	cust = frappe.get_doc("Bizcity Site Customer", site.customer)
	body = {
		"slug": site.slug,
		"domain": site.domain,
		"displayName": cust.company_name,
		"owner": {"email": cust.email, "name": cust.full_name, "phone": cust.phone or ""},
	}
	if cust.external_ref:
		body["externalRef"] = cust.external_ref
	return body


def _poll(client, remote_job_id: str, every: int) -> dict:
	deadline = time.monotonic() + POLL_TIMEOUT
	while True:
		job = client.get_job(remote_job_id)
		if job.get("status") in ("done", "failed"):
			return job
		if time.monotonic() > deadline:
			raise ProvisioningError("JOB_TIMEOUT", 0, f"việc {remote_job_id} quá {POLL_TIMEOUT} giây")
		time.sleep(every)


def refresh(site, remote: dict) -> None:
	"""Chép trạng thái từ Site Registry về bản điều hành (lệch thì tin registry, D001-10)."""
	lic = (remote.get("license") or {}).get("status") or "unknown"
	site.db_set({
		"status": remote.get("status") or site.status,
		"schema_version": remote.get("schemaVersion"),
		"app_version": remote.get("appVersion"),
		"license_status": lic if lic in LICENSE_STATES else "unknown",
		"last_backup_at": _dt(remote.get("lastBackupAt")),
		"last_synced_at": now_datetime(),
	})


def sync_all() -> None:
	"""Việc mỗi giờ (hooks.py): đọc toàn bộ registry theo trang, cập nhật site đã biết. Site lạ chỉ ghi nhật ký."""
	settings = frappe.get_single(SETTINGS)
	if not settings.provisioning_url:
		return
	client = settings.client()
	known = {r.site_id: r.name for r in frappe.get_all(SITE, fields=["name", "site_id"], filters={"site_id": ["is", "set"]})}
	cursor = None
	unknown = []
	while True:
		page = client.list_sites(cursor=cursor)
		for remote in page.get("items") or []:
			name = known.get(remote.get("siteId"))
			if name:
				refresh(frappe.get_doc(SITE, name), remote)
			else:
				unknown.append(str(remote.get("siteId")))
		cursor = page.get("next")
		if not cursor:
			break
	frappe.db.commit()
	if unknown:
		frappe.log_error(title="Site Manager: site có ở Open Kế Toán, chưa có ở Site Manager", message=", ".join(unknown))


def _dt(value):
	if not value:
		return None
	return get_datetime(str(value)[:19].replace("T", " "))
