## 10. Parallelism

This specification is written for a single agent executing phases sequentially.
For parallel execution:

- **Within a phase:** Multiple agents may work in parallel provided they write
  to separate sub-artifacts and a consolidation step merges outputs before
  review.
- **Across phases:** Sequential by design. An agent beginning Phase N reads the
  completed artifact from Phase N-1.
- **Review as a separate agent:** Results and writeup reviews should be distinct
  agent invocations. This provides adversarial review that self-review cannot.
- **Per-channel parallelism:** In multi-channel analyses, channel-specific work
  in Phases 2–3 can proceed in parallel as separate agent teams, merging in
  Phase 4.

### 10.1 Sub-delegation Within a Phase

Phase executors should sub-delegate compute-heavy or narrowly-scoped tasks to
sub-agents rather than attempting everything in a single session. The executor
acts as coordinator: it plans the work, delegates execution, and integrates
results.

Tasks well-suited for sub-delegation:
- **MVA training** — hyperparameter search, overtraining validation, feature
  importance. The sub-agent receives the training data specification and
  returns the trained model + performance metrics.
- **Systematic variation evaluation** — each systematic source (or group of
  related sources) can be evaluated independently.
- **Plot generation** — once the data is prepared, producing a batch of
  standard plots is mechanical work suitable for a lower-tier model.
- **Closure tests** — running fits or comparisons in validation regions.

Sub-agents within a phase:
- Run **sequentially by default** (to avoid conflicting file writes), unless
  their outputs are guaranteed independent (separate directories).
- Receive **explicit, bounded inputs** — the executor writes an input
  specification, the sub-agent reads it and writes output files.
- Share the phase's **experiment log** — sub-agents append to the same log.
- Use **dedicated sub-agents** — BDT training and plot generation can use
  dedicated sub-agents; the executor coordinates them.

The executor should not sub-delegate *judgment* — decisions about which
backgrounds to include, what selection approach to use, or whether closure
tests pass are the executor's responsibility. Sub-agents handle execution.

---
