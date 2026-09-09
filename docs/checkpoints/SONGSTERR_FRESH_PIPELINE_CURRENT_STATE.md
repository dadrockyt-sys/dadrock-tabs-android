# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or historical percentages unless the user explicitly asks.

## PRODUCT / ARCHITECTURE

Preserve `/ai-tab`:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh foundational order:

**full-mixture audio → frozen timing/measure map → role-isolated structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

Non-negotiables:
- work only on `songsterr-fresh-pipeline-v1`;
- no `main` / Production changes;
- frozen structure cannot be rewritten downstream;
- never silently change/drop detected MIDI/event identity;
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free;
- model/DSP execution stays under `scripts/songsterr-fresh/`;
- archived V143/Gomyway code, reference tabs, reference-based correction, professional/reference scorer use, training/fine-tuning, and broad optimizer sweeps remain unauthorized.

The user explicitly authorized the fresh reference-blind model/source-separation path, including GPU if useful. Model execution authorization does not imply musical/customer acceptance.

## EXACT AUTHORIZED FIXTURE

`public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a` on `main`

Git blob SHA:
`4dd709e3fa177b4daeed71ca97f0199757729d4b`

Duration ~210.674648526 s.

## FROZEN STRUCTURE

Structure identity:
`fnv1a32:2f493225`
canonicalLength 19653

Key facts:
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

Pitch analyzer:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Contract:
`songsterr-fresh-cpu-note-evidence-v4`

Exact baseline:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous pitch selections
- 353 ambiguous
- MIDI 40 in 97/139 local selections
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

## MODEL PATH — VALIDATION STILL PENDING

Architecture:
1. frozen full-mixture structure;
2. Demucs 4.1.0 `htdemucs_6s` guitar isolation;
3. Basic Pitch 0.4.0 polyphonic pitch/onset inference;
4. Basic Pitch decoded note-off remains diagnostic only;
5. model pitch evidence crosses duration-free;
6. dedicated release stage remains sole active duration authority;
7. explicit model-upstream authorization required;
8. `MODEL_EVIDENCE_VALIDATION_PENDING` blocks customer eligibility.

Historical first green model canary:
- run `34309319200`, job `102332488694`
- artifact `10087877760`
- digest `sha256:c051dfe5166a0d4fb019cf50aaae7afa97c7f477225657d9cc31b311c612ca31`
- 97/97 tests
- 1,128 Basic Pitch notes
- 591 duration-resolved / 537 unresolved
- 517 reattack-censored unresolved
- customer eligible 0

That historical run used Demucs `--shifts 1`; its exact stem/note count is not a reproducibility baseline.

## SINGLE DURATION AUTHORITY

Active script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Active contract:
`songsterr-fresh-cpu-spectral-release-evidence-v2`

Hard rules:
- input must be duration-free;
- upstream non-null `durationSeconds` / `sourceEnd` rejected;
- model/GPU upstream denied unless explicitly authorized;
- decoded Basic Pitch note-off never becomes active duration;
- next generic onset never becomes duration;
- same-pitch reattack is a censor/search boundary, not an automatic duration.

Current fixed v2 parameters:
- HOP_LENGTH 512
- SUSTAINED_LOW_FRAMES 5
- MIN_DURATION_SECONDS 0.07
- MAX_SEARCH_SECONDS 4.0
- MIN_ONSET_ABOVE_FLOOR_DB 12
- DROP_FROM_ONSET_DB 18
- MIN_FLOOR_MARGIN_DB 6

Do not weaken these rules.

## DEMUCS 4.1 PRIMARY LOADER / EXECUTED ASSET — VERIFIED

For `htdemucs_6s`:
- HF namespace `adefossez`
- repo `adefossez/HTDemucs-6s`
- pinned repo snapshot `3c5ee475be622df764938de97e4281a7b07ffa58`
- model-file upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- bag `htdemucs_6s.yaml`
- bag models `['5c90dfd2']`
- executed model asset `5c90dfd2.safetensors`
- asset SHA256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- Xet hash `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`
- model class `demucs.htdemucs.HTDemucs`

Verifier:
`scripts/songsterr-fresh/verify_demucs_model_asset.py`
contract `songsterr-fresh-demucs-model-asset-v2`
latest verifier commit `88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`.

Legacy `.th` fallback is informational only.

## DEMUCS REPRODUCIBILITY — GREEN SAME-RUNTIME PROOF

`--shifts 0` removes intentional random shift augmentation, but cross-environment audio-byte equality is not required.

Acceptance contract:
1. exact source fixture and decoded input hashes;
2. pinned package/model/runtime identities;
3. `--shifts 0`;
4. exact executed HF asset SHA;
5. same-job / same-runtime pass A and B identical by SHA and byte `cmp`;
6. cross-environment stem SHA diagnostic only;
7. semantic note/evidence stability evaluated separately.

Final green reproducibility canary:
- run `34313902753`
- job `102345983922`
- head `88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`
- conclusion success
- Ubuntu 24.04.4 image `20260831.293.1`
- CPU `AMD EPYC 7763 64-Core Processor`
- Python 3.10.21
- decoded separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- pass A stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass B same SHA
- identicalStemSha256 true
- identicalStemBytes true
- artifact `10089522605`
- digest `sha256:a49e36478b541907b377fb94e9a264003eb69ff1bf20dd2d2904e0fc2f37fb43`

## DETERMINISTIC ACTIVATION PROBE — LAST GREEN SECOND-INFERENCE BASELINE

Before same-inference capture was implemented, final green descriptive run:
- run `34313902747`
- job `102345984013`
- head `88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`
- artifact `10089483424`
- digest `sha256:7d20bb6b18423c8dac44820391161eafa4de2e724465488f99598edf876b8ef5`
- 97/97 tests
- stem SHA `0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12`
- 1,139 notes
- 1,031 start clusters
- 97 polyphonic clusters
- max cluster 4
- MIDI 40 count 34
- v2 duration: 577 resolved / 562 unresolved
- 537 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- fixed activation probe: 84/537 = 15.64%

Fixed descriptive rule remains unchanged:
- Basic Pitch per-pitch activation <= 0.20
- sustained 3 BP frames
- activation drop >= 0.15
- observed span >= 0.07 s
- search stops at next same-pitch reattack or 4.0 s
- independent CQT corroboration >= 6 dB over 3 frames
- no threshold sweep
- no duration/sourceEnd writes
- no decoded model ends
- no next-onset duration
- no pitch mutation

## AUTHORITATIVE `--shifts 0` MODEL CANARY — GREEN BASELINE

The authoritative model workflow was modernized at commit:
`760e716c0cab0a1ba620eaf4ef037798f033c548`

It now pins runtime/model dependencies, uses Demucs `--shifts 0`, verifies the exact executed safetensors asset, records runtime provenance, keeps Basic Pitch pitch evidence duration-free, uses unchanged v2 release authority, preserves explicit model-adaptation authorization, and remains fail-closed for delivery.

Green run:
- run **`34314845733`**
- job **`102348798520`**
- head `760e716c0cab0a1ba620eaf4ef037798f033c548`
- conclusion success
- artifact **`10089820501`**
- artifact digest **`sha256:f1054d9721b0bab8b6e13aee4b3015f9a93af2ec379317b236655d8cf2184871`**
- artifact size 473,546 bytes
- 97/97 deterministic tests pass

Runtime:
- Ubuntu 24.04.4 / image `20260831.293.1`
- Python 3.10.21
- CPU `AMD EPYC 9V74 80-Core Processor`
- FFmpeg 6.1.1-3ubuntu5
- analysis WAV SHA `824af60bbc3d701c8c1f085194be2acf59f0ac5d0ae4133e763eadb9793ca873`
- separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- exact HF asset SHA verified

Runtime-scoped stem SHA:
`5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`

Basic Pitch / pitch evidence:
- **1,139 notes**
- 1,032 start clusters
- 96 polyphonic start clusters
- max cluster size 4
- MIDI 40 count 34
- role resolved true
- polyphony resolved true
- duration none before release

v2 release result:
- attempted 1,139
- resolved **577**
- unresolved **562**
- resolution rate 50.658%
- reattack unresolved **537**
- no clear spectral release 7
- insufficient onset/floor contrast 18
- same-pitch reattack censor count 967
- mean resolved duration ~0.460473 s
- median ~0.339367 s
- max ~3.652337 s
- mean duration confidence ~0.915533

Evaluator / delivery:
- pitch-resolved 1,139
- role-accepted 1,139
- complete-tab/customer eligible 0
- failures exactly include `MODEL_EVIDENCE_VALIDATION_PENDING` and `DURATION_EVIDENCE_INCOMPLETE`
- deliveryReady false
- exact MIDI preserved 1,139/1,139 downstream

## CROSS-RUNTIME SEMANTIC STABILITY — STRONG DESCRIPTIVE EVIDENCE

Compared the final green deterministic activation run (`34313902747`) against the green authoritative run (`34314845733`). This comparison is descriptive only; it does not tune thresholds or define musical ground truth.

Despite different Demucs stem bytes:
- activation-run stem `0d9339df...`
- authoritative stem `5b3e7c6f...`

Basic Pitch outputs are highly stable:
- note count: **1,139 vs 1,139**
- MIDI 40: 34 vs 34
- max start cluster: 4 vs 4
- start clusters: 1,031 vs 1,032
- polyphonic clusters: 97 vs 96
- normalized MIDI-histogram total-variation distance ~**0.000878**
- only histogram changes: MIDI 55 count 35→34 and MIDI 64 count 223→224

One-to-one same-MIDI onset matching, minimizing absolute start difference per MIDI:
- 1,138 same-MIDI matches
- 1 unmatched note from each run
- **1,137/1,138 matched notes within 1 ms**
- one remaining same-MIDI match at ~81.27 ms
- for the 1,137 <=50 ms matches, confidence delta median ~1.39e-5 and p95 ~5.53e-4

Release semantics are even more stable:
- both runs: 577 resolved / 562 unresolved
- both runs: 537 reattack-censored unresolved, 7 no-clear-spectral, 18 insufficient onset/floor
- both runs: 967 same-pitch reattack censors
- max resolved duration identical ~3.652337 s

Conclusion: the available pinned `--shifts 0` environments show strong semantic note/release stability even though Demucs WAV bytes differ across runner CPU environments. Do not promote stem SHA to a universal canonical identity.

## SAME-INFERENCE ACTIVATION SIDECAR — CAPTURE-ONLY IMPLEMENTATION IN VALIDATION

Goal: stop rerunning Basic Pitch solely to access raw `model_output['note']` activations. Capture those activations from the **same `predict()` call** that emits decoded pitch/onset notes, cryptographically bind the two outputs, and keep the sidecar duration/end-free.

New helper:
`scripts/songsterr-fresh/basic_pitch_activation_evidence.py`
commit `fa7049a890e258e8775b29e7ac2cbd56be133382`

Contracts:
- `songsterr-fresh-basic-pitch-note-activation-evidence-v1`
- `songsterr-fresh-basic-pitch-note-identity-v1`
- `songsterr-fresh-basic-pitch-inference-bundle-v1`

Identity design:
- canonical note identity hashes sorted `(startSeconds, midi, confidence)` using binary little-endian f64/u8/f64 rows plus a domain separator;
- activation sidecar stores the playable MIDI 40–88 slice of raw Basic Pitch `note` activations as exact little-endian float32 bytes, zlib+base64 encoded, with raw SHA256;
- exact Basic Pitch frame-time axis stored as little-endian float64 bytes, zlib+base64 encoded, with raw SHA256;
- bundle SHA binds note identity + activation matrix SHA + frame-time SHA + MIDI range/shape;
- release/probe consumers independently decode and verify raw SHA, shape, note identity, and bundle identity.

Hard sidecar guards:
- sameInferenceAsDecodedNotes true
- decodedModelNoteEndsIncluded false
- decodedModelNoteEndsUsedAsDuration false
- writesSourceEnd false
- writesDurationSeconds false
- activeDurationAuthority false
- changesPitchIdentity false

Transcription update:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`
commit `d03b22d2e1eb4e4cce6df591021f1066524e3f77`
- exactly one `predict()` call;
- optional `--activation-output` emits the sidecar from the same model output;
- decoded model note-off remains present only in ordinary note JSON as diagnosticModelEndSeconds;
- sidecar contains no decoded note-off field;
- note JSON records note and activation bundle identities.

Evidence propagation:
`scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs`
commit `8a252b69820eb5deea385f3073b2749553186408`
- validates note identity contract;
- validates optional activation bundle identity;
- propagates both identities into duration-free evidence;
- still emits null `sourceEnd` / `durationSeconds` at pitch stage.

Probe update:
`scripts/songsterr-fresh/probe_model_activation_valleys.py`
commit `d30243b7199793786fead9f86f090a80bc7c75a5`
contract now `songsterr-fresh-model-activation-valley-probe-v2`.
- optional `--activation-evidence` consumes same-inference sidecar;
- sidecar mode invokes **no second Basic Pitch model call**;
- cryptographically verifies exact note/bundle identity against duration evidence;
- uses the unchanged fixed activation+spectral rule;
- remains descriptiveOnly true / changesDuration false.

Validation workflows:
- deterministic sidecar probe workflow commit `4af488ececbe756fc168bb22578117ddf14d62d4`
- authoritative capture-only workflow commit `e68769012344ab66ccc870e2bad4fce0d91d27c5`

Active validation runs:
- deterministic same-inference activation run **`34315619967`**, job **`102351096162`**
- authoritative capture-only run **`34315700274`**, job **`102351339722`**

Both workflows deliberately call unchanged v2 release authority **without passing the sidecar**. Therefore activation capture cannot change active durations during this validation phase.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

Basic Pitch output is not ground truth. No reference scorer or archived logic is authorized.

## NEXT ENGINEERING STEPS

1. Finish sidecar validation runs `34315619967` and `34315700274`.
2. Require: one Basic Pitch predict call, exact cryptographic note/bundle identity, exact sidecar decoding, no duration/end fields, no second model call in the descriptive probe, unchanged v2 duration output, unchanged fixed activation thresholds, and 97/97 tests.
3. Compare sidecar-mode descriptive valley results against the previous 84/537 second-inference baseline. The expectation is close semantic agreement, but do not tune thresholds to force equality.
4. If capture-only validation is green, update this checkpoint with exact sidecar hashes/shapes/artifacts.
5. Only then modify the **same sole duration authority** to accept an optional activation sidecar as a fallback solely for events still unresolved as `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`.
6. Existing v2 spectral release must run first and remain primary.
7. The unchanged fixed activation+spectral rule may produce an observed release only before the same-pitch reattack and only with CQT corroboration; otherwise unresolved remains unresolved.
8. Do not use decoded Basic Pitch note-off, generic next onset, or the reattack itself as duration.
9. Do not invent a new duration-confidence heuristic merely to satisfy schema; deterministic adapter permits resolved duration with null duration confidence if needed.
10. Provenance must distinguish spectral-only versus activation+spectral observed-valley release.
11. Keep `modelValidationComplete: false` and customer eligibility 0 until independent model validation is separately completed.

## NON-NEGOTIABLES

- canonical branch/checkpoint above remain authoritative;
- no `main` / Production changes;
- frozen structure cannot be rewritten downstream;
- never silently alter/drop detected MIDI/event identity;
- preserve `/ai-tab` preview → unlock → full PDF → email/download journey;
- real-audio work stays on the exact authorized fixture unless explicitly expanded;
- archived V143/Gomyway and scorer/reference knowledge remain untouched;
- keep this checkpoint updated after every meaningful milestone.
