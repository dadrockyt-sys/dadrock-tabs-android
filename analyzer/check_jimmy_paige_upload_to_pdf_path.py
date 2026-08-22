#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/ai-tab/page.js"
ANALYZE = ROOT / "app/api/analyze-audio-tab/route.js"
PREVIEW = ROOT / "app/api/generate-tab-preview/route.js"
FINAL = ROOT / "app/api/generate-tab-pdf/route.js"
PAYLOAD = ROOT / "lib/jimmyPaigeAnalysisPayload.js"
CONTRACT = ROOT / "lib/jimmyPaigeProfessionalPdfContract.js"
BRIDGE = ROOT / "lib/createJimmyPaigeProfessionalPdf.js"
RENDER_CONTRACT = ROOT / "lib/v143RenderContract.js"
AI_PDF = ROOT / "lib/createAiTabPdf.js"
V143_PDF = ROOT / "lib/createV143RhythmPdf.js"


def read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> None:
    page = read(PAGE)
    analyze = read(ANALYZE)
    preview = read(PREVIEW)
    final = read(FINAL)
    payload = read(PAYLOAD)
    contract = read(CONTRACT)
    bridge = read(BRIDGE)
    render_contract = read(RENDER_CONTRACT)
    ai_pdf = read(AI_PDF)
    v143_pdf = read(V143_PDF)

    checks = {
        "privateAudioUploadPreserved": "access: 'private'" in page,
        "analyzerRequestPreserved": "'/api/analyze-audio-tab'" in page,
        "structuredPayloadBuilderExists": "buildJimmyPaigeAnalysisPayload" in payload,
        "analysisRouteUsesStructuredPayloadBuilder": "buildJimmyPaigeAnalysisPayload" in analyze,
        "analysisRouteStillFailsClosedForV143Identity": (
            "analyzerData?.liveV143?.referenceFree !== true" in analyze
        ),
        "analysisPayloadCarriesBoundedEvents": (
            "events," in payload and "MAX_EVENTS = 20000" in payload
        ),
        "analysisPayloadUsesEstablishedV143RenderContract": (
            "projectV143RenderEvents" in payload
            and "renderEvents," in payload
            and "renderContractVersion" in payload
        ),
        "analysisPayloadDoesNotInferMusicalPlacement": (
            "measure +" in payload
            and "We never infer those fields" in payload
        ),
        "analysisPayloadDoesNotAuthorizeProduction": (
            "productionPromotionAuthorized: false" in payload
        ),
        "v143RenderContractRequiresMeasureStepAndPlayablePosition": all(
            token in render_contract
            for token in (
                "measure === null || measure < 1",
                "step === null || step < 0 || step > 15",
                "stringIndex === null || stringIndex < 0 || stringIndex > 5",
                "fret === null || fret < 0 || fret > 36",
            )
        ),
        "pageStoresAnalysisMetadata": "setAnalysisMetadata" in page,
        "pageClearsAnalysisMetadataOnReset": "setAnalysisMetadata(null)" in page,
        "pagePreservesAnalyzerResultAfterGeneration": (
            "setAnalysisMetadata(\n          analyzerData\n        )" in page
            or "setAnalysisMetadata(analyzerData)" in page
        ),
        "previewRequestCarriesAnalysisEngine": (
            "analysisEngine:\n    analysisMetadata.analysisEngine || ''" in page
        ),
        "previewRequestCarriesRenderEvents": (
            "renderEvents:\n    Array.isArray(analysisMetadata.renderEvents)" in page
        ),
        "finalRequestCarriesTuning": "analysisMetadata?.tuning" in page,
        "finalRequestCarriesTempo": "analysisMetadata?.tempo" in page,
        "finalRequestCarriesTimeSignature": "analysisMetadata?.timeSignature" in page,
        "finalRequestCarriesKeySignature": "analysisMetadata?.keySignature" in page,
        "finalRequestCarriesAnalysisEngine": "analysisMetadata?.analysisEngine" in page,
        "finalRequestCarriesRenderEvents": (
            "Array.isArray(analysisMetadata?.renderEvents)" in page
        ),
        "previewProfessionalPathIsFeatureGated": (
            "JIMMY_PAIGE_PROFESSIONAL_PDF_V1" in preview
            and "createJimmyPaigeProfessionalPdf" in preview
            and "createTabPdf" in preview
            and "body?.renderEvents" in preview
        ),
        "finalProfessionalPathIsFeatureGated": (
            "JIMMY_PAIGE_PROFESSIONAL_PDF_V1" in final
            and "createJimmyPaigeProfessionalPdf" in final
            and "createTabPdf" in final
            and "body?.renderEvents" in final
        ),
        "professionalContractFailsSafe": "polished-safe-fallback" in contract,
        "professionalBridgePrefersEstablishedV143Renderer": (
            "createAiTabPdf" in bridge
            and "projectV143RenderEvents" in bridge
            and "v143-structured-rhythm" in bridge
        ),
        "aiPdfSelectsV143OnlyForReferenceFreeRhythm": all(
            token in ai_pdf
            for token in (
                "transcriptionType || '').toLowerCase() === 'rhythm'",
                "analysisEngine || '') === 'v143-reference-free-rhythm'",
                "renderEvents.length > 0",
            )
        ),
        "v143PdfUsesStructuredMeasureStepPlacement": (
            "Number(event.measure)" in v143_pdf
            and "Number(event.step)" in v143_pdf
            and "STEPS_PER_MEASURE = 16" in v143_pdf
        ),
    }

    failed = [name for name, passed in checks.items() if not passed]
    payload_out = {
        "artifact": "jimmy-paige-upload-to-professional-pdf-path",
        "schemaVersion": 2,
        "passed": not failed,
        "checks": checks,
        "failedChecks": failed,
        "featureGate": "JIMMY_PAIGE_PROFESSIONAL_PDF_V1",
        "featureGateDefault": "off",
        "structuredRhythmContract": "v143-render-contract-v1",
        "mainModified": False,
        "productionPromotionPerformed": False,
        "nextRequiredStage": (
            "render-contract-fixture-and-pdf-quality-validation"
            if not failed
            else "repair-upload-to-pdf-transport"
        ),
    }
    print(json.dumps(payload_out, indent=2))
    if failed:
        raise SystemExit("Jimmy PAIge upload-to-PDF integration guard failed")


if __name__ == "__main__":
    main()
