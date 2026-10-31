
import json
import os
import uuid
from datetime import date
from backend.storage import JSONStorage
from .security_service import SecurityService

class PatientService:
    def __init__(self):
        self.storage = JSONStorage()
        self.security = SecurityService(self.storage)
        self.file_name = "patients.json"
        self._merge_legacy_patients()

    def _merge_legacy_patients(self):
        """One-time rescue of patients saved by older versions in <project>/data."""
        legacy = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "patients.json"
        )
        if not os.path.exists(legacy):
            return
        try:
            with open(legacy, "r", encoding="utf-8") as file:
                old = json.load(file)
            if not isinstance(old, list):
                return
            current = self._load_all()
            known = {p.get("patient_id") for p in current}
            missing = [p for p in old if p.get("patient_id") not in known]
            if missing:
                self._save_all(current + missing)
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    def _load_all(self):
        try:
            data = self.storage.load(self.file_name)
            return data if isinstance(data, list) else []
        except (ValueError, OSError):
            return []

    def _save_all(self, patients):
        self.storage.save(self.file_name, patients)

    def add_patient_profile(self, profile):
        patients = self._load_all()

        required_fields = {
            "full_name": "Full name",
            "date_of_birth": "Date of birth",
            "diagnosis": "Diagnosis",
            "attending_physician": "Attending physician"
        }

        for field, label in required_fields.items():
            if not str(profile.get(field, "")).strip():
                return False, f"{label} is required."

        date_of_birth = str(profile["date_of_birth"]).strip()

        try:
            dob = date.fromisoformat(date_of_birth)
            if dob > date.today():
                return False, "Date of birth cannot be in the future."
        except ValueError:
            return False, "Date of birth must use YYYY-MM-DD format."

        age = date.today().year - dob.year
        if (date.today().month, date.today().day) < (dob.month, dob.day):
            age -= 1

        patient_id = "PT-" + uuid.uuid4().hex[:8].upper()

        new_patient = {
            "patient_id": patient_id,
            "full_name": str(profile.get("full_name", "")).strip(),
            "date_of_birth": date_of_birth,
            "age": age,
            "sex": profile.get("sex", ""),
            "contact_number": profile.get("contact_number", ""),
            "address": profile.get("address", ""),
            "emergency_contact": profile.get("emergency_contact", ""),
            "emergency_relationship": profile.get("emergency_relationship", ""),
            "diagnosis": str(profile.get("diagnosis", "")).strip(),
            "diagnosis_date": profile.get("diagnosis_date", ""),
            "medical_history": profile.get("medical_history", ""),
            "conditions": profile.get("conditions", ""),
            "allergies": profile.get("allergies", ""),
            "current_medications": profile.get("current_medications", ""),
            "clinical_notes": profile.get("clinical_notes", ""),
            "attending_physician": str(
                profile.get("attending_physician", "")
            ).strip(),
            "arv_regimen": profile.get("arv_regimen", ""),
            "treatment_start": profile.get("treatment_start", ""),
            "treatment_status": profile.get("treatment_status", ""),
            "next_appointment": profile.get("next_appointment", ""),
            "follow_up_notes": profile.get("follow_up_notes", ""),
            "date_registered": date.today().isoformat()
        }

        patients.append(new_patient)
        self._save_all(patients)
        return True, new_patient

    def get_patients(self, search_text=""):
        patients = self._load_all()
        search_text = str(search_text).strip().lower()

        if search_text:
            patients = [
                patient for patient in patients
                if search_text in str(patient.get("patient_id", "")).lower()
                or search_text in str(patient.get("full_name", "")).lower()
            ]

        return True, patients

    
    def update_patient(self, patient_id, updated_profile, staff=None):
        patients = self._load_all()

        patient_index = next(
            (
                index for index, patient in enumerate(patients)
                if patient.get("patient_id") == patient_id
            ),
            None
        )

        if patient_index is None:
            return False, "Patient record not found."

        old_patient = patients[patient_index]

        required_fields = {
            "full_name": "Full name",
            "date_of_birth": "Date of birth",
            "diagnosis": "Diagnosis",
            "attending_physician": "Attending physician"
        }

        for field, label in required_fields.items():
            value = updated_profile.get(
                field, old_patient.get(field, "")
            )
            if not str(value).strip():
                return False, f"{label} is required."

        date_of_birth = str(old_patient.get("date_of_birth", "")).strip()

        try:
            dob = date.fromisoformat(date_of_birth)
            if dob > date.today():
                return False, "Date of birth cannot be in the future."
        except ValueError:
            return False, "Date of birth must use YYYY-MM-DD format."

        age = date.today().year - dob.year
        if (date.today().month, date.today().day) < (dob.month, dob.day):
            age -= 1

        # Keep patient identity fields fixed after initial registration.
        # This is enforced in the service as well as the GUI, so a caller
        # cannot change the name, date of birth, or sex through an update.
        updated_patient = old_patient.copy()
        updated_patient.update(updated_profile)
        for identity_field in ("full_name", "date_of_birth", "sex"):
            if identity_field in old_patient:
                updated_patient[identity_field] = old_patient[identity_field]
        updated_patient["patient_id"] = patient_id
        updated_patient["date_registered"] = old_patient.get(
            "date_registered", ""
        )
        updated_patient["date_of_birth"] = date_of_birth
        updated_patient["age"] = age

        # Save the updated patient without creating a duplicate.
        patients[patient_index] = updated_patient
        self._save_all(patients)

        staff = staff or {}

        self.security.log_patient_edit(
            patient_id=patient_id,
            username=staff.get("username", "System"),
            staff_id=staff.get("staff_id", "System"),
            full_name=staff.get("full_name", "System"),
            action_type="UPDATE",
            changes_summary="Updated patient profile.",
            previous_data=old_patient,
            new_data=updated_patient
        )

        return True, updated_patient

    def get_patient_by_id(self, patient_id):
        for patient in self._load_all():
            if patient.get("patient_id") == patient_id:
                return True, patient

        return False, "Patient record not found."

    def delete_patient(self, patient_id):
        patients = self._load_all()

        target_patient = next((p for p in patients if p.get("patient_id") == patient_id), None)

        updated_patients = [
            patient for patient in patients
            if patient.get("patient_id") != patient_id
        ]

        if len(updated_patients) == len(patients):
            return False, "Patient record not found."

        self._save_all(updated_patients)

        return True, "Patient record deleted successfully."