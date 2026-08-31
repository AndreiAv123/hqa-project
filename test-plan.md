# Test Plan — Single Bet Placement

**Application:** https://qae-assignment-tau.vercel.app/?user-id=<your-user-id>
**Feature under test:** Single Bet Placement (Feature Specification v1)
**Author:** QA Engineer
**Scope note:** Scenarios are derived directly from the Feature Specification (sections 2–5) and Domain Context doc. Priority reflects business/financial risk (money movement, data integrity) over cosmetic issues.

---

## TC-01 — Place a valid single bet end-to-end (Happy Path)

- **Priority:** Critical
- **Risk Rationale:** This is the core revenue-generating flow. If it breaks, the product has no function. Any inconsistency between odds shown, stake entered, and payout on the receipt directly affects money and user trust.
- **Steps:**
  1. Load the app with a valid `user-id`.
  2. Note starting balance (header/bet slip).
  3. Select any upcoming match, click one odds button (e.g. `1`).
  4. In the bet slip, confirm selection, odds, and computed payout preview are visible.
  5. Enter a valid stake, e.g. `10.00`.
  6. Click **Place Bet**.
  7. Observe loading state (`Placing...`).
  8. Wait for resolution.
- **Expected Result:**
  - Button shows `Placing...` then resolves to success.
  - Balance decreases by exactly the stake amount.
  - Success receipt modal shows Bet ID, correct match (home listed first), selection, stake, odds at placement, payout = stake × odds, and a timestamp.
  - Closing the receipt returns to the main flow with no active selection in the bet slip.

---

## TC-02 — Stake below minimum is rejected

- **Priority:** Critical
- **Risk Rationale:** Stake boundaries are a hard business rule (§3) enforced at both UI and API layers. Under-enforcement risks invalid low-value bets slipping through; over-strict enforcement blocks legitimate low stakes. **Note:** the spec itself is inconsistent here — §3 "Business Rules" states minimum stake is **€1.00**, while §4.1 "Validation Rules" states minimum is **€1.01**. This ambiguity must be resolved and is called out separately as a defect/clarification (see Bug Reports).
- **Steps:**
  1. Select a match and odds.
  2. Enter stake `0.50`.
  3. Attempt to place bet (and/or observe inline validation before submit).
  4. Also test the boundary value `1.00` to see which spec rule the app actually implements.
- **Expected Result:**
  - Placement is blocked in the UI with the message "Minimum stake is €1.00" (per §4.4 copy).
  - If submitted anyway (e.g. via API), server returns `422` and rejects.
  - Balance is unchanged.

---

## TC-03 — Stake above maximum is rejected

- **Priority:** Critical
- **Risk Rationale:** Symmetric boundary to TC-02, protects against unbounded liability on a single bet — a direct financial/business risk.
- **Steps:**
  1. Select a match and odds.
  2. Enter stake `100.01`.
  3. Attempt to place bet.
  4. Also test boundary `100.00` (must be accepted) and `150` (must be rejected).
- **Expected Result:**
  - `100.01` and `150` are blocked/rejected with "Maximum stake is €100.00".
  - `100.00` (exact max) is accepted.
  - Balance only changes for the accepted case.

---

## TC-04 — Stake exceeding available balance is rejected

- **Priority:** High
- **Risk Rationale:** Distinct failure mode from the fixed min/max rule — depends on dynamic user state. If under-validated, a user could go into negative balance, which is a serious financial/data-integrity defect.
- **Steps:**
  1. Note current balance (e.g. €125.50 on a fresh reset).
  2. Select a match/odds, enter a stake greater than the balance but within the €1–€100 range (e.g. if balance is €5, enter €10).
  3. Attempt to place bet.
- **Expected Result:**
  - UI shows "Insufficient balance" and blocks placement.
  - API returns rejection (422) if called directly with an over-balance stake.
  - Balance is not deducted.

---

## TC-05 — Selecting new odds replaces the previous selection

- **Priority:** High
- **Risk Rationale:** §2.1/2.2 explicitly require single-selection behavior ("only one active selection at a time"). A failure here (e.g. stale odds staying in the bet slip, or multiple selections accumulating) could cause a user to place a bet on the wrong outcome or at stale odds — a direct financial-accuracy risk.
- **Steps:**
  1. Click odds `1` on Match A. Confirm bet slip shows Match A / Home selection.
  2. Without removing it, click odds `X` on Match A (or odds on Match B).
  3. Observe bet slip.
- **Expected Result:**
  - Bet slip shows only the newest selection; the prior one is fully replaced, not appended.
  - Stake field behavior on replacement is consistent (spec doesn't state explicitly whether stake is preserved or cleared — verify actual behavior and flag if unexpected, e.g. stale stake attached to a new selection).

---

## TC-06 — Only upcoming/future matches are displayed for betting

- **Priority:** Critical
- **Risk Rationale:** Spec §1 explicitly scopes this feature to "Upcoming/Pre-match events only (no live betting)," and lists live betting as out of scope. If a live or past match appears in the match list, a user could place a bet with foreknowledge of a partial or final result — a direct integrity and financial-risk issue, not just a display glitch.
- **Steps:**
  1. Load the match list in the UI.
  2. For each match shown, check its kickoff date/time label against the current date/time.
  3. Confirm no match with a kickoff time in the past, and no match currently in progress, appears in the list.
- **Expected Result:**
  - Every match displayed has a kickoff date/time that is about to start or in the future — no live or past matches are shown anywhere in the match list.

---

## Coverage Summary

| ID | Area | Priority | Result |
|----|------|----------|--------|
| TC-01 | Happy path E2E | Critical | **FAILED** — see execution-results.md BUG-03 |
| TC-02 | Stake min boundary / negative | Critical | Pending — spec ambiguity (BUG-01) not yet resolved against a live run |
| TC-03 | Stake max boundary / negative | Critical | Pending |
| TC-04 | Balance validation | High | **FAILED** — see execution-results.md BUG-04 |
| TC-05 | Selection replace logic | High | Not executed this round |
| TC-06 | Match list scope (upcoming-only) | Critical | **FAILED** — see execution-results.md BUG-02 |

Originally selected for execution (Part A.2): **TC-01, TC-02, TC-03** — the three Critical scenarios covering the money-moving happy path plus both hard boundary rules, which is where a bug has the most direct financial consequence. TC-04 and TC-06 were also executed and both failed; see `execution-results.md` for full bug reports (BUG-02, BUG-03, BUG-04).