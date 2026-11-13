# Security, Privacy and Cyber-Safety Baseline

## Security principles

- Deny by default; least privilege; server-side object-level authorisation.
- Strong account recovery and session lifecycle; administrative MFA.
- Validate inputs at trust boundaries; rate-limit abuse-sensitive operations.
- Encrypt transport; protect stored data and backups; redact logs.
- Keep secrets out of source, logs, client bundles and test fixtures.
- Verify payment callbacks and enforce idempotency before introducing payments.
- Audit privileged administrative actions and security-relevant events.
- Scan dependencies and review high-risk changes.
- Test backup restoration, not merely backup creation.

## Threats to model

Account takeover/recovery abuse; broken object-level authorisation; cross-learner data exposure; XP/reward manipulation; mission tampering; malicious content; API abuse/denial of service; replay and duplicate sync; payment callback spoofing; insider misuse; future lab escape or unintended network access.

## Privacy

Collect only information needed to operate the product and evaluate learning. Document purpose, lawful basis, retention, deletion, export, access and incident handling before production collection. Avoid collecting contacts, SMS, call logs, precise location, files or unrelated device data for the MVP.

Legal review must cover Kenya's Data Protection Act and applicable regulations, international users, minors, age-appropriate design, consent and cross-border processing before launch. This document is an engineering baseline, not legal advice or a completed compliance assessment.

## Cyber-safety boundaries

MVP activities are static lessons and deterministic simulations. No real targets, credential harvesting, malware execution, uncontrolled network scanning or arbitrary command execution.

Future technical labs require isolated disposable environments, deny-by-default egress, private-host and cloud-metadata blocking, network policy enforced outside learner control, resource quotas, short-lived credentials, expiry/teardown and audit evidence. Lab launch must fail closed if any required control is absent.

## Claims and evidence

A simulated detection is not a real device scan. A lesson is not a security control. A quiz score is not professional certification. Product copy and telemetry must preserve these distinctions.
