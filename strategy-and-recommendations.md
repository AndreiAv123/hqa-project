# Strategy & Recommendations

## Why these 2 tests

**E2E: happy-path bet placement.** It's the one flow the product exists for, and it touches
everything — match list, bet slip, loading state, receipt. Money not matching what the user was
shown is the worst-case failure here.

This test found BUG-03 (receipt missing the selection, teams reversed, payout wrong). It doesn't
just check a Bet ID appears — it computes `stake × odds` itself and checks that against both the
Bet Slip and the receipt, and checks team order is identical across match card → bet slip →
receipt.

**API: stake/balance validation.** Cheap and fast to check at the API layer, and it's the layer
that actually matters — client-side validation can always be bypassed.

This found BUG-04 (API accepts a stake over the available balance, balance goes negative, wrong
currency returned). The test places a valid bet, then one that's in-range but exceeds what's left,
and checks it's rejected (422) with balance unchanged. Every request logs its curl equivalent, so a
failing run prints the exact repro.

Both tests also check the first match/element is `UPCOMING`, guarding against BUG-02 (past matches
still biddable).

## Left manual-only

- **Error modal (Rebet/Close/X)** — lower risk, UX detail, not worth automating yet. Its selectors
  are also still unconfirmed.
- **Selection replace (TC-05) / filters (§2.6)** — worth automating later; the odds filter has a
  confirmed bug (Quick-Fire #2).
- **Visual/layout** — different tooling (Percy/Chromatic), out of scope here.
- **Cross-browser/responsive** — spec scopes this to desktop only, correctly out of scope.

## Recommendations

1. **For every bug found manually, add the assertion that would've caught it** — don't just fix
   and move on. That's exactly how the current 2 tests were shaped.
2. **Resolve the spec conflict (BUG-01) before writing more tests against it.** A contradictory
   spec produces tests that all look "correct" until compared.
3. **CI: API suite on every PR, E2E suite nightly.** Keeps PRs fast, still catches full-stack
   regressions.
4. **Test data isolation will need to go further at scale** — unique `user_id` + reset-before-run
   works for one suite, but parallel CI/shared staging needs dedicated per-run users and a stable
   match catalog (`first_match` currently just trusts whatever's returned first). Also: the
   reset-balance endpoint reports €125.50 but actual balance is €120.00 (Quick-Fire #5) — worth
   fixing upstream.