from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-renderer-integration-benchmark.json"
SIDECAR_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-readonly-production-renderer-adapter.json"


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


def first_bool(payload: Any, keys: list[str]) -> bool:
    if isinstance(payload, dict):
        for key in keys:
            if isinstance(payload.get(key), bool):
                return bool(payload[key])
        for value in payload.values():
            if first_bool(value, keys):
                return True
    elif isinstance(payload, list):
        for value in payload:
            if first_bool(value, keys):
                return True
    return False


def main() -> None:
    integration = load(INTEGRATION_PATH)
    sidecar = load(SIDECAR_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    integration_passed = first_bool(
        integration,
        [
            "protectedRendererIntegrationBenchmarkPassed",
            "benchmarkPassed",
            "passed",
        ],
    )
    ready = first_bool(
        integration,
        [
            "readyForReadOnlyProductionRendererAdapter",
            "readyForReadonlyProductionRendererAdapter",
        ],
    )

    if not integration_passed or not ready:
        raise RuntimeError("Protected renderer integration benchmark is not ready")

    source_sha_before = sha256(source_path)
    sidecar_sha_before = sha256(SIDECAR_PATH)

    rows = sidecar.get("renderRows") or sidecar.get("rows") or sidecar.get("attackRows") or []
    if not isinstance(rows, list):
        raise RuntimeError("Renderer sidecar rows are not a list")

    adapted_rows: list[dict[str, Any]] = []
    invalid_rows = 0

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            invalid_rows += 1
            continue

        measure_number = row.get("measureNumber")
        attack_number = row.get("attackNumber")
        frets = row.get("fretsHighToLow") or row.get("resolvedFretsHighToLow")

        valid = (
            isinstance(measure_number, int)
            and isinstance(attack_number, int)
            and isinstance(frets, list)
            and len(frets) == 6
        )
        if not valid:
            invalid_rows += 1
            continue

        adapted_rows.append(
            {
                "adapterRow": index,
                "measureNumber": measure_number,
                "attackNumber": attack_number,
                "phase": row.get("phase") or row.get("targetPhase"),
                "fretsHighToLow": frets,
                "resolutionMode": row.get("resolutionMode"),
                "readOnly": True,
                "rendererConsumptionAllowed": False,
                "productionConsumptionAllowed": False,
                "sourceMutationAllowed": False,
                "timingMutationAllowed": False,
                "pitchEvidenceMutationAllowed": False,
            }
        )

    source_sha_after = sha256(source_path)
    sidecar_sha_after = sha256(SIDECAR_PATH)

    source_unchanged = source_sha_before == source_sha_after
    sidecar_unchanged = sidecar_sha_before == sidecar_sha_after
    row_count = len(adapted_rows)

    checks = {
        "protectedRendererIntegrationPassed": integration_passed,
        "adapterReadOnly": True,
        "sourceEventsUnchanged": source_unchanged,
        "rendererSidecarUnchanged": sidecar_unchanged,
        "invalidRowsZero": invalid_rows == 0,
        "adaptedRows44": row_count == 44,
        "allRowsSixStrings": all(len(row["fretsHighToLow"]) == 6 for row in adapted_rows),
        "rendererConsumptionDisabled": True,
        "productionConsumptionDisabled": True,
    }

    adapter_passed = all(checks.values())

    payload = {
        "adapterVersion": 1,
        "adapterType": "read-only-production-renderer-contract",
        "status": "disabled-shadow-adapter",
        "sourceEventCache": str(source_path.relative_to(REPO_ROOT)),
        "rendererSidecar": str(SIDECAR_PATH.relative_to(REPO_ROOT)),
        "sourceEventSha256": source_sha_before,
        "rendererSidecarSha256": sidecar_sha_before,
        "adaptedRows": adapted_rows,
        "adaptedRowCount": row_count,
        "invalidRowCount": invalid_rows,
        "checks": checks,
        "adapterPassed": adapter_passed,
        "rendererMayConsume": False,
        "productionMayConsume": False,
        "featureFlagRequired": True,
        "featureFlagDefault": False,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "readyForFeatureFlaggedNoOutputSmokeTest": adapter_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Read-only production renderer adapter contract complete")
    print(f"Adapted rows: {row_count}/44")
    print(f"Invalid rows: {invalid_rows}")
    print(f"Source event SHA unchanged: {source_unchanged}")
    print(f"Renderer sidecar SHA unchanged: {sidecar_unchanged}")
    print(f"Adapter passed: {adapter_passed}")
    print(f"Ready for feature-flagged no-output smoke test: {adapter_passed}")
    print("Renderer consumption allowed: False")
    print("Production consumption allowed: False")
    print("Renderer changed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
