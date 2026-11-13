from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cross_platform_architecture_preserves_server_authority() -> None:
    architecture = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    review = (ROOT / "docs/CQ-00.4-ARCHITECTURE-REVIEW.md").read_text(encoding="utf-8").lower()
    assert "server" in architecture and "authoritative" in architecture
    assert "offline" in architecture and "untrusted" in architecture
    assert "server remains authoritative" in review
    assert "client-submitted score" in review or "client-supplied xp" in review


def test_all_four_pillars_share_one_platform_baseline() -> None:
    review = (ROOT / "docs/CQ-00.4-ARCHITECTURE-REVIEW.md").read_text(encoding="utf-8").lower()
    for pillar in ("cyber academy", "cyber defense", "cyber labs", "cyber arena"):
        assert pillar in review
    assert "one product" in review
    assert "modular monolith" in review


def test_executable_labs_remain_deferred_pending_isolation_evidence() -> None:
    review = (ROOT / "docs/CQ-00.4-ARCHITECTURE-REVIEW.md").read_text(encoding="utf-8").lower()
    assert "executable labs are not enabled" in review
    for control in ("network isolation", "egress denial", "credential isolation", "teardown", "emergency stop"):
        assert control in review


def test_android_and_web_are_not_misrepresented_as_verified() -> None:
    matrix = (ROOT / "docs/CQ-00.4-TOOLCHAIN-MATRIX.md").read_text(encoding="utf-8").lower()
    assert "not implemented" in matrix
    assert "no android or web build is certified" in matrix
    assert "a version matrix alone is not a build result" in matrix


def test_offline_sync_contract_has_idempotency_and_version_conflict_rules() -> None:
    adr = (ROOT / "docs/DECISIONS/ADR-0005-OFFLINE-SYNC-AUTHORITY.md").read_text(encoding="utf-8").lower()
    assert "idempotency" in adr
    assert "stale-version" in adr
    assert "never award twice" in adr
    assert "client timestamps are advisory" in adr
