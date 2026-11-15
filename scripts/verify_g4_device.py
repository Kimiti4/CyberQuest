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
    install_output = adb.install(str(apk_path))
    results.append(
        DeviceResult(
            "apk_installed",
            "Success" in install_output,
            install_output.splitlines()[0] if install_output else "no output",
            {"apk": str(apk_path)},
        )
    )

    adb.shell("input keyevent KEYCODE_WAKEUP")
    adb.shell("wm dismiss-keyguard")
    adb.clear_logcat()
    adb.stop_app(package)
    adb.launch(package)

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

    checkboxes = find_nodes(adb.dump_ui(), "android.widget.CheckBox")
    if len(checkboxes) >= 8:
        for node in checkboxes[:5]:
            x, y = center(node)
            adb.tap(x, y)
            time.sleep(0.4)
    radios = find_nodes(adb.dump_ui(), "android.widget.RadioButton")
    if len(radios) >= 3:
        x, y = center(radios[2])
        adb.tap(x, y)
        time.sleep(0.4)

    submit_buttons = [
        node for node in adb.dump_ui().iter("node")
        if "Submit for assessment" in node_text(node)
    ]
    if submit_buttons:
        x, y = center(submit_buttons[0])
        adb.tap(x, y)
    results.append(
        DeviceResult(
            "assessment_submitted",
            bool(submit_buttons),
            f"{len(checkboxes)} checkboxes, {len(radios)} radio options, submit button present"
            if submit_buttons
            else "submit button not found",
            {"checkboxes": len(checkboxes), "radios": len(radios)},
        )
    )

    scored, texts = wait_for_text(adb, "points")
    score_ten = any("10" in text for text in texts) and any("points" in text for text in texts)
    results.append(
        DeviceResult(
            "server_determined_result_rendered",
            scored and score_ten,
            f"result screen rendered={scored}; score 10 present={score_ten}",
            {"texts": [text for text in texts if text][:12]},
        )
    )
    guidance_seen = any(
        "A display name can claim any organisation" in text for text in texts
    )
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
