import copy

from .base_service import BaseService, guarded
from .inventory_service import InventoryService
from .patient_service import PatientService
from .transaction_service import TransactionService


class AllocationService(BaseService):
    ACTIVE = "Active"
    CANCELLED = "Cancelled"

    def __init__(
        self,
        storage=None,
        inventory_service=None,
        patient_service=None,
        transaction_service=None
    ):
        super().__init__(storage)
        self.inventory = inventory_service or InventoryService()
        self.patients = patient_service or PatientService()
        self.transactions = transaction_service or TransactionService(
            self.storage, self.inventory
        )
        self.file_name = "allocations.json"

    def load_all(self):
        return self.storage.load(self.file_name)

    def save_all(self, allocations):
        self.storage.save(self.file_name, allocations)

    def find_batches(self, medicine_name, strength, medicine_id, on_date):
        success, medicines = self.inventory.get_medicines()

        if not success:
            raise ValueError(medicines)

        if medicine_id:
            matches = [
                medicine for medicine in medicines
                if medicine.get("medicine_id") == medicine_id
            ]
        else:
            matches = [
                medicine for medicine in medicines
                if str(medicine.get("medicine_name", "")).casefold()
                == medicine_name.casefold()
                and str(medicine.get("strength", "")).casefold()
                == strength.casefold()
            ]

        usable = []

        for medicine in matches:
            expiry = self.parse_date(medicine.get("expiry_date", ""))

            if expiry is None or expiry < on_date:
                continue

            if int(medicine.get("quantity", 0)) <= 0:
                continue

            usable.append(medicine)

        usable.sort(
            key=lambda item: (
                item.get("expiry_date", ""), item.get("batch_number", "")
            )
        )

        return matches, usable

    @guarded
    def get_available_stock(self, medicine_name="", strength="", medicine_id=""):
        matches, usable = self.find_batches(
            str(medicine_name).strip(),
            str(strength).strip(),
            str(medicine_id).strip(),
            self.today()
        )

        if not matches:
            return False, "Medicine not found in the inventory."

        return True, {
            "total_available": sum(int(item["quantity"]) for item in usable),
            "batches": [
                {
                    "medicine_id": item["medicine_id"],
                    "batch_number": item["batch_number"],
                    "expiry_date": item["expiry_date"],
                    "quantity": int(item["quantity"]),
                }
                for item in usable
            ],
        }

    def restore_quantities(self, medicines):
        for medicine in medicines:
            self.transactions.write_quantity(
                medicine, int(medicine["quantity"])
            )

    def restore_files(self, allocations, transactions):
        for action, data in (
            (self.save_all, allocations),
            (self.transactions.save_all, transactions),
        ):
            try:
                action(data)
            except OSError:
                continue

    @guarded
    def allocate_medicine(self, data, staff=None):
        patient_id = str(data.get("patient_id", "")).strip()

        if not patient_id:
            return False, "Please select a patient."

        success, patient = self.patients.get_patient_by_id(patient_id)

        if not success:
            return False, "Patient record not found."

        medicine_id = str(data.get("medicine_id", "")).strip()
        medicine_name = str(
            data.get("medicine_name") or data.get("name") or ""
        ).strip()
        strength = str(data.get("strength", "")).strip()

        if not medicine_id and not (medicine_name and strength):
            return False, "Please select a medicine."

        quantity = self.parse_positive_int(data.get("quantity", ""))

        if quantity is None:
            return False, "Quantity must be a whole number greater than zero."

        dosage = str(data.get("dosage", "")).strip()

        if not dosage:
            return False, "Dosage instructions are required."

        allocation_text = str(data.get("allocation_date", "")).strip()

        if allocation_text:
            allocation_date = self.parse_date(allocation_text)

            if allocation_date is None:
                return False, "Allocation date must be in YYYY-MM-DD format."

            if allocation_date > self.today():
                return False, "Allocation date cannot be in the future."
        else:
            allocation_date = self.today()

        followup_text = str(data.get("next_followup_date", "")).strip()
        followup_date = None

        if followup_text:
            followup_date = self.parse_date(followup_text)

            if followup_date is None:
                return False, "Follow-up date must be in YYYY-MM-DD format."

            if followup_date < allocation_date:
                return False, (
                    "Follow-up date cannot be before the allocation date."
                )

        matches, usable = self.find_batches(
            medicine_name, strength, medicine_id, allocation_date
        )

        if not matches:
            return False, "Medicine not found in the inventory."

        available = sum(int(item["quantity"]) for item in usable)

        if available < quantity:
            return False, (
                f"Only {available} unexpired units are available. "
                f"Requested: {quantity}."
            )

        picks = []
        remaining = quantity

        for medicine in usable:
            if remaining == 0:
                break

            take = min(remaining, int(medicine["quantity"]))
            picks.append((medicine, take))
            remaining -= take

        written = []

        for medicine, take in picks:
            success, result = self.transactions.write_quantity(
                medicine, int(medicine["quantity"]) - take
            )

            if not success:
                self.restore_quantities(written)
                return False, result

            written.append(medicine)

        allocations = self.load_all()
        transactions = self.transactions.load_all()
        original_allocations = copy.deepcopy(allocations)
        original_transactions = copy.deepcopy(transactions)

        first = picks[0][0]
        allocation_id = self.next_id("ALLOC", allocations, "allocation_id")

        record = {
            "allocation_id": allocation_id,
            "patient_id": patient["patient_id"],
            "patient_name": patient.get("full_name", ""),
            "medicine_name": first["medicine_name"],
            "strength": first["strength"],
            "quantity": quantity,
            "dosage": dosage,
            "batches": [
                {
                    "medicine_id": medicine["medicine_id"],
                    "batch_number": medicine["batch_number"],
                    "expiry_date": medicine["expiry_date"],
                    "quantity": take,
                }
                for medicine, take in picks
            ],
            "allocation_date": allocation_date.isoformat(),
            "next_followup_date": (
                followup_date.isoformat() if followup_date else ""
            ),
            "notes": str(data.get("notes", "")).strip(),
            "allocated_by": self.staff_label(staff),
            "status": self.ACTIVE,
            "created_at": self.timestamp(),
            "cancelled_at": "",
            "cancelled_by": "",
            "cancel_reason": "",
        }

        try:
            allocations.append(record)
            self.save_all(allocations)

            self.transactions.log_transactions([
                {
                    "type": TransactionService.STOCK_OUT,
                    "medicine": medicine,
                    "quantity": take,
                    "balance_after": int(medicine["quantity"]) - take,
                    "reference": allocation_id,
                    "remarks": f"Allocated to {patient['patient_id']}",
                    "staff": staff,
                }
                for medicine, take in picks
            ])
        except (OSError, ValueError) as error:
            self.restore_files(original_allocations, original_transactions)
            self.restore_quantities(written)
            return False, f"Could not save the allocation: {error}"

        return True, record

    @guarded
    def get_allocations(
        self,
        search_text="",
        status="",
        start_date="",
        end_date="",
        patient_id=""
    ):
        start, end, error = self.parse_range(start_date, end_date)

        if error:
            return False, error

        search_text = str(search_text).strip().lower()
        status = str(status).strip().casefold()
        patient_id = str(patient_id).strip()
        results = []

        for record in reversed(self.load_all()):
            if status and record.get("status", "").casefold() != status:
                continue

            if patient_id and record.get("patient_id") != patient_id:
                continue

            if (start or end) and not self.in_range(
                record.get("allocation_date", ""), start, end
            ):
                continue

            if search_text:
                haystack = " ".join(
                    str(record.get(key, "")) for key in (
                        "allocation_id", "patient_id", "patient_name",
                        "medicine_name", "strength"
                    )
                ).lower()

                if search_text not in haystack:
                    continue

            results.append(record)

        return True, results

    @guarded
    def get_allocation(self, allocation_id):
        for record in self.load_all():
            if record.get("allocation_id") == allocation_id:
                return True, record

        return False, "Allocation record not found."

    @guarded
    def cancel_allocation(self, allocation_id, reason, staff=None):
        reason = str(reason).strip()

        if not reason:
            return False, "A reason is required to cancel an allocation."

        allocations = self.load_all()
        original_allocations = copy.deepcopy(allocations)
        record = next(
            (
                item for item in allocations
                if item.get("allocation_id") == allocation_id
            ),
            None
        )

        if record is None:
            return False, "Allocation record not found."

        if record.get("status") != self.ACTIVE:
            return False, "This allocation has already been cancelled."

        targets = []

        for batch in record.get("batches", []):
            medicine = self.transactions.find_medicine(batch["medicine_id"])

            if medicine is None or (
                medicine.get("batch_number") != batch.get("batch_number")
                or str(medicine.get("medicine_name", "")).casefold()
                != record.get("medicine_name", "").casefold()
            ):
                return False, (
                    f"Cannot cancel: batch {batch.get('batch_number')} "
                    f"({batch.get('medicine_id')}) is no longer in the "
                    "inventory."
                )

            targets.append((medicine, int(batch["quantity"])))

        written = []

        for medicine, amount in targets:
            success, result = self.transactions.write_quantity(
                medicine, int(medicine["quantity"]) + amount
            )

            if not success:
                self.restore_quantities(written)
                return False, result

            written.append(medicine)

        original_transactions = copy.deepcopy(self.transactions.load_all())

        record["status"] = self.CANCELLED
        record["cancelled_at"] = self.timestamp()
        record["cancelled_by"] = self.staff_label(staff)
        record["cancel_reason"] = reason

        try:
            self.save_all(allocations)

            self.transactions.log_transactions([
                {
                    "type": TransactionService.STOCK_IN,
                    "medicine": medicine,
                    "quantity": amount,
                    "balance_after": int(medicine["quantity"]) + amount,
                    "reference": allocation_id,
                    "remarks": f"Allocation cancelled: {reason}",
                    "staff": staff,
                }
                for medicine, amount in targets
            ])
        except (OSError, ValueError) as error:
            self.restore_files(original_allocations, original_transactions)
            self.restore_quantities(written)
            return False, f"Could not cancel the allocation: {error}"

        return True, record