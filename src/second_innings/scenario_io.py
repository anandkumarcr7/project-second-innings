"""
Scenario persistence for Project Second Innings.

Saves and loads RetirementScenario objects as human-readable JSON files
in the Git-ignored data/private/ directory (DR-001, DR-002).
"""

from __future__ import annotations

import dataclasses
import json
from datetime import date
from pathlib import Path

from .models import MODEL_VERSION, RetirementScenario

# Metadata keys added to the JSON file but not part of the dataclass.
_METADATA_KEYS = {"saved_date", "last_modified_date"}


def save_scenario(scenario: RetirementScenario, path: Path) -> None:
    """
    Serialise *scenario* to a JSON file at *path*.

    The parent directory is created if it does not exist.
    Saved and last-modified dates are written as ISO-8601 strings.
    """
    data = dataclasses.asdict(scenario)
    today = date.today().isoformat()
    # Preserve existing saved_date if the file already exists.
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            data["saved_date"] = existing.get("saved_date", today)
        except (json.JSONDecodeError, OSError):
            data["saved_date"] = today
    else:
        data["saved_date"] = today
    data["last_modified_date"] = today

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def load_scenario(path: Path) -> RetirementScenario:
    """
    Load a :class:`RetirementScenario` from a JSON file.

    Raises
    ------
    ValueError
        If the file cannot be parsed or required fields are missing / invalid.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed scenario file '{path}': {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read scenario file '{path}': {exc}") from exc

    # Strip metadata keys that are not part of the dataclass
    for key in _METADATA_KEYS:
        data.pop(key, None)

    try:
        return RetirementScenario(**data)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid scenario data in '{path}': {exc}") from exc
