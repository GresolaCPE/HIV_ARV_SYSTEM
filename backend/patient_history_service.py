
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


class PatientHistoryService:
    def __init__(self):
        self.data_directory = Path(__file__).resolve().parent.parent / "data"
        self.history_file = self.data_directory / "patient_history.json"

        self.data_directory.mkdir(parents=True, exist_ok=True)

        if not self.history_file.exists():
            self._save_history([])

    def _load_history(self):
        try:
            with self.history_file.open("r", encoding="utf-8") as file:
                history = json.load(file)

            if not isinstance(history, list):
                raise ValueError("Patient history must be a JSON list.")

            return history

        except (json.JSONDecodeError, OSError, ValueError) as error:
            raise RuntimeError(
                f"Could not load patient history: {error}"
            ) from error

    def _save_history(self, history):
        try:
            with self.history_file.open("w", encoding="utf-8") as file:
                json.dump(history, file, indent=4, ensure_ascii=False)

        except OSError as error:
            raise RuntimeError(
                f"Could not save patient history: {error}"
            ) from error

    def record_version(
        self,
        patient,
        updated_by,
        change_type,
        changed_fields=None
    ):
        if not patient or not patient.get("patient_id"):
            return False, "A valid patient record is required."

        try:
            history = self._load_history()

            patient_id = patient["patient_id"]

            previous_versions = [
                entry for entry in history
                if entry.get("patient_id") == patient_id
            ]

            version_number = len(previous_versions) + 1

            entry = {
                "patient_id": patient_id,
                "patient_name": patient.get("full_name", ""),
                "version": version_number,
                "change_type": change_type,
                "updated_by": updated_by or "Unknown staff",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "changed_fields": deepcopy(changed_fields or {}),
                "record_snapshot": deepcopy(patient)
            }

            history.append(entry)
            self._save_history(history)

            return True, entry

        except (OSError, RuntimeError, ValueError) as error:
            return False, str(error)

    def get_patient_history(self, patient_id):
        try:
            history = self._load_history()

            patient_history = [
                entry for entry in history
                if entry.get("patient_id") == patient_id
            ]

            patient_history.sort(
                key=lambda entry: entry.get("version", 0)
            )

            return True, patient_history

        except (OSError, RuntimeError, ValueError) as error:
            return False, str(error)

    def get_all_history(self):
        try:
            history = self._load_history()

            history.sort(
                key=lambda entry: entry.get("updated_at", ""),
                reverse=True
            )

            return True, history

        except (OSError, RuntimeError, ValueError) as error:
            return False, str(error)
