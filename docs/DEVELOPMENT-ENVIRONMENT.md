# Development Environment Baseline

**Status: partially reproducible foundation; full-stack environment not yet certified.**

## Verified CI environment

- Runner: GitHub-hosted `ubuntu-24.04` (image contents remain maintained by GitHub; this is not a byte-for-byte immutable runner image)
- Python: 3.12.16 (observed in the successful CQ-00 workflow run)
- Pytest: 9.2.0
- Foundation suite: 7 tests passed on commit `0a6cbf62fe837990b38aa9ee519be289528f05c2` (workflow run 43469295571 and PR run 43469279581).

This is evidence for the foundation test harness only. It does not verify FastAPI, PostgreSQL, Android, web, migrations or deployment.

## Local Python setup

1. Install Python 3.12.x.
2. Create a virtual environment: `python -m venv .venv`.
3. Activate the environment.
4. Install the foundation test runner: `python -m pip install "pytest==9.2.0"`.
5. Run: `python -m pytest`.

The API dependency extra in `pyproject.toml` is a proposed dependency set and has not yet been installed or compatibility-tested as a whole.

## Environment and secrets

- Never commit `.env`, access tokens, private keys, signing keys or real learner data.
- Use a local untracked `.env` and provide a redacted `.env.example` only when application configuration is introduced.
- CI receives only the minimum required permissions; no deployment credentials are configured.
- Do not put secrets in workflow output or test fixtures.

## Deferred environment work

- Install and verify the complete backend dependency set; generate and review a lock file.
- Record the resolved GitHub Action commit SHAs and keep them pinned in CI.
- Select and pin Node.js, package manager and Android Gradle/JDK toolchains.
- Provision a disposable PostgreSQL test service and verify migrations/restore.
- Add local compose/devcontainer only after the service topology is selected.
- Document supported OS setup and resource requirements.

Until these steps are executed, the full development environment gate remains PARTIAL/NOT RUN.
