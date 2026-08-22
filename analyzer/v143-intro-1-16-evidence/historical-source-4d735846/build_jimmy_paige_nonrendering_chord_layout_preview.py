from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SIDECAR_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar-report.json"
JSON_OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview.json"
TEXT_OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview.txt"
VALIDATION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview-report.json"

STRING_ORDER = ["e", "B", "G", "D", "A", "E"]


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell_map(row: dict[str, Any]) -> dict[str, str]:
    return {
        str(cell["stringName"]): str(cell["display"])
        for cell in row.get("renderCells", [])
    }


def build_ascii_measure(measure_number: int, rows: list[dict[str, Any]]) -> list[str]:
    ordered = sorted(rows, key=lambda row: (float(row["targetPhase"]), int(row["attackNumber"])))
    labels = []
    for row in ordered:
        for label in row.get("chordLabels", []):
            if label not in labels:
                labels.append(label)

    output = [f"Measure {measure_number} | {' / '.join(labels) if labels else 'Chord'}"]
    output.append("phase  " + "  ".join(f"{float(row['targetPhase']):.2f}" for row in ordered))

    for string_name in STRING_ORDER:
        displays = [cell_map(row).get(string_name, "-") for row in ordered]
        output.append(f"{string_name:>2} | " + "  ".join(f"{display:>2}" for display in displays))

    output.append("mode   " + "  ".join(row["resolutionMode"] for row in ordered))
    return output


def main() -> None:
    sidecar = load(SIDECAR_PATH)
    report = load(REPORT_PATH)

    if not bool(report.get("rendererSidecarBenchmarkPassed", False)):
        raise RuntimeError("Renderer sidecar benchmark is not passing")
    if not bool(report.get("readyForNonRenderingLayoutPreview", False)):
        raise RuntimeError("Renderer sidecar is not ready for layout preview")

    sidecar_sha_before = sha256(SIDECAR_PATH)
    report_sha_before = sha256(REPORT_PATH)

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in sidecar.get("rows", []):
        grouped[int(row["measureNumber"])].append(row)

    measure_numbers = sorted(grouped)
    sections = [
        {
            "sectionRole": "training-professional-reference",
            "measureNumbers": [number for number in measure_numbers if 33 <= number <= 38],
        },
        {
            "sectionRole": "heldout-shadow-resolved",
            "measureNumbers": [number for number in measure_numbers if 63 <= number <= 67],
        },
    ]

    preview_measures: list[dict[str, Any]] = []
    text_lines = [
        "JIMMY PAIGE CHORD LAYOUT PREVIEW",
        "NON-RENDERING / BENCHMARK ONLY",
        "Professional PDF remains scoring authority",
        "",
    ]

    invalid_rows: list[dict[str, Any]] = []

    for section in sections:
        text_lines.append(f"[{section['sectionRole']}]")
        for measure_number in section["measureNumbers"]:
            rows = sorted(
                grouped[measure_number],
                key=lambda row: (float(row["targetPhase"]), int(row["attackNumber"])),
            )
            for row in rows:
                if row.get("rendererMayConsume") is not False or row.get("productionMayConsume") is not False:
                    invalid_rows.append(row)
                if len(row.get("renderCells", [])) != 6:
                    invalid_rows.append(row)

            preview_measures.append(
                {
                    "sectionRole": section["sectionRole"],
                    "measureNumber": measure_number,
                    "attackCount": len(rows),
                    "rows": rows,
                    "layoutOnly": True,
                    "rendererMayConsume": False,
                    "productionMayConsume": False,
                }
            )
            text_lines.extend(build_ascii_measure(measure_number, rows))
            text_lines.append("")

    json_payload = {
        "previewVersion": 1,
        "previewType": "non-rendering-protected-chord-layout",
        "mode": "layout-preview-only",
        "measureCount": len(preview_measures),
        "attackCount": sum(item["attackCount"] for item in preview_measures),
        "measures": preview_measures,
        "rendererMayConsume": False,
        "productionMayConsume": False,
        "sourceEventsMutated": False,
        "syntheticAttacksCreated": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    JSON_OUTPUT_PATH.write_text(json.dumps(json_payload, indent=2) + "\n", encoding="utf-8")
    TEXT_OUTPUT_PATH.write_text("\n".join(text_lines) + "\n", encoding="utf-8")

    sidecar_sha_after = sha256(SIDECAR_PATH)
    report_sha_after = sha256(REPORT_PATH)

    checks = {
        "measureCount11": len(preview_measures) == 11,
        "attackCount44": json_payload["attackCount"] == 44,
        "invalidRowsZero": len(invalid_rows) == 0,
        "sidecarShaUnchanged": sidecar_sha_before == sidecar_sha_after,
        "sidecarReportShaUnchanged": report_sha_before == report_sha_after,
        "rendererMayConsumeFalse": json_payload["rendererMayConsume"] is False,
        "productionMayConsumeFalse": json_payload["productionMayConsume"] is False,
    }
    passed = all(checks.values())

    validation = {
        "benchmarkVersion": 1,
        "benchmarkType": "non-rendering-protected-chord-layout-preview",
        "checks": checks,
        "measureCount": len(preview_measures),
        "attackCount": json_payload["attackCount"],
        "invalidRows": invalid_rows,
        "layoutPreviewPassed": passed,
        "readyForHumanLayoutInspection": passed,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "protectedPitchCheckpointChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
        "jsonPreview": str(JSON_OUTPUT_PATH.relative_to(REPO_ROOT)),
        "textPreview": str(TEXT_OUTPUT_PATH.relative_to(REPO_ROOT)),
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    print("Non-rendering chord layout preview complete")
    print(f"Measures laid out: {len(preview_measures)}/11")
    print(f"Chord attacks laid out: {json_payload['attackCount']}/44")
    print(f"Invalid layout rows: {len(invalid_rows)}")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"Layout preview passed: {passed}")
    print(f"Ready for human layout inspection: {passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Text preview: {TEXT_OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"JSON preview: {JSON_OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {VALIDATION_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
