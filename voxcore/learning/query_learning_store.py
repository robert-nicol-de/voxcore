import json
import os
from datetime import datetime

STORE_PATH = "voxcore_learning.json"


def _load_store():
    if not os.path.exists(STORE_PATH):
        return []

    with open(STORE_PATH, "r") as f:
        return json.load(f)


def _save_store(data):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def save_learning_entry(entry: dict):
    store = _load_store()

    entry["timestamp"] = datetime.utcnow().isoformat()

    store.append(entry)

    # keep last 1000 entries (prevent bloat)
    store = store[-1000:]

    _save_store(store)
