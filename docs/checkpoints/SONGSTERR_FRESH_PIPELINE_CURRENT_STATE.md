# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the Songsterr-inspired fresh pipeline. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or historical percentages unless the user explicitly asks.

## PRODUCT / ARCHITECTURE

Preserve `/ai-tab`:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh foundational order:

**full-mixture audio → frozen timing/measure map → role-isolated structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

Non-negotiables:
- only branch `songsterr-fresh-pipeline-v1`;
- no `main` / Production changes;
- frozen structure cannot be rewritten downstream;
- never silently change/drop detected MIDI/event identity;
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free;
- model/DSP work stays under `scripts/songsterr-fresh/`;
- archived V143/Gomyway code, reference tabs, reference-based correction, professional/reference scorer use, training/fine-tuning, and broad optimizer sweeps remain unauthorized.

The user explicitly authorized the **fresh reference-blind model/source-separation path**, including GPU if useful. Model execution authorization does not imply musical/customer acceptance.

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
- run `34309319200`
- job `102332488694`
- artifact `10087877760`
- digest `sha256:c051dfe5166a0d4fb019cf50aaae7afa97c7f477225657d9cc31b311c612ca31`
- 97/97 tests
- 1,128 Basic Pitch notes
- 591 duration-resolved / 537 unresolved
- 517 reattack-censored unresolved
- customer eligible 0

That run used Demucs `--shifts 1`, which is now known to apply one random shift augmentation, so its exact stem/note count is historical evidence rather than a reproducibility baseline.

## SINGLE DURATION AUTHORITY

Active script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract:
`songsterr-fresh-cpu-spectral-release-evidence-v2`

Hard rules:
- input must be duration-free;
- upstream non-null `durationSeconds` / `sourceEnd` rejected;
- model/GPU upstream denied unless explicitly authorized;
- decoded Basic Pitch note-off never becomes active duration;
- next generic onset never becomes duration;
- same-pitch reattack is a censor/search boundary, not an automatic duration.

Do not weaken these rules.

## ACTIVATION-VALLEY PROBE — DESCRIPTIVE ONLY

Script:
`scripts/songsterr-fresh/probe_model_activation_valleys.py`

Contract:
`songsterr-fresh-model-activation-valley-probe-v1`

Fixed rule, no sweep:
- Basic Pitch per-pitch activation <= 0.20
- sustained 3 BP frames
- activation drop >= 0.15
- observed span >= 0.07 s
- search stops at next same-pitch reattack or 4.0 s
- independent CQT corroboration >= 6 dB over 3 frames

Hard guards:
- descriptiveOnly true
- changesDuration false
- decoded model ends unused
- next onset unused
- no active `sourceEnd` / `durationSeconds` writes
- no pitch identity changes

Evidence:
- run `34310962622`: 89/541 corroborated valleys = 16.45%
- repaired green run `34311401076`, job `102338636114`: 79/550 = 14.36%, 1,174/1,174 exact same-run MIDI identity, 601 v2 durations resolved / 573 unresolved, 97/97 tests
- artifact `10088603197`
- digest `sha256:b13d90601f36ed150429b7d23e8d7073afac8623738498af1b3b20ed4566160c`

This is promising observed release evidence but is **not active duration yet**.

## DEMUCS 4.1 PRIMARY LOADER / EXECUTED ASSET — VERIFIED IDENTITY

Demucs 4.1 first loads named models through Hugging Face and falls back to the legacy remote repo only if HF loading fails.

For `htdemucs_6s`:
- HF namespace: `adefossez`
- HF repo: `adefossez/HTDemucs-6s`
- current pinned `main` snapshot: **`3c5ee475be622df764938de97e4281a7b07ffa58`**
- its parent / model-file upload commit: **`053e1404489b3dc58bf718224fac4b7316de8c93`**
- the later `3c5ee475...` commit changed only README license metadata; model assets remain inherited from `053e140...`
- bag: `htdemucs_6s.yaml`
- bag models: `['5c90dfd2']`
- executed model asset: `5c90dfd2.safetensors`
- safetensors SHA256: **`d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`**
- Xet hash: `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`

Legacy fallback, informational only:
- `5c90dfd2-34c22ccb.th`
- checksum prefix `34c22ccb`

Verifier:
`scripts/songsterr-fresh/verify_demucs_model_asset.py`

Contract:
`songsterr-fresh-demucs-model-asset-v2`

Revision history:
- v1 incorrectly targeted the legacy `.th` cache path;
- early v2 incorrectly treated `053e140...` as current HF `main`;
- commit **`a27bdb2b5736922b26c32c81454f25d016e725a3`** correctly distinguishes pinned repo snapshot `3c5ee475...` from model-file upload revision `053e140...` while keeping the exact model SHA gate.

## DEMUCS REPRODUCIBILITY BOUNDARY

### Intentional shift randomness

Old `--shifts 1` stems/counts varied:
- `d47f51ac...` → 1,128 notes
- `99ded9ff...` → 1,170 notes
- `dbc198ae...` → 1,174 notes

Root cause: Demucs random shift trick for any `shifts > 0`.

### Cross-environment floating-point/runtime variation

`--shifts 0` removes intentional random augmentation, but stem bytes are not assumed universal across arbitrary runner environments.

Observed `--shifts 0` stems include:
- two earlier jobs on one runner generation: `8983d2694cbae3a519a65eadc63cc5bf691a6a542f2f6539b9a5f4461cd8727c`
- later runner: `419fcb5dd869e7d7cd2f66468c6c436fc9bb7767aaf546dd4cb61d34fde62ef1`
- pinned-runtime pass A on run `34313107961`: `c303f0a0d99f94e2bddedebd0679cc5034aa9505c350cc28a5200d4c419637af`

Pinned-runtime run `34313107961`, job `102343661824` recorded:
- runner image `20260831.293.1`
- CPU `INTEL(R) XEON(R) PLATINUM 8573C`
- Python 3.10.21
- FFmpeg 6.1.1-3ubuntu5
- decoded separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- numpy 1.26.4
- torch 2.14.0
- huggingface-hub 1.30.0
- safetensors 0.8.0
- sphn 0.2.1
- demucs 4.1.0
- soundfile 0.13.1
- OMP/MKL/OpenBLAS/NumExpr threads = 1
- PYTHONHASHSEED=0

That run stopped before pass B only because the verifier expected the wrong HF repo revision. Partial artifact `10089166444`, digest `sha256:4ca0ebb33a58bd7d5c79be004581ad41fd0a8a3fa3538c271a3248a5134db885`.

Current reproducibility acceptance contract:
1. exact source fixture and decoded input hash;
2. pinned package/model/runtime identities;
3. Demucs `--shifts 0`;
4. exact executed HF asset SHA;
5. same-job / same-runtime pass A and B must have identical SHA and byte `cmp`;
6. cross-environment stem SHA is diagnostic only;
7. semantic note/evidence stability is evaluated separately.

## CURRENT CORRECTED CANARIES

Reproducibility workflow:
`.github/workflows/songsterr-fresh-demucs-reproducibility-canary.yml`

Current workflow commit:
**`2c401079b59937d1d3fde6beb4bbba97f411e3ce`**

Active corrected run:
- **`34313527494`**
- job **`102344892749`**

Goal:
exact fixture → runtime/input manifest → Demucs shifts=0 pass A → verified HF snapshot `3c5ee475...` + exact safetensors SHA → pass B → same-runtime byte identity → artifact.

Deterministic activation workflow:
`.github/workflows/songsterr-fresh-model-activation-valley-deterministic.yml`

Current workflow commit:
**`afbf901a03f11e93e8b2edf18823a3b25aa1c129`**

Active corrected run:
- **`34313623897`**
- job **`102345173559`**

Goal:
exact fixture/frozen structure → pinned-runtime Demucs shifts=0 → exact HF asset proof → duration-free Basic Pitch evidence → unchanged v2 sole release authority → unchanged descriptive activation rule → 97/97 suite → artifact.

No historical fixed stem SHA or Basic Pitch note count is used as a cross-environment gate.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

## NEXT ENGINEERING STEPS

1. Require corrected reproducibility run `34313527494` to prove same-runtime pass-A/pass-B byte identity and exact HF asset identity.
2. Require corrected activation run `34313623897` to produce same-run Basic Pitch/duration/valley diagnostics and 97/97 tests.
3. If both are green, update the authoritative model canary from stochastic `--shifts 1` to pinned-runtime `--shifts 0` with the same HF-asset proof.
4. Compare available `--shifts 0` outputs semantically rather than demanding cross-runner audio-byte equality.
5. Capture Basic Pitch raw `note` activations from the **same existing inference call** rather than rerunning Basic Pitch solely for duration.
6. Feed those activations into the **same sole duration authority** only as a fallback for events otherwise unresolved by `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`, using the unchanged fixed activation+spectral rule.
7. Preserve negative proofs: no decoded BP note-off as active duration, no next-onset duration, no upstream duration leakage, explicit model-upstream authorization, exact MIDI/event identity, no reference/scorer provenance.
8. Keep model validation false and customer eligibility 0 until separately validated.

## NON-NEGOTIABLES

- canonical branch/checkpoint above remain authoritative;
- no `main` / Production changes;
- frozen structure cannot be rewritten downstream;
- never silently alter/drop detected MIDI/event identity;
- preserve `/ai-tab` preview → unlock → full PDF → email/download journey;
- real-audio work stays on the exact authorized fixture unless explicitly expanded;
- archived V143/Gomyway and scorer/reference knowledge remain untouched;
- keep this checkpoint updated after every meaningful milestone.
