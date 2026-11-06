## [2026-07-02] ingest | Sovereign Domain Migration Refactor
- **Event**: Refactored `Main.elm` to federated domain architecture.
- **Failure**: E2E tests failed due to state loss in `Auth` and `Archive` models.
- **Fix**: Replaced "clever" record updates with explicit model reconstruction.
- **Result**: All 28 Fortress scenarios passed.
