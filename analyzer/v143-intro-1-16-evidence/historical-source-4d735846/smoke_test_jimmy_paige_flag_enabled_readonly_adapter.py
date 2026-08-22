from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-readonly-production-renderer-adapter.json"
DISABLED_SMOKE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-feature-flagged-renderer-smoke-test.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-flag-enabled-readonly-adapter-smoke-test.json"


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
    disabled_smoke = load(DISABLED_SMOKE_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(adapter.get("adapterPassed", False)):
        raise RuntimeError("Read-only renderer adapter has not passed")
    if not bool(disabled_smoke.get("smokeTestPassed", False)):
        raise RuntimeError("Disabled feature-flag smoke test has not passed")

    source_sha_before = sha256(source_path)
    adapter_sha_before = sha256(ADAPTER_PATH)
    disabled_smoke_sha_before = sha256(DISABLED_SMOKE_PATH)

    feature_flag_enabled = True
    adapter_rows = adapter.get("adaptedRows", [])
    if not isinstance(adapter_rows, list):
        raise RuntimeError("Adapter rows are not a list")

    emitted_rows: list[dict[str, Any]] = []
    invalid_rows = 0

    for row in adapter_rows:
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
            and row.get("sourceMutationAllowed") is False
        )
        if not valid:
            invalid_rows += 1
            continue

        emitted_rows.append(
            {
                "measureNumber": row["measureNumber"],
                "attackNumber": row["attackNumber"],
                "phase": row.get("phase"),
                "fretsHighToLow": frets,
                "resolutionMode": row.get("resolutionMode"),
                "adapterReadOnly": True,
                "rendererCalled": False,
                "pdfOutputAllowed": False,
                "productionOutputAllowed": False,
            }
        )

    renderer_called = False
    pdf_created = False
    production_output_created = False

    source_sha_after = sha256(source_path)
    adapter_sha_after = sha256(ADAPTER_PATH)
    disabled_smoke_sha_after = sha256(DISABLED_SMOKE_PATH)

    checks = {
        "featureFlagEnabled": feature_flag_enabled,
        "adapterPassed": bool(adapter.get("adapterPassed", False)),
        "disabledFlagSmokePassed": bool(disabled_smoke.get("smokeTestPassed", False)),
        "adapterRows44": len(adapter_rows) == 44,
        "emittedRows44": len(emitted_rows) == 44,
        "invalidRowsZero": invalid_rows == 0,
        "rendererNotCalled": not renderer_called,
        "pdfNotCreated": not pdf_created,
        "productionOutputNotCreated": not production_output_created,
        "sourceEventShaUnchanged": source_sha_before == source_sha_after,
        "adapterShaUnchanged": adapter_sha_before == adapter_sha_after,
        "disabledSmokeShaUnchanged": disabled_smoke_sha_before == disabled_smoke_sha_after,
    }

    smoke_test_passed = all(checks.values())

    payload = {
        "smokeTestVersion": 1,
        "smokeTestType": "feature-flag-enabled-read-only-adapter",
        "featureFlagEnabled": feature_flag_enabled,
        "adapterRowsAvailable": len(adapter_rows),
        "rowsEmittedToReadOnlyBoundary": len(emitted_rows),
        "invalidRows": invalid_rows,
        "rendererCalled": renderer_called,
        "outputPdfCreated": pdf_created,
        "productionOutputCreated": production_output_created,
        "rows": emitted_rows,
        "checks": checks,
        "smokeTestPassed": smoke_test_passed,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "readyForIsolatedAdapterOutputBenchmark": smoke_test_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Flag-enabled read-only renderer adapter smoke test complete")
    print(f"Feature flag enabled: {feature_flag_enabled}")
    print(f"Adapter rows available: {len(adapter_rows)}/44")
    print(f"Rows emitted to read-only boundary: {len(emitted_rows)}/44")
    print(f"Invalid rows: {invalid_rows}")
    print(f"Renderer called: {renderer_called}")
    print(f"Output PDF created: {pdf_created}")
    print(f"Production output created: {production_output_created}")
    print(f"Source event SHA unchanged: {source_sha_before == source_sha_after}")
    print(f"Adapter SHA unchanged: {adapter_sha_before == adapter_sha_after}")
    print(f"Smoke test passed: {smoke_test_passed}")
    print(f"Ready for isolated adapter output benchmark: {smoke_test_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
