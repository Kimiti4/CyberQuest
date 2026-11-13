# Branch, Change and Evidence Policy

## Branches

- `main`: integration branch; no direct feature development.
- `feat/<checkpoint>-<description>`: checkpoint work.
- `fix/<issue>-<description>`: bounded defect correction.
- `docs/<topic>`: documentation-only work.

Initial working branch: `feat/cq-00-foundation`.

## Pull requests

Use draft PRs while work is incomplete. Every PR records scope, non-goals, risk, tests run, tests not run, evidence, known limitations and rollback considerations. Required CI must pass before merge. Do not merge with unresolved critical/high security findings.

## Commits

Use scoped messages, e.g. `docs(cq-00): establish product and architecture baseline`.

## Evidence discipline

Record commit SHA, workflow run, commands, environment and result. Preserve failures and explain exclusions. Never claim a test passed if it was not executed. Static inspection, mocks and simulations are not runtime proof. Pin baselines before regression-sensitive changes. Avoid force pushes to shared branches.
