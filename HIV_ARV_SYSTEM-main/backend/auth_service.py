import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from backend.storage import JSONStorage
from backend.security_service import SecurityService

class AuthService:
    def __init__(self):
        self.storage = JSONStorage()
        self.security = SecurityService(self.storage)
        self.users_file = "users.json"
        self.authorized_file = "authorized_staff.json"

    # -----------------------------
    # PASSWORD SECURITY
    # -----------------------------

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_bytes(16)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            310_000
        )

        return salt.hex(), hashed.hex()

    def _verify_password(self, password, salt, stored_hash):
        _, hashed = self._hash_password(
            password,
            bytes.fromhex(salt)
        )

        return hmac.compare_digest(hashed, stored_hash)

    # -----------------------------
    # STAFF REGISTRATION
    # -----------------------------

    def register_staff(
        self, staff_id, full_name, username, password
    ):
        staff_id = staff_id.strip().upper()
        full_name = full_name.strip()
        username = username.strip()

        if not all([staff_id, full_name, username, password]):
            return False, "Please complete all fields."

        if len(username) < 3 or any(c.isspace() for c in username):
            return False, "Username must be at least 3 characters with no spaces."

        if len(password) < 8:
            return False, "Password must be at least 8 characters."

        # For a classroom/demo deployment, allow self-registration when no
        # matching pre-authorized staff entry exists. If an administrator has
        # explicitly listed this staff ID, retain the claim/name checks.
        authorized_staff = self.storage.load(self.authorized_file)
        authorized_record = next(
            (
                staff for staff in authorized_staff
                if staff.get("staff_id", "").strip().upper() == staff_id
            ),
            None
        )

        if authorized_record is not None:
            if authorized_record.get("claimed", False):
                return False, "This staff ID has already been registered."
            if authorized_record.get("full_name", "").strip().casefold() != full_name.casefold():
                return False, "The name does not match the authorized record."

        users = self.storage.load(self.users_file)

        if any(
            user.get("username", "").casefold() == username.casefold()
            for user in users
        ):
            return False, "This username is already in use."

        if any(
            user.get("staff_id", "").upper() == staff_id
            for user in users
        ):
            return False, "An account already exists for this staff ID."

        salt, password_hash = self._hash_password(password)

        new_user = {
            "staff_id": staff_id,
            "full_name": full_name,
            "username": username,
            "salt": salt,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        users.append(new_user)
        self.storage.save(self.users_file, users)

        if authorized_record is not None:
            authorized_record["claimed"] = True
            self.storage.save(self.authorized_file, authorized_staff)

        return True, "Registration successful. You can now sign in."

    # -----------------------------
    # STAFF LOGIN
    # -----------------------------

    def login(self, username, password):
        username = username.strip()

        if not username or not password:
            return False, "Please enter your username and password."

        users = self.storage.load(self.users_file)

        user = next(
            (
                item for item in users
                if item.get("username", "").casefold()
                == username.casefold()
            ),
            None
        )

        if user is None:
            return False, "Invalid username or password."

        if not self._verify_password(
            password,
            user["salt"],
            user["password_hash"]
        ):
            return False, "Invalid username or password."

        logged_in_user = {
            "staff_id": user["staff_id"],
            "full_name": user["full_name"],
            "username": user["username"]
        }

        self.security.log_login_attempt(
            username=user["username"],
            staff_id=user["staff_id"],
            full_name=user["full_name"],
            success=True
        )
        return True, logged_in_user