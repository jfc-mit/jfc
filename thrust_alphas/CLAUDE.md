# Analysis: thrust_alphas

Type: measurement
Technique: unfolding

## Environment

This analysis has its own pixi environment defined in `pixi.toml`.
All scripts must run through pixi:

```bash
pixi run py path/to/script.py          # run a script
pixi run py -c "import uproot; ..."     # quick check
pixi shell                              # interactive shell with all deps
```

**Never use bare `python`, `pip install`, or `conda`.** If you need a
package, add it to `pixi.toml` under `[pypi-dependencies]` and run
`pixi install`.

## Applicable conventions

- `conventions/unfolding.md` — required systematics, response matrix validation, regularization, covariance

## Reference analyses

To be filled during Phase 1. The strategy must identify 2-3 published
reference analyses and tabulate their systematic programs. This table is
a binding input to Phase 4 and Phase 5 reviews.

## General rules

See the project-root CLAUDE.md for tool requirements and coding rules.
See `conventions/` for technique-specific guidance.
