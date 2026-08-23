#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="${1:-/tmp/rhythm-preholdout-static}"
SOURCE_COMMIT="${GITHUB_SHA:-unknown}"

cd "$ROOT"
rm -rf "$WORK"
mkdir -p "$WORK/esm" "$WORK/logs"

python validation/rhythm_holdout/verify_runtime_isolation.py \
  > "$WORK/logs/runtime-isolation.json"

cp lib/v143RenderContract.js "$WORK/esm/v143RenderContract.mjs"

sed \
  "s#'./v143RenderContract.js'#'./v143RenderContract.mjs'#" \
  lib/v143AnalyzerQuality.js \
  > "$WORK/esm/v143AnalyzerQuality.mjs"

sed \
  -e "s#'./v143AnalyzerQuality.js'#'./v143AnalyzerQuality.mjs'#" \
  -e "s#'./v143RenderContract.js'#'./v143RenderContract.mjs'#" \
  lib/jimmyPaigeAnalysisPayload.js \
  > "$WORK/esm/jimmyPaigeAnalysisPayload.mjs"

sed \
  "s#../../lib/jimmyPaigeAnalysisPayload.js#./jimmyPaigeAnalysisPayload.mjs#" \
  validation/rhythm_holdout/prepare_rhythm_freeze_payload.mjs \
  > "$WORK/esm/prepare-freeze.mjs"

sed \
  "s#@/lib/v143RenderContract#./v143RenderContract.mjs#" \
  lib/createV143RhythmPdf.js \
  > "$WORK/esm/createV143RhythmPdf.mjs"

sed \
  "s#../../lib/v143RenderContract.js#./v143RenderContract.mjs#" \
  validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs \
  > "$WORK/esm/render-frozen.mjs"

node --check "$WORK/esm/v143RenderContract.mjs"
node --check "$WORK/esm/v143AnalyzerQuality.mjs"
node --check "$WORK/esm/jimmyPaigeAnalysisPayload.mjs"
node --check "$WORK/esm/prepare-freeze.mjs"
node --check "$WORK/esm/createV143RhythmPdf.mjs"
node --check "$WORK/esm/render-frozen.mjs"

python -m py_compile \
  validation/rhythm_holdout/canonical.py \
  validation/rhythm_holdout/freeze_rhythm_analysis.py \
  validation/rhythm_holdout/verify_pdf_event_fidelity.py

python - "$WORK/raw-product-output.json" <<'PY'
import json
import sys
from pathlib import Path

output = Path(sys.argv[1])
positions = [
    (5, 0, 40),
    (4, 2, 47),
    (3, 2, 52),
    (2, 0, 55),
]
events = []
index = 0
for measure in range(1, 101):
    for step_index, step in enumerate((0, 4, 8, 12)):
        string_index, fret, midi = positions[step_index]
        start = index * 0.115
        events.append(
            {
                "start": start,
                "end": start + 0.10,
                "duration": 0.10,
                "measure": measure,
                "step": step,
                "stringIndex": string_index,
                "fret": fret,
                "midi": midi,
                "durationSteps": 2,
                "techniques": [],
            }
        )
        index += 1

payload = {
    "generatedTab": "Synthetic reference-free Rhythm preflight tablature",
    "tuning": "E Standard",
    "tempo": 129.19921875,
    "timeSignature": "4/4",
    "noteCount": len(events),
    "events": events,
    "liveV143": {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
    },
    "canary": {
        "sameProductRhythmPipeline": True,
        "sameProductRhythmImage": True,
        "productionModified": False,
        "liveEndpointDeployedOrModified": False,
        "productionPromotionAuthorized": False,
        "sourceSha256": "3333333333333333333333333333333333333333333333333333333333333333",
        "sourceBytes": 123456,
    },
}
output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

node "$WORK/esm/prepare-freeze.mjs" \
  "$WORK/raw-product-output.json" \
  "$WORK/rhythm-freeze-input.json" \
  > "$WORK/logs/prepare-freeze.log" 2>&1

python validation/rhythm_holdout/freeze_rhythm_analysis.py \
  "$WORK/rhythm-freeze-input.json" \
  "$WORK/freeze" \
  --source-commit "$SOURCE_COMMIT" \
  > "$WORK/logs/freeze.log" 2>&1

node "$WORK/esm/render-frozen.mjs" \
  "$WORK/freeze/rhythm-frozen-analysis.json" \
  "$WORK/freeze/pdf" \
  "$WORK/esm/createV143RhythmPdf.mjs" \
  > "$WORK/logs/render-frozen-pdf.log" 2>&1

python validation/rhythm_holdout/verify_pdf_event_fidelity.py \
  "$WORK/freeze" \
  "$WORK/freeze/pdf/pdf-event-evidence.json" \
  > "$WORK/logs/pdf-event-fidelity.log" 2>&1

python - "$WORK" "$SOURCE_COMMIT" <<'PY'
import json
import sys
from pathlib import Path

work = Path(sys.argv[1])
source_commit = sys.argv[2]
isolation = json.loads((work / "logs/runtime-isolation.json").read_text(encoding="utf-8"))
manifest = json.loads((work / "freeze/rhythm-freeze-manifest.json").read_text(encoding="utf-8"))
pdf = json.loads((work / "freeze/rhythm-pdf-event-fidelity.json").read_text(encoding="utf-8"))
render = json.loads((work / "freeze/pdf/pdf-event-evidence.json").read_text(encoding="utf-8"))

checks = {
    "runtimeIsolationPassed": isolation.get("passed") is True,
    "syntheticEventCount400": manifest.get("eventCount") == 400,
    "syntheticMeasureCount100": manifest.get("uniqueMeasureCount") == 100,
    "sourceAudioHashPresent": bool(manifest.get("sourceAudioSha256")),
    "rendererProjectionExactlyEqual": render.get("rendererProjectionExactlyEqual") is True,
    "fullPdfHeaderValid": render.get("fullPdfHeaderValid") is True,
    "previewPdfHeaderValid": render.get("previewPdfHeaderValid") is True,
    "fullPdfRendered": int(render.get("fullPdfBytes") or 0) > 20000,
    "previewPdfRendered": int(render.get("previewPdfBytes") or 0) > 20000,
    "pdfEventFidelityExact": pdf.get("pdfEventFidelity") == 1.0,
    "pdfHashMatchesFrozen": pdf.get("pdfEventSha256") == manifest.get("eventSha256"),
}
failed = [name for name, passed in checks.items() if not passed]
report = {
    "schemaVersion": 1,
    "gate": "rhythm-preholdout-static-preflight",
    "sourceCommit": source_commit,
    "eventCount": manifest.get("eventCount"),
    "uniqueMeasureCount": manifest.get("uniqueMeasureCount"),
    "frozenEventSha256": manifest.get("eventSha256"),
    "pdfEventSha256": manifest.get("pdfEventSha256"),
    "pdfEventFidelity": manifest.get("pdfEventFidelity"),
    "fullPdfBytes": render.get("fullPdfBytes"),
    "previewPdfBytes": render.get("previewPdfBytes"),
    "fullPageCount": render.get("fullPageCount"),
    "previewPageCount": render.get("previewPageCount"),
    "checks": checks,
    "failedChecks": failed,
    "usesSyntheticAudioResponseOnly": True,
    "realProfessionalReferenceOpened": False,
    "productionModified": False,
    "productionPromotionAuthorized": False,
    "passed": not failed,
}
(work / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
if failed:
    raise SystemExit("Static preflight failed: " + ", ".join(failed))
PY
