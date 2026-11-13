# Architecture Baseline

**Status: proposed; subject to CQ-00 compatibility and risk review.**

## Topology

Android (Kotlin/Compose) and Web (Next.js/TypeScript) use one versioned HTTPS REST API. A Python/FastAPI modular monolith owns application rules and persists durable state in PostgreSQL. Optional object storage and external identity services are isolated behind adapters.

## Backend modules

- Identity integration and account lifecycle
- Learner profiles
- Curriculum and content versioning
- Mission catalogue and attempts
- Assessment and competency evidence
- Progress and XP ledger
- Achievements
- Feedback and analytics
- Administration and audit events
- Entitlements/payments (deferred pending separate design)

Modules expose explicit service interfaces. Route handlers do not own domain rules. Avoid direct cross-module table mutation.

## Authority and consistency

The backend is authoritative for mission completion, assessment outcomes, XP transactions, achievements, competency status and entitlements. XP writes must be transactional, append-only and protected against duplicate/idempotent submissions. Attempts pin to immutable content versions. Client evidence is untrusted until validated.

Offline clients may cache approved content and queue attempt events. Sync must be idempotent, version-aware and replay-resistant. Offline events cannot directly grant authoritative XP or mastery.

## Mission format

Missions are declarative, schema-validated data: identity/version, objectives, stages, allowed choices, expected evidence, assessment rules and rewards. No arbitrary executable scripts, arbitrary external URLs or learner-provided commands in the MVP mission runtime. Content publication requires review and immutable versioning.

## API and data

REST with OpenAPI. PostgreSQL is the durable source of truth. Use UUID identifiers, foreign keys, unique constraints, UTC timestamps and explicit transaction boundaries. Database migrations are versioned and reviewed. Credentials are delegated to an identity provider; application secrets never enter source control.

## Technology proposal

- Android: Kotlin, Jetpack Compose, Room, DataStore, WorkManager, Retrofit/OkHttp.
- Web: TypeScript, Next.js, React, Tailwind CSS, TanStack Query, Zod.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2, Alembic.
- Data: PostgreSQL.
- Verification: Pytest, JUnit/Compose UI Test, Vitest, Playwright.
- CI: GitHub Actions.

Pin exact versions only after compatibility checks. Start with a modular monolith; do not introduce microservices, Kubernetes, message brokers or self-hosted cyber-range infrastructure without measured requirements and a reviewed decision.

## Deployment

Prefer low-cost managed hosting and managed PostgreSQL after portability, access control, secret handling, backup and restore requirements are tested. Provider-specific integrations remain behind adapters. No production environment is defined or deployed by CQ-00.
