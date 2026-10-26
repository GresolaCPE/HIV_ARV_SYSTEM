import json
import os
import uuid
from datetime import date, datetime, timezone
from backend.patient_history_service import PatientHistoryService
from copy import deepcopy


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

        self.history_service = PatientHistoryService()


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

    def add_patient_profile(self, profile, created_by=""):
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

        optional_dates = {
            "diagnosis_date": "Diagnosis date",
            "treatment_start_date": "Treatment start date",
            "next_appointment": "Next appointment",
        }

        for field, label in optional_dates.items():
            value = str(profile.get(field, "")).strip()

            if value:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    return False, (
                        f"{label} must use YYYY-MM-DD format."
                    )
                
        # Calculate the patient's age.
        age = date.today().year - dob.year

        if (date.today().month, date.today().day) < (dob.month, dob.day):
            age -= 1

        # Generate a unique patient ID.
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
            "conditions": profile.get(
                "other_conditions",
                profile.get("conditions", "")
            ),
            "allergies": profile.get("allergies", ""),
            "current_medications": profile.get("current_medications", ""),
            "clinical_notes": profile.get("clinical_notes", ""),
            "attending_physician": str(
                profile.get("attending_physician", "")
            ).strip(),
            "arv_regimen": profile.get("arv_regimen", ""),
            "treatment_start": profile.get(
                "treatment_start_date",
                profile.get("treatment_start", "")
            ),
            "treatment_status": profile.get("treatment_status", ""),
            "next_appointment": profile.get("next_appointment", ""),
            "follow_up_notes": profile.get("follow_up_notes", ""),
            "date_registered": date.today().isoformat()
        }

        patients.append(new_patient)
        self._save_all(patients)

        history_success, history_result = (
            self.history_service.record_version(
                patient=new_patient,
                updated_by=created_by or "Unknown staff",
                change_type="CREATE",
                changed_fields={
                    "record": {
                        "previous": None,
                        "new": "Initial patient record"
                    }
                }
            )
        )

        if not history_success:
            patients.pop()
            self._save_all(patients)

            return False, (
                "Patient registration was cancelled because the "
                f"history could not be saved: {history_result}"
            )

        return True, new_patient

    
    def update_patient_profile(
        self, patient_id, profile, updated_by=""
    ):
        patients = self._load_all()

        patient = next(
            (
                item for item in patients
                if item.get("patient_id") == patient_id
            ),
            None
        )

        if patient is None:
            return False, "Patient record not found."

        original_patient = deepcopy(patient)

        # Map form field names to the names stored in JSON.
        field_mapping = {
            "diagnosis": "diagnosis",
            "diagnosis_date": "diagnosis_date",
            "medical_history": "medical_history",
            "other_conditions": "conditions",
            "allergies": "allergies",
            "current_medications": "current_medications",
            "clinical_notes": "clinical_notes",
            "attending_physician": "attending_physician",
            "arv_regimen": "arv_regimen",
            "treatment_start_date": "treatment_start",
            "treatment_status": "treatment_status",
            "next_appointment": "next_appointment",
            "follow_up_notes": "follow_up_notes",
        }

        # Check required fields.
        for field, label in {
            "full_name": "Full name",
            "date_of_birth": "Date of birth",
            "diagnosis": "Diagnosis",
            "attending_physician": "Attending physician",
        }.items():
            if not str(profile.get(field, "")).strip():
                return False, f"{label} is required."

        # Validate date of birth.
        try:
            dob = date.fromisoformat(
                str(profile["date_of_birth"]).strip()
            )
            if dob > date.today():
                return False, "Date of birth cannot be in the future."
        except ValueError:
            return False, "Date of birth must use YYYY-MM-DD format."

        # Validate the optional follow-up date.
        appointment = str(
            profile.get("next_appointment", "")
        ).strip()

        if appointment:
            try:
                date.fromisoformat(appointment)
            except ValueError:
                return False, (
                    "Next appointment must use YYYY-MM-DD format."
                )

        # Validate optional dates when provided.
        for field, label in (
            ("diagnosis_date", "Diagnosis date"),
            ("treatment_start_date", "Treatment start date"),
        ):
            value = str(profile.get(field, "")).strip()
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    return False, (
                        f"{label} must use YYYY-MM-DD format."
                    )

        # Calculate the updated age.
        today = date.today()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1

        old_appointment = str(
            patient.get("next_appointment", "")
        ).strip()

        changed_fields = []
        history_changes = {}

        for form_field, stored_field in field_mapping.items():
            new_value = profile.get(form_field, "")

            if isinstance(new_value, str):
                new_value = new_value.strip()

            old_value = patient.get(stored_field, "")

            if old_value != new_value:
                changed_fields.append(stored_field)

                history_changes[stored_field] = {
                    "previous": old_value,
                    "new": new_value
                }

                patient[stored_field] = new_value

        if patient.get("age") != age:
            old_age = patient.get("age")

            patient["age"] = age

            if "age" not in changed_fields:
                changed_fields.append("age")

            history_changes["age"] = {
                "previous": old_age,
                "new": age
            }

        # Preserve the original registration date and patient ID.
        if not changed_fields:
            return True, "No changes were made."

        timestamp = datetime.now(timezone.utc).isoformat()

        # Preserve earlier update history.
        history = patient.get("update_history", [])
        if not isinstance(history, list):
            history = []

        history_entry = {
            "updated_at": timestamp,
            "updated_by": updated_by or "Staff",
            "changed_fields": changed_fields,
        }

        # Record appointment changes explicitly.
        new_appointment = str(
            patient.get("next_appointment", "")
        ).strip()

        if old_appointment != new_appointment:
            history_entry["appointment_change"] = {
                "previous_date": old_appointment,
                "new_date": new_appointment,
            }

        history.append(history_entry)
        patient["update_history"] = history
        patient["last_updated"] = timestamp

        # Save the latest patient record.
        self._save_all(patients)

        # Save a complete snapshot of this version.
        history_success, history_result = (
            self.history_service.record_version(
                patient=patient,
                updated_by=updated_by,
                change_type="UPDATE",
                changed_fields=history_changes
            )
        )

        if not history_success:
            # Restore the original record if history saving fails.
            for index, item in enumerate(patients):
                if item.get("patient_id") == patient_id:
                    patients[index] = original_patient
                    break

            self._save_all(patients)

            return False, (
                "Patient update was rolled back because the history "
                f"could not be saved: {history_result}"
            )

        return True, patient

    
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
