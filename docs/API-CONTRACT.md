# API Contract Baseline

**Status: proposed contract v1; not an implemented API.**

## Contract rules

- Base path: `/v1`; HTTPS is required outside local development.
- Format: JSON request/response bodies; UTF-8.
- Authentication: bearer access token from the selected identity provider. The provider and exact token claims remain undecided.
- Authorization: server-side checks on every learner-owned resource; object identifiers are not authorization.
- Time: RFC 3339 UTC timestamps.
- IDs: opaque UUID strings; clients must not infer meaning from them.
- Errors: stable machine-readable `code`, safe `message`, optional `request_id`; never return stack traces or secrets.
- Idempotency: state-changing client requests carry an `Idempotency-Key`; server binds key to authenticated actor, operation and request digest.
- Versioning: additive compatible changes within v1; breaking changes require a new major API path and migration plan.
- Pagination: cursor-based for collections; bounded page size.
- Rate limits: enforced server-side; return 429 with a retry hint where safe.

## Initial resource groups

1. Health — liveness and readiness, no learner data.
2. Learning catalogue — published paths, modules, lessons and mission metadata.
3. Mission attempts — create, submit stage choices/evidence and request evaluation.
4. Learner progress — authenticated learner's progress snapshot.

## Authority boundaries

The client may display content and collect choices. It cannot decide authoritative completion, XP, achievements, competency or entitlements. Submission is a request for server evaluation, not proof of success. The API must pin each attempt to a published immutable mission version.

## Contract artefact

`openapi/cyberquest-v1.json` is the machine-readable draft. It is a design contract only. No server implementation, identity integration, schema migration or endpoint runtime test is claimed in CQ-00.

## Deferred contract details

Identity provider and claims; full catalogue filtering and pagination; assessment evidence schema; upload handling; retention/export endpoints; payment/entitlement APIs; administrative endpoints. These require explicit designs before implementation.
