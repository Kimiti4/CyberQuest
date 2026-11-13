# CQ-00 Risk Register

**Status: initial qualitative register; owners are role assignments pending named project owners.**

| ID | Risk | Initial likelihood / impact | Required treatment | Accountable role | Status |
|---|---|---|---|---|---|
| R-001 | Public repository accidentally contains credentials or personal data | Medium / Critical | Secret scanning, synthetic fixtures, PR review, immediate revocation and incident process | Repository maintainer | Open |
| R-002 | Learner can manipulate XP, completion or competencies | Medium / High | Server authority, append-only ledger, idempotency, adversarial replay and authorization tests | Backend owner | Open |
| R-003 | Cross-learner data exposure through object ID manipulation | Medium / Critical | Object-level authorization on every operation; two-user negative tests | Backend/security owner | Open |
| R-004 | Phishing scenarios teach unsafe behaviour or contain real targets | Medium / High | Fictional data/domains, safety review, publication approval and learner feedback | Curriculum/safety owner | Open |
| R-005 | Product overstates device protection or detection | Medium / High | Claims review; label simulations; prohibit unsupported scan/protection claims | Product owner | Open |
| R-006 | Underage learner data processed without adequate safeguards | Medium / High | Age policy, lawful-basis/consent review and age-appropriate design before launch | Privacy/legal owner | Open |
| R-007 | External provider outage or pricing change disrupts MVP | Medium / Medium | Provider adapter boundaries, cost alerts, export/backup plan and fallback review | Technical lead | Open |
| R-008 | CI supply-chain compromise through mutable third-party actions | Medium / High | Pin actions to reviewed commit SHAs, read-only token permissions, update review | Repository maintainer | Mitigating |
| R-009 | Backups exist but cannot be restored | Medium / Critical | Isolated restore drills and release gate | Operations owner | Open |
| R-010 | Budget is insufficient for full custom Android/backend/web delivery | High / High | Scope discipline, staged delivery, cost tracking and contingency | Product owner | Open |
| R-011 | Future cyber lab escapes isolation or reaches public targets | Low / Critical | Defer technical labs; external network policy; fail-closed launch gate and independent testing | Security/lab owner | Deferred |
| R-012 | AI output is inaccurate or encourages unsafe action | Medium / High | AI optional; constrained retrieval; user-visible uncertainty; human review; no arbitrary execution | Product/security owner | Open |

## Review rules

- Reassess likelihood and impact at each checkpoint and before beta.
- A mitigation marked planned is not a closed risk.
- Critical risks require documented owner acceptance or verified treatment before release.
- Record evidence links and residual risk; do not silently downgrade severity.
