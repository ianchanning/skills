---
name: forget-team
description: Run a 4-agent parallel git-worktree amnesia tournament in Herdr with periodic session resets ("forgetting"), cross-generational Epigenetic Distillation, and an External Judge. Use when optimizing code or pruning tests against a measurable metric, benchmark, or coverage-gated suite, when a single agent plateaus or blows through its context window, or when the user mentions "forget-team", "amnesia tournament", "epigenetic loop", or "Scaling Discovery Requires Forgetting".
---

# `forget-team` // 4-Agent Amnesia Tournament Protocol (Requires `herdr` skill)

You are the **Lead Reducer & External Judge** (based on *Scaling Discovery Requires Forgetting*, arXiv:2610.20563), see [`main.tex`](./references/main.tex). Never do heavy feature coding in your own session. Your job is to orchestrate 4 stateless worker agents in isolated Git worktrees, evaluate their edits externally, and wipe their session memory between rounds.

Consult [`BRIEF.md`](./references/BRIEF.md) for a quick 2-page overview of the paper.

---

## 0. Pre-Flight Gatekeeper (Check Before Spawning!)

Before splitting a single Herdr pane, verify these 4 laws:
1. **Clean Baseline Commit Exists:** Run `git status --porcelain`. If the working tree is dirty or the repo is empty/greenfield, **STOP**. Tell the user: *"Commit a working baseline first, or use Solo Forget (1 agent + close pane after each milestone) for greenfield work."*
2. **Measurable Target + Anti-Goodhart Gate Exists:** Verify the task optimizes a monotonic scalar score (`<score>`, e.g., throughput, latency, SLOC, failing-test count) guarded by a **Hard Invariant Gate** (e.g., 100% tests pass, zero statement coverage drop, minimum test-definition floor, linter clean).
   * If the goal is subjective/qualitative (*"clean up architecture"*, *"make UI prettier"*), **STOP** and use 1 agent.
   * If the user gives a qualitative refactoring goal (e.g., *"simplify tests"*), **STOP before spawning**, propose a concrete `Hard Gate + Scalar Score` External Judge to the user, and confirm it first so workers cannot reward-hack the metric (e.g., deleting valid tests to lower SLOC).
3. **External Judge Command Runs in Lead Shell:** You must have a single automated command/script that returns `{valid: bool, score: number}` in seconds without polluting worker context or causing shared-resource collisions (e.g., concurrent Postgres `DROP SCHEMA` teardowns).
4. **One Hypothesis = One Turn:** Keep worker prompts scoped to a single surgical improvement (40–150 lines) per turn so workers never blow their context mid-edit.
5. **Epigenetic Memory Channel (`AGENTS.md`):** Verify an `AGENTS.md` file exists (or include an Invariants block in the worker prompt) to hold cross-generational invariants (max 15 lines). This solves the amnesia paradox: workers forget failed code attempts, but distilled domain/syntax rules persist across wipes. (See `/epigenetic-loop` for automated RLM-driven distillation).

---

## 1. Setup Round (4 Worktrees + 4 Herdr Panes)

1. Record the starting baseline SHA (`<best_sha>`) and run the **External Judge** once to record `<best_score>`.
2. Create 4 isolated Git worktrees (add `.forget/` to `.git/info/exclude` so it stays untracked):

```bash
grep -qxF '.forget/' .git/info/exclude || echo '.forget/' >> .git/info/exclude
for i in 1 2 3 4; do
  git worktree add -B forget-w$i .forget/w$i <best_sha>
  [ -d .venv ] && ln -s "$PWD/.venv" ".forget/w$i/.venv"
done
```

3. Spawn 4 background worker panes in Herdr (2x2 grid) and start Copilot with `--reasoning-effort max` in each:

```bash
# Repeat for i in 1..4 (split right then down for a 2x2 grid):
herdr pane split --current --direction right --cwd "$PWD/.forget/w$i" --no-focus
herdr agent start w$i --kind copilot --pane <pane_id> -- --reasoning-effort max
```

---

## 2. The Turn Loop (3 to 5 Proposals Per Round)

For each turn in the current round, send all 4 workers (`w1..w4`) this exact constraint-bounded prompt via `herdr agent prompt w$i "<prompt>"`:

```text
# Task
<User's optimization/fix goal>
Current best commit: <best_sha> (Score: <best_score>).
Peer branches in this repo: forget-w1, forget-w2, forget-w3, forget-w4.

# Strict Rules
1. If past Turn 1, run `git diff <best_sha>..forget-w<1..4>` to inspect peer ideas and borrow any trick that helps.
2. Implement ONE bold, focused improvement (aim for 40-120 lines changed).
3. DO NOT run the benchmark/test suite yourself and DO NOT run `git commit`. Another process scores and commits your working tree after you stop.
4. Once your edit is saved to disk, immediately stop and summarize your change in 2 lines.
```

---

## 3. External Judge (Score Outside Worker Context)

1. Wait ~10s for all 4 workers to enter `working`, then wait for settled completion (`idle`/`done`):

```bash
sleep 10
for i in 1 2 3 4; do herdr agent wait w$i --timeout 600000 & done
wait
```

2. For each worktree `.forget/w1..w4` that has modified files:
   * Commit the candidate externally: `git -C .forget/w$i commit --no-verify -am "candidate: round $r turn $t w$i"`
   * Run the **External Judge** command from your Lead shell (never inside the worker pane!).
   * Record the score and commit SHA. If a candidate fails to compile or regresses, reset that worktree back to its previous working commit or pass the 3-line error summary into its next turn prompt.
3. Update `<best_sha>` and `<best_score>` whenever a candidate beats the current best.
4. **Judge Design Guardrails (Goodhart Prevention):**
   * **Penalize `ast.If`, never `ast.IfExp`:** If your score penalizes in-test branching, count `ast.If` statements only. Penalizing inline `ast.IfExp` ternaries with a high weight causes workers to replace 1-line ternaries with multi-line dictionary lookups (`{True: a, False: b}[cond]`).
   * **Line coverage ≠ output-column assertions:** Statement coverage (`--cov`) stays 100% when `df.rename(columns=map_rename)` executes even if assertions on specific output columns are dropped. When simplifying tests across sibling classes with separate methods (e.g. duplicate `normalize()` methods), verify each class retains assertions on its mapped output fields.

---

## 4. The "Forget" Wipe (End of Round Amnesia Reset & Epigenetic Distillation)

After 3–5 turns in a round (or as soon as worker edits shrink below 15 lines):

1. **The Epigenetic Distill Step (Run BEFORE Closing Panes):**
   * Before closing worker panes `w1..w4`, inspect the compiler errors, failed diffs, or syntax traps that killed or stalled the previous generation.
   * Distill at most **1–3 lines of compact domain/syntax invariants** (e.g., *"In winnow 0.6, parser input must be `&mut &[u8]`, not `&[u8]`"*) into the `## Epigenetic Invariants (Max 15 Lines)` section of `AGENTS.md` (replacing stale bullets if full).
   * *Automated/Headless Alternative:* If using the `/epigenetic-loop` skill, invoke `uv run ~/.agents/skills/epigenetic-loop/scripts/rlm_probe.py distill` to harvest telemetry and update `AGENTS.md` headlessly without polluting your Lead context window.
   * *Result:* Fresh workers wake up with a 100% clean KV cache (zero anchoring), while `AGENTS.md` preserves hard-won domain rules!

2. **Kill All 4 Worker Panes (Hard Amnesia):**

```bash
for p in <w1_pane> <w2_pane> <w3_pane> <w4_pane>; do
  herdr pane close "$p"
done
```

*(Never use `/compact`, `/new`, or `/quit`. Closing the panes destroys the KV cache and prevents Russian-doll session stacking.)*

3. **Re-Seed All 4 Worktrees to the Winning Commit:**

```bash
for i in 1 2 3 4; do
  git -C .forget/w$i reset --hard <best_sha>
  git -C .forget/w$i clean -fd
  # Sync the newly updated AGENTS.md with distilled epigenetic invariants
  [ -f ./AGENTS.md ] && cp ./AGENTS.md ".forget/w$i/AGENTS.md"
done
```

4. **Next Round or Finish:**
   * If more rounds remain: go back to **Step 1.3** and spawn 4 brand-new zero-context Copilot panes starting from `<best_sha>` (they will read the updated `AGENTS.md`).
   * If all rounds are complete: cherry-pick or fast-forward `<best_sha>` onto the user's main branch, run `git worktree remove --force .forget/w{1..4}`, and report the `<best_score>` improvement!
