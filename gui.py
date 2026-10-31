import os
import importlib.util

from PyQt6.QtCore import Qt, QDate, QMarginsF
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
    QFileDialog,
    QDateEdit,
    QScrollArea
)
from PyQt6.QtGui import QIntValidator, QTextDocument, QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrinter

from backend.auth_service import AuthService
from backend.patient_service import PatientService
from backend.inventory_service import InventoryService
from allocation_page import AllocationPage
from backend.security_service import SecurityService
from backend.report_service import ReportService
from schedule_page import SchedulePage

_report_html_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "report_html.py"
)
_report_html_spec = importlib.util.spec_from_file_location(
    "report_html", _report_html_path
)
if _report_html_spec is None or _report_html_spec.loader is None:
    raise ImportError(f"Unable to load report module: {_report_html_path}")
report_html = importlib.util.module_from_spec(_report_html_spec)
_report_html_spec.loader.exec_module(report_html)


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



def make_dialog_header(title, text=""):
    """Blue title band shown at the top of every fill-up form."""
    header = QFrame()
    header.setObjectName("dialogHeader")
    box = QVBoxLayout(header)
    box.setContentsMargins(20, 14, 20, 14)
    box.setSpacing(2)

    title_label = QLabel(title)
    title_label.setObjectName("dialogHeaderTitle")
    box.addWidget(title_label)

    if text:
        text_label = QLabel(text)
        text_label.setObjectName("dialogHeaderText")
        text_label.setWordWrap(True)
        box.addWidget(text_label)

    return header


def polish_forms(widget):
    """Give every form inside a dialog the same roomy spacing."""
    for form in widget.findChildren(QFormLayout):
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(18)
        form.setContentsMargins(18, 16, 18, 16)


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
        staff_id_label = QLabel("Staff ID")
        staff_id_label.setObjectName("fieldLabel")

        self.staff_id_input = QLineEdit()
        self.staff_id_input.setPlaceholderText("Create a staff ID (e.g. STAFF001)")

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
            "Create a password (at least 8 characters)"
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


class PatientRegistrationDialog(QDialog):
    def __init__(self, parent=None, patient=None):
        super().__init__(parent)

        self.patient = patient or {}

        self.setWindowTitle(
            "Edit Patient Record"
            if self.patient
            else "Register New Patient"
        )
        self.resize(760, 620)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        main_layout.addWidget(make_dialog_header(
            "Edit Patient Record" if self.patient else "Register New Patient",
            "Fields marked * are required. Date fields open a calendar."
        ))

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
            QDate(1900, 1, 1), QDate.currentDate()
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

        self.emergency_relationship = QComboBox()
        self.emergency_relationship.addItems([
            "Select relationship",
            "Mother",
            "Father",
            "Spouse",
            "Sibling",
            "Child",
            "Guardian",
            "Other Relative",
            "Friend",
            "Other"
        ])

        personal_form.addRow("Full Name *:", self.full_name)
        personal_form.addRow("Date of Birth *:", self.date_of_birth)
        personal_form.addRow("Sex:", self.sex)
        personal_form.addRow("Contact Number:", self.contact_number)
        personal_form.addRow("Address:", self.address)
        personal_form.addRow(
            "Emergency Contact:", self.emergency_contact
        )
        personal_form.addRow("Relationship to Patient:",self.emergency_relationship)

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
        self.diagnosis_date.setDateRange(
            QDate(1900, 1, 1), QDate.currentDate()
        )
        self.diagnosis_date.setDate(QDate.currentDate())

                

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
            QDate(1900, 1, 1), QDate.currentDate()
        )
        self.treatment_start.setDate(QDate.currentDate())

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
        self.next_appointment.setDateRange(
            QDate.currentDate(), QDate(2100, 12, 31)
        )
        self.next_appointment.setDate(QDate.currentDate())


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
        polish_forms(self)

        # SAVE AND CANCEL BUTTONS
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.button(
            QDialogButtonBox.StandardButton.Save
        ).setText("Save Patient")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

                # Fill the form when editing an existing patient.
        if self.patient:
            self.full_name.setText(
                str(self.patient.get("full_name", ""))
            )
            self.set_date_field(
                self.date_of_birth,
                self.patient.get("date_of_birth", "")
            )
            self.sex.setCurrentText(
                str(self.patient.get("sex", "Prefer not to specify"))
            )
            self.contact_number.setText(
                str(self.patient.get("contact_number", ""))
            )
            self.address.setPlainText(
                str(self.patient.get("address", ""))
            )
            self.emergency_contact.setText(
                str(self.patient.get("emergency_contact", ""))
            )


            relationship = self.patient.get(
                "emergency_relationship", "Select relationship"
            )

            index = self.emergency_relationship.findText(relationship)

            if index >= 0:
                self.emergency_relationship.setCurrentIndex(index)
            else:
                self.emergency_relationship.setCurrentText("Other")

            # Core identity fields are fixed after registration.
            self.full_name.setReadOnly(True)
            self.date_of_birth.setReadOnly(True)
            self.sex.setEnabled(False)
            self.full_name.setToolTip("Patient identity is fixed after registration.")
            self.date_of_birth.setToolTip("Date of birth cannot be changed after registration.")
            self.sex.setToolTip("Sex is fixed after registration.")

            self.set_date_field(
                self.diagnosis_date,
                self.patient.get("diagnosis_date", "")
            )
            
            self.medical_history.setPlainText(
                str(self.patient.get("medical_history", ""))
            )
            self.conditions.setPlainText(
                str(self.patient.get(
                    "conditions",
                    self.patient.get("other_conditions", "")
                ))
            )
            self.allergies.setPlainText(
                str(self.patient.get("allergies", ""))
            )
            self.current_medications.setPlainText(
                str(self.patient.get("current_medications", ""))
            )
            self.clinical_notes.setPlainText(
                str(self.patient.get("clinical_notes", ""))
            )

            self.physician.setText(
                str(self.patient.get("attending_physician", ""))
            )
            self.arv_regimen.setText(
                str(self.patient.get("arv_regimen", ""))
            )
            self.set_date_field(
                self.treatment_start,
                self.patient.get(
                    "treatment_start",
                    self.patient.get("treatment_start_date", "")
                )
            )
            self.treatment_status.setCurrentText(
                str(self.patient.get("treatment_status", "Not specified"))
            )
            self.set_date_field(
                self.next_appointment,
                self.patient.get("next_appointment", "")
            )
            self.follow_up_notes.setPlainText(
                str(self.patient.get("follow_up_notes", ""))
            )

    def set_date_field(self, field, value, optional=False):
        if not value and optional:
            field.setDate(QDate(1900, 1, 1))
            return

        parsed_date = QDate.fromString(
            str(value), "yyyy-MM-dd"
        )

        if parsed_date.isValid():
            field.setDate(parsed_date)

    def get_date_field_value(self, field, optional=False):
        if optional and field.date() == QDate(1900, 1, 1):
            return ""

        return field.date().toString("yyyy-MM-dd")

    
    def get_patient_data(self):
        relationship = self.emergency_relationship.currentText()

        if relationship == "Select relationship":
            relationship = ""

        return {
            "full_name": self.full_name.text().strip(),
            "date_of_birth": self.date_of_birth.date().toString("yyyy-MM-dd"),
            "sex": self.sex.currentText(),
            "contact_number": self.contact_number.text().strip(),
            "address": self.address.toPlainText().strip(),
            "emergency_contact": self.emergency_contact.text().strip(),
            "emergency_relationship": relationship,
            "diagnosis": self.diagnosis.text().strip(),
            "diagnosis_date": self.diagnosis_date.date().toString("yyyy-MM-dd"),
            "medical_history": self.medical_history.toPlainText().strip(),
            "conditions": self.conditions.toPlainText().strip(),
            "allergies": self.allergies.toPlainText().strip(),
            "current_medications": self.current_medications.toPlainText().strip(),
            "clinical_notes": self.clinical_notes.toPlainText().strip(),
            "attending_physician": self.physician.text().strip(),
            "arv_regimen": self.arv_regimen.text().strip(),
            "treatment_start": self.treatment_start.date().toString("yyyy-MM-dd"),
            "treatment_status": self.treatment_status.currentText(),
            "next_appointment": self.next_appointment.date().toString("yyyy-MM-dd"),
            "follow_up_notes": self.follow_up_notes.toPlainText().strip(),
        }


class MedicineDialog(QDialog):
    def __init__(self, medicine=None, parent=None):
        super().__init__(parent)

        self.medicine = medicine or {}

        self.setWindowTitle(
            "Edit Medicine" if medicine else "Add Medicine"
        )
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        layout.addWidget(make_dialog_header(
            "Edit Medicine" if medicine else "Add Medicine",
            "Enter the batch details exactly as printed on the package."
        ))
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(18)

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
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("yyyy-MM-dd")
        self.expiry_date.setDateRange(QDate(2000, 1, 1), QDate(2100, 12, 31))
        self.expiry_date.setDate(QDate.currentDate().addYears(1))
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
            expiry = QDate.fromString(
                str(medicine.get("expiry_date", "")), "yyyy-MM-dd"
            )
            if expiry.isValid():
                self.expiry_date.setDate(expiry)
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
        self.security_service = SecurityService()

        self.setWindowTitle(
            "HIV ARV Allocation and Management System"
        )
        self.setMinimumSize(900, 600)

        self.create_ui()
        self.setStyleSheet(load_stylesheet())
        self.refresh_dashboard_schedule()

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

        self.schedule_page = SchedulePage(
            self.user,
            on_change=self.refresh_dashboard_schedule
        )

        self.pages.addWidget(self.schedule_page)  # Index 4: Schedule

        self.pages.addWidget(self.create_reports_page())  # Index 5: Report

        self.pages.addWidget(self.create_security_page())
         # Index 6: Security

        content_layout.addWidget(self.pages)

        # ADD SIDEBAR AND CONTENT
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

        self.setCentralWidget(central_widget)

        self.change_page(0)

    def sign_out(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def create_home_page(self):
        from datetime import date as _date

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(16)

        # Welcome banner
        hero = QFrame()
        hero.setObjectName("heroBanner")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(26, 22, 26, 22)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(4)

        welcome_title = QLabel(
            "Welcome back, " + self.user.get("full_name", "Staff")
        )
        welcome_title.setObjectName("heroTitle")

        welcome_description = QLabel(
            "Here's an overview of your patient records and system activities."
        )
        welcome_description.setObjectName("heroText")
        welcome_description.setWordWrap(True)

        hero_text.addWidget(welcome_title)
        hero_text.addWidget(welcome_description)
        hero_layout.addLayout(hero_text, 1)

        date_label = QLabel(_date.today().strftime("%A, %B %d, %Y"))
        date_label.setObjectName("heroDate")
        hero_layout.addWidget(date_label, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(hero)

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
            ("Total Patients", str(patient_count),
             "Registered patient records", None, "blue", ""),
            ("Medicine Stock", "0 types",
             "0 total units available", "medicine_stock", "teal", ""),
            ("Patients Expected Today", "0",
             "Patients with an appointment today", "today_appointments",
             "amber", ""),
            ("Active Allocations", "0",
             "Medicine allocations in progress", "allocations", "purple", ""),
        ]

        for index, (
            title_text, value_text, description_text, key, accent, icon
        ) in enumerate(summary_items):

            card = QFrame()
            card.setObjectName("dashboardCard")
            card.setProperty("accent", accent)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 16)
            card_layout.setSpacing(6)

            top_row = QHBoxLayout()
            title = QLabel(title_text)
            title.setObjectName("metricCaption")
            title.setWordWrap(True)

            top_row.addWidget(title, 1)

            value = QLabel(value_text)
            value.setObjectName("metricValue")
            value.setProperty("accent", accent)
            value.setWordWrap(True)

            description = QLabel(description_text)
            description.setObjectName("cardDescription")
            description.setWordWrap(True)

            if key == "medicine_stock":
                self.dashboard_inventory_labels["types"] = value
                self.dashboard_inventory_labels["units"] = description

            elif key == "today_appointments":
                self.dashboard_today_appointments_label = value
                self.dashboard_today_appointments_description = description

            elif key == "allocations":
                self.dashboard_allocation_label = value
                self.dashboard_allocation_description = description

            card_layout.addLayout(top_row)
            card_layout.addWidget(value)
            card_layout.addWidget(description)

            summary_layout.addWidget(card, 0, index)
            summary_layout.setColumnStretch(index, 1)

        layout.addLayout(summary_layout)

        # Lower dashboard panels
        panels_layout = QGridLayout()
        panels_layout.setSpacing(14)

        schedule_card = QFrame()
        schedule_card.setObjectName("dashboardCard")
        schedule_card.setProperty("accent", "blue")
        schedule_layout = QVBoxLayout(schedule_card)
        schedule_layout.setContentsMargins(20, 16, 20, 16)

        schedule_title = QLabel("Incoming Patient Schedule")
        schedule_title.setObjectName("cardTitle")
        schedule_title.setProperty("accent", "blue")

        self.dashboard_schedule_message = QLabel(
            "Loading today's appointment..."
        )
        self.dashboard_schedule_message.setObjectName("cardDescription")
        self.dashboard_schedule_message.setTextFormat(Qt.TextFormat.RichText)
        self.dashboard_schedule_message.setWordWrap(True)

        schedule_layout.addWidget(schedule_title)
        schedule_layout.addWidget(self.dashboard_schedule_message)
        schedule_layout.addStretch()

        inventory_card = QFrame()
        inventory_card.setObjectName("dashboardCard")
        inventory_card.setProperty("accent", "teal")
        inventory_layout = QVBoxLayout(inventory_card)
        inventory_layout.setContentsMargins(20, 16, 20, 16)

        inventory_title = QLabel("Inventory Overview")
        inventory_title.setObjectName("cardTitle")
        inventory_title.setProperty("accent", "teal")

        inventory_message = QLabel("Loading inventory information...")
        inventory_message.setObjectName("cardDescription")
        inventory_message.setTextFormat(Qt.TextFormat.RichText)
        inventory_message.setWordWrap(True)
        self.dashboard_inventory_message = inventory_message

        inventory_layout.addWidget(inventory_title)
        inventory_layout.addWidget(inventory_message)
        inventory_layout.addStretch()

        panels_layout.addWidget(schedule_card, 0, 0)
        panels_layout.addWidget(inventory_card, 0, 1)
        panels_layout.setColumnStretch(0, 1)
        panels_layout.setColumnStretch(1, 1)

        layout.addLayout(panels_layout)

        # Quick access
        quick_card = QFrame()
        quick_card.setObjectName("dashboardCard")
        quick_card.setProperty("accent", "rose")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(20, 16, 20, 18)
        quick_layout.setSpacing(12)

        quick_title = QLabel("Quick Actions")
        quick_title.setObjectName("cardTitle")
        quick_title.setProperty("accent", "rose")
        quick_layout.addWidget(quick_title)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        actions = [
            ("Patient Records", 1, "blue"),
            ("Inventory", 2, "teal"),
            ("Allocation", 3, "purple"),
            ("Reports", 5, "amber"),
        ]

        for label, page_index, accent in actions:
            button = QPushButton(label)
            button.setObjectName("quickAction")
            button.setProperty("accent", accent)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, i=page_index: self.change_page(i)
            )
            actions_layout.addWidget(button)

        quick_layout.addLayout(actions_layout)
        layout.addWidget(quick_card)
        layout.addStretch()

        self.update_dashboard_allocations()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(page)
        return scroll

    def update_dashboard_allocations(self):
        try:
            records = ReportService().allocations()
        except Exception:
            self.dashboard_allocation_label.setText("—")
            self.dashboard_allocation_description.setText(
                "Unable to load allocations."
            )
            return

        active = sum(1 for item in records if item.get("status") == "Active")
        units = sum(
            int(item.get("quantity", 0) or 0)
            for item in records if item.get("status") == "Active"
        )
        self.dashboard_allocation_label.setText(str(active))
        self.dashboard_allocation_description.setText(
            f"{units} units issued in total"
        )

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
        edit_button.clicked.connect(
            self.edit_patient_record
        )

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
        delete_button.setObjectName("dangerButton")
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
        self.patient_table.setWordWrap(True)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.verticalHeader().setDefaultSectionSize(48)

        # Column sizing
        header = self.patient_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Allow horizontal scrolling if the window is too narrow
        self.patient_table.setHorizontalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )

        layout.addWidget(self.patient_table, 1)


        self.load_patient_records()
        return page

    def open_patient_registration(self):
        dialog = PatientRegistrationDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        profile = dialog.get_patient_data()

        success, result = self.patient_service.add_patient_profile(
            profile
        )

        if not success:
            QMessageBox.warning(
                self,
                "Registration Failed",
                str(result)
            )
            return

        self.security_service.log_patient_edit(
            patient_id=result["patient_id"],
            username=self.user.get("username", ""),
            staff_id=self.user.get("staff_id", ""),
            full_name=self.user.get("full_name", ""),
            action_type="CREATE",
            changes_summary="Created a new patient record.",
            previous_data={},
            new_data=result
        )

        QMessageBox.information(
            self,
            "Patient Registered",
            "Patient profile saved successfully.\n\n"
            f"Patient ID: {result['patient_id']}"
        )

        self.patient_search_input.clear()
        self.load_patient_records()

    def edit_patient_record(self):
        row = self.patient_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Select a patient record to edit."
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

        updated_profile = dialog.get_patient_data()

        staff = {
            "username": self.user.get("username", ""),
            "staff_id": self.user.get("staff_id", ""),
            "full_name": self.user.get("full_name", "")
        }

        success, result = self.patient_service.update_patient(
            patient_id,
            updated_profile,
            staff=staff
        )

        if not success:
            QMessageBox.warning(
                self,
                "Update Failed",
                str(result)
            )
            return

        QMessageBox.information(
            self,
            "Patient Updated",
            f"Patient record {patient_id} was updated successfully."
        )

        self.load_patient_records(
            self.patient_search_input.text()
        )

    def view_patient_history(self):
        row = self.patient_table.currentRow()
        if row < 0 or self.patient_table.item(row, 0) is None:
            QMessageBox.information(self, "Select a patient", "Select a patient row first to view its saved versions.")
            return
        patient_id = self.patient_table.item(row, 0).text()
        history = self.report_service.patient_history(patient_id) if hasattr(self, "report_service") else ReportService().patient_history(patient_id)
        if not history:
            QMessageBox.information(self, "No history", "No saved history is available for this patient yet.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Patient History — {patient_id}")
        dialog.resize(980, 700)
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(history), 5)
        table.setHorizontalHeaderLabels(["Version", "Date / Time", "Action", "Updated By", "Change Summary"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setWordWrap(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i, entry in enumerate(history):
            values = [
                f"v{entry.get('version', '')}",
                f"{entry.get('date', '')} {entry.get('time', '')}",
                entry.get('action_type', ''),
                f"{entry.get('full_name', '')} ({entry.get('staff_id', '')})",
                entry.get('changes_summary', '')
            ]
            for j, value in enumerate(values):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        layout.addWidget(table)
        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlaceholderText("Select a version to inspect the saved record data.")
        def show_details(selected_row, _column=0):
            if selected_row < 0 or selected_row >= len(history):
                return
            entry = history[selected_row]
            details.setHtml(report_html.history_entry_html(entry))
        table.cellClicked.connect(show_details)
        layout.addWidget(details, 1)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        if history:
            table.selectRow(0)
            show_details(0)
        dialog.exec()

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
            # Record the deletion in the security audit logs
            self.security_service.log_patient_edit(
                patient_id=patient_id,
                username=self.user.get("username", ""),
                staff_id=self.user.get("staff_id", ""),
                full_name=self.user.get("full_name", ""),
                action_type="DELETE",
                changes_summary="Deleted a patient record.",
                previous_data={"patient_id": patient_id},
                new_data={}
            )
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
        delete_button.setObjectName("dangerButton")
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
            QHeaderView.ResizeMode.Stretch
        )

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
    
    
    def refresh_dashboard_schedule(self):
        from datetime import date
        from schedule_service import ScheduleService

        schedule_service = ScheduleService()
        success, patients = schedule_service.get_all_patients()

        if not success:
            self.dashboard_today_appointments_label.setText("—")
            self.dashboard_today_appointments_description.setText(
                "Unable to load appointments."
            )
            self.dashboard_schedule_message.setText(
                "Appointment information could not be loaded."
            )
            return

        today = date.today().isoformat()
        upcoming = []

        for patient in patients:
            appointment_date = str(
                patient.get("next_appointment", "")
            ).strip()

            if not appointment_date:
                continue

            try:
                date.fromisoformat(appointment_date)
            except ValueError:
                continue

            if appointment_date >= today:
                upcoming.append((appointment_date, patient))

        upcoming.sort(key=lambda item: item[0])

        today_count = sum(
            1 for appointment_date, patient in upcoming
            if appointment_date == today
        )

        self.dashboard_today_appointments_label.setText(
            str(today_count)
        )
        self.dashboard_today_appointments_description.setText(
            "Patients expected today"
        )

        if not upcoming:
            self.dashboard_schedule_message.setText(
                "No upcoming patient appointments."
            )
            return

        import html as _html

        rows = []

        for appointment_date, patient in upcoming[:5]:
            name = _html.escape(str(patient.get("full_name", "Unnamed Patient")))
            tag = (
                ' &nbsp;<span style="color:#0F2F57;font-weight:bold;">TODAY</span>'
                if appointment_date == today else ""
            )
            rows.append(
                '<tr><td style="padding:4px 16px 4px 0;color:#1B4F8A;'
                f'font-weight:bold;">{appointment_date}</td>'
                f'<td style="color:#17365D;">{name}{tag}</td></tr>'
            )

        text = "<table>" + "".join(rows) + "</table>"

        if len(upcoming) > 5:
            text += (
                '<p style="color:#64748B;">'
                f"...and {len(upcoming) - 5} more appointment(s).</p>"
            )

        self.dashboard_schedule_message.setText(text)

    def refresh_inventory(self):
        self.update_dashboard_allocations()
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
        expiring = summary.get("expiring_soon", 0)
        expired = summary.get("expired", 0)

        def stat(label, value, bad_color, ok_color="#17365D"):
            color = bad_color if value else ok_color
            return (
                '<tr><td style="padding:4px 22px 4px 0;color:#475569;">'
                f"{label}</td>"
                f'<td style="color:{color};font-weight:bold;font-size:16px;">'
                f"{value}</td></tr>"
            )

        self.dashboard_inventory_message.setText(
            "<table>"
            + stat("Medicine types", total_types, "#17365D", "#17365D")
            + stat("Total units", total_units, "#17365D", "#17365D")
            + stat("Low-stock items", low_stock, "#B45309")
            + stat("Out-of-stock items", out_of_stock, "#B91C1C")
            + stat("Expiring within 90 days", expiring, "#B45309")
            + stat("Expired batches", expired, "#B91C1C")
            + "</table>"
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



    def create_reports_page(self):
        """Search, preview and export patient and medicine records."""
        self.report_service = ReportService()
        self._report_html_text = ""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        controls = QFrame()
        controls.setObjectName("dashboardCard")
        controls.setProperty("accent", "blue")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(20, 16, 20, 18)
        controls_layout.setSpacing(10)

        heading = QLabel("Generate a document")
        heading.setObjectName("cardTitle")
        heading.setProperty("accent", "blue")
        controls_layout.addWidget(heading)

        intro = QLabel(
            "Find patient records, version history, referral forms, "
            "allocation history, and stock movement totals. Export any "
            "preview as a PDF for printing or as an HTML document."
        )
        intro.setObjectName("cardDescription")
        intro.setWordWrap(True)
        controls_layout.addWidget(intro)

        form = QFormLayout()
        form.setVerticalSpacing(10)
        form.setHorizontalSpacing(18)

        self.report_type = QComboBox()
        self.report_type.addItems([
            "Patient Record",
            "Patient Record History",
            "Referral Form",
            "Allocation History",
            "Medicine Stock Movement"
        ])
        form.addRow("Document type:", self.report_type)

        self.report_patient_id = QLineEdit()
        self.report_patient_id.setPlaceholderText("Enter exact Patient ID")
        form.addRow("Patient ID:", self.report_patient_id)

        self.report_record = QComboBox()
        self.report_record.addItem("All records", "")
        form.addRow("History / record to retrieve:", self.report_record)

        self.referral_reason = QLineEdit()
        self.referral_reason.setPlaceholderText("Reason for referral (for referral documents)")
        form.addRow("Referral reason (optional):", self.referral_reason)
        self.referral_facility = QLineEdit()
        self.referral_facility.setPlaceholderText("Receiving facility / specialist")
        form.addRow("Referred to (optional):", self.referral_facility)
        controls_layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        search_button = QPushButton("Generate Preview")
        search_button.setObjectName("loginButton")
        search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_button.clicked.connect(self.generate_report_preview)
        buttons.addWidget(search_button)

        pdf_button = QPushButton("Export PDF / Print")
        pdf_button.setObjectName("primaryButton")
        pdf_button.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_button.clicked.connect(self.export_report_pdf)
        buttons.addWidget(pdf_button)

        html_button = QPushButton("Save Document (HTML)")
        html_button.setCursor(Qt.CursorShape.PointingHandCursor)
        html_button.clicked.connect(self.export_report_html)
        buttons.addWidget(html_button)
        buttons.addStretch()
        controls_layout.addLayout(buttons)

        layout.addWidget(controls)

        self.report_preview = QTextEdit()
        self.report_preview.setObjectName("reportPreview")
        self.report_preview.setReadOnly(True)
        self.report_preview.document().setDocumentMargin(24)
        self.report_preview.setPlaceholderText(
            "Your printable document preview will appear here."
        )
        layout.addWidget(self.report_preview, 1)

        self.report_type.currentTextChanged.connect(self.refresh_report_choices)
        self.report_patient_id.textChanged.connect(self.refresh_report_choices)
        self.report_type.currentTextChanged.connect(self.update_referral_inputs)
        self.update_referral_inputs(self.report_type.currentText())
        self.refresh_report_choices()
        return page

    def update_referral_inputs(self, report_type):
        is_referral = report_type == "Referral Form"
        self.referral_reason.setEnabled(is_referral)
        self.referral_facility.setEnabled(is_referral)
        if not is_referral:
            self.referral_reason.clear()
            self.referral_facility.clear()

    def refresh_report_choices(self, *args):
        if not hasattr(self, "report_record"):
            return
        report_type = self.report_type.currentText()
        patient_id = self.report_patient_id.text().strip()
        self.report_record.clear()
        self.report_record.addItem("All records", "")

        if report_type == "Patient Record History" and patient_id:
            for row in self.report_service.patient_history(patient_id):
                label = "{} | v{} | {} | {}".format(
                    row.get("date", ""), row.get("version", ""),
                    row.get("action_type", ""), row.get("changes_summary", "")
                )
                self.report_record.addItem(label, row.get("audit_id", ""))
        elif report_type == "Allocation History":
            for row in self.report_service.allocations(patient_id):
                label = "{} | {} | {} | {} units | {}".format(
                    row.get("allocation_date", ""), row.get("allocation_id", ""),
                    row.get("medicine_name", ""), row.get("quantity", ""),
                    row.get("status", "")
                )
                self.report_record.addItem(label, row.get("allocation_id", ""))
        elif report_type == "Medicine Stock Movement":
            for row in self.report_service.transactions():
                label = "{} | {} | {} | {} units".format(
                    str(row.get("transaction_date", ""))[:10],
                    row.get("transaction_id", ""), row.get("transaction_type", ""),
                    row.get("quantity", "")
                )
                self.report_record.addItem(label, row.get("transaction_id", ""))

    def generate_report_preview(self):
        kind = self.report_type.currentText()
        patient_id = self.report_patient_id.text().strip()
        selected_id = self.report_record.currentData()
        staff_name = self.user.get("full_name", "Staff")
        staff_id = self.user.get("staff_id", "")
        generated_by = "{} ({})".format(staff_name, staff_id)

        if kind in ("Patient Record", "Patient Record History", "Referral Form"):
            if not patient_id:
                QMessageBox.information(self, "Patient ID required", "Enter a Patient ID first.")
                return
            patient = self.report_service.patient(patient_id)
            if not patient:
                QMessageBox.warning(self, "No patient found", "No patient record matches that Patient ID.")
                return

            if kind == "Patient Record":
                document = report_html.patient_record_html(patient, generated_by)
            elif kind == "Referral Form":
                document = report_html.referral_html(
                    patient,
                    self.referral_reason.text().strip(),
                    self.referral_facility.text().strip(),
                    staff_name,
                    staff_id
                )
            else:
                history = self.report_service.patient_history(patient_id)
                if selected_id:
                    history = [r for r in history if r.get("audit_id") == selected_id]
                if not history:
                    QMessageBox.information(self, "No history", "No saved history entries were found for this patient.")
                    return
                document = report_html.patient_history_html(patient, history, generated_by)

        elif kind == "Allocation History":
            records = self.report_service.allocations(patient_id)
            if selected_id:
                records = [r for r in records if r.get("allocation_id") == selected_id]
            if not records:
                QMessageBox.information(self, "No allocations", "No allocation records match the selected criteria.")
                return
            document = report_html.allocation_html(records, patient_id, generated_by)

        else:
            records = self.report_service.transactions()
            if selected_id:
                records = [r for r in records if r.get("transaction_id") == selected_id]
            summary = self.report_service.stock_summary()
            document = report_html.stock_html(records, summary, generated_by)

        self._report_html_text = document
        self.report_preview.setHtml(document)

    def export_report_pdf(self):
        if not self._report_html_text:
            self.generate_report_preview()
        if not self._report_html_text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save printable PDF", "system_report.pdf", "PDF files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageMargins(QMarginsF(16, 16, 16, 16), QPageLayout.Unit.Millimeter)
        printer.setOutputFileName(path)

        # Print from a fresh document so the on-screen preview margin
        # does not add extra white space to the printed page.
        document = QTextDocument()
        document.setHtml(self._report_html_text)
        document.print(printer)

        QMessageBox.information(self, "PDF saved", "Printable report saved to:\n" + path)

    def export_report_html(self):
        if not self._report_html_text:
            self.generate_report_preview()
        if not self._report_html_text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save editable document", "system_report.html", "HTML documents (*.html)")
        if not path:
            return
        if not path.lower().endswith(".html"):
            path += ".html"
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._report_html_text)
        QMessageBox.information(self, "Document saved", "HTML document saved to:\n" + path)

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

    
    def create_security_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("Security and Audit Logs")
        title.setObjectName("cardTitle")

        description = QLabel(
            "Review login attempts and track changes made "
            "to patient records."
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        # Search and refresh controls
        controls = QHBoxLayout()

        self.security_search_input = QLineEdit()
        self.security_search_input.setPlaceholderText(
            "Search username, staff ID, patient ID, date, or action..."
        )
        self.security_search_input.returnPressed.connect(
            self.refresh_security_logs
        )

        search_button = QPushButton("Search")
        search_button.setObjectName("loginButton")
        search_button.clicked.connect(self.refresh_security_logs)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("linkButton")
        refresh_button.clicked.connect(
            lambda: (
                self.security_search_input.clear(),
                self.refresh_security_logs()
            )
        )

        controls.addWidget(self.security_search_input, 1)
        controls.addWidget(search_button)
        controls.addWidget(refresh_button)
        layout.addLayout(controls)

        # Separate tabs for login and patient audit records
        self.security_tabs = QTabWidget()

        self.login_audit_table = QTableWidget()
        self.login_audit_table.setColumnCount(7)
        self.login_audit_table.setHorizontalHeaderLabels([
            "Username",
            "Staff ID",
            "Full Name",
            "Date",
            "Time",
            "Status",
            "IP Address"
        ])

        self.patient_audit_table = QTableWidget()
        self.patient_audit_table.setColumnCount(8)
        self.patient_audit_table.setHorizontalHeaderLabels([
            "Audit ID",
            "Patient ID",
            "Version",
            "Action",
            "Staff ID",
            "Username",
            "Date / Time",
            "Change Summary"
        ])

        for table in (
            self.login_audit_table,
            self.patient_audit_table
        ):
            table.setEditTriggers(
                QTableWidget.EditTrigger.NoEditTriggers
            )
            table.setSelectionBehavior(
                QTableWidget.SelectionBehavior.SelectRows
            )
            table.setAlternatingRowColors(True)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )

        self.security_tabs.addTab(
            self.login_audit_table, "Login Audit Logs"
        )
        self.security_tabs.addTab(
            self.patient_audit_table, "Patient Audit Logs"
        )

        layout.addWidget(self.security_tabs, 1)

        self.refresh_security_logs()

        return page

    def refresh_security_logs(self):
        if not hasattr(self, "security_search_input"):
            return

        query = self.security_search_input.text().strip()

        # Load login attempts
        login_logs = self.security_service.get_login_logs(query)
        self.login_audit_table.setRowCount(0)

        for log in login_logs:
            row = self.login_audit_table.rowCount()
            self.login_audit_table.insertRow(row)

            values = [
                log.get("username", ""),
                log.get("staff_id", ""),
                log.get("full_name", ""),
                log.get("date", ""),
                log.get("time", ""),
                log.get("status", ""),
                log.get("ip_address", "")
            ]

            for column, value in enumerate(values):
                self.login_audit_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

        # Load patient record changes
        patient_logs = (
            self.security_service.get_all_patient_audit_logs(query)
        )
        self.patient_audit_table.setRowCount(0)

        for log in patient_logs:
            row = self.patient_audit_table.rowCount()
            self.patient_audit_table.insertRow(row)

            values = [
                log.get("audit_id", ""),
                log.get("patient_id", ""),
                log.get("version", ""),
                log.get("action_type", ""),
                log.get("staff_id", ""),
                log.get("username", ""),
                f"{log.get('date', '')} {log.get('time', '')}",
                log.get("changes_summary", "")
            ]

            for column, value in enumerate(values):
                self.patient_audit_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

   
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