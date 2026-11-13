# CQ-00 — Acceptance Gates

CQ-00 establishes product and engineering foundations; it does not claim a deployed or production-ready product.

| ID | Gate | Required evidence | Initial status |
|---|---|---|---|
| CQ00-01 | Repository and change governance | Repo metadata, branch convention, reviewed PR process | IN PROGRESS |
| CQ00-02 | Product scope | Approved MVP, exclusions, learner journeys and content boundaries | DRAFT |
| CQ00-03 | Architecture | Reviewed topology, authority boundaries, data and API direction | DRAFT |
| CQ00-04 | Security and privacy | Threat model, privacy baseline, cyber-safety boundaries | DRAFT |
| CQ00-05 | Reproducible toolchain | Pinned compatible runtimes and documented setup | NOT RUN |
| CQ00-06 | API and data contracts | Draft OpenAPI 3.1 contract, conceptual data model and migration policy documented; runtime/schema verification pending | PARTIAL |
| CQ00-07 | Automated verification | CI executes foundation tests; action SHAs pinned and least-privilege workflow; application/runtime checks remain pending | PARTIAL |
| CQ00-08 | Traceability | Requirements map to implementation and executable verification | DRAFT |
| CQ00-09 | Operational readiness | Initial budget, risk register and backup/recovery requirements documented; restore exercise and provider costs pending | PARTIAL |
| CQ00-10 | CQ-00 review | All blockers resolved or explicitly accepted; owner sign-off | NOT STARTED |

## Evidence notes

- Draft OpenAPI contract: `openapi/cyberquest-v1.json` (design artefact; no API runtime).
- API rules: `docs/API-CONTRACT.md`.
- Conceptual entities and migration policy: `docs/DATA-MODEL.md` (no DDL or migrations applied).
- Development environment evidence and outstanding toolchain work: `docs/DEVELOPMENT-ENVIRONMENT.md`.

## Status vocabulary

- PASS: acceptance evidence exists and was reviewed.
- PARTIAL: some evidence exists, but the full gate is not satisfied.
- FAIL: an executed check demonstrates a requirement is not met.
- BLOCKED: a dependency prevents verification.
- NOT RUN / NOT STARTED: no verification claim.
- UNKNOWN: evidence is insufficient to classify.

Do not mark a gate PASS based solely on documentation or a green CI job if its acceptance requires runtime or operational evidence.

## Exit conditions

CQ-00 exits only when product scope and architecture are reviewed; the toolchain is reproducible; API/data contracts are defined; CI is green on the candidate commit; security/privacy and safety boundaries are reviewed; requirements traceability is complete for the approved foundation; and unresolved risks have owners and dispositions. CQ-01 remains blocked until this review is recorded.
