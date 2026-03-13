# Experiment Log — Phase 2: Exploration

## 2026-03-13 | Claude | Phase 2 Exploration

### Actions taken
1. Installed Python dependencies (uproot, awkward, mplhep, hist, rich) into user site-packages
2. Wrote and executed `01_sample_inventory.py` — catalogued all data/MC files, trees, branches, data types, event counts. Verified MC tree relationships. Identified and characterized all `passes*` branches.
3. Wrote and executed `02_exploration.py` — prototyped on 1 data file (1992, 551k events) + 1 MC file (001, 19k reco). Produced 16 figures: thrust, multiplicity, energy, cos(theta), track pT/|p|/theta, thrust recomputation, cut boundaries, resolution, cutflow, weights, thrust variants, efficiency, MC matching, nParticle, sphericity.
4. Wrote and executed `03_full_stats.py` — loaded ALL 6 data files (3.05M events) and ALL 40 MC files (772k reco, 974k genBefore). Produced 3 additional figures: full-stats tau comparison, resolution+efficiency, year-by-year stability. Computed full cutflow and binning proposal.
5. Committed scripts to git.
6. Produced exploration artifact `EXPLORATION_claude_2026-03-13_17-00.md`.

### Key results
- 3,050,610 data events, 771,597 MC reco, 973,769 MC genBefore
- MC trees verified event-matched
- passesAll selects 94.72% of data
- Pre-applied cuts confirmed looser than Batts selection
- Thrust resolution: RMS ~0.015 (varies 0.006-0.032 with tau)
- particleWeight = 1.0 everywhere (unweighted MC)
- Recommended binning: published ALEPH 19-bin scheme

### Issues encountered
- Initial script tried to load all particle-level jagged branches for 551k events, causing slow I/O. Fixed by loading scalar-only branches first and limiting particle-level reads to 50k events.
- `passes*` branches include one jagged type (passesArtificAccept per track), which caused a crash when trying np.unique on nested arrays. Fixed by using awkward-array handling.

### Time spent
- Script development and debugging: ~30 minutes
- Data I/O and processing: ~5 minutes total runtime
- Artifact writing: ~15 minutes
