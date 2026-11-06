---
name: hard-won-wisdom
description: A repository of "Rapid Unscheduled Disassemblies" (RUDs) and their surgical fixes, providing a historical record of failures and systemic fortifications to prevent recurrence.
---

# Hard-Won Wisdom (The RUD Ledger)

This skill is a repository of "Rapid Unscheduled Disassemblies" (RUDs)—failures encountered during development—and the surgical corrections required to prevent their recurrence. It is a living document of technical scars and systemic fortifications.



## Trigger Conditions
Invoke this skill when:
- Performing bulk file operations via shell scripts.
- Using `git ls-files` or other git plumbing commands for automation.
- Implementing backup or migration logic within a repository.
- Encountering "inexplicable" shell behavior.

## The Codex of Lessons

### 1. The Space Gremlin (Word Splitting)
**The Failure:** Using `for file in $(git ls-files ...)` leads to "Rapid Unscheduled Disassembly" when filenames contain spaces. The shell splits the filename into multiple arguments, causing `mv`, `cp`, or `rm` to fail.
**The Fortification:** ALWAYS use `while read -r file; do ... done` when processing lists of files from a command output.
**Example:**
```bash
git ls-files --others --exclude-standard | while read -r file; do
    # Surgical operation here
done
```

### 2. The Recursive Backup Void (Untracked Nesting)
**The Failure:** Moving untracked files into a new directory *inside* the same repository without ignoring that directory. `git ls-files --others` will see the backup directory as untracked, leading to a fractal loop where the backup is backed up into itself.
**The Fortification:** 
- Move the backup directory outside the git root.
- OR, immediately add the backup directory to `.gitignore`.
- OR, use a specific exclusion pattern in the `ls-files` command.

### 3. The RUD Philosophy
**The Wisdom:** Failure is not a bug; it is telemetry. A "Rapid Unscheduled Disassembly" is simply a high-velocity reveal of a systemic weakness. Document the RUD, apply the surgical fix, and forge a permanent fortification.

### 4. The Registry Purge Word Split (Lesson 1 Recurrence, 2026-10-24)
**The Failure:** During the GHCR legacy-tag purge of `fpl-dominator-runner`, the id list was consumed with `for LINE in $IDS` (unquoted expansion → IFS word-split). The list was two columns per line (`<version_id> <digest>`); iteration 1 consumed the bare numeric id (accidentally correct, HTTP 204), iteration 2 consumed the *digest name* as the id → `HTTP 422: The version_id parameter must be an integer` → hard stop after 1 deletion.
**The Fortification:** `for x in $LIST` must never be used for structured records — Lesson 1 applies exactly as much to API id lists as it does to filenames. ALWAYS `while read -r ID NAME; do ...; done <<< "$LIST"`. Bonus fortification: make deletion loops idempotent (treat HTTP 404 as success) so a partial RUD can be safely re-run.
**The Telemetry (registry forensics learned the hard way):**
- The GHCR REST packages API tracks **every manifest digest as its own version** — index manifests, image manifests, and platform-less attestation manifests are all separate rows; a single attested push yields 3 versions.
- `metadata.container.tags` is an **array of tag-name strings**, not objects (jq `index("latest")` works; `map(.name)` fails with "Cannot index string with string").
- Deleting the manifest version that a tag references **removes the tag** from the registry.

---
(⊕) (⇌) (⁂)
