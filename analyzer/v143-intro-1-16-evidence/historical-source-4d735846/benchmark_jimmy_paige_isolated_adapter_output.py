from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-readonly-production-renderer-adapter.json"
SMOKE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-flag-enabled-readonly-adapter-smoke-test.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output.json"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output-report.json"


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
    adapter = load(ADAPTER_PATH)
    smoke = load(SMOKE_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(adapter.get("adapterPassed", False)):
        raise RuntimeError("Read-only renderer adapter is not passing")
    if not bool(smoke.get("smokeTestPassed", False)):
        raise RuntimeError("Flag-enabled read-only smoke test is not passing")

    source_sha_before = sha256(source_path)
    adapter_sha_before = sha256(ADAPTER_PATH)
    smoke_sha_before = sha256(SMOKE_PATH)

    rows = adapter.get("adaptedRows", [])
    if not isinstance(rows, list):
        raise RuntimeError("Adapter rows are not a list")

    isolated_rows: list[dict[str, Any]] = []
    invalid_rows = 0

    for row in rows:
        if not isinstance(row, dict):
            invalid_rows += 1
            continue

        frets = row.get("fretsHighToLow")
        valid = (
            isinstance(row.get("measureNumber"), int)
            and isinstance(row.get("attackNumber"), int)
            and isinstance(frets, list)
            and len(frets) == 6
            and bool(row.get("readOnly", False))
            and row.get("rendererConsumptionAllowed") is False
            and row.get("productionConsumptionAllowed") is False
        )
        if not valid:
            invalid_rows += 1
            continue

        isolated_rows.append(
            {
                "measureNumber": row["measureNumber"],
                "attackNumber": row["attackNumber"],
                "phase": row.get("phase"),
                "fretsHighToLow": frets,
                "resolutionMode": row.get("resolutionMode"),
                "boundaryMode": "isolated-adapter-output",
                "rendererCalled": False,
                "pdfCreated": False,
                "productionOutputCreated": False,
                "sourceMutationAllowed": False,
            }
        )

    output_payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "isolated-readonly-adapter-output",
        "mode": "isolated-json-only",
        "rows": isolated_rows,
        "rowCount": len(isolated_rows),
        "invalidRowCount": invalid_rows,
        "rendererCalled": False,
        "pdfCreated": False,
        "productionOutputCreated": False,
        "rendererChanged": False,
        "sourceEventsMutated": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    OUTPUT_PATH.write_text(json.dumps(output_payload, indent=2) + "\n", encoding="utf-8")

    source_sha_after = sha256(source_path)
    adapter_sha_after = sha256(ADAPTER_PATH)
    smoke_sha_after = sha256(SMOKE_PATH)

    checks = {
        "adapterPassed": True,
        "flagEnabledReadonlySmokePassed": True,
        "isolatedRows44": len(isolated_rows) == 44,
        "invalidRowsZero": invalid_rows == 0,
        "allRowsSixStrings": all(len(row["fretsHighToLow"]) == 6 for row in isolated_rows),
        "rendererNotCalled": True,
        "pdfNotCreated": True,
        "productionOutputNotCreated": True,
        "sourceEventShaUnchanged": source_sha_before == source_sha_after,
        "adapterShaUnchanged": adapter_sha_before == adapter_sha_after,
        "smokeShaUnchanged": smoke_sha_before == smoke_sha_after,
    }

    benchmark_passed = all(checks.values())

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "isolated-readonly-adapter-output-report",
        "checks": checks,
        "isolatedRowCount": len(isolated_rows),
        "invalidRowCount": invalid_rows,
        "benchmarkPassed": benchmark_passed,
        "readyForIsolatedAdapterPdfBenchmark": benchmark_passed,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "output": str(OUTPUT_PATH.relative_to(REPO_ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Isolated adapter output benchmark complete")
    print(f"Rows written to isolated output: {len(isolated_rows)}/44")
    print(f"Invalid rows: {invalid_rows}")
    print("Renderer called: False")
    print("Output PDF created: False")
    print("Production output created: False")
    print(f"Source event SHA unchanged: {checks['sourceEventShaUnchanged']}")
    print(f"Adapter SHA unchanged: {checks['adapterShaUnchanged']}")
    print(f"Smoke test SHA unchanged: {checks['smokeShaUnchanged']}")
    print(f"Benchmark passed: {benchmark_passed}")
    print(f"Ready for isolated adapter PDF benchmark: {benchmark_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
