# Python Dependency Locking

**Checkpoint:** CQ-00.3  
**Status:** CI lock-generation and verification workflow implemented; canonical lock not yet committed.

## Source of truth

`pyproject.toml` is the canonical declaration of direct Python dependencies and optional groups (`api`, `test`, `dev`). Avoid maintaining a second independently edited list of direct pins.

## Resolution procedure

The main `foundation-ci` workflow pins Python 3.12.16 and `pip-tools==7.6.2`, resolves all declared extras, and installs from the generated hash-locked resolution before migration and test execution:

```sh
python -m piptools compile \
  --all-extras \
  --generate-hashes \
  --allow-unsafe \
  --resolver=backtracking \
  --output-file=requirements-lock.txt \
  pyproject.toml
```

The resulting file must contain exact versions and SHA-256 hashes for all resolved distributions. CI installs it using pip hash-checking mode:

```sh
python -m pip install --require-hashes -r requirements-lock.txt
```

## Acceptance requirements

1. The generated lock resolves successfully for the declared Python runtime.
2. Every transitive requirement is pinned and has one or more SHA-256 artifact hashes.
3. A clean CI job installs only from the generated lock in hash-checking mode.
4. `pip check` reports no broken requirements.
5. Alembic upgrade and the complete PostgreSQL-backed test suite pass after the locked install.
6. The generated lock is reviewed and committed; a generated CI artifact alone is not a repository lock.
7. CI later switches to consuming the committed lock and checks that the lock is up to date with `pyproject.toml`.
8. Dependency updates are deliberate, reviewed changes; no routine CI auto-upgrade.

## Scope and limitations

- The lock compiler is version-pinned but its own installation is not yet hash-locked.
- GitHub-hosted runner images and the PostgreSQL service image are not yet pinned by immutable image digest.
- Python 3.12.16 is pinned for this lock-generation workflow; broader Python-version support is not claimed.
- Android and web toolchains are outside this checkpoint.
- Hash locking verifies downloaded distribution artifacts against recorded hashes; it does not by itself establish publisher trust, provenance, vulnerability status or a hermetic build.

CQ00-05 remains PARTIAL until a successful run is inspected, the generated lock is reviewed and committed, and CI is changed to consume that committed lock rather than regenerate it on every run.