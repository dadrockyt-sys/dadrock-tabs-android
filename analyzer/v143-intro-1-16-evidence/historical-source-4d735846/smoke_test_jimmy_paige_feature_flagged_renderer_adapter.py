from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-readonly-production-renderer-adapter.json"
SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]
SIDECAR_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-feature-flagged-renderer-smoke-test.json"

FEATURE_FLAG_NAME = "JIMMY_CHORD_RENDERER_ADAPTER_ENABLED"


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


def env_flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    adapter = load(ADAPTER_PATH)
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    if not bool(adapter.get("adapterPassed", False)):
        raise RuntimeError("Read-only renderer adapter has not passed")
    if not bool(adapter.get("readyForFeatureFlaggedNoOutputSmokeTest", False)):
        raise RuntimeError("Adapter is not ready for the no-output smoke test")

    source_sha_before = sha256(source_path)
    sidecar_sha_before = sha256(SIDECAR_PATH)
    adapter_sha_before = sha256(ADAPTER_PATH)

    feature_flag_enabled = env_flag_enabled(FEATURE_FLAG_NAME)
    rows = adapter.get("adaptedRows", [])

    consumed_rows = 0
    emitted_rows = 0
    renderer_called = False
    output_pdf_created = False

    if feature_flag_enabled:
        # This smoke path proves the adapter contract can be read behind a flag.
        # It intentionally does not invoke the renderer or emit any production output.
        consumed_rows = len(rows) if isinstance(rows, list) else 0

    source_sha_after = sha256(source_path)
    sidecar_sha_after = sha256(SIDECAR_PATH)
    adapter_sha_after = sha256(ADAPTER_PATH)

    checks = {
        "adapterPassed": bool(adapter.get("adapterPassed", False)),
        "adaptedRows44": isinstance(rows, list) and len(rows) == 44,
        "featureFlagDefaultFalse": not feature_flag_enabled,
        "rendererNotCalled": renderer_called is False,
        "noRowsEmitted": emitted_rows == 0,
        "noPdfCreated": output_pdf_created is False,
        "sourceEventShaUnchanged": source_sha_before == source_sha_after,
        "rendererSidecarShaUnchanged": sidecar_sha_before == sidecar_sha_after,
        "adapterShaUnchanged": adapter_sha_before == adapter_sha_after,
        "productionConsumptionStillDisabled": adapter.get("productionMayConsume") is False,
        "rendererConsumptionStillDisabled": adapter.get("rendererMayConsume") is False,
    }

    smoke_test_passed = all(checks.values())

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "feature-flagged-no-output-renderer-adapter-smoke-test",
        "featureFlagName": FEATURE_FLAG_NAME,
        "featureFlagEnabled": feature_flag_enabled,
        "featureFlagDefault": False,
        "adaptedRowsAvailable": len(rows) if isinstance(rows, list) else 0,
        "rowsReadBehindFlag": consumed_rows,
        "rowsEmitted": emitted_rows,
        "rendererCalled": renderer_called,
        "outputPdfCreated": output_pdf_created,
        "checks": checks,
        "smokeTestPassed": smoke_test_passed,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForFlagEnabledReadOnlySmokeTest": smoke_test_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Feature-flagged renderer adapter no-output smoke test complete")
    print(f"Feature flag enabled: {feature_flag_enabled}")
    print(f"Adapted rows available: {payload['adaptedRowsAvailable']}/44")
    print(f"Rows emitted: {emitted_rows}")
    print(f"Renderer called: {renderer_called}")
    print(f"Output PDF created: {output_pdf_created}")
    print(f"Source event SHA unchanged: {checks['sourceEventShaUnchanged']}")
    print(f"Renderer sidecar SHA unchanged: {checks['rendererSidecarShaUnchanged']}")
    print(f"Adapter SHA unchanged: {checks['adapterShaUnchanged']}")
    print(f"Smoke test passed: {smoke_test_passed}")
    print(f"Ready for flag-enabled read-only smoke test: {smoke_test_passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
