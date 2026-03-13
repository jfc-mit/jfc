## Phase Regression

When a reviewer or executor discovers a fundamental issue from an earlier phase:

```
1. Document the issue + identify origin phase
2. Tag as "regression trigger" in review artifact
3. Log in analysis_name/regression_log.md
4. Orchestrator re-runs the identified phase with new context
5. All downstream phases re-run from the regressed phase
```

The regression input for the re-run phase includes a brief describing what
was discovered and why the original output was insufficient.
