import json
import os
from typing import Optional

from app.config import get_settings

settings = get_settings()

_cached_data = None


def load_opening_hours() -> dict:
    """Load opening hours data from JSON file."""
    global _cached_data

    if _cached_data is not None:
        return _cached_data

    filepath = settings.opening_hours_path
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        _cached_data = json.load(f)

    return _cached_data


def get_opening_hours(department: Optional[str] = None) -> str:
    """
    Get opening hours for city departments.

    Args:
        department: Optional department name to filter by

    Returns:
        Formatted string with opening hours information
    """
    data = load_opening_hours()

    if not data:
        return "Die Öffnungszeiten sind derzeit nicht verfügbar."

    # Data format: {"Einwohnermeldeamt": {"Montag": "08:00-12:00", ...}, ...}

    # If no department specified, return list of available departments
    if not department:
        dept_names = list(data.keys())[:5]
        return f"Verfügbare Abteilungen: {', '.join(dept_names)}. Fragen Sie nach einer bestimmten Abteilung für Details."

    # Search for matching department (case-insensitive, partial match)
    department_lower = department.lower()
    matches = []

    for dept_name, hours in data.items():
        if department_lower in dept_name.lower():
            matches.append((dept_name, hours))

    if not matches:
        # Try fuzzy matching
        for dept_name, hours in data.items():
            if any(word in dept_name.lower() for word in department_lower.split()):
                matches.append((dept_name, hours))

    if not matches:
        dept_names = list(data.keys())
        return f"Keine Abteilung mit dem Namen '{department}' gefunden. Verfügbare Abteilungen: {', '.join(dept_names)}"

    # Format opening hours for matched departments
    results = []
    for dept_name, hours in matches[:3]:  # Limit to 3 matches
        hours_str = []
        for day, time in hours.items():
            hours_str.append(f"{day}: {time}")

        result = f"{dept_name}: " + ", ".join(hours_str)
        results.append(result)

    return "\n".join(results)
