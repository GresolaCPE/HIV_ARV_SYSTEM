
import json
import os
import uuid
from datetime import date


class PatientService:
    def __init__(self):
        self.data_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )
        self.file_path = os.path.join(
            self.data_folder, "patients.json"
        )

        os.makedirs(self.data_folder, exist_ok=True)

        if not os.path.exists(self.file_path):
            self._save_all([])

    def _load_all(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            return []

    def _save_all(self, patients):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(patients, file, indent=4, ensure_ascii=False)

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

    def get_patient_by_id(self, patient_id):
        for patient in self._load_all():
            if patient.get("patient_id") == patient_id:
                return True, patient

        return False, "Patient record not found."

    def delete_patient(self, patient_id):
        patients = self._load_all()

        updated_patients = [
            patient for patient in patients
            if patient.get("patient_id") != patient_id
        ]

        if len(updated_patients) == len(patients):
            return False, "Patient record not found."

        self._save_all(updated_patients)
        return True, "Patient record deleted successfully."
