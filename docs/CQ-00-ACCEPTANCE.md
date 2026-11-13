# CQ-00 — Acceptance Gates

CQ-00 establishes product and engineering foundations; it does not claim a deployed or production-ready product.

| ID | Gate | Required evidence | Initial status |
|---|---|---|---|
| CQ00-01 | Repository and change governance | Repo metadata, branch convention, reviewed PR process | IN PROGRESS |
| CQ00-02 | Product scope | Approved MVP, exclusions, learner journeys and content boundaries | DRAFT |
| CQ00-03 | Architecture | Reviewed topology, authority boundaries, data and API direction | DRAFT |
| CQ00-04 | Security and privacy | Threat model, privacy baseline, cyber-safety boundaries | DRAFT |
| CQ00-05 | Reproducible toolchain | Python 3.12.16 backend environment, committed transitive hash lock, locked CI installation and drift rejection verified; Android/web toolchains remain pending | PARTIAL |
| CQ00-06 | API and data contracts | Initial FastAPI health slice, SQLAlchemy identity models and PostgreSQL migration verified; authentication/authorization and learner API contracts remain unimplemented | PARTIAL |
| CQ00-07 | Automated verification | PostgreSQL-backed CI passed 18 tests on PR merge candidate; broader runtime, Android, web and security verification remain pending | PARTIAL |
| CQ00-08 | Traceability | Requirements map to implementation and executable verification | DRAFT |
| CQ00-09 | Operational readiness | Initial budget, risk register and backup/recovery requirements documented; restore exercise and provider costs pending | PARTIAL |
| CQ00-10 | CQ-00 review | All blockers resolved or explicitly accepted; owner sign-off | NOT STARTED |

## Evidence notes

- CQ-00.3 Python dependency verification: run 43494824837 succeeded on candidate `ccd7ddcbd2c680866b561ede6cfc148ab743ff98`; committed lock drift check, `--require-hashes` install, `pip check`, PostgreSQL migration/schema/downgrade/re-upgrade and 18-test suite passed (1 warning). Artifact `cq00-python-dependency-lock` (ID `14070308973`, SHA-256 `675af19fbd6558b1b6d5d9128fbca80bfbb36da1487b1ba5bd50b9fb4e84281c`) was produced. Follow-up commit `fdefbe5350f96d01b3a0695ea84d785fd40e0933` records evidence. Python portion of CQ00-05 is VERIFIED; overall toolchain gate remains PARTIAL until Android and web toolchains are established.

- Draft OpenAPI contract: `openapi/cyberquest-v1.json` (design artefact; not a claim of complete API implementation).
- API rules: `docs/API-CONTRACT.md`.
- Conceptual entities and migration policy: `docs/DATA-MODEL.md`.
- Development environment evidence and outstanding toolchain work: `docs/DEVELOPMENT-ENVIRONMENT.md`.
- Backend implementation and boundaries: `docs/BACKEND-FOUNDATION.md`.
- PostgreSQL CI run 43471996771: migration upgrade, schema inspection, downgrade/re-upgrade and complete test suite succeeded; pytest reported 18 passed, 1 warning. The run tested PR merge candidate `1f866a9179cfedf3d94d8340c8ab50f1ba1d3219`, containing source commit `6b2f564277d0a7af92a83bea3369feeba924ca3c`. The documentation-only follow-up commit is separately verified by its own workflow before this register is treated as current-head CI evidence.
- PostgreSQL CI run 43494824837: verified committed `requirements-lock.txt` is up to date with `pyproject.toml`, installed it in hash-checking mode, `pip check` passed, migration upgrade/schema/downgrade/re-upgrade passed, and complete test suite reported 18 passed, 1 warning. Candidate commit `ccd7ddc` on `feat/cq-00-3-dependency-lock`.

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
