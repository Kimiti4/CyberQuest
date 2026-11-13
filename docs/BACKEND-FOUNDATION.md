# Backend Foundation — CQ-00

**Status: initial API and persistence slice implemented; PostgreSQL migration and identity constraints are exercised in CI.**

## Included

- FastAPI application factory with liveness and fail-closed readiness endpoints.
- SQLAlchemy declarative metadata and a minimal identity mapping/profile model.
- Alembic migration for the two initial tables.
- PostgreSQL driver dependency and pinned direct requirements files.
- CI provisions a disposable PostgreSQL 16 service, applies the Alembic migration, inspects the resulting schema, and tests downgrade/re-upgrade.
- Unit tests for health semantics and model metadata.
- PostgreSQL integration tests for duplicate external identity rejection, orphan profile rejection and user/profile cascade deletion.

## Security and correctness boundaries

- Liveness is independent of downstream services.
- Readiness returns 503 when the database is not configured or cannot be reached.
- Readiness does not reveal connection strings or driver errors.
- No learner-facing mission, XP, competency, identity-token validation or admin endpoint is implemented.
- No authentication provider has been selected or integrated. The API must not be exposed as a learner service until authentication and authorization are implemented.
- The initial schema stores an external identity subject, not passwords or raw authentication credentials.

## Dependency verification

The canonical direct dependency declarations live in `pyproject.toml`; CI consumes committed `requirements-lock.txt` with pip `--require-hashes` and regenerates a temporary lock to reject drift. Workflow run `43494824837` verified lock consistency, hash-enforced installation, `pip check`, PostgreSQL migration/schema/downgrade/re-upgrade and the 18-test suite (1 warning). This verifies the current Python backend foundation scope, not a hermetic build, production deployment or complete application behavior.

PostgreSQL runtime verification is PASS only for a completed workflow on the exact commit containing the integration tests. A commit or queued workflow is not evidence.
