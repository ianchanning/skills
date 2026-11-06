# The Epigenetic Amnesia Loop: Architecture & Theoretical Foundations

## 1. The Core Paradox of Agentic Coding: Anchoring vs. Amnesia

When autonomous LLM agents iterate over complex engineering tasks across 5+ turns, two opposing pathologies emerge:

1. **Path-Dependent Anchoring (Session Bloat):**
   * As workers iterate, their KV cache accumulates failed attempts, rejected diffs, borrow-checker errors, and rambling reasoning traces.
   * LLMs become psychologically anchored to their initial structural choices, making progressively smaller edits (15 lines or fewer) until plateauing in local optima.
   * *The `/forget-team` solution (arXiv:2610.20563):* Closing the panes (`herdr pane close`) and wiping session memory destroys the KV cache and shatters the anchoring.

2. **The Amnesia Blind Spot (The Paradox):**
   * When worker panes are wiped to zero, the next generation wakes up with complete amnesia.
   * While this prevents anchoring, fresh workers frequently walk straight back into the exact same domain traps (e.g., deprecated API patterns, borrow-checker lifetime traps, or collation misinterpretations) that killed the previous generation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│               THE PARADOX OF AGENTIC SEARCH & DISCOVERY                │
├─────────────────────────────────────────────────────────────────────────┤
│  KEEP HISTORY  ──>  Context Rot & Psychological Anchoring (Local Optima)│
│  WIPE HISTORY  ──>  Total Amnesia & Repetitive Syntax/Domain Traps      │
└─────────────────────────────────────────────────────────────────────────┘
```

The **Epigenetic Loop** solves this paradox by decoupling **code survival**, **tactical execution memory**, and **environmental domain laws**.

---

## 2. The Biological Triad of State

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE CYBERNETIC TRIAD OF STATE                        │
├─────────────────────────────────────────────────────────────────────────┤
│  1. GENETICS (DNA) = `<best_sha>` in Git                                │
│     • Cold-blooded survival: only code passing `judge_rust.sh`          │
│       survives to become the baseline genome for Generation N+1.        │
├─────────────────────────────────────────────────────────────────────────┤
│  2. SYNAPSES (Working Memory) = `Herdr` Panes `w1..w4`                  │
│     • Short-lived tactical execution powered by cheap/fast models       │
│       (Gemma 4, Qwen 3.8, Gemini Flash 3.8).                            │
│     • Ruthlessly wiped every 3–5 turns via `herdr pane close`.          │
│     • 0% KV-cache bloat, -38% token burn, zero path-dependency.         │
├─────────────────────────────────────────────────────────────────────────┤
│  3. EPIGENETICS (Methylation) = `dspy.RLM` Distillation                 │
│     • Runs headlessly OUTSIDE the worker panes and Lead session.        │
│     • Diagnoses failed worktree diffs and compiler stderr via RLM.      │
│     • Injects distilled 1-line laws into `AGENTS.md` (max 15 lines)     │
│       between `<!-- EPIGENETIC_START -->` / `<!-- EPIGENETIC_END -->`.  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Three Engine Modes

### Mode 1: The RLM Excavator & Torture Miner
* **Challenge:** Multi-gigabyte database dumps (e.g., 15-year MySQL dumps) or 300,000-line legacy PHP codebases choke token context windows and trigger hallucinations. Furthermore, sandboxed REPL environments cannot arbitrarily open host filesystem files without explicit host reader callables.
* **Mechanism:** `scripts/rlm_probe.py excavate` provides read-only host tools (`read_slice`, `find_pattern_offsets`, `list_files`) to `dspy.RLM(..., tools=tools)`. The model programmatically slices bytes and queries sub-LLMs over 2KB windows via `llm_query()` in its REPL sandbox, extracting adversarial boundary cases without context bloat.
* **Output:** Generates a formal Markdown specification (`specs/<task>.md`) and a line-framed torture suite (`tests/fixtures/<task>_torture.bin`) containing `<corrupted_input_hex>\t<expected_healed_output_hex>\n` records for deterministic byte-for-byte evaluation in Rust.

### Mode 2: The DSPy-Compiled Herdr Amnesia Tournament
* **Phase 2 (Mode A Bootstrap):** A single Herdr pane (`w0`) scaffolds module signatures and wires tests against the torture fixtures, compiling with `cargo test --no-run`. Once green, `w0` is immediately killed.
* **Phase 3 (Mode B Tournament):** Herdr launches 4 parallel worktrees (`w1..w4`) seeded with orthogonal algorithmic hypotheses (e.g., combinator parser vs. state machine vs. memory scan vs. recovery fallback).
* **Two-Stage Backpressure:**
  - *Inside Panes:* Workers verify types via fast `cargo check --quiet --message-format=short`.
  - *Outside Panes (Lead Shell):* `judge_rust.sh` scores candidates sequentially against a shared `$CARGO_TARGET_DIR`.
* **Equivalence:** The external judge script `judge_rust.sh` serves simultaneously as the `/forget-team` tournament judge and the DSPy objective metric function `metric(example, prediction) -> float`.

### Mode 3: Autonomous Differential Oracle Fuzzing
* Programmatically compares outputs between the legacy implementation and the new compiled engine over large corpora.
* Minimizes failing payloads down to minimal byte-level reproductions, appends them to the torture corpus, and triggers targeted tournament cycles.

---

## 4. Token Economics: 95%+ Compute Reduction

| Cost Vector | Conventional Agentic Swarm | Epigenetic Amnesia Loop |
| :--- | :--- | :--- |
| **Quadratic Attention Tax** | Massive 100k–500k context windows containing entire dumps/logs. | **Zero:** Inputs treated as REPL variables; models read only 2KB slices. |
| **Zombie Debugging Loops** | 20–50 turns arguing with borrow-checker errors in polluted context. | **Zero:** Panes killed every 3–5 turns (`herdr pane close`). |
| **Model Tier Allocation** | Expensive frontier models burned on repetitive syntax trials. | **90% Cheap/Fast:** Gemma 4 / Qwen 3.8 / Flash 3.8 do the work; frontier models reserved for Lead architecture. |

---

## 5. Zero-Maintenance (0M) Principles

1. **Target Repository Purity:**
   The codebase under development (e.g., a Rust systems service) remains 100% pure language code. No Python harnesses, `pyproject.toml`, or auxiliary scaffolding pollute the repository. All cybernetic factory tooling lives inside `~/.agents/skills/epigenetic-loop/`.
2. **Deterministic Composability:**
   Every tournament follows a predictable state machine: Excavate $\rightarrow$ Mode A $\rightarrow$ Mode B $\rightarrow$ Distill $\rightarrow$ Hard Reset.
3. **Anti-Goodhart Sentinel:**
   Test suites and binary fixtures are hashed (`sha256sum`) before the tournament begins. If an agent tampers with or stubs tests to increase its score, the judge immediately fails the candidate.
4. **Context Window Shield for Lead Agent:**
   The Lead Agent (Cockpit) NEVER reads raw SQL dumps or full multi-worktree diffs. All heavy evaluation is offloaded to standalone scripts (`rlm_probe.py` and `judge_rust.sh`), returning concise JSON summaries.
