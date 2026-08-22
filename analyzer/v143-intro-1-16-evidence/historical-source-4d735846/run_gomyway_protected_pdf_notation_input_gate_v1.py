from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
INPUT_AUDIT_PATH = PUBLIC_DIR / "gomyway-protected-pdf-comparison-input-audit-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-protected-pdf-notation-input-gate-v1.json"

PROFESSIONAL_PATH = PUBLIC_DIR / "gomyway-professional-reference.pdf"
PREFERRED_JIMMY_PATHS = (
    PUBLIC_DIR / "gomyway-full-song-v8-notation-proof.pdf",
    PUBLIC_DIR / "gomyway-full-song-v8-rhythm-proof.pdf",
    PUBLIC_DIR / "gomyway-full-song-v7-notation-proof-v2.pdf",
    PUBLIC_DIR / "gomyway-full-song-v7-notation-proof.pdf",
)


def main() -> None:
    if not INPUT_AUDIT_PATH.exists():
        raise FileNotFoundError(INPUT_AUDIT_PATH)

    input_audit = json.loads(INPUT_AUDIT_PATH.read_text(encoding="utf-8"))
    selected_jimmy = next((path for path in PREFERRED_JIMMY_PATHS if path.exists()), None)

    v8_notation_available = any(
        path.exists() and "v8" in path.name.lower()
        for path in PREFERRED_JIMMY_PATHS
    )
    professional_available = PROFESSIONAL_PATH.exists()
    jimmy_notation_available = selected_jimmy is not None
    measure_grid_rejected = True

    passed = bool(
        input_audit.get("passed")
        and professional_available
        and jimmy_notation_available
        and measure_grid_rejected
    )

    report = {
        "schemaVersion": 1,
        "gateType": "protected-pdf-notation-input",
        "passed": passed,
        "professionalPdf": str(PROFESSIONAL_PATH.relative_to(REPO_ROOT)) if professional_available else None,
        "jimmyNotationPdf": str(selected_jimmy.relative_to(REPO_ROOT)) if selected_jimmy else None,
        "v8NotationPdfAvailable": v8_notation_available,
        "fallbackUsesProtectedV7NotationProof": bool(selected_jimmy and "v7" in selected_jimmy.name.lower()),
        "measureGridProofRejected": measure_grid_rejected,
        "readyForVisualNotationComparison": passed,
        "interpretation": (
            "The measure-grid proof is not a valid musical-notation comparison target. This gate "
            "selects a full-song notation proof only. If no V8 notation PDF exists yet, the protected "
            "V7 notation proof may be used solely as a renderer/layout baseline, not as proof that the "
            "newly reviewed V8 rhythm content matches the professional PDF."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Protected PDF notation-input gate V1 complete")
    print("Passed:", passed)
    print("Professional PDF:", report["professionalPdf"])
    print("Jimmy notation PDF:", report["jimmyNotationPdf"])
    print("V8 notation PDF available:", report["v8NotationPdfAvailable"])
    print("Fallback uses protected V7 notation proof:", report["fallbackUsesProtectedV7NotationProof"])
    print("Measure-grid proof rejected:", report["measureGridProofRejected"])
    print("Ready for visual notation comparison:", report["readyForVisualNotationComparison"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
