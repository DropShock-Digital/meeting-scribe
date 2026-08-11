# Test strategy and requirements-to-evidence traceability

| Requirement | Test/evidence |
|---|---|
| FR-01 explicit confirmation + allowlist | API unit tests for denied and accepted creation |
| FR-02 append-only events | lifecycle tests check event order |
| FR-04 validated transcript | payload validation tests |
| FR-05 deterministic exports | export snapshot/contract test |
| FR-06 finalization | post-finalization ingest rejection test |
| FR-07 disabled Discord | configuration/adapter test |
| NFR-03 secret safety | repository safety scan + health response test |
| NFR-04 accessibility floor | static markup semantic assertions and manual browser check |
| NFR-05 Docker | `docker compose config`, image build, health smoke |
| NFR-06 truthful degradation | adapter failure/state test |

## Test levels
Unit: domain state machine and rendering. Integration: FastAPI + temporary SQLite. Configuration: Compose and public-repo safety scan. Manual: local browser console and optional Discord test guild. The latter remains explicitly unverified until run by an authorized operator.
