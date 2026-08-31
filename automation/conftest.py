"""
Root-level fixtures — DATA ONLY.

This file intentionally holds nothing that spins up a browser or an HTTP
session. Those live in tests/ui/conftest.py and tests/api/conftest.py
respectively, scoped only to the suite that needs them. This file is just
the environment/config values both suites share.
"""
import os
import uuid

import pytest

BASE_URL = "https://qae-assignment-tau.vercel.app/"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def user_id():
    """
    A fresh, unique user-id per test session so tests don't collide with each
    other's balance/bet state when run repeatedly or in parallel.
    Override with USER_ID env var to pin a fixed test user.
    """
    return os.getenv("USER_ID") or str(uuid.uuid4())
