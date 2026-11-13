# Initial Data Model and Migration Policy

**Status: conceptual model; no database schema or migration has been applied.**

## Core entities

| Entity | Purpose | Key integrity rules |
|---|---|---|
| users | Internal learner identity mapping | UUID PK; unique external subject/provider pair |
| learner_profiles | Display and learner preferences | One-to-one with user; minimise optional personal data |
| learning_paths | Published learning journey | Stable slug; versioned publication |
| courses | Course grouping | Stable slug; belongs to path |
| modules | Ordered course sections | Unique order within course |
| lessons | Learning content | Immutable published versions |
| competencies | Skills and criteria | Versioned rubric; no XP-only award |
| missions | Stable mission identity | Stable slug |
| mission_versions | Immutable mission definition | Unique mission/version; schema-validated |
| mission_attempts | Learner attempt | FK to user and exact mission version |
| mission_stage_attempts | Stage submissions | Ordered, idempotent event identity |
| assessment_attempts | Assessment session | Pinned assessment/content version |
| assessment_responses | Learner answers | FK to attempt and question; no answer leakage |
| xp_transactions | Append-only reward ledger | Unique idempotency key; signed/validated server-side event |
| learner_competencies | Awarded competency state | Evidence reference and rubric version required |
| achievements | Achievement definitions | Versioned criteria |
| learner_achievements | Awarded achievements | Unique learner/achievement award |
| audit_events | Privileged/security-relevant actions | Append-only access controls; redacted payloads |

Subscriptions, payments, lab sessions and lab audit events are intentionally deferred from the initial persistence slice.

## Invariants

- UUID primary keys and explicit foreign keys.
- Unique constraints enforce stable slugs, content versions, event identities and reward idempotency.
- Attempt records pin immutable content/assessment versions.
- XP ledger is append-only; corrections use compensating entries, not mutation/deletion.
- A competency award references evidence and the rubric version used.
- Learner-owned rows are always scoped by authenticated actor at the service/query boundary.
- Store timestamps in UTC; use database transactions for attempt finalisation and reward grants.
- Do not store passwords; identity credentials remain with the identity provider.
- Avoid collecting phone, national ID, contacts, SMS, call logs or location unless a separately approved necessity and lawful basis exist.

## Migration policy

- Alembic owns schema evolution; every migration is reviewed and has a downgrade/forward-recovery strategy.
- Never edit an already-applied migration; add a new migration.
- Migrations must be deterministic, ordered and tested against an empty database and the previous supported schema.
- Destructive changes require an expand/migrate/contract plan and backup verification.
- No production migration runs automatically on application startup.
- Seed data is deterministic, non-sensitive and separate from production user data.

## CQ-00 boundary

This document is a conceptual ERD substitute for foundation planning. Actual SQLAlchemy models, PostgreSQL DDL, Alembic revisions, indexes, retention policies and transaction tests belong to CQ-01/CQ-02 after the contracts are reviewed. No database has been provisioned.
