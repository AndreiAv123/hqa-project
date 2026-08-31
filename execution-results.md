# Execution Results — Top Priority Scenarios

## Execution Log

| Scenario | Result | Notes |
|----------|--------|-------|
| TC-01 — Happy path bet placement | **FAILED** | Receipt is missing the selected outcome, shows teams in reverse order vs. the match display, and the potential payout is calculated incorrectly. See BUG-03. |
| TC-04 — Insufficient balance rejected | **FAILED** | The API accepts a stake that exceeds the available balance and drives the balance negative. See BUG-04. |
| TC-06 — Only upcoming matches displayed | **FAILED** | Finished/past matches are returned by both the UI and the API, and bets can be placed on them. See BUG-02. |

## Exploratory Notes

Additional exploratory checks performed, beyond the prioritized scenarios above — see Quick-Fire Issues below for what turned up:
- Date filter, odds filter, balance auto-refresh, profile icon, reset-balance response accuracy, and bet slip selection labeling.

---

## Bug Reports

### BUG-01 — Conflicting minimum stake value in the specification (§3 vs §4.1)

- **Severity:** High
- **Found via:** Specification review (not live execution)
- **Reproduction Steps:**
  1. Open the Feature Specification document.
  2. Compare §3 "Business Rules" table — "Stake min (per bet): **€1.00**" — against §4.1 "Stake Validation" table — "Stake Minimum: **€1.01** (positive values)".
- **Expected vs Actual:** A single feature spec should define one unambiguous minimum stake. Instead it defines two different values (€1.00 and €1.01), and §4.4's UI copy ("Minimum stake is €1.00") only matches one of them.
- **Business Impact:** Whichever value the engineering team implemented, it silently contradicts the other stated rule and the UI copy. This risks: (a) a boundary value like exactly €1.00 being wrongly accepted or wrongly rejected depending on which table was implemented against, and (b) test suites written against one rule failing against a build written to the other. This is exactly the kind of ambiguity that produces flaky "is this a bug or not" boundary defects in production.
- **Evidence:** See `Feature_Specification.pdf`, §3 Business Rules table vs §4.1 Stake Validation table.
- **Recommended Fix:** Product/spec owner confirms the correct value; §3, §4.1, and §4.4 UI copy are aligned to a single number; TC-02's exact-boundary case (`1.00`) is added as a regression test once resolved.

### BUG-02 — Finished/past games are available for betting via UI and API

- **Severity:** Critical
- **Reproduction Steps:**
  1. Open the UI and navigate to the available games/events.
  2. Observe that games which have already finished or whose scheduled start time has passed are still displayed.
  3. Attempt to place a bet on one of the finished/past games.
  4. Request the available games through the API.
  5. Observe that the API also returns finished/past games.
  6. Attempt to place a bet on one of the returned finished/past games.
- **Expected vs Actual:**
  - **Expected:** Finished or past games should not be returned by the API or displayed in the UI as available betting options. Bets should not be accepted for events that have already finished or started.
  - **Actual:** Both the UI and API return finished/past games, and bets can be placed on these games.
- **Business Impact:** Users can place bets on events that have already finished, potentially resulting in invalid bets, incorrect settlements, financial loss, and significant trust/compliance issues.
- **Evidence:** Screenshots and API responses showing finished/past games being returned and bets successfully placed on them.
- **Covered by automation:** `test_e2e_bet_placement.py` and `test_api_insufficient_balance.py` both assert the first match/first element returned is `UPCOMING`, failing loudly with the actual badge/date if a past match ever surfaces there again.

### BUG-03 — Incorrect/missing information on successful bet receipt

- **Severity:** Critical
- **Reproduction Steps:**
  1. Open the UI and select an available game.
  2. Place a bet with a known stake and odds.
  3. Successfully complete the bet.
  4. Success receipt appears.
  5. Observe the bet details displayed on the receipt.
- **Expected vs Actual:**
  - **Expected:**
    - The receipt should display the selected betting selection from the Bet Slip.
    - Teams should be displayed in the same order as shown before placing the bet.
    - As per §2.4 Success Receipt (Feature Specification), all approved fields should appear.
    - Potential payout should be calculated as `Stake × Odds`. For example, a €1 stake at odds of 2.45 should result in a potential payout of **€2.45**.
  - **Actual:**
    - The selected betting selection is missing from the success receipt.
    - The teams are displayed in the reverse order compared to the original match display.
    - Match details are only displayed as "Match" (no home/away distinction).
    - The potential payout is calculated incorrectly. For example, a €1 stake at odds of 2.45 displays a potential payout of **€2.00** instead of **€2.45**.
- **Business Impact:** Incorrect or missing information on the bet receipt can confuse users and may lead to incorrect understanding of the placed bet and its potential return. The incorrect payout calculation is particularly critical, since it displays misleading financial information to the user.
- **Evidence:** Screenshot of the receipt alongside the Bet Slip for team-order and payout comparison.
- **Covered by automation:** `test_e2e_bet_placement.py` independently computes `stake × odds` and asserts it against both the Bet Slip's displayed payout and the receipt's displayed payout, and asserts the receipt's team-order text matches what the match card showed before placement — this is precisely the test that should have caught this bug, and will catch any regression of it going forward.

### BUG-04 — Insufficient balance protection and incorrect currency in `/api/place-bet`

- **Severity:** Critical
- **Reproduction Steps:**
  1. Ensure the account has a balance of €30.
  2. Send a `POST` request to `/api/place-bet` with a stake of €60.
  3. Observe the API response and account balance.
  4. Check the currency displayed in the API response.
- **Expected vs Actual:**
  - **Expected:**
    - The API should reject the bet when the stake exceeds the available balance.
    - The balance should never become negative.
    - The API response should use **EUR (€)** consistently with the rest of the application.
  - **Actual:**
    - The API accepts a €60 bet with only €30 available.
    - The account balance becomes **-€30**.
    - The API response displays the currency as **USD ($)**, while the rest of the application uses **EUR (€)**.
- **Business Impact:** The API does not enforce the same balance validation as the UI, allowing direct API requests to place bets exceeding the available balance and resulting in negative account balances. While the UI prevents this scenario, the missing server-side validation creates a backend integrity and financial risk if the API endpoint is accessed directly or exploited.
- **Evidence:** Screenshot and curl reproduction of the API call.
- **Covered by automation:** `test_api_insufficient_balance.py` places a valid bet then attempts a second, still-in-range stake that exceeds what's left, asserting a `422` and an unchanged balance. Every request it makes is logged as an equivalent curl command, so a failing run already prints the exact repro curl in the terminal output.

## Quick-Fire Issues

1. **Date Filter Allows Selecting Past Dates** — The date filter allows dates from the past to be selected.
2. **Odds Filter Issues** — The odds filter does not function correctly. The maximum value can be set lower than the minimum, the minimum value indicator is misaligned with the range line, and the requirements specify a minimum odds value of 1.01 while the filter allows values starting from 1.00.
3. **Balance Not Updated Automatically** — The displayed balance is only updated after refreshing the page.
4. **Profile Icon Not Functional** — The profile icon does not perform any action when clicked.
5. **Reset Balance API Returns Incorrect Value** — The reset-balance API response body reports a balance of €125.50, while the actual balance afterward is €120.00. (Note: the automation suite's `STARTING_BALANCE = 120.00` constant was set from the real observed value, not the API's self-reported one — worth keeping in mind if this gets fixed and the reported value changes.)
6. **Bet Slip Selection Label Mismatch** — The bet slip displays "Match Winner" when "Draw" is selected. Expected label/selection behavior isn't explicitly defined in the spec, so this may need a product decision rather than a pure bug fix.