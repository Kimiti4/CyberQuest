# Development Environment Baseline

**Status: backend foundation, Android/Linux build, Windows wrapper smoke and web build foundations verified in CI on candidate `0b1c2d5642dd5b8641f519c586b6a8f60bbc9b61`.**

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

Candidate stack: Kotlin, Jetpack Compose, Gradle Wrapper, Android Gradle Plugin and JDK. The minimal Android Compose project, Gradle wrapper scripts and checksum-verified wrapper payload are now present on the CQ-00.5 branch. Linux CI verified clean Gradle build, JUnit execution, debug APK assembly and lint with Gradle build cache disabled; Windows CI verified wrapper materialization, SHA-256 and Gradle startup.

Current Android pins are JDK 17.0.17+10, AGP 8.11.1, Kotlin/Compose compiler 2.2.21, Gradle 8.13 and Android SDK/build-tools 36/36.0.0. The Gradle wrapper payload and distribution are checksum-verified. CI runs clean assemble, unit tests and lint; emulator smoke/instrumentation remains deferred.

## Web environment

Candidate stack: Next.js 16, TypeScript, Node.js LTS and npm. CQ-00.5 pins Node 24.22.3, npm 11.19.1, Next.js 16.4.0, React 19.3.0 and TypeScript 5.9.3. `web/package-lock.json` is committed (308 package entries; 307 resolved packages with integrity hashes). CI runs `npm ci`, TypeScript typecheck, five Node contract tests, warning-free Redocly lint and Next.js production build.

Browser smoke tests remain required before claiming cross-client integration.

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
- Add emulator/instrumentation smoke tests.
- Contract-test OpenAPI against a live backend and validate Android/web API compatibility.
- Select production identity/session design and provider only after threat-model review.
- Execute backup restore and document provider cost/data-residency decisions.

CQ-00.5 build foundations PASS on candidate `0b1c2d5642dd5b8641f519c586b6a8f60bbc9b61`. Emulator/instrumentation, API/client integration and production readiness remain unverified.