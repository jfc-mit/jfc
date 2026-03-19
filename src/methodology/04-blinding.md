## 4. Blinding / Staged Validation Protocol

Both searches and measurements follow the same staged protocol. For
searches, "blinding" means not examining the SR discriminant in data. For
measurements without SR structure, it means not computing the final quantity
on real data. The gate structure is identical.

### 4.1 Stages

| Stage | Data access | Gate |
|-------|-------------|------|
| Phases 1–3 | MC only (searches: no SR data; measurements: no data-derived result) | — |
| Phase 4a | Asimov/MC pseudo-data only | 4-bot review (§6.2) |
| Phase 4b | 10% data subsample (fixed random seed) | 4-bot review → human gate |
| Phase 4c | Full data | 1-bot review |

**Asimov data** = synthetic pseudo-data from the nominal model, bin contents
at exact expected values (no fluctuations).

**10% partial unblinding (Phase 4b):** Select 10% of data with fixed seed.
Normalize MC to 10% luminosity. Run full analysis chain. Compare to Phase 4a
expected results — should be compatible within large uncertainties. Fix
problems *before* seeing more data.

**Full unblinding (Phase 4c):** Only after human approves at the 4b gate.
Post-unblinding modifications must be documented and justified.

### 4.2 Human Gate

After Phase 4b review passes, present to the human:
- Draft analysis note with 10% results
- Unblinding checklist:
  1. Background model validated (closure tests pass)
  2. Systematics evaluated, fit model stable
  3. Expected results physically sensible
  4. Signal injection / closure tests pass
  5. 10% partial unblinding shows no pathologies
  6. All agent review cycles resolved (arbiter PASS)
  7. Draft AN reviewed and publication-ready modulo full results

The human approves, requests changes, or halts. The agent does not fully
unblind autonomously.

---
