from backend.base_service import BaseService, guarded
from backend.inventory_service import InventoryService
from backend.security_service import SecurityService


class TransactionService(BaseService):
    STOCK_IN = "STOCK IN"
    STOCK_OUT = "STOCK OUT"

    def __init__(self, storage=None, inventory_service=None, security_service=None):
        super().__init__(storage)
        self.security = security_service or SecurityService(self.storage)
        self.inventory = inventory_service or InventoryService(self.storage, self.security)
        self.file_name = "stock_transactions.json"

    def load_all(self):
        return self.storage.load(self.file_name)

    def save_all(self, transactions):
        self.storage.save(self.file_name, transactions)

    def find_medicine(self, medicine_id):
        success, medicines = self.inventory.get_medicines()

        if not success:
            raise ValueError(medicines)

        return next(
            (
                medicine for medicine in medicines
                if medicine.get("medicine_id") == medicine_id
            ),
            None
        )

    def write_quantity(self, medicine, quantity):
        return self.inventory.update_medicine(
            medicine["medicine_id"],
            {
                "medicine_name": medicine["medicine_name"],
                "strength": medicine["strength"],
                "batch_number": medicine["batch_number"],
                "quantity": quantity,
                "expiry_date": medicine["expiry_date"],
                "low_stock_threshold": medicine["low_stock_threshold"],
            }
        )

    def log_transactions(self, entries):
        transactions = self.load_all()
        created = []

        for entry in entries:
            medicine = entry["medicine"]

            record = {
                "transaction_id": self.next_id(
                    "TXN", transactions, "transaction_id"
                ),
                "transaction_type": entry["type"],
                "medicine_id": medicine["medicine_id"],
                "medicine_name": medicine["medicine_name"],
                "strength": medicine["strength"],
                "batch_number": medicine["batch_number"],
                "quantity": entry["quantity"],
                "balance_after": entry["balance_after"],
                "reference": entry.get("reference", ""),
                "remarks": entry.get("remarks", ""),
                "performed_by": self.staff_label(entry.get("staff")),
                "transaction_date": self.timestamp(),
            }

            transactions.append(record)
            created.append(record)

        self.save_all(transactions)
        return created

    def apply_movement(
        self, medicine, transaction_type, amount, staff, remarks
    ):
        current = int(medicine.get("quantity", 0))

        if transaction_type == self.STOCK_IN:
            new_quantity = current + amount
        else:
            new_quantity = current - amount

        if new_quantity < 0:
            return False, (
                f"Only {current} units are in stock for this batch."
            )

        success, result = self.write_quantity(medicine, new_quantity)

        if not success:
            return False, result

        try:
            created = self.log_transactions([
                {
                    "type": transaction_type,
                    "medicine": medicine,
                    "quantity": amount,
                    "balance_after": new_quantity,
                    "remarks": remarks,
                    "staff": staff,
                }
            ])
        except (OSError, ValueError) as error:
            self.write_quantity(medicine, current)
            return False, f"Could not record the transaction: {error}"

        staff_info = staff if isinstance(staff, dict) else {} # Declared for auditing
        self.security.log_service_edit(
            service_name="TransactionService",
            record_id=medicine.get("medicine_id"),
            username=staff_info.get("username", "System"),
            staff_id=staff_info.get("staff_id", "System"),
            full_name=staff_info.get("full_name", "System"),
            action_type=transaction_type,
            changes_summary=f"{transaction_type}: {amount} units of {medicine.get('medicine_name')} (Batch: {medicine.get('batch_number')}). Remarks: {remarks}",
            new_data=created[0]
        )

        return True, created[0]

    @guarded
    def stock_in(self, medicine_id, quantity, staff=None, remarks=""):
        amount = self.parse_positive_int(quantity)

        if amount is None:
            return False, "Quantity must be a whole number greater than zero."

        medicine = self.find_medicine(medicine_id)

        if medicine is None:
            return False, "Medicine record not found."

        expiry = self.parse_date(medicine.get("expiry_date", ""))

        if expiry is not None and expiry < self.today():
            return False, "This batch is expired and cannot receive new stock."

        return self.apply_movement(
            medicine, self.STOCK_IN, amount, staff, str(remarks).strip()
        )

    @guarded
    def stock_out(self, medicine_id, quantity, reason, staff=None):
        amount = self.parse_positive_int(quantity)

        if amount is None:
            return False, "Quantity must be a whole number greater than zero."

        if not str(reason).strip():
            return False, "A reason is required for stock-out."

        medicine = self.find_medicine(medicine_id)

        if medicine is None:
            return False, "Medicine record not found."

        return self.apply_movement(
            medicine, self.STOCK_OUT, amount, staff, str(reason).strip()
        )

    @guarded
    def get_transactions(
        self, search_text="", transaction_type="", start_date="", end_date=""
    ):
        start, end, error = self.parse_range(start_date, end_date)

        if error:
            return False, error

        search_text = str(search_text).strip().lower()
        transaction_type = str(transaction_type).strip().upper()
        results = []

        for record in reversed(self.load_all()):
            if transaction_type and (
                record.get("transaction_type") != transaction_type
            ):
                continue

            if (start or end) and not self.in_range(
                record.get("transaction_date", ""), start, end
            ):
                continue

            if search_text:
                haystack = " ".join(
                    str(record.get(key, "")) for key in (
                        "transaction_id", "medicine_id", "medicine_name",
                        "batch_number", "reference", "performed_by"
                    )
                ).lower()

                if search_text not in haystack:
                    continue

            results.append(record)

        return True, results
