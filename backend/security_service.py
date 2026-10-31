import os
import json
from datetime import datetime, timezone
from backend.storage import JSONStorage


class SecurityService:
    def __init__(self, storage=None):
        self.storage = storage or JSONStorage()
        self.login_log_file = "login_audit.json"
        self.patient_audit_file = "patient_audit.json"
        self.service_audit_file = "service_audit.json"
        self._ensure_files()

    def _ensure_files(self):
        """Ensure security and audit log files exist with proper initial structure."""
        login_data = self.storage.load(self.login_log_file)
        if not isinstance(login_data, list):
            self.storage.save(self.login_log_file, [])

        patient_audit_data = self.storage.load(self.patient_audit_file)
        if not isinstance(patient_audit_data, list):
            self.storage.save(self.patient_audit_file, [])

        service_audit_data = self.storage.load(self.service_audit_file)
        if not isinstance(service_audit_data, list):
            self.storage.save(self.service_audit_file, [])

    def log_service_edit(self, service_name, record_id, action_type, changes_summary,
                         username="System", staff_id="System", full_name="System",
                         previous_data=None, new_data=None, success=True):
        """
        Record a change made by a non-patient service (inventory, allocation,
        stock transactions). Kept separate from patient_audit.json so patient
        history reports only contain patient records.
        """
        records = self.storage.load(self.service_audit_file)
        if not isinstance(records, list):
            records = []

        now = datetime.now(timezone.utc)
        entry = {
            "audit_id": f"AUDIT-SV-{len(records) + 1:05d}",
            "service_name": str(service_name),
            "record_id": str(record_id),
            "action_type": str(action_type).upper(),
            "staff_id": str(staff_id).strip() if staff_id else "System",
            "username": str(username).strip() if username else "System",
            "full_name": str(full_name).strip() if full_name else "System",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
            "changes_summary": str(changes_summary).strip(),
            "previous_data": previous_data or {},
            "new_data": new_data or {},
            "success": bool(success),
        }
        records.insert(0, entry)
        self.storage.save(self.service_audit_file, records)
        return entry

    def log_login_attempt(self, username, staff_id, full_name, success, ip_address="Local"):
        """
        Record a login attempt with timestamp, date, time, user details, and success status.
        Fully open for all users to review login history.
        """
        logs = self.storage.load(self.login_log_file)
        if not isinstance(logs, list):
            logs = []

        now = datetime.now(timezone.utc)
        log_entry = {
            "id": f"LOG-{len(logs) + 1:05d}",
            "username": str(username).strip(),
            "staff_id": str(staff_id).strip() if staff_id else "N/A",
            "full_name": str(full_name).strip() if full_name else "N/A",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
            "status": "SUCCESS" if success else "FAILED",
            "ip_address": ip_address
        }
        logs.insert(0, log_entry)  # Most recent first
        self.storage.save(self.login_log_file, logs)
        return log_entry

    def get_login_logs(self, search_query=""):
        """
        Retrieve all login logs. Open to all users to check who logged in, when, and date/time.
        Optional search query to filter by username, staff ID, or date.
        """
        logs = self.storage.load(self.login_log_file)
        if not isinstance(logs, list):
            return []

        search_query = str(search_query).strip().lower()
        if not search_query:
            return logs

        filtered = [
            log for log in logs
            if search_query in log.get("username", "").lower()
            or search_query in log.get("staff_id", "").lower()
            or search_query in log.get("full_name", "").lower()
            or search_query in log.get("date", "").lower()
            or search_query in log.get("status", "").lower()
        ]
        return filtered

    def log_patient_edit(self, patient_id, username, staff_id, full_name, action_type, changes_summary, previous_data=None, new_data=None):
        """
        Record any modification (Create, Update, Delete) to a patient record, 
        tracking who performed the edit, timestamp, and version increments.
        """
        audit_records = self.storage.load(self.patient_audit_file)
        if not isinstance(audit_records, list):
            audit_records = []

        patient_id = str(patient_id).strip()
            
        # Calculate version number based on previous edits for this patient
        patient_history = [r for r in audit_records if r.get("patient_id") == patient_id]
        next_version = len(patient_history) + 1

        now = datetime.now(timezone.utc)
        audit_entry = {
            "audit_id": f"AUDIT-PT-{len(audit_records) + 1:05d}",
            "patient_id": patient_id,
            "version": next_version,
            "action_type": action_type.upper(),  # CREATE, UPDATE, DELETE
            "staff_id": str(staff_id).strip() if staff_id else "System",
            "username": str(username).strip() if username else "System",
            "full_name": str(full_name).strip() if full_name else "System",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
            "changes_summary": str(changes_summary).strip(),
            "previous_data": previous_data or {},
            "new_data": new_data or {}
        }

        audit_records.insert(0, audit_entry)  # Most recent first
        self.storage.save(self.patient_audit_file, audit_records)
        return audit_entry

    def get_patient_history(self, patient_id):
        """
        Retrieve complete editing history, version timeline, and audit trail 
        for a specific patient record, showing who made each edit and when.
        """
        audit_records = self.storage.load(self.patient_audit_file)
        if not isinstance(audit_records, list):
            return []

        patient_id = str(patient_id).strip()
        history = [r for r in audit_records if r.get("patient_id") == patient_id]
        # Sort chronologically by version
        history.sort(key=lambda x: x.get("version", 1))
        return history

    def get_all_patient_audit_logs(self, search_query=""):
        """
        Retrieve all patient editing history logs across the entire system.
        Fully open to all users to verify who modified patient records and when.
        """
        audit_records = self.storage.load(self.patient_audit_file)
        if not isinstance(audit_records, list):
            return []

        search_query = str(search_query).strip().lower()
        if not search_query:
            return audit_records

        filtered = [
            record for record in audit_records
            if search_query in str(record.get("patient_id", "")).lower()
            or search_query in str(record.get("staff_id", "")).lower()
            or search_query in str(record.get("username", "")).lower()
            or search_query in str(record.get("full_name", "")).lower()
            or search_query in str(record.get("action_type", "")).lower()
            or search_query in str(record.get("date", "")).lower()
            or search_query in str(record.get("changes_summary", "")).lower()
        ]
        return filtered