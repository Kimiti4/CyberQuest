# API Contract Baseline

**Status: mixed.** The authenticated learner API remains a proposed contract and is not implemented. CQ-00.7 implements only two stateless synthetic demo routes.

## Contract rules

- Base path: `/v1`; HTTPS is required outside local development.
- Format: JSON request/response bodies; UTF-8.
- Authentication: bearer access token from the selected identity provider for learner-owned routes. The provider and exact token claims remain undecided. The two `/v1/demo/` routes are explicitly unauthenticated, stateless and local/development only.
- Authorization: server-side checks on every learner-owned resource; object identifiers are not authorization.
- Time: RFC 3339 UTC timestamps.
- IDs: opaque UUID strings; clients must not infer meaning from them.
- Errors: stable machine-readable `code`, safe `message`, optional `request_id`; never return stack traces or secrets.
- Idempotency: state-changing client requests carry an `Idempotency-Key`; server binds key to authenticated actor, operation and request digest.
- Versioning: additive compatible changes within v1; breaking changes require a new major API path and migration plan.
- Pagination: cursor-based for collections; bounded page size.
- Rate limits: enforced server-side; return 429 with a retry hint where safe.

## Implemented demo slice

- `GET /v1/demo/missions/phishing-detective` returns versioned fictional mission content.
- `POST /v1/demo/missions/phishing-detective/assessment` evaluates bounded learner choices on the server and returns practice feedback.
- These routes do not create accounts, persist attempts, award XP or certify competencies. Do not expose them publicly without a separate abuse/rate-control and deployment review.

## Proposed learner resource groups

1. Health — liveness and readiness, no learner data.
2. Learning catalogue — published paths, modules, lessons and mission metadata.
3. Mission attempts — create, submit stage choices/evidence and request evaluation.
4. Learner progress — authenticated learner's progress snapshot.

## Authority boundaries

The client may display content and collect choices. It cannot decide authoritative completion, XP, achievements, competency or entitlements. Submission is a request for server evaluation, not proof of success. The API must pin each attempt to a published immutable mission version.

## Contract artefact

`openapi/cyberquest-v1.json` is the machine-readable contract. Its learner resource paths remain proposed. The CQ-00.7 demo paths have FastAPI implementations and automated tests; their local runtime/manual end-to-end verification remains a separate acceptance item. No identity integration, learner-data persistence or production endpoint is claimed.

## Deferred contract details

Identity provider and claims; full catalogue filtering and pagination; assessment evidence schema; upload handling; retention/export endpoints; payment/entitlement APIs; administrative endpoints. These require explicit designs before implementation.
