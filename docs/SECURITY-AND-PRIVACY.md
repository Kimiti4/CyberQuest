# Security, Privacy and Cyber-Safety Baseline

**Status: requirements baseline updated in CQ-00.6; controls are not certified or generally implemented.**

## Governing requirements

- Deny by default; least privilege; server-side object-level authorization for every learner-owned resource.
- Validate token issuer, audience, signature, algorithm, expiry and key rotation against an explicitly selected identity provider.
- Secure account recovery and session lifecycle; MFA for privileged roles.
- Treat client input, offline events, content imports and AI output as untrusted.
- Keep assessment, mission completion, XP, mastery, achievements and entitlements server-authoritative.
- Validate all inputs at trust boundaries; bound payloads, pagination, timeouts and resource use; rate-limit abuse-sensitive operations.
- Encrypt transport; protect tokens and stored data; redact logs; keep secrets out of source, bundles, CI and fixtures.
- Audit privileged/security-relevant actions without retaining credentials or unnecessary learner content.
- Minimize personal data; document purpose, lawful basis, access, retention, deletion/export and processor sharing before collection.
- Review dependency provenance, vulnerabilities, backup restoration and incident response before release.
- Future lab launch fails closed unless every isolation and lifecycle control is independently verified.

## Checkpoint documents

- [CQ-00.6 threat model and privacy inventory](CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md)
- [CQ-00.6 security verification plan](CQ-00.6-SECURITY-VERIFICATION-PLAN.md)
- [Risk register](RISK-REGISTER.md)
- [Operations and recovery baseline](OPERATIONS-AND-RECOVERY.md)

The threat model covers STRIDE, system assets, actors, trust boundaries, privacy data categories, Kenyan legal review work, child-safety requirements, cyber-safety and future lab containment. It is a design baseline only.

## Privacy and legal boundary

CYBERQUEST targets Kenya and may later serve international learners. Before live personal-data collection, obtain qualified Kenyan privacy/legal review of the Data Protection Act, 2019; applicable 2021 regulations; ODPC guidance; controller/processor roles; ODPC registration applicability; lawful bases; notices; rights workflows; processor contracts; cross-border transfers; retention and incident obligations.

No minor-facing service may launch until age scope, age assurance, parent/guardian consent mechanisms where required, best-interests safeguards, child-friendly notices and safeguarding workflows have been reviewed and approved. Do not assume consent is the lawful basis for every processing purpose.

This baseline is not legal advice, a completed DPIA or a compliance certification.

## MVP cyber-safety boundaries

MVP activities are static lessons and deterministic simulations using fictional data and targets. No live credential collection, malware execution, uncontrolled network scanning, arbitrary commands or learner-controlled code execution.

Do not request contacts, SMS, call logs, precise location, installed-app inventory, files, microphone or camera for MVP learning. Any future device permission requires a documented purpose, least privilege, clear notice and separate approval.

## Future technical labs

Executable labs remain deferred. Any future launch requires disposable isolated environments, immutable approved images, no privileged mode/host mounts/socket, externally enforced default-deny egress, private/loopback/link-local/cloud-metadata blocking, resource quotas, short-lived credentials, expiry, verified teardown, audit, emergency stop and independent escape/network testing.

## Claims and evidence

A simulated detection is not a real device scan. A lesson is not a security control. A quiz score is not professional certification. No product claim may exceed independently verified functionality.
