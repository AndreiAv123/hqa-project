"""
API-suite fixtures — everything requests/HTTP related lives here, scoped
only to tests under tests/api/. UI tests never pull this in.
"""
from datetime import date

import pytest
import requests


@pytest.fixture
def api_client(user_id, base_url):
    """
    A requests.Session pre-configured with the required x-user-id header
    (spec §5.1), plus small helpers so tests read as api_client.api_get(...).
    """
    session = requests.Session()
    session.headers.update({
        "x-user-id": user_id,
        "Content-Type": "application/json",
    })

    session.api_get = lambda path, **kw: session.request("GET", f"{base_url}{path}", **kw)
    session.api_post = lambda path, **kw: session.request("POST", f"{base_url}{path}", **kw)

    return session


@pytest.fixture
def reset_balance(api_client):
    """
    Resets the test user's balance to the configured initial value before a
    test that depends on a known starting balance (spec §5.3).
    """
    resp = api_client.api_post("/api/reset-balance")
    resp.raise_for_status()
    return resp.json()


@pytest.fixture
def get_balance(api_client):
    """
    Retrieves the current balance of the test user.
    """
    resp = api_client.api_get("/api/balance")
    resp.raise_for_status()
    return resp.json()


@pytest.fixture
def first_match(api_client):
    """
    A valid matchId to bet against, with a built-in contract check: the
    endpoint must never return a past match (spec §1 - upcoming/pre-match
    only). Any test using this fixture gets that check for free.
    """
    resp = api_client.api_get("/api/matches")
    resp.raise_for_status()
    matches = resp.json()
    assert matches, "No matches returned by /api/matches -- cannot run bet API tests"

    today = date.today()
    past_matches = [m for m in matches if date.fromisoformat(m["kickoffDate"]) < today]
    assert not past_matches, (
        f"Found {len(past_matches)} past match(es) returned by /api/matches -- the endpoint "
        f"should only return upcoming/pre-match events (spec §1): "
        f"{[m['id'] for m in past_matches]}"
    )

    return matches[0]
