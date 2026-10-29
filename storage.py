import json
from pathlib import Path


# Locate the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Folder where JSON files will be stored
DATA_DIR = PROJECT_DIR / "data"


class JSONStorage:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load(self, filename):
        file_path = DATA_DIR / filename

        # Create an empty JSON list if the file does not exist
        if not file_path.exists():
            self.save(filename, [])
            return []

        # Read the existing JSON file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except json.JSONDecodeError:
            raise ValueError(
                f"{filename} contains invalid JSON data."
            )

    def save(self, filename, data):
        file_path = DATA_DIR / filename

        # Save data in a readable JSON format
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
