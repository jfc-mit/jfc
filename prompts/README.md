# Analysis Prompts

Physics prompts for ALEPH open data analyses at the Z pole. Each prompt
is self-contained -- paste the fenced block into a Claude instance at
the repo root. The agent reads the spec, conventions, and RAG corpus
to fill in methodology, systematics, and correction strategy.

## Analyses

| Prompt | Physics | Key observables |
|--------|---------|-----------------|
| [lund_jet_plane](lund_jet_plane.md) | Jet substructure | Lund plane density, k_t and angular projections |
| [zlineshape_alphas](zlineshape_alphas.md) | Electroweak | M_Z, Gamma_Z, N_nu, R_l, alpha_s |
| [rb_rc](rb_rc.md) | Heavy flavour EW | R_b, R_c, A_FB^b, sin^2(theta_eff) |
| [eec_correlators](eec_correlators.md) | QCD precision | EEC, AEEC, mean charged multiplicity |
| [colour_factors](colour_factors.md) | QCD gauge structure | C_A/C_F, T_R/C_F from 4-jet angles |

## Data

All analyses use the same ALEPH archived data at sqrt(s) ~ 91.2 GeV:

- **Data:** ~3M hadronic Z decays (1992-1995), 6 ROOT files
- **MC:** PYTHIA 6.1 with full detector simulation, ~770K events, 41 ROOT files
- **Location:** `/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/`
- **RAG corpus:** ~2400 converted LEP papers (ALEPH + DELPHI)

## Usage

```bash
# From the repo root:
pixi run scaffold analyses/<name> --type measurement
# Edit .analysis_config to set data_dir
cd analyses/<name> && pixi install
claude   # paste the prompt
```
