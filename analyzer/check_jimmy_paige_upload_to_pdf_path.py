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

    checks = {
        "privateAudioUploadPreserved": "access: 'private'" in page,
        "analyzerRequestPreserved": "'/api/analyze-audio-tab'" in page,
        "structuredPayloadBuilderExists": "buildJimmyPaigeAnalysisPayload" in payload,
        "analysisRouteUsesStructuredPayloadBuilder": "buildJimmyPaigeAnalysisPayload" in analyze,
        "analysisRouteStillFailsClosedForV143Identity": (
            "analyzerData?.liveV143?.referenceFree !== true" in analyze
        ),
        "analysisPayloadCarriesEvents": "events," in payload,
        "analysisPayloadCarriesMeasureGrid": "measureGrid," in payload,
        "analysisPayloadBoundsEvents": "MAX_EVENTS = 20000" in payload,
        "analysisPayloadDoesNotAuthorizeProduction": (
            "productionPromotionAuthorized: false" in payload
        ),
        "pageStoresAnalysisMetadata": "setAnalysisMetadata" in page,
        "pageClearsAnalysisMetadataOnReset": "setAnalysisMetadata(null)" in page,
        "pagePreservesAnalyzerResultAfterGeneration": "setAnalysisMetadata(analyzerData)" in page,
        "previewRequestCarriesMeasureGrid": "measureGrid:\n    analysisMetadata.measureGrid || null" in page,
        "previewRequestCarriesAnalysisEngine": "analysisEngine:\n    analysisMetadata.analysisEngine || ''" in page,
        "finalRequestCarriesTuning": "analysisMetadata?.tuning" in page,
        "finalRequestCarriesTempo": "analysisMetadata?.tempo" in page,
        "finalRequestCarriesTimeSignature": "analysisMetadata?.timeSignature" in page,
        "finalRequestCarriesKeySignature": "analysisMetadata?.keySignature" in page,
        "finalRequestCarriesMeasureGrid": "analysisMetadata?.measureGrid" in page,
        "previewProfessionalPathIsFeatureGated": (
            "JIMMY_PAIGE_PROFESSIONAL_PDF_V1" in preview
            and "createJimmyPaigeProfessionalPdf" in preview
            and "createTabPdf" in preview
        ),
        "finalProfessionalPathIsFeatureGated": (
            "JIMMY_PAIGE_PROFESSIONAL_PDF_V1" in final
            and "createJimmyPaigeProfessionalPdf" in final
            and "createTabPdf" in final
        ),
        "professionalContractFailsSafe": "polished-safe-fallback" in contract,
        "professionalBridgeUsesV7Renderer": "createStructuredPolishedTabPdf" in bridge,
    }

    failed = [name for name, passed in checks.items() if not passed]
    payload_out = {
        "artifact": "jimmy-paige-upload-to-professional-pdf-path",
        "schemaVersion": 1,
        "passed": not failed,
        "checks": checks,
        "failedChecks": failed,
        "featureGate": "JIMMY_PAIGE_PROFESSIONAL_PDF_V1",
        "featureGateDefault": "off",
        "mainModified": False,
        "productionPromotionPerformed": False,
        "nextRequiredStage": (
            "measure-grid-production-from-reference-free-timing"
            if not failed
            else "repair-upload-to-pdf-transport"
        ),
    }
    print(json.dumps(payload_out, indent=2))
    if failed:
        raise SystemExit("Jimmy PAIge upload-to-PDF integration guard failed")


if __name__ == "__main__":
    main()
