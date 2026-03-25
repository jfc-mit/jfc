# Spec Audit — 2026-03-25

Comprehensive review of the slopspec methodology for weaknesses, gaps,
conflicts, physics errors, and anything that could prevent a first-try
analysis note without human intervention.

---

## Status key

- [ ] Not started
- [~] Decision needed from user
- [x] Fixed

---

## 1. Structural / Process Gaps

### 1a. Phase 4 sub-directory structure not scaffolded

**Problem:** `scaffold_analysis.py` creates a flat `phase4_inference/`
directory. The methodology (`appendix-sessions.md`, `root_claude.md`
phase gates table) expects `phase4_inference/4a_expected/`,
`4b_partial/`, `4c_observed/` with full subdirectory trees (outputs/,
src/, review/, logs/). The agent will look for
`phase4_inference/4a_expected/outputs/INFERENCE_EXPECTED.md` and find
nothing.

**Proposed fix:** Add 4a/4b/4c subdirectory creation to
`scaffold_analysis.py` with the same subdir structure as other phases.

- [ ] Apply fix

---

### 1b. Phase 4 CLAUDE.md template doesn't address the 4a/4b/4c split

**Problem:** `src/templates/phase4_claude.md` is a single template for
all of Phase 4. The methodology describes three distinct sub-phases with
different goals (expected / 10% validation / full data), different data
access rules, and different review tiers. The template doesn't tell the
executor which sub-phase they're in.

**Proposed fix:** Split into `phase4a_claude.md`, `phase4b_claude.md`,
`phase4c_claude.md` — each stating the sub-phase goal, data access
permissions, artifact name, and review tier. The scaffolder creates
all three inside the 4a/4b/4c subdirs.

- [ ] Apply fix

---

### 1c. COMMITMENTS.md required but not scaffolded or mentioned in templates

**Problem:** Section 3 Phase 4a says "At Phase 1 completion, create
`COMMITMENTS.md`" — but the scaffolder doesn't create a stub, and the
Phase 1 CLAUDE.md template doesn't mention it. The commitment-tracking
memory note confirms this was a real failure mode in previous analyses.

**Proposed fix:** Add explicit instruction to `phase1_claude.md` template:
"Before submitting the strategy artifact, create COMMITMENTS.md listing
every binding commitment." Scaffold a stub file.

- [ ] Apply fix

---

### 1d. `references.bib` scaffolded only in `phase5_documentation/outputs/`

**Problem:** BibTeX validation runs at Phase 4a (4-bot+bib) and 4b. The
AN is written starting at 4a, so citations need a `references.bib` at
that point. The scaffolder puts the stub only in Phase 5.

**Proposed fix:** Scaffold `references.bib` at the analysis root level
(or in a shared `outputs/` directory) and symlink/copy into each AN-
producing phase. Alternatively, scaffold it in `phase4_inference/`
and instruct the Phase 5 note writer to use the same file.

**Question for user:** Do you prefer a single analysis-root
`references.bib` that all phases reference, or per-phase copies?

- [~] Decision needed

---

### 1e. `build-pdf` pixi task referenced everywhere but never defined

**Problem:** The methodology references `pixi run build-pdf` in: Phase 2
(PDF build test), typesetter instructions, rendering reviewer, table
formatting advice. The template `pixi.toml` doesn't define this task.
First-try agents will get "task not found."

**Proposed fix:** Add a `build-pdf` task to the template `pixi.toml`
that runs the three-step pipeline (pandoc -> postprocess_tex.py ->
tectonic). Something like:

```toml
[tasks]
build-pdf = """
  pandoc phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md \
    -o phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.tex \
    --standalone --include-in-header=conventions/preamble.tex \
    --number-sections --toc --filter pandoc-crossref --citeproc && \
  python conventions/postprocess_tex.py phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.tex && \
  tectonic phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.tex
"""
```

**Question for user:** The AN filename changes per phase (4a, 4b, 4c, 5)
and version. Should `build-pdf` take an argument, or should each phase
define its own `build-pdf-4a` etc.? Or should the task just find the
latest AN markdown automatically?

- [~] Decision needed

---

### 1f. `lint-plots` pixi task referenced but never defined

**Problem:** The executor prompt says "Run `pixi run lint-plots`" but
the task doesn't exist in the template `pixi.toml`. The script exists at
`src/conventions/lint_plots.py` (symlinked as `conventions/lint_plots.py`
in each analysis).

**Proposed fix:** Add to template `pixi.toml`:

```toml
lint-plots = "python conventions/lint_plots.py"
```

- [ ] Apply fix

---

### 1g. No `tectonic` or LaTeX compiler in scaffolded pixi.toml dependencies

**Problem:** The typesetter instructions say to compile with `tectonic`
or `pdflatex`, but neither is in the template `pixi.toml` dependencies.
`pixi add tectonic` at runtime may fail on some platforms.

**Proposed fix:** Add `tectonic` to `[dependencies]` in the template
`pixi.toml`. Also add `pandoc-crossref` if it's available via conda-forge
(it is).

- [ ] Apply fix

---

## 2. Conflicting Instructions

### 2a. Category B: "must fix before PASS" vs arbiter only iterates on A

**Problem:** The classification says Category B "Must fix before PASS."
But the arbiter's prompt template says "End with: PASS / ITERATE (list
Category A items)" — no mention of B items forcing iteration. The
`root_claude.md` review protocol section says "(B) Must fix before PASS."
This creates inconsistency: does the arbiter ITERATE on B items?

**Proposed fix:** Update the arbiter prompt template to explicitly
include B items in the ITERATE decision:

```
End with: PASS / ITERATE (list Category A and B items) / ESCALATE
If ITERATE: list ALL Category A and B findings the fixer must address.
```

Also update §6.5 to state: "The arbiter must not PASS with unresolved
A or B items. Category C items are applied before commit but do not
require re-review."

- [ ] Apply fix

---

### 2b. Phase 2 review: self-review vs self-review + plot validator

**Problem:** §6.2 says Phase 2 is "Self-review + plot validator." The
Phase 2 description in §3 doesn't mention the plot validator. The
appendix-sessions directory layout shows "# Self-review only — no
review/ directory" for Phase 2. These contradict each other.

**Proposed fix:** Phase 2 exploration produces figures (data/MC
comparisons, variable surveys). These should be validated. Update the
Phase 2 description to say: "Self-review with mechanical plot validation
(run `pixi run lint-plots`). No independent reviewer subagent required."
This makes it a self-review + automated check, not a full subagent review.

**Question for user:** Do you want a full plot validator subagent at
Phase 2, or just the mechanical lint check? The figures at Phase 2 are
exploratory — a full visual validator feels like overkill, but the linter
catches real bugs.

- [~] Decision needed

---

### 2c. Figure height sizing near-collision between preamble and postprocessor

**Problem:** The preamble sets default figure height to `0.45\linewidth`.
The postprocessor adds `height=0.35\textheight` cap. With 0.75in margins:
`0.45\linewidth ~ 3.15in`, `0.35\textheight ~ 3.33in`. These are close
but different, causing inconsistent figure sizing depending on which
mechanism "wins."

**Proposed fix:** Make the postprocessor cap consistent with the preamble
default. Since `\linewidth ~ 7in` and `\textheight ~ 9.5in`:
- `0.45\linewidth = 3.15in`
- `0.33\textheight = 3.14in` (matches)

Change `postprocess_tex.py` from `0.35\textheight` to `0.33\textheight`,
or better yet, use `0.45\linewidth` in the postprocessor too (matching
the preamble exactly).

- [ ] Apply fix

---

### 2d. Ban on `[-@fig:...]` makes number-only references impossible

**Problem:** The spec bans `[-@fig:...]`, which is pandoc-crossref's
standard way to get just the figure number without "fig." prefix. This
makes patterns like "see Figs. 3-5" or "(Fig. 3)" awkward.

**Proposed fix:** This is a deliberate choice to enforce consistent
reference style. The workaround (always write `Figure @fig:name`) is
acceptable for analysis notes. Keep the ban but add a brief note
explaining the rationale: "Always use `@fig:name` for cross-references.
The `[-@fig:...]` suppressed-prefix form produces inconsistent reference
styles and is banned. For ranges, write 'Figures @fig:a through @fig:c'."

- [ ] Apply fix (add rationale note)

---

## 3. Physics Methodology Concerns

### 3a. Asimov data definition confuses extraction measurements

**Problem:** §4.1 defines Asimov data as "exact expected values (no
fluctuations)." But `extraction.md` says Phase 4a should use MC pseudo-
data that may be Poisson-fluctuated to assess statistical reach. These
are different things — Asimov (no fluctuation) vs pseudo-data (with
fluctuation).

**Proposed fix:** Add a clarification to §4.1:

> For shape/template fit analyses, Asimov data has bin contents at exact
> expected values (no fluctuations). For counting/extraction analyses,
> MC pseudo-data may include Poisson fluctuations to assess statistical
> reach — see the applicable conventions file for the specific protocol.

- [ ] Apply fix

---

### 3b. No covariance guidance for bin-by-bin correction outside unfolding conventions

**Problem:** The unfolding conventions discuss covariance construction in
detail. But an analysis doing bin-by-bin correction (e.g., EEC) might
not consult `unfolding.md` because it's not technically "unfolding."
The general methodology (§3, §7) doesn't discuss covariance at all.

**Proposed fix:** The unfolding conventions file already says "When this
applies: Any analysis that corrects a detector-level distribution to a
particle-level result — regardless of the correction method used." This
is clear enough. Add a cross-reference in §3 Phase 4a:

> For any analysis that produces a corrected distribution (including
> bin-by-bin correction), consult `conventions/unfolding.md` for
> covariance construction requirements — these apply regardless of
> whether the method is technically "unfolding."

- [ ] Apply fix

---

### 3c. 3-sigma validation target rule lacks trials factor guidance

**Problem:** If an analysis extracts 10 quantities and one deviates by
3.1 sigma, the probability of at least one such deviation is ~25%. The
rule doesn't account for this. Agents will burn hours investigating
statistical fluctuations.

**Proposed fix:** Add to §6.8 after the Tier 1 description:

> **Trials factor.** When an analysis extracts N independent quantities,
> a single >3-sigma deviation among them is increasingly expected as N
> grows. For N >= 5, reviewers should assess whether the deviation is
> consistent with a trials factor before requiring full Tier 1
> investigation. A single 3.1-sigma pull among 10 independent
> measurements (expected: ~2.7% chance for at least one) warrants
> documentation but not necessarily a blocking investigation. Two or
> more >3-sigma deviations, or a single deviation >4-sigma, always
> triggers Tier 1 regardless of N.

- [ ] Apply fix

---

### 3d. No guidance on numerical precision for intermediate calculations

**Problem:** The spec requires 2-3 significant figures for AN display
but says nothing about computational precision. Extraction formulas
involving ratios of large numbers can lose significance.

**Proposed fix:** This is minor for modern Python (float64 by default).
Add a brief note to §11.2:

> Use double precision (float64) throughout. Avoid intermediate rounding
> of computed quantities — round only for display in the AN. For ratios
> of large numbers (e.g., N_obs/N_exp where both are O(10^6)), verify
> the result is stable to at least 4 significant figures.

- [ ] Apply fix

---

## 4. Agent Prompt Gaps

### 4a. Physics reviewer checks convention drift but doesn't receive conventions

**Problem:** The physics reviewer's prompt includes "CONVENTION DRIFT
CHECK (mandatory at Phases 4a-5): Re-read the Phase 1 strategy and the
conventions/ file." But its Reads section says it receives "ONLY physics
prompt + artifact." The conventions file isn't in its context.

**Proposed fix:** Remove the convention drift check from the physics
reviewer. This is the critical reviewer's job — the critical reviewer
has full access to conventions. Add a note:

> Convention drift is checked by the critical reviewer (who has
> conventions access). The physics reviewer evaluates physics merit
> independently.

Move the convention drift check text from `physics_reviewer.md` to
`critical_reviewer.md` (if not already there — the critical reviewer
already has a "DECISION LABEL TRACEABILITY" check that partially
overlaps).

- [ ] Apply fix

---

### 4b. Constructive reviewer lacks plotting standards reference

**Problem:** The critical reviewer reads `appendix-plotting.md`. The
constructive reviewer doesn't. If the constructive reviewer spots a
figure quality issue, it has no standard to cite.

**Proposed fix:** Add to constructive reviewer's Methodology References:

```
| Plotting standards | `methodology/appendix-plotting.md` |
```

- [ ] Apply fix

---

### 4c. Fixer agent has no RAG access

**Problem:** The fixer reads artifacts, code, and conventions — but not
the RAG corpus. If a review finding says "propagate systematic X as done
in ALEPH:2005ab," the fixer can't look up the reference.

**Proposed fix:** Add RAG MCP tools to the fixer's Reads section:

```
- Experiment corpus (via RAG MCP tools) — when a finding references a
  published analysis methodology
```

- [ ] Apply fix

---

### 4d. No agent is explicitly told to create `results/` JSON files

**Problem:** §3 Phase 4c says the executor "must create
`phase5_documentation/outputs/results/`" with JSON files. The note
writer reads from these. But the executor prompt template never mentions
creating JSON outputs — it focuses on the artifact markdown and figures.

**Proposed fix:** Add to the executor prompt template (after the
artifact self-check section):

```
MACHINE-READABLE OUTPUTS (mandatory at Phases 4a-4c):
Write all numerical results to JSON files in
phase5_documentation/outputs/results/:
- Fitted parameters: {name: {value: float, stat: float, syst: float}}
- Per-systematic shifts: {source: {bin_edges: [...], shifts: [...]}}
- Covariance matrices: {stat: [[...]], syst: [[...]], total: [[...]]}
- Per-energy-point results (if applicable): {sqrt_s: {value, stat, syst}}
These JSON files are the single source of truth for the note writer.
```

- [ ] Apply fix

---

### 4e. Note writer's figure inventory command has wrong path

**Problem:** The note writer prompt says:
`find */outputs/figures/ -name "*.pdf" | sort`
But the note writer runs from within `phase5_documentation/`, so
`*/outputs/figures/` won't find figures in other phases.

**Proposed fix:** Change to:
`find ../../phase*/outputs/figures/ -name "*.pdf" | sort`

Or better yet, use a relative path from the analysis root:
`find phase*/outputs/figures/ ../../phase*/outputs/figures/ -name "*.pdf" 2>/dev/null | sort -u`

Actually, the simplest fix: instruct the note writer to run from the
analysis root, or provide the correct path explicitly.

- [ ] Apply fix

---

## 5. Rendering / Typesetting Issues

### 5a. `<!-- COMPOSE -->` annotations stripped by pandoc

**Problem:** The note writer marks figure groups with HTML comments like
`<!-- COMPOSE: 2x3 grid -->`. Pandoc strips HTML comments from `.tex`
output. The typesetter is told to search the `.tex` for these
annotations, but they won't be there.

**Proposed fix:** The Phase 5 description already partially addresses
this: "the typesetter should search for `COMPOSE` in the markdown
source." Make this explicit and primary:

1. Update the typesetter prompt to say: "Search the MARKDOWN source
   (not .tex) for `<!-- COMPOSE -->` annotations to identify figure
   groups."
2. Add a pre-typesetting step: the typesetter reads the .md first for
   annotations, then processes the .tex.

- [ ] Apply fix

---

### 5b. `fix_subfig_package` adds support for banned `\subfloat`

**Problem:** The postprocessor adds `\usepackage{subfig}` when it
detects `\subfloat` — but the spec bans `\subfloat`. This is a belt-
and-suspenders safety net, but its presence is confusing.

**Proposed fix:** Change `fix_subfig_package` to emit a WARNING instead
of silently adding the package:

```python
def fix_subfig_package(lines):
    """Warn if \\subfloat is used — banned by spec."""
    text = ''.join(lines)
    if '\\subfloat' in text:
        count = text.count('\\subfloat')
        sys.stderr.write(
            f"WARNING: {count} \\subfloat occurrence(s) found. "
            f"The spec bans \\subfloat — use side-by-side "
            f"\\includegraphics with \\hspace instead.\n")
        return f'{count} subfloat-warnings'
    return None
```

Still add the package (so compilation doesn't fail), but warn loudly.

- [ ] Apply fix

---

## 6. Process Integrity Risks

### 6a. No enforcement of `model: "opus"` for subagents

**Problem:** The spec says all subagents must use `model: "opus"` —
"non-negotiable." But there's no hook, no check, and no automated
enforcement.

**Proposed fix:** This is a Claude Code configuration concern, not a
spec fix. Add a note to the orchestrator template:

> When spawning any subagent, always include `model: "opus"` in the
> Agent tool call. Verify this before every spawn — degraded model
> quality silently weakens review and execution quality.

Beyond this, enforcement would require a hook (out of scope for the
spec itself).

- [ ] Apply fix (add note to template)

---

### 6b. Session name assignment has no operational mechanism

**Problem:** The spec describes session names from a pool of 88 names.
But the orchestrator template never mentions them, and the
`orchestrator/names.py` referenced in the spec doesn't exist (per user
feedback: "do not read/modify/reference orchestrator/ directory").

**Proposed fix:** Add a simple session name assignment block to the
orchestrator template:

```
SESSION NAME ASSIGNMENT:
Before spawning each subagent, assign a unique session name from this
pool: Ada, Agnes, Albert, Alfred, ... [full list].
Tell the subagent its name in the prompt: "Your session name is {name}."
The subagent uses this name in output filenames:
  {ARTIFACT}_{name}_{YYYY-MM-DD}_{HH-MM}.md
Track used names to avoid reuse within the analysis run.
```

This keeps naming self-contained in the template without needing
external infrastructure.

**Question for user:** Is the session naming system working in practice,
or do agents just use un-named files? If the latter, should we simplify
to timestamped filenames without names?

- [~] Decision needed

---

### 6c. Re-review protocol unclear in orchestrator template

**Problem:** When the arbiter says ITERATE, the orchestrator spawns a
fixer, then... what? "Re-review with a fresh reviewer added to the
panel" — does this mean a completely new panel, the same panel + one
more, or just one reviewer? The naming of re-review artifacts
(`{PHASE}_REREVIEW.md` vs `{PHASE}_REVIEW_v2.md`) is also inconsistent.

**Proposed fix:** Update the orchestrator template step 3 to be
explicit:

```
3. CHECK — read the arbiter verdict.
   If ITERATE:
     a. Spawn fixer agent with the arbiter's finding list
     b. After fixer completes, spawn a FRESH review panel (same
        composition as the original — physics + critical +
        constructive + arbiter for 4-bot phases, critical only for
        1-bot phases). Do NOT reuse the original reviewers.
     c. The re-review artifact is named with the new reviewer's
        session name and version-incremented.
     d. Repeat until arbiter PASS. Warn at 3 iterations, strong warn
        at 5, hard cap at 10.
   If PASS: proceed.
   If ESCALATE: present to human with escalation reasoning.
```

- [ ] Apply fix

---

## 7. Missing Pieces That Will Block First-Try Success

### 7a. No guidance when `pixi install` fails

**Problem:** Package resolution failures are common (version conflicts,
unavailable packages). The spec assumes `pixi install` works.

**Proposed fix:** Add to §7 (Tools) or the orchestrator template:

> If `pixi install` fails: (1) read the error message, (2) check
> whether the failing package has a conda-forge vs PyPI mismatch (move
> between `[dependencies]` and `[pypi-dependencies]`), (3) try relaxing
> version constraints, (4) if a specific package is unavailable, check
> for an alternative. Document the resolution in the experiment log.

- [ ] Apply fix

---

### 7b. No SLURM availability detection

**Problem:** Scale-out rules say "> 15 min -> SLURM" but don't address
systems without SLURM.

**Proposed fix:** Add: "If SLURM is not available (`which sbatch`
returns empty), use `ProcessPoolExecutor` with all available cores as
the fallback for long-running tasks. Adjust expectations for wall-clock
time accordingly."

- [ ] Apply fix

---

### 7c. No fallback when RAG corpus is unavailable

**Problem:** The critical and constructive reviewers are told to "query
the experiment corpus." If the MCP server isn't running, they have no
fallback protocol.

**Proposed fix:** Add to the reviewer prompt templates:

> If RAG corpus tools are unavailable (MCP connection fails), proceed
> with the review using only the artifact, conventions, and your domain
> knowledge. Note "RAG unavailable" in the review output. Prioritize
> checks that don't require corpus access (numerical consistency,
> convention coverage, figure quality) over those that do (reference
> analysis comparison, published methodology cross-check).

- [ ] Apply fix

---

### 7d. Phase CLAUDE.md templates may be incomplete

**Problem:** The phase templates (`phase1_claude.md` through
`phase5_claude.md`) may not contain all the requirements from the
methodology sections. If a template is sparse, the executor misses
critical requirements.

**Proposed fix:** Audit each template against its methodology section.
This is a follow-up task, not an immediate fix.

- [ ] Audit templates (follow-up)

---

### 7e. No explicit crash-recovery handoff protocol

**Problem:** The spec says "write the artifact and stop cleanly" under
context pressure, and session logs provide crash resilience. But there's
no explicit protocol for: how does the orchestrator detect a stalled
agent? How does it resume? What if the artifact was half-written?

**Proposed fix:** The orchestrator template already has health monitoring
("check logs before respawning," "no commit in >10 minutes"). Add:

> When respawning a stalled agent: (1) read the session log to determine
> what was accomplished, (2) read any partial artifact on disk, (3) tell
> the replacement agent what its predecessor accomplished (from the
> session log) and instruct it to continue from that point, not restart.
> If no session log exists, the agent produced nothing — restart from
> scratch.

- [ ] Apply fix

---

## 8. Minor Issues

### 8a. §8 doesn't exist but is referenced

**Problem:** The methodology skips from §7 to §9. Some references to
"§8" may exist (e.g., in context management tables).

**Proposed fix:** Search for §8 references and either renumber or
redirect. If no references exist, this is a non-issue.

- [ ] Verify and fix if needed

---

### 8b. Double data=False violation in lint_plots.py

**Problem:** Lines 89-96 check `data=False` on the same line as
`llabel`, then also within a 3-line context window. This can produce
duplicate violations for the same issue.

**Proposed fix:** Deduplicate: if the same-line check fires, skip the
context-window check.

- [ ] Apply fix

---

### 8c. Excessive `\needspace` before figures in postprocessor

**Problem:** `fix_figure_placement` adds `\needspace{0.4\textheight}`
before every `\begin{figure}`. With many sequential figures, this
forces excessive page breaks.

**Proposed fix:** Reduce to `\needspace{0.25\textheight}` — enough to
avoid orphaned figure starts but not so aggressive that it creates
whitespace.

- [ ] Apply fix

---

### 8d. agents/README.md not verified

**Problem:** The agents README contains the activation matrix telling
the orchestrator which agents to spawn per phase. If this is incomplete
or inconsistent with the methodology, the orchestrator will assemble
wrong review panels.

**Proposed fix:** Audit `agents/README.md` against §6.2 review tier
table. Follow-up task.

- [ ] Audit (follow-up)

---

## Prioritized Fix Order

### Batch 1: First-try blockers (fix immediately)
1. **1a** — Scaffold Phase 4 subdirectories
2. **1e** — Add `build-pdf` pixi task
3. **1f** — Add `lint-plots` pixi task
4. **1g** — Add `tectonic` to pixi dependencies
5. **2a** — Fix Category B ambiguity in arbiter

### Batch 2: High-impact fixes
6. **1b** — Split Phase 4 CLAUDE.md templates
7. **1c** — Add COMMITMENTS.md to scaffolder + Phase 1 template
8. **4a** — Fix physics reviewer convention drift contradiction
9. **4d** — Add JSON output instructions to executor prompt
10. **4e** — Fix note writer figure inventory path

### Batch 3: Medium-impact fixes
11. **1d** — Decide on references.bib location
12. **2c** — Unify figure sizing
13. **3a** — Clarify Asimov vs pseudo-data
14. **3b** — Cross-reference covariance guidance
15. **3c** — Add trials factor guidance
16. **4b** — Add plotting standards to constructive reviewer
17. **4c** — Add RAG to fixer agent
18. **5a** — Fix COMPOSE annotation discovery
19. **6b** — Add session name instructions to orchestrator
20. **6c** — Clarify re-review protocol

### Batch 4: Polish
21. **2b** — Clarify Phase 2 review scope
22. **2d** — Add rationale for [-@fig:] ban
23. **3d** — Numerical precision note
24. **5b** — Change subfig function to warning
25. **6a** — Add model selection note
26. **7a-7e** — Robustness / fallback guidance
27. **8a-8d** — Minor fixes

---

## Questions for User

1. **1d:** Single analysis-root `references.bib` vs per-phase copies?
2. **1e:** Should `build-pdf` take an argument for the AN filename, or
   should each phase define its own task?
3. **2b:** Full plot validator subagent at Phase 2, or just mechanical
   lint check?
4. **6b:** Is the session naming system working in practice? Should we
   simplify to timestamped filenames?
