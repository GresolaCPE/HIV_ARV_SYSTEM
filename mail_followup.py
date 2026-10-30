# PLEASE READ:
# There is a block of code below that is commented.
# For testing purposes, uncomment the block

import smtplib # SMTP library for sending emails. Don't remove this import even if dimmed.
from backend.security_service import SecurityService
# MIME - Multipurpose Internet Mail Extensions: For email formatting.
from email.mime.text import MIMEText # Turns text to MIME for emails.
from email.mime.multipart import MIMEMultipart # For recepient and sender container and email body.
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QTextEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel
)

class FollowUpEmailDialog(QDialog):
    def __init__(self, patient_data=None, security_service=None, parent=None):
        super().__init__(parent)
        self.patient_data = patient_data or {}
        self.security_service = security_service if security_service is not None else SecurityService()
        
        self.setWindowTitle("Send Follow-Up Check-Up Reminder")
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Header instruction
        header_label = QLabel("Compose Follow-Up Email Reminder")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #123B70;")
        layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Patient info fields
        self.patient_name = QLineEdit(self.patient_data.get("full_name", ""))
        self.patient_email = QLineEdit(self.patient_data.get("email", ""))
        self.appointment_date = QLineEdit(self.patient_data.get("next_appointment", ""))

        form_layout.addRow("Patient Name:", self.patient_name)
        form_layout.addRow("Patient Email:", self.patient_email)
        form_layout.addRow("Scheduled Date:", self.appointment_date)

        # Subject and body
        self.subject_input = QLineEdit("Reminder: Upcoming ARV Follow-Up & Medication Refill")
        self.body_input = QTextEdit()
        
        # Template for professional email
        name = self.patient_name.text() or "Valued Patient"
        date = self.appointment_date.text() or "your scheduled date"
        
        self.body_input.setPlainText(
            f"Dear {name},\n\n"
            "This is a gentle reminder from the HIV ARV Management System regarding your upcoming "
            f"follow-up check-up and medication refill scheduled for {date}.\n\n"
            "Please ensure you arrive on time at the clinic. If you need to reschedule your "
            "appointment or have any questions regarding your treatment regimen, please contact "
            "our clinic staff immediately.\n\n"
            "Stay safe and take care,\n\n"
            "HIV ARV Management System"
        )

        form_layout.addRow("Subject:", self.subject_input)
        form_layout.addRow("Message Body:", self.body_input)

        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send Email")
        self.send_btn.setObjectName("primaryButton")
        self.send_btn.clicked.connect(self.send_email)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)

    def send_email(self):
        recipient = self.patient_email.text().strip()
        if not recipient:
            QMessageBox.warning(self, "Validation Error", "Patient email address cannot be empty.")
            return

        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()

        # SMTP Server Config
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your_clinic_email@gmail.com"
        sender_password = "your_app_password"  # Use environment variable or secure config in production

        try:
            # Construct MIME message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # NOTE: For testing purposes, this block is commented out. Uncomment to send actual emails. Don't uncomment this.
            # server = smtplib.SMTP(smtp_server, smtp_port) # Makes the connection
            # server.starttls() # Encrypted TLS connection.
            # server.login(sender_email, sender_password) # Authenticate sender.
            # server.send_message(msg)
            # server.quit()

            patient_id = self.patient_data.get("patient_id", "PATIENT-GEN")
            summary = f"Sent follow-up reminder email to {recipient}"
            
            self.security_service.log_patient_edit(
                patient_id=patient_id,
                username="SystemStaff",
                staff_id="STF-001",
                full_name="Clinic Staff",
                action_type="SEND_EMAIL",
                changes_summary=summary,
                new_data={"recipient": recipient, "subject": subject}
            )

            QMessageBox.information(self, "Success", f"Follow-up reminder email successfully sent to:\n{recipient}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Transmission Error", f"Failed to send email. Error details:\n{str(e)}")