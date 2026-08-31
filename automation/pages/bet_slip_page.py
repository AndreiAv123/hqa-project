"""
Page Object for the Single Bet Placement flow.

All selectors below were taken directly from real captured DOM snapshots -
the match list, the bet slip, and (now) the success receipt modal.
"""
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _parse_euro(text: str) -> float:
    """'€1.00' -> 1.00"""
    return float(re.sub(r"[^\d.]", "", text))


def _parse_number(text: str) -> float:
    """'Odds: 2.45' -> 2.45, '2.45' -> 2.45"""
    match = re.search(r"[\d.]+", text)
    return float(match.group())


class BetSlipPage:
    TIMEOUT = 10

    # Header / global
    HEADER_BALANCE = (By.ID, "header-balance")

    # First match card only. find_element()/find_elements() return elements
    # in document order, so scoping to ".matchCard ..." without an index
    # naturally targets the first card - no "upcoming" filtering/skipping.
    FIRST_MATCH_BADGE = (By.CSS_SELECTOR, ".matchCard .badge")
    FIRST_MATCH_KICKOFF_LABEL = (By.CSS_SELECTOR, ".matchCard .matchMeta span:last-child")
    FIRST_MATCH_TEAM_NAMES = (By.CSS_SELECTOR, ".matchCard .teamName")  # [0]=home, [1]=away
    FIRST_MATCH_ODDS_BUTTONS = (By.CSS_SELECTOR, ".matchCard .oddsButton")
    FIRST_MATCH_ODDS_VALUES = (By.CSS_SELECTOR, ".matchCard .oddsButtonValue")  # [0]=home,[1]=draw,[2]=away
    OUTCOME_INDEX = {"HOME": 0, "DRAW": 1, "AWAY": 2}

    # Bet slip
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET_BTN = (By.ID, "bet-slip-place-bet")
    REMOVE_ALL_BTN = (By.ID, "bet-slip-remove-all")
    SELECTION_REMOVE_BTN = (By.ID, "bet-slip-selection-remove")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    SELECTION_TEAMS_TEXT = (By.CLASS_NAME, "betSelectionTeams")   # e.g. "Chelsea vs Manchester Utd"
    SELECTION_ODDS_TEXT = (By.CLASS_NAME, "betSelectionOdds")     # e.g. "Odds: 2.45"

    # Success receipt modal (spec §2.4) - confirmed against real DOM.
    RECEIPT_BET_ID = (By.ID, "modal-success-bet-id")
    RECEIPT_MATCH = (By.ID, "modal-success-match")           # e.g. "Chelsea vs Manchester Utd"
    RECEIPT_STAKE = (By.ID, "modal-success-stake")            # e.g. "€1.00"
    RECEIPT_ODDS = (By.ID, "modal-success-odds")              # e.g. "2.45"
    RECEIPT_PAYOUT = (By.ID, "modal-success-payout")          # e.g. "€2.00"
    RECEIPT_PLACED_AT = (By.ID, "modal-success-placed-at")
    RECEIPT_CLOSE_BTN = (By.ID, "modal-success-close")


    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    # --- actions -----------------------------------------------------------
    def select_first_match_outcome(self, outcome: str):
        """outcome: 'HOME' | 'DRAW' | 'AWAY' - clicks that odds button on the FIRST match card."""
        index = self.OUTCOME_INDEX[outcome]
        buttons = self.wait.until(EC.presence_of_all_elements_located(self.FIRST_MATCH_ODDS_BUTTONS))
        buttons[index].click()
        return self

    def enter_stake(self, amount: str):
        field = self.wait.until(EC.visibility_of_element_located(self.STAKE_INPUT))
        field.clear()
        field.send_keys(amount)
        return self

    def place_bet(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.PLACE_BET_BTN))
        btn.click()
        return self

    def wait_for_receipt(self):
        self.wait.until(EC.visibility_of_element_located(self.RECEIPT_BET_ID))
        return self

    def close_receipt(self):
        self.driver.find_element(*self.RECEIPT_CLOSE_BTN).click()
        return self

    # --- reads: match list ---------------------------------------------------
    def get_first_match_badge(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.FIRST_MATCH_BADGE)).text.strip()

    def get_first_match_kickoff_label(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.FIRST_MATCH_KICKOFF_LABEL)).text.strip()

    def get_first_match_teams(self) -> tuple[str, str]:
        """Returns (home_team, away_team) - home is always listed first (spec: Match Ordering)."""
        names = self.wait.until(EC.presence_of_all_elements_located(self.FIRST_MATCH_TEAM_NAMES))
        return names[0].text.strip(), names[1].text.strip()

    def get_first_match_odds(self) -> dict:
        """Returns {'HOME': float, 'DRAW': float, 'AWAY': float} for the first match card."""
        values = self.wait.until(EC.presence_of_all_elements_located(self.FIRST_MATCH_ODDS_VALUES))
        return {
            outcome: _parse_number(values[index].text)
            for outcome, index in self.OUTCOME_INDEX.items()
        }

    # --- reads: header / bet slip --------------------------------------------
    def get_balance(self) -> float:
        text = self.wait.until(EC.visibility_of_element_located(self.HEADER_BALANCE)).text
        return _parse_euro(text)

    def get_bet_slip_teams(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.SELECTION_TEAMS_TEXT)).text.strip()

    def get_bet_slip_odds(self) -> float:
        text = self.wait.until(EC.visibility_of_element_located(self.SELECTION_ODDS_TEXT)).text
        return _parse_number(text)

    def get_total_stake_text(self) -> str:
        return self.driver.find_element(*self.TOTAL_STAKE).text

    def get_potential_payout(self) -> float:
        text = self.wait.until(EC.visibility_of_element_located(self.POTENTIAL_PAYOUT)).text
        return _parse_euro(text)

    def is_place_bet_disabled(self) -> bool:
        btn = self.driver.find_element(*self.PLACE_BET_BTN)
        return btn.get_attribute("disabled") is not None

    # --- reads: receipt ------------------------------------------------------
    def get_receipt_bet_id(self) -> str:
        return self.driver.find_element(*self.RECEIPT_BET_ID).text.strip()

    def get_receipt_match_text(self) -> str:
        return self.driver.find_element(*self.RECEIPT_MATCH).text.strip()

    def get_receipt_stake(self) -> float:
        return _parse_euro(self.driver.find_element(*self.RECEIPT_STAKE).text)

    def get_receipt_odds(self) -> float:
        return _parse_number(self.driver.find_element(*self.RECEIPT_ODDS).text)

    def get_receipt_payout(self) -> float:
        return _parse_euro(self.driver.find_element(*self.RECEIPT_PAYOUT).text)