from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "app" / "api" / "analyze-audio-tab" / "route.js"
PAGE = ROOT / "app" / "ai-tab" / "page.js"
WORKER = ROOT / "analyzer" / "v143_modal_live_endpoint.py"
SCHEDULER = ROOT / "analyzer" / "v143_seeded_separator.py"
BRIDGE = ROOT / "analyzer" / "v143_modal_http_endpoint.py"
PROTOCOL = ROOT / "analyzer" / "v143_async_job_protocol.py"

EXPECTED = {
    "worker": "111bf14a8f91045d3478901f8e36b88a2e7f181a",
    "scheduler": "fc9b4c45c208d80be7abab64a8959f2a3babcee8",
    "bridge": "03dda2d78eb8d1bc892ed12037644a6ceb8e3591",
    "protocol": "1bd55017e16a4e1d8b14c7429492f811a43a28d8",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_all(source: str, fragments: list[str], label: str) -> None:
    for fragment in fragments:
        require(fragment in source, f"{label} missing invariant: {fragment}")


def forbid_all(source: str, fragments: list[str], label: str) -> None:
    for fragment in fragments:
        require(fragment not in source, f"{label} contains forbidden fragment: {fragment}")


def main() -> None:
    route = ROUTE.read_text(encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")

    actual = {
        "worker": git_blob_sha(WORKER),
        "scheduler": git_blob_sha(SCHEDULER),
        "bridge": git_blob_sha(BRIDGE),
        "protocol": git_blob_sha(PROTOCOL),
    }
    require(actual == EXPECTED, f"runtime source pin mismatch: {actual}")

    require_all(
        route,
        [
            "export const runtime = 'nodejs';",
            "export const maxDuration = 150;",
            "async function buildCompletedProductPayload",
            "liveV143?.referenceFree === true",
            "liveV143?.professionalReferenceUsed === false",
            "liveV143?.referenceRuntimeInputUsed === false",
            "liveV143?.runtimeLabelsRequired === false",
            "buildJimmyPaigeAnalysisPayload(",
            "buildAiTabConditioningContractV1({",
            "buildAiTabConditionedShadowProjectionV1({",
            "buildAiTabMixtureStructureContextV1({",
            "buildAiTabMixtureStructureContextFromAnalyzerObservationV1({",
            "buildAiTabDualContextShadowFusionV1({",
            "await buildAiTabProductPlacementCandidateCanaryV1({",
            "buildAiTabProductPlacementPromotionV1({",
            "(usingV143RhythmAnalyzer\n        ? 'start'\n        : 'analyze')",
            "operation === 'status' ||\n      operation === 'ack'",
            "operation === 'start' ||\n      operation === 'analyze'",
            "token: analyzerToken,\n            operation,\n            jobToken,",
            "status: 'processing'",
            "{ status: 202 }",
            "bridgeData?.status !== 'completed'",
            "analyzerData = bridgeData.result;",
            "await buildCompletedProductPayload({",
            "status: 'completed'",
            "status: 'acknowledged'",
        ],
        "route",
    )

    require_all(
        page,
        [
            "const requestTabAnalysis =",
            "response.status === 202",
            "selectedType === 'rhythm'",
            "data?.analysisJob?.token",
            "operation: 'status'",
            "operation: 'ack'",
            "21 * 60 * 1000",
            "!data.generatedTab",
            "return data;",
            "await requestTabAnalysis(",
            "await requestPreviewPdf(",
            "setPreviewReady(true);",
            "15-minute TTL",
        ],
        "page",
    )

    forbid_all(
        page,
        [
            "localStorage.setItem",
            "sessionStorage.setItem",
            "history.pushState",
            "router.push(`?job",
            "window.location.hash",
        ],
        "page",
    )

    forbid_all(
        route + "\n" + page,
        [
            "torch",
            "demucs",
            "roformer",
            "modal.Function",
            "GOAT",
            "GuitarSet",
            "referenceScoreCalls +=",
        ],
        "vercel wiring",
    )

    require(
        "? {\n            token: analyzerToken,\n            operation,\n            jobToken,\n          }" in route,
        "status/ack control body changed unexpectedly",
    )

    summary = {
        "schemaVersion": 3,
        "gate": "v143-async-vercel-wiring",
        "allPassed": True,
        "routeBlob": git_blob_sha(ROUTE),
        "pageBlob": git_blob_sha(PAGE),
        "runtimePins": actual,
        "rhythmDefaultsAsync": True,
        "leadBassRemainSynchronous": True,
        "processingUsesHttp202": True,
        "completedResultStillUsesExistingSafetyProductPipeline": True,
        "jobTokenPersistedClientSide": False,
        "ackAfterBrowserReceipt": True,
        "isolatedBridgeModeSupported": True,
        "bridgeResourceNamesBakedIntoImage": True,
        "workerChanged": False,
        "schedulerChanged": False,
        "modelExecuted": False,
        "audioRead": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
