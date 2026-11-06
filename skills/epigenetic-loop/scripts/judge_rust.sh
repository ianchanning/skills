#!/usr/bin/env bash
# ==============================================================================
# judge_rust.sh — Cold-Blooded External Judge for WillowPress Worktrees
# Part of the /epigenetic-loop & /forget-team harness.
#
# Usage:
#   ./judge_rust.sh <worktree_dir> [fixture_sha256_path]
#
# Output:
#   A single deterministic JSON line:
#   {"worktree": "w2", "valid": true, "pass_rate": 0.94, "ns_per_op": 412.0, "score": 94.58}
# ==============================================================================

set -euo pipefail

# 1. Parameter Validation & Absolute Path Resolution
# Resolve all relative paths BEFORE changing directory!
WORKTREE_DIR="${1:-}"
FIXTURE_SHA="${2:-}"

if [[ -z "$WORKTREE_DIR" || ! -d "$WORKTREE_DIR" ]]; then
    echo "{\"valid\": false, \"score\": 0.0, \"error\": \"invalid_worktree_dir\"}"
    exit 0
fi

WORKTREE_DIR="$(realpath "$WORKTREE_DIR")"
WORKTREE_NAME="$(basename "$WORKTREE_DIR")"

if [[ -n "$FIXTURE_SHA" ]]; then
    if [[ -f "$FIXTURE_SHA" ]]; then
        FIXTURE_SHA="$(realpath "$FIXTURE_SHA")"
    else
        echo "{\"worktree\": \"$WORKTREE_NAME\", \"valid\": false, \"pass_rate\": 0.0, \"ns_per_op\": null, \"score\": 0.0, \"error\": \"fixture_sha_file_not_found\"}"
        exit 0
    fi
fi

cd "$WORKTREE_DIR"

# 2. Shared Target Directory (Prevents Multi-Gigabyte Target Duplication)
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-/tmp/willow-shared-target}"
mkdir -p "$CARGO_TARGET_DIR"

# 3. Anti-Goodhart Sentinel Check
# Prevents agents from passing by deleting tests or editing fixtures!
if [[ -n "$FIXTURE_SHA" && -f "$FIXTURE_SHA" ]]; then
    if ! sha256sum --quiet -c "$FIXTURE_SHA" 2>/dev/null; then
        echo "{\"worktree\": \"$WORKTREE_NAME\", \"valid\": false, \"pass_rate\": 0.0, \"ns_per_op\": null, \"score\": 0.0, \"error\": \"anti_goodhart_fixture_tampering_detected\"}"
        exit 0
    fi
fi

# 4. Compilation Gate
if ! cargo check --quiet --message-format=short >/dev/null 2>&1; then
    echo "{\"worktree\": \"$WORKTREE_NAME\", \"valid\": false, \"pass_rate\": 0.0, \"ns_per_op\": null, \"score\": 0.0, \"error\": \"compilation_failed\"}"
    exit 0
fi

# 5. Test Suite Evaluation (Parse Passed vs Total across all test binaries)
# Skip Doc-tests (--lib --bins --tests) and sum all 'test result:' lines across binaries
TEST_OUTPUT="$(cargo test --lib --bins --tests --quiet 2>&1 || true)"

PASSED_COUNT=$(echo "$TEST_OUTPUT" | awk '/test result:/ {for(i=1;i<=NF;i++) if($i=="passed;") sum+=$(i-1)} END {print sum+0}')
FAILED_COUNT=$(echo "$TEST_OUTPUT" | awk '/test result:/ {for(i=1;i<=NF;i++) if($i=="failed;") sum+=$(i-1)} END {print sum+0}')

TOTAL_TESTS=$((PASSED_COUNT + FAILED_COUNT))

if [[ "$TOTAL_TESTS" -eq 0 ]]; then
    # If no tests exist yet (Bootstrap phase)
    PASS_RATE=0.0
else
    PASS_RATE=$(awk -v p="$PASSED_COUNT" -v t="$TOTAL_TESTS" 'BEGIN { printf "%.4f", p / t }')
fi

# 6. Benchmark Metric (ns_per_op)
# Run microbenches only if the test pass rate is high (>=80%)
NS_PER_OP="null"
LATENCY_BONUS=0.0

if awk -v pr="$PASS_RATE" 'BEGIN { exit (pr >= 0.80 ? 0 : 1) }'; then
    BENCH_OUTPUT="$(cargo bench 2>&1 || true)"
    
    # Extract nanoseconds from standard criterion / bench output: "time: [412.10 ns ...]" or "412 ns/iter"
    DETECTED_NS=$(echo "$BENCH_OUTPUT" | grep -oE '[0-9]+(\.[0-9]+)? ns/iter' | head -n 1 | awk '{print $1}' || true)
    if [[ -z "$DETECTED_NS" ]]; then
        DETECTED_NS=$(echo "$BENCH_OUTPUT" | grep -oE 'time: +\[[0-9]+(\.[0-9]+)? ns' | head -n 1 | awk '{print $NF}' || true)
    fi

    if [[ -n "$DETECTED_NS" ]]; then
        NS_PER_OP="$DETECTED_NS"
        # Composite reward: base score from pass_rate (0-100) + sub-microsecond latency bonus
        LATENCY_BONUS=$(awk -v ns="$DETECTED_NS" 'BEGIN { printf "%.2f", (1000.0 / (ns + 10.0)) }')
    fi
fi

# 7. Compute Composite Score
# Score = (pass_rate * 100) + latency_bonus
FINAL_SCORE=$(awk -v pr="$PASS_RATE" -v bonus="$LATENCY_BONUS" 'BEGIN { printf "%.2f", (pr * 100.0) + bonus }')

VALID_FLAG="false"
if awk -v pr="$PASS_RATE" 'BEGIN { exit (pr > 0.0 ? 0 : 1) }'; then
    VALID_FLAG="true"
fi

# 8. Output Single Clean JSON Record
echo "{\"worktree\": \"$WORKTREE_NAME\", \"valid\": $VALID_FLAG, \"pass_rate\": $PASS_RATE, \"ns_per_op\": $NS_PER_OP, \"score\": $FINAL_SCORE}"
exit 0
