---
name: dan-luu-testing
description: skill that attempts to encode some information Dan Luu has in his head about testing
---

- Think about areas likely to have subtle bugs before implementing; for each, state likely mistakes and plausible alternative interpretations, then come up with a check where the results differ (prefer asymmetric / boundary examples on both sides of the boundary)
- After implementing, for high risk areas, independently re-derive the result without context on production code and compare (fresh context, do not re-use helper functions)
- When feasible, use property-based testing or randomized inputs to try to explore the space, minimizing effort on no-panic or no-crash randomization
- When randomizing, lean towards inputs that will explore interesting state and code paths (don't just naively randomize inputs that all fall into the same error paths); this may require structured random inputs
- If you're unsure about details, use independent reasoning to check what's correct (fresh context, do not re-use helper functions)
