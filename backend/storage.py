import json
import os
import shutil
import sys
from pathlib import Path


# Keep application data outside the extracted project directory so accounts
# and records survive app restarts, project updates, and re-extraction of the ZIP.
PROJECT_DIR = Path(__file__).resolve().parent.parent
LEGACY_DATA_DIR = PROJECT_DIR / "data"


def _get_user_data_dir():
    app_name = "HIV ARV System"
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / app_name


DATA_DIR = _get_user_data_dir()


class JSONStorage:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_data()

    
    def _migrate_legacy_data(self):
        """Copy existing JSON files into the persistent user data folder."""

        # Migrate JSON files from the original data folder.
        if LEGACY_DATA_DIR.exists():
            for source in LEGACY_DATA_DIR.glob("*.json"):
                destination = DATA_DIR / source.name

                if not destination.exists():
                    try:
                        shutil.copy2(source, destination)
                    except OSError:
                        pass

        # Migrate the original root inventory file, if present.
        legacy_inventory = PROJECT_DIR / "inventory_data.json"
        destination = DATA_DIR / "inventory_data.json"

        if legacy_inventory.exists() and not destination.exists():
            try:
                shutil.copy2(legacy_inventory, destination)
            except OSError:
                pass


    def load(self, filename):
        file_path = DATA_DIR / filename
        if not file_path.exists():
            self.save(filename, [])
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{filename} contains invalid JSON data.") from exc

    def save(self, filename, data):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        file_path = DATA_DIR / filename
        # Write to a temporary file first to reduce the risk of partial/corrupt data.
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        temp_path.replace(file_path)
