import json
import os
from datetime import date, datetime


class InventoryService:

    def __init__(self):
        # Store inventory data in the backend folder.
        self.data_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "inventory_data.json"
        )

        self._ensure_data_file()

    def _ensure_data_file(self):
        """Create an empty inventory file if none exists."""
        if not os.path.exists(self.data_file):
            self._save_data([])

    def _load_data(self):
        """Read medicine records from JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Inventory data must be a list.")

            return data

        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                f"Inventory data is invalid: {error}"
            ) from error

    def _save_data(self, medicines):
        """Save medicine records to JSON."""
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(medicines, file, indent=4)

    def get_medicines(self, search_text=""):
        """Return all medicines or matching search results."""
        try:
            medicines = self._load_data()
            search_text = search_text.strip().lower()

            if search_text:
                medicines = [
                    medicine for medicine in medicines
                    if search_text in medicine.get(
                        "medicine_name", ""
                    ).lower()
                    or search_text in medicine.get(
                        "batch_number", ""
                    ).lower()
                    or search_text in medicine.get(
                        "medicine_id", ""
                    ).lower()
                ]

            return True, medicines

        except (OSError, ValueError) as error:
            return False, str(error)

    def _normalize_medicine_data(self, medicine_data):
        """Make GUI field names compatible with backend field names."""
        return {
            "medicine_name": (
                medicine_data.get("medicine_name")
                or medicine_data.get("name")
                or ""
            ).strip(),
            "strength": str(
                medicine_data.get("strength", "")
            ).strip(),
            "batch_number": str(
                medicine_data.get("batch_number", "")
            ).strip(),
            "quantity": medicine_data.get("quantity", ""),
            "expiry_date": str(
                medicine_data.get("expiry_date", "")
            ).strip(),
            "low_stock_threshold": medicine_data.get(
                "low_stock_threshold",
                medicine_data.get("threshold", "")
            ),
        }  

    def add_medicine(self, medicine_data):
        """Validate and add a medicine record."""
        try:
            medicine_data = self._normalize_medicine_data(
            medicine_data)
            medicines = self._load_data()

            required_fields = [
                "medicine_name",
                "strength",
                "batch_number",
                "quantity",
                "expiry_date",
                "low_stock_threshold"
            ]

            for field in required_fields:
                if not str(medicine_data.get(field, "")).strip():
                    return False, f"{field.replace('_', ' ').title()} is required."

            try:
                quantity = int(medicine_data["quantity"])
                threshold = int(medicine_data["low_stock_threshold"])

                if quantity < 0 or threshold < 0:
                    return False, "Quantity and low-stock threshold cannot be negative."

                expiry = date.fromisoformat(
                    medicine_data["expiry_date"]
                )

            except (ValueError, TypeError):
                return False, (
                    "Enter a valid non-negative quantity and threshold, "
                    "and an expiration date in YYYY-MM-DD format."
                )

            # A batch number identifies a specific stock batch.
            for existing in medicines:
                if (
                    existing.get("medicine_name", "").casefold()
                    == medicine_data["medicine_name"].strip().casefold()
                    and existing.get("strength", "").casefold()
                    == medicine_data["strength"].strip().casefold()
                    and existing.get("batch_number", "").casefold()
                    == medicine_data["batch_number"].strip().casefold()
                ):
                    return False, (
                        "This medicine, strength, and batch number "
                        "already exist."
                    )

            medicine = {
                "medicine_id": self._generate_id(medicines),
                "medicine_name": medicine_data["medicine_name"].strip(),
                "strength": medicine_data["strength"].strip(),
                "batch_number": medicine_data["batch_number"].strip(),
                "quantity": quantity,
                "expiry_date": expiry.isoformat(),
                "low_stock_threshold": threshold,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }

            medicines.append(medicine)
            self._save_data(medicines)

            return True, medicine

        except (OSError, ValueError) as error:
            return False, str(error)

    def update_medicine(self, medicine_id, updated_data):
        """Update an existing medicine record."""
        try:
            updated_data = self._normalize_medicine_data(
            updated_data)
            medicines = self._load_data()

            for index, medicine in enumerate(medicines):
                if medicine.get("medicine_id") != medicine_id:
                    continue

                updated = medicine.copy()

                for field in (
                    "medicine_name",
                    "strength",
                    "batch_number"
                ):
                    value = str(updated_data.get(field, "")).strip()
                    if not value:
                        return False, f"{field.replace('_', ' ').title()} is required."
                    updated[field] = value

                try:
                    quantity = int(updated_data["quantity"])
                    threshold = int(updated_data["low_stock_threshold"])
                    expiry = date.fromisoformat(
                        updated_data["expiry_date"]
                    )

                    if quantity < 0 or threshold < 0:
                        return False, "Quantity and threshold cannot be negative."

                except (ValueError, TypeError, KeyError):
                    return False, (
                        "Enter a valid non-negative quantity and threshold, "
                        "and an expiration date in YYYY-MM-DD format."
                    )

                for other in medicines:
                    if other.get("medicine_id") == medicine_id:
                        continue

                    if (
                        other.get("medicine_name", "").casefold()
                        == updated["medicine_name"].casefold()
                        and other.get("strength", "").casefold()
                        == updated["strength"].casefold()
                        and other.get("batch_number", "").casefold()
                        == updated["batch_number"].casefold()
                    ):
                        return False, "That medicine batch already exists."

                updated["quantity"] = quantity
                updated["low_stock_threshold"] = threshold
                updated["expiry_date"] = expiry.isoformat()

                medicines[index] = updated
                self._save_data(medicines)

                return True, updated

            return False, "Medicine record not found."

        except (OSError, ValueError) as error:
            return False, str(error)

    def delete_medicine(self, medicine_id):
        """Delete a medicine record."""
        try:
            medicines = self._load_data()
            remaining = [
                medicine for medicine in medicines
                if medicine.get("medicine_id") != medicine_id
            ]

            if len(remaining) == len(medicines):
                return False, "Medicine record not found."

            self._save_data(remaining)
            return True, "Medicine record deleted successfully."

        except (OSError, ValueError) as error:
            return False, str(error)

    def get_summary(self):
        """Calculate inventory totals and stock alerts."""
        try:
            medicines = self._load_data()
            today = date.today()

            total_types = len(medicines)
            total_units = sum(
                medicine.get("quantity", 0)
                for medicine in medicines
            )

            low_stock = 0
            out_of_stock = 0
            expiring_soon = 0
            expired = 0

            for medicine in medicines:
                quantity = medicine.get("quantity", 0)
                threshold = medicine.get("low_stock_threshold", 0)

                if quantity == 0:
                    out_of_stock += 1
                elif quantity <= threshold:
                    low_stock += 1

                try:
                    expiry = date.fromisoformat(
                        medicine.get("expiry_date", "")
                    )
                    days_remaining = (expiry - today).days

                    if days_remaining < 0:
                        expired += 1
                    elif days_remaining <= 90:
                        expiring_soon += 1

                except ValueError:
                    pass

            return True, {
                "total_types": total_types,
                "total_units": total_units,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "expiring_soon": expiring_soon,
                "expired": expired
            }

        except (OSError, ValueError) as error:
            return False, str(error)

    @staticmethod
    def _generate_id(medicines):
        """Generate a unique medicine ID."""
        existing_ids = {
            medicine.get("medicine_id")
            for medicine in medicines
        }

        number = 1

        while f"MED-{number:04d}" in existing_ids:
            number += 1

        return f"MED-{number:04d}"
