#!/usr/bin/env bash
set -euo pipefail

OUT="${OUT:-debug/v143-contextual-prune/existing-preview-async-breakthrough}"
mkdir -p "$OUT"

require_env() {
  local name="$1"
  test -n "${!name:-}" || {
    echo "Missing required environment variable: $name" >&2
    exit 2
  }
}

for name in \
  VERCEL_TOKEN PREVIEW_URL PREVIEW_DEPLOYMENT_ID EXPECTED_PREVIEW_SOURCE_COMMIT \
  EXPECTED_ROUTE_BLOB EXPECTED_PAGE_BLOB HARDENED_BRIDGE_BLOB PROTOCOL_BLOB \
  WORKER_BLOB SCHEDULER_BLOB AUDIO_URL AUDIO_BLOB_SHA
do
  require_env "$name"
done

write_base_summary() {
  python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ.get("OUT", "debug/v143-contextual-prune/existing-preview-async-breakthrough"))
out.mkdir(parents=True, exist_ok=True)
summary = {
    "schemaVersion": 1,
    "gate": "v143-existing-preview-async-breakthrough-e2e",
    "previewDeploymentId": os.environ["PREVIEW_DEPLOYMENT_ID"],
    "previewDeploymentUrl": os.environ["PREVIEW_URL"],
    "expectedPreviewSourceCommit": os.environ["EXPECTED_PREVIEW_SOURCE_COMMIT"],
    "routeBlob": os.environ["EXPECTED_ROUTE_BLOB"],
    "pageBlob": os.environ["EXPECTED_PAGE_BLOB"],
    "hardenedBridgeBlob": os.environ["HARDENED_BRIDGE_BLOB"],
    "protocolBlob": os.environ["PROTOCOL_BLOB"],
    "workerBlob": os.environ["WORKER_BLOB"],
    "schedulerBlob": os.environ["SCHEDULER_BLOB"],
    "audioBlobSha": os.environ["AUDIO_BLOB_SHA"],
    "protectedTransport": "authenticated-vercel-curl",
    "backendCapableRealAudioStartRequestCount": 0,
    "startAccepted": False,
    "completed": False,
    "acknowledged": False,
    "transientResultCleared": False,
    "productionEnvironmentChanged": False,
    "productionPromotionPerformed": False,
    "deploymentProtectionDisabled": False,
    "rawTranscriptionRetained": False,
    "referenceFacingInputs": 0,
    "referenceFacingAccuracyScored": False,
    "referenceScoreCalls": 0,
    "qualityVerdictMade": False,
}
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
}

patch_summary() {
  python3 - "$@" <<'PY'
import json, sys
from pathlib import Path
out = Path("debug/v143-contextual-prune/existing-preview-async-breakthrough")
path = out / "summary.json"
summary = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
for arg in sys.argv[1:]:
    key, value = arg.split("=", 1)
    if value == "true":
        parsed = True
    elif value == "false":
        parsed = False
    elif value == "null":
        parsed = None
    else:
        try:
            parsed = int(value)
        except ValueError:
            try:
                parsed = float(value)
            except ValueError:
                parsed = value
    summary[key] = parsed
path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
}

echo "sourceBoundary=checking"
test "$(git hash-object app/api/analyze-audio-tab/route.js)" = "$EXPECTED_ROUTE_BLOB"
test "$(git hash-object app/ai-tab/page.js)" = "$EXPECTED_PAGE_BLOB"
test "$(git hash-object analyzer/v143_modal_http_endpoint.py)" = "$HARDENED_BRIDGE_BLOB"
test "$(git hash-object analyzer/v143_async_job_protocol.py)" = "$PROTOCOL_BLOB"
test "$(git hash-object analyzer/v143_modal_live_endpoint.py)" = "$WORKER_BLOB"
test "$(git hash-object analyzer/v143_seeded_separator.py)" = "$SCHEDULER_BLOB"
test "$(git hash-object public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a)" = "$AUDIO_BLOB_SHA"
echo "backendCapableRealAudioStartRequestBudget=1"
echo "provenPriorBackendModelStarts=0"
echo "productionEnvironmentTargeted=false"
echo "productionPromotionPerformed=false"

export OUT
write_base_summary

vercel inspect "$PREVIEW_URL" --token "$VERCEL_TOKEN" 2>&1 | tee "$OUT/inspect.log"
grep -Fq "$PREVIEW_DEPLOYMENT_ID" "$OUT/inspect.log"
grep -Eq 'target[[:space:]]+preview' "$OUT/inspect.log"
grep -Eq 'status[[:space:]]+.*Ready|status[[:space:]]+● Ready' "$OUT/inspect.log"
echo "existingPreviewIdentityVerified=true"

PREFLIGHT_STATUS="$(
  vercel curl /api/analyze-audio-tab \
    --deployment "$PREVIEW_URL" \
    -- \
    --silent --show-error --max-time 30 \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary '{"transcriptionType":"invalid"}' \
    --output "$OUT/preflight-response.json" \
    --write-out '%{http_code}'
)"
echo "protectedPreviewRoutePreflightStatus=$PREFLIGHT_STATUS"
export PREFLIGHT_STATUS
set +e
python3 - <<'PY2'
import json, os
from pathlib import Path
out = Path(os.environ["OUT"])
try:
    data = json.loads((out / "preflight-response.json").read_text(encoding="utf-8"))
except Exception:
    data = {}
ok = (
    int(os.environ["PREFLIGHT_STATUS"]) == 400
    and data.get("error") == "Transcription type must be lead, rhythm, or bass."
)
print(f"protectedPreviewRouteReached={str(ok).lower()}")
raise SystemExit(0 if ok else 1)
PY2
PREFLIGHT_PARSE_RC=$?
set -e
patch_summary \
  "protectedPreviewStatus=$PREFLIGHT_STATUS" \
  "previewIdentityVerified=true"
if [ "$PREFLIGHT_PARSE_RC" -ne 0 ]; then
  patch_summary "error=Protected Preview model-free route preflight failed before real-audio start."
  echo "Protected Preview model-free route preflight failed before real-audio start; do not send a start." >&2
  exit 3
fi

cat > "$OUT/start-request.json" <<JSON
{"operation":"start","audioUrl":"$AUDIO_URL","pathname":"gomyway-midterm-source.m4a","song":"Are You Gonna Go My Way","artist":"Lenny Kravitz","transcriptionType":"rhythm"}
JSON

START_EPOCH="$(date +%s)"
set +e
START_METRICS="$(
  vercel curl /api/analyze-audio-tab \
    --deployment "$PREVIEW_URL" \
    -- \
    --silent --show-error --max-time 45 \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary "@$OUT/start-request.json" \
    --output "$OUT/start-response.json" \
    --write-out '%{http_code} %{time_total}'
)"
START_CURL_RC=$?
set -e

START_STATUS="${START_METRICS%% *}"
START_SECONDS="${START_METRICS#* }"
if ! [[ "$START_STATUS" =~ ^[0-9]{3}$ ]]; then START_STATUS=0; fi
patch_summary \
  "backendCapableRealAudioStartRequestCount=1" \
  "startStatus=$START_STATUS" \
  "startCurlExitCode=$START_CURL_RC" \
  "startRequestSeconds=${START_SECONDS:-0}"

export START_STATUS START_SECONDS
set +e
python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ["OUT"])
try:
    data = json.loads((out / "start-response.json").read_text(encoding="utf-8"))
except Exception:
    data = {}
job = data.get("analysisJob") if isinstance(data.get("analysisJob"), dict) else {}
token = str(job.get("token") or "")
ok = int(os.environ["START_STATUS"]) == 202 and job.get("status") == "processing" and token.startswith("v143a1.")
if ok:
    (out / "job-token.txt").write_text(token, encoding="utf-8")
    print("startAccepted=true")
raise SystemExit(0 if ok else 1)
PY
START_PARSE_RC=$?
set -e

if [ "$START_CURL_RC" -ne 0 ] || [ "$START_PARSE_RC" -ne 0 ]; then
  patch_summary \
    "startAccepted=false" \
    "terminalState=start-response-unusable" \
    "error=The single backend-capable real-audio start did not return an accepted signed async job token."
  echo "The one backend-capable real-audio start was sent but no usable token was returned. STOP: do not send a second start." >&2
  exit 4
fi

patch_summary "startAccepted=true"
JOB_TOKEN="$(cat "$OUT/job-token.txt")"
POLL_COUNT=0
TERMINAL_STATUS=''
TERMINAL_SECONDS=''
TERMINAL_KIND=''
DEADLINE=$(( START_EPOCH + 20 * 60 ))

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  POLL_COUNT=$((POLL_COUNT + 1))
  sleep 5
  printf '{"operation":"status","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/status-request.json"

  set +e
  POLL_METRICS="$(
    vercel curl /api/analyze-audio-tab \
      --deployment "$PREVIEW_URL" \
      -- \
      --silent --show-error --max-time 45 \
      --request POST \
      --header 'Content-Type: application/json' \
      --data-binary "@$OUT/status-request.json" \
      --output "$OUT/status-response.json" \
      --write-out '%{http_code} %{time_total}'
  )"
  POLL_CURL_RC=$?
  set -e

  if [ "$POLL_CURL_RC" -ne 0 ]; then
    echo "poll=$POLL_COUNT transportError=$POLL_CURL_RC; same-token polling only"
    continue
  fi

  POLL_STATUS="${POLL_METRICS%% *}"
  POLL_SECONDS="${POLL_METRICS#* }"
  ELAPSED=$(( $(date +%s) - START_EPOCH ))
  echo "poll=$POLL_COUNT status=$POLL_STATUS requestSeconds=$POLL_SECONDS elapsed=$ELAPSED"

  if [ "$POLL_STATUS" = "202" ]; then
    continue
  fi

  TERMINAL_STATUS="$POLL_STATUS"
  TERMINAL_SECONDS="$POLL_SECONDS"
  if [ "$POLL_STATUS" = "200" ]; then
    TERMINAL_KIND="completed"
  else
    TERMINAL_KIND="failed"
  fi
  break
done

if [ -z "$TERMINAL_STATUS" ]; then
  ELAPSED=$(( $(date +%s) - START_EPOCH ))
  patch_summary \
    "pollCount=$POLL_COUNT" \
    "asyncTotalSeconds=$ELAPSED" \
    "terminalStatus=0" \
    "terminalState=poll-deadline-exceeded" \
    "error=Same-token polling deadline exceeded after the single backend-capable start."
  echo "Polling deadline exceeded. STOP: do not send another start." >&2
  exit 5
fi

export TERMINAL_STATUS TERMINAL_SECONDS TERMINAL_KIND POLL_COUNT START_EPOCH
python3 - <<'PY'
import json, os, time
from pathlib import Path
out = Path(os.environ["OUT"])
try:
    terminal = json.loads((out / "status-response.json").read_text(encoding="utf-8"))
except Exception:
    terminal = {}
completed = os.environ["TERMINAL_KIND"] == "completed"
pc = terminal.get("payloadContract") if isinstance(terminal.get("payloadContract"), dict) else {}
aq = terminal.get("analysisQuality") if isinstance(terminal.get("analysisQuality"), dict) else {}
metrics = aq.get("metrics") if isinstance(aq.get("metrics"), dict) else {}
conditioning = terminal.get("conditioningContract") if isinstance(terminal.get("conditioningContract"), dict) else {}
job = terminal.get("analysisJob") if isinstance(terminal.get("analysisJob"), dict) else {}
total_seconds = max(0.0, time.time() - float(os.environ["START_EPOCH"]))
summary_path = out / "summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary.update({
    "pollCount": int(os.environ["POLL_COUNT"]),
    "terminalStatus": int(os.environ["TERMINAL_STATUS"]),
    "terminalRequestSeconds": float(os.environ["TERMINAL_SECONDS"]),
    "terminalState": os.environ["TERMINAL_KIND"],
    "asyncTotalSeconds": total_seconds,
    "crossedOld150SecondWall": total_seconds > 150.0,
    "completed": completed,
    "analysisJobCompleted": job.get("status") == "completed",
    "rhythmCanaryActive": terminal.get("rhythmCanaryActive"),
    "generatedTabPresent": bool(str(terminal.get("generatedTab") or "").strip()),
    "eventCount": len(terminal.get("events") or []) if isinstance(terminal.get("events"), list) else 0,
    "renderEventCount": len(terminal.get("renderEvents") or []) if isinstance(terminal.get("renderEvents"), list) else 0,
    "payloadContract": {
        "referenceFree": pc.get("referenceFree"),
        "professionalReferenceNotUsed": pc.get("professionalReferenceNotUsed"),
        "referenceRuntimeInputNotUsed": pc.get("referenceRuntimeInputNotUsed"),
        "runtimeLabelsNotRequired": pc.get("runtimeLabelsNotRequired"),
        "v143RuntimeSafetyVerified": pc.get("v143RuntimeSafetyVerified"),
        "analyzerQualityGatePassed": pc.get("analyzerQualityGatePassed"),
        "structuredRenderEligible": pc.get("structuredRenderEligible"),
    },
    "productHealthSignals": {
        "analysisQualityGatePassed": aq.get("passed"),
        "analysisQualityFailures": aq.get("failures"),
        "rawEventCount": metrics.get("rawEventCount"),
        "validRenderEventCount": metrics.get("validRenderEventCount"),
        "renderEventSurvivalPercent": metrics.get("renderEventSurvivalPercent"),
        "playableStringFretPercent": metrics.get("playableStringFretPercent"),
        "musicalPlacementPercent": metrics.get("musicalPlacementPercent"),
        "pitchValidityPercent": metrics.get("pitchValidityPercent"),
    },
    "conditioningReferenceBlind": conditioning.get("referenceBlind"),
    "conditioningReferenceScoreAuthorized": conditioning.get("referenceScoreAuthorized"),
})
if not completed:
    error = terminal.get("error") or terminal.get("detail") or "Async job returned terminal failure."
    summary["error"] = str(error)[:240]
summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
PY

printf '{"operation":"ack","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/ack-request.json"
set +e
ACK_METRICS="$(
  vercel curl /api/analyze-audio-tab \
    --deployment "$PREVIEW_URL" \
    -- \
    --silent --show-error --max-time 45 \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary "@$OUT/ack-request.json" \
    --output "$OUT/ack-response.json" \
    --write-out '%{http_code} %{time_total}'
)"
ACK_CURL_RC=$?
set -e

ACK_STATUS="${ACK_METRICS%% *}"
ACK_SECONDS="${ACK_METRICS#* }"
if ! [[ "$ACK_STATUS" =~ ^[0-9]{3}$ ]]; then ACK_STATUS=0; fi
export ACK_STATUS ACK_SECONDS ACK_CURL_RC

python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ["OUT"])
summary_path = out / "summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
try:
    ack = json.loads((out / "ack-response.json").read_text(encoding="utf-8"))
except Exception:
    ack = {}
job = ack.get("analysisJob") if isinstance(ack.get("analysisJob"), dict) else {}
summary.update({
    "ackStatus": int(os.environ["ACK_STATUS"]),
    "ackCurlExitCode": int(os.environ["ACK_CURL_RC"]),
    "ackRequestSeconds": float(os.environ["ACK_SECONDS"] or 0),
    "acknowledged": job.get("status") == "acknowledged",
    "transientResultCleared": job.get("resultCleared") is True,
    "bridgeAckContractClearsControl": True,
})
summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))

if summary["ackStatus"] != 200 or not summary["acknowledged"] or not summary["transientResultCleared"]:
    raise SystemExit("ACK/cleanup failed after the single backend-capable start. STOP: no retry.")

if not summary["completed"]:
    raise SystemExit("The single async job reached terminal failure after ACK/cleanup. STOP: diagnose exact call, no retry.")

if summary["analysisJobCompleted"] is not True or summary["rhythmCanaryActive"] is not True or not summary["generatedTabPresent"]:
    raise SystemExit("Completed result failed required product state after ACK/cleanup. STOP: no retry.")

for key in ("referenceFree","professionalReferenceNotUsed","referenceRuntimeInputNotUsed","runtimeLabelsNotRequired","v143RuntimeSafetyVerified"):
    if summary["payloadContract"].get(key) is not True:
        raise SystemExit(f"Runtime safety contract failed after ACK/cleanup: {key}. STOP: no retry.")
PY
