# Requirements Traceability Register

Status vocabulary: NOT_STARTED, IN_PROGRESS, PARTIAL, PASS, FAIL, BLOCKED, UNKNOWN. PASS requires linked, reproducible evidence.

| Requirement | Statement | Design reference | Verification method | Status |
|---|---|---|---|---|
| CQ-REQ-001 | Android and web use one versioned API contract | ARCHITECTURE.md | OpenAPI contract and client contract tests | NOT_STARTED |
| CQ-REQ-002 | XP and rewards are server-authoritative and idempotent | ADR-0003 | Replay, duplicate and transaction tests | NOT_STARTED |
| CQ-REQ-003 | Missions are versioned and schema validated | ARCHITECTURE.md | Positive/negative schema tests | NOT_STARTED |
| CQ-REQ-004 | Offline attempts require server validation | ARCHITECTURE.md | Replay, stale-version and sync tests | NOT_STARTED |
| CQ-REQ-005 | Core learning works without external AI | PRODUCT-BASELINE.md | Disable AI and run acceptance suite | NOT_STARTED |
| CQ-REQ-006 | MVP makes no unsupported device-protection claims | SECURITY-AND-PRIVACY.md | Product copy and feature review | NOT_STARTED |
| CQ-REQ-007 | Learner data is access-controlled and minimised | SECURITY-AND-PRIVACY.md | Threat review and cross-account tests | NOT_STARTED |
| CQ-REQ-008 | Future labs are isolated and fail closed | SECURITY-AND-PRIVACY.md | Deferred lab isolation adversarial suite | DEFERRED |

For every approved requirement, add implementation paths, named test cases, CI run URL and commit SHA when implemented. A design reference alone is not implementation evidence.
