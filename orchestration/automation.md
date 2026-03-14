## Automation

The following pseudocode illustrates the orchestration logic. It is not a
runnable script — helper functions like `find_latest_artifact`, `extract_decision`,
and `present_for_human_review` are orchestrator responsibilities whose
implementation depends on the agent system. The logic and control flow are
what matter.

```bash
# --- Configuration ---

# exec_model is derived from the model_tier setting in analysis_config.yaml:
#   auto:         sonnet for phases 2-4 execution, opus for phase 1
#   uniform_high: opus everywhere
#   uniform_mid:  sonnet everywhere
exec_model=${EXEC_MODEL:-sonnet}

# Hard cap on review iterations. Correctness is the real termination condition
# (arbiter PASS or reviewer finding no Category A issues), but this prevents
# infinite loops if something goes pathologically wrong.
max_review_iterations=${MAX_REVIEW_ITER:-10}

# --- Session naming ---

# Pool of human first names. The orchestrator picks randomly without
# replacement within an analysis run. See "Agent Session Identity" above.
pick_session_name() {
  # Returns an unused name from the pool. Implementation detail —
  # any unique-per-run naming scheme works.
  echo "$(shuf -n1 names_pool.txt)"
}

# --- Regression detection and upstream feedback ---

run_regression_check() {
  # Checks review output for regression triggers. If found, dispatches
  # investigation and fixes. Returns non-zero if regression was found,
  # signaling that the caller should not proceed to the next phase.
  dir=$1
  review_artifact=$(find_latest_review_artifact "$dir")

  if grep -q "regression trigger" "$review_artifact"; then
    origin_phase=$(extract_regression_origin "$review_artifact")
    echo "REGRESSION detected in $dir — origin: $origin_phase"
    echo "$(date): $dir -> $origin_phase" >> regression_log.md

    # Investigator (opus) produces a scoped regression ticket
    run_agent --name "$(pick_session_name)" --model opus \
      --output "$origin_phase/REGRESSION_TICKET.md" \
      "Investigate regression trigger from $dir."

    # Fix the origin phase
    run_agent --name "$(pick_session_name)" --model $exec_model \
      --output "$origin_phase/exec" \
      "Fix regression described in $origin_phase/REGRESSION_TICKET.md"

    # Re-review at the original tier for that phase
    tier=$(get_review_tier "$origin_phase")
    if [ "$tier" = "3bot" ]; then
      run_3bot_review "$origin_phase"
    else
      run_1bot_review "$origin_phase"
    fi

    # Re-run all downstream phases from the regressed phase
    rerun_downstream_from "$origin_phase"
    return 1  # regression found — caller should not proceed
  fi
  return 0
}

check_upstream_feedback() {
  dir=$1
  feedback_file="$dir/UPSTREAM_FEEDBACK.md"
  if [ -f "$feedback_file" ]; then
    echo "Upstream feedback found in $dir — routing to next review"
    # The feedback file is in the directory; reviewers will discover it
    # when reading the phase contents for the next review gate.
  fi
}

# --- Review tier functions ---

# Returns 0 on PASS, 1 on regression, 2 on escalation/max-iterations.
# Callers should check the return code before proceeding to the next phase.
run_3bot_review() {
  dir=$1
  i=0
  while [ $i -lt $max_review_iterations ]; do
    i=$((i + 1))
    if [ $i -gt 3 ]; then
      echo "WARNING: review iteration $i for $dir"
    fi
    if [ $i -gt 5 ]; then
      echo "STRONG WARNING: review iteration $i for $dir"
    fi

    # Critical and constructive reviewers run in parallel (independent)
    run_agent --name "$(pick_session_name)" --model opus \
      --output "$dir/review/critical" "critical review" &
    run_agent --name "$(pick_session_name)" --model opus \
      --output "$dir/review/constructive" "constructive review" &
    wait

    # Arbiter reads both reviews and the artifact
    run_agent --name "$(pick_session_name)" --model opus \
      --output "$dir/review/arbiter" "arbitrate"
    decision=$(extract_decision "$dir/review/arbiter")

    case $decision in
      PASS)
        if ! run_regression_check "$dir"; then
          return 1  # regression found — do not proceed
        fi
        check_upstream_feedback "$dir"
        return 0
        ;;
      ITERATE)
        # Write new session-named inputs file for the next executor run.
        # Includes: arbiter assessment, Category A issues, original upstream
        # artifacts. No file is overwritten — session naming ensures each
        # iteration's inputs and outputs coexist on disk.
        exec_name=$(pick_session_name)
        write_iteration_inputs "$dir" "$i" "$exec_name"
        run_agent --name "$exec_name" --model $exec_model \
          --output "$dir/exec" "iterate v$((i+1))"
        ;;
      ESCALATE)
        present_for_human_review "$dir"
        wait_for_human_input
        # Human may resolve and signal continue, or halt the analysis
        ;;
    esac
  done

  # Fell through — hit the hard cap
  echo "ERROR: 3-bot review reached $max_review_iterations iterations for $dir"
  present_for_human_review "$dir"
  wait_for_human_input
  return 2
}

# Returns 0 on PASS, 1 on regression, 2 on escalation/max-iterations.
run_1bot_review() {
  dir=$1
  i=0
  while [ $i -lt $max_review_iterations ]; do
    i=$((i + 1))
    if [ $i -gt 3 ]; then
      echo "WARNING: 1-bot review iteration $i for $dir"
    fi

    run_agent --name "$(pick_session_name)" --model sonnet \
      --output "$dir/review/critical" "critical review"

    if ! review_has_category_a "$dir/review/critical"; then
      # No Category A issues — review passes
      if ! run_regression_check "$dir"; then
        return 1
      fi
      check_upstream_feedback "$dir"
      return 0
    fi

    # Category A issues found — iterate
    exec_name=$(pick_session_name)
    write_iteration_inputs_1bot "$dir" "$i" "$exec_name"
    run_agent --name "$exec_name" --model $exec_model \
      --output "$dir/exec" "iterate v$((i+1))"
  done

  # Fell through — hit the hard cap
  echo "ERROR: 1-bot review reached $max_review_iterations iterations for $dir"
  present_for_human_review "$dir"
  wait_for_human_input
  return 2
}

# --- Main pipeline ---
# Supports two flows:
#   analysis_type=search:      full blinding protocol (4a → 4b → human → 4c → 5)
#   analysis_type=measurement: no blinding (4a → human → 5)

run_agent --name "$(pick_session_name)" --model opus \
  --output "phase1_strategy/exec" "execute phase 1"
run_3bot_review "phase1_strategy" || exit 1
git merge phase1_strategy

run_agent --name "$(pick_session_name)" --model sonnet \
  --output "phase2_exploration/exec" "execute phase 2"
# Self-review only — no external review
git merge phase2_exploration

# Phase 3 — per channel (parallel execution, sequential review)
for channel in nunu llbb; do
  run_agent --name "$(pick_session_name)" --model sonnet \
    --output "phase3_selection/channel_$channel/exec" \
    "execute phase 3 ($channel)" &
done
wait
for channel in nunu llbb; do
  run_1bot_review "phase3_selection/channel_$channel" || exit 1
done
run_agent --name "$(pick_session_name)" --model sonnet \
  --output "phase3_selection/exec" "consolidate channels"
git merge phase3_selection

# Shared calibrations (can run in parallel with phases 2-3)
for cal in btag jet_corrections; do
  run_agent --name "$(pick_session_name)" --model sonnet \
    --output "calibrations/$cal" "calibration: $cal" &
done
# Calibrations must complete before Phase 4a — calibration artifacts
# (scale factors, corrections) are required inputs for inference.
wait

# Phase 4a — agent gate (3-bot review must PASS to proceed)
run_agent --name "$(pick_session_name)" --model sonnet \
  --output "phase4_inference/4a_expected/exec" "execute phase 4a"
run_3bot_review "phase4_inference/4a_expected" || {
  echo "Phase 4a review did not pass."
  exit 1
}
git merge phase4a_expected

if [ "$analysis_type" = "search" ]; then
  # Search flow: partial unblinding → human gate → full unblinding
  run_agent --name "$(pick_session_name)" --model sonnet \
    --output "phase4_inference/4b_partial/exec" "partial unblinding"
  run_3bot_review "phase4_inference/4b_partial" || exit 1
  present_for_human_review "phase4_inference/4b_partial"
  wait_for_human_decision  # APPROVE / REQUEST CHANGES / HALT
  git merge phase4b_partial

  run_agent --name "$(pick_session_name)" --model sonnet \
    --output "phase4_inference/4c_observed/exec" "full unblinding"
  run_1bot_review "phase4_inference/4c_observed" || exit 1
  git merge phase4c_observed
else
  # Measurement flow: result is already visible — skip 4b/4c
  # Human gate still applies after 4a review passes
  present_for_human_review "phase4_inference/4a_expected"
  wait_for_human_decision  # APPROVE / REQUEST CHANGES / HALT
fi

run_agent --name "$(pick_session_name)" --model sonnet \
  --output "phase5_documentation/exec" "execute phase 5"
run_3bot_review "phase5_documentation" || exit 1
git merge phase5_documentation
```
