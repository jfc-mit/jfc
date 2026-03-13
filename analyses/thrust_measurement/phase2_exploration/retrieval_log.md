# Retrieval Log — Phase 2: Exploration

## Retrieved information

### From upstream artifacts
- **Strategy document** (`STRATEGY_margaret_2026-03-13_16-00.md`): Analysis plan, event selection criteria, MC tree definitions, observable definition, binning guidance, correction procedure
- **Input spec** (`inputs_claude_2026-03-13_17-00.md`): Phase instructions, upstream artifact reference

### From data files (programmatic discovery)
- Tree and branch structure discovered at runtime via uproot
- Event counts read from ROOT file metadata
- Selection flag values read and characterized

### External references used
- Published ALEPH thrust binning from hep-ex/0406111 (Table 9): 19-bin scheme from 0 to 0.50. **Note:** The exact bin edges were reconstructed from general knowledge of the publication; the paper itself was not directly accessed during this phase. The bin edges should be verified against the actual publication in Phase 3.

### Information NOT retrieved (marked for future phases)
- ALEPH detector performance paper (inspire_325900): not accessed; track quality criteria (ntpc >= 4) remain unverified from primary source
- Batts thesis (inspire_1793969): not accessed; exact cut definitions for passesISR, passesWW, passesLEP1TwoPC remain unknown
- Published ALEPH thrust data points from hep-ex/0406111: not retrieved; needed for quantitative comparison in Phase 4
