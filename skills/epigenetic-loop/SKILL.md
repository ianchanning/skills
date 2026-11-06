---
name: epigenetic-loop
description: >
  Orchestrates the Epigenetic Amnesia Loop combining dspy.RLM (external context excavation
  and post-mortem invariant distillation), Ralph Mode-A bootstrapping, and /forget-team
  Mode-B 4-worktree Herdr tournaments with Rust compiler backpressure.
requires:
  - forget-team
  - herdr
  - uv
---

# Skill: The Epigenetic Amnesia Loop (`/epigenetic-loop`)

## 1. Architectural Premise & The Triad of State

Standard coding agents fail at scale from two opposing pathologies: **Context Anchoring** (keeping session history causes smaller edits and local-optima plateaus) and **Total Amnesia** (wiping session history causes fresh agents to repeatedly fall into the same syntax/domain traps).

This skill resolves the paradox by splitting state into three strict biological tiers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│             THE CYBERNETIC TRIAD OF THE EPIGENETIC LOOP                 │
├─────────────────────────────────────────────────────────────────────────┤
│  1. GENETICS (DNA) = `<best_sha>` in Git                                │
│     • Only code that passes `judge_rust.sh` (tests + benchmark gate)    │
│       survives to become the baseline genome for the next generation.   │
├─────────────────────────────────────────────────────────────────────────┤
│  2. WORKING MEMORY (Synapses) = `Herdr` Worker Panes (`w1..w4`)         │
│     • Short-lived tactical execution (Gemma 4 / Qwen 3.8 / Flash 3.8).  │
│     • Ruthlessly WIPED every 3–5 turns via `/forget-team` so the        │
│       workers never suffer context rot or path-dependent anchoring!     │
├─────────────────────────────────────────────────────────────────────────┤
│  3. EPIGENETICS (Methylation) = `dspy.RLM` Prompt Compiler              │
│     • Runs OUTSIDE the worker panes and Lead session during resets!     │
│     • Uses RLM to inspect failed worktree diffs & compiler stderr       │
│       without bloating any context window.                              │
│     • Uses DSPy to compile 1-line "invariants" & few-shot signatures    │
│       into `AGENTS.md` / worker contract for the NEXT generation!       │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Mental Model: Component Interaction

```
┌────────────────────────────────────────────────────────────────────────┐
│  1. THE COCKPIT (Interactive Chat: Lead Architect in `agy`)            │
│     • Pure high-level conversation: zero Python harness in chat.       │
│     • Guards Lead context window: delegates heavy reading to CLI.      │
└───────────────────┬────────────────────────────────────┬───────────────┘
                    │                                    │
     (Massive dirty data/code)              (Parallel code evolution)
                    ▼                                    ▼
┌───────────────────────────────────────┐  ┌─────────────────────────────┐
│  2. THE EXCAVATOR (`rlm_probe.py`)    │  │  3. THE MUSCLE              │
│     • Standalone CLI tool via `uv run`│  │     (`/forget-team` Skill)  │
│     • Chews through multi-GB dumps or │  │     • Markdown skill driving│
│       legacy source trees in REPL.    │  │       `herdr pane` + git wt │
│     • Spits out specs & fixtures.     │  │     • Evaluated externally  │
│     • Headless post-mortem distill.   │  │       via `judge_rust.sh`.   │
└───────────────────────────────────────┘  └─────────────────────────────┘
```

### When Do We Use What? (The 0M Cheat Sheet)

| Component | What It Is | When To Use It |
| :--- | :--- | :--- |
| **Cockpit (`agy`)** | Interactive conversation & Lead Architect session | Always: architectural decisions, strategy, milestone gates. |
| **`/forget-team` + `Herdr`** | Multi-worktree tournament (`w1..w4`) + `judge_rust.sh` | Whenever writing or optimizing code against a concrete metric. |
| **`dspy.RLM` (`rlm_probe.py`)** | Standalone CLI tool (`excavate` & `distill`) | Whenever mining massive dumps/legacy code or distilling post-mortem failures headlessly. |
| **Full DSPy Optimizers (`MIPROv2`)** | Offline prompt compiler | Rarely: only when tuning internal signatures offline. |

*For deep architectural context, token-economics breakdowns, and biological analogies, see [`references/ARCHITECTURE.md`](./references/ARCHITECTURE.md).*

---

## 2. Pre-Flight Gatekeeper (Mandatory Before Phase 1)

As the **Lead Agent (Cockpit)**, verify these four invariants before spawning any worker:
1. **Protect Your Own Context Window:** NEVER read raw database dumps, large legacy source trees, or full multi-worktree compiler logs directly into the Lead session. Delegate all bulk reading to `scripts/rlm_probe.py`.
2. **Shared Rust Target Cache:** Export a single shared target directory so all 4 worktrees reuse compiled dependencies without lock contention during sequential judging:
   ```bash
   export CARGO_TARGET_DIR="/tmp/$(basename "$PWD")-shared-target"
   ```
3. **Anti-Goodhart Fixture Lock:** Before starting a tournament, compute and store the SHA-256 hash of the test suite and binary fixtures:
   ```bash
   sha256sum tests/**/* > /tmp/judge_fixtures.sha256
   ```
   The External Judge (`judge_rust.sh`) MUST verify `sha256sum -c /tmp/judge_fixtures.sha256` before scoring so workers cannot pass by deleting or stubbing tests.
4. **Epigenetic Cap:** The section between `<!-- EPIGENETIC_START -->` and `<!-- EPIGENETIC_END -->` in `AGENTS.md` MUST NEVER exceed **15 lines**.

---

## 3. Execution State Machine

### PHASE 1: RLM Excavation (`excavate`) — *Skip if `specs/<task>.md` & fixtures already exist*
When facing a massive external environment (e.g., a multi-gigabyte SQL dump or legacy codebase), invoke the RLM Excavator from the Lead shell:

```bash
uv run ~/.agents/skills/epigenetic-loop/scripts/rlm_probe.py excavate \
  --source "<path_to_sql_dump_or_legacy_repo>" \
  --task "<one_sentence_topic_of_concern>" \
  --out-spec "specs/${TASK_ID}.md" \
  --out-fixture "tests/fixtures/${TASK_ID}_torture.bin"
```
* **Gate Check:** Verify `specs/${TASK_ID}.md` contains explicit input/output byte contracts and `tests/fixtures/${TASK_ID}_torture.bin` contains framed `<corrupted_input_hex>\t<expected_healed_output_hex>\n` records on disk.

---

### PHASE 2: Mode A — Solo Ralph Bootstrap (Greenfield Initialization)
**NEVER launch a 4-pane `/forget-team` tournament on an uncompiled or empty module.**
1. Copy `references/AGENTS_EPIGENETIC_STUB.md` to `./AGENTS.md` in the repository root if not present.
2. Spawn **1 Herdr worker pane (`w0`)** tasked strictly with scaffolding:
   * Module files, public structs, and exact Rust trait/function signatures matching `specs/${TASK_ID}.md`.
   * Wiring the integration test harness to read `tests/fixtures/${TASK_ID}_torture.bin` (splitting on `\n` and `\t`, decoding hex pairs into `&[u8]`, and asserting parser output byte equality against the expected healed payload).
   * Leaving the core algorithmic body as `todo!()` or a minimal baseline.
3. Run `cargo test --no-run` from the Lead shell using `$CARGO_TARGET_DIR` to warm the dependency cache and verify the test harness compiles cleanly.
4. Commit this baseline as `<best_sha>`, record the baseline score (`0.0`), and **immediately kill pane `w0` (`herdr pane close`)**.

---

### PHASE 3: Mode B — The Herdr Amnesia Tournament (Invoke `/forget-team`)
Invoke the `/forget-team` workflow across 4 isolated git worktrees (`.forget/w1` .. `.forget/w4`) checked out at `<best_sha>`, applying these **Rust-Specific Overrides**:

1. **Orthogonal Hypothesis Seeding:** Do not send identical prompts to all 4 panes. Assign each worker (`w1..w4`) a distinct algorithmic vector in its launch prompt while sharing the same `AGENTS.md` and `specs/${TASK_ID}.md`:
   * `w1`: Direct combinator composition (`winnow` zero-copy slices).
   * `w2`: State-machine / lookahead boundary recovery.
   * `w3`: Inside-out recursive healing / edge-case defense.
   * `w4`: Wildcard / minimal-allocation fast path (`bstr` / `memchr`).
2. **Two-Stage Backpressure (Worker vs. Judge Split):**
   * **Stage 1 (Inside Worker Panes `w1..w4`):** Workers ARE permitted to run fast type-checking to resolve Rust borrow/lifetime errors before finishing their turn:
     ```bash
     CARGO_TARGET_DIR="/tmp/$(basename "$PWD")-shared-target" cargo check --quiet --message-format=short | head -n 15
     ```
     Workers are **FORBIDDEN** from running `cargo bench`, modifying `tests/`, or running `git commit`.
   * **Stage 2 (External Judge in Lead Shell ONLY):** Once workers complete a turn (40–120 lines changed), the Lead shell evaluates `w1..w4` **sequentially** against the shared `$CARGO_TARGET_DIR`:
     ```bash
     for wt in .forget/w1 .forget/w2 .forget/w3 .forget/w4; do
       ~/.agents/skills/epigenetic-loop/scripts/judge_rust.sh "$wt" "/tmp/judge_fixtures.sha256"
     done
     ```
     `judge_rust.sh` outputs a single JSON line per worktree:
     `{"worktree": "w2", "valid": true, "pass_rate": 0.94, "ns_per_op": 412.0, "score": 94.58}`
3. **Peer Borrowing Within a Generation (Turns 2–4):**
   * Follow `/forget-team` peer-diff rules: workers may inspect sibling breakthroughs exclusively via `git diff <best_sha>..forget-w<1..4> -- src/`. Zero conversational cross-talk.

---

### PHASE 4: The Epigenetic Wipe (`distill` + Hard Reset)
Trigger a **Hard Reset** as soon as ANY of these conditions occur:
* Workers reach **4 turns** in the current generation.
* Edits shrink below **15 lines** per turn (anchoring plateau detected).
* A worker achieves a new high `<winning_sha>` that changes core data structures.

**Execute the Epigenetic Reset Sequence in exact order:**
1. **Commit Winning Genome:** In the highest-scoring valid worktree, commit the winning changes and update `<best_sha>`. If `pass_rate == 1.0` and latency targets are met, **HALT TOURNAMENT — MISSION COMPLETE**.
2. **Snapshot Previous Epigenetics:**
   ```bash
   cp AGENTS.md /tmp/AGENTS.md.prev_gen
   ```
3. **Run Headless Epigenetic Distillation (Zero Lead Context Pollution):**
   Invoke `rlm_probe.py distill` to inspect the failed/stalled diffs and compiler stderr across `w1..w4` and update the 15-line block in `AGENTS.md`:
   ```bash
   uv run ~/.agents/skills/epigenetic-loop/scripts/rlm_probe.py distill \
     --base-sha "$BEST_SHA" \
     --worktrees .forget/w1 .forget/w2 .forget/w3 .forget/w4 \
     --agents-md ./AGENTS.md \
     --max-lines 15
   ```
   *(Graceful Degradation Fallback: If `rlm_probe.py` is unavailable or errors out, the Lead Agent inspects ONLY `git diff --stat` and the final 5 lines of `judge_rust.sh` stderr to manually replace 1–2 stale lines inside the `<!-- EPIGENETIC_START -->` block).*
4. **Epigenetic Rollback Guardrail:** If the *entire* generation failed to compile or regressed below the previous generation's failure rate after an `AGENTS.md` update, restore `/tmp/AGENTS.md.prev_gen` before running `distill` again.
5. **Destroy Synaptic KV Caches:**
   * Close all 4 worker panes (`herdr pane close w1 w2 w3 w4`).
   * Reset all 4 worktrees to `<best_sha>` (`git reset --hard "$BEST_SHA"` and `git clean -fd`).
   * Sync the newly updated `AGENTS.md` into `.forget/w1..w4`.
   * Return to **Phase 3** and spawn fresh worker panes for Generation $N+1$.
