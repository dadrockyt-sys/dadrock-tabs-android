#!/usr/bin/env bash
set -euo pipefail

OUT="${OUT:-debug/v143-contextual-prune/fresh-preview-async-breakthrough}"
mkdir -p "$OUT"

require_env() {
  local name="$1"
  test -n "${!name:-}" || {
    echo "Missing required environment variable: $name" >&2
    exit 2
  }
}

for name in \
  VERCEL_TOKEN PREVIEW_GIT_BRANCH EXPECTED_ROUTE_BLOB EXPECTED_PAGE_BLOB \
  HARDENED_BRIDGE_BLOB PROTOCOL_BLOB WORKER_BLOB SCHEDULER_BLOB \
  AUDIO_URL AUDIO_BLOB_SHA GITHUB_SHA
do
  require_env "$name"
done

test -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}"
test -n "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:-}"

mint_oidc() {
  local response token
  response="$(
    curl --silent --show-error --fail \
      --retry 2 --retry-all-errors \
      --header "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
      "$ACTIONS_ID_TOKEN_REQUEST_URL"
  )"
  token="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])' <<<"$response")"
  test -n "$token"
  echo "::add-mask::$token" >&2
  printf '%s' "$token"
}

write_preflight_summary() {
  local status="$1"
  PREFLIGHT_STATUS="$status" python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ.get("OUT", "debug/v143-contextual-prune/fresh-preview-async-breakthrough"))
out.mkdir(parents=True, exist_ok=True)
summary = {
    "schemaVersion": 1,
    "gate": "v143-fresh-preview-async-breakthrough-e2e",
    "previewDeploymentId": os.environ.get("PREVIEW_DEPLOYMENT_ID"),
    "previewDeploymentUrl": os.environ.get("PREVIEW_DEPLOYMENT_URL"),
    "previewBuildSourceCommit": os.environ.get("GITHUB_SHA"),
    "routeBlob": os.environ.get("EXPECTED_ROUTE_BLOB"),
    "pageBlob": os.environ.get("EXPECTED_PAGE_BLOB"),
    "hardenedBridgeBlob": os.environ.get("HARDENED_BRIDGE_BLOB"),
    "protocolBlob": os.environ.get("PROTOCOL_BLOB"),
    "workerBlob": os.environ.get("WORKER_BLOB"),
    "schedulerBlob": os.environ.get("SCHEDULER_BLOB"),
    "audioBlobSha": os.environ.get("AUDIO_BLOB_SHA"),
    "protectedPreviewStatus": int(os.environ["PREFLIGHT_STATUS"]),
    "trustedOidcAccessGranted": os.environ["PREFLIGHT_STATUS"] == "200",
    "modelBearingStartRequestCount": 0,
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

write_start_failure_summary() {
  local status="$1"
  local curl_rc="$2"
  START_STATUS="$status" START_CURL_RC="$curl_rc" python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ.get("OUT", "debug/v143-contextual-prune/fresh-preview-async-breakthrough"))
path = out / "summary.json"
summary = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
summary.update({
    "modelBearingStartRequestCount": 1,
    "startStatus": int(os.environ.get("START_STATUS") or 0),
    "startCurlExitCode": int(os.environ.get("START_CURL_RC") or 0),
    "startAccepted": False,
    "terminalState": "start-response-unusable",
    "error": "The single start request did not return an accepted signed async job token.",
})
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
echo "modelBearingStartRequestBudget=1"
echo "priorE2EModelStarts=0"
echo "productionEnvironmentTargeted=false"
echo "productionPromotionPerformed=false"

vercel pull --yes --environment=preview --git-branch="$PREVIEW_GIT_BRANCH" --token "$VERCEL_TOKEN" >/dev/null
vercel build --token "$VERCEL_TOKEN"
DEPLOYMENT_URL="$(vercel deploy --prebuilt --token "$VERCEL_TOKEN" | tail -n 1)"
echo "$DEPLOYMENT_URL" | grep -Eq '^https://[^ ]+\.vercel\.app$'
export PREVIEW_DEPLOYMENT_URL="$DEPLOYMENT_URL"
echo "PREVIEW_DEPLOYMENT_URL=$DEPLOYMENT_URL" >> "$GITHUB_ENV"
echo "freshPreviewUrl=$DEPLOYMENT_URL"
echo "productionPromotionPerformed=false"

vercel inspect "$DEPLOYMENT_URL" --wait --token "$VERCEL_TOKEN" 2>&1 | tee "$OUT/inspect.log"
grep -Eq 'target[[:space:]]+preview' "$OUT/inspect.log"
grep -Eq 'status[[:space:]]+.*Ready|status[[:space:]]+● Ready' "$OUT/inspect.log"
DEPLOYMENT_ID="$(awk '$1 == "id" {print $2; exit}' "$OUT/inspect.log")"
test -n "$DEPLOYMENT_ID"
export PREVIEW_DEPLOYMENT_ID="$DEPLOYMENT_ID"
echo "PREVIEW_DEPLOYMENT_ID=$DEPLOYMENT_ID" >> "$GITHUB_ENV"
echo "freshPreviewDeploymentId=$DEPLOYMENT_ID"

OIDC_TOKEN="$(mint_oidc)"
PREFLIGHT_STATUS="$(
  curl --silent --show-error --location --max-time 30 \
    --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" \
    --output /dev/null --write-out '%{http_code}' \
    "$PREVIEW_DEPLOYMENT_URL/ai-tab"
)"
unset OIDC_TOKEN
export OUT PREVIEW_DEPLOYMENT_ID PREVIEW_DEPLOYMENT_URL
write_preflight_summary "$PREFLIGHT_STATUS"
echo "protectedPreviewAiTabStatus=$PREFLIGHT_STATUS"
if [ "$PREFLIGHT_STATUS" != "200" ]; then
  echo "Protected Preview preflight failed before model start; do not retry blindly." >&2
  exit 3
fi
echo "modelBearingStartRequestsSoFar=0"

cat > "$OUT/start-request.json" <<JSON
{"operation":"start","audioUrl":"$AUDIO_URL","pathname":"gomyway-midterm-source.m4a","song":"Are You Gonna Go My Way","artist":"Lenny Kravitz","transcriptionType":"rhythm"}
JSON

START_EPOCH="$(date +%s)"
OIDC_TOKEN="$(mint_oidc)"
set +e
START_METRICS="$(
  curl --silent --show-error --location --max-time 45 \
    --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary "@$OUT/start-request.json" \
    --output "$OUT/start-response.json" \
    --write-out '%{http_code} %{time_total}' \
    "$PREVIEW_DEPLOYMENT_URL/api/analyze-audio-tab"
)"
START_CURL_RC=$?
set -e
unset OIDC_TOKEN
START_STATUS="${START_METRICS%% *}"
START_SECONDS="${START_METRICS#* }"
if ! [[ "$START_STATUS" =~ ^[0-9]{3}$ ]]; then START_STATUS=0; fi

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
    print(f"startStatus=202 startSeconds={float(os.environ['START_SECONDS']):.6f} modelBearingStartRequests=1")
raise SystemExit(0 if ok else 1)
PY
START_PARSE_RC=$?
set -e

if [ "$START_CURL_RC" -ne 0 ] || [ "$START_PARSE_RC" -ne 0 ]; then
  write_start_failure_summary "$START_STATUS" "$START_CURL_RC"
  echo "The one start request was sent but did not yield a usable accepted token. Do not send a second start; diagnose this request." >&2
  exit 4
fi

JOB_TOKEN="$(cat "$OUT/job-token.txt")"
POLL_COUNT=0
COMPLETION_STATUS=''
COMPLETION_SECONDS=''
COMPLETED=0
DEADLINE=$(( START_EPOCH + 20 * 60 ))

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  POLL_COUNT=$((POLL_COUNT + 1))
  sleep 5
  printf '{"operation":"status","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/status-request.json"
  OIDC_TOKEN="$(mint_oidc)"
  set +e
  POLL_METRICS="$(
    curl --silent --show-error --location --max-time 45 \
      --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" \
      --request POST \
      --header 'Content-Type: application/json' \
      --data-binary "@$OUT/status-request.json" \
      --output "$OUT/status-response.json" \
      --write-out '%{http_code} %{time_total}' \
      "$PREVIEW_DEPLOYMENT_URL/api/analyze-audio-tab"
  )"
  POLL_CURL_RC=$?
  set -e
  unset OIDC_TOKEN
  if [ "$POLL_CURL_RC" -ne 0 ]; then
    echo "poll=$POLL_COUNT transportError=$POLL_CURL_RC; same-token polling will continue"
    continue
  fi
  POLL_STATUS="${POLL_METRICS%% *}"
  POLL_SECONDS="${POLL_METRICS#* }"
  ELAPSED=$(( $(date +%s) - START_EPOCH ))
  echo "poll=$POLL_COUNT status=$POLL_STATUS requestSeconds=$POLL_SECONDS elapsed=$ELAPSED"
  if [ "$POLL_STATUS" = "202" ]; then
    continue
  fi
  COMPLETION_STATUS="$POLL_STATUS"
  COMPLETION_SECONDS="$POLL_SECONDS"
  [ "$POLL_STATUS" = "200" ] && COMPLETED=1 || true
  break
done

export START_EPOCH START_STATUS START_SECONDS POLL_COUNT COMPLETION_STATUS COMPLETION_SECONDS COMPLETED
if [ -z "$COMPLETION_STATUS" ]; then
  python3 - <<'PY'
import json, os, time
from pathlib import Path
out = Path(os.environ["OUT"])
path = out / "summary.json"
summary = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
summary.update({
    "modelBearingStartRequestCount": 1,
    "startStatus": int(os.environ["START_STATUS"]),
    "startRequestSeconds": float(os.environ["START_SECONDS"]),
    "pollCount": int(os.environ["POLL_COUNT"]),
    "terminalStatus": 0,
    "asyncTotalSeconds": max(0.0, time.time() - float(os.environ["START_EPOCH"])),
    "completed": False,
    "terminalState": "poll-deadline-exceeded",
    "error": "Same-token status polling reached its deadline without a terminal response.",
})
path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
  echo "Polling deadline reached after the single model-bearing start. Do not retry; diagnose this exact job." >&2
  exit 5
fi

python3 - <<'PY'
import json, os, time
from pathlib import Path
out = Path(os.environ["OUT"])
try:
    terminal = json.loads((out / "status-response.json").read_text(encoding="utf-8"))
except Exception:
    terminal = {}
completed = os.environ["COMPLETED"] == "1"
pc = terminal.get("payloadContract") if isinstance(terminal.get("payloadContract"), dict) else {}
aq = terminal.get("analysisQuality") if isinstance(terminal.get("analysisQuality"), dict) else {}
metrics = aq.get("metrics") if isinstance(aq.get("metrics"), dict) else {}
conditioning = terminal.get("conditioningContract") if isinstance(terminal.get("conditioningContract"), dict) else {}
job = terminal.get("analysisJob") if isinstance(terminal.get("analysisJob"), dict) else {}
total_seconds = max(0.0, time.time() - float(os.environ["START_EPOCH"]))
summary = {
    "schemaVersion": 1,
    "gate": "v143-fresh-preview-async-breakthrough-e2e",
    "previewDeploymentId": os.environ["PREVIEW_DEPLOYMENT_ID"],
    "previewDeploymentUrl": os.environ["PREVIEW_DEPLOYMENT_URL"],
    "previewBuildSourceCommit": os.environ["GITHUB_SHA"],
    "routeBlob": os.environ["EXPECTED_ROUTE_BLOB"],
    "pageBlob": os.environ["EXPECTED_PAGE_BLOB"],
    "hardenedBridgeBlob": os.environ["HARDENED_BRIDGE_BLOB"],
    "protocolBlob": os.environ["PROTOCOL_BLOB"],
    "workerBlob": os.environ["WORKER_BLOB"],
    "schedulerBlob": os.environ["SCHEDULER_BLOB"],
    "audioBlobSha": os.environ["AUDIO_BLOB_SHA"],
    "protectedPreviewStatus": 200,
    "trustedOidcAccessGranted": True,
    "modelBearingStartRequestCount": 1,
    "startStatus": int(os.environ["START_STATUS"]),
    "startRequestSeconds": float(os.environ["START_SECONDS"]),
    "pollCount": int(os.environ["POLL_COUNT"]),
    "terminalStatus": int(os.environ["COMPLETION_STATUS"]),
    "terminalRequestSeconds": float(os.environ["COMPLETION_SECONDS"]),
    "terminalState": "completed" if completed else "failed",
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
    "productionEnvironmentChanged": False,
    "productionPromotionPerformed": False,
    "deploymentProtectionDisabled": False,
    "rawTranscriptionRetained": False,
    "referenceFacingInputs": 0,
    "referenceFacingAccuracyScored": False,
    "referenceScoreCalls": 0,
    "qualityVerdictMade": False,
}
if not completed:
    error = terminal.get("error") or terminal.get("detail") or "async job did not complete"
    summary["error"] = str(error)[:240]
(out / "summary-pre-ack.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
PY

printf '{"operation":"ack","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/ack-request.json"
OIDC_TOKEN="$(mint_oidc)"
set +e
ACK_METRICS="$(
  curl --silent --show-error --location --max-time 45 \
    --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary "@$OUT/ack-request.json" \
    --output "$OUT/ack-response.json" \
    --write-out '%{http_code} %{time_total}' \
    "$PREVIEW_DEPLOYMENT_URL/api/analyze-audio-tab"
)"
ACK_CURL_RC=$?
set -e
unset OIDC_TOKEN
ACK_STATUS="${ACK_METRICS%% *}"
ACK_SECONDS="${ACK_METRICS#* }"
if ! [[ "$ACK_STATUS" =~ ^[0-9]{3}$ ]]; then ACK_STATUS=0; fi
export ACK_STATUS ACK_SECONDS ACK_CURL_RC

python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ["OUT"])
summary = json.loads((out / "summary-pre-ack.json").read_text(encoding="utf-8"))
try:
    ack = json.loads((out / "ack-response.json").read_text(encoding="utf-8"))
except Exception:
    ack = {}
job = ack.get("analysisJob") if isinstance(ack.get("analysisJob"), dict) else {}
summary["ackStatus"] = int(os.environ["ACK_STATUS"])
summary["ackCurlExitCode"] = int(os.environ["ACK_CURL_RC"])
summary["ackRequestSeconds"] = float(os.environ["ACK_SECONDS"] or 0)
summary["acknowledged"] = job.get("status") == "acknowledged"
summary["transientResultCleared"] = job.get("resultCleared") is True
summary["bridgeAckContractClearsControl"] = True
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))

if summary["ackStatus"] != 200 or not summary["acknowledged"] or not summary["transientResultCleared"]:
    raise SystemExit("Async ACK/cleanup failed after the one model-bearing start; do not retry the start.")

if not summary["completed"]:
    raise SystemExit("The one model-bearing async job reached terminal failure after ACK/cleanup; diagnose this exact call and do not retry.")

if summary["analysisJobCompleted"] is not True or summary["rhythmCanaryActive"] is not True or not summary["generatedTabPresent"]:
    raise SystemExit("Completed async result failed required V143 product state after ACK/cleanup; do not retry.")

for key in ("referenceFree","professionalReferenceNotUsed","referenceRuntimeInputNotUsed","runtimeLabelsNotRequired","v143RuntimeSafetyVerified"):
    if summary["payloadContract"].get(key) is not True:
        raise SystemExit(f"Runtime safety contract failed after ACK/cleanup: {key}; do not retry.")
PY
