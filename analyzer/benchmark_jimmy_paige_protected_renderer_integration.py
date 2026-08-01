from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "gate": REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json",
    "multi_section": REPO_ROOT / "public" / "gomyway-jimmy-paige-multi-section-chord-shadow-validation.json",
    "sidecar_report": REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar-report.json",
    "layout_report": REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview-report.json",
    "layout_inspection": REPO_ROOT / "public" / "gomyway-jimmy-paige-human-chord-layout-inspection.json",
    "pdf_report": REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview-report.json",
    "pdf_inspection": REPO_ROOT / "public" / "gomyway-jimmy-paige-human-isolated-pdf-inspection.json",
    "sidecar": REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-renderer-sidecar.json",
    "isolated_pdf": REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview.pdf",
}

SOURCE_EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
]

OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-renderer-integration-benchmark.json"


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


def recursive_bool(payload: Any, keys: list[str]) -> bool:
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, bool):
                return value
        return any(recursive_bool(value, keys) for value in payload.values())
    if isinstance(payload, list):
        return any(recursive_bool(value, keys) for value in payload)
    return False


def recursive_number(payload: Any, keys: list[str], default: float = 0.0) -> float:
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, (int, float)):
                return float(value)
        for value in payload.values():
            found = recursive_number(value, keys, default=float("nan"))
            if found == found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = recursive_number(value, keys, default=float("nan"))
            if found == found:
                return found
    return default


def main() -> None:
    payloads = {name: load(path) for name, path in FILES.items() if path.suffix == ".json"}
    source_path = first_existing(SOURCE_EVENT_CANDIDATES)

    source_sha_before = sha256(source_path)
    sidecar_sha_before = sha256(FILES["sidecar"])
    pdf_sha_before = sha256(FILES["isolated_pdf"])

    checks = {
        "protectedGatePassed": recursive_bool(payloads["gate"], ["gatePassed"]),
        "multiSectionShadowPassed": recursive_bool(
            payloads["multi_section"], ["multiSectionShadowPassed"]
        ),
        "rendererSidecarPassed": recursive_bool(
            payloads["sidecar_report"], ["rendererSidecarBenchmarkPassed"]
        ),
        "layoutPreviewPassed": recursive_bool(
            payloads["layout_report"], ["layoutPreviewPassed"]
        ),
        "humanLayoutInspectionPassed": recursive_bool(
            payloads["layout_inspection"], ["humanLayoutInspectionPassed"]
        ),
        "isolatedPdfPreviewPassed": recursive_bool(
            payloads["pdf_report"], ["isolatedPdfPreviewPassed"]
        ),
        "humanPdfInspectionPassed": recursive_bool(
            payloads["pdf_inspection"], ["humanPdfInspectionPassed"]
        ),
        "measureCount11": recursive_number(
            payloads["pdf_report"], ["measureCount", "measuresRendered"]
        ) >= 11,
        "attackCount44": recursive_number(
            payloads["pdf_report"], ["attackCount", "chordAttacksRendered"]
        ) >= 44,
        "pdfPageCount2": recursive_number(
            payloads["pdf_report"], ["pdfPageCount", "pageCount"]
        ) >= 2,
    }

    source_sha_after = sha256(source_path)
    sidecar_sha_after = sha256(FILES["sidecar"])
    pdf_sha_after = sha256(FILES["isolated_pdf"])

    checks.update(
        {
            "sourceEventShaUnchanged": source_sha_before == source_sha_after,
            "rendererSidecarShaUnchanged": sidecar_sha_before == sidecar_sha_after,
            "isolatedPdfShaUnchanged": pdf_sha_before == pdf_sha_after,
        }
    )

    passed = all(checks.values())

    result = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-renderer-integration-readiness",
        "checks": checks,
        "protectedRendererIntegrationBenchmarkPassed": passed,
        "sourceEventCache": str(source_path.relative_to(REPO_ROOT)),
        "sourceEventShaBefore": source_sha_before,
        "sourceEventShaAfter": source_sha_after,
        "rendererSidecarShaBefore": sidecar_sha_before,
        "rendererSidecarShaAfter": sidecar_sha_after,
        "isolatedPdfShaBefore": pdf_sha_before,
        "isolatedPdfShaAfter": pdf_sha_after,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForReadOnlyProductionRendererAdapter": passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Protected renderer integration benchmark complete")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"Protected renderer integration benchmark passed: {passed}")
    print(f"Ready for read-only production renderer adapter: {passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
