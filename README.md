# CYBERQUEST

**Learn. Hack. Defend. Master.**

CYBERQUEST is an Android-first cybersecurity learning and digital-protection platform for adults aged 18 and above, with a companion web experience. It combines practical security education, defensive decision-making, deterministic scenario simulations and evidence-based competency development. The initial release is adults-only; minors are out of scope.

## Programme status

- Current checkpoint: **CQ-00 — Product and Engineering Foundation**
- Repository: [Kimiti4/CyberQuest](https://github.com/Kimiti4/CyberQuest)
- Default branch: `main`
- CQ-00 status: **IN PROGRESS**
- CQ-00.4 architecture decisions ADR-0004 and ADR-0005: **FOUNDER-APPROVED**
- CQ-00.5 — Android and Web Reproducible Build Foundations: **PASS** on verified candidate `0c95b30c990d0a9fc0247ded70fd5bf163f27261`.
- CQ-00.6 — Security, Privacy and Cyber-Safety Threat Model: **DESIGN BASELINE COMPLETE; CQ00-04 PARTIAL**. Runtime controls, legal review and adversarial security tests remain open.
- CI verified Android/Linux build, uncached unit tests, debug APK assembly and lint; Windows Gradle wrapper integrity/startup; web clean install from committed lock, typecheck, five contract tests, warning-free OpenAPI lint and Next.js production build; Python/PostgreSQL foundation suite also passed.
- The next demonstrable prototype may use synthetic accounts and fictional data only; no live identity provider or real learner personal data is approved for the demo.
- Cloud provider and exact processing region, formal legal review, privacy procedures and final mandatory-record retention schedule are deferred until production-readiness and must be resolved before public beta/live learner data.
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

Exact versions and compatibility evidence are recorded in [CQ-00.5 toolchain locks](docs/CQ-00.5-TOOLCHAIN-LOCKS.md); CI verifies the build scaffolds, not production readiness.

## Documentation

- [Product baseline](docs/PRODUCT-BASELINE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [CQ-00.4 architecture review](docs/CQ-00.4-ARCHITECTURE-REVIEW.md)
- [CQ-00.5 build foundations](docs/CQ-00.5-BUILD-FOUNDATIONS.md)
- [CQ-00.5 toolchain locks](docs/CQ-00.5-TOOLCHAIN-LOCKS.md)
- [Cross-platform toolchain matrix](docs/CQ-00.4-TOOLCHAIN-MATRIX.md)
- [Security and privacy baseline](docs/SECURITY-AND-PRIVACY.md)
- [CQ-00.6 threat model and privacy inventory](docs/CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md)
- [CQ-00.6 security verification plan](docs/CQ-00.6-SECURITY-VERIFICATION-PLAN.md)
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

See [pyproject.toml](pyproject.toml) and the CQ-00.5 toolchain lock register for pinned build environments. Candidate CI verifies the backend foundation, Android build/test/lint, Windows Gradle wrapper startup and Next.js production build from the committed npm lock. No production deployment or learner-facing functionality is claimed.