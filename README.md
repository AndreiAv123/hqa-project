# QA Engineer Home Assignment — Submission

## Contents

| File | Maps to |
|---|---|
| `test-plan.md` | Part A.1 — 6 prioritized test scenarios |
| `execution-results.md` | Part A.2 — execution results + bug reports (5 scenarios executed, 4 confirmed bugs plus 6 quick-fire issues) |
| `automation/` | Part B — automation framework + 2 automated tests (each parametrized over HOME/DRAW/AWAY) |
| `strategy-and-recommendations.md` | Part C |

## Automation — setup & run

```bash
cd automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Chrome + matching chromedriver must be installed and on PATH.
# (Selenium 4 can also auto-manage the driver via Selenium Manager - no extra install needed
#  as long as Chrome itself is present.)

# Run everything:
pytest

# Run just the fast API suite:
pytest -m api

# Run just the E2E suite, with the browser visible:
HEADED=1 pytest -m e2e

# Point at a different environment or fixed test user:
BASE_URL=https://qae-assignment-tau.vercel.app USER_ID=my-fixed-user pytest
```

## Project structure

```
automation/
  conftest.py                 # Shared by BOTH suites: base_url, user_id, api_client, reset_balance
  pages/
    bet_slip_page.py           # Page Object - all Selenium selectors live here
  tests/
    ui/
      conftest.py              # Selenium-only: `driver` fixture (depends on reset_balance directly)
      ui_helpers.py             # Plain functions: kickoff-date parsing, assert_equal/assert_close
      test_e2e_bet_placement.py     # E2E: critical happy-path bet placement, parametrized HOME/DRAW/AWAY
    api/
      conftest.py              # API-only: first_match / first_match_id (api_client/reset_balance live in root)
      api_helpers.py            # Plain functions: print_curl, place_bet, assert_bet_response_matches
      test_api_insufficient_balance.py  # API: stake-exceeds-balance business rule, parametrized HOME/DRAW/AWAY
  requirements.txt
  pytest.ini
```
