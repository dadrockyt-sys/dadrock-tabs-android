from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INSPECTION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-human-isolated-adapter-pdf-inspection.json"
ADAPTER_OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output.json"
ADAPTER_REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output-report.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-production-renderer-dry-run.json"

EXPECTED_MEASURES = [33, 34, 35, 36, 37, 38, 63, 64, 65, 66, 67]


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError("No protected source event cache was found")


def main() -> None:
    inspection = load(INSPECTION_PATH)
    adapter_output = load(ADAPTER_OUTPUT_PATH)
    adapter_report = load(ADAPTER_REPORT_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(inspection.get("humanInspectionPassed", False)):
        raise RuntimeError("Human isolated adapter PDF inspection did not pass")
    if not bool(inspection.get("readyForProtectedProductionRendererDryRun", False)):
        raise RuntimeError("Human inspection gate is not ready for protected dry run")
    if not bool(adapter_report.get("benchmarkPassed", False)):
        raise RuntimeError("Isolated adapter output benchmark did not pass")

    source_sha_before = sha256(source_path)
    inspection_sha_before = sha256(INSPECTION_PATH)
    adapter_output_sha_before = sha256(ADAPTER_OUTPUT_PATH)
    adapter_report_sha_before = sha256(ADAPTER_REPORT_PATH)

    rows = adapter_output.get("rows", [])
    if not isinstance(rows, list):
        raise RuntimeError("Adapter output rows are not a list")

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    invalid_rows = 0

    for row in rows:
        if not isinstance(row, dict):
            invalid_rows += 1
            continue

        measure_number = row.get("measureNumber")
        attack_number = row.get("attackNumber")
        frets = row.get("fretsHighToLow")

        valid = (
            isinstance(measure_number, int)
            and isinstance(attack_number, int)
            and isinstance(frets, list)
            and len(frets) == 6
            and row.get("rendererCalled") is False
            and row.get("pdfCreated") is False
            and row.get("productionOutputCreated") is False
        )
        if not valid:
            invalid_rows += 1
            continue

        grouped[measure_number].append(
            {
                "measureNumber": measure_number,
                "attackNumber": attack_number,
                "phase": row.get("phase"),
                "fretsHighToLow": list(frets),
                "resolutionMode": row.get("resolutionMode"),
            }
        )

    dry_run_measures: list[dict[str, Any]] = []
    duplicate_attack_keys = 0

    for measure_number in sorted(grouped):
        measure_rows = sorted(
            grouped[measure_number],
            key=lambda item: (float(item.get("phase") or 0), int(item["attackNumber"])),
        )
        seen: set[tuple[int, int]] = set()
        for row in measure_rows:
            key = (row["measureNumber"], row["attackNumber"])
            if key in seen:
                duplicate_attack_keys += 1
            seen.add(key)

        dry_run_measures.append(
            {
                "measureNumber": measure_number,
                "attackCount": len(measure_rows),
                "rows": measure_rows,
                "productionRendererInvocation": "suppressed",
                "pdfWrite": "suppressed",
                "productionWrite": "suppressed",
            }
        )

    measure_numbers = [measure["measureNumber"] for measure in dry_run_measures]
    attack_count = sum(measure["attackCount"] for measure in dry_run_measures)

    source_sha_after = sha256(source_path)
    inspection_sha_after = sha256(INSPECTION_PATH)
    adapter_output_sha_after = sha256(ADAPTER_OUTPUT_PATH)
    adapter_report_sha_after = sha256(ADAPTER_REPORT_PATH)

    checks = {
        "humanInspectionPassed": True,
        "adapterOutputBenchmarkPassed": True,
        "measureSequenceExact": measure_numbers == EXPECTED_MEASURES,
        "measureCount11": len(dry_run_measures) == 11,
        "attackCount44": attack_count == 44,
        "invalidRowsZero": invalid_rows == 0,
        "duplicateAttackKeysZero": duplicate_attack_keys == 0,
        "allRowsSixStrings": all(
            len(row["fretsHighToLow"]) == 6
            for measure in dry_run_measures
            for row in measure["rows"]
        ),
        "productionRendererInvocationSuppressed": True,
        "pdfWriteSuppressed": True,
        "productionWriteSuppressed": True,
        "sourceEventShaUnchanged": source_sha_before == source_sha_after,
        "inspectionShaUnchanged": inspection_sha_before == inspection_sha_after,
        "adapterOutputShaUnchanged": adapter_output_sha_before == adapter_output_sha_after,
        "adapterReportShaUnchanged": adapter_report_sha_before == adapter_report_sha_after,
    }

    passed = all(checks.values())

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-production-renderer-dry-run",
        "mode": "in-memory-contract-only",
        "checks": checks,
        "measureCount": len(dry_run_measures),
        "attackCount": attack_count,
        "invalidRowCount": invalid_rows,
        "duplicateAttackKeyCount": duplicate_attack_keys,
        "measures": dry_run_measures,
        "dryRunPassed": passed,
        "readyForProductionRendererShadowInvocation": passed,
        "productionRendererCalled": False,
        "pdfCreated": False,
        "productionOutputCreated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Protected production renderer dry run complete")
    print(f"Measures staged in memory: {len(dry_run_measures)}/11")
    print(f"Adapter rows staged in memory: {attack_count}/44")
    print(f"Invalid rows: {invalid_rows}")
    print(f"Duplicate attack keys: {duplicate_attack_keys}")
    print(f"Source event SHA unchanged: {checks['sourceEventShaUnchanged']}")
    print(f"Adapter output SHA unchanged: {checks['adapterOutputShaUnchanged']}")
    print(f"Dry run passed: {passed}")
    print(f"Ready for production renderer shadow invocation: {passed}")
    print("Production renderer called: False")
    print("PDF created: False")
    print("Production output created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
