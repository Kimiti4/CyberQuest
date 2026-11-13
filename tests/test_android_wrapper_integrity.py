import base64
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gradle_wrapper_payload_matches_official_gradle_813_checksum() -> None:
    encoded = (ROOT / "android/gradle/wrapper/gradle-wrapper.jar.base64").read_text()
    wrapper_bytes = base64.b64decode("".join(encoded.split()), validate=True)
    assert sha256(wrapper_bytes).hexdigest() == (
        "81a82aaea5abcc8ff68b3dfcb58b3c3c429378efd98e7433460610fecd7ae45f"
    )


def test_gradle_distribution_is_pinned_and_checksum_verified() -> None:
    properties = (ROOT / "android/gradle/wrapper/gradle-wrapper.properties").read_text()
    assert "gradle-8.13-bin.zip" in properties
    assert (
        "distributionSha256Sum=20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78"
        in properties
    )
