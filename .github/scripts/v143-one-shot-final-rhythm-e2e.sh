#!/usr/bin/env bash
set -euo pipefail

OUT="${OUT:-debug/v143-contextual-prune/final-rhythm-one-shot}"
FREEZE="$OUT/freeze"
PDF_DIR="$FREEZE/pdf"
FINAL_DIR="$OUT/final-holdout"
REF_SOURCE="research/v154-professional-references/rhythm-professional-reference.json"
REF_TMP="validation/rhythm_holdout/reference/.one-shot-professional-rhythm-reference.json"
mkdir -p "$OUT" "$FREEZE" "$PDF_DIR" "$FINAL_DIR"

require_env() {
  local name="$1"
  test -n "${!name:-}" || { echo "Missing required env: $name" >&2; exit 2; }
}

for name in VERCEL_TOKEN PREVIEW_GIT_BRANCH EXPECTED_ROUTE_BLOB EXPECTED_PAGE_BLOB HARDENED_BRIDGE_BLOB PROTOCOL_BLOB WORKER_BLOB SCHEDULER_BLOB AUDIO_URL AUDIO_BLOB_SHA PROFESSIONAL_REFERENCE_SHA256 GITHUB_SHA; do
  require_env "$name"
done

test -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}"
test -n "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:-}"

mint_oidc() {
  local response token
  response="$(curl --silent --show-error --fail --retry 2 --retry-all-errors --header "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL")"
  token="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])' <<<"$response")"
  test -n "$token"
  echo "::add-mask::$token" >&2
  printf '%s' "$token"
}

sha256_file() {
  python3 - "$1" <<'PY'
import hashlib, pathlib, sys
p=pathlib.Path(sys.argv[1]); h=hashlib.sha256()
with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
print(h.hexdigest())
PY
}

write_initial_summary() {
  python3 - <<'PY'
import json, os
from pathlib import Path
out=Path(os.environ.get('OUT','debug/v143-contextual-prune/final-rhythm-one-shot'))
out.mkdir(parents=True,exist_ok=True)
summary={
 'schemaVersion':1,'gate':'v143-final-rhythm-one-shot','sourceCommit':os.environ['GITHUB_SHA'],
 'routeBlob':os.environ['EXPECTED_ROUTE_BLOB'],'pageBlob':os.environ['EXPECTED_PAGE_BLOB'],
 'bridgeBlob':os.environ['HARDENED_BRIDGE_BLOB'],'protocolBlob':os.environ['PROTOCOL_BLOB'],
 'workerBlob':os.environ['WORKER_BLOB'],'schedulerBlob':os.environ['SCHEDULER_BLOB'],
 'audioBlobSha':os.environ['AUDIO_BLOB_SHA'],'professionalReferenceSha256':os.environ['PROFESSIONAL_REFERENCE_SHA256'],
 'modelBearingStartRequestCount':0,'professionalScoreCalls':0,'pdfE2EPerformed':False,
 'productionEnvironmentChanged':False,'productionPromotionPerformed':False,'deploymentProtectionDisabled':False,
 'referenceOpenedBeforeFreeze':False,'rawAudioRetained':False,'rawStemsRetained':False,'modelBytesRetained':False,
 'completed':False,'acknowledged':False,'transientResultCleared':False
}
(out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
PY
}

patch_summary() {
  python3 - "$@" <<'PY'
import json,sys
from pathlib import Path
p=Path('debug/v143-contextual-prune/final-rhythm-one-shot/summary.json')
s=json.loads(p.read_text())
for arg in sys.argv[1:]:
    k,v=arg.split('=',1)
    if v=='true': v=True
    elif v=='false': v=False
    elif v=='null': v=None
    else:
        try: v=int(v)
        except ValueError:
            try: v=float(v)
            except ValueError: pass
    s[k]=v
p.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
PY
}

export OUT
write_initial_summary
trap 'rm -f "$REF_TMP"' EXIT

echo 'sourceBoundary=checking'
test "$(git hash-object app/api/analyze-audio-tab/route.js)" = "$EXPECTED_ROUTE_BLOB"
test "$(git hash-object app/ai-tab/page.js)" = "$EXPECTED_PAGE_BLOB"
test "$(git hash-object analyzer/v143_modal_http_endpoint.py)" = "$HARDENED_BRIDGE_BLOB"
test "$(git hash-object analyzer/v143_async_job_protocol.py)" = "$PROTOCOL_BLOB"
test "$(git hash-object analyzer/v143_modal_live_endpoint.py)" = "$WORKER_BLOB"
test "$(git hash-object analyzer/v143_seeded_separator.py)" = "$SCHEDULER_BLOB"
test "$(git hash-object public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a)" = "$AUDIO_BLOB_SHA"
test -f "$REF_SOURCE"
test "$(sha256_file "$REF_SOURCE")" = "$PROFESSIONAL_REFERENCE_SHA256"
echo 'liveBudgetBeforeStart=1'
echo 'professionalScoreBudgetBeforeScore=1'
echo 'productionTargeted=false'

# Fresh Preview only. No --prod, promote, rollback, env mutation, or protection mutation.
vercel pull --yes --environment=preview --git-branch="$PREVIEW_GIT_BRANCH" --token "$VERCEL_TOKEN" >/dev/null
vercel build --token "$VERCEL_TOKEN"
DEPLOYMENT_URL="$(vercel deploy --prebuilt --token "$VERCEL_TOKEN" | tail -n 1)"
echo "$DEPLOYMENT_URL" | grep -Eq '^https://[^ ]+\.vercel\.app$'
export PREVIEW_DEPLOYMENT_URL="$DEPLOYMENT_URL"
vercel inspect "$DEPLOYMENT_URL" --wait --token "$VERCEL_TOKEN" 2>&1 | tee "$OUT/inspect.log"
grep -Eq 'target[[:space:]]+preview' "$OUT/inspect.log"
grep -Eq 'status[[:space:]]+.*Ready|status[[:space:]]+● Ready' "$OUT/inspect.log"
DEPLOYMENT_ID="$(awk '$1 == "id" {print $2; exit}' "$OUT/inspect.log")"
test -n "$DEPLOYMENT_ID"
export PREVIEW_DEPLOYMENT_ID="$DEPLOYMENT_ID"
patch_summary "previewDeploymentId=$DEPLOYMENT_ID" "previewDeploymentUrl=$DEPLOYMENT_URL" "previewReady=true"

# Model-free protected route preflight.
OIDC_TOKEN="$(mint_oidc)"
PREFLIGHT_STATUS="$(curl --silent --show-error --location --max-time 30 --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" --request POST --header 'Content-Type: application/json' --data-binary '{"transcriptionType":"invalid"}' --output "$OUT/preflight-response.json" --write-out '%{http_code}' "$DEPLOYMENT_URL/api/analyze-audio-tab")"
unset OIDC_TOKEN
export PREFLIGHT_STATUS
python3 - <<'PY'
import json,os
from pathlib import Path
p=Path(os.environ['OUT'])/'preflight-response.json'
try:d=json.loads(p.read_text())
except Exception:d={}
ok=int(os.environ['PREFLIGHT_STATUS'])==400 and d.get('error')=='Transcription type must be lead, rhythm, or bass.'
print('protectedPreviewRouteReached='+str(ok).lower())
raise SystemExit(0 if ok else 1)
PY
patch_summary "protectedPreviewPreflightStatus=$PREFLIGHT_STATUS"

echo 'ONE-SHOT START BOUNDARY: the next request is the only authorized model-bearing start.'
cat > "$OUT/start-request.json" <<JSON
{"operation":"start","audioUrl":"$AUDIO_URL","pathname":"gomyway-midterm-source.m4a","song":"Are You Gonna Go My Way","artist":"Lenny Kravitz","transcriptionType":"rhythm"}
JSON
START_EPOCH="$(date +%s)"
OIDC_TOKEN="$(mint_oidc)"
set +e
START_METRICS="$(curl --silent --show-error --location --max-time 45 --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" --request POST --header 'Content-Type: application/json' --data-binary "@$OUT/start-request.json" --output "$OUT/start-response.json" --write-out '%{http_code} %{time_total}' "$DEPLOYMENT_URL/api/analyze-audio-tab")"
START_CURL_RC=$?
set -e
unset OIDC_TOKEN
START_STATUS="${START_METRICS%% *}"; START_SECONDS="${START_METRICS#* }"
[[ "$START_STATUS" =~ ^[0-9]{3}$ ]] || START_STATUS=0
patch_summary "modelBearingStartRequestCount=1" "liveBudgetConsumed=true" "startStatus=$START_STATUS" "startCurlExitCode=$START_CURL_RC" "startRequestSeconds=${START_SECONDS:-0}"
export START_STATUS
set +e
python3 - <<'PY'
import json,os
from pathlib import Path
out=Path(os.environ['OUT'])
try:d=json.loads((out/'start-response.json').read_text())
except Exception:d={}
j=d.get('analysisJob') if isinstance(d.get('analysisJob'),dict) else {}
t=str(j.get('token') or '')
ok=int(os.environ['START_STATUS'])==202 and j.get('status')=='processing' and t.startswith('v143a1.')
if ok:(out/'job-token.txt').write_text(t)
raise SystemExit(0 if ok else 1)
PY
START_PARSE_RC=$?
set -e
if [ "$START_CURL_RC" -ne 0 ] || [ "$START_PARSE_RC" -ne 0 ]; then
  patch_summary 'terminalState=start-response-unusable' 'error=Single authorized start did not yield a usable async token.'
  echo 'STOP: the single live start was consumed; no retry or replacement is authorized.' >&2
  exit 4
fi

JOB_TOKEN="$(cat "$OUT/job-token.txt")"
POLL_COUNT=0; TERMINAL_STATUS=''; DEADLINE=$((START_EPOCH+20*60))
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  POLL_COUNT=$((POLL_COUNT+1)); sleep 5
  printf '{"operation":"status","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/status-request.json"
  OIDC_TOKEN="$(mint_oidc)"
  set +e
  POLL_METRICS="$(curl --silent --show-error --location --max-time 45 --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" --request POST --header 'Content-Type: application/json' --data-binary "@$OUT/status-request.json" --output "$OUT/status-response.json" --write-out '%{http_code} %{time_total}' "$DEPLOYMENT_URL/api/analyze-audio-tab")"
  POLL_RC=$?
  set -e
  unset OIDC_TOKEN
  if [ "$POLL_RC" -ne 0 ]; then echo "poll=$POLL_COUNT transportError=$POLL_RC sameTokenOnly=true"; continue; fi
  POLL_STATUS="${POLL_METRICS%% *}"
  echo "poll=$POLL_COUNT status=$POLL_STATUS elapsed=$(( $(date +%s)-START_EPOCH ))"
  if [ "$POLL_STATUS" = '202' ]; then continue; fi
  TERMINAL_STATUS="$POLL_STATUS"; break
done
patch_summary "pollCount=$POLL_COUNT" "terminalStatus=${TERMINAL_STATUS:-0}" "asyncTotalSeconds=$(( $(date +%s)-START_EPOCH ))"
if [ -z "$TERMINAL_STATUS" ]; then patch_summary 'terminalState=poll-deadline-exceeded'; echo 'STOP: same-token poll deadline exceeded; no retry.' >&2; exit 5; fi
if [ "$TERMINAL_STATUS" != '200' ]; then patch_summary 'terminalState=failed'; echo 'STOP: authorized job returned terminal failure; no retry.' >&2; exit 6; fi

# Validate terminal structured result and build a scorer/PDF freeze input WITHOUT opening the reference.
python3 - <<'PY'
import json,os
from pathlib import Path
out=Path(os.environ['OUT']); d=json.loads((out/'status-response.json').read_text())
pc=d.get('payloadContract') if isinstance(d.get('payloadContract'),dict) else {}
required=('referenceFree','professionalReferenceNotUsed','referenceRuntimeInputNotUsed','runtimeLabelsNotRequired','v143RuntimeSafetyVerified')
if any(pc.get(k) is not True for k in required): raise SystemExit('terminal payload safety contract failed')
events=d.get('renderEvents')
if not isinstance(events,list) or not events: raise SystemExit('terminal payload has no renderEvents')
j=d.get('analysisJob') if isinstance(d.get('analysisJob'),dict) else {}
if j.get('status')!='completed': raise SystemExit('analysis job not completed')
freeze={
 'schemaVersion':2,'instrument':'rhythm','referenceFree':True,'professionalReferenceUsed':False,
 'referenceRuntimeInputUsed':False,'runtimeLabelsRequired':False,'v143RuntimeSafetyVerified':True,
 'tempoBpm':d.get('tempo') or d.get('tempoBpm'),'timeSignature':d.get('timeSignature'),'tuning':d.get('tuning'),
 'structuredMode':d.get('analysisEngine') or 'v143-reference-free-rhythm','renderEvents':events
}
(out/'freeze-input.json').write_text(json.dumps(freeze,indent=2)+'\n')
bounded={'analysisJobStatus':j.get('status'),'renderEventCount':len(events),'analysisEngine':d.get('analysisEngine'),
 'rhythmCanaryActive':d.get('rhythmCanaryActive'),'generatedTabPresent':bool(str(d.get('generatedTab') or '').strip()),
 'payloadContract':{k:pc.get(k) for k in required}}
(out/'terminal-bounded.json').write_text(json.dumps(bounded,indent=2)+'\n')
PY
patch_summary 'terminalState=completed' 'completed=true'

python3 validation/rhythm_holdout/freeze_rhythm_analysis.py "$OUT/freeze-input.json" "$FREEZE" --source-commit "$GITHUB_SHA"
node validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs "$FREEZE/rhythm-frozen-analysis.json" "$PDF_DIR" lib/createV143RhythmPdf.js
python3 validation/rhythm_holdout/verify_pdf_event_fidelity.py "$FREEZE" "$PDF_DIR/pdf-event-evidence.json"
patch_summary 'pdfE2EPerformed=true' 'pdfEventFidelity=1.0'

# Scorer-only reference access begins only now, after frozen exact-PDF identity.
cp "$REF_SOURCE" "$REF_TMP"
test "$(sha256_file "$REF_TMP")" = "$PROFESSIONAL_REFERENCE_SHA256"
set +e
python3 validation/rhythm_holdout/run_final_holdout_gate.py "$FREEZE" "$REF_TMP" --output-dir "$FINAL_DIR" --minimum 0.99
SCORE_RC=$?
set -e
patch_summary 'professionalScoreCalls=1' "professionalScoreExitCode=$SCORE_RC"

# Capture bounded score evidence, then remove scorer-only reference before ACK/artifact upload.
python3 - <<'PY'
import json,os
from pathlib import Path
out=Path(os.environ['OUT']); final=out/'final-holdout'
score_path=final/'rhythm-professional-holdout-score.json'; gate_path=final/'rhythm-final-holdout-gate.json'
score=json.loads(score_path.read_text()) if score_path.exists() else {}
gate=json.loads(gate_path.read_text()) if gate_path.exists() else {}
bounded={
 'gatedMetrics':score.get('gatedMetrics'),'criticalMismatchCount':score.get('criticalMismatchCount'),
 'pdfEventFidelity':score.get('pdfEventFidelity'),'near100ProfessionalGatePassed':score.get('near100ProfessionalGatePassed'),
 'rhythmComplete':score.get('rhythmComplete'),'finalGatePassed':gate.get('passed'),
 'frozenEventSha256':score.get('frozenEventSha256'),'pdfEventSha256':score.get('pdfEventSha256'),
 'referenceJsonSha256':gate.get('referenceJsonSha256')
}
(out/'professional-score-bounded.json').write_text(json.dumps(bounded,indent=2,sort_keys=True)+'\n')
PY
rm -f "$REF_TMP"

# ACK the exact same job once. This never invokes the worker/model.
printf '{"operation":"ack","jobToken":"%s","transcriptionType":"rhythm"}\n' "$JOB_TOKEN" > "$OUT/ack-request.json"
OIDC_TOKEN="$(mint_oidc)"
set +e
ACK_METRICS="$(curl --silent --show-error --location --max-time 45 --header "x-vercel-trusted-oidc-idp-token: $OIDC_TOKEN" --request POST --header 'Content-Type: application/json' --data-binary "@$OUT/ack-request.json" --output "$OUT/ack-response.json" --write-out '%{http_code} %{time_total}' "$DEPLOYMENT_URL/api/analyze-audio-tab")"
ACK_RC=$?
set -e
unset OIDC_TOKEN
ACK_STATUS="${ACK_METRICS%% *}"; [[ "$ACK_STATUS" =~ ^[0-9]{3}$ ]] || ACK_STATUS=0
export ACK_STATUS ACK_RC
python3 - <<'PY'
import json,os
from pathlib import Path
out=Path(os.environ['OUT'])
try:d=json.loads((out/'ack-response.json').read_text())
except Exception:d={}
j=d.get('analysisJob') if isinstance(d.get('analysisJob'),dict) else {}
p=out/'summary.json'; s=json.loads(p.read_text())
s['ackStatus']=int(os.environ['ACK_STATUS']); s['ackCurlExitCode']=int(os.environ['ACK_RC'])
s['acknowledged']=j.get('status')=='acknowledged'; s['transientResultCleared']=j.get('resultCleared') is True
score=json.loads((out/'professional-score-bounded.json').read_text()) if (out/'professional-score-bounded.json').exists() else {}
s['professionalScore']=score
p.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
if int(os.environ['ACK_STATUS'])!=200 or not s['acknowledged'] or not s['transientResultCleared']:
 raise SystemExit('ACK/cleanup failed; do not retry the model start')
PY

# Remove raw/token/full event-bearing JSON. Keep PDFs and bounded aggregate evidence only.
rm -f "$OUT/preflight-response.json" "$OUT/start-request.json" "$OUT/start-response.json" "$OUT/status-request.json" "$OUT/status-response.json" "$OUT/ack-request.json" "$OUT/ack-response.json" "$OUT/job-token.txt" "$OUT/freeze-input.json"
rm -f "$FREEZE/rhythm-frozen-analysis.json" "$PDF_DIR/pdf-event-evidence.json"
rm -rf "$FINAL_DIR"

if [ "$SCORE_RC" -ne 0 ]; then
  echo 'The single professional score completed but did not pass the 0.99 final gate. The live run is still consumed; no retry is authorized.' >&2
  exit "$SCORE_RC"
fi

echo 'V143 final Rhythm one-shot completed: one live start, one professional score, exact same-result PDF, ACK cleanup.'
