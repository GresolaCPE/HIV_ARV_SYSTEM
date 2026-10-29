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
        """Copy existing project JSON files into the persistent user data folder once.

        Existing persistent files always win, so updating/re-extracting the project
        will never overwrite accounts or records already saved by the application.
        """
        if not LEGACY_DATA_DIR.exists():
            return
        for source in LEGACY_DATA_DIR.glob("*.json"):
            destination = DATA_DIR / source.name
            if not destination.exists():
                try:
                    shutil.copy2(source, destination)
                except OSError:
                    # If migration of one file fails, the app can still initialize;
                    # loading that file will create its default data file if needed.
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
