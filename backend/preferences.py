import json
import os

PREFS_FILE = "backend/user_preferences.json"

DEFAULT_PREFS = {
    "categories": ["technology", "business"],
    "language": "en",
    "reading_style": "short"
}

def load_preferences() -> dict:
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_PREFS.copy()

def save_preferences(prefs: dict):
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2)