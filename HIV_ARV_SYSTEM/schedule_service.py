from datetime import date
from backend.storage import JSONStorage
from backend.patient_service import PatientService
from backend.security_service import SecurityService


class ScheduleService:
    def __init__(self):
        self.patient_service = PatientService()
        self.storage = JSONStorage()

        self.security_service = SecurityService(self.storage)

    def get_all_patients(self):
        """Return all registered patients."""
        success, patients = self.patient_service.get_patients()

        if not success:
            return False, patients

        return True, patients

    def get_appointments_by_date(self, appointment_date):
        """
        Return patients scheduled for a particular date.
        Date format: YYYY-MM-DD
        """
        success, patients = self.get_all_patients()

        if not success:
            return False, patients

        appointments = [
            patient
            for patient in patients
            if str(patient.get("next_appointment", "")).strip()
            == appointment_date
        ]

        return True, appointments

    def get_appointments_today(self):
        """Return patients scheduled for today."""
        today = date.today().isoformat()
        return self.get_appointments_by_date(today)

    def update_appointment(
        self,
        patient_id,
        appointment_date,
        follow_up_notes,
        staff=None
    ):
        """Update an existing patient's appointment details."""

        # Validate the date if one was provided.
        if appointment_date:
            try:
                date.fromisoformat(appointment_date)
            except ValueError:
                return False, "Invalid date. Use YYYY-MM-DD."

        success, patients = self.get_all_patients()

        if not success:
            return False, patients

        patient = next(
            (
                item for item in patients
                if str(item.get("patient_id", item.get("id", "")))
                == str(patient_id)
            ),
            None
        )

        if patient is None:
            return False, "Patient record was not found."

        updated_profile = {
            "next_appointment": appointment_date,
            "follow_up_notes": follow_up_notes
        }

        return self.patient_service.update_patient(
            patient_id,
            updated_profile,
            staff=staff
        )
    
