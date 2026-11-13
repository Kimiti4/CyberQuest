# ADR-0004: Unified Platform and Cross-Pillar Boundaries

- **Status:** ACCEPTED — founder ratified 2026-11-14
- **Date:** 2026-11-13
- **Ratification:** Founder approval recorded in the CYBERQUEST project conversation on 2026-11-14.
- **Checkpoint:** CQ-00.4

## Context

Four experiences (Cyber Academy, Cyber Labs, Cyber Defense and Cyber Arena) would duplicate identity, curriculum, assessment, progress, audit and entitlement capabilities if built as separate applications or services. That duplication conflicts with the initial MVP budget and increases operational risk.

## Decision

Keep one product and one backend modular monolith. The four pillars are product experiences and bounded capability areas, not independent platforms or microservices. Android and web are clients of one versioned HTTPS API. PostgreSQL remains the durable system of record.

Cyber Labs executable infrastructure and Cyber Arena competition hosting remain deferred. Any future executable lab requires independently verified isolation and lifecycle controls.

## Consequences

**Positive:** one account and progression model; shared authoritative assessment and competency rules; lower hosting complexity; reuse of mission/content capabilities.

**Risks:** modular boundaries require enforcement tests; shared backend can become coupled if modules bypass interfaces; future workload separation may eventually be justified by measured evidence, not speculation.

## Authority invariants

- Server owns assessment outcomes, XP, mastery, achievements and entitlements.
- Client evidence is untrusted until validated.
- Offline sync submits events; it does not mint rewards or mastery.
- AI cannot autonomously award competencies or execute arbitrary code.
- This ADR authorizes no real-world offensive operation.

## Alternatives rejected

1. Four separate apps/services: duplicate core capabilities and increase cost.
2. Microservices from inception: operational complexity without measured scale or separate teams.
3. Client-side authority: permits tampering with assessment and rewards.
4. Executable public labs in MVP: unsafe and unsupported by current isolation evidence.

## Review triggers

Revisit only when measured scaling, team ownership, regulatory or operational needs demonstrate a concrete limitation in the modular monolith.