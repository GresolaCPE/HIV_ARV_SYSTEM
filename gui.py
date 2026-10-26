import os
import json

from backend.patient_history_service import PatientHistoryService
from datetime import datetime
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QMenu,
    QGridLayout,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QCheckBox,
    QApplication,
    QMainWindow,
    QStackedWidget,
    QFrame,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QFormLayout,
    QComboBox,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit

)
from PyQt6.QtGui import QIntValidator

from backend.auth_service import AuthService
from backend.patient_service import PatientService
from backend.inventory_service import InventoryService
from allocation_page import AllocationPage


def load_stylesheet():
    """Load the separate QSS stylesheet."""
    style_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "style.qss"
    )

    try:
        with open(style_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        QMessageBox.warning(
            None,
            "Stylesheet Missing",
            "style.qss was not found. Please check your project folder."
        )
        return ""



class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.auth_service = AuthService()

        self.setWindowTitle(
            "HIV ARV Allocation and Management System"
        )
        self.setMinimumSize(700, 600)

        self.create_ui()
        self.setStyleSheet(load_stylesheet())

    def create_ui(self):

        # MAIN LAYOUT
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(30, 25, 30, 25)

        # LOGIN CARD
        card = QFrame()
        card.setObjectName("loginCard")
        card.setMaximumWidth(480)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 35, 40, 35)
        card_layout.setSpacing(15)

        # TITLE
        title = QLabel("HIV ARV SYSTEM")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(
            "Antiretroviral Allocation and Management System"
        )
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)

        # USERNAME
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setClearButtonEnabled(True)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)

        # PASSWORD
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.show_password_checkbox = QCheckBox("Show password")
        self.show_password_checkbox.setStyleSheet("""
            QCheckBox {
                color: #52657A;
                font-size: 12px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)

        self.show_password_checkbox.toggled.connect(
            lambda checked: self.password_input.setEchoMode(
                QLineEdit.EchoMode.Normal
                if checked
                else QLineEdit.EchoMode.Password
            )
        )
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.show_password_checkbox)

        # Error message for failed login
        self.login_error_label = QLabel("")
        self.login_error_label.setWordWrap(True)
        self.login_error_label.setStyleSheet("""
            QLabel {
                color: #DC2626;
                font-size: 12px;
                background: transparent;
                padding: 2px 0px;
            }
        """)

        card_layout.addWidget(self.login_error_label)
        self.username_input.textChanged.connect(self.clear_login_error)
        self.password_input.textChanged.connect(self.clear_login_error) 

        # LOGIN BUTTON
        login_button = QPushButton("LOGIN")
        login_button.setObjectName("loginButton")
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.handle_login)

        card_layout.addSpacing(10)
        card_layout.addWidget(login_button)

        # FORGOT PASSWORD
        forgot_button = QPushButton("Forgot Password?")
        forgot_button.setObjectName("linkButton")
        forgot_button.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_button.clicked.connect(self.forgot_password)

        card_layout.addWidget(
            forgot_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # NO ACCOUNT YET? SIGN UP.
        signup_layout = QHBoxLayout()
        signup_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_layout.setSpacing(3)

        signup_label = QLabel("No account yet?")
        signup_label.setStyleSheet(
            "background-color: transparent; color: #64748B;"
        )

        signup_button = QPushButton("Sign Up")
        signup_button.setObjectName("linkButton")
        signup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_button.clicked.connect(self.open_registration)

        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(signup_button)

        card_layout.addSpacing(5)
        card_layout.addLayout(signup_layout)

        card.setLayout(card_layout)

        # CENTER THE CARD
        main_layout.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.setLayout(main_layout)

    def set_login_error(self, message):
        error_style = """
            QLineEdit {
                border: 1px solid #DC2626;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFF5F5;
                color: #1F2937;
            }
            QLineEdit:focus {
                border: 1px solid #DC2626;
                background-color: #FFFFFF;
            }
        """

        self.username_input.setStyleSheet(error_style)
        self.password_input.setStyleSheet(error_style)
        self.login_error_label.setText(message)


    def clear_login_error(self):
        normal_style = """
            QLineEdit {
                border: 1px solid #D5DFEA;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
            }
        """

        self.username_input.setStyleSheet(normal_style)
        self.password_input.setStyleSheet(normal_style)
        self.login_error_label.clear()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Clear previous error before trying again
        self.clear_login_error()

        if not username or not password:
            self.set_login_error(
                "Please enter both your username and password."
            )
            return

        success, result = self.auth_service.login(
            username,
            password
        )

        if success:
            self.dashboard = DashboardWindow(result)
            self.dashboard.showMaximized()
            self.close()
        else:
            self.set_login_error(
                "Invalid username or password. Please try again."
            )

    def forgot_password(self):

        QMessageBox.information(
            self,
            "Forgot Password",
            "Please contact the authorized system administrator "
            "or designated support personnel to reset your password."
        )

    def open_registration(self):

        dialog = RegistrationDialog(self)

        # Keep the registration dialog within the same application.
        dialog.exec()


class RegistrationDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.auth_service = AuthService()

        self.setWindowTitle("Staff Registration")
        self.setMinimumWidth(420)

        self.create_ui()
        self.setStyleSheet(load_stylesheet())

    def create_ui(self):

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(12)

        title = QLabel("Staff Registration")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)

        # STAFF ID
        staff_id_label = QLabel("Authorized Staff ID")
        staff_id_label.setObjectName("fieldLabel")

        self.staff_id_input = QLineEdit()
        self.staff_id_input.setPlaceholderText("Enter your staff ID")

        layout.addWidget(staff_id_label)
        layout.addWidget(self.staff_id_input)

        # FULL NAME
        name_label = QLabel("Full Name")
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")

        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # USERNAME
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Create a username")

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # PASSWORD
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Create a password"
        )
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        layout.addWidget(password_label)
        layout.addWidget(self.password_input)


        # REGISTER BUTTON
        register_button = QPushButton("CREATE ACCOUNT")
        register_button.setObjectName("loginButton")
        register_button.clicked.connect(self.register_staff)

        layout.addSpacing(10)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register_staff(self):

        staff_id = self.staff_id_input.text().strip()
        full_name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        success, result = self.auth_service.register_staff(
            staff_id,
            full_name,
            username,
            password
        )

        if success:
            QMessageBox.information(
                self,
                "Registration Successful",
                "Your staff account has been created. "
                "You can now log in."
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Registration Failed",
                str(result)
            )


class PatientHistoryDialog(QDialog):
    def __init__(self, patient, history_service, parent=None):
        super().__init__(parent)

        self.patient = patient
        self.history_service = history_service
        self.versions = []

        self.setWindowTitle("Patient Record History")
        self.resize(850, 700)

        layout = QVBoxLayout(self)

        title = QLabel("Patient Record History")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        patient_info = QLabel(
            f"Patient: {patient.get('full_name', 'Unknown')}\n"
            f"Patient ID: {patient.get('patient_id', 'Unknown')}"
        )
        patient_info.setWordWrap(True)
        layout.addWidget(patient_info)

        layout.addWidget(QLabel("Select record version:"))

        self.version_combo = QComboBox()
        self.version_combo.currentIndexChanged.connect(
            self.display_selected_version
        )
        layout.addWidget(self.version_combo)

        self.record_display = QTextEdit()
        self.record_display.setReadOnly(True)
        self.record_display.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )
        layout.addWidget(self.record_display, 1)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(
            close_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        self.load_versions()

    def load_versions(self):
        success, result = self.history_service.get_patient_history(
            self.patient.get("patient_id", "")
        )

        if not success:
            self.record_display.setPlainText(
                f"Unable to load patient history.\n\n{result}"
            )
            self.version_combo.setEnabled(False)
            return

        self.versions = result

        if not self.versions:
            self.record_display.setPlainText(
                "No saved versions were found for this patient."
            )
            self.version_combo.setEnabled(False)
            return

        for entry in self.versions:
            version_number = entry.get("version", "?")
            change_type = entry.get("change_type", "UPDATE")
            staff = entry.get("updated_by", "Unknown staff")
            timestamp = entry.get("updated_at", "Unknown date")

            try:
                readable_time = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                ).astimezone().strftime("%b %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                readable_time = timestamp

            if change_type == "CREATE":
                description = "Initial Record"
            else:
                description = "Updated Record"

            self.version_combo.addItem(
                f"Version {version_number} — {description} | "
                f"{readable_time} | Staff: {staff}"
            )

        # Show the latest saved version first.
        self.version_combo.setCurrentIndex(
            self.version_combo.count() - 1
        )

    def display_selected_version(self, index):
        if index < 0 or index >= len(self.versions):
            return

        entry = self.versions[index]
        snapshot = entry.get("record_snapshot", {})
        changes = entry.get("changed_fields", {})

        lines = []

        def add_section(title, fields):
            lines.append(title.upper())
            lines.append("=" * len(title))

            for label, key in fields:
                value = snapshot.get(key, "")
                if value is None or str(value).strip() == "":
                    value = "Not recorded"

                lines.append(f"{label}: {value}")

            lines.append("")

        lines.append(
            f"VERSION {entry.get('version', '?')} — "
            f"{entry.get('change_type', 'UPDATE')}"
        )
        lines.append(
            f"Updated by: {entry.get('updated_by', 'Unknown staff')}"
        )
        lines.append(
            f"Timestamp: {entry.get('updated_at', 'Unknown date')}"
        )
        lines.append("")

        add_section("Personal Information", [
            ("Patient ID", "patient_id"),
            ("Full Name", "full_name"),
            ("Date of Birth", "date_of_birth"),
            ("Age at This Version", "age"),
            ("Sex", "sex"),
            ("Contact Number", "contact_number"),
            ("Address", "address"),
            ("Emergency Contact", "emergency_contact"),
            ("Date Registered", "date_registered"),
        ])

        add_section("Medical History", [
            ("Diagnosis", "diagnosis"),
            ("Diagnosis Date", "diagnosis_date"),
            ("Medical History", "medical_history"),
            ("Other Conditions", "conditions"),
            ("Allergies", "allergies"),
            ("Current Medications", "current_medications"),
            ("Clinical Notes", "clinical_notes"),
        ])

        add_section("Treatment Information", [
            ("Attending Physician", "attending_physician"),
            ("ARV Regimen", "arv_regimen"),
            ("Treatment Start Date", "treatment_start"),
            ("Treatment Status", "treatment_status"),
            ("Next Appointment", "next_appointment"),
            ("Follow-up Notes", "follow_up_notes"),
        ])

        lines.append("CHANGES IN THIS VERSION")
        lines.append("=======================")

        if not changes:
            lines.append(
                "No individual field changes were recorded."
            )
        else:
            for field, values in changes.items():
                if isinstance(values, dict):
                    previous = values.get("previous", "Not recorded")
                    new = values.get("new", "Not recorded")

                    lines.append(f"{field.replace('_', ' ').title()}")
                    lines.append(f"  Previous: {previous}")
                    lines.append(f"  New: {new}")
                else:
                    lines.append(f"{field}: {values}")

                lines.append("")

        self.record_display.setPlainText("\n".join(lines))
        self.record_display.moveCursor(
            self.record_display.textCursor().MoveOperation.Start
        )


class PatientRegistrationDialog(QDialog):
    def __init__(self, parent=None, patient=None):
        super().__init__(parent)

        self.patient = patient or {}

        self.setWindowTitle(
            "Edit Patient Record" if patient else "Register New Patient"
        )

        self.resize(760, 620)

        main_layout = QVBoxLayout(self)

        title = QLabel("Edit Patient Record" if patient else "Patient Registration")
        title.setObjectName("cardTitle")
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: PERSONAL INFORMATION
        personal_tab = QWidget()
        personal_form = QFormLayout(personal_tab)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full name")

        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDisplayFormat("yyyy-MM-dd")
        self.date_of_birth.setDateRange(
            QDate(1900, 1, 1),
            QDate.currentDate()
        )
        self.date_of_birth.setDate(QDate.currentDate())

        self.sex = QComboBox()
        self.sex.addItems([
            "Prefer not to specify",
            "Female",
            "Male",
            "Other"
        ])

        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("Contact number")

        self.address = QTextEdit()
        self.address.setMaximumHeight(75)
        self.address.setPlaceholderText("Address")

        self.emergency_contact = QLineEdit()
        self.emergency_contact.setPlaceholderText(
            "Emergency contact name and number"
        )

        personal_form.addRow("Full Name *:", self.full_name)
        personal_form.addRow("Date of Birth *:", self.date_of_birth)
        personal_form.addRow("Sex:", self.sex)
        personal_form.addRow("Contact Number:", self.contact_number)
        personal_form.addRow("Address:", self.address)
        personal_form.addRow(
            "Emergency Contact:", self.emergency_contact
        )

        self.tabs.addTab(personal_tab, "Personal Information")

        # TAB 2: MEDICAL HISTORY
        medical_tab = QWidget()
        medical_form = QFormLayout(medical_tab)

        self.diagnosis = QLineEdit()
        self.diagnosis.setPlaceholderText(
            "Enter diagnosis as documented by the clinician"
        )

        self.diagnosis_date = QDateEdit()
        self.diagnosis_date.setCalendarPopup(True)
        self.diagnosis_date.setDisplayFormat("yyyy-MM-dd")
        self.diagnosis_date.setSpecialValueText("Not set")
        self.diagnosis_date.setDateRange(
            QDate(1900, 1, 1),
            QDate.currentDate()
        )
        self.diagnosis_date.setDate(QDate(1900, 1, 1))

        self.medical_history = QTextEdit()
        self.medical_history.setPlaceholderText(
            "Relevant previous medical history"
        )

        self.conditions = QTextEdit()
        self.conditions.setPlaceholderText(
            "Other conditions or comorbidities"
        )

        self.allergies = QTextEdit()
        self.allergies.setPlaceholderText(
            "Known allergies or adverse drug reactions; "
            "write 'None reported' only if confirmed"
        )

        self.current_medications = QTextEdit()
        self.current_medications.setPlaceholderText(
            "Current medications"
        )

        self.clinical_notes = QTextEdit()
        self.clinical_notes.setPlaceholderText(
            "Relevant clinical notes"
        )

        medical_form.addRow("Diagnosis *:", self.diagnosis)
        medical_form.addRow("Diagnosis Date:", self.diagnosis_date)
        medical_form.addRow("Medical History:", self.medical_history)
        medical_form.addRow("Other Conditions:", self.conditions)
        medical_form.addRow("Allergies:", self.allergies)
        medical_form.addRow(
            "Current Medications:", self.current_medications
        )
        medical_form.addRow("Clinical Notes:", self.clinical_notes)

        self.tabs.addTab(medical_tab, "Medical History")

        # TAB 3: TREATMENT INFORMATION
        treatment_tab = QWidget()
        treatment_form = QFormLayout(treatment_tab)

        self.physician = QLineEdit()
        self.physician.setPlaceholderText(
            "Attending physician's name"
        )

        self.arv_regimen = QLineEdit()
        self.arv_regimen.setPlaceholderText(
            "Regimen as prescribed by the clinician"
        )

        self.treatment_start = QDateEdit()
        self.treatment_start.setCalendarPopup(True)
        self.treatment_start.setDisplayFormat("yyyy-MM-dd")
        self.treatment_start.setDateRange(
            QDate(1900, 1, 1),
            QDate.currentDate()
        )
        self.treatment_start.setSpecialValueText("Not set")
        self.treatment_start.setDate(QDate(1900, 1, 1))

        self.treatment_status = QComboBox()
        self.treatment_status.addItems([
            "Not specified",
            "Active",
            "On hold",
            "Discontinued",
            "Transferred",
        ])

        self.next_appointment = QDateEdit()
        self.next_appointment.setCalendarPopup(True)
        self.next_appointment.setDisplayFormat("yyyy-MM-dd")
        self.next_appointment.setSpecialValueText("Not scheduled")
        self.next_appointment.setDateRange(
            QDate(1900, 1, 1),
            QDate(2100, 12, 31)
        )
        self.next_appointment.setDate(QDate(1900, 1, 1))

        self.follow_up_notes = QTextEdit()
        self.follow_up_notes.setPlaceholderText(
            "Follow-up instructions or notes from staff"
        )

        treatment_form.addRow("Attending Physician *:", self.physician)
        treatment_form.addRow("ARV Regimen:", self.arv_regimen)
        treatment_form.addRow(
            "Treatment Start Date:", self.treatment_start
        )
        treatment_form.addRow(
            "Treatment Status:", self.treatment_status
        )
        treatment_form.addRow(
            "Next Appointment:", self.next_appointment
        )
        treatment_form.addRow(
            "Follow-up Notes:", self.follow_up_notes
        )

        self.tabs.addTab(treatment_tab, "Treatment Information")

        # SAVE AND CANCEL BUTTONS
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.button(
            QDialogButtonBox.StandardButton.Save
        ).setText(
            "Update Patient" if patient else "Save Patient"
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

        if patient:
            self.set_patient_data(patient)

            # Lock identifying information during routine updates.
            self.full_name.setReadOnly(True)
            self.date_of_birth.setEnabled(False)
            self.sex.setEnabled(False)
            self.contact_number.setReadOnly(True)
            self.address.setReadOnly(True)
            self.emergency_contact.setReadOnly(True)

            # Keep diagnosis and medical history read-only too.
            self.diagnosis.setReadOnly(False)
            self.diagnosis_date.setEnabled(True)
            self.medical_history.setReadOnly(True)
            self.conditions.setReadOnly(True)

    def get_patient_data(self):
        return {
            "full_name": self.full_name.text().strip(),
            "date_of_birth": self.date_of_birth.date().toString("yyyy-MM-dd"),
            "sex": self.sex.currentText(),
            "contact_number": self.contact_number.text().strip(),
            "address": self.address.toPlainText().strip(),
            "emergency_contact": (
                self.emergency_contact.text().strip()
            ),
            "diagnosis": self.diagnosis.text().strip(),
            "diagnosis_date": (
                ""
                if self.diagnosis_date.date() == QDate(1900, 1, 1)
                else self.diagnosis_date.date().toString("yyyy-MM-dd")),
            "medical_history": (
                self.medical_history.toPlainText().strip()
            ),
            "other_conditions": (
                self.conditions.toPlainText().strip()
            ),
            "allergies": self.allergies.toPlainText().strip(),
            "current_medications": (
                self.current_medications.toPlainText().strip()
            ),
            "clinical_notes": (
                self.clinical_notes.toPlainText().strip()
            ),
            "attending_physician": self.physician.text().strip(),
            "arv_regimen": self.arv_regimen.text().strip(),
            "treatment_start_date": (
                ""
                if self.treatment_start.date() == QDate(1900, 1, 1)
                else self.treatment_start.date().toString("yyyy-MM-dd")
            ),
            "treatment_status": self.treatment_status.currentText(),
            "next_appointment": (
                ""
                if self.next_appointment.date() == QDate(1900, 1, 1)
                else self.next_appointment.date().toString("yyyy-MM-dd")
            ),
            "follow_up_notes": (
                self.follow_up_notes.toPlainText().strip()
            ),
        }

    def set_patient_data(self, patient):
        self.full_name.setText(str(patient.get("full_name", "")))
        dob = QDate.fromString(
            str(patient.get("date_of_birth", "")),
            "yyyy-MM-dd"
        )

        if dob.isValid():
            self.date_of_birth.setDate(dob)

        sex = patient.get("sex", "Prefer not to specify")
        index = self.sex.findText(sex)
        if index >= 0:
            self.sex.setCurrentIndex(index)

        self.contact_number.setText(
            str(patient.get("contact_number", ""))
        )
        self.address.setPlainText(str(patient.get("address", "")))
        self.emergency_contact.setText(
            str(patient.get("emergency_contact", ""))
        )
        diagnosis_date = QDate.fromString(
            str(patient.get("diagnosis_date", "")),
            "yyyy-MM-dd"
        )

        self.diagnosis_date.setDate(
            diagnosis_date
            if diagnosis_date.isValid()
            else QDate(1900, 1, 1)
        )
        self.medical_history.setPlainText(
            str(patient.get("medical_history", ""))
        )
        self.conditions.setPlainText(
            str(patient.get("conditions", ""))
        )
        self.allergies.setPlainText(str(patient.get("allergies", "")))
        self.current_medications.setPlainText(
            str(patient.get("current_medications", ""))
        )
        self.clinical_notes.setPlainText(
            str(patient.get("clinical_notes", ""))
        )

        self.physician.setText(
            str(patient.get("attending_physician", ""))
        )
        self.arv_regimen.setText(str(patient.get("arv_regimen", "")))
        treatment_start = QDate.fromString(
            str(patient.get("treatment_start", "")),
            "yyyy-MM-dd"
        )

        self.treatment_start.setDate(
            treatment_start
            if treatment_start.isValid()
            else QDate(1900, 1, 1)
        )

        status = patient.get("treatment_status", "Not specified")
        index = self.treatment_status.findText(status)
        if index >= 0:
            self.treatment_status.setCurrentIndex(index)

        next_appointment = QDate.fromString(str(patient.get("next_appointment", "")),"yyyy-MM-dd")
        self.next_appointment.setDate(
            next_appointment
            if next_appointment.isValid()
            else QDate(1900, 1, 1)
        )
        self.follow_up_notes.setPlainText(
            str(patient.get("follow_up_notes", ""))
        )

class PatientHistoryDialog(QDialog):
    def __init__(self, patient, history_service, parent=None):
        super().__init__(parent)

        self.patient = patient
        self.history_service = history_service
        self.history_entries = []

        patient_id = patient.get("patient_id", "Unknown")

        self.setWindowTitle("Patient Record History")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        title = QLabel("Patient Record History")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        description = QLabel(
            f"Patient: {patient.get('full_name', 'Unknown')}\n"
            f"Patient ID: {patient_id}\n"
            "Select a saved version to view the complete record."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addWidget(QLabel("Saved Versions"))

        self.version_table = QTableWidget()
        self.version_table.setColumnCount(4)
        self.version_table.setHorizontalHeaderLabels([
            "Version",
            "Change Type",
            "Date and Time",
            "Updated By"
        ])
        self.version_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.version_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.version_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.version_table.setAlternatingRowColors(True)
        self.version_table.verticalHeader().setVisible(False)

        header = self.version_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setStretchLastSection(True)

        layout.addWidget(self.version_table, 1)
        layout.addWidget(QLabel("Selected Version Details"))

        self.snapshot_view = QTextEdit()
        self.snapshot_view.setReadOnly(True)
        self.snapshot_view.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )
        layout.addWidget(self.snapshot_view, 2)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(
            close_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        self.version_table.cellClicked.connect(
            self.show_selected_version
        )

        self.populate_versions()

    def populate_versions(self):
        success, result = self.history_service.get_patient_history(
            self.patient.get("patient_id", "")
        )

        if not success:
            QMessageBox.warning(
                self,
                "History Error",
                str(result)
            )
            return

        self.history_entries = sorted(
            result,
            key=lambda entry: entry.get("version", 0),
            reverse=True
        )

        self.version_table.setRowCount(0)

        for entry in self.history_entries:
            row = self.version_table.rowCount()
            self.version_table.insertRow(row)

            timestamp = entry.get("updated_at", "")
            try:
                readable_time = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                ).astimezone().strftime("%b %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                readable_time = timestamp or "Unknown date"

            change_type = entry.get("change_type", "UPDATE")
            if change_type == "CREATE":
                change_type = "Initial Record"

            values = [
                f"Version {entry.get('version', '?')}",
                change_type,
                readable_time,
                entry.get("updated_by", "Unknown staff")
            ]

            for column, value in enumerate(values):
                self.version_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

        if self.version_table.rowCount() > 0:
            self.version_table.selectRow(0)
            self.show_selected_version(0, 0)
        else:
            self.snapshot_view.setPlainText(
                "No saved history versions were found for this patient."
            )

    def show_selected_version(self, row, column):
        if row < 0 or row >= len(self.history_entries):
            return

        entry = self.history_entries[row]
        record = entry.get("record_snapshot", {})
        changes = entry.get("changed_fields", {})

        lines = []

        def add_section(title, fields):
            lines.append(title.upper())
            lines.append("=" * len(title))

            for label, key in fields:
                value = record.get(key)

                if value is None or str(value).strip() == "":
                    value = "Not recorded"

                lines.append(f"{label}: {value}")

            lines.append("")

        lines.extend([
            f"VERSION {entry.get('version', '?')}",
            f"Change Type: {entry.get('change_type', 'UPDATE')}",
            f"Updated By: {entry.get('updated_by', 'Unknown staff')}",
            f"Updated At: {entry.get('updated_at', 'Unknown date')}",
            ""
        ])

        add_section("Personal Information", [
            ("Patient ID", "patient_id"),
            ("Full Name", "full_name"),
            ("Date of Birth", "date_of_birth"),
            ("Age at This Version", "age"),
            ("Sex", "sex"),
            ("Contact Number", "contact_number"),
            ("Address", "address"),
            ("Emergency Contact", "emergency_contact"),
            ("Date Registered", "date_registered"),
        ])

        add_section("Medical History", [
            ("Diagnosis", "diagnosis"),
            ("Diagnosis Date", "diagnosis_date"),
            ("Medical History", "medical_history"),
            ("Other Conditions", "conditions"),
            ("Allergies", "allergies"),
            ("Current Medications", "current_medications"),
            ("Clinical Notes", "clinical_notes"),
        ])

        add_section("Treatment Information", [
            ("Attending Physician", "attending_physician"),
            ("ARV Regimen", "arv_regimen"),
            ("Treatment Start Date", "treatment_start"),
            ("Treatment Status", "treatment_status"),
            ("Next Appointment", "next_appointment"),
            ("Follow-up Notes", "follow_up_notes"),
        ])

        lines.append("CHANGES IN THIS VERSION")
        lines.append("=======================")

        if not changes:
            lines.append("No individual field changes were recorded.")
        else:
            for field, values in changes.items():
                lines.append(field.replace("_", " ").title())

                if isinstance(values, dict):
                    previous = values.get("previous", "Not recorded")
                    new = values.get("new", "Not recorded")
                    lines.append(f"  Previous: {previous}")
                    lines.append(f"  New: {new}")
                else:
                    lines.append(f"  {values}")

                lines.append("")

        self.snapshot_view.setPlainText("\n".join(lines))
        self.snapshot_view.moveCursor(
            self.snapshot_view.textCursor().MoveOperation.Start
        )



class MedicineDialog(QDialog):
    def __init__(self, medicine=None, parent=None):
        super().__init__(parent)

        self.medicine = medicine or {}

        self.setWindowTitle(
            "Edit Medicine" if medicine else "Add Medicine"
        )
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Medicine name
        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter medicine name")
        form.addRow("Medicine Name:", self.name)

        # Medicine strength
        self.strength = QLineEdit()
        self.strength.setPlaceholderText("e.g., 300 mg")
        form.addRow("Strength:", self.strength)

        # Batch number
        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("Enter batch number")
        form.addRow("Batch Number:", self.batch_number)

        # Available quantity
        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("Available units")
        self.quantity.setValidator(
            QIntValidator(0, 100000000, self)
        )
        form.addRow("Quantity:", self.quantity)

        # Expiration date
        self.expiry_date = QLineEdit()
        self.expiry_date.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Expiration Date:", self.expiry_date)

        # Low-stock threshold
        self.threshold = QLineEdit()
        self.threshold.setPlaceholderText("e.g., 20")
        self.threshold.setValidator(
            QIntValidator(0, 100000000, self)
        )
        form.addRow("Low-Stock Threshold:", self.threshold)

        layout.addLayout(form)

        # Save and cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        # Fill fields when editing an existing medicine
        if medicine:
            self.name.setText(str(medicine.get("medicine_name", medicine.get("name", ""))))
            self.strength.setText(
                str(medicine.get("strength", ""))
            )
            self.batch_number.setText(
                str(medicine.get("batch_number", ""))
            )
            self.quantity.setText(
                str(medicine.get("quantity", 0))
            )
            self.expiry_date.setText(
                str(medicine.get("expiry_date", ""))
            )
            self.threshold.setText(
                str(medicine.get("low_stock_threshold",  20))
            )
        else:
            self.threshold.setText("20")

    def validate_and_accept(self):
        from datetime import date

        if not self.name.text().strip():
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter the medicine name."
            )
            return

        if not self.strength.text().strip():
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter the medicine strength."
            )
            return

        if not self.batch_number.text().strip():
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter the batch number."
            )
            return

        if not self.quantity.text().strip():
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter the available quantity."
            )
            return

        if not self.threshold.text().strip():
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter the low-stock threshold."
            )
            return

        try:
            date.fromisoformat(self.expiry_date.text().strip())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Date",
                "Enter the expiration date in YYYY-MM-DD format."
            )
            return

        self.accept()

    def get_medicine_data(self):
        return {
            "name": self.name.text().strip(),
            "strength": self.strength.text().strip(),
            "batch_number": self.batch_number.text().strip(),
            "quantity": int(self.quantity.text()),
            "expiry_date": self.expiry_date.text().strip(),
            "threshold": int(self.threshold.text()),
        }
   

class DashboardWindow(QMainWindow):

    def __init__(self, user):
        super().__init__()

        self.user = user
        self.page_buttons = []
        self.inventory_service = InventoryService()

        self.setWindowTitle(
            "HIV ARV Allocation and Management System"
        )
        self.setMinimumSize(900, 600)

        self.create_ui()
        self.setStyleSheet(load_stylesheet())

    def create_ui(self):

        # MAIN CONTAINER
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT SIDEBAR
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 25, 18, 20)
        sidebar_layout.setSpacing(10)

        # SYSTEM TITLE
        system_title = QLabel("HIV ARV SYSTEM")
        system_title.setObjectName("sidebarTitle")

        system_subtitle = QLabel(
            "Allocation and Management"
        )
        system_subtitle.setObjectName("sidebarSubtitle")
        system_subtitle.setWordWrap(True)

        sidebar_layout.addWidget(system_title)
        sidebar_layout.addWidget(system_subtitle)
        sidebar_layout.addSpacing(25)

        # NAVIGATION
        navigation_items = [
            ("Home", 0),
            ("Patient Record", 1),
            ("Inventory", 2),
            ("Allocation", 3),
            ("Schedule", 4),
            ("Report", 5),
            ("Security", 6),
        ]

        self.pages = QStackedWidget()

        for label, page_index in navigation_items:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False, index=page_index:
                    self.change_page(index)
            )

            sidebar_layout.addWidget(button)
            self.page_buttons.append(button)

        sidebar_layout.addStretch()

        # LOGGED-IN STAFF INFORMATION
        staff_name = QLabel(
            self.user.get("full_name", "Staff")
        )
        staff_name.setObjectName("staffName")
        staff_name.setWordWrap(True)

        staff_id = QLabel(
            "Staff ID: " + self.user.get("staff_id", "")
        )
        staff_id.setObjectName("staffDetails")
        staff_id.setWordWrap(True)

        sidebar_layout.addWidget(staff_name)
        sidebar_layout.addWidget(staff_id)

        # SIGN OUT
        sign_out_button = QPushButton("Sign Out")
        sign_out_button.setObjectName("signOutButton")
        sign_out_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        sign_out_button.clicked.connect(self.sign_out)

        sidebar_layout.addWidget(sign_out_button)

        # RIGHT CONTENT AREA
        content_area = QWidget()
        content_area.setObjectName("contentArea")

        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(35, 30, 35, 30)

        self.page_heading = QLabel("Dashboard")
        self.page_heading.setObjectName("pageHeading")

        self.page_description = QLabel(
            "Welcome to the HIV Antiretroviral "
            "Allocation and Management System."
        )
        self.page_description.setObjectName("pageDescription")
        self.page_description.setWordWrap(True)

        content_layout.addWidget(self.page_heading)
        content_layout.addWidget(self.page_description)
        content_layout.addSpacing(20)

        # PAGE CONTENT
        # PAGE CONTENT
        self.pages.addWidget(self.create_home_page())       # Index 0: Home
        self.pages.addWidget(self.create_patients_page())   # Index 1: Patient Record
        self.pages.addWidget(self.create_inventory_page()) # Index 2: Inventory

        self.allocation_page = AllocationPage(
            self.user, on_change=self.refresh_inventory
        )
        self.pages.addWidget(self.allocation_page)  # Index 3: Allocation

        self.pages.addWidget(
            self.create_placeholder_page(
                "Schedule",
                "View and manage patient appointments."
            )
        )  # Index 4: Schedule

        self.pages.addWidget(
            self.create_placeholder_page(
                "Reports",
                "View system summaries and generate reports."
            )
        )  # Index 5: Report

        self.pages.addWidget(
            self.create_placeholder_page(
                "Security",
                "Manage system security settings."
            )
        )  # Index 6: Security

        content_layout.addWidget(self.pages)

        # ADD SIDEBAR AND CONTENT
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

        self.setCentralWidget(central_widget)

        self.change_page(0)


    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Welcome section
        welcome_title = QLabel(
            "Welcome back, " + self.user.get("full_name", "Staff")
        )
        welcome_title.setObjectName("welcomeTitle")

        welcome_description = QLabel(
            "Here's an overview of your patient records and system activities."
        )
        welcome_description.setObjectName("pageDescription")
        welcome_description.setWordWrap(True)

        layout.addWidget(welcome_title)
        layout.addWidget(welcome_description)

        # Summary cards
        summary_layout = QGridLayout()
        summary_layout.setSpacing(14)

        try:
            self.patient_service = PatientService()
            success, patients = self.patient_service.get_patients()
            patient_count = len(patients) if success else 0
        except Exception:
            patient_count = 0

        
        self.dashboard_inventory_labels = {}

        summary_items = [
            (
                "Total Patients",
                str(patient_count),
                "Registered patient records",
                None
            ),
            (
                "Medicine Stock",
                "0 types",
                "0 total units available",
                "medicine_stock"
            ),
            (
                "Upcoming Appointments",
                "View Schedule",
                "Review patient appointments",
                None
            ),
            (
                "Allocations",
                "View Allocation",
                "Track medicine allocations",
                None
            ),
        ]

        for index, (
            title_text,
            value_text,
            description_text,
            key
        ) in enumerate(summary_items):

            card = QFrame()
            card.setObjectName("dashboardCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 16)
            card_layout.setSpacing(8)

            title = QLabel(title_text)
            title.setObjectName("cardDescription")

            value = QLabel(value_text)
            value.setObjectName("metricValue")
            value.setWordWrap(True)

            description = QLabel(description_text)
            description.setObjectName("cardDescription")
            description.setWordWrap(True)

            # Save the dashboard labels for live updates
            if key == "medicine_stock":
                self.dashboard_inventory_labels["types"] = value
                self.dashboard_inventory_labels["units"] = description

            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card_layout.addWidget(description)

            summary_layout.addWidget(
                card,
                index // 2,
                index % 2
            )

        layout.addLayout(summary_layout)


        # Lower dashboard panels
        panels_layout = QGridLayout()
        panels_layout.setSpacing(14)

        # Incoming appointments
        schedule_card = QFrame()
        schedule_card.setObjectName("dashboardCard")
        schedule_layout = QVBoxLayout(schedule_card)

        schedule_title = QLabel("Incoming Patient Schedule")
        schedule_title.setObjectName("cardTitle")

        schedule_message = QLabel(
            "No appointment schedule is connected yet.\n"
            "Patient appointments can be displayed here once Schedule is implemented."
        )
        schedule_message.setObjectName("cardDescription")
        schedule_message.setWordWrap(True)

        schedule_layout.addWidget(schedule_title)
        schedule_layout.addWidget(schedule_message)
        schedule_layout.addStretch()

        # Inventory alerts
        inventory_card = QFrame()
        inventory_card.setObjectName("dashboardCard")
        inventory_layout = QVBoxLayout(inventory_card)

        inventory_title = QLabel("Inventory Overview")
        inventory_title.setObjectName("cardTitle")

        inventory_message = QLabel(
            "Loading inventory information..."
        )
        inventory_message.setObjectName("cardDescription")
        inventory_message.setWordWrap(True)

        # Keep a reference so the dashboard can update it
        self.dashboard_inventory_message = inventory_message

        inventory_layout.addWidget(inventory_title)
        inventory_layout.addWidget(inventory_message)
        inventory_layout.addStretch()

        panels_layout.addWidget(schedule_card, 0, 0)
        panels_layout.addWidget(inventory_card, 0, 1)

        layout.addLayout(panels_layout)

        # Quick access
        quick_card = QFrame()
        quick_card.setObjectName("dashboardCard")
        quick_layout = QVBoxLayout(quick_card)

        quick_title = QLabel("Quick Actions")
        quick_title.setObjectName("cardTitle")
        quick_layout.addWidget(quick_title)

        actions_layout = QHBoxLayout()

        actions = [
            ("Patient Records", 1),
            ("Inventory", 2),
            ("Allocation", 3),
            ("Schedule", 4),
            ("Reports", 5),
        ]

        for label, page_index in actions:
            button = QPushButton(label)
            button.setObjectName("loginButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, i=page_index: self.change_page(i)
            )
            actions_layout.addWidget(button)

        quick_layout.addLayout(actions_layout)
        layout.addWidget(quick_card)
        layout.addStretch()

        return page


    def create_patients_page(self):
        self.patient_service = PatientService()

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("Patient Management")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        description = QLabel(
            "Register patients and manage their medical "
            "and treatment records."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Action buttons and search
        actions = QHBoxLayout()

        add_button = QPushButton("+ Add Patient")
        add_button.setObjectName("loginButton")
        add_button.clicked.connect(
            self.open_patient_registration
        )

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("linkButton")
        edit_button.clicked.connect(self.edit_patient_record)

        history_button = QPushButton("View History")
        history_button.setObjectName("linkButton")
        history_button.clicked.connect(self.view_patient_history)

        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText(
            "Search by patient ID or name"
        )
        self.patient_search_input.returnPressed.connect(
            self.search_patient_records
        )

        search_button = QPushButton("Search")
        search_button.setObjectName("loginButton")
        search_button.clicked.connect(
            self.search_patient_records
        )

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("linkButton")
        refresh_button.clicked.connect(
            self.refresh_patient_records
        )

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("linkButton")
        delete_button.clicked.connect(
            self.delete_patient_record
        )

        actions.addWidget(add_button)
        actions.addWidget(edit_button)
        actions.addWidget(history_button)
        actions.addWidget(self.patient_search_input, 1)
        actions.addWidget(search_button)
        actions.addWidget(refresh_button)
        actions.addWidget(delete_button)

        layout.addLayout(actions)

        # PATIENT RECORDS TABLE
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(8)

        self.patient_table.setHorizontalHeaderLabels([
            "Patient ID",
            "Full Name",
            "Age",
            "Diagnosis",
            "Attending Physician",
            "ARV Regimen",
            "Treatment Status",
            "Date Registered"
        ])

        # Table behavior
        self.patient_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.patient_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.patient_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        # Table appearance
        self.patient_table.setAlternatingRowColors(True)
        self.patient_table.setShowGrid(False)
        self.patient_table.setWordWrap(False)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.verticalHeader().setDefaultSectionSize(48)

        # Column sizing
        header = self.patient_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setStretchLastSection(True)

        # Allow horizontal scrolling if the window is too narrow
        self.patient_table.setHorizontalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )

        layout.addWidget(self.patient_table, 1)

        self.patient_table.cellDoubleClicked.connect(
        lambda row, column: self.view_patient_history())

        self.load_patient_records()
        return page

    def open_patient_registration(self):
        dialog = PatientRegistrationDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        profile = dialog.get_patient_data()

        success, result = self.patient_service.add_patient_profile(profile, created_by=self.user.get("staff_id", ""))

        if not success:
            QMessageBox.warning(
                self,
                "Registration Failed",
                str(result)
            )
            return

        QMessageBox.information(
            self,
            "Patient Registered",
            "Patient profile saved successfully.\n\n"
            f"Patient ID: {result['patient_id']}"
        )

        self.patient_search_input.clear()
        self.load_patient_records()

    def load_patient_records(self, search_text=""):
        success, result = self.patient_service.get_patients(
            search_text
        )

        if not success:
            QMessageBox.warning(
                self,
                "Patient Records Error",
                str(result)
            )
            return

        self.patient_table.setRowCount(0)

        for patient in result:
            row = self.patient_table.rowCount()
            self.patient_table.insertRow(row)

            values = [
                patient.get("patient_id", ""),
                patient.get("full_name", ""),
                str(patient.get("age", "")),
                patient.get("diagnosis", ""),
                patient.get("attending_physician", ""),
                patient.get("arv_regimen", ""),
                patient.get("treatment_status", ""),
                patient.get("date_registered", "")
            ]

            for column, value in enumerate(values):
                self.patient_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

    def search_patient_records(self):
        self.load_patient_records(
            self.patient_search_input.text()
        )

    def refresh_patient_records(self):
        self.patient_search_input.clear()
        self.load_patient_records()

    
    def edit_patient_record(self):
        row = self.patient_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Select a patient record first."
            )
            return

        item = self.patient_table.item(row, 0)

        if item is None:
            return

        patient_id = item.text()

        success, patient = self.patient_service.get_patient_by_id(
            patient_id
        )

        if not success:
            QMessageBox.warning(
                self,
                "Patient Not Found",
                str(patient)
            )
            return

        dialog = PatientRegistrationDialog(
            parent=self,
            patient=patient
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        success, result = self.patient_service.update_patient_profile(
            patient_id,
            dialog.get_patient_data(),
            updated_by=self.user.get("staff_id", "")
        )

        if not success:
            QMessageBox.warning(
                self,
                "Update Failed",
                str(result)
            )
            return

        if isinstance(result, str):
            QMessageBox.information(
                self,
                "No Changes",
                result
            )
        else:
            QMessageBox.information(
                self,
                "Patient Updated",
                "Patient record updated successfully."
            )

        self.load_patient_records(
            self.patient_search_input.text()
        )

    def view_patient_history(self):
        row = self.patient_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "No Patient Selected",
                "Select or double-click a patient record first."
            )
            return

        item = self.patient_table.item(row, 0)

        if item is None:
            return

        patient_id = item.text()

        success, patient = self.patient_service.get_patient_by_id(
            patient_id
        )

        if not success:
            QMessageBox.warning(
                self,
                "Patient Not Found",
                str(patient)
            )
            return

        history_service = PatientHistoryService()

        dialog = PatientHistoryDialog(
            patient=patient,
            history_service=history_service,
            parent=self
        )

        dialog.exec()

    def delete_patient_record(self):
        row = self.patient_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Select a patient record first."
            )
            return

        item = self.patient_table.item(row, 0)

        if item is None:
            return

        patient_id = item.text()

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete patient record {patient_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message = self.patient_service.delete_patient(
            patient_id
        )

        if success:
            QMessageBox.information(
                self,
                "Success",
                str(message)
            )
            self.load_patient_records(
                self.patient_search_input.text()
            )
        else:
            QMessageBox.warning(
                self,
                "Deletion Failed",
                str(message)
            )

    
    def create_inventory_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Summary cards
        summary_layout = QGridLayout()
        summary_layout.setSpacing(12)

        self.inventory_summary_labels = {}

        summary_items = [
            ("Medicine Types", "total_types"),
            ("Total Units", "total_units"),
            ("Low Stock", "low_stock"),
            ("Out of Stock", "out_of_stock")
        ]

        for index, (title_text, key) in enumerate(summary_items):
            card = QFrame()
            card.setObjectName("dashboardCard")

            card_layout = QVBoxLayout(card)

            title = QLabel(title_text)
            title.setObjectName("cardDescription")

            value = QLabel("0")
            value.setObjectName("metricValue")

            self.inventory_summary_labels[key] = value

            card_layout.addWidget(title)
            card_layout.addWidget(value)

            summary_layout.addWidget(card, index // 2, index % 2)

        layout.addLayout(summary_layout)

        # Search and action buttons
        actions = QHBoxLayout()

        self.inventory_search = QLineEdit()
        self.inventory_search.setPlaceholderText(
            "Search medicine, batch number, or medicine ID..."
        )
        self.inventory_search.returnPressed.connect(
            self.search_inventory
        )

        search_button = QPushButton("Search")
        search_button.setObjectName("loginButton")
        search_button.clicked.connect(self.search_inventory)

        add_button = QPushButton("+ Add Medicine")
        add_button.setObjectName("loginButton")
        add_button.clicked.connect(self.add_medicine)

        edit_button = QPushButton("Edit Selected")
        edit_button.setObjectName("linkButton")
        edit_button.clicked.connect(self.edit_medicine)

        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("linkButton")
        delete_button.clicked.connect(self.delete_medicine)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("linkButton")
        refresh_button.clicked.connect(self.refresh_inventory)

        actions.addWidget(self.inventory_search, 1)
        actions.addWidget(search_button)
        actions.addWidget(add_button)
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        actions.addWidget(refresh_button)

        layout.addLayout(actions)

        # Medicine table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "Medicine ID",
            "Medicine Name",
            "Strength",
            "Batch Number",
            "Quantity",
            "Expiration Date",
            "Stock Status"
        ])

        self.inventory_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.inventory_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.inventory_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setShowGrid(False)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.verticalHeader().setDefaultSectionSize(42)

        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setStretchLastSection(True)

        layout.addWidget(self.inventory_table, 1)

        self.refresh_inventory()

        return page


    def load_inventory_records(self, search_text=""):
        success, medicines = self.inventory_service.get_medicines(
            search_text
        )

        if not success:
            QMessageBox.warning(
                self, "Inventory Error", str(medicines)
            )
            return

        self.inventory_table.setRowCount(0)

        from datetime import date

        for medicine in medicines:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)

            quantity = int(medicine.get("quantity", 0))
            threshold = int(
                medicine.get(
                    "threshold",
                    medicine.get("low_stock_threshold", 20)
                )
            )

            try:
                expiry = date.fromisoformat(medicine.get("expiry_date", ""))
                if expiry < date.today():
                    status = "EXPIRED"
                elif (expiry - date.today()).days <= 90:
                    status = "EXPIRING SOON"
                elif quantity == 0:
                    status = "OUT OF STOCK"
                elif quantity <= threshold:
                    status = "LOW STOCK"
                else:
                    status = "In Stock"
            except ValueError:
                status = "Check Expiry Date"

            values = [
                medicine.get("medicine_id", ""),
                medicine.get("name", medicine.get("medicine_name", "")),
                medicine.get("strength", ""),
                medicine.get("batch_number", ""),
                str(quantity),
                medicine.get("expiry_date", ""),
                status
            ]

            for column, value in enumerate(values):
                self.inventory_table.setItem(
                    row, column, QTableWidgetItem(str(value))
                )


    def refresh_inventory(self):
        self.inventory_search.clear()
        self.load_inventory_records()
        self.update_inventory_summary()
        self.update_dashboard_inventory()


    def search_inventory(self):
        self.load_inventory_records(
            self.inventory_search.text()
        )


    def update_inventory_summary(self):
        success, summary = self.inventory_service.get_summary()

        if not success:
            QMessageBox.warning(
                self, "Inventory Error", str(summary)
            )
            return

        for key, label in self.inventory_summary_labels.items():
            label.setText(str(summary.get(key, 0)))


    def add_medicine(self):
        dialog = MedicineDialog(parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        success, result = self.inventory_service.add_medicine(
            dialog.get_medicine_data()
        )

        if not success:
            QMessageBox.warning(
                self, "Unable to Add Medicine", str(result)
            )
            return

        QMessageBox.information(
            self,
            "Medicine Added",
            f"Medicine record {result['medicine_id']} was saved."
        )

        self.refresh_inventory()


    
    def update_dashboard_inventory(self):
        success, summary = self.inventory_service.get_summary()

        if not success:
            self.dashboard_inventory_message.setText(
                "Unable to load inventory information."
            )
            return

        total_types = summary.get("total_types", 0)
        total_units = summary.get("total_units", 0)
        low_stock = summary.get("low_stock", 0)
        out_of_stock = summary.get("out_of_stock", 0)

        # Update the Medicine Stock summary card
        self.dashboard_inventory_labels["types"].setText(
            f"{total_types} types"
        )

        self.dashboard_inventory_labels["units"].setText(
            f"{total_units} total units available"
        )

        # Update the Inventory Overview panel
        self.dashboard_inventory_message.setText(
            f"Medicine types: {total_types}\n"
            f"Total units: {total_units}\n"
            f"Low-stock items: {low_stock}\n"
            f"Out-of-stock items: {out_of_stock}"
        )



    def edit_medicine(self):
        row = self.inventory_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "No Selection",
                "Select a medicine record first."
            )
            return

        item = self.inventory_table.item(row, 0)
        if item is None:
            return

        medicine_id = item.text()
        success, medicines = self.inventory_service.get_medicines()

        if not success:
            QMessageBox.warning(self, "Inventory Error", str(medicines))
            return

        medicine = next(
            (
                item for item in medicines
                if item.get("medicine_id") == medicine_id
            ),
            None
        )

        if medicine is None:
            QMessageBox.warning(
                self, "Not Found", "Medicine record not found."
            )
            return

        dialog = MedicineDialog(medicine=medicine, parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        success, result = self.inventory_service.update_medicine(
            medicine_id, dialog.get_medicine_data()
        )

        if not success:
            QMessageBox.warning(
                self, "Update Failed", str(result)
            )
            return

        QMessageBox.information(
            self, "Updated", "Medicine record updated successfully."
        )
        self.refresh_inventory()


    def delete_medicine(self):
        row = self.inventory_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "No Selection",
                "Select a medicine record first."
            )
            return

        item = self.inventory_table.item(row, 0)
        if item is None:
            return

        medicine_id = item.text()

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete medicine record {medicine_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message = self.inventory_service.delete_medicine(
            medicine_id
        )

        if not success:
            QMessageBox.warning(
                self, "Delete Failed", str(message)
            )
            return

        QMessageBox.information(self, "Deleted", str(message))
        self.refresh_inventory()


    def create_placeholder_page(self, title, description):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        message_card = QFrame()
        message_card.setObjectName("dashboardCard")

        card_layout = QVBoxLayout(message_card)
        card_layout.setContentsMargins(25, 25, 25, 25)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        description_label = QLabel(description)
        description_label.setObjectName("cardDescription")
        description_label.setWordWrap(True)

        status_label = QLabel(
            "This module's backend and working interface "
            "will be integrated in the next development step."
        )
        status_label.setObjectName("moduleNotice")
        status_label.setWordWrap(True)

        card_layout.addWidget(title_label)
        card_layout.addWidget(description_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(status_label)

        layout.addWidget(message_card)
        layout.addStretch()

        return page

   
    def change_page(self, index):
        page_names = [
            "Home",
            "Patient Record",
            "Inventory",
            "Allocation",
            "Schedule",
            "Report",
            "Security",
        ]

        # Make sure the requested page exists.
        if index < 0 or index >= self.pages.count():
            QMessageBox.warning(
                self,
                "Page Unavailable",
                "This page has not been created yet."
            )
            return

        self.pages.setCurrentIndex(index)
        self.page_heading.setText(page_names[index])

        # Highlight the selected navigation button.
        for button_index, button in enumerate(self.page_buttons):
            button.setProperty("active", button_index == index)
            button.style().unpolish(button)
            button.style().polish(button)


    def sign_out(self):

        reply = QMessageBox.question(
            self,
            "Sign Out",
            "Are you sure you want to sign out?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.login_window = LoginWindow()
            self.login_window.showMaximized()
            self.close()