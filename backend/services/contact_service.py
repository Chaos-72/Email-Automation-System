import pandas as pd
from typing import Optional
from difflib import get_close_matches

CONTACTS = {}  # in-memory store


def load_contacts(file_path: str):
    """Load contacts from a CSV or Excel file."""
    global CONTACTS
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Expected columns: name, email
    CONTACTS = {
        str(row["name"]).strip().lower(): str(row["email"]).strip()
        for _, row in df.iterrows()
        if pd.notna(row["name"]) and pd.notna(row["email"])
    }
    return {"ok": True, "count": len(CONTACTS)}


def find_email_by_name(name: str) -> Optional[str]:
    """Find email by exact or fuzzy match."""
    if not CONTACTS:
        return None
    key = name.strip().lower()
    if key in CONTACTS:
        return CONTACTS[key]

    # Fuzzy match
    matches = get_close_matches(key, CONTACTS.keys(), n=1, cutoff=0.7)
    if matches:
        return CONTACTS[matches[0]]
    return None
