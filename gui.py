
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QDialog,
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
    QHeaderView

)

from backend.auth_service import AuthService
from backend.patient_service import PatientService


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

        self.setWindowTitle("HIV ARV Allocation and Management System")
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
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)

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

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        success, result = self.auth_service.login(username, password)

        if success:
            self.dashboard = DashboardWindow(result)
            self.dashboard.showMaximized()
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Login Failed",
                str(result)
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


class PatientRegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Register New Patient")
        self.resize(760, 620)

        main_layout = QVBoxLayout(self)

        title = QLabel("Patient Registration")
        title.setObjectName("cardTitle")
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: PERSONAL INFORMATION
        personal_tab = QWidget()
        personal_form = QFormLayout(personal_tab)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full name")

        self.date_of_birth = QLineEdit()
        self.date_of_birth.setPlaceholderText("YYYY-MM-DD")

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

        self.diagnosis_date = QLineEdit()
        self.diagnosis_date.setPlaceholderText(
            "YYYY-MM-DD (optional)"
        )

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

        self.treatment_start = QLineEdit()
        self.treatment_start.setPlaceholderText(
            "YYYY-MM-DD (optional)"
        )

        self.treatment_status = QComboBox()
        self.treatment_status.addItems([
            "Not specified",
            "Active",
            "On hold",
            "Discontinued",
            "Transferred",
        ])

        self.next_appointment = QLineEdit()
        self.next_appointment.setPlaceholderText(
            "YYYY-MM-DD (optional)"
        )

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
        ).setText("Save Patient")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout.addWidget(buttons)

    def get_patient_data(self):
        return {
            "full_name": self.full_name.text().strip(),
            "date_of_birth": self.date_of_birth.text().strip(),
            "sex": self.sex.currentText(),
            "contact_number": self.contact_number.text().strip(),
            "address": self.address.toPlainText().strip(),
            "emergency_contact": (
                self.emergency_contact.text().strip()
            ),
            "diagnosis": self.diagnosis.text().strip(),
            "diagnosis_date": self.diagnosis_date.text().strip(),
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
                self.treatment_start.text().strip()
            ),
            "treatment_status": self.treatment_status.currentText(),
            "next_appointment": (
                self.next_appointment.text().strip()
            ),
            "follow_up_notes": (
                self.follow_up_notes.toPlainText().strip()
            ),
        }

class DashboardWindow(QMainWindow):

    def __init__(self, user):
        super().__init__()

        self.user = user
        self.page_buttons = []

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
            ("Dashboard", 0),
            ("Patient Records", 1),
            ("ARV Inventory", 2),
            ("Allocations", 3),
            ("Reports", 4),
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
        self.pages.addWidget(self.create_home_page())

        self.pages.addWidget(self.create_patients_page())

        self.pages.addWidget(
            self.create_placeholder_page(
                "ARV Inventory",
                "Manage antiretroviral medicine stock and availability."
            )
        )

        self.pages.addWidget(
            self.create_placeholder_page(
                "Allocations",
                "Record and manage antiretroviral medicine allocations."
            )
        )

        self.pages.addWidget(
            self.create_placeholder_page(
                "Reports",
                "View system summaries and generate reports."
            )
        )

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
        layout.setSpacing(15)

        welcome_title = QLabel(
            "Welcome, " + self.user.get("full_name", "Staff")
        )
        welcome_title.setObjectName("welcomeTitle")
        welcome_title.setWordWrap(True)

        welcome_description = QLabel(
            "Use the navigation menu to access the system modules."
        )
        welcome_description.setObjectName("pageDescription")
        welcome_description.setWordWrap(True)

        layout.addWidget(welcome_title)
        layout.addWidget(welcome_description)

        # QUICK ACCESS CARDS
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(12)

        card_items = [
            (
                "Patient Records",
                "Access patient management."
            ),
            (
                "ARV Inventory",
                "Access medicine inventory management."
            ),
            (
                "Allocations",
                "Access medicine allocation management."
            ),
        ]

        for title_text, description_text in card_items:
            card = QFrame()
            card.setObjectName("dashboardCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)

            title_label = QLabel(title_text)
            title_label.setObjectName("cardTitle")

            description_label = QLabel(description_text)
            description_label.setObjectName("cardDescription")
            description_label.setWordWrap(True)

            card_layout.addWidget(title_label)
            card_layout.addWidget(description_label)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
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

        self.pages.setCurrentIndex(index)

        page_names = [
            "Dashboard",
            "Patient Records",
            "ARV Inventory",
            "Allocations",
            "Reports",
        ]

        self.page_heading.setText(page_names[index])

        # Highlight the selected navigation button.
        for button_index, button in enumerate(self.page_buttons):
            button.setProperty(
                "active",
                button_index == index
            )

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
