from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_security_threat_model_preserves_evidence_boundaries() -> None:
    model = (ROOT / "docs/CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md").read_text(encoding="utf-8")
    assert "IMPLEMENTATION NOT VERIFIED" in model
    assert "CQ00-04 remains PARTIAL" in model
    assert "No production security control is certified" in model
    assert "NOT RUN" in model


def test_security_model_covers_stride_and_privacy() -> None:
    model = (ROOT / "docs/CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md").read_text(encoding="utf-8")
    for token in ("Spoofing", "Tampering", "Repudiation", "Information disclosure", "Denial of service", "Elevation"):
        assert token in model
    for token in ("data inventory", "Retention and deletion", "child", "cross-border", "DPIA"):
        assert token.lower() in model.lower()


def test_security_model_preserves_deferred_lab_boundary() -> None:
    model = (ROOT / "docs/CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md").read_text(encoding="utf-8").lower()
    for token in ("default-deny", "cloud metadata", "short-lived credentials", "teardown", "emergency stop"):
        assert token in model
    assert "no lab is approved by this document" in model


def test_verification_plan_does_not_claim_tests_ran() -> None:
    plan = (ROOT / "docs/CQ-00.6-SECURITY-VERIFICATION-PLAN.md").read_text(encoding="utf-8")
    assert "None of the tests below is represented as executed" in plan
    assert "NOT RUN" in plan
    assert "two distinct learner identities" in plan


def test_security_controls_are_not_claimed_as_implemented() -> None:
    model = (ROOT / "docs/CQ-00.6-SECURITY-PRIVACY-THREAT-MODEL.md").read_text(encoding="utf-8")
    assert "Identity provider not selected; NOT IMPLEMENTED" in model
    assert "runtime NOT IMPLEMENTED" in model
    assert "No production deployment" in model
