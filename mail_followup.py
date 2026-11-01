"""Privacy-conscious follow-up email dialog. Configure SMTP via environment variables."""
import os
import re
import smtplib
from email.message import EmailMessage
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel)
from backend.security_service import SecurityService

class FollowUpEmailDialog(QDialog):
    def __init__(self, patient_data=None, security_service=None, staff=None, parent=None):
        super().__init__(parent)
        self.patient_data = patient_data or {}
        self.security_service = security_service or SecurityService()
        self.staff = staff or {}
        self.setWindowTitle("Send Appointment Confirmation / Follow-Up Reminder")
        self.setMinimumSize(560, 480)
        layout = QVBoxLayout(self)
        title = QLabel("Appointment Confirmation / Follow-Up Reminder")
        title.setStyleSheet("font-size:15px;font-weight:bold;color:#123B70;")
        layout.addWidget(title)
        form = QFormLayout()
        self.patient_name = QLineEdit(str(self.patient_data.get("full_name", "")))
        self.patient_email = QLineEdit(str(self.patient_data.get("email", "")))
        self.appointment_date = QLineEdit(str(self.patient_data.get("next_appointment", "")))
        self.subject_input = QLineEdit("Appointment Reminder")
        self.body_input = QTextEdit()
        name = self.patient_name.text().strip() or "Patient"
        date = self.appointment_date.text().strip() or "your scheduled date"
        # Keep subject/body discreet: do not expose HIV status or treatment details.
        self.body_input.setPlainText(
            f"Dear {name},\n\nThis is a reminder from your clinic about your upcoming appointment on {date}.\n\n"
            "If you need to confirm or reschedule, please contact the clinic directly.\n\n"
            "Thank you,\nClinic Staff"
        )
        form.addRow("Patient Name:", self.patient_name)
        form.addRow("Patient Email:", self.patient_email)
        form.addRow("Appointment Date:", self.appointment_date)
        form.addRow("Email Subject:", self.subject_input)
        form.addRow("Message:", self.body_input)
        layout.addLayout(form)
        note = QLabel("Email is optional. If no address is available, use the printable appointment record instead.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#64748B;font-size:11px;")
        layout.addWidget(note)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        self.send_btn = QPushButton("Send Email")
        self.send_btn.setObjectName("primaryButton")
        self.send_btn.clicked.connect(self.send_email)
        buttons.addWidget(cancel)
        buttons.addWidget(self.send_btn)
        layout.addLayout(buttons)

    def send_email(self):
        recipient = self.patient_email.text().strip()
        if not recipient or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
            QMessageBox.warning(self, "Invalid Email", "Enter a valid patient email address.")
            return
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()
        if not subject or not body:
            QMessageBox.warning(self, "Incomplete Message", "Subject and message are required.")
            return
        host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        try:
            port = int(os.getenv("SMTP_PORT", "587"))
        except ValueError:
            QMessageBox.warning(self, "SMTP Configuration", "SMTP_PORT must be a number.")
            return
        sender = os.getenv("SMTP_USERNAME", "").strip()
        password = os.getenv("SMTP_PASSWORD", "")
        from_address = os.getenv("SMTP_FROM", sender).strip()
        if not sender or not password or not from_address:
            QMessageBox.warning(
                self, "Email Not Configured",
                "Email sending is not configured yet. Set SMTP_USERNAME, SMTP_PASSWORD, "
                "and optionally SMTP_FROM in Windows environment variables, then restart the app."
            )
            return
        message = EmailMessage()
        message["From"] = from_address
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        try:
            with smtplib.SMTP(host, port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender, password)
                server.send_message(message)
            staff = self.staff or {}
            self.security_service.log_service_edit(
                service_name="follow_up_email",
                record_id=self.patient_data.get("patient_id", ""),
                action_type="EMAIL_SENT",
                changes_summary=f"Appointment reminder email sent to {recipient}",
                username=staff.get("username", "System"),
                staff_id=staff.get("staff_id", "System"),
                full_name=staff.get("full_name", "System"),
                new_data={"recipient": recipient, "subject": subject}
            )
            QMessageBox.information(self, "Email Sent", f"The reminder was successfully sent to {recipient}.")
            self.accept()
        except (OSError, smtplib.SMTPException) as exc:
            QMessageBox.critical(self, "Email Delivery Failed", f"The email was not sent.\n\n{exc}")
