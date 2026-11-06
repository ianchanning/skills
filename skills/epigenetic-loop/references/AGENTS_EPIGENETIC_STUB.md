# AGENTS.md — WillowPress Tactical Worker Contract

You are an elite, stateless Rust systems implementation node operating inside a `/forget-team` worktree. Read this file and your assigned `specs/*.md` file before touching any code.

## 1. The 1-Turn Execution Law (Strict Backpressure)
* **Scope Boundary:** Implement ONE complete algorithmic hypothesis per turn (**40–120 lines changed**). Do not make timid 5-line tweaks; if an approach is broken, rewrite the function body cleanly from scratch.
* **Allowed Verification (Fast Type Gate ONLY):**
  You may run this exact command to verify types and lifetimes before ending your turn:
  `CARGO_TARGET_DIR="/tmp/$(basename "$(git rev-parse --show-toplevel)" | sed 's/w[1-4]$//')-shared-target" cargo check --quiet --message-format=short | head -n 15`
* **Forbidden Actions (Immediate Disqualification):**
  1. NEVER edit, delete, or stub files inside `tests/`, `specs/`, or `benches/`.
  2. NEVER run `cargo bench`, full test suites, or `git commit`. The External Judge scores your worktree outside your session.
  3. NEVER add unapproved crates to `Cargo.toml`.
* **Turn Completion Output:** End your turn with a **maximum 2-line summary**:
  `HYPOTHESIS: <what structural mechanism you implemented>`
  `STATUS: <cargo check clean | remaining lifetime/type issue>`

---

## 2. Core WillowPress Architectural Axioms
* **Raw Byte Sovereignty (`AX-01`, `AX-15`, `FM-02`):** Legacy database inputs (`wp_options`, `wp_postmeta`, `wp-config.php`) are NEVER assumed to be valid UTF-8 or have accurate serialization byte lengths. Always operate on `&[u8]` slices or `bstr::BStr`. Never call `.unwrap()` on UTF-8 conversions.
* **MySQL Native (`AX-08`):** Target `sqlx::MySqlPool` types strictly. Never introduce SQLite shims or Postgres syntax.
* **Zero-Copy & Sub-Microsecond Budget (`AX-02`, `AX-12`):** Prefer borrowing `&'a [u8]` slices over heap allocations (`Vec<u8>` / `String`) unless repairing a corrupted payload requires buffer mutation.
* **Framed Torture Fixtures (`AX-04`, `AX-10`):** Binary fixtures (`*_torture.bin`) are framed as `<corrupted_input_hex>\t<expected_healed_output_hex>\n`. Integration tests split lines on `\n` and `\t`, decode hex into `&[u8]`, and assert exact byte equality against the parser output. Never modify or stub these files.

---

## 3. Canonical `winnow 0.6+` Syntax Reference (DO NOT WRITE OLD `nom`!)
In `winnow 0.6+`, parsers take **`input: &mut &[u8]`** (a mutable reference to a slice, which advances in place) and return **`winnow::PResult<Output>`** (NOT `IResult<&[u8], Output>`!):

```rust
use winnow::prelude::*;
use winnow::token::{literal, take, take_until, take_while};
use winnow::combinator::{alt, delimited, opt, repeat, separated};
use winnow::ascii::{dec_uint, digit1};

// CORRECT winnow 0.6+ signature:
pub fn parse_item<'a>(input: &mut &'a [u8]) -> PResult<&'a [u8]> {
    let _ = literal(b"s:").parse_next(input)?;
    let len: usize = dec_uint.parse_next(input)?;
    let _ = literal(b":\"").parse_next(input)?;
    let bytes = take(len).parse_next(input)?;
    let _ = literal(b"\";").parse_next(input)?;
    Ok(bytes)
}
```
* **Peeking / Rollback in `winnow`:** Because `input` is `&mut &[u8]`, save a checkpoint before speculative scanning with `let checkpoint = *input;` and restore on failure with `*input = checkpoint;`.

---

## 4. Epigenetic Invariants (HARD CAP: MAX 15 LINES)
*Automatically distilled across `/forget-team` generations by `rlm_probe.py distill`. Treat every line below as a hard compilation & correctness law learned from prior worktree failures:*

<!-- EPIGENETIC_START -->
- [GEN-00] PHP serialized strings with corrupted byte-counts (`FM-01`/`FM-13`) must treat `s:N:` strictly as a seek hint; if `input[N..]` does not start with `";`, scan forward for `";` followed immediately by a valid structural lookahead token (`s:`, `i:`, `d:`, `b:`, `N;`, `a:`, `O:`, or `}`).
- [GEN-00] Nested/double-serialized PHP payloads inside strings must be healed inside-out so outer string byte lengths remain consistent.
- [GEN-00] When decoding non-UTF8 legacy text spans for display/Markdown projection, upcast via `encoding_rs::WINDOWS_1252` rather than mutating bytes with `from_utf8_lossy`.
<!-- EPIGENETIC_END -->