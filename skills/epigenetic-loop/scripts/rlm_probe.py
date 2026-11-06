#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "dspy>=3.2.0",
#     "pydantic>=2.0",
# ]
# ///
"""
rlm_probe.py — Dual-Mode RLM Engine for the Epigenetic Amnesia Loop
Part of the /epigenetic-loop & /forget-team harness.

Subcommands:
  excavate : Explore large SQL dumps or legacy source files via dspy.RLM and
             generate specs + framed binary torture fixtures.
  distill  : Post-mortem failure analysis of Herdr worktrees (.forget/w1..w4)
             to update the ## Epigenetic Invariants block in AGENTS.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple

import dspy


# ==============================================================================
# Model & DSPy Telemetry Configuration
# ==============================================================================

def configure_dspy(model_name: str | None = None, sub_model_name: str | None = None) -> Tuple[dspy.LM, dspy.LM]:
    """
    Configures DSPy with a primary root LM and an optional lightweight sub_lm
    for recursive sub-calls inside the RLM REPL.
    """
    primary = model_name or os.getenv("RLM_MODEL", "gemini/gemini-2.5-flash")
    sub = sub_model_name or os.getenv("RLM_SUB_MODEL", "gemini/gemini-2.5-flash")

    lm = dspy.LM(primary, cache=True)
    sub_lm = dspy.LM(sub, cache=True) if sub != primary else lm
    dspy.configure(lm=lm)
    return lm, sub_lm


# ==============================================================================
# Host Slicing Tools for Sandboxed dspy.RLM
# ==============================================================================

def make_file_tools(source_path: Path) -> List[Callable]:
    """
    Constructs safe, read-only host tools passed into dspy.RLM so the sandboxed
    REPL can slice, inspect, and pattern-search gigabyte-scale inputs.
    """
    def read_slice(offset: int, length: int = 4096, rel_path: str = "") -> str:
        """Read up to 16KB of raw bytes (as latin1/repr) from target file (or file within source directory) at byte offset."""
        target = source_path
        if rel_path and source_path.is_dir():
            target = (source_path / rel_path).resolve()
            if not str(target).startswith(str(source_path.resolve())):
                return "Error: Path traversal outside source directory"
            if not target.is_file():
                return f"Error: File '{rel_path}' does not exist"
        elif not target.is_file():
            return "Error: Source is a directory; specify rel_path"

        length = min(length, 16384)
        with open(target, "rb") as f:
            f.seek(max(0, offset))
            return repr(f.read(length))

    def find_pattern_offsets(ascii_pattern: str, max_hits: int = 50, rel_path: str = "") -> List[int]:
        """Return byte offsets where ascii_pattern occurs in target file (or file within source directory)."""
        target = source_path
        if rel_path and source_path.is_dir():
            target = (source_path / rel_path).resolve()
            if not str(target).startswith(str(source_path.resolve())):
                return []
            if not target.is_file():
                return []
        elif not target.is_file():
            return []

        pat = ascii_pattern.encode("latin1", errors="ignore")
        hits: List[int] = []
        with open(target, "rb") as f:
            chunk_size = 1024 * 1024
            offset = 0
            while chunk := f.read(chunk_size):
                pos = 0
                while (idx := chunk.find(pat, pos)) != -1:
                    hits.append(offset + idx)
                    if len(hits) >= max_hits:
                        return hits
                    pos = idx + 1
                offset += len(chunk)
        return hits

    def list_files(max_files: int = 100) -> List[str]:
        """List relative file paths in source directory (if source is a directory)."""
        if not source_path.is_dir():
            return [source_path.name]
        files = []
        for p in source_path.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                files.append(str(p.relative_to(source_path)))
                if len(files) >= max_files:
                    break
        return files

    return [read_slice, find_pattern_offsets, list_files]


# ==============================================================================
# DSPy Signatures
# ==============================================================================

class ExcavateSignature(dspy.Signature):
    """
    Programmatically explore legacy database dumps or source trees inside a REPL.
    Identify structural edge cases, corrupted serialization boundaries, collation
    mismatches, or obscure syntax patterns, and synthesize both an explicit byte
    specification and reproducible binary test fixtures.
    """
    source_metadata: str = dspy.InputField(desc="File path, size, and structural preview of data environment")
    target_task: str = dspy.InputField(desc="The specific subsystem invariants or edge cases to hunt for")
    spec_markdown: str = dspy.OutputField(desc="Exhaustive Markdown spec with input/output byte contracts")
    fixture_pairs: list[tuple[str, str]] = dspy.OutputField(
        desc="List of (corrupted_input_hex, expected_healed_utf8_or_hex) pairs"
    )


class DistillSignature(dspy.Signature):
    """
    Examine the failed git diffs, compiler error logs, and judge metrics from
    a generation of 4 amnesiac worker nodes. Distill at most 1 to 3 compact,
    actionable domain/syntax invariants that explain why workers failed.
    """
    worktree_telemetry: str = dspy.InputField(desc="Combined git diffs, cargo check stderr, and judge scores")
    existing_invariants: str = dspy.InputField(desc="Current contents of the AGENTS.md epigenetic block")
    max_lines: int = dspy.InputField(desc="Maximum allowable lines in the distilled output block")
    updated_invariants_block: str = dspy.OutputField(desc="Complete updated bulleted list of invariants (strictly <= max_lines)")
    summary_for_lead: str = dspy.OutputField(desc="Strictly 2 lines summarizing root causes of worker stalls and new rules")


# ==============================================================================
# Subcommand: EXCAVATE
# ==============================================================================

def run_excavate(args: argparse.Namespace) -> None:
    source_path = Path(args.source).resolve()
    if not source_path.exists():
        sys.exit(f"[-] Error: Source target '{source_path}' does not exist.")

    out_spec = Path(args.out_spec).resolve()
    out_fixture = Path(args.out_fixture).resolve()
    out_spec.parent.mkdir(parents=True, exist_ok=True)
    out_fixture.parent.mkdir(parents=True, exist_ok=True)

    try:
        _, sub_lm = configure_dspy(args.model, args.sub_model)
    except Exception as exc:
        sys.exit(f"[-] Error configuring DSPy: {exc}\nEnsure valid API credentials (e.g. GEMINI_API_KEY) are set.")

    # Prepare file preview / metadata without loading gigabytes into RAM
    size_mb = source_path.stat().st_size / (1024 * 1024)
    preview = ""
    if source_path.is_file():
        with open(source_path, "rb") as f:
            head = f.read(2048)
            preview = head.decode("utf-8", errors="replace")
    else:
        file_list = [p.name for p in source_path.iterdir()][:20]
        preview = f"Directory listing (first 20): {', '.join(file_list)}"

    source_meta = f"Path: {source_path}\nSize: {size_mb:.2f} MB\nType: {'Directory' if source_path.is_dir() else 'File'}\nPreview:\n{preview}"

    print(f"[*] Initializing dspy.RLM Excavator on {source_path} ({size_mb:.2f} MB)...")

    # Pass sub_lm and host slicing tools into dspy.RLM
    tools = make_file_tools(source_path)

    try:
        rlm_excavator = dspy.RLM(
            ExcavateSignature,
            sub_lm=sub_lm,
            tools=tools,
            max_iters=15,
            max_llm_calls=25,
        )
        result = rlm_excavator(
            source_metadata=source_meta,
            target_task=args.task
        )
    except Exception as exc:
        sys.exit(f"[-] RLM Excavation failed: {exc}\nCheck model availability and credentials.")

    # Write out the generated specification
    with open(out_spec, "w", encoding="utf-8") as f:
        f.write(result.spec_markdown)
    print(f"[+] Spec written successfully to: {out_spec}")

    # Write line-framed hex pairs: <corrupted_input_hex>\t<expected_healed_output_hex>\n
    pairs = getattr(result, "fixture_pairs", None) or []
    written_count = 0
    with open(out_fixture, "wb") as f:
        for item in pairs:
            raw_hex = ""
            expected_hex = ""
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                raw_hex, expected_hex = str(item[0]), str(item[1])
            elif isinstance(item, str) and "\t" in item:
                parts = item.split("\t", 1)
                raw_hex, expected_hex = parts[0], parts[1]
            elif isinstance(item, str) and "," in item:
                parts = item.split(",", 1)
                raw_hex, expected_hex = parts[0], parts[1]

            r_clean = re.sub(r"[^0-9a-fA-F]", "", raw_hex).encode("ascii")
            e_clean = re.sub(r"[^0-9a-fA-F]", "", expected_hex).encode("ascii")
            if r_clean and e_clean:
                f.write(r_clean + b"\t" + e_clean + b"\n")
                written_count += 1

    print(f"[+] Framed binary torture fixtures written ({written_count} pairs) to: {out_fixture}")


# ==============================================================================
# Subcommand: DISTILL
# ==============================================================================

def run_distill(args: argparse.Namespace) -> None:
    agents_md_path = Path(args.agents_md).resolve()
    if not agents_md_path.exists():
        sys.exit(f"[-] Error: Target AGENTS.md '{agents_md_path}' does not exist.")

    try:
        _, sub_lm = configure_dspy(args.model, args.sub_model)
    except Exception as exc:
        sys.exit(f"[-] Error configuring DSPy: {exc}\nEnsure valid API credentials (e.g. GEMINI_API_KEY) are set.")

    # 1. Harvest telemetry across all worktrees outside the Lead chat window
    env = os.environ.copy()
    env.setdefault("CARGO_TARGET_DIR", "/tmp/willow-shared-target")

    telemetry_parts: List[str] = []
    for wt_str in args.worktrees:
        wt = Path(wt_str).resolve()
        if not wt.exists():
            continue

        # Git diff relative to base_sha
        diff_cmd = ["git", "-C", str(wt), "diff", args.base_sha, "--", "src/"]
        diff_proc = subprocess.run(diff_cmd, capture_output=True, text=True)
        diff_text = diff_proc.stdout[:8000]  # Cap per worktree to avoid runaway logs

        # Fast compiler check stderr with shared target dir
        check_cmd = ["cargo", "check", "--quiet", "--message-format=short"]
        check_proc = subprocess.run(check_cmd, cwd=str(wt), env=env, capture_output=True, text=True)
        check_err = check_proc.stderr[:4000]

        telemetry_parts.append(
            f"=== WORKTREE: {wt.name} ===\n"
            f"--- CARGO CHECK STDERR ---\n{check_err or 'Clean (No compile errors)'}\n"
            f"--- GIT DIFF ---\n{diff_text or 'No changes made'}\n"
        )

    all_telemetry = "\n".join(telemetry_parts)
    if not all_telemetry.strip():
        print("[!] No worktree telemetry discovered. Nothing to distill.")
        return

    # 2. Extract current epigenetic block (with graceful injection if missing)
    content = agents_md_path.read_text(encoding="utf-8")
    start_tag = "<!-- EPIGENETIC_START -->"
    end_tag = "<!-- EPIGENETIC_END -->"

    start_idx = content.find(start_tag)
    end_idx = content.find(end_tag)
    if start_idx == -1 or end_idx == -1:
        header = "## Epigenetic Invariants"
        h_idx = content.find(header)
        if h_idx != -1:
            end_of_header_line = content.find("\n", h_idx)
            if end_of_header_line == -1:
                end_of_header_line = len(content)
            content = (
                content[:end_of_header_line]
                + f"\n{start_tag}\n{end_tag}\n"
                + content[end_of_header_line:]
            )
        else:
            content += f"\n\n## Epigenetic Invariants (HARD CAP: MAX {args.max_lines} LINES)\n{start_tag}\n{end_tag}\n"
        start_idx = content.find(start_tag)
        end_idx = content.find(end_tag)

    current_invariants = content[start_idx + len(start_tag):end_idx].strip()

    # 3. Run dspy.RLM Distiller
    print("[*] Running dspy.RLM Post-Mortem Distiller...")
    try:
        rlm_distiller = dspy.RLM(
            DistillSignature,
            sub_lm=sub_lm,
            max_iters=15,
            max_llm_calls=25,
        )
        result = rlm_distiller(
            worktree_telemetry=all_telemetry,
            existing_invariants=current_invariants,
            max_lines=args.max_lines
        )
    except Exception as exc:
        sys.exit(f"[-] RLM Distillation failed: {exc}\nFallback: Inspect git diff --stat and cargo check stderr manually.")

    # 4. Enforce strict line cap (Anti-Fragile Guardrail)
    raw_lines = [line.strip() for line in result.updated_invariants_block.splitlines() if line.strip()]
    capped_lines = raw_lines[:args.max_lines]
    new_invariants_block = "\n" + "\n".join(capped_lines) + "\n"

    # 5. Programmatically splice back into AGENTS.md
    new_content = content[:start_idx + len(start_tag)] + new_invariants_block + content[end_idx:]
    agents_md_path.write_text(new_content, encoding="utf-8")

    print(f"[+] Successfully updated {agents_md_path} ({len(capped_lines)} lines, cap: {args.max_lines}).")
    print("--- LEAD SUMMARY ---")
    print(result.summary_for_lead.strip())


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="RLM Excavator & Distiller CLI")
    parser.add_argument("--model", type=str, default=None, help="Primary DSPy LM model identifier")
    parser.add_argument("--sub-model", type=str, default=None, help="Sub-call LM identifier for dspy.RLM REPL")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: excavate
    excavate_parser = subparsers.add_parser("excavate", help="Explore massive inputs and generate test corpus")
    excavate_parser.add_argument("--source", type=str, required=True, help="Path to SQL dump or codebase directory")
    excavate_parser.add_argument("--task", type=str, required=True, help="Description of invariants to hunt")
    excavate_parser.add_argument("--out-spec", type=str, required=True, help="Output markdown spec path")
    excavate_parser.add_argument("--out-fixture", type=str, required=True, help="Output binary fixture path")

    # Subcommand: distill
    distill_parser = subparsers.add_parser("distill", help="Distill failures into AGENTS.md invariants")
    distill_parser.add_argument("--base-sha", type=str, required=True, help="Base git commit SHA")
    distill_parser.add_argument("--worktrees", nargs="+", required=True, help="List of worktree paths")
    distill_parser.add_argument("--agents-md", type=str, default="./AGENTS.md", help="Path to AGENTS.md")
    distill_parser.add_argument("--max-lines", type=int, default=15, help="Hard ceiling on invariant lines")

    args = parser.parse_args()

    if args.command == "excavate":
        run_excavate(args)
    elif args.command == "distill":
        run_distill(args)


if __name__ == "__main__":
    main()
