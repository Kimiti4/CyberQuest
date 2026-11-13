# ADR-0003: Server Authority for Progress and Competency

- Status: PROPOSED — requires review
- Date: 2026-11-13

The backend alone determines authoritative mission completion, XP transactions, achievements, assessment outcomes, competency status and entitlements.

XP is an append-only transaction ledger protected by database uniqueness/idempotency constraints. Attempts pin to immutable mission/content versions. Client-submitted events and evidence remain untrusted until server validation. Offline events cannot grant authoritative rewards or mastery before validation.

Competency requires explicit evidence and criteria; XP and course completion alone are insufficient.

Revisit only when a documented requirement and independent security review justify a different trust model.
