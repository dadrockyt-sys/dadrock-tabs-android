# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless the user explicitly asks.
- The exact fixture name containing `gomyway` authorizes that audio file only.
- The user authorized the fresh reference-blind source-separation/model path, including GPU if useful, while preserving fail-closed contracts.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free.
- Model/DSP execution stays under `scripts/songsterr-fresh/`.
- Frozen structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop detected MIDI/event identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## EXACT AUTHORIZED FIXTURE

On `main`:
`public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

Git blob SHA:
`4dd709e3fa177b4daeed71ca97f0199757729d4b`

Duration:
~210.674648526 s

Canaries fetch the raw file from `main` and verify `git hash-object`.

## FROZEN STRUCTURE

Structure identity:
`fnv1a32:2f493225`
canonicalLength 19653

Accepted facts:
- 4/4
- straight feel
- pickup / first downbeat ~0.65016 s
- 115 measures
- 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- accepted true

## GUARDED CPU BASELINE

Analyzer:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Contract:
`songsterr-fresh-cpu-note-evidence-v4`

Baseline:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous pitch selections
- 353 ambiguous
- MIDI 40 in 97/139 selections
- role relevance unresolved
- polyphony unresolved
- customer eligible 0

Latest CPU regression:
- run `34309259214`
- job `102332311684`
- artifact `10087798684`
- digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`
- 97/97 tests
- duration 103 resolved / 36 unresolved

## MODEL PATH

Architecture:
1. frozen full-mixture structure
2. Demucs 4.1.0 `htdemucs_6s` guitar isolation
3. Basic Pitch 0.4.0 polyphonic pitch/onset inference
4. decoded Basic Pitch note-off remains diagnostic only
5. model pitch evidence crosses duration-free
6. release stage is sole active duration authority
7. model adaptation requires explicit authorization
8. `MODEL_EVIDENCE_VALIDATION_PENDING` independently blocks customer delivery

Historical first model canary used Demucs `--shifts 1`; its exact 1,128-note output is historical only, not a reproducibility baseline.

## ACTIVE V2 DURATION AUTHORITY — UNCHANGED

Script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract:
`songsterr-fresh-cpu-spectral-release-evidence-v2`

Hard rules:
- input must be duration-free
- non-null upstream `durationSeconds` / `sourceEnd` rejected
- model/GPU upstream denied unless explicitly authorized
- decoded Basic Pitch note-off never becomes active duration
- generic next onset never becomes duration
- same-pitch reattack is a censor/search boundary only
- unresolved remains unresolved when no observed release is found

Fixed v2 parameters:
- HOP_LENGTH 512
- SUSTAINED_LOW_FRAMES 5
- MIN_DURATION_SECONDS 0.07
- MAX_SEARCH_SECONDS 4.0
- MIN_ONSET_ABOVE_FLOOR_DB 12
- DROP_FROM_ONSET_DB 18
- MIN_FLOOR_MARGIN_DB 6

Resolved v2 method:
`selected-pitch-sustained-spectral-decay`

Do not mutate this audited v2 implementation while v3 is being evaluated.

## DEMUCS EXECUTED ASSET — VERIFIED

Verifier:
`scripts/songsterr-fresh/verify_demucs_model_asset.py`

Contract:
`songsterr-fresh-demucs-model-asset-v2`

For `htdemucs_6s`:
- primary loader: Hugging Face
- repo: `adefossez/HTDemucs-6s`
- pinned repo snapshot: `3c5ee475be622df764938de97e4281a7b07ffa58`
- model-file upload revision: `053e1404489b3dc58bf718224fac4b7316de8c93`
- bag model signature: `5c90dfd2`
- executed asset: `5c90dfd2.safetensors`
- asset SHA256: `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- Xet hash: `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`
- model class: `demucs.htdemucs.HTDemucs`
- legacy `.th` fallback is informational, not primary

## DEMUCS REPRODUCIBILITY — GREEN

Old `--shifts 1` cross-run drift was traced to Demucs' deliberate random shift augmentation.

Current acceptance:
- `--shifts 0`
- pinned runtime/model asset identity
- same-job same-runtime A/B exact SHA + byte `cmp`
- cross-environment stem SHA is diagnostic only
- semantic note/release stability evaluated separately

Green run:
- run `34313902753`
- job `102345983922`
- head `88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`
- pass A/B stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- identicalStemSha256 true
- identicalStemBytes true
- decoded separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- artifact `10089522605`
- digest `sha256:a49e36478b541907b377fb94e9a264003eb69ff1bf20dd2d2904e0fc2f37fb43`

## AUTHORITATIVE DETERMINISTIC V2 MODEL CANARY — GREEN

Workflow:
`.github/workflows/songsterr-fresh-model-guitar-polyphonic-canary.yml`

Deterministic conversion commit:
`760e716c0cab0a1ba620eaf4ef037798f033c548`

Green run:
- run `34314845733`
- job `102348798520`
- artifact `10089820501`
- digest `sha256:f1054d9721b0bab8b6e13aee4b3015f9a93af2ec379317b236655d8cf2184871`
- 97/97 tests

Exact run facts:
- runtime-scoped stem SHA `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`
- 1,139 Basic Pitch notes
- 1,032 start clusters
- 96 polyphonic clusters
- max cluster 4
- v2 attempted 1,139
- v2 resolved 577
- v2 unresolved 562
- 537 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- 7 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- 18 `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`
- same-pitch censor count 967
- exact MIDI preserved 1,139/1,139
- pitch-resolved 1,139
- role-accepted 1,139
- customer eligible 0
- evaluator failures include `MODEL_EVIDENCE_VALIDATION_PENDING` and `DURATION_EVIDENCE_INCOMPLETE`
- deliveryReady false

## CROSS-RUNTIME SEMANTIC STABILITY — STRONG DESCRIPTIVE EVIDENCE

Compared the deterministic activation run and authoritative deterministic model run under the existing 10 ms simultaneity tolerance, without defining a new tuning threshold.

Observed:
- both had 1,139 notes
- 1,137/1,139 events matched by MIDI within 10 ms (~99.82%)
- all matched start deltas were exactly 0.0 s
- 1,136/1,137 matched events preserved the same resolved/unresolved state
- 576 events were duration-resolved in both
- all 576 shared resolved durations were exactly equal
- both total release splits were 577 resolved / 562 unresolved with the same unresolved reason totals

Conclusion: pinned `--shifts 0` model evidence is semantically stable across the observed runner variation even when Demucs WAV bytes differ. Do not canonize one cross-environment stem SHA.

## FIXED ACTIVATION + SPECTRAL RULE

Shared helper:
`scripts/songsterr-fresh/activation_valley_release_evidence.py`

Contract:
`songsterr-fresh-activation-spectral-valley-rule-v1`

Fixed rule, no optimizer/sweep:
- Basic Pitch per-pitch activation <= 0.20
- sustained 3 Basic Pitch frames
- activation drop >= 0.15 from onset-window peak
- minimum observed span >= 0.07 s
- maximum search 4.0 s
- search stops before next same-pitch reattack
- independent selected-pitch CQT spectral drop >= 6 dB over 3 frames

The observed valley timestamp is the only possible activation-based release candidate. The reattack timestamp itself is never duration.

## SAME-INFERENCE ACTIVATION SIDECAR — GREEN

Goal: capture raw Basic Pitch `model_output["note"]` activations from the same `predict()` call that emits decoded notes, so the probe/release path does not rerun Basic Pitch.

Helper:
`scripts/songsterr-fresh/basic_pitch_activation_evidence.py`

Contracts:
- `songsterr-fresh-basic-pitch-note-activation-evidence-v1`
- `songsterr-fresh-basic-pitch-note-identity-v1`
- `songsterr-fresh-basic-pitch-inference-bundle-v1`

Current sidecar representation is JSON with exact zlib+base64 encoded arrays:
- playable MIDI 40–88 activation slice as little-endian float32
- exact frame-time axis as little-endian float64
- raw array SHA256s
- note identity hash over sorted `(startSeconds, midi, confidence)`
- bundle hash binding note identity + activation matrix + frame times + MIDI range/shape

Hard sidecar guards:
- same inference as decoded notes true
- decoded model ends excluded
- decoded model ends used as duration false
- writes `sourceEnd` false
- writes `durationSeconds` false
- active duration authority false
- pitch identity changes false

Transcription:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`
- exactly one `predict()` call
- optional `--activation-output`
- decoded note-off remains diagnostic only
- note JSON records note/bundle identities

Evidence propagation:
`scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs`
- validates and propagates the note/bundle identities
- pitch evidence remains duration-free

Probe:
`scripts/songsterr-fresh/probe_model_activation_valleys.py`
contract `songsterr-fresh-model-activation-valley-probe-v2`
- sidecar mode makes no second Basic Pitch call
- exact identity/bundle verification
- unchanged fixed rule
- descriptiveOnly true
- changesDuration false

### Green deterministic same-inference probe

Run:
`34315619967`
job:
`102351096162`
head:
`4af488ececbe756fc168bb22578117ddf14d62d4`
artifact:
`10090106400`
digest:
`sha256:73fb818710903358399655d0c77cde216e2bc3106d7db57b6e00ac04e46cbdf6`

Exact evidence:
- stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- 1,138 notes
- 1,031 start clusters
- 96 polyphonic clusters
- max cluster 4
- Basic Pitch predict invocation count 1
- activation frame count 18,118
- MIDI bins 49
- note identity SHA `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`
- activation matrix SHA `b002673dd6ab0ec5bb31157db33659676d7c694eeb1d89cbb96f6bff02201dd0`
- frame-time SHA `7cc95d91fc64040cb49622f993ff94c8e2018f99fa972a4b2577f4e7b0f6b997`
- inference bundle SHA `5e1aa1f76bfb2b3dae77f6aeb6bf6dd1fc5f84e102292dd12a5432683b330159`
- v2 resolved 577 / unresolved 561
- 536 reattack-censored unresolved
- fixed-rule valleys 84/536 = 15.6716%
- rejection counts: activation drop 5, spectral corroboration 76, sustained activation 371
- valley span mean ~0.299432 s
- median ~0.290249 s
- p90 ~0.430853 s
- max ~1.069402 s
- probe model invocation false
- 97/97 tests

The 84-candidate count and span distribution agree with the earlier second-inference deterministic probe closely enough to support same-inference parity without threshold tuning.

### Green authoritative capture-only validation

Run:
`34315700274`
job:
`102351339722`
head:
`e68769012344ab66ccc870e2bad4fce0d91d27c5`
artifact:
`10090124225`
digest:
`sha256:f14447af27cc58290da07553e5bc66856813987b878a9366c7f02891d0281466`

Exact evidence:
- stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- 1,138 notes
- predict invocation count 1
- same note identity SHA `e85323e5...cbe77`
- same bundle SHA `5e1aa1f7...30159`
- v2 active release remained unchanged and received no activation sidecar
- v2 resolved 577 / unresolved 561
- 536 reattack-censored unresolved
- customer eligible 0
- fail-closed evaluator preserved
- 97/97 tests

This completes capture-only validation. Same-inference activation evidence is now proven as an optional evidence source, not yet an authoritative customer-duration source.

## V3 RELEASE FALLBACK PROTOTYPE — ACTIVE CANARY

v2 remains untouched.

New prototype:
`scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`

Commit:
`df41605d0e232fc3ea3a5aaf0ea591cbd98d2a35`

Contract:
`songsterr-fresh-spectral-activation-release-evidence-v3`

Design:
1. require duration-free evidence
2. preserve explicit model-upstream authorization
3. cryptographically verify the same-inference activation sidecar
4. run the existing v2 spectral logic first using v2 constants/functions
5. never change a v2-resolved event
6. activation fallback is eligible only for exact v2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
7. apply the unchanged fixed activation + CQT rule
8. release is the observed valley timestamp only
9. require release < next same-pitch reattack
10. generic next onset never becomes duration
11. decoded Basic Pitch note-off never becomes duration
12. same-pitch reattack itself never becomes duration
13. no new duration-confidence heuristic; activation fallback emits `durationConfidence: null`
14. exact MIDI/start/event identity is preserved
15. failed fallback keeps the original v2 unresolved reason
16. provenance distinguishes v2 spectral release from activation+spectral fallback
17. model validation remains false

Dedicated canary:
`.github/workflows/songsterr-fresh-model-release-v3-canary.yml`

Workflow commit:
`39f22fc49755f421aeac8d4b7caa7af2fdca0af2`

Active run:
`34316898152`
job:
`102354896399`

Canary acceptance is intentionally strict:
- exact fixture/frozen structure
- deterministic Demucs `--shifts 0` + executed asset proof
- one Basic Pitch call + same-inference sidecar
- reject unauthorized model use
- reject tampered sidecar identity
- run untouched v2 baseline and v3 from the same duration-free evidence
- prove every v2-resolved event is byte-for-byte/numerically unchanged in v3
- prove every v3 fallback was exact v2 reattack-censored unresolved
- prove every fallback end is the observed valley and strictly before reattack
- prove no decoded-end/next-onset/reattack duration use
- run the descriptive probe on the same evidence/sidecar and require exact onset-ID parity with v3 fallback promotions
- do not hardcode an expected fallback count
- adapt v3 evidence through the deterministic pipeline
- preserve `MODEL_EVIDENCE_VALIDATION_PENDING`
- preserve `DURATION_EVIDENCE_INCOMPLETE`
- customer eligible 0
- deliveryReady false
- 97/97 deterministic tests

Do not promote v3 into the authoritative model workflow until this canary is green and its artifact is reviewed.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

Basic Pitch output is not ground truth.
No reference scorer.
No archived logic.
No decoded Basic Pitch end as duration.
No generic next-onset duration.
No same-pitch reattack default duration.

## NEXT ENGINEERING STEPS

1. Finish v3 run `34316898152`.
2. If red, inspect the exact failed guard and fix the prototype/canary without weakening the acceptance rule.
3. If green, record exact v2/v3/fallback counts, identity hashes, artifact digest, and rejection distribution here.
4. Re-run v3 on at least one additional pinned `--shifts 0` runner instance and compare semantic fallback stability; do not require cross-environment stem-byte equality.
5. Keep v2 authoritative until v3 is separately accepted.
6. Do not clear `MODEL_EVIDENCE_VALIDATION_PENDING` merely because duration coverage improves.
7. Before any customer exposure, independently validate model pitch evidence and duration quality while preserving exact event identity and fail-closed delivery.
