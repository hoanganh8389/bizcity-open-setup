# Copyright (c) 2026 Johnny Chu (Chu Hoàng Anh) / BizCity. GPL-2.0-or-later. See LICENSE.
# [2026-11-21 10:48 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 — W1: việc nền gửi lệnh sang Provisioning API, hỏi trạng thái tới khi xong (R-JOB-1, R-IDEM-1); đồng bộ mỗi giờ từ Site Registry (D001-10)
"""Phần dán vào Frappe: tạo `Bizcity Provision Job`, đẩy vào hàng đợi, chạy, cập nhật `Bizcity Ketoan Site`.

Site Manager không chạy migration, không chạm PostgreSQL (R-ROLE-3): mọi việc đi qua Provisioning API.
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import get_datetime, now_datetime

from bizcity_site_manager.provisioning import ProvisioningError
from bizcity_site_manager.relay import owner_from_result, poll_job

JOB = "Bizcity Provision Job"
SITE = "Bizcity Ketoan Site"
SETTINGS = "Bizcity Site Manager Settings"
POLL_TIMEOUT = 600  # giây
WRITE_KINDS = ("provision", "suspend", "resume", "backup", "delete")
LICENSE_STATES = ("ok", "expiring", "expired", "missing", "unknown")
OWNER_KEEP_HOURS = 24  # [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — mật khẩu ban đầu chưa ai nhận thì xoá sau 24 giờ (khách đặt lại qua email)


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

		# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — ghi bước sau MỖI lần hỏi (trang dùng thử hiện console ngay, không chờ xong)
		def progress(remote: dict) -> None:
			job.db_set("steps", json.dumps(remote.get("steps") or [], ensure_ascii=False, indent=1), update_modified=False)
			frappe.db.commit()

		result = poll_job(client, out["jobId"], max(1, settings.poll_seconds or 2), POLL_TIMEOUT, on_progress=progress)
		# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — lần đọc cuối là lần duy nhất Open Kế Toán trả mật khẩu ban đầu → giữ mã hoá ngay (relay.py)
		owner = owner_from_result(result) if job.kind == "provision" else None
		if owner:
			keep_owner(job, owner)
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
	# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — nạp dữ liệu mẫu khi khách xin (bizcity-web luôn gửi sample = 1, D02-8)
	if site.get("sample"):
		body["sample"] = True
	return body


# [2026-11-22 08:05 PM Johnny Chu - Chu Hoàng Anh] PHASE-001 B2 — giữ / trao / xoá mật khẩu ban đầu. Mật khẩu nằm ở bảng __Auth của Frappe (mã hoá), không ở cột, không ở nhật ký.
def keep_owner(job, owner: tuple[str, str]) -> None:
	from frappe.utils.password import set_encrypted_password

	set_encrypted_password(JOB, job.name, owner[1], "owner_password")
	job.db_set({"owner_email": owner[0], "owner_password": "*" * 8, "owner_kept_at": now_datetime()}, update_modified=False)


def take_owner(job_name: str) -> tuple[str, str] | None:
	"""Trao mật khẩu ban đầu đúng MỘT lần rồi xoá. Gọi từ api.job_status sau khi đã kiểm external_ref."""
	from frappe.utils.password import get_decrypted_password, remove_encrypted_password

	row = frappe.db.get_value(JOB, job_name, ["owner_email", "owner_delivered_at"], as_dict=True)
	if not row or row.owner_delivered_at:
		return None
	pwd = get_decrypted_password(JOB, job_name, "owner_password", raise_exception=False)
	if not pwd:
		return None
	remove_encrypted_password(JOB, job_name, "owner_password")
	frappe.db.set_value(JOB, job_name, {"owner_password": None, "owner_delivered_at": now_datetime()}, update_modified=False)
	frappe.db.commit()
	return row.owner_email or "", pwd


def purge_owner_passwords() -> None:
	"""Việc mỗi giờ: xoá mật khẩu ban đầu không ai nhận sau OWNER_KEEP_HOURS giờ."""
	from frappe.utils import add_to_date
	from frappe.utils.password import remove_encrypted_password

	cutoff = add_to_date(now_datetime(), hours=-OWNER_KEEP_HOURS)
	for name in frappe.get_all(JOB, filters={"owner_kept_at": ["<", cutoff], "owner_delivered_at": ["is", "not set"], "owner_password": ["is", "set"]}, pluck="name"):
		remove_encrypted_password(JOB, name, "owner_password")
		frappe.db.set_value(JOB, name, {"owner_password": None}, update_modified=False)
	frappe.db.commit()


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
