#!/usr/bin/env bash
set -euo pipefail

# Run one full Songsterr Fresh model-path measurement inside the dedicated
# Codespaces workbench. This is explicitly NOT Policy C authority evidence.
# Hosted/container decode differences are measured, never promoted to authority.

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

WORKBENCH_ROOT="${SONGSTERR_FRESH_WORKBENCH_ROOT:-/workspaces/.songsterr-fresh-workbench}"
VENV="${WORKBENCH_ROOT}/venv"
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SOURCE_COMMIT="$(git rev-parse HEAD)"
RUN_DIR="${WORKBENCH_ROOT}/runs/${RUN_STAMP}-${SOURCE_COMMIT:0:12}"
PYTHON="${VENV}/bin/python"
EXPECTED_SOURCE_BLOB='4dd709e3fa177b4daeed71ca97f0199757729d4b'
EXPECTED_SEPARATION_SHA='e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a'
EXPECTED_STRUCTURE_SIGNATURE='fnv1a32:2f493225'

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-${WORKBENCH_ROOT}/pip-cache}"
export HF_HOME="${HF_HOME:-${WORKBENCH_ROOT}/huggingface}"
export TORCH_HOME="${TORCH_HOME:-${WORKBENCH_ROOT}/torch}"
export PATH="${VENV}/bin:${PATH}"

if [[ ! -x "$PYTHON" ]]; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:VENV_MISSING:$VENV" >&2
  echo "Run: bash .devcontainer/songsterr-fresh-workbench/setup.sh" >&2
  exit 2
fi

mkdir -p "$RUN_DIR"
START_TOTAL="$(date +%s)"
echo "WORKBENCH_STAGE:probe runDir=$RUN_DIR"

"$PYTHON" scripts/songsterr-fresh/verify_pinned_compute_authority.py \
  --validate-manifest \
  --probe-output "$RUN_DIR/workbench-probe.json" \
  > "$RUN_DIR/workbench-probe.stdout.json"

# Fixed authorized fixture only. This does not authorize any archived pipeline.
echo "WORKBENCH_STAGE:fixture"
curl --fail --location --silent --show-error --retry 3 \
  'https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/main/public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a' \
  --output "$RUN_DIR/source.m4a"
SOURCE_BLOB="$(git hash-object "$RUN_DIR/source.m4a")"
if [[ "$SOURCE_BLOB" != "$EXPECTED_SOURCE_BLOB" ]]; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:SOURCE_FIXTURE_IDENTITY_CHANGED:expected=$EXPECTED_SOURCE_BLOB:actual=$SOURCE_BLOB" >&2
  exit 2
fi

# Decode-byte identity is authority provenance, not a workbench correctness gate.
# The exact source blob remains mandatory. Codespaces FFmpeg variation is captured
# explicitly and keeps this run non-authoritative.
echo "WORKBENCH_STAGE:decode"
ffmpeg -hide_banner -loglevel error -y -i "$RUN_DIR/source.m4a" -ac 1 -ar 22050 "$RUN_DIR/analysis.wav"
ffmpeg -hide_banner -loglevel error -y -i "$RUN_DIR/source.m4a" -ac 2 -ar 44100 "$RUN_DIR/separation.wav"
ANALYSIS_SHA="$(sha256sum "$RUN_DIR/analysis.wav" | awk '{print $1}')"
SEPARATION_SHA="$(sha256sum "$RUN_DIR/separation.wav" | awk '{print $1}')"
if [[ "$SEPARATION_SHA" != "$EXPECTED_SEPARATION_SHA" ]]; then
  echo "WORKBENCH_DIAGNOSTIC:SEPARATION_WAV_DIFFERS_FROM_AUTHORITY_BASELINE:expected=$EXPECTED_SEPARATION_SHA:actual=$SEPARATION_SHA"
fi

START_STRUCTURE="$(date +%s)"
echo "WORKBENCH_STAGE:structure"
"$PYTHON" scripts/songsterr-fresh/analyze_full_mixture_structure.py \
  --input "$RUN_DIR/analysis.wav" \
  --output "$RUN_DIR/raw-structure-analysis.json" \
  --audio-source 'public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a@main#4dd709e3fa177b4daeed71ca97f0199757729d4b'
node scripts/songsterr-fresh/build_structure_map.mjs "$RUN_DIR/raw-structure-analysis.json" "$RUN_DIR/adapted-structure-map.json"
node scripts/songsterr-fresh/build_note_evidence_context.mjs "$RUN_DIR/adapted-structure-map.json" "$RUN_DIR/note-evidence-context.json"
RUN_DIR="$RUN_DIR" EXPECTED_STRUCTURE_SIGNATURE="$EXPECTED_STRUCTURE_SIGNATURE" node --input-type=module - <<'NODE'
import { readFile, writeFile } from 'node:fs/promises';
const context = JSON.parse(await readFile(`${process.env.RUN_DIR}/note-evidence-context.json`, 'utf8'));
if (context?.referenceBlind !== true) throw new Error('WORKBENCH_REFERENCE_BLIND_GUARD_FAILED');
const actual = context?.structureIdentity?.signature ?? null;
const expected = process.env.EXPECTED_STRUCTURE_SIGNATURE;
const diagnostic = {
  expectedStructureSignature: expected,
  actualStructureSignature: actual,
  structureIdentityMatchesAuthorityBaseline: actual === expected,
  referenceBlind: context?.referenceBlind === true,
  structureFrozen: context?.structureFrozen === true,
  structureAccepted: context?.structureAcceptance?.accepted === true,
  authorityEligible: false,
};
await writeFile(`${process.env.RUN_DIR}/structure-diagnostic.json`, `${JSON.stringify(diagnostic, null, 2)}\n`, 'utf8');
if (actual !== expected) console.log(`WORKBENCH_DIAGNOSTIC:STRUCTURE_IDENTITY_DIFFERS_FROM_AUTHORITY_BASELINE:expected=${expected}:actual=${actual}`);
NODE
END_STRUCTURE="$(date +%s)"

START_DEMUCS="$(date +%s)"
echo "WORKBENCH_STAGE:demucs"
/usr/bin/time -v -o "$RUN_DIR/demucs-resource.txt" \
  "$PYTHON" -m demucs -n htdemucs_6s --device cpu --shifts 0 --overlap 0.25 --segment 7 \
  -o "$RUN_DIR/separated" "$RUN_DIR/separation.wav"
END_DEMUCS="$(date +%s)"

STEM="$RUN_DIR/separated/htdemucs_6s/separation/guitar.wav"
if [[ ! -s "$STEM" ]]; then
  echo "SONGSTERR_FRESH_WORKBENCH_ERROR:DEMUCS_GUITAR_STEM_MISSING" >&2
  exit 2
fi
"$PYTHON" scripts/songsterr-fresh/verify_demucs_model_asset.py --output "$RUN_DIR/demucs-model-asset.json"
RUN_DIR="$RUN_DIR" "$PYTHON" - <<'PY'
import json, os
base = os.environ['RUN_DIR']
data = json.load(open(f'{base}/demucs-model-asset.json', encoding='utf-8'))
if data.get('assetSha256') != 'd2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411':
    raise SystemExit('DEMUCS_MODEL_ASSET_CHANGED')
if data.get('legacyFallback', {}).get('primary') is not False:
    raise SystemExit('DEMUCS_LEGACY_FALLBACK_MUST_NOT_BE_PRIMARY')
PY

STEM_SHA="$(sha256sum "$STEM" | awk '{print $1}')"
START_BP="$(date +%s)"
echo "WORKBENCH_STAGE:basic-pitch"
/usr/bin/time -v -o "$RUN_DIR/basic-pitch-resource.txt" \
  "$PYTHON" scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py \
    --input "$STEM" \
    --output "$RUN_DIR/basic-pitch-guitar-notes.json" \
    --activation-output "$RUN_DIR/basic-pitch-note-activations.json" \
    --decision-surface-output "$RUN_DIR/basic-pitch-decision-surface.json" \
    --audio-source 'public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a@main#4dd709e3fa177b4daeed71ca97f0199757729d4b' \
    --separation-source "demucs==4.1.0/htdemucs_6s/shifts=0/overlap=0.25/segment=7:guitar@sha256:${STEM_SHA}"
END_BP="$(date +%s)"

echo "WORKBENCH_STAGE:evidence"
node scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs \
  "$RUN_DIR/note-evidence-context.json" \
  "$RUN_DIR/basic-pitch-guitar-notes.json" \
  "$RUN_DIR/evidence.json"

END_TOTAL="$(date +%s)"

RUN_DIR="$RUN_DIR" \
SOURCE_COMMIT="$SOURCE_COMMIT" \
SOURCE_BLOB="$SOURCE_BLOB" ANALYSIS_SHA="$ANALYSIS_SHA" SEPARATION_SHA="$SEPARATION_SHA" \
EXPECTED_SOURCE_BLOB="$EXPECTED_SOURCE_BLOB" EXPECTED_SEPARATION_SHA="$EXPECTED_SEPARATION_SHA" \
START_TOTAL="$START_TOTAL" END_TOTAL="$END_TOTAL" \
START_STRUCTURE="$START_STRUCTURE" END_STRUCTURE="$END_STRUCTURE" \
START_DEMUCS="$START_DEMUCS" END_DEMUCS="$END_DEMUCS" \
START_BP="$START_BP" END_BP="$END_BP" \
"$PYTHON" - <<'PY'
import hashlib
import json
import os
from pathlib import Path

base = Path(os.environ['RUN_DIR'])

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def seconds(a, b):
    return int(os.environ[b]) - int(os.environ[a])

def time_value(path, prefix):
    for line in Path(path).read_text(encoding='utf-8', errors='replace').splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped.split(':', 1)[1].strip()
    return None

probe = json.loads((base / 'workbench-probe.json').read_text(encoding='utf-8'))
structure = json.loads((base / 'structure-diagnostic.json').read_text(encoding='utf-8'))
summary = {
    'contract': 'songsterr-fresh-codespaces-workbench-measurement-v2',
    'version': 2,
    'sourceCommit': os.environ['SOURCE_COMMIT'],
    'workbenchOnly': True,
    'authorityEligible': False,
    'probeAloneEnrollsAuthority': False,
    'modelValidationComplete': False,
    'mayAdvanceDelivery': False,
    'durationAuthorityChanged': False,
    'customerEligibleEvents': 0,
    'workbenchFingerprintSha256': probe['fingerprintSha256'],
    'hardware': {
        'logicalCpuCount': probe['fingerprint']['hardware']['logicalCpuCount'],
        'modelName': probe['fingerprint']['hardware']['modelName'],
        'vendorId': probe['fingerprint']['hardware']['vendorId'],
    },
    'decodeDiagnostics': {
        'sourceBlob': os.environ['SOURCE_BLOB'],
        'expectedSourceBlob': os.environ['EXPECTED_SOURCE_BLOB'],
        'sourceBlobMatchesAuthorizedFixture': os.environ['SOURCE_BLOB'] == os.environ['EXPECTED_SOURCE_BLOB'],
        'analysisWavSha256': os.environ['ANALYSIS_SHA'],
        'separationWavSha256': os.environ['SEPARATION_SHA'],
        'authorityBaselineSeparationWavSha256': os.environ['EXPECTED_SEPARATION_SHA'],
        'separationWavMatchesAuthorityBaseline': os.environ['SEPARATION_SHA'] == os.environ['EXPECTED_SEPARATION_SHA'],
        'decodeByteIdentityUsedForAuthority': False,
    },
    'structureDiagnostics': structure,
    'timingsSeconds': {
        'structure': seconds('START_STRUCTURE', 'END_STRUCTURE'),
        'demucs': seconds('START_DEMUCS', 'END_DEMUCS'),
        'basicPitch': seconds('START_BP', 'END_BP'),
        'total': seconds('START_TOTAL', 'END_TOTAL'),
    },
    'resources': {
        'demucsMaximumResidentSetKb': time_value(base / 'demucs-resource.txt', 'Maximum resident set size (kbytes)'),
        'basicPitchMaximumResidentSetKb': time_value(base / 'basic-pitch-resource.txt', 'Maximum resident set size (kbytes)'),
    },
    'identities': {
        'guitarStemSha256': sha256(base / 'separated/htdemucs_6s/separation/guitar.wav'),
        'noteInferenceSha256': sha256(base / 'basic-pitch-guitar-notes.json'),
        'activationBundleSha256': sha256(base / 'basic-pitch-note-activations.json'),
        'decisionSurfaceSha256': sha256(base / 'basic-pitch-decision-surface.json'),
        'canonicalEvidenceSha256': sha256(base / 'evidence.json'),
    },
}
(base / 'workbench-measurement-summary.json').write_text(
    json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8'
)
print(json.dumps(summary, indent=2, sort_keys=True))
PY

cat <<EOF
SONGSTERR_FRESH_WORKBENCH_MEASUREMENT_COMPLETE
runDir=$RUN_DIR
summary=$RUN_DIR/workbench-measurement-summary.json
authorityEligible=false
modelValidationComplete=false
customerEligibleEvents=0

IMPORTANT: stop the Codespace when finished so compute billing stops.
EOF
