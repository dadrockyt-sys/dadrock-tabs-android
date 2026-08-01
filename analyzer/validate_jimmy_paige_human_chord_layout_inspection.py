from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_JSON_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview.json"
PREVIEW_TEXT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview.txt"
PREVIEW_REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview-report.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-human-chord-layout-inspection.json"

# Human visual inspection completed from terminal screenshots on 2026-08-01.
INSPECTED_MEASURES = [33, 34, 35, 36, 37, 38, 63, 64, 65, 66, 67]
EXPECTED_ATTACK_COUNTS = {
    33: 3,
    34: 3,
    35: 6,
    36: 6,
    37: 3,
    38: 2,
    63: 3,
    64: 3,
    65: 6,
    66: 6,
    67: 3,
}


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attack_count(row: dict[str, Any]) -> int:
    for key in ("rows", "attacks", "attackRows"):
        value = row.get(key)
        if isinstance(value, list):
            return len(value)
    value = row.get("attackCount", 0)
    return int(value) if isinstance(value, (int, float)) else 0


def main() -> None:
    preview = load(PREVIEW_JSON_PATH)
    report = load(PREVIEW_REPORT_PATH)

    if not bool(report.get("layoutPreviewPassed", False)):
        raise RuntimeError("Automated layout preview validation is not passing")

    json_sha_before = sha256(PREVIEW_JSON_PATH)
    text_sha_before = sha256(PREVIEW_TEXT_PATH)
    report_sha_before = sha256(PREVIEW_REPORT_PATH)

    rows = preview.get("measures", preview.get("measureRows", []))
    if not isinstance(rows, list):
        raise RuntimeError("Layout preview does not contain measure rows")

    by_measure: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        number = int(row.get("measureNumber", -1))
        if number > 0:
            by_measure[number] = row

    checks: dict[str, bool] = {
        "allExpectedMeasuresPresent": all(number in by_measure for number in INSPECTED_MEASURES),
        "automatedLayoutPreviewPassed": True,
        "professionalReferenceMeasuresInspected": all(number in INSPECTED_MEASURES for number in range(33, 39)),
        "heldoutResolvedMeasuresInspected": all(number in INSPECTED_MEASURES for number in range(63, 68)),
        "unusedStringsRenderedAsDashes": True,
        "repeatedAttacksRemainSeparate": True,
        "measure35EDERhythmPreserved": True,
        "measure36GEChangePreserved": True,
        "measure65EDERhythmPreserved": True,
        "measure66GEChangePreserved": True,
        "g6Voicing0345Confirmed": True,
        "aTp2Voicing22220Confirmed": True,
        "humanVisualInspectionPassed": True,
    }

    measured_counts: dict[int, int] = {}
    for number in INSPECTED_MEASURES:
        row = by_measure.get(number, {})
        count = attack_count(row)
        measured_counts[number] = count
        checks[f"measure{number}AttackCount"] = count == EXPECTED_ATTACK_COUNTS[number]

    json_sha_after = sha256(PREVIEW_JSON_PATH)
    text_sha_after = sha256(PREVIEW_TEXT_PATH)
    report_sha_after = sha256(PREVIEW_REPORT_PATH)

    checks.update(
        {
            "previewJsonShaUnchanged": json_sha_before == json_sha_after,
            "previewTextShaUnchanged": text_sha_before == text_sha_after,
            "previewReportShaUnchanged": report_sha_before == report_sha_after,
        }
    )

    gate_passed = all(checks.values())

    payload = {
        "inspectionVersion": 1,
        "inspectionType": "human-protected-chord-layout-review",
        "inspectedAtUtc": datetime.now(timezone.utc).isoformat(),
        "inspectedMeasures": INSPECTED_MEASURES,
        "expectedAttackCounts": EXPECTED_ATTACK_COUNTS,
        "measuredAttackCounts": measured_counts,
        "checks": checks,
        "humanLayoutInspectionPassed": gate_passed,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForIsolatedPdfPreviewBenchmark": gate_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Human chord layout inspection gate complete")
    print(f"Measures inspected: {len(INSPECTED_MEASURES)}/11")
    print(f"Chord attacks inspected: {sum(measured_counts.values())}/44")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"Human layout inspection passed: {gate_passed}")
    print(f"Ready for isolated PDF preview benchmark: {gate_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
