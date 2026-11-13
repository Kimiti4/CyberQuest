# Operations, Environments and Recovery Baseline

**Status: requirements defined; no production environment or backup system exists.**

## Environment separation

| Environment | Purpose | Data | Credentials |
|---|---|---|---|
| Local | Developer implementation and tests | Synthetic fixtures only | Individual local credentials; never committed |
| CI | Automated verification | Synthetic fixtures only | Read-only repository token; no deployment secrets |
| Staging (future) | Pre-release integration and acceptance | Synthetic or explicitly approved pseudonymised data | Separate short-lived secrets and restricted operators |
| Production (future) | Live learner service | Minimum necessary learner data | Separate production secret store, MFA and audited access |

Staging and production must not share credentials, databases, signing keys or storage buckets. Production data must never be copied into local development or CI.

## Operational minimums before public beta

- Health endpoints distinguish process liveness from dependency readiness.
- Structured logs include request/correlation IDs and redact tokens, passwords, payment data and learner answers where unnecessary.
- Alerting covers availability, error rate, database capacity, failed background jobs and suspicious authentication/reward patterns.
- Admin access uses MFA, least privilege and audit events.
- Dependency, secret and container scanning are enabled before deployable services are exposed.
- A release has a named owner, rollback plan, migration plan and documented incident contact path.
- Operational claims and security detections must be tied to actual telemetry and tested controls.

## Backup and recovery requirements

- Define RPO/RTO with the service owner before production launch; do not invent targets before provider and budget selection.
- Back up PostgreSQL and required object storage using provider-supported encryption and access controls.
- Keep backup credentials separate from application credentials; restrict deletion and modification.
- Define retention and deletion policy consistent with legal and product requirements.
- Monitor backup job completion and age; backup creation alone is not evidence of recoverability.
- Run a restore into an isolated environment before beta and after material backup-policy changes.
- Verify schema migration compatibility, row counts/integrity checks, application startup and a representative learner workflow after restore.
- Record restore date, source backup identifier, duration, observed data loss window, checks and operator.
- A failed or unverified restore blocks production release.

## Incident handling

1. Triage and classify suspected event.
2. Contain affected credentials, sessions, services or content.
3. Preserve relevant audit evidence without collecting unnecessary personal data.
4. Assess scope and legal notification obligations with the responsible privacy/legal owner.
5. Recover from a known-good state and rotate exposed credentials.
6. Document root cause, corrective actions and regression tests.

No production backup, restore, alerting or incident-response exercise has been performed as part of CQ-00.
