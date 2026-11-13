# ADR-0005: Offline Synchronization Is Untrusted Event Submission

- **Status:** PROPOSED — requires founder ratification
- **Date:** 2026-11-13
- **Checkpoint:** CQ-00.4

## Context

Intermittent connectivity makes offline content useful, but locally generated events can be modified, replayed, reordered or submitted after content changes.

## Decision

Offline clients may cache approved, versioned learning content and queue interaction events. The server remains authoritative for acceptance, assessment, XP, achievements and competency.

Each event carries a unique client event ID, schema version, content/mission version, event type and payload. The authenticated server establishes actor identity and receipt time, validates ownership and allowed transitions, checks idempotency/replay, and evaluates assessment against the pinned version.

The server returns explicit accepted, duplicate, stale-version, invalid-transition, unauthorized or retryable outcomes. Duplicate submissions never award twice. Stale content is not silently reinterpreted against a newer version.

## Security requirements

- Client timestamps are advisory and cannot prove event order or completion time.
- Client-submitted score, XP, mastery or entitlement fields are never authoritative.
- Logout/account switching isolates or clears queued user data.
- Credentials use platform-appropriate secure storage.
- Offline data is minimized and subject to retention/deletion rules.
- Sync endpoints require rate limits, validation and auditability.

## Consequences

Offline progress may remain pending or be rejected after synchronization. The UI must explain this and offer remediation. This is preferable to granting unverifiable rewards.

## Alternatives rejected

- Trusting local scores or XP enables client tampering.
- Replaying events against latest content changes the assessment contract after the learner acted.
- Treating local timestamps as authoritative trusts user-controlled device clocks.