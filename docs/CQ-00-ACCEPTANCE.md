# CQ-00 — Acceptance Gates

CQ-00 establishes product and engineering foundations; it does not claim a deployed or production-ready product.

| ID | Gate | Required evidence | Current status |
|---|---|---|---|
| CQ00-01 | Repository and change governance | Repo metadata, branch convention, reviewed PR process | IN PROGRESS |
| CQ00-02 | Product scope | Approved MVP, exclusions, learner journeys and content boundaries | DRAFT |
| CQ00-03 | Architecture | Cross-pillar topology, module ownership, server authority and offline-sync contract reviewed and founder-ratified | PASS |
| CQ00-04 | Security and privacy | Threat model, privacy baseline, cyber-safety boundaries | DRAFT |
| CQ00-05 | Reproducible toolchain | Python hash lock plus pinned Android/web toolchains, committed wrapper and npm lock, clean CI builds | PASS |
| CQ00-06 | API and data contracts | Initial FastAPI health slice, SQLAlchemy identity models and PostgreSQL migration verified; authentication/authorization and learner API contracts remain unimplemented | PARTIAL |
| CQ00-07 | Automated verification | PostgreSQL-backed CI, Android unit tests and web contract tests; integration, emulator and security verification remain pending | PARTIAL |
| CQ00-08 | Traceability | Requirements map to implementation and executable verification | DRAFT |
| CQ00-09 | Operational readiness | Initial budget, risk register and backup/recovery requirements documented; restore exercise and provider costs pending | PARTIAL |
| CQ00-10 | CQ-00 review | All blockers resolved or explicitly accepted; owner sign-off | NOT STARTED |

## Evidence notes

- CQ-00.3 Python dependency verification: workflow run 43494824837 passed on candidate `ccd7ddcbd2c680866b561ede6cfc148ab743ff98`; lock drift check, hash-enforced install, `pip check`, PostgreSQL migration/schema/downgrade/re-upgrade and 18 tests passed (1 warning). The Python portion of CQ00-05 is VERIFIED; the overall gate remains PARTIAL pending Android/web toolchains.
- CQ-00.4 architecture review: `docs/CQ-00.4-ARCHITECTURE-REVIEW.md`; ADR-0004 and ADR-0005 were ratified by the founder on 2026-11-14. Their decisions are now accepted architecture constraints.
- CQ-00.4 toolchain assessment: Python backend foundation verified by run 43494824837; Android and web projects/builds were absent at CQ-00.4 close. CQ-00.5 adds the client scaffolds and CI evidence recorded below.
- `tests/test_architecture_contract.py` checks selected documented invariants. It is a documentation contract test, not runtime proof of Android/web/API behavior.
- `tests/test_android_wrapper_integrity.py` verifies the base64-encoded official Gradle wrapper payload and pinned distribution checksum; CI separately builds the Android project.
- Draft OpenAPI contract: `openapi/cyberquest-v1.json` (design artefact; not a claim of complete API implementation).
- API rules: `docs/API-CONTRACT.md`.
- Conceptual entities and migration policy: `docs/DATA-MODEL.md`.
- Development environment evidence and outstanding toolchain work: `docs/DEVELOPMENT-ENVIRONMENT.md`.
- Backend implementation and boundaries: `docs/BACKEND-FOUNDATION.md`.
- PostgreSQL CI run 43471996771: migration upgrade, schema inspection, downgrade/re-upgrade and complete test suite succeeded; pytest reported 18 passed, 1 warning. The run tested PR merge candidate `1f866a9179cfedf3d94d8340c8ab50f1ba1d3219`, containing source commit `6b2f564277d0a7af92a83bea3369feeba924ca3c`. The documentation-only follow-up commit is separately verified by its own workflow before this register is treated as current-head CI evidence.
- PostgreSQL CI run 43494824837: verified committed `requirements-lock.txt` is up to date with `pyproject.toml`, installed it in hash-checking mode, `pip check` passed, migration upgrade/schema/downgrade/re-upgrade passed, and complete test suite reported 18 passed, 1 warning. Candidate commit `ccd7ddc` on `feat/cq-00-3-dependency-lock`.
- CQ-00.4 ratification: ADR-0004 and ADR-0005 were accepted by the founder on 2026-11-14. Ratified branch head `e1387436ecb1ae036ae345356f7f64d71b41b899` had 2 successful CI check runs.
- CQ-00.5 cross-platform run `43510431845` and Python/PostgreSQL foundation run `43510432019` both passed on candidate `0c95b30c990d0a9fc0247ded70fd5bf163f27261`.
- Android/Linux: Gradle 8.13 clean build, uncached JUnit execution, debug APK assembly and lint passed (56 tasks; 55 executed, 1 up-to-date).
- Android/Windows: PowerShell materialized the official wrapper payload, verified its SHA-256 and started Gradle 8.13 successfully.
- Web: `npm ci` from committed lock, TypeScript typecheck, five Node contract tests, warning-free Redocly lint and Next.js 16.4.0 production build passed. No server URL is declared because no API deployment exists; Redocly's empty-server rule is explicitly disabled and placeholder server URLs are rejected.
- Python/PostgreSQL: lock drift check, hash-enforced install, `pip check`, migration upgrade/schema/downgrade/re-upgrade and full suite passed (25 passed, 1 non-blocking Starlette TestClient/AnyIO deprecation warning).
- Committed web lock: `web/package-lock.json` at commit `87c792de906cd1dd4b0d777efb75798cee01f77f`; lockfileVersion 3, 308 package entries, 307 resolved packages with integrity hashes, SHA-256 `b1ee9065901b18543385e071878bcf5259a4dd0e10cb75cea8c0c2432805102a`.

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