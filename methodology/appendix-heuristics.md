## Appendix C: Tool Heuristics (Agent-Maintained)

This appendix is a living document. On first encounter with a tool, the agent
queries the tool's current documentation, extracts best practices and common
pitfalls, and records a concise summary here. Subsequent agents (or sessions)
consult this appendix first and only re-query upstream docs if something is
out of date or missing.

**Purpose:** Avoid repeated full-doc lookups. Each entry captures what the agent
learned so the next session starts with working knowledge rather than reading
the full API surface from scratch. This is analogous to the blessed snippets
library but for tool-level idioms and gotchas.

**Format:** One subsection per tool. Each entry should include:
- Version tested against
- Key idioms and recommended patterns
- Common pitfalls and how to avoid them
- Performance notes if relevant

**Maintenance rules:**
- The agent **must** check this appendix before querying external docs for any
  tool listed in Section 7.1.
- If an entry exists and is sufficient, use it — do not re-query.
- If an entry is missing or incomplete, query the current docs and use the
  result. **Do not modify this file during analysis execution** — it lives
  in the spec directory. Instead, note the missing/outdated entry in the
  experiment log. Updates to this appendix happen after the analysis completes,
  following the same process as `conventions/` updates.
- Keep entries concise — heuristics and gotchas, not full API references.

<!-- Agent: populate entries below as you encounter each tool. -->

### mplhep

**Version:** 0.3.x+

**Key idioms:**
- Use `mplhep.style.use("CMS")` for the default style sheet. This sets fonts,
  tick sizes, and figure aesthetics. It does NOT add experiment labels.
- Experiment labels are added explicitly via `mplhep.cms.label(...)`,
  `mplhep.atlas.label(...)`, etc. These functions have kwargs to control every
  piece of text:
  - `label=''` — the status text (e.g., "Preliminary", "Internal", or empty)
  - `rlabel='sqrt(s) = 91 GeV'` — the right-side label (energy, lumi, etc.)
  - `loc=0` — position preset
  - `data=True/False` — whether to show "data" qualifier
- **Do NOT** hack around unwanted label text by patching rcParams or removing
  matplotlib text objects after the fact. The label functions expose all
  the controls you need as kwargs. Read `help(mplhep.cms.label)`.
- For ALEPH-era analyses using CMS style: call
  `mplhep.cms.label(label='', rlabel='ALEPH LEP1 data', data=True)` to get
  clean labeling without CMS branding.

**Common pitfalls:**
- Using `hep.style.use('ATLAS')` then trying to suppress "ATLAS" text
  post-hoc. Just use the style for aesthetics and the label function for text.
- Forgetting `rlabel=''` and getting a default "(13 TeV)" watermark from CMS
  style. Always set `rlabel` explicitly.

**Performance:** No concerns — plotting is never the bottleneck.
