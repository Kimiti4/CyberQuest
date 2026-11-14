# CQ-00 Risk Register

**Status: initial qualitative register; accountable owners are role assignments pending named project owners.** Risk likelihood/impact are preliminary and must be reassessed with implementation evidence.

| ID | Risk | Initial likelihood / impact | Required treatment | Accountable role | Status |
|---|---|---|---|---|---|
| R-001 | Public repository accidentally contains credentials or personal data | Medium / Critical | Secret scanning, synthetic fixtures, PR review, immediate revocation and incident process | Repository maintainer | Open |
| R-002 | Learner can manipulate XP, completion or competencies | Medium / High | Server authority, append-only ledger, idempotency, adversarial replay and authorization tests | Backend owner | Open |
| R-003 | Cross-learner data exposure through object ID manipulation | Medium / Critical | Object-level authorization on every operation; two-user negative tests | Backend/security owner | Open |
| R-004 | Phishing scenarios teach unsafe behaviour or contain real targets | Medium / High | Fictional data/domains, safety review, publication approval and learner feedback | Curriculum/safety owner | Open |
| R-005 | Product overstates device protection or detection | Medium / High | Claims review; label simulations; prohibit unsupported scan/protection claims | Product owner | Open |
| R-006 | Underage access to adults-only service | Medium / High | Adults-only 18+ scope; proportionate age gate; avoid unnecessary DOB collection; abuse/reporting path | Product + privacy owner | Open — age gate required before live registration |
| R-007 | External provider outage or pricing change disrupts MVP | Medium / Medium | Provider adapter boundaries, cost alerts, export/backup plan and fallback review | Technical lead | Open |
| R-008 | CI supply-chain compromise through third-party actions/dependencies | Medium / High | Pin actions and dependencies, read-only CI permissions, provenance/SBOM and vulnerability response | Repository maintainer | Mitigating — partial |
| R-009 | Backups exist but cannot be restored | Medium / Critical | Isolated restore drills and release gate | Operations owner | Open |
| R-010 | Budget is insufficient for full custom Android/backend/web delivery | High / High | Scope discipline, staged delivery, cost tracking and contingency | Product owner | Open |
| R-011 | Future cyber lab escapes isolation or reaches public targets | Low / Critical | Defer technical labs; external network policy; fail-closed launch gate and independent testing | Security/lab owner | Deferred — no lab approved |
| R-012 | AI output is inaccurate or encourages unsafe action | Medium / High | AI optional; constrained retrieval; user-visible uncertainty; human review; no arbitrary execution | Product/security owner | Open |
| R-013 | Account takeover through weak recovery or token/session validation | Medium / Critical | Select identity provider; threat-model token lifecycle/recovery; MFA for privileged users; abuse controls; adversarial tests | Identity/security owner | Open — before CQ-01 identity |
| R-014 | Broken object-level authorization exposes or alters another learner's data | Medium / Critical | Actor-scoped queries, deny-by-default policy, two-user read/write negative tests | Backend/security owner | Open — before learner APIs |
| R-015 | Privacy processing is unlawful, excessive or transferred without safeguards | Medium / High | Minimise collection; synthetic demo data; complete purpose/legal-basis analysis, notices, processor contracts and transfer review before public beta | Founder + qualified privacy/legal reviewer | Open — before public beta/live learner data |
| R-016 | Adults-only age restriction is not enforced | Medium / Critical | Enforce and test 18+ eligibility gate; prevent underage account activation; future minors expansion requires separate approval | Product + privacy owner | Open — release blocker before live registration |
| R-017 | Retention, deletion or export cannot be honoured across systems/backups | Medium / High | Category-specific schedule, rights workflow, processor propagation and backup expiry design | Privacy + operations owner | Open — before beta |
| R-018 | Unsafe content or false protection claims reach learners | Medium / High | Content publication review, schema restrictions, fictional targets, claims taxonomy and report/remove path | Curriculum/safety owner | Open |
| R-019 | Android local cache/token or account-switch behavior exposes learner data | Medium / High | Secure storage, cache partitioning, logout clearing, backup review, emulator/physical-device tests | Android/security owner | Open — device validation pending |
| R-020 | Future lab workload reaches host, metadata or unauthorized networks | Low / Critical | Separate control plane, external deny-by-default network enforcement, quotas, credentials, teardown and independent escape tests | Security/lab owner | Deferred — blocks lab launch |

## Review rules

- Reassess likelihood and impact at each checkpoint and before beta.
- A mitigation marked planned or design-only is not a closed risk.
- Critical risks require documented owner acceptance or verified treatment before release; legal and safety obligations cannot be waived by project preference.
- Record evidence links, residual risk, named owner and disposition; do not silently downgrade severity.
