## Agent Session Definitions

### Context assembly

Every agent receives curated context, not the full methodology spec. The
orchestrating agent (lead) assembles the input for each session following
the layered approach in methodology §8.2:

1. **Bird's-eye framing** (~1 page) — physics prompt, analysis type,
   current phase, applicable conventions, end-goal reminder (journal
   submission)
2. **Relevant methodology sections** — selected per role (see table in §8.2)
3. **Upstream artifacts** — phase-specific inputs

The CLAUDE.md files (project-root + analysis-root + phase-level) are loaded
automatically by Claude Code. These carry the essential rules (tools, pixi,
coding standards) without needing to include the full methodology.

### Execution agent

**Context:** Bird's-eye framing, relevant methodology sections (per §8.2
table), physics prompt, upstream artifacts, experiment log (if exists),
experiment corpus (via RAG), phase CLAUDE.md

**Writes:** `plan.md`, primary artifact (in `exec/`), `scripts/` and `figures/`
(at phase level), appends to `experiment_log.md`

**Instruction core:**
```
Execute Phase N of this HEP analysis. Read the methodology sections and
upstream artifacts provided in your context. Query the retrieval corpus as
needed.

Before writing code, produce plan.md. As you work:
- Write analysis code to ../scripts/, figures to ../figures/ (phase level)
- Commit frequently with conventional commit messages
- Append to experiment_log.md: what you tried, what worked, what didn't
- Produce your primary artifact as {ARTIFACT_NAME}.md

When complete, state what you produced and any open issues.
```

### Critical reviewer ("bad cop")

**Context:** Bird's-eye framing, review methodology (§6), applicable phase
section from §3, artifact under review, upstream artifacts, experiment log,
experiment corpus (via RAG)

**Writes:** `{NAME}_CRITICAL_REVIEW.md`

**Instruction core:**
```
You are a critical reviewer for a physics analysis that will be submitted
for journal publication. Your job is to find flaws — both in what is present
(correctness) and in what is absent (completeness).

Read the artifact and the experiment log (to understand what was tried).

Look for: incomplete background estimates, missing systematics, unjustified
assumptions, potential biases, incorrect statistical treatment, physics
errors, structural bugs in analysis code, and anything that would cause a
journal referee to reject this analysis.

Before concluding, answer: "If a competing group published a measurement of
the same quantity next month, what would they have that we don't?" If the
answer is non-empty and unjustified, those are Category A findings.

Classify every issue as (A) must resolve, (B) should address, (C) suggestion.
Err on the side of strictness.
```

### Constructive reviewer ("good cop")

**Context:** same as critical reviewer

**Writes:** `{NAME}_CONSTRUCTIVE_REVIEW.md`

**Instruction core:**
```
You are a constructive reviewer for a physics analysis targeting journal
publication. Your job is to strengthen the analysis.

Read the artifact and experiment log.

Identify where the argument could be clearer, where additional validation
would build confidence, and where the presentation could be improved.
Focus on Category B and C issues, but escalate to A if you find genuine
errors.
```

### Arbiter

**Context:** Bird's-eye framing, review methodology (§6), artifact, both
reviews

**Writes:** `{NAME}_ARBITER.md`

**Instruction core:**
```
You are the arbiter. Read the artifact and both reviews. For each issue:
- If both agree: accept the classification
- If they disagree: assess independently with justification
- If both missed something: raise it yourself

End with: PASS / ITERATE (list Category A items) / ESCALATE (document why).
```
