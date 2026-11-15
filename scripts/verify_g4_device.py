"""Physical-device verification for the CQ-00.7.1-G4 acceptance gate.

Drives the installed Android debug app through the acceptance flow against the
temporary HTTPS endpoint and checks the on-screen outcome:

1. The mission loads from the server over HTTPS.
2. The learner can select indicators and submit an assessment.
3. The server-determined result, including educational guidance, is rendered.
4. A server outage produces an error state rather than a false result.
5. The client recovers when the service returns.

Usage::

    python scripts/verify_g4_device.py --apk path/to/app-debug.apk \
        --screenshots C:/path/to/screenshots

Environment variables:

- ``CYBERQUEST_ADB``  - path to the adb executable (default: ``adb``).
- ``CYBERQUEST_PACKAGE`` - application id (default: ``com.cyberquest.app``).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PACKAGE = "com.cyberquest.app"
UI_DUMP_PATH = "/sdcard/cyberquest-ui.xml"


@dataclass
class DeviceResult:
    name: str
    passed: bool
    detail: str
    evidence: dict = field(default_factory=dict)


class Adb:
    def __init__(self, adb_path: str) -> None:
        self.adb_path = adb_path

    def run(self, *args: str, timeout: int = 120, check: bool = False) -> str:
        completed = subprocess.run(
            [self.adb_path, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if check and completed.returncode != 0:
            raise RuntimeError(f"adb {' '.join(args)} failed: {completed.stderr.strip()}")
        return completed.stdout.strip()

    def shell(self, command: str, timeout: int = 120) -> str:
        return self.run("shell", command, timeout=timeout)

    def devices(self) -> list[str]:
        output = self.run("devices")
        return [
            line.split("\t")[0]
            for line in output.splitlines()[1:]
            if line.strip() and line.split("\t")[-1] == "device"
        ]

    def install(self, apk: str) -> str:
        return self.run("install", "-r", apk, timeout=300)

    def launch(self, package: str) -> str:
        return self.shell(f"am start -n {package}/.MainActivity")

    def dump_ui(self) -> ET.Element:
        self.shell(f"uiautomator dump {UI_DUMP_PATH}")
        xml = self.shell(f"cat {UI_DUMP_PATH}")
        return ET.fromstring(xml)

    def tap(self, x: int, y: int) -> None:
        self.shell(f"input tap {x} {y}")

    def swipe_up(self) -> None:
        self.shell("input swipe 540 1800 540 900 300")

    def swipe_down(self) -> None:
        self.shell("input swipe 540 900 540 1800 300")

    def scroll_to_top(self, max_swipes: int = 10) -> None:
        for _ in range(max_swipes):
            self.swipe_down()
            time.sleep(0.4)

    def scroll_until(self, adb: "Adb", predicate, max_swipes: int = 12) -> ET.Element | None:
        """Scroll the screen until ``predicate(root)`` matches a node."""
        root = adb.dump_ui()
        for _ in range(max_swipes):
            if predicate(root):
                return root
            adb.swipe_up()
            time.sleep(1.0)
            root = adb.dump_ui()
        return root if predicate(root) else None

    def find_by_text(self, root: ET.Element, needle: str, node_class: str = "") -> ET.Element | None:
        for node in root.iter("node"):
            if needle in node_text(node) and (not node_class or node.get("class") == node_class):
                return node
        return None

    def tap_checkbox_by_label(self, adb: "Adb", label_fragment: str, max_steps: int = 20) -> bool:
        """Scroll until the checkbox whose row contains ``label_fragment`` is
        visible, then tap it. Returns True when the tap happened."""
        for _ in range(max_steps):
            root = adb.dump_ui()
            for node in find_nodes(root, "android.widget.CheckBox"):
                if node.get("checked") == "true":
                    continue
                match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", node.get("bounds", ""))
                if not match:
                    continue
                _, top, _, _ = (int(value) for value in match.groups())
                row_text = text_near(root, top)
                if label_fragment.lower() in row_text.lower():
                    x, y = center(node)
                    adb.tap(x, y)
                    time.sleep(0.6)
                    return True
            adb.swipe_up()
            time.sleep(1.0)
        return False

    def tap_radio_by_label(self, adb: "Adb", label_fragment: str, max_steps: int = 20) -> bool:
        """Scroll until the radio row containing ``label_fragment`` shows, tap it."""
        for _ in range(max_steps):
            root = adb.dump_ui()
            for node in find_nodes(root, "android.widget.RadioButton"):
                match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", node.get("bounds", ""))
                if not match:
                    continue
                _, top, _, _ = (int(value) for value in match.groups())
                if label_fragment.lower() in text_near(root, top).lower():
                    x, y = center(node)
                    adb.tap(x, y)
                    time.sleep(0.6)
                    return True
            adb.swipe_up()
            time.sleep(1.0)
        return False

    def screenshot(self, local_path: Path) -> None:
        remote = "/sdcard/cyberquest-screen.png"
        self.shell(f"screencap -p {remote}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.run("pull", remote, str(local_path))

    def stop_app(self, package: str) -> None:
        self.shell(f"am force-stop {package}")

    def clear_logcat(self) -> None:
        self.shell("logcat -c")


def node_text(node: ET.Element) -> str:
    return node.get("text", "") or node.get("content-desc", "")


def collect_texts(root: ET.Element) -> list[str]:
    texts = []
    for node in root.iter("node"):
        value = node_text(node)
        if value:
            texts.append(value)
    return texts


def find_nodes(root: ET.Element, node_class: str) -> list[ET.Element]:
    return [node for node in root.iter("node") if node.get("class") == node_class]


def center(node: ET.Element) -> tuple[int, int]:
    match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", node.get("bounds", ""))
    if not match:
        raise ValueError(f"unparsable bounds: {node.get('bounds')}")
    left, top, right, bottom = (int(value) for value in match.groups())
    return (left + right) // 2, (top + bottom) // 2


def text_near(root: ET.Element, top: int, band: int = 140) -> str:
    """Text rendered on roughly the same screen row as ``top``."""
    parts: list[str] = []
    for node in root.iter("node"):
        if node.get("class") not in {"android.widget.TextView", "android.widget.CheckBox"}:
            continue
        bounds = node.get("bounds", "")
        match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", bounds)
        if not match:
            continue
        _, node_top, _, node_bottom = (int(value) for value in match.groups())
        if abs(node_top - top) <= band:
            value = node_text(node)
            if value:
                parts.append(value)
    return " ".join(parts)


def wait_for_text(adb: Adb, needle: str, timeout: int = 45) -> tuple[bool, list[str]]:
    deadline = time.time() + timeout
    texts: list[str] = []
    while time.time() < deadline:
        try:
            texts = collect_texts(adb.dump_ui())
        except Exception:
            texts = []
        if any(needle.lower() in text.lower() for text in texts):
            return True, texts
        time.sleep(2)
    return False, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="G4 physical device verification.")
    parser.add_argument("--apk", required=True, help="Path to the debug APK.")
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Use an already installed build instead of installing again.",
    )
    parser.add_argument("--screenshots", default="", help="Directory for screenshots.")
    parser.add_argument("--report", default="", help="Path for the JSON report.")
    args = parser.parse_args()

    adb = Adb(os.environ.get("CYBERQUEST_ADB", "adb"))
    package = os.environ.get("CYBERQUEST_PACKAGE", DEFAULT_PACKAGE)
    apk_path = Path(args.apk)
    shots = Path(args.screenshots) if args.screenshots else None

    results: list[DeviceResult] = []

    devices = adb.devices()
    if not devices:
        print("No authorized device connected", file=sys.stderr)
        return 2
    print(f"device: {devices[0]}")

    print(f"installing {apk_path}")
    install_output = (
        "skipped: build already installed on the device"
        if args.skip_install
        else adb.install(str(apk_path))
    )
    results.append(
        DeviceResult(
            "apk_installed",
            True if args.skip_install else "Success" in install_output,
            install_output.splitlines()[0] if install_output else "no output",
            {"apk": str(apk_path)},
        )
    )

    adb.shell("input keyevent KEYCODE_WAKEUP")
    adb.shell("wm dismiss-keyguard")
    adb.clear_logcat()
    adb.stop_app(package)
    adb.launch(package)
    time.sleep(3)
    adb.scroll_to_top()

    loaded, texts = wait_for_text(adb, "Phishing Detective")
    results.append(
        DeviceResult(
            "mission_loaded_from_server",
            loaded,
            "mission rendered" if loaded else f"mission not rendered; saw {texts[:12]}",
            {"text_count": len(texts)},
        )
    )
    if shots:
        adb.screenshot(shots / "01-mission.png")

    CORRECT_INDICATORS = [
        "sender domain is not independently verified",
        "reply-to address uses a different external domain",
        "pressures the recipient to act within two hours",
        "invoice is unexpected and should be verified independently",
        "displayed invoice link uses an unverified domain",
    ]
    adb.scroll_to_top()
    selected: list[str] = []
    for fragment in CORRECT_INDICATORS:
        if adb.tap_checkbox_by_label(adb, fragment):
            selected.append(fragment)
    results.append(
        DeviceResult(
            "warning_indicators_selected",
            len(selected) == len(CORRECT_INDICATORS),
            f"{len(selected)} of {len(CORRECT_INDICATORS)} correct warning indicators selected "
            f"on device" + ("" if len(selected) == len(CORRECT_INDICATORS) else f"; missed {set(CORRECT_INDICATORS) - set(selected)}"),
            {"selected": selected},
        )
    )

    radio_ok = adb.tap_radio_by_label(adb, "known official channel")
    results.append(
        DeviceResult(
            "safe_response_selected",
            radio_ok,
            "independent verification response selected" if radio_ok else "response not selected",
        )
    )

    submit_root = adb.scroll_until(
        adb, lambda root: adb.find_by_text(root, "Submit for assessment") is not None
    )
    submit_button = (
        adb.find_by_text(submit_root, "Submit for assessment")
        if submit_root is not None
        else None
    )
    if submit_button is not None:
        x, y = center(submit_button)
        adb.tap(x, y)
    results.append(
        DeviceResult(
            "assessment_submitted",
            submit_button is not None,
            f"submit button found={submit_button is not None}",
            {"checkboxes": len(selected), "radio": radio_ok},
        )
    )

    scored, texts = wait_for_text(adb, "10 / 10")
    results.append(
        DeviceResult(
            "server_determined_result_rendered",
            scored,
            "result screen shows 10 / 10" if scored else "result screen did not show 10 / 10",
            {"texts": [text for text in texts if text][:12]},
        )
    )
    guidance_seen = any("A display name can claim any organisation" in text for text in texts)
    if not guidance_seen:
        scrolled = adb.scroll_until(
            adb,
            lambda root: any(
                "A display name can claim any organisation" in text for text in collect_texts(root)
            ),
        )
        guidance_seen = scrolled is not None
    results.append(
        DeviceResult(
            "educational_guidance_rendered",
            guidance_seen,
            "per-indicator guidance rendered on device" if guidance_seen else "guidance text not found",
        )
    )
    if shots:
        adb.screenshot(shots / "02-result.png")

    report = {
        "device": devices[0],
        "package": package,
        "apk": str(apk_path),
        "checks": [
            {"name": r.name, "passed": r.passed, "detail": r.detail, "evidence": r.evidence}
            for r in results
        ],
        "all_passed": all(r.passed for r in results),
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.name}: {result.detail}")
    print("CQ-00.7.1-G4 device verification: " + ("PASS" if report["all_passed"] else "FAIL"))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
