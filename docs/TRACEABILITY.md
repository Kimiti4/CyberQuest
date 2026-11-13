# Requirements Traceability Register

Status vocabulary: NOT_STARTED, IN_PROGRESS, PARTIAL, DESIGN_ONLY, PASS, FAIL, BLOCKED, UNKNOWN. DESIGN_ONLY is not implementation evidence. PASS requires linked, reproducible evidence.

| Requirement | Statement | Design reference | Verification method | Status |
|---|---|---|---|---|
| CQ-REQ-001 | Android and web use one versioned API contract | API-CONTRACT.md; openapi/cyberquest-v1.json | OpenAPI structure/auth/idempotency tests; client contract tests pending | PARTIAL |
| CQ-REQ-002 | XP and rewards are server-authoritative and idempotent | ADR-0003; DATA-MODEL.md | Replay, duplicate and transaction tests | DESIGN_ONLY |
| CQ-REQ-003 | Missions are versioned and schema validated | ARCHITECTURE.md; DATA-MODEL.md | Positive/negative schema tests; runtime validation pending | PARTIAL |
| CQ-REQ-004 | Offline attempts require server validation | ARCHITECTURE.md; API-CONTRACT.md | Replay, stale-version and sync tests | DESIGN_ONLY |
| CQ-REQ-005 | Core learning works without external AI | PRODUCT-BASELINE.md | Disable AI and run acceptance suite | NOT_STARTED |
| CQ-REQ-006 | MVP makes no unsupported device-protection claims | SECURITY-AND-PRIVACY.md | Product copy and feature review | NOT_STARTED |
| CQ-REQ-007 | Learner data is access-controlled and minimised | SECURITY-AND-PRIVACY.md | Threat review and cross-account tests | NOT_STARTED |
| CQ-REQ-008 | Future labs are isolated and fail closed | SECURITY-AND-PRIVACY.md | Deferred lab isolation adversarial suite | DEFERRED |

For every approved requirement, add implementation paths, named test cases, CI run URL and commit SHA when implemented. A design reference alone is not implementation evidence.
