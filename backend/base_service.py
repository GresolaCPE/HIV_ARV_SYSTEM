import functools
from datetime import datetime

from backend.storage import JSONStorage


def guarded(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (OSError, ValueError) as error:
            return False, f"Could not complete the request: {error}"

    return wrapper


class BaseService:
    def __init__(self, storage=None):
        self.storage = storage or JSONStorage()

    @staticmethod
    def today():
        return datetime.now().date()

    @staticmethod
    def timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parse_date(text):
        try:
            return datetime.strptime(str(text).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def parse_positive_int(value):
        try:
            number = int(str(value).strip())
        except (TypeError, ValueError):
            return None

        return number if number > 0 else None

    @staticmethod
    def next_id(prefix, records, key):
        highest = 0

        for record in records:
            value = str(record.get(key, ""))

            if value.startswith(prefix + "-"):
                try:
                    highest = max(highest, int(value.split("-")[1]))
                except ValueError:
                    continue

        return f"{prefix}-{highest + 1:04d}"

    @staticmethod
    def staff_label(staff):
        if not staff:
            return "System"

        name = str(staff.get("full_name", "")).strip()
        staff_id = str(staff.get("staff_id", "")).strip()

        if name and staff_id:
            return f"{name} ({staff_id})"

        return name or staff_id or "System"

    def parse_range(self, start_text, end_text):
        start_text = str(start_text or "").strip()
        end_text = str(end_text or "").strip()

        start = self.parse_date(start_text) if start_text else None
        end = self.parse_date(end_text) if end_text else None

        if start_text and start is None:
            return None, None, "Start date must be in YYYY-MM-DD format."

        if end_text and end is None:
            return None, None, "End date must be in YYYY-MM-DD format."

        if start and end and start > end:
            return None, None, "Start date cannot be after end date."

        return start, end, None

    def in_range(self, value, start, end):
        day = self.parse_date(str(value)[:10])

        if day is None:
            return False

        if start and day < start:
            return False

        if end and day > end:
            return False

        return True
