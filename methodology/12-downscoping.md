## 12. Scope Management and Downscoping

Scientific research is inherently iterative. Every analysis is complete enough
for a key message — a measurement, a limit, a new technique — but there is
always more that could be done with more resources, more data, or more time.
The agent must internalize this: **a finished analysis with a simpler method
is always better than an unfinished analysis waiting for the ideal method.**

### 12.1 When to Downscope

The agent should downscope when any of the following are true:

- **Data or MC is unavailable.** A simulation sample is inaccessible, corrupt,
  or simply doesn't exist. Example: signal MC for an exotic decay mode hasn't
  been produced yet.
- **MC statistics are insufficient.** The available MC sample is too small for
  the intended method (e.g., training a BDT with 200 events, or a template
  fit where MC stat uncertainty dominates).
- **Compute exceeds what's available.** Training a large neural network would
  require multi-GPU for days, but the analysis needs to move forward now.
- **External inputs are missing.** A required measurement (luminosity
  calibration, tracking efficiency map, beam energy spread) hasn't been
  published or isn't accessible.
- **The method is disproportionate to the gain.** A GNN tagger might improve
  b-tagging efficiency by 5% relative, but a BDT gets you 90% of the way
  there and can be built in an afternoon.

### 12.2 How to Downscope

When downscoping, the agent follows this protocol:

1. **Document the constraint.** Record in the experiment log what is
   unavailable and why (e.g., "ZZ→4l MC not accessible on current storage;
   only ZZ→2l2ν available").
2. **Choose the best achievable method.** Fall back along the complexity
   ladder: GNN → FCN → BDT → cut-based. Or reduce the scope: fewer channels,
   fewer systematic variations, simpler background model. The goal is the
   best result achievable with what's available now.
3. **Quantify the impact.** Where possible, estimate what the missing resource
   would have contributed. "The ZZ→4l background is expected to be <2% of the
   total in the signal region based on cross-section ratios, so its omission
   has negligible impact on the result." Or: "A GNN tagger could improve
   signal efficiency by ~15% based on LHC benchmarks, but the BDT achieves
   sufficient separation for a 3σ observation."
4. **Flag it for future work.** Add a concrete entry to the analysis's future
   directions: what resource is needed, what method would be used, and what
   improvement is expected.

### 12.3 Common Downscoping Scenarios

**Missing MC samples.** Omit the process if it's small, or estimate its
contribution from theory (cross-section × efficiency from a similar process).
Document the assumption and its uncertainty.

**Insufficient MC statistics.** Use a coarser binning, merge regions, or
switch from a shape-based fit to a cut-and-count. MC statistical uncertainty
can also be included as a systematic (Barlow-Beeston lite) if the fitter
supports it — pyhf does.

**No GPU / large training infeasible.** Use a BDT instead. For most HEP
classification tasks (especially at LEP scale), a BDT on well-chosen
high-level features matches or approaches NN performance. Reserve NNs for
cases where the input space genuinely demands it.

**Missing external measurements.** Use the best available value from
literature, assign a conservative uncertainty, and document the source.
Example: "Luminosity taken from [ALEPH-2000-xyz] with 1.5% uncertainty;
a dedicated Bhabha analysis could reduce this to 0.5%."

**Inaccessible data subsets.** Run on what's available. If only 70% of the
data is accessible, the analysis is still valid — just with reduced
statistical power. Scale the MC accordingly and note the missing runs.

### 12.4 Downscoping and the Review Protocol

Reviewers should evaluate downscoping decisions on two axes:

1. **Is the chosen method adequate for the physics goal?** A 3σ evidence
   claim needs less sophistication than a 5σ discovery. Cut-based selections
   are perfectly fine if they achieve sufficient sensitivity.
2. **Is the limitation properly documented?** The analysis note must
   acknowledge what was not done and why, with a quantitative estimate of the
   impact where possible.

A reviewer should NOT flag "you could have used a more complex method" as a
Category A issue unless the simpler method is demonstrably inadequate for the
stated physics goal. This is a Category B suggestion at most.

### 12.5 Future Directions as a First-Class Output

The Phase 5 documentation artifact must include a **Future Directions** section
that collects all downscoping decisions into a concrete roadmap:

- What was descoped and why
- What resources would be needed to un-descope it
- What improvement is expected (quantitative where possible)
- Rough priority ordering

This section is not an apology — it is a plan. Every analysis generates
knowledge about what to do next. The next iteration of the analysis (or a
follow-up analysis) consults this roadmap and picks up where this one left off.

---
