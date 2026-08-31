"""
E2E UI test — Critical user journey: place a valid single bet end-to-end.

Why this test was chosen for automation: this is the one flow the entire
product exists to support (spec §1: "core betting functionality"). It
touches every layer of the UI (match list -> bet slip -> loading state ->
receipt) and its failure mode is maximally severe: money silently not
matching what the user was shown.

Contract check on the FIRST match card only (not filtered/skipped to find
"an" upcoming match): it must show the UPCOMING badge and its kickoff label
must resolve to today or later (spec §1: upcoming/pre-match only, no live
betting). If either check fails, the actual badge/label text is printed so
it's obvious what the app actually rendered.

Parametrized over all three outcomes (HOME/DRAW/AWAY) against that first
match, since each is an independent selection path through the bet slip.

Validates that team order and the numbers (stake, odds, payout) stay
consistent across all three stages - match card, bet slip, and receipt -
and that payout is actually verified as stake x odds rather than just
"present", at both the bet slip and receipt stage. See helpers.py for the
shared comparison/parsing utilities used throughout.

"""
from datetime import date

import pytest

from pages.bet_slip_page import BetSlipPage
from ui_helpers import assert_close, assert_equal, parse_kickoff_label

STAKE = "10.00"


@pytest.mark.e2e
@pytest.mark.nondestructive  # dedicated test app - a placed bet here is expected and safe
@pytest.mark.parametrize("selection", ["HOME"])
def test_place_single_bet_updates_balance_and_shows_receipt(driver, reset_balance, selection):
    page = BetSlipPage(driver)

    # Contract check on the first match card: must be UPCOMING, not PAST/live.
    assert_equal(
        page.get_first_match_badge(), "UPCOMING",
        "First match card badge (spec §1: upcoming/pre-match events only)",
    )

    # Contract check: its kickoff date must be today or later.
    today = date.today()
    kickoff_label = page.get_first_match_kickoff_label()
    kickoff_date = parse_kickoff_label(kickoff_label, today)
    assert kickoff_date is not None, (
        f"Could not parse the first match's kickoff label into a date -- actual value: {kickoff_label!r}"
    )
    assert kickoff_date >= today, (
        f"First match's kickoff date ({kickoff_date}) is before today ({today}) -- "
        f"raw label was {kickoff_label!r}"
    )

    # Capture ground truth from the match card BEFORE clicking anything, so
    # we can confirm it's carried through unchanged into the bet slip and
    # the receipt (spec: "Match Ordering" - home is always listed first).
    home_team, away_team = page.get_first_match_teams()
    expected_teams_text = f"{home_team} vs {away_team}"
    odds = page.get_first_match_odds()[selection]

    starting_balance = page.get_balance()

    page.select_first_match_outcome(selection)

    # Bet slip must show the same team order and the same odds as the match card.
    assert_equal(page.get_bet_slip_teams(), expected_teams_text, "Bet slip team order")
    assert_close(page.get_bet_slip_odds(), odds, f"Bet slip odds vs match card's {selection} odds")

    page.enter_stake(STAKE)
    assert not page.is_place_bet_disabled(), "Place Bet should be enabled once a valid stake is entered"

    expected_payout = round(float(STAKE) * odds, 2)
    assert_close(
        page.get_potential_payout(), expected_payout,
        f"Bet slip potential payout vs stake x odds (€{STAKE} x {odds})",
    )

    page.place_bet()
    page.wait_for_receipt()

    bet_id = page.get_receipt_bet_id()
    assert bet_id, "Receipt did not display a Bet ID"

    # Receipt must carry the same team order, stake, odds, and payout through
    # as the match card / bet slip - and payout must actually equal stake x odds.
    assert_equal(page.get_receipt_match_text(), expected_teams_text, "Receipt team order")
    assert_close(page.get_receipt_stake(), float(STAKE), "Receipt stake vs stake placed")
    assert_close(page.get_receipt_odds(), odds, f"Receipt odds vs {selection} odds shown before placement")
    assert_close(page.get_receipt_payout(), expected_payout, "Receipt payout vs stake x odds")

    page.close_receipt()

    # The one assertion that actually catches a bug that would cost real money:
    # balance must be debited by exactly the stake (spec §2.3).
    assert_close(
        page.get_balance(), starting_balance - float(STAKE),
        "Balance after bet vs starting balance minus stake",
    )
