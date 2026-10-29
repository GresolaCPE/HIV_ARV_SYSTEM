from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QIntValidator
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.allocation_service import AllocationService


class NewAllocationDialog(QDialog):
    def __init__(self, allocation_service, parent=None):
        super().__init__(parent)

        self.allocation_service = allocation_service

        self.setWindowTitle("New Allocation")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.patient = QComboBox()
        self.patient.setEditable(True)
        self.patient.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.patient.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.patient.completer().setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        form.addRow("Patient:", self.patient)

        self.medicine = QComboBox()
        self.medicine.currentIndexChanged.connect(self.update_availability)
        form.addRow("Medicine:", self.medicine)

        self.availability = QLabel("")
        self.availability.setObjectName("cardDescription")
        self.availability.setWordWrap(True)
        form.addRow("", self.availability)

        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("Number of units")
        self.quantity.setValidator(QIntValidator(1, 100000000, self))
        form.addRow("Quantity:", self.quantity)

        self.dosage = QLineEdit()
        self.dosage.setPlaceholderText("e.g., 1 tablet once daily")
        form.addRow("Dosage:", self.dosage)

        self.allocation_date = QLineEdit(date.today().isoformat())
        self.allocation_date.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Allocation Date:", self.allocation_date)

        self.next_followup = QLineEdit()
        self.next_followup.setPlaceholderText("YYYY-MM-DD (optional)")
        form.addRow("Next Follow-up:", self.next_followup)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)
        self.notes.setPlaceholderText("Optional notes")
        form.addRow("Notes:", self.notes)

        layout.addLayout(form)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.load_patients()
        self.load_medicines()

    def load_patients(self):
        success, patients = self.allocation_service.patients.get_patients()

        if not success:
            patients = []

        patients = sorted(
            patients, key=lambda item: str(item.get("full_name", "")).casefold()
        )

        for patient in patients:
            label = f"{patient['patient_id']} - {patient.get('full_name', '')}"
            self.patient.addItem(label, patient)

        self.patient.setCurrentIndex(-1)
        self.patient.lineEdit().setPlaceholderText(
            "Type a name or patient ID"
        )

    def load_medicines(self):
        success, medicines = self.allocation_service.inventory.get_medicines()

        if not success:
            medicines = []

        seen = set()

        for medicine in medicines:
            name = str(medicine.get("medicine_name", "")).strip()
            strength = str(medicine.get("strength", "")).strip()
            key = (name.casefold(), strength.casefold())

            if key in seen:
                continue

            seen.add(key)

            success, stock = self.allocation_service.get_available_stock(
                name, strength
            )

            if not success or stock["total_available"] <= 0:
                continue

            self.medicine.addItem(
                f"{name} {strength} - {stock['total_available']} available",
                {
                    "name": name,
                    "strength": strength,
                    "total": stock["total_available"],
                    "batches": stock["batches"],
                },
            )

        if self.medicine.count() == 0:
            self.availability.setText(
                "No unexpired stock is available. Add or restock "
                "medicine in the Inventory page first."
            )
            self.buttons.button(
                QDialogButtonBox.StandardButton.Save
            ).setEnabled(False)
        else:
            self.update_availability()

    def update_availability(self):
        data = self.medicine.currentData()

        if not data:
            return

        batches = "; ".join(
            f"batch {batch['batch_number']}: {batch['quantity']} units "
            f"(expires {batch['expiry_date']})"
            for batch in data["batches"][:3]
        )

        extra = len(data["batches"]) - 3
        suffix = f"; and {extra} more" if extra > 0 else ""

        self.availability.setText(
            f"Stock is taken from the earliest-expiring batch first. "
            f"{batches}{suffix}"
        )

    def warn(self, title, message):
        QMessageBox.warning(self, title, message)

    def validate_and_accept(self):
        patient_index = self.patient.findText(self.patient.currentText())

        if patient_index < 0:
            self.warn("Patient Required", "Choose a patient from the list.")
            return

        medicine = self.medicine.currentData()

        if not medicine:
            self.warn("Medicine Required", "Choose a medicine.")
            return

        if not self.quantity.text().strip():
            self.warn("Quantity Required", "Enter the quantity to allocate.")
            return

        quantity = int(self.quantity.text())

        if quantity < 1:
            self.warn("Invalid Quantity", "Quantity must be at least 1.")
            return

        if quantity > medicine["total"]:
            self.warn(
                "Not Enough Stock",
                f"Only {medicine['total']} unexpired units are available."
            )
            return

        if not self.dosage.text().strip():
            self.warn("Dosage Required", "Enter the dosage instructions.")
            return

        service = self.allocation_service
        allocated_on = service.parse_date(self.allocation_date.text())

        if allocated_on is None:
            self.warn(
                "Invalid Date",
                "Enter the allocation date as YYYY-MM-DD."
            )
            return

        if allocated_on > date.today():
            self.warn(
                "Invalid Date", "The allocation date cannot be in the future."
            )
            return

        followup_text = self.next_followup.text().strip()

        if followup_text:
            followup = service.parse_date(followup_text)

            if followup is None:
                self.warn(
                    "Invalid Date",
                    "Enter the follow-up date as YYYY-MM-DD."
                )
                return

            if followup < allocated_on:
                self.warn(
                    "Invalid Date",
                    "The follow-up date cannot be before the allocation date."
                )
                return

        patient = self.patient.itemData(patient_index)
        status = str(patient.get("treatment_status", ""))

        if status in ("Discontinued", "Transferred"):
            reply = QMessageBox.question(
                self,
                "Confirm Allocation",
                f"This patient's treatment status is {status}. "
                "Allocate medicine anyway?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        self.accept()

    def get_data(self):
        patient = self.patient.itemData(
            self.patient.findText(self.patient.currentText())
        )
        medicine = self.medicine.currentData()

        return {
            "patient_id": patient["patient_id"],
            "medicine_name": medicine["name"],
            "strength": medicine["strength"],
            "quantity": int(self.quantity.text()),
            "dosage": self.dosage.text().strip(),
            "allocation_date": self.allocation_date.text().strip(),
            "next_followup_date": self.next_followup.text().strip(),
            "notes": self.notes.toPlainText().strip(),
        }


class AllocationPage(QWidget):
    COLUMNS = [
        ("Allocation ID", "allocation_id"),
        ("Date", "allocation_date"),
        ("Patient ID", "patient_id"),
        ("Patient Name", "patient_name"),
        ("Medicine", "medicine_name"),
        ("Strength", "strength"),
        ("Quantity", "quantity"),
        ("Dosage", "dosage"),
        ("Next Follow-up", "next_followup_date"),
        ("Allocated By", "allocated_by"),
        ("Status", "status"),
    ]

    def __init__(self, user, on_change=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.on_change = on_change
        self.allocation_service = AllocationService()
        self.records = []

        self.create_ui()
        self.load_allocations()

    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        summary_layout = QGridLayout()
        summary_layout.setSpacing(12)

        self.summary_labels = {}

        summary_items = [
            ("Active Allocations", "active"),
            ("Units Allocated", "units"),
            ("Allocated Today", "today"),
            ("Cancelled", "cancelled"),
        ]

        for index, (title_text, key) in enumerate(summary_items):
            card = QFrame()
            card.setObjectName("dashboardCard")

            card_layout = QVBoxLayout(card)

            title = QLabel(title_text)
            title.setObjectName("cardDescription")

            value = QLabel("0")
            value.setObjectName("metricValue")

            self.summary_labels[key] = value

            card_layout.addWidget(title)
            card_layout.addWidget(value)

            summary_layout.addWidget(card, 0, index)

        layout.addLayout(summary_layout)

        actions = QHBoxLayout()

        new_button = QPushButton("+ New Allocation")
        new_button.setObjectName("loginButton")
        new_button.clicked.connect(self.new_allocation)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by allocation ID, patient, or medicine"
        )
        self.search_input.returnPressed.connect(self.load_allocations)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Cancelled"])
        self.status_filter.currentIndexChanged.connect(self.load_allocations)

        search_button = QPushButton("Search")
        search_button.setObjectName("loginButton")
        search_button.clicked.connect(self.load_allocations)

        details_button = QPushButton("View Details")
        details_button.setObjectName("linkButton")
        details_button.clicked.connect(self.view_details)

        cancel_button = QPushButton("Cancel Allocation")
        cancel_button.setObjectName("linkButton")
        cancel_button.clicked.connect(self.cancel_selected)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("linkButton")
        refresh_button.clicked.connect(self.refresh)

        actions.addWidget(new_button)
        actions.addWidget(self.search_input, 1)
        actions.addWidget(self.status_filter)
        actions.addWidget(search_button)
        actions.addWidget(details_button)
        actions.addWidget(cancel_button)
        actions.addWidget(refresh_button)

        layout.addLayout(actions)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(
            [label for label, _ in self.COLUMNS]
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setHorizontalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )
        self.table.doubleClicked.connect(self.view_details)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        layout.addWidget(self.table, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_allocations()

    def refresh(self):
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.load_allocations()

    def load_allocations(self):
        status = self.status_filter.currentText()
        status = "" if status == "All" else status

        success, records = self.allocation_service.get_allocations(
            search_text=self.search_input.text(), status=status
        )

        if not success:
            QMessageBox.warning(self, "Allocation Error", str(records))
            return

        self.records = records
        self.table.setRowCount(0)

        muted = QBrush(QColor("#94A3B8"))

        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for column, (_, key) in enumerate(self.COLUMNS):
                item = QTableWidgetItem(str(record.get(key, "") or "-"))

                if record.get("status") == AllocationService.CANCELLED:
                    item.setForeground(muted)

                self.table.setItem(row, column, item)

        self.update_summary()

    def update_summary(self):
        success, records = self.allocation_service.get_allocations()

        if not success:
            return

        today = date.today().isoformat()
        active = [
            item for item in records
            if item.get("status") == AllocationService.ACTIVE
        ]

        self.summary_labels["active"].setText(str(len(active)))
        self.summary_labels["units"].setText(
            str(sum(int(item.get("quantity", 0)) for item in active))
        )
        self.summary_labels["today"].setText(
            str(sum(1 for item in active if item.get("allocation_date") == today))
        )
        self.summary_labels["cancelled"].setText(
            str(len(records) - len(active))
        )

    def selected_record(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "No Selection", "Select an allocation record first."
            )
            return None

        item = self.table.item(row, 0)

        if item is None:
            return None

        return next(
            (
                record for record in self.records
                if record.get("allocation_id") == item.text()
            ),
            None
        )

    @staticmethod
    def describe_batches(record):
        return ", ".join(
            f"batch {batch['batch_number']} x{batch['quantity']} "
            f"(expires {batch['expiry_date']})"
            for batch in record.get("batches", [])
        ) or "-"

    def notify_changed(self):
        if self.on_change:
            self.on_change()

    def new_allocation(self):
        dialog = NewAllocationDialog(self.allocation_service, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        success, result = self.allocation_service.allocate_medicine(
            dialog.get_data(), self.user
        )

        if not success:
            QMessageBox.warning(self, "Unable to Allocate", str(result))
            return

        QMessageBox.information(
            self,
            "Allocation Saved",
            f"{result['allocation_id']}: {result['quantity']} units of "
            f"{result['medicine_name']} {result['strength']} allocated to "
            f"{result['patient_name']}.\n\n"
            f"Taken from: {self.describe_batches(result)}"
        )

        self.load_allocations()
        self.notify_changed()

    def view_details(self):
        record = self.selected_record()

        if record is None:
            return

        lines = [
            f"Allocation: {record['allocation_id']}",
            f"Status: {record['status']}",
            f"Date: {record['allocation_date']}",
            f"Patient: {record['patient_name']} ({record['patient_id']})",
            f"Medicine: {record['medicine_name']} {record['strength']} "
            f"x {record['quantity']}",
            f"Dosage: {record['dosage']}",
            f"Batches used: {self.describe_batches(record)}",
            f"Next follow-up: {record.get('next_followup_date') or '-'}",
            f"Notes: {record.get('notes') or '-'}",
            f"Allocated by: {record['allocated_by']}",
        ]

        if record["status"] == AllocationService.CANCELLED:
            lines.append(
                f"Cancelled by: {record.get('cancelled_by')} on "
                f"{record.get('cancelled_at')}"
            )
            lines.append(f"Reason: {record.get('cancel_reason')}")

        QMessageBox.information(
            self, "Allocation Details", "\n".join(lines)
        )

    def cancel_selected(self):
        record = self.selected_record()

        if record is None:
            return

        if record["status"] != AllocationService.ACTIVE:
            QMessageBox.warning(
                self, "Already Cancelled",
                "This allocation has already been cancelled."
            )
            return

        reason, accepted = QInputDialog.getText(
            self,
            "Cancel Allocation",
            f"Cancel {record['allocation_id']} and return "
            f"{record['quantity']} units to the inventory?\n\n"
            "Reason for cancelling:"
        )

        if not accepted:
            return

        success, result = self.allocation_service.cancel_allocation(
            record["allocation_id"], reason, self.user
        )

        if not success:
            QMessageBox.warning(self, "Unable to Cancel", str(result))
            return

        QMessageBox.information(
            self,
            "Allocation Cancelled",
            f"{record['allocation_id']} was cancelled and the stock "
            "was returned to the inventory."
        )

        self.load_allocations()
        self.notify_changed()
