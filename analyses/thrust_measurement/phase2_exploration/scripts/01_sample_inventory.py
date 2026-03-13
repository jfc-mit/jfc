#!/usr/bin/env python3
"""Phase 2 Exploration — Script 01: Sample Inventory and Tree/Branch Discovery.

Examines data and MC ROOT files to catalog tree structures, branch names,
event counts, and data types. Validates MC tree relationships (t, tgen, tgenBefore).
"""

import logging
import json
import sys
from pathlib import Path

import numpy as np
import uproot
import awkward as ak
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("inventory")

# --- Paths ---
DATA_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPH")
MC_DIR = Path("/n/holystore01/LABS/iaifi_lab/Lab/sambt/LEP/ALEPHMC")
OUT_DIR = Path("/n/home07/anovak/work/reslop/analyses/thrust_measurement/phase2_exploration/scripts")

DATA_FILES = sorted(DATA_DIR.glob("LEP1Data*_recons_aftercut-MERGED.root"))
MC_FILES = sorted(MC_DIR.glob("LEP1MC1994_recons_aftercut-*.root"))

# ============================================================
# 1. Data file inventory
# ============================================================
log.info("=" * 60)
log.info("DATA FILE INVENTORY")
log.info("=" * 60)

data_summary = {}
total_data_events = 0

for fpath in DATA_FILES:
    log.info(f"Opening {fpath.name}")
    with uproot.open(fpath) as f:
        keys = f.keys()
        log.info(f"  Top-level keys: {keys}")
        tree = f["t"]
        n = tree.num_entries
        total_data_events += n
        branches = tree.keys()
        log.info(f"  Tree 't': {n} entries, {len(branches)} branches")
        data_summary[fpath.name] = {
            "entries": n,
            "n_branches": len(branches),
            "keys": keys,
        }

log.info(f"\nTotal data events: {total_data_events:,}")

# Save branch list from first data file
with uproot.open(DATA_FILES[0]) as f:
    tree = f["t"]
    branch_info = {}
    for bname in tree.keys():
        b = tree[bname]
        branch_info[bname] = {
            "typename": str(b.typename),
            "interpretation": str(b.interpretation),
        }

log.info(f"\nData branches ({len(branch_info)}):")
for bname, binfo in sorted(branch_info.items()):
    log.info(f"  {bname:40s} {binfo['typename']:30s}")

# ============================================================
# 2. MC file inventory (prototype on first file, then count all)
# ============================================================
log.info("\n" + "=" * 60)
log.info("MC FILE INVENTORY")
log.info("=" * 60)

mc_file_0 = MC_FILES[0]
log.info(f"Prototype MC file: {mc_file_0.name}")

with uproot.open(mc_file_0) as f:
    keys = f.keys()
    log.info(f"  Top-level keys: {keys}")

    for tname in ["t", "tgen", "tgenBefore"]:
        if f"{tname};1" in keys or tname in keys:
            tree = f[tname]
            n = tree.num_entries
            branches = tree.keys()
            log.info(f"  Tree '{tname}': {n} entries, {len(branches)} branches")

            # Print branches for this tree
            log.info(f"  Branches of '{tname}':")
            for bname in sorted(branches):
                b = tree[bname]
                log.info(f"    {bname:40s} {str(b.typename):30s}")
        else:
            log.warning(f"  Tree '{tname}' NOT FOUND")

# Count events across all MC files
log.info("\nCounting events across all MC files...")
mc_counts = {"t": [], "tgen": [], "tgenBefore": []}

for fpath in MC_FILES:
    with uproot.open(fpath) as f:
        for tname in mc_counts:
            try:
                mc_counts[tname].append(f[tname].num_entries)
            except Exception:
                mc_counts[tname].append(0)

for tname, counts in mc_counts.items():
    log.info(
        f"  Tree '{tname}': {sum(counts):,} total, "
        f"min={min(counts):,}, max={max(counts):,}, "
        f"mean={np.mean(counts):.0f}/file, files={len(counts)}"
    )

# ============================================================
# 3. Verify MC tree relationships (t and tgen are event-matched)
# ============================================================
log.info("\n" + "=" * 60)
log.info("MC TREE RELATIONSHIP VERIFICATION")
log.info("=" * 60)

with uproot.open(mc_file_0) as f:
    n_t = f["t"].num_entries
    n_tgen = f["tgen"].num_entries
    n_tgenBefore = f["tgenBefore"].num_entries

    log.info(f"  t entries:          {n_t}")
    log.info(f"  tgen entries:       {n_tgen}")
    log.info(f"  tgenBefore entries: {n_tgenBefore}")
    log.info(f"  t == tgen?          {n_t == n_tgen}")
    log.info(f"  tgenBefore > t?     {n_tgenBefore > n_t}")

    # Check if t and tgen share common branches that can verify event matching
    t_branches = set(f["t"].keys())
    tgen_branches = set(f["tgen"].keys())
    tgenBefore_branches = set(f["tgenBefore"].keys())

    common_t_tgen = t_branches & tgen_branches
    only_t = t_branches - tgen_branches
    only_tgen = tgen_branches - t_branches

    log.info(f"\n  Branches in t: {len(t_branches)}")
    log.info(f"  Branches in tgen: {len(tgen_branches)}")
    log.info(f"  Branches in tgenBefore: {len(tgenBefore_branches)}")
    log.info(f"  Common t & tgen: {len(common_t_tgen)}")
    log.info(f"  Only in t (not tgen): {sorted(only_t)[:10]}...")
    log.info(f"  Only in tgen (not t): {sorted(only_tgen)[:10]}...")

    # Check tgenBefore branches vs tgen
    common_tgen_before = tgen_branches & tgenBefore_branches
    only_before = tgenBefore_branches - tgen_branches
    log.info(f"  Common tgen & tgenBefore: {len(common_tgen_before)}")
    log.info(f"  Only in tgenBefore: {sorted(only_before)[:10]}...")

# ============================================================
# 4. Check for passes* branches
# ============================================================
log.info("\n" + "=" * 60)
log.info("SELECTION FLAG BRANCHES (passes*)")
log.info("=" * 60)

with uproot.open(DATA_FILES[0]) as f:
    tree = f["t"]
    passes_branches = [b for b in tree.keys() if "pass" in b.lower()]
    log.info(f"  Branches containing 'pass': {passes_branches}")

    # Also check for Thrust-related branches
    thrust_branches = [b for b in tree.keys() if "thrust" in b.lower() or "Thrust" in b]
    log.info(f"  Branches containing 'thrust/Thrust': {thrust_branches}")

    # Check for weight branches
    weight_branches = [b for b in tree.keys() if "weight" in b.lower() or "Weight" in b]
    log.info(f"  Branches containing 'weight/Weight': {weight_branches}")

    # Check for event number / run number branches
    event_branches = [b for b in tree.keys() if any(x in b.lower() for x in ["event", "run", "evn", "nrun"])]
    log.info(f"  Event/run branches: {event_branches}")

# Do the same for MC
log.info("\n  MC file passes* branches:")
with uproot.open(mc_file_0) as f:
    for tname in ["t", "tgen", "tgenBefore"]:
        tree = f[tname]
        passes_branches = [b for b in tree.keys() if "pass" in b.lower()]
        thrust_branches = [b for b in tree.keys() if "thrust" in b.lower() or "Thrust" in b]
        weight_branches = [b for b in tree.keys() if "weight" in b.lower() or "Weight" in b]
        log.info(f"    {tname} passes*: {passes_branches}")
        log.info(f"    {tname} thrust*: {thrust_branches}")
        log.info(f"    {tname} weight*: {weight_branches}")

# ============================================================
# 5. Quick look at passes* values in data
# ============================================================
log.info("\n" + "=" * 60)
log.info("PASSES* BRANCH VALUES (first data file)")
log.info("=" * 60)

with uproot.open(DATA_FILES[0]) as f:
    tree = f["t"]
    passes_branches = [b for b in tree.keys() if "pass" in b.lower()]
    if passes_branches:
        data = tree.arrays(passes_branches, library="ak")
        for bname in passes_branches:
            vals = data[bname]
            # Handle both scalar and jagged types
            if hasattr(vals.type.content, 'content'):
                # jagged array - flatten first
                flat = ak.flatten(vals)
                unique = np.unique(ak.to_numpy(flat))
                log.info(
                    f"  {bname}: JAGGED, unique(flat)={unique}, "
                    f"len={len(vals)}"
                )
            else:
                arr = ak.to_numpy(vals)
                unique = np.unique(arr)
                log.info(
                    f"  {bname}: unique={unique}, "
                    f"sum={np.sum(arr)}, "
                    f"frac_true={np.mean(arr):.4f}, "
                    f"n={len(arr)}"
                )

# Same for MC
log.info("\n  MC passes* values (tree t):")
with uproot.open(mc_file_0) as f:
    tree = f["t"]
    passes_branches = [b for b in tree.keys() if "pass" in b.lower()]
    if passes_branches:
        data = tree.arrays(passes_branches, library="ak")
        for bname in passes_branches:
            vals = data[bname]
            if hasattr(vals.type.content, 'content'):
                flat = ak.flatten(vals)
                unique = np.unique(ak.to_numpy(flat))
                log.info(
                    f"  {bname}: JAGGED, unique(flat)={unique}, "
                    f"len={len(vals)}"
                )
            else:
                arr = ak.to_numpy(vals)
                unique = np.unique(arr)
                log.info(
                    f"  {bname}: unique={unique}, "
                    f"sum={np.sum(arr)}, "
                    f"frac_true={np.mean(arr):.4f}, "
                    f"n={len(arr)}"
                )

# ============================================================
# 6. Print all branch names for reference
# ============================================================
log.info("\n" + "=" * 60)
log.info("FULL BRANCH LISTING — Data tree 't'")
log.info("=" * 60)

with uproot.open(DATA_FILES[0]) as f:
    tree = f["t"]
    for i, bname in enumerate(sorted(tree.keys())):
        b = tree[bname]
        log.info(f"  [{i:3d}] {bname:45s} {str(b.typename):30s}")

log.info("\n" + "=" * 60)
log.info("FULL BRANCH LISTING — MC tree 'tgenBefore'")
log.info("=" * 60)

with uproot.open(mc_file_0) as f:
    tree = f["tgenBefore"]
    for i, bname in enumerate(sorted(tree.keys())):
        b = tree[bname]
        log.info(f"  [{i:3d}] {bname:45s} {str(b.typename):30s}")

log.info("\nDone with sample inventory.")
