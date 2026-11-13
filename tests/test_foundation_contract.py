from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_foundation_documents_exist() -> None:
    required = [
        "README.md",
        "docs/PRODUCT-BASELINE.md",
        "docs/ARCHITECTURE.md",
        "docs/SECURITY-AND-PRIVACY.md",
        "docs/CQ-00-ACCEPTANCE.md",
        "docs/TRACEABILITY.md",
        "docs/BRANCH-AND-CHANGE-POLICY.md",
        "docs/DECISIONS/ADR-0001-STACK.md",
        "docs/DECISIONS/ADR-0002-MODULAR-MONOLITH.md",
        "docs/DECISIONS/ADR-0003-SERVER-AUTHORITY.md",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing, f"Missing foundation documents: {missing}"


def test_foundation_does_not_claim_application_is_complete() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "CQ-00" in readme
    assert "No production application" in readme


def test_acceptance_register_preserves_unverified_states() -> None:
    acceptance = (ROOT / "docs/CQ-00-ACCEPTANCE.md").read_text(encoding="utf-8")
    assert "| NOT RUN |" in acceptance
    assert "| NOT STARTED |" in acceptance
    assert "CQ-01 remains blocked" in acceptance
