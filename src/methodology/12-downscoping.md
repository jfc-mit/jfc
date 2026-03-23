## 12. Scope Management and Downscoping

Downscoping is a last resort when the full-strength approach is genuinely
infeasible. It is not a shortcut for avoiding difficulty, and it is not
the default response to a hard problem. Every downscope weakens the
analysis — the protocol exists to ensure the weakening is documented,
quantified, and justified.

### When to downscope

Downscoping is justified only when the stronger approach has been
**attempted and failed**, or when attempting it is **demonstrably
infeasible** (not merely difficult or uncertain). Concrete triggers:

- Data or MC genuinely unavailable (not "hard to use" — unavailable)
- Insufficient MC statistics after exploring all available samples
- Compute limits that make the method impossible within the resource
  envelope (not "slower than we'd like")
- Missing external inputs with no viable substitute
- Method attempted and shown to fail (with documented evidence)

"The alternative might not work" or "the alternative would be harder" are
not sufficient justifications. If the alternative is the stronger method,
try it first. If it fails, document why and downscope with evidence.

### How

0. **Attempt the full-strength approach first.** Before downscoping,
   the executor must either (a) attempt the stronger method and document
   its failure, or (b) document why attempting it is infeasible (not
   merely difficult). "We expected it wouldn't work" is not evidence —
   "we tried it and it failed because [specific reason]" is.
1. **Document** the constraint in the experiment log.
2. **Choose best achievable method.** Fall back along complexity ladder
   (GNN → BDT → cut-based) or reduce scope.

   **Label the status change.** When a method's role changes (e.g.,
   "co-primary" → "cross-check", "primary unfolding" → "abandoned"),
   record the transition in the experiment log with a [D] label:
   `[D] SVD unfolding: co-primary → cross-check (diagonal fraction 24.7%,
   below 30% threshold)`. The Phase 3/4 artifact must use the updated
   status label. Silent status changes — where a method quietly
   disappears or is relabeled without documentation — are Category A
   at review.
3. **Quantify impact.** Estimate what the missing resource would contribute.
4. **Carry to the AN.** Every downscoping → method section + systematic
   table + Future Directions. A limitation only in the experiment log is
   not properly documented.

### Key scenarios

- **Missing MC:** Omit if small, or estimate from theory (sigma * epsilon from similar
  process).
- **Low MC stats:** Coarser binning, merged regions, cut-and-count. Include
  MC stat uncertainty (Barlow-Beeston).
- **Cannot evaluate a systematic from own data:** Never leave as zero. Use
  literature value (via RAG), inflate conservatively, cite source.
- **Skipping approach exploration.** Choosing a simpler approach (e.g.,
  cut-based over MVA) without trying the alternative is a downscope. It must
  follow the standard protocol: document the constraint, quantify the
  expected impact, and carry the limitation to the AN. Concerns about the
  alternative's costs (e.g., increased correlations, training difficulty)
  are valid constraints to document, but they do not exempt the analysis
  from quantifying what was foregone.

### Review

Reviewers check: (1) was the stronger approach attempted or is
infeasibility documented with evidence? (2) is the quantified impact
credible? (3) is the limitation documented in the AN? Downscoping
without evidence of attempting the stronger method is Category A.

### Future Directions — implement, don't defer

**The default response to a feasible improvement is to implement it, not
to write it in Future Directions.** When an agent identifies an
improvement during the analysis — a better tagging method, a generator
comparison, a calibration that would reduce a dominant systematic — the
question is: "Can this be done in < 2 hours of implementation + compute?"
If yes, do it now. If no, document it in Future Directions with a
specific explanation of what makes it infeasible.

**"Future Directions" is for genuinely infeasible improvements:**
- Collecting more data (requires new running)
- Developing a new algorithm architecture (requires R&D)
- Running full detector simulation (requires multi-day compute + expertise)
- Obtaining external inputs not available (requires other groups)
- Implementing methods that require software not installable in the
  current environment (after documented installation failure)

**"Future Directions" is NOT for:**
- Running PYTHIA 8 at particle level (~30 min)
- Trying a contamination matrix correction on an existing tagger (~1 hour)
- Decomposing a systematic into normalization vs shape components (~1 hour)
- Overlaying published measurements from a thesis (~1 hour)
- Implementing a per-hemisphere truth label using available gen-level info
  (~1 hour)
- Attempting a data-driven calibration of an uncalibrated variable (~2 hours)

These are all tasks that were deferred to "Future Directions" in actual
analyses but were later implemented (sometimes during regression) in ~1
hour, producing significant improvements. The analysis would have been
stronger if they had been attempted during the original phase execution.

**Practical test:** When writing a Future Directions item, ask: "If the
human reading this said 'do it now,' would the agent be able to complete
it within the current session?" If yes, it should not be in Future
Directions — it should be in the current plan. The orchestrator should
monitor Future Directions items as they accumulate and trigger their
implementation when feasible.

Phase 5 AN must include a Future Directions section for genuinely
infeasible items: what was downscoped, what resources are needed, expected
improvement, and priority order. Each item must pass the feasibility test
above — reviewers should flag any item that could have been implemented.

---
