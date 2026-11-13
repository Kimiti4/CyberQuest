from pathlib import Path
import json

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


def test_openapi_contract_is_valid_json_with_expected_versioned_paths() -> None:
    contract = json.loads((ROOT / "openapi/cyberquest-v1.json").read_text(encoding="utf-8"))
    assert contract["openapi"] == "3.1.0"
    assert contract["info"]["version"] == "1.0.0"
    assert "/v1/mission-attempts" in contract["paths"]
    assert "/v1/me/progress" in contract["paths"]
    assert "/health/ready" in contract["paths"]


def test_mutating_mission_operations_require_idempotency_and_authentication() -> None:
    contract = json.loads((ROOT / "openapi/cyberquest-v1.json").read_text(encoding="utf-8"))
    for path in ["/v1/mission-attempts", "/v1/mission-attempts/{attemptId}/events"]:
        endpoint = contract["paths"][path]["post"]
        assert endpoint["security"] == [{"BearerAuth": []}]
        assert any(p["name"] == "Idempotency-Key" and p["required"] for p in endpoint["parameters"]]


def test_mission_event_receipt_does_not_claim_completion() -> None:
    contract = json.loads((ROOT / "openapi/cyberquest-v1.json").read_text(encoding="utf-8"))
    receipt = contract["components"]["schemas"]["EventReceipt"]
    assert receipt["properties"]["status"]["enum"] == ["accepted_for_evaluation"]


def test_data_model_documents_append_only_rewards_and_version_pinning() -> None:
    model = (ROOT / "docs/DATA-MODEL.md").read_text(encoding="utf-8")
    assert "XP ledger is append-only" in model
    assert "Attempt records pin immutable content/assessment versions" in model
    assert "no database schema or migration has been applied" in model
