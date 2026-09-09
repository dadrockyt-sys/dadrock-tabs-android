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

Earlier evidence:
- run `34310962622`: 89/541 corroborated valleys = 16.45%
- repaired green run `34311401076`, job `102338636114`: 79/550 = 14.36%, 1,174/1,174 exact same-run MIDI identity, 601 v2 durations resolved / 573 unresolved, 97/97 tests
- artifact `10088603197`
- digest `sha256:b13d90601f36ed150429b7d23e8d7073afac8623738498af1b3b20ed4566160c`

Latest pinned deterministic evidence is recorded below. Activation valleys remain **descriptive only** and are not active duration yet.

## DEMUCS 4.1 PRIMARY LOADER / EXECUTED ASSET — VERIFIED

Demucs 4.1 first loads named models through Hugging Face and falls back to the legacy remote repo only if HF loading fails.

For `htdemucs_6s`:
- HF namespace: `adefossez`
- HF repo: `adefossez/HTDemucs-6s`
- pinned repo snapshot: **`3c5ee475be622df764938de97e4281a7b07ffa58`**
- model-file upload revision: **`053e1404489b3dc58bf718224fac4b7316de8c93`**
- bag: `htdemucs_6s.yaml`
- bag models: `['5c90dfd2']`
- executed model asset: `5c90dfd2.safetensors`
- safetensors SHA256: **`d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`**
- Xet hash: `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`
- safetensors metadata keys: `args`, `klass`, `kwargs`
- model class: `demucs.htdemucs.HTDemucs`

Legacy fallback, informational only:
- `5c90dfd2-34c22ccb.th`
- checksum prefix `34c22ccb`

Verifier:
`scripts/songsterr-fresh/verify_demucs_model_asset.py`

Contract:
`songsterr-fresh-demucs-model-asset-v2`

Latest verifier commit:
**`88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`**

Important correction history:
- v1 incorrectly targeted the legacy `.th` cache path;
- early v2 conflated the current repo snapshot with the model-file upload commit;
- another early v2 required a nonexistent `5c90dfd2.json` sidecar;
- current v2 matches the actual Demucs 4.1 HF loader: bag YAML + safetensors, with class/init metadata verified from inside the safetensors file.

The verifier invokes no model and changes no audio/evidence.

## DEMUCS REPRODUCIBILITY — GREEN SAME-RUNTIME PROOF

### Intentional shift randomness

Old `--shifts 1` stems/counts varied:
- `d47f51ac...` → 1,128 notes
- `99ded9ff...` → 1,170 notes
- `dbc198ae...` → 1,174 notes

Root cause: Demucs random shift trick for any `shifts > 0`.

### Cross-environment floating-point/runtime variation

`--shifts 0` removes intentional random augmentation, but stem bytes are not assumed universal across arbitrary runner environments.

Observed `--shifts 0` stem SHA variation across runners includes `8983d269...`, `419fcb5d...`, `c303f0a0...`, `0d9339df...`, and `4227a41f...`.

Therefore the acceptance contract is runtime-scoped:
1. exact source fixture and decoded input hash;
2. pinned package/model/runtime identities;
3. Demucs `--shifts 0`;
4. exact executed HF asset SHA;
5. same-job / same-runtime pass A and B must have identical SHA and byte `cmp`;
6. cross-environment stem SHA is diagnostic only;
7. semantic note/evidence stability is evaluated separately.

Final green reproducibility canary:
- workflow `.github/workflows/songsterr-fresh-demucs-reproducibility-canary.yml`
- run **`34313902753`**
- job **`102345983922`**
- head **`88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`**
- conclusion **success**
- runner Ubuntu 24.04.4, image `20260831.293.1`
- CPU `AMD EPYC 7763 64-Core Processor`
- Python 3.10.21
- FFmpeg 6.1.1-3ubuntu5
- decoded separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- Demucs 4.1.0 / Torch 2.14.0 / CPU / shifts 0 / overlap 0.25 / segment 7
- executed asset SHA `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- pass A stem SHA **`4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`**
- pass B stem SHA **`4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`**
- `identicalStemSha256: true`
- `identicalStemBytes: true`
- sample rate 44,100 Hz, 2 channels, 9,290,752 frames, 210.6746485260771 s
- determinism contract `songsterr-fresh-demucs-determinism-proof-v2`
- artifact **`10089522605`**
- artifact size 3,048 bytes
- artifact ZIP digest **`sha256:a49e36478b541907b377fb94e9a264003eb69ff1bf20dd2d2904e0fc2f37fb43`**

Conclusion: **same-runtime deterministic Demucs separation is now proven for the exact authorized fixture under the pinned runtime.** Cross-environment stem-byte canonicality remains explicitly false.

## PINNED DETERMINISTIC ACTIVATION CANARY — GREEN

Workflow:
`.github/workflows/songsterr-fresh-model-activation-valley-deterministic.yml`

Final green run:
- run **`34313902747`**
- job **`102345984013`**
- head **`88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`**
- conclusion **success**
- artifact **`10089483424`**
- artifact ZIP digest **`sha256:7d20bb6b18423c8dac44820391161eafa4de2e724465488f99598edf876b8ef5`**
- artifact size 304,743 bytes
- 97/97 deterministic tests pass

Runtime/input:
- Ubuntu 24.04.4 / image `20260831.293.1`
- Python 3.10.21
- CPU `AMD EPYC 9V74 80-Core Processor`
- FFmpeg 6.1.1-3ubuntu5
- analysis WAV SHA `824af60bbc3d701c8c1f085194be2acf59f0ac5d0ae4133e763eadb9793ca873`
- separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- frozen structure identity exact `fnv1a32:2f493225`

Demucs/model separation:
- guitar stem SHA **`0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12`**
- shifts 0, CPU, overlap 0.25, segment 7
- exact HF repo/snapshot/model SHA verified
- separation contract `songsterr-fresh-demucs-guitar-separation-v3`
- `crossEnvironmentStemShaCanonical: false`

Basic Pitch / duration-free evidence:
- **1,139 notes**
- 1,031 start clusters
- 97 polyphonic start clusters
- max cluster size 4
- MIDI 40 count 34
- 1,139/1,139 exact same-run model/evidence identity
- exact MIDI identity true
- role relevance resolved true
- polyphony resolved true
- durationResolution none before release
- decoded note ends remain diagnostic only

Existing sole v2 release authority:
- attempted **1,139**
- resolved **577**
- unresolved **562**
- resolution rate ~50.66%
- `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`: **537**
- `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`: 7
- `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`: 18
- same-pitch reattack censor count 967
- mean resolved duration ~0.463894 s
- median ~0.341035 s
- max ~3.652337 s
- mean duration confidence ~0.913798

Fixed descriptive activation-valley probe on the same evidence:
- examined reattack-censored: **537**
- corroborated activation+spectral valleys: **84**
- fixed-rule hit rate **15.64%**
- rejections: 5 insufficient activation drop, 76 insufficient spectral corroboration, 372 no sustained subthreshold activation
- observed spans mean ~0.299432 s, median ~0.290249 s, p90 ~0.430853 s, max ~1.069402 s
- exact MIDI identity true
- max start delta 0
- max confidence delta 0
- threshold sweep false
- decoded model note ends used false
- next onset used as duration false
- writes `sourceEnd` false
- writes `durationSeconds` false
- changes pitch identity false

Conclusion: the unchanged fixed rule again finds a stable minority (~14–16% across the available runs) of reattack-censored events with activation valleys independently corroborated by spectral decay. It is still **descriptive only** pending same-inference activation capture and guarded integration into the sole duration authority.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

Basic Pitch output is not ground truth. No reference scorer or archived logic is authorized.

## NEXT ENGINEERING STEPS

1. Update the authoritative model canary from stochastic Demucs `--shifts 1` to the pinned-runtime `--shifts 0` architecture, including exact HF asset verification and runtime provenance.
2. Establish the new **runtime-scoped** authoritative model baseline; do not impose a universal cross-runner stem SHA or historical fixed Basic Pitch note-count gate.
3. Compare available `--shifts 0` outputs semantically rather than demanding cross-runner audio-byte equality: note counts/distributions, onset characteristics, v2 duration coverage, and valley coverage. Do not tune thresholds from this comparison.
4. Capture Basic Pitch raw `note` activations from the **same existing inference call** rather than rerunning Basic Pitch solely for duration evidence. Tie the activation sidecar to the emitted note list with a deterministic identity hash over `(start,midi,confidence)` and keep it duration/end-free.
5. Feed that sidecar into the **same sole duration authority** only as a fallback for events otherwise unresolved by `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`, using the unchanged fixed activation+spectral rule.
6. Existing v2 spectral release remains first/primary; an activation valley may become observed release only when the fixed activation rule and independent CQT corroboration both pass.
7. If integrated, provenance must distinguish spectral-only vs activation+spectral observed-valley release. Unqualified events remain unresolved.
8. Preserve negative proofs: no decoded BP note-off as active duration, no next-onset duration, no upstream duration leakage, explicit model-upstream authorization, exact MIDI/event identity, no reference/scorer provenance.
9. Keep model validation false and customer eligibility 0 until independent model validation is separately completed.

## NON-NEGOTIABLES

- canonical branch/checkpoint above remain authoritative;
- no `main` / Production changes;
- frozen structure cannot be rewritten downstream;
- never silently alter/drop detected MIDI/event identity;
- preserve `/ai-tab` preview → unlock → full PDF → email/download journey;
- real-audio work stays on the exact authorized fixture unless explicitly expanded;
- archived V143/Gomyway and scorer/reference knowledge remain untouched;
- keep this checkpoint updated after every meaningful milestone.
