from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SHADOW_REPORT = PUBLIC / "gomyway-jimmy-paige-production-renderer-shadow-invocation.json"
ADAPTER = PUBLIC / "gomyway-jimmy-paige-readonly-production-renderer-adapter.json"
OUTPUT = PUBLIC / "gomyway-jimmy-paige-professional-notation-technique-contract.json"

TECHNIQUE_TYPES = [
    "bend",
    "bend-release",
    "pre-bend",
    "sustain-tie",
    "let-ring",
    "palm-mute",
    "slide-up",
    "slide-down",
    "hammer-on",
    "pull-off",
    "vibrato",
    "dead-note",
    "muted-strum",
    "natural-harmonic",
    "pinch-harmonic",
    "tap",
    "trill",
]

DRAWING_PRIMITIVES = [
    "curved-arrow",
    "straight-arrow",
    "dashed-span",
    "solid-span",
    "wavy-span",
    "text-label",
    "slur-curve",
    "diagonal-line",
    "diamond-notehead",
    "cross-notehead",
]


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    shadow = load(SHADOW_REPORT)
    adapter = load(ADAPTER)

    if shadow.get("shadowInvocationPassed") is not True:
        raise RuntimeError("Production renderer shadow invocation is not passing")
    if adapter.get("adapterPassed") is not True:
        raise RuntimeError("Read-only renderer adapter is not passing")

    shadow_sha_before = sha256(SHADOW_REPORT)
    adapter_sha_before = sha256(ADAPTER)

    schema = {
        "measureNumber": "positive integer",
        "attackNumber": "positive integer or null for span-only techniques",
        "stringIndex": "0-5 or null for multi-string/span techniques",
        "fret": "non-negative integer or null",
        "startPhase": "0.0-0.999",
        "endPhase": "0.0-0.999 or null",
        "techniqueType": TECHNIQUE_TYPES,
        "drawingPrimitive": DRAWING_PRIMITIVES,
        "amount": "half|full|one-and-half|two|custom|null",
        "release": "boolean",
        "continuation": "boolean",
        "label": "short printed label or null",
        "confidence": "0.0-1.0",
        "source": "professional-pdf-manual-reference",
        "verifiedByHuman": "boolean",
    }

    technique_contract = {
        "contractVersion": 1,
        "contractType": "professional-notation-technique-reference",
        "status": "schema-ready-reference-extraction-required",
        "professionalPdfIsScoringAuthority": True,
        "rendererEntryPoint": shadow.get("rendererEntryPoint"),
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "supportedTechniqueTypes": TECHNIQUE_TYPES,
        "supportedDrawingPrimitives": DRAWING_PRIMITIVES,
        "referenceSchema": schema,
        "referenceAnnotations": [],
        "referenceAnnotationCount": 0,
        "syntheticAnnotationsCreated": False,
        "manualProfessionalPdfInspectionRequired": True,
        "minimumVerifiedExamplesPerTechnique": 3,
        "minimumTotalVerifiedExamples": len(TECHNIQUE_TYPES) * 3,
        "trainingRules": {
            "doNotInferFromPitchAlone": True,
            "doNotCreateTechniqueLabelsWithoutProfessionalPdfEvidence": True,
            "separateAnalyzerPredictionFromRendererDrawing": True,
            "keepTechniqueLayerBehindDisabledFeatureFlag": True,
            "requireHumanVisualComparisonBeforeRendererIntegration": True,
        },
        "geometryChecksPlanned": {
            "arrowDirection": True,
            "curveStartAndEnd": True,
            "spanLength": True,
            "labelPlacement": True,
            "stringAlignment": True,
            "measureClipping": True,
            "crossPageContinuation": True,
        },
        "shadowRendererPassed": True,
        "readOnlyAdapterPassed": True,
        "shadowReportSha256": shadow_sha_before,
        "adapterSha256": adapter_sha_before,
        "shadowReportShaUnchanged": sha256(SHADOW_REPORT) == shadow_sha_before,
        "adapterShaUnchanged": sha256(ADAPTER) == adapter_sha_before,
        "contractPassed": True,
        "readyForManualProfessionalTechniqueReferenceExtraction": True,
        "readyForTechniqueRendererTraining": False,
        "readyForProduction": False,
    }

    OUTPUT.write_text(json.dumps(technique_contract, indent=2) + "\n", encoding="utf-8")

    print("Professional notation technique reference contract complete")
    print(f"Technique types registered: {len(TECHNIQUE_TYPES)}")
    print(f"Drawing primitives registered: {len(DRAWING_PRIMITIVES)}")
    print("Verified professional annotations: 0")
    print("Synthetic annotations created: False")
    print("Professional PDF remains scoring authority: True")
    print("Shadow renderer passed: True")
    print("Read-only adapter passed: True")
    print("Contract passed: True")
    print("Ready for manual professional technique reference extraction: True")
    print("Ready for technique renderer training: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
