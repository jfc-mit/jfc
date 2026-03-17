## 12. Scope Management and Downscoping

When a resource is unavailable, downscope to what is achievable and document
the limitation — in the experiment log during execution, and in the AN.

### When to downscope

Data/MC unavailable, insufficient MC statistics, compute limits, missing
external inputs, or method is disproportionate to the gain.

### How

1. **Document** the constraint in the experiment log.
2. **Choose best achievable method.** Fall back along complexity ladder
   (GNN → BDT → cut-based) or reduce scope.
3. **Quantify impact.** Estimate what the missing resource would contribute.
4. **Carry to the AN.** Every downscoping → method section + systematic
   table + Future Directions. A limitation only in the experiment log is
   not properly documented.

### Key scenarios

- **Missing MC:** Omit if small, or estimate from theory (σ × ε from similar
  process).
- **Low MC stats:** Coarser binning, merged regions, cut-and-count. Include
  MC stat uncertainty (Barlow-Beeston).
- **Cannot evaluate a systematic from own data:** Never leave as zero. Use
  literature value (via RAG), inflate conservatively, cite source.

### Review

Reviewers check: (1) is the simpler method adequate? (2) is the limitation
documented in the AN?

### Future Directions

Phase 5 AN must include a Future Directions section: what was descoped, what
resources needed, expected improvement, priority order.

---
