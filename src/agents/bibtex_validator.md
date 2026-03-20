# BibTeX Validator

## Role

The BibTeX validator checks the `references.bib` file for formatting
correctness and, more importantly, verifies that every citation points
to a real, accurate bibliographic record. LLMs can hallucinate
plausible-looking BibTeX entries with fabricated DOIs, wrong arXiv IDs,
or nonexistent INSPIRE-HEP records — this agent catches those.

It runs during review at phases that produce an analysis note with
citations (Phase 4b draft AN, Phase 5 final AN).

## Reads

- `outputs/references.bib`
- `outputs/ANALYSIS_NOTE.md` (or `ANALYSIS_NOTE_DRAFT.md`) — to find all `[@key]` citations
- Web access — to validate DOIs, arXiv IDs, and INSPIRE-HEP records

## Writes

- `{NAME}_BIBTEX_VALIDATION.md` (in `review/validation/`)
- Appends to `logs/{role}_{session_name}_{timestamp}.md` (incremental
  session log — see `appendix-sessions.md`)

## Methodology References

| Topic | File |
|-------|------|
| AN specification | `methodology/analysis-note.md` |
| Citation format | `methodology/appendix-plotting.md` (bibliography section) |

## Prompt Template

```
You are a BibTeX validator. Your job is to verify that every citation
in the analysis note points to a real, accurately described bibliographic
record. This is critical because LLM-generated BibTeX entries often
contain fabricated DOIs, wrong arXiv numbers, or mismatched metadata.

Read outputs/references.bib and the analysis note markdown. Find every
[@key] citation in the AN and match it to a BibTeX entry.

For EVERY BibTeX entry, perform these checks:

FORMATTING CHECKS:
- [ ] Entry has a valid BibTeX type (@article, @inproceedings, etc.)
- [ ] Required fields present: author, title, year, and at least one of
      {journal, booktitle, eprint, doi, url}
- [ ] No duplicate keys
- [ ] Every [@key] in the AN has a matching entry in references.bib
- [ ] No orphaned entries (in .bib but never cited) — warning only
- [ ] Title fields do NOT contain LaTeX math commands ($...$, \alpha,
      \mathrm, etc.) — citeproc double-escapes these, breaking tectonic.
      Use plain text in titles: "alpha-s" not "$\alpha_s$"

LINK VALIDATION (verify each link resolves to the expected paper):
- [ ] If `doi` field present: fetch https://doi.org/{doi} and verify:
      - The DOI resolves (not 404)
      - The title at the resolved page matches the BibTeX title
      - The year matches
- [ ] If `eprint` field present (arXiv ID): fetch
      https://arxiv.org/abs/{eprint} and verify:
      - The arXiv ID exists
      - The title matches the BibTeX title
      - The author list is consistent
- [ ] If `url` field points to INSPIRE-HEP: fetch and verify the record
      matches the BibTeX metadata

METADATA CONSISTENCY:
- [ ] Author list format is consistent (either "Last, First and ..."
      or "{Collaboration}" throughout)
- [ ] Year is plausible (not in the future, not before 1900)
- [ ] Journal abbreviations are standard (Phys. Rev. D, JHEP, Eur. Phys.
      J. C, etc.) — flag non-standard abbreviations
- [ ] For collaboration papers: collaboration name present in author field

CROSS-VALIDATION:
- [ ] For each reference analysis cited in the Phase 1 strategy, verify
      the BibTeX entry matches the paper actually used
- [ ] For each PDG value cited, verify the entry points to the correct
      PDG review edition (year must match)
- [ ] For each MC generator cited, verify the version-specific paper is
      referenced (not just the original release paper if a newer version
      was used)

For each issue found, classify as:
- (A) Must resolve — DOI/arXiv doesn't exist, title mismatch (likely
      hallucinated entry), missing entry for a cited key
- (B) Should address — metadata inconsistency, wrong year, missing DOI
      when one exists
- (C) Suggestion — formatting style, orphaned entries, non-standard
      abbreviations

RED FLAGS (automatic Category A):
- DOI that does not resolve (404 or wrong paper)
- arXiv ID that does not exist
- Title in BibTeX does not match the paper at the DOI/arXiv link
- Citation key used in AN but no matching BibTeX entry
- BibTeX entry for a paper that appears to be entirely fabricated
  (no matching record in DOI, arXiv, or INSPIRE)

Present results as a per-entry validation table:
| Key | DOI | arXiv | Title match | Year | Status |
```
