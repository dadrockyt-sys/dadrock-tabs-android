#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "lib" / "jimmyPaigeProfessionalPdfContract.js"
BRIDGE = ROOT / "lib" / "createJimmyPaigeProfessionalPdf.js"
STRUCTURED_RENDERER = ROOT / "lib" / "createTabPdfPolishedV7.js"
OVERLAY = ROOT / "lib" / "v7MeasureGridOverlay.js"
PREVIEW_ROUTE = ROOT / "app" / "api" / "generate-tab-preview" / "route.js"
FINAL_ROUTE = ROOT / "app" / "api" / "generate-tab-pdf" / "route.js"
ANALYZE_ROUTE = ROOT / "app" / "api" / "analyze-audio-tab" / "route.js"
PAGE = ROOT / "app" / "ai-tab" / "page.js"


def read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    contract = read(CONTRACT)
    bridge = read(BRIDGE)
    structured_renderer = read(STRUCTURED_RENDERER)
    overlay = read(OVERLAY)
    preview_route = read(PREVIEW_ROUTE)
    final_route = read(FINAL_ROUTE)
    analyze_route = read(ANALYZE_ROUTE)
    page = read(PAGE)

    marker_types = {
        "bend-release": "type === 'bend-release'" in overlay,
        "chord-label": "type === 'chord-label'" in overlay,
        "palm-mute-span": "type === 'palm-mute-span'" in overlay,
        "slide": "type === 'slide'" in overlay,
        "muted-attack": "type === 'muted-attack'" in overlay,
        "rest": "type === 'rest'" in overlay,
    }

    checks = {
        "contractExists": "buildJimmyPaigeProfessionalPdfOptions" in contract,
        "contractSupportsLeadRhythmBass": all(
            f"'{value}'" in contract for value in ("lead", "rhythm", "bass")
        ),
        "contractPreservesTuning": "tuning:" in contract,
        "contractPreservesTempo": "tempo:" in contract,
        "contractPreservesTimeSignature": "timeSignature:" in contract,
        "contractPreservesKeySignature": "keySignature:" in contract,
        "contractValidatesMeasureGridVersion": "MEASURE_GRID_VERSION = 7" in contract,
        "contractValidatesSixMeasureLayout": "MEASURES_PER_SYSTEM = 6" in contract,
        "contractRequiresReadOnlyNotes": "note.measureGridReadOnly !== true" in contract,
        "contractRequiresMusicallyFilteredNotes": "note.musicallyFiltered !== true" in contract,
        "contractRequiresReadOnlyFragments": "fragment.readOnly !== true" in contract,
        "contractFailsSafeToPolishedRenderer": "polished-safe-fallback" in contract,
        "contractDoesNotAuthorizeProduction": "productionPromotionAuthorized: false" in contract,
        "bridgeCallsStructuredPolishedRenderer": "createStructuredPolishedTabPdf" in bridge,
        "bridgeUsesContract": "buildJimmyPaigeProfessionalPdfOptions" in bridge,
        "structuredRendererStillOptIn": "enableV7MeasureGrid === true" in structured_renderer,
        "structuredRendererFallsBackToPolishedBytes": structured_renderer.count("return polishedBytes;") >= 3,
        "allProfessionalMarkerTypesSupported": all(marker_types.values()),
        "previewRouteStillProtectedCurrentRenderer": "from '@/lib/createTabPdfPolished';" in preview_route,
        "finalRouteStillProtectedCurrentRenderer": "from '@/lib/createTabPdfPolished';" in final_route,
        "liveRoutesNotPromotedToJimmyBridge": (
            "createJimmyPaigeProfessionalPdf" not in preview_route
            and "createJimmyPaigeProfessionalPdf" not in final_route
        ),
        "analyzerRouteStillExplicitCanary": "usingV143RhythmAnalyzer" in analyze_route,
        "uploadUiStillUsesPrivateBlob": "access: 'private'" in page,
        "uploadUiStillCallsAnalyzerRoute": "'/api/analyze-audio-tab'" in page,
    }

    known_gaps = {
        "analysisApiPassesStructuredMeasureGrid": (
            "measureGrid:" in analyze_route or "measureGrid," in analyze_route
        ),
        "analysisApiPassesRawEvents": (
            "events:" in analyze_route or "events," in analyze_route
        ),
        "finalDownloadPreservesAnalyzerMetadata": (
            "analysisMetadata" in page[page.find("const handleDownloadPdf"):]
            if "const handleDownloadPdf" in page
            else False
        ),
        "previewRouteUsesJimmyBridge": "createJimmyPaigeProfessionalPdf" in preview_route,
        "finalRouteUsesJimmyBridge": "createJimmyPaigeProfessionalPdf" in final_route,
    }

    passed = all(checks.values())
    payload = {
        "artifact": "jimmy-paige-professional-pdf-bridge-guard",
        "schemaVersion": 1,
        "passed": passed,
        "checks": checks,
        "markerTypes": marker_types,
        "knownIntegrationGaps": known_gaps,
        "nextRequiredStage": (
            "structured-analyzer-payload-and-metadata-preservation"
            if passed
            else "repair-bridge-contract"
        ),
        "productionModified": False,
        "liveRoutePromotionPerformed": False,
    }

    print(json.dumps(payload, indent=2))

    if not passed:
        raise SystemExit("Jimmy PAIge professional PDF bridge guard failed")


if __name__ == "__main__":
    main()
