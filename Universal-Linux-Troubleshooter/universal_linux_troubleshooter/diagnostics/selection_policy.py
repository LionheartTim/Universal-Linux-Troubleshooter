"""Decide when manual checkboxes should be cleared, without touching saved results."""
from __future__ import annotations


def forget_checks_on_area_change(selections: dict[str, set[str]], previous: str | None, new: str) -> bool:
    """Moving to another area starts a fresh selection; initial view does not clear."""
    if previous is None or previous == new:
        return False
    for checks in selections.values():
        checks.clear()
    return True
