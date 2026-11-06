# Engineering Brief: Scaling Discovery Requires Forgetting
**Summary of [arXiv:2610.20563](./main.tex) & Practical Guide to the `forget-team` Herdr Workflow**

Why long AI coding sessions plateau early—and how periodic session resets ("forgetting") combined with parallel Git worktrees improve code quality while reducing token spend by 38%.

---

## 1. Myth vs. Reality (Benchmark Findings)

| Common Assumption | Actual Empirical Finding |
| :--- | :--- |
| **Myth 1:** Only reset an AI session when the context window hits 100%. | **Reality:** Agent output degrades after **~5–10 turns** (~15% context) because failed attempts anchor the model. |
| **Myth 2:** Cheap KV-Cache reads make long sessions practically free. | **Reality:** Periodically wiping the session is **38% cheaper per round** and yields **6.5x higher score gains**. |

---

## 2. The Two Core Paradoxes Explained

### A. Cost Analysis: Why Resetting Costs 38% Less ($15.32 vs. $24.67)
The study evaluated models with aggressive KV-cache compression (where cached reads cost ~20x less than fresh input, e.g., `10` vs. `200` credits). Even with discounted cache reads, long sessions remain more expensive due to three factors:
1. **Tool-Loop Multiplier:** 1 user turn triggers ~10 internal tool calls, re-reading cached context repeatedly alongside fresh `200`-credit file inputs.
2. **66.2% Unproductive Turns:** In long single-agent sessions, **532 of 763 turns** produced zero code edits while still billing high-cost (`1,000`-credit) output tokens to declare a false plateau.
3. **Same 30 Turns, Half the Bill (Table 3):** Continuing an old chat for 30 turns cost **$24.67** (and stalled out), whereas wiping the chat cost **$15.32** and delivered a **6.5x larger benchmark jump**.

### B. Scope Control: Why Agents Don't Blow Context Mid-Commit (Appendix B)
1. **Start From a Working Baseline:** Never run a 4-agent parallel workflow on an empty repository. Build the initial working draft with a single agent first.
2. **One Hypothesis = One Commit:** Each worker turn targets a single focused improvement (40–100 lines), avoiding sprawling multi-file rewrites.
3. **External Verification (The Judge):** Workers edit code and stop. The lead process runs tests/benchmarks **externally** so stack traces do not bloat worker context.

---

## 3. Two Practical Workflows (When to Use What)

| Workflow | Best For | How to Run It |
| :--- | :--- | :--- |
| **Mode A: Solo Reset** *(1 Agent)* | Greenfield features, normal coding, routine bug fixes | Work with **1 agent**. Each time a milestone passes tests (~15–20 mins): **1.** `git commit` the working code. **2.** Close the agent pane (`prefix + x`). **3.** Open a fresh agent pane. Progress stays in Git; debugging history is discarded. |
| **Mode B: 4-Agent Tournament** *(`forget-team`)* | Optimizing benchmarks, fixing stubborn test suites, breaking plateaus | Split your budget across **4 parallel agents in 4 Git worktrees** for short rounds (3–5 turns). Keep the single **Winning Commit**, close all 4 panes, and start Round 2 fresh from that winner. |

---

## 4. How the 4-Step Tournament Cycle Works

1. **Step 1 — Isolation (4 Git Worktrees):** All 4 agents start from the exact same baseline commit in separate folders (`.forget/w1..w4`) and explore 4 different approaches.
2. **Step 2 — Diff Sharing (Inspect Peer Commits):** Agents never chat with one another. They inspect peers' code via `git diff`, adopting useful patterns with zero chat bloat.
3. **Step 3 — Evaluation (External Benchmark):** The Lead harness runs the test/benchmark suite on all 4 folders outside worker context. The highest-scoring commit becomes the **Winning Commit**.
4. **Step 4 — Session Reset (Close & Re-Seed):** All 4 agent panes are closed (`herdr pane close`). All 4 worktrees are reset to the **Winning Commit**, and 4 fresh sessions begin Round 2.

---

## 5. Empirical Metrics From the Paper

| Metric | Observed Number | What It Means |
| :--- | :--- | :--- |
| **Edit Scope Decay** | **150 → 6 Lines** | **Context Anchoring:** As failed attempts accumulate in session history, agents become conservative, shrinking median edits from ~150 lines to 6 lines. |
| **Unproductive Spend** | **66.2% Idle Turns** | **Premature Plateaus:** In continuous single-agent runs, 66.2% of budget was spent on turns where the agent declared a "practical limit" and made no edit. |
| **Reasoning Recovery** | **9.4k vs. 2.9k Tokens** | **Post-Reset Reasoning:** Starting a fresh session on the Winning Commit restores **3.2x deeper reasoning effort** and ~40-line median edits. |

---

## 6. Glossary of Terms

* **Baseline Commit:** The initial working Git commit that compiles and runs before starting an optimization round.
* **Candidate Commit:** A single focused code change produced by one worker agent during a turn.
* **External Judge:** An automated verification command (e.g., `bun test`, `bun run bench`) executed outside the worker agent's session.
* **Winning Git Commit ("Best Candidate"):** The candidate commit that achieves the best score from the External Judge at the end of a round. All other 3 attempts are discarded.
* **Git Worktrees (`.forget/w1..w4`):** A built-in Git feature allowing multiple working directories to share one repository so 4 agents can edit in parallel without file collisions.
* **Session Reset ("Forgetting"):** Closing the active agent panes (`herdr pane close`) to clear KV-cache and failure history while resetting all worktrees to the Winning Git Commit.

---

## 7. Quick Trigger in Herdr

~~~text
Use forget-team for 3 rounds to optimize src/parser.ts — judge each candidate externally with 'bun run bench' and keep the fastest commit.
~~~
