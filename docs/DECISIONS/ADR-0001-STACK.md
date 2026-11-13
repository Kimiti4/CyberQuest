# ADR-0001: Initial Technology Stack

- Status: PROPOSED — requires CQ-00 compatibility review
- Date: 2026-11-13

## Decision

Propose Kotlin/Jetpack Compose for Android; TypeScript/Next.js for web; Python/FastAPI/Pydantic/SQLAlchemy 2/Alembic for backend; PostgreSQL for durable data; REST/OpenAPI for client contracts; GitHub Actions for CI.

## Rationale

Native Android UX, one shared server authority, transactional relational data and a maintainable modular backend fit the Android-first MVP and constrained initial budget.

## Trade-offs

Multiple client ecosystems increase contract discipline and maintenance. Exact versions, hosting, identity provider and deployment topology remain subject to compatibility and cost validation.

## Revisit when

Measured performance, team capacity, accessibility, security or operating cost demonstrates that this stack is unsuitable.
