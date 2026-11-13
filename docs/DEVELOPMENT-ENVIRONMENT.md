# Development Environment Baseline

**Status: backend foundation verified; Android and web scaffolds introduced in CQ-00.5; current clean-build evidence pending.**

## Verified backend CI environment

- Runner: GitHub-hosted `ubuntu-24.04`; image contents are maintained by GitHub and are not a byte-for-byte immutable runner image.
- Python: `3.12.16`.
- Dependency source: `pyproject.toml` optional groups and committed `requirements-lock.txt`.
- Lock compiler: `pip-tools==7.6.2` (version-pinned; its bootstrap install is not itself hash-locked).
- Installation: pip `--require-hashes`; CI regenerates a temporary lock and diffs it against the committed lock.
- PostgreSQL: version 16 CI service.
- Evidence: workflow run `43494824837`, candidate `ccd7ddc`; committed lock drift check, hash-enforced installation, `pip check`, Alembic migration/schema/downgrade/re-upgrade and 18-test suite passed (1 warning).

This verifies the existing backend foundation scope, not production deployment or complete application behavior.

## Android environment

Candidate stack: Kotlin, Jetpack Compose, Gradle Wrapper, Android Gradle Plugin and JDK. The minimal Android Compose project, Gradle wrapper scripts and checksum-verified wrapper payload are now present on the CQ-00.5 branch. The Android SDK build/test job has not yet supplied a verified result.

At scaffold creation, choose a mutually compatible Kotlin/AGP/Gradle/JDK tuple from official compatibility matrices. Commit wrapper scripts/JAR and distribution checksum, dependency verification configuration, exact JDK patch, compile/target SDK and build-tools versions. CI must run clean assemble, unit tests, lint and emulator smoke/instrumentation tests.

## Web environment

Candidate stack: Next.js 16, TypeScript, Node.js LTS and one package manager. Next.js 16 is listed as Active LTS and official installation documentation specifies Node.js 20.9 minimum. CQ-00.5 pins Node 24.22.3, npm 11.19.1, Next.js 16.4.0, React 19.3.0 and TypeScript 5.9.3. The first CI run bootstraps package-lock.json as a temporary artifact; commit that generated lock and rerun CI before declaring reproducibility.

Commit the selected package manager's lockfile and use immutable installation (`npm ci` if npm is selected). CI must run lint, typecheck, unit tests and production build; add browser smoke tests before integration claims.

## Local Python setup

1. Install Python 3.12.16.
2. Create and activate a virtual environment.
3. Install the committed lock with `python -m pip install --require-hashes -r requirements-lock.txt`.
4. Run `python -m pip check`.
5. Configure a disposable PostgreSQL 16 database and `DATABASE_URL` for migrations/integration tests.
6. Run `python -m pytest`.

## Secrets and data

- Never commit `.env`, access tokens, private keys, signing keys or real learner data.
- CI receives minimum required permissions; no deployment credentials are configured.
- Never put secrets in workflow output or test fixtures.

## Deferred environment work

- Hash-lock the bootstrap lock compiler and assess artifact provenance.
- Pin immutable runner/container images where operationally justified.
- Review the Android clean-build CI result and add emulator-backed smoke verification.
- Commit the generated npm lock artifact and rerun the web job using npm ci from the committed lock.
- Contract-test OpenAPI and client compatibility.
- Select production identity/session design and provider only after threat-model review.
- Execute backup restore and document provider cost/data-residency decisions.

Until Android and web builds execute from clean pinned environments, full cross-platform toolchain readiness remains PARTIAL.