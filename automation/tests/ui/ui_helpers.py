"""
Plain utility functions for UI tests — not fixtures, so they live here
rather than in conftest.py. Import explicitly where needed:

    from helpers import parse_kickoff_label, assert_close, assert_equal
"""
from datetime import date, datetime, timedelta

import pytest

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_kickoff_label(label: str, today: date):

    label = label.strip()

    # Shape 1: "Sat, Sep 19" - always this year, no rollover guessing.
    try:
        return datetime.strptime(f"{label} {today.year}", "%a, %b %d %Y").date()
    except ValueError:
        pass

    # Shape 2: bare weekday name -> nearest occurrence on/after today
    if label in WEEKDAYS:
        target_idx = WEEKDAYS.index(label)
        days_ahead = (target_idx - today.weekday()) % 7
        return today + timedelta(days=days_ahead)

    return None


def assert_equal(actual, expected, label: str):
    """Assert exact equality with a consistent, informative failure message."""
    assert actual == expected, f"{label}: expected {expected!r}, got {actual!r}"


def assert_close(actual: float, expected: float, label: str, abs_tol: float = 0.01):
    """Assert two numeric values match within tolerance, with a consistent, informative message."""
    assert actual == pytest.approx(expected, abs=abs_tol), (
        f"{label}: expected {expected}, got {actual}"
    )