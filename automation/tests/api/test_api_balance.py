"""
API test — business rule check: a stake that exceeds the user's current
balance must be rejected, even though it's within the normal €1-€100 range
(spec §4.1: "Stake must not exceed available balance").

Reset first so we start from a known balance (€120.00), place one valid bet
that eats most of it, then attempt a second bet that's still within the
normal €1-€100 stake range but exceeds what's left -- that one must be
rejected and must not touch the balance.

"""
import random

import pytest

from api_helpers import place_bet, assert_bet_response_matches

FIRST_STAKE = 100.00  # leaves 20.00
SECOND_STAKE = 50.00  # more than the 20.00 left -> should be rejected
SELECTIONS = ("HOME", "DRAW", "AWAY")


@pytest.mark.api
@pytest.mark.nondestructive  # dedicated test app - resetting/placing bets here is expected and safe
def test_place_bet_rejects_stake_above_available_balance(api_client, first_match, reset_balance, base_url, get_balance):
    selection = random.choice(SELECTIONS)
    # Bet 1: valid, well within balance and the €1-€100 stake range.
    resp = place_bet(api_client, base_url, match=first_match, stake=FIRST_STAKE, selection=selection)
    assert_bet_response_matches(resp.json(), match_id=first_match["id"], selection=selection, stake=FIRST_STAKE,
                                odds=first_match["odds"][selection.lower()], balance_after_bet=get_balance,
                                currency="USD")
    assert resp.status_code == 200, (
        f"Expected the first bet (€{FIRST_STAKE:.2f}) to succeed, got {resp.status_code}: {resp.text}"
    )

    # Bet 2: still within the valid stake range, but exceeds what's left -> must be rejected.
    resp = place_bet(api_client, base_url, match=first_match, stake=SECOND_STAKE, selection=selection)
    assert_bet_response_matches(resp.json(), match_id=first_match["id"], selection=selection, stake=SECOND_STAKE,
                                odds=first_match["odds"][selection.lower()], balance_after_bet=get_balance,
                                currency="USD")
    assert resp.status_code == 422, (
        f"Expected 422 placing €{SECOND_STAKE:.2f} against a remaining balance of €{get_balance['balance'] - FIRST_STAKE}, "
        f"got status code: {resp.status_code}: {resp.text}"
    )
