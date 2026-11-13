# Requirements Traceability Register

Status vocabulary: NOT_STARTED, IN_PROGRESS, PARTIAL, DESIGN_ONLY, PASS, FAIL, BLOCKED, UNKNOWN. DESIGN_ONLY is not implementation evidence. PASS requires linked, reproducible evidence.

| Requirement | Statement | Design reference | Verification method | Status |
|---|---|---|---|---|
| CQ-REQ-001 | Android and web use one versioned API contract | API-CONTRACT.md; openapi/cyberquest-v1.json | OpenAPI structure/auth/idempotency tests; client contract tests pending | PARTIAL |
| CQ-REQ-002 | XP and rewards are server-authoritative and idempotent | ADR-0003; DATA-MODEL.md | Replay, duplicate and transaction tests | DESIGN_ONLY |
| CQ-REQ-003 | Missions are versioned and schema validated | ARCHITECTURE.md; DATA-MODEL.md | Positive/negative schema tests; runtime validation pending | PARTIAL |
| CQ-REQ-004 | Offline attempts require server validation | ADR-0005; API-CONTRACT.md | Replay, stale-version and sync tests | DESIGN_ONLY |
| CQ-REQ-005 | Core learning works without external AI | PRODUCT-BASELINE.md | Disable AI and run acceptance suite | NOT_STARTED |
| CQ-REQ-006 | MVP makes no unsupported device-protection claims | SECURITY-AND-PRIVACY.md; CQ-00.6 threat model | Product copy and feature review | DESIGN_ONLY |
| CQ-REQ-007 | Learner data is access-controlled and minimised | CQ-00.6 threat model; DATA-MODEL.md | Two-user access tests, data inventory and privacy review | DESIGN_ONLY |
| CQ-REQ-008 | Future labs are isolated and fail closed | CQ-00.6 threat model | Deferred lab isolation adversarial suite | DEFERRED |
| CQ-REQ-009 | Authentication and session lifecycle resist takeover | CQ-00.6 threat model §9 | Token, recovery, revocation and abuse tests | NOT_STARTED |
| CQ-REQ-010 | Personal data is processed for documented purposes and retention | CQ-00.6 threat model §7–8 | Legal review, rights workflow and retention/deletion tests | NOT_STARTED |
| CQ-REQ-011 | Child data is protected and age scope is explicit | CQ-00.6 threat model §8 | Founder decision, counsel review and age/guardian workflow tests | BLOCKED |
| CQ-REQ-012 | Content publication prevents unsafe or executable payloads | CQ-00.6 threat model §10 | Schema, injection and publication-approval tests | DESIGN_ONLY |
| CQ-REQ-013 | Security controls have reproducible adversarial verification | CQ-00.6 security verification plan | CI-backed negative tests with commit and run evidence | NOT_STARTED |

For every approved requirement, add implementation paths, named test cases, CI run URL and commit SHA when implemented. A design reference alone is not implementation evidence.
