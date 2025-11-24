
import csv
from typing import List, Dict
from exceptions import StorageError

def save_dicts_to_csv(path: str, fieldnames: List[str], rows: List[Dict]):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
    except Exception as e:
        raise StorageError(f"Failed to save CSV {path}: {e}")

def load_dicts_from_csv(path: str):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []
    except Exception as e:
        raise StorageError(f"Failed to load CSV {path}: {e}")
