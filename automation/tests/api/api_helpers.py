"""
Plain utility functions for API tests — not fixtures, so they live here
rather than in conftest.py. Import explicitly where needed:

    from helpers import print_curl, place_bet, assert_bet_response_matches
"""
import json
import random

import pytest




def print_curl(method, url, headers, body=None):
    """
    Print a request as an equivalent curl command. pytest only shows
    captured stdout for tests that FAIL, so on a red run the terminal
    output already contains the exact curl to reproduce the failing
    request by hand.
    """
    parts = [f"curl -X {method} '{url}'"]
    for key, value in headers.items():
        parts.append(f"-H '{key}: {value}'")
    if body is not None:
        parts.append(f"-d '{json.dumps(body)}'")
    print("\n" + " ".join(parts))


def place_bet(api_client, base_url, match, stake, selection=None):
    """
    selection=None (default) picks a random outcome from HOME/DRAW/AWAY each
    call - useful for tests that don't care which outcome is bet on and want
    coverage spread across all three over repeated runs. Pass an explicit
    value ("HOME"/"DRAW"/"AWAY") when a test specifically needs that outcome.
    """
    match_id = match["id"]
    body = {"matchId": match_id, "selection": selection, "stake": stake}
    print_curl("POST", f"{base_url}/api/place-bet", api_client.headers, body)
    return api_client.api_post("/api/place-bet", json=body)

def assert_bet_response_matches(actual: dict, *, match_id, selection, stake, odds, balance_after_bet, currency):
    """
    Build the response we EXPECT for a successful bet placement (spec §5.3
    200 response) and diff it field-by-field against what the API actually
    returned, rather than eyeballing the raw JSON. Numeric fields use a
    small tolerance for float rounding; everything else must match exactly.
    """
    remaining_balance = balance_after_bet["balance"] - stake
    if remaining_balance < 0:
        pytest.fail(
            f"Test setup error: balance after bet would be negative ({remaining_balance:.2f})"
        )
    expected = {
        "matchId": match_id,
        "selection": selection,
        "stake": stake,
        "odds": odds,
        "payout": pytest.approx(round(stake * odds, 2), abs=0.01),
        "balance": pytest.approx(round(remaining_balance, 2), abs=0.01),
        "currency": currency,
    }

    assert actual.get("message"), "Response is missing a confirmation 'message' (spec §5.3)"

    mismatches = [
        f"  {field}: expected {expected_value!r}, got {actual.get(field)!r}"
        for field, expected_value in expected.items()
        if actual.get(field) != expected_value
    ]
    # print(mismatches)
    assert not mismatches, "Bet response did not match expected values:\n" + "\n".join(mismatches)