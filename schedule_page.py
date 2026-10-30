from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QBrush
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
    QTextEdit,
    QMessageBox,
    QFormLayout
)

from schedule_service import ScheduleService
from mail_followup import FollowUpEmailDialog


class SchedulePage(QWidget):
    def __init__(self, user, on_change=None):
        super().__init__()

        self.user = user
        self.on_change = on_change
        self.schedule_service = ScheduleService()
        self.selected_patient = None

        self.create_ui()
        self.refresh_schedule()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        title = QLabel("Patient Schedule")
        title.setObjectName("cardTitle")
        main_layout.addWidget(title)

        description = QLabel(
            "View scheduled appointments and manage follow-up details."
        )
        description.setWordWrap(True)
        main_layout.addWidget(description)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # LEFT SIDE: CALENDAR
        calendar_card = QFrame()
        calendar_card.setObjectName("dashboardCard")
        calendar_layout = QVBoxLayout(calendar_card)

        calendar_title = QLabel("Appointment Calendar")
        calendar_title.setObjectName("cardTitle")
        calendar_layout.addWidget(calendar_title)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(
            self.refresh_appointments_for_selected_date
        )
        self.calendar.currentPageChanged.connect(
            self.highlight_appointment_dates
        )

        calendar_layout.addWidget(self.calendar)

        # RIGHT SIDE: APPOINTMENT TABLE
        appointments_card = QFrame()
        appointments_card.setObjectName("dashboardCard")
        appointments_layout = QVBoxLayout(appointments_card)

        self.date_title = QLabel("Appointments")
        self.date_title.setObjectName("cardTitle")
        appointments_layout.addWidget(self.date_title)

        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(3)
        self.appointment_table.setHorizontalHeaderLabels([
            "Patient ID",
            "Patient Name",
            "Attending Physician"
        ])
        self.appointment_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.appointment_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.appointment_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.appointment_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.appointment_table.itemSelectionChanged.connect(
            self.load_selected_patient
        )

        appointments_layout.addWidget(self.appointment_table)

        content_layout.addWidget(calendar_card, 1)
        content_layout.addWidget(appointments_card, 2)
        main_layout.addLayout(content_layout)

        # FOLLOW-UP DETAILS
        details_card = QFrame()
        details_card.setObjectName("dashboardCard")
        details_layout = QVBoxLayout(details_card)

        details_title = QLabel("Appointment Details")
        details_title.setObjectName("cardTitle")
        details_layout.addWidget(details_title)

        form = QFormLayout()

        self.patient_name_label = QLabel("No patient selected")
        form.addRow("Selected Patient:", self.patient_name_label)

        self.appointment_date = QDateEdit()
        self.appointment_date.setCalendarPopup(True)
        self.appointment_date.setDisplayFormat("yyyy-MM-dd")
        self.appointment_date.setDate(QDate.currentDate())
        form.addRow("Next Appointment:", self.appointment_date)

        self.follow_up_notes = QTextEdit()
        self.follow_up_notes.setPlaceholderText(
            "Enter follow-up instructions or notes..."
        )
        self.follow_up_notes.setMaximumHeight(90)
        form.addRow("Follow-up Notes:", self.follow_up_notes)

        details_layout.addLayout(form)

        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Appointment")
        self.save_button.setObjectName("loginButton")
        self.save_button.clicked.connect(self.save_appointment)

        self.email_button = QPushButton("Send Follow-Up Email")
        self.email_button.setObjectName("primaryButton")
        self.email_button.clicked.connect(self.open_follow_up_email_dialog)
        
        self.clear_button = QPushButton("Clear Appointment Date")
        self.clear_button.setObjectName("linkButton")
        self.clear_button.clicked.connect(
            self.clear_appointment_date
        )

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.email_button)
        button_layout.addWidget(self.clear_button)
        details_layout.addLayout(button_layout)

        main_layout.addWidget(details_card)

    def get_patient_id(self, patient):
        return patient.get("patient_id", patient.get("id", ""))

    def refresh_schedule(self):
        self.highlight_appointment_dates()
        self.refresh_appointments_for_selected_date()

    def highlight_appointment_dates(self, *args):
        success, patients = self.schedule_service.get_all_patients()

        if not success:
            return

        # Remove the previous date formatting.
        self.calendar.setDateTextFormat(
            QDate(), QTextCharFormat()
        )

        appointment_format = QTextCharFormat()
        appointment_format.setBackground(
            QBrush(QColor("#DBEAFE"))
        )
        appointment_format.setForeground(
            QBrush(QColor("#1D4ED8"))
        )
        appointment_format.setFontWeight(700)

        for patient in patients:
            date_text = str(
                patient.get("next_appointment", "")
            ).strip()

            try:
                appointment_date = QDate.fromString(
                    date_text, "yyyy-MM-dd"
                )

                if appointment_date.isValid():
                    self.calendar.setDateTextFormat(
                        appointment_date,
                        appointment_format
                    )
            except (TypeError, ValueError):
                continue

    def refresh_appointments_for_selected_date(self):
        selected_date = self.calendar.selectedDate()
        date_text = selected_date.toString("yyyy-MM-dd")

        self.date_title.setText(
            "Appointments for " + date_text
        )

        success, appointments = (
            self.schedule_service.get_appointments_by_date(
                date_text
            )
        )

        if not success:
            QMessageBox.warning(
                self,
                "Schedule Error",
                str(appointments)
            )
            return

        self.appointment_table.setRowCount(0)
        self.selected_patient = None
        self.patient_name_label.setText("No patient selected")
        self.follow_up_notes.clear()
        self.appointment_date.setDate(selected_date)

        for patient in appointments:
            row = self.appointment_table.rowCount()
            self.appointment_table.insertRow(row)

            patient_id = self.get_patient_id(patient)

            values = [
                str(patient_id),
                str(patient.get("full_name", "Unnamed Patient")),
                str(patient.get("attending_physician", ""))
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column == 0:
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        patient_id
                    )

                self.appointment_table.setItem(
                    row, column, item
                )

    def load_selected_patient(self):
        row = self.appointment_table.currentRow()

        if row < 0:
            self.selected_patient = None
            return

        id_item = self.appointment_table.item(row, 0)

        if id_item is None:
            return

        patient_id = id_item.data(Qt.ItemDataRole.UserRole)

        success, patients = self.schedule_service.get_all_patients()

        if not success:
            return

        self.selected_patient = next(
            (
                patient for patient in patients
                if str(self.get_patient_id(patient))
                == str(patient_id)
            ),
            None
        )

        if self.selected_patient is None:
            return

        patient = self.selected_patient

        self.patient_name_label.setText(
            str(patient.get("full_name", "Unnamed Patient"))
        )

        date_text = str(
            patient.get("next_appointment", "")
        ).strip()

        appointment_date = QDate.fromString(
            date_text, "yyyy-MM-dd"
        )

        if appointment_date.isValid():
            self.appointment_date.setDate(appointment_date)
        else:
            self.appointment_date.setDate(QDate.currentDate())

        self.follow_up_notes.setPlainText(
            str(patient.get("follow_up_notes", ""))
        )

    def save_appointment(self):
        if not self.selected_patient:
            QMessageBox.warning(
                self,
                "No Patient Selected",
                "Select a patient from the appointment table first."
            )
            return

        patient_id = self.get_patient_id(self.selected_patient)

        appointment_date = self.appointment_date.date().toString(
            "yyyy-MM-dd"
        )

        result = self.schedule_service.update_appointment(
            patient_id=patient_id,
            appointment_date=appointment_date,
            follow_up_notes=self.follow_up_notes.toPlainText().strip(),
            staff=self.user
        )

        if isinstance(result, tuple):
            success = result[0]
            message = result[1] if len(result) > 1 else ""
        else:
            success = bool(result)
            message = ""

        if not success:
            QMessageBox.warning(
                self,
                "Save Failed",
                str(message or "The appointment could not be saved.")
            )
            return

        QMessageBox.information(
            self,
            "Appointment Saved",
            "The patient's appointment details were updated."
        )

        self.refresh_schedule()

        if self.on_change:
            self.on_change()

    def clear_appointment_date(self):
        if not self.selected_patient:
            QMessageBox.warning(
                self,
                "No Patient Selected",
                "Select a patient first."
            )
            return

        patient_id = self.get_patient_id(self.selected_patient)

        result = self.schedule_service.update_appointment(
            patient_id=patient_id,
            appointment_date="",
            follow_up_notes=self.follow_up_notes.toPlainText().strip(),
            staff=self.user
        )

        if isinstance(result, tuple):
            success = result[0]
            message = result[1] if len(result) > 1 else ""
        else:
            success = bool(result)
            message = ""

        if not success:
            QMessageBox.warning(
                self,
                "Update Failed",
                str(message or "The appointment could not be cleared.")
            )
            return

        self.refresh_schedule()

        if self.on_change:
            self.on_change()

    def open_follow_up_email_dialog(self):
        if not self.selected_patient:
            QMessageBox.warning(
                self,
                "No Patient Selected",
                "Select a patient from the appointment table first."
            )
            return

        dialog = FollowUpEmailDialog(
            patient_data=self.selected_patient,
            security_service=self.schedule_service.security_service,
            parent=self
        )
        dialog.exec()
