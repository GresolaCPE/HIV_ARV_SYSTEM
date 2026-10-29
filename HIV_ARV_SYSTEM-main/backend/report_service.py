"""Data helpers for printable system reports."""
from collections import defaultdict
from backend.storage import JSONStorage


class ReportService:
    def __init__(self, storage=None):
        self.storage = storage or JSONStorage()

    def _list(self, filename):
        value = self.storage.load(filename)
        return value if isinstance(value, list) else []

    def patients(self, search=""):
        rows = self._list("patients.json")
        search = str(search).strip().casefold()
        if search:
            rows = [r for r in rows if search in str(r.get("patient_id", "")).casefold()
                    or search in str(r.get("full_name", "")).casefold()]
        return rows

    def patient(self, patient_id):
        return next((p for p in self._list("patients.json")
                     if str(p.get("patient_id", "")) == str(patient_id).strip()), None)

    def patient_history(self, patient_id):
        rows = [r for r in self._list("patient_audit.json")
                if str(r.get("patient_id", "")) == str(patient_id).strip()]
        return sorted(rows, key=lambda r: (r.get("timestamp", ""), r.get("version", 0)))

    def allocations(self, patient_id=""):
        rows = self._list("allocations.json")
        if patient_id:
            rows = [r for r in rows if str(r.get("patient_id", "")) == str(patient_id).strip()]
        return sorted(rows, key=lambda r: r.get("allocation_date", ""))

    def transactions(self):
        rows = self._list("stock_transactions.json")
        return sorted(rows, key=lambda r: r.get("transaction_date", ""))

    def stock_summary(self):
        totals = defaultdict(int)
        for row in self.transactions():
            kind = str(row.get("transaction_type", "")).upper()
            qty = int(row.get("quantity", 0) or 0)
            if kind == "STOCK IN":
                totals["stock_in"] += qty
            elif kind == "STOCK OUT":
                totals["stock_out"] += qty
        return dict(totals)
