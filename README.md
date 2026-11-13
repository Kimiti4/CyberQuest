# CYBERQUEST

**Learn. Hack. Defend. Master.**

CYBERQUEST is an Android-first cybersecurity learning and digital-protection platform, with a companion web experience. It combines practical security education, defensive decision-making, deterministic scenario simulations and evidence-based competency development.

## Programme status

- Current checkpoint: **CQ-00 — Product and Engineering Foundation**
- Repository: [Kimiti4/CyberQuest](https://github.com/Kimiti4/CyberQuest)
- Default branch: `main`
- CQ-00 status: **IN PROGRESS**
- CQ-00.4 architecture decisions ADR-0004 and ADR-0005: **FOUNDER-APPROVED**
- Next checkpoint: **CQ-00.5 — Android and Web Reproducible Build Foundations**
- No production application, real device scanning, malware detection or cyber-range execution is claimed.

## Product principles

1. Evidence before confidence; unknown is not pass.
2. The server is authoritative for progress, rewards, assessment outcomes and competencies.
3. Simulated exercises are clearly labelled and never presented as real device protection.
4. MVP exercises are static learning content and deterministic simulations; no arbitrary learner-supplied code execution.
5. Privacy, consent, data minimisation and security are design requirements.
6. Core learning works without an external AI provider.

## Technology direction

| Layer | Proposed baseline |
|---|---|
| Android | Kotlin, Jetpack Compose, Room, DataStore, WorkManager |
| Web | TypeScript, Next.js |
| API | Python, FastAPI, Pydantic |
| Data | PostgreSQL, SQLAlchemy 2, Alembic |
| Tests | Pytest, JUnit/Compose UI Test, Vitest, Playwright |
| CI | GitHub Actions |

These choices are approved architecture direction; exact runtime/tool versions must be pinned after compatibility checks and actual build verification.

## Documentation

- [Product baseline](docs/PRODUCT-BASELINE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [CQ-00.4 architecture review](docs/CQ-00.4-ARCHITECTURE-REVIEW.md)
- [Cross-platform toolchain matrix](docs/CQ-00.4-TOOLCHAIN-MATRIX.md)
- [Security and privacy](docs/SECURITY-AND-PRIVACY.md)
- [CQ-00 acceptance gates](docs/CQ-00-ACCEPTANCE.md)
- [Requirements traceability](docs/TRACEABILITY.md)
- [API contract baseline](docs/API-CONTRACT.md)
- [OpenAPI draft](openapi/cyberquest-v1.json)
- [Initial data model and migration policy](docs/DATA-MODEL.md)
- [Development environment](docs/DEVELOPMENT-ENVIRONMENT.md)
- [Branch and change policy](docs/BRANCH-AND-CHANGE-POLICY.md)
- [Architecture decisions](docs/DECISIONS/)

## Checkpoints

CQ-00 Foundation → CQ-01 Identity → CQ-02 Curriculum → CQ-03 Mission Engine → CQ-04 Phishing Detective → CQ-05 Digital Protection → CQ-06 Gamification → CQ-07 Client Integration → CQ-08 Assessment Evidence → CQ-09 Security/Privacy Audit → CQ-10 Beta → CQ-11 Release.

CQ-01 must not begin until CQ-00 exit gates are reviewed and accepted.

## Development

See [pyproject.toml](pyproject.toml) for the Python tooling baseline. CQ-00 CI currently validates the foundation documentation and Python test harness; it does not certify an application runtime or deployment.