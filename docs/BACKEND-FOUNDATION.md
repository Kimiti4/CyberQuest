# Backend Foundation — CQ-00

**Status: initial API and persistence slice implemented; full dependency/toolchain reproducibility remains under verification.**

## Included

- FastAPI application factory with liveness and fail-closed readiness endpoints.
- SQLAlchemy declarative metadata and a minimal identity mapping/profile model.
- Alembic migration for the two initial tables.
- PostgreSQL driver dependency and pinned direct requirements files.
- Unit tests for health semantics and model constraints.

## Security and correctness boundaries

- Liveness is independent of downstream services.
- Readiness returns 503 when the database is not configured or cannot be reached.
- Readiness does not reveal connection strings or driver errors.
- No learner-facing mission, XP, competency, identity-token validation or admin endpoint is implemented.
- No authentication provider has been selected or integrated. The API must not be exposed as a learner service until authentication and authorization are implemented.
- The initial schema stores an external identity subject, not passwords or raw authentication credentials.

## Dependency verification

The direct dependency pins in `requirements-api.txt` and `requirements-test.txt` are candidate pins. CI installation is the compatibility check; this is not a fully transitive lockfile. A hash-locked dependency solution remains a CQ-00 exit requirement.
