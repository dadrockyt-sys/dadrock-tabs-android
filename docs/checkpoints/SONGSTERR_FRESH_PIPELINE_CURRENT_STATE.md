# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — boundary-aware V2 repair completed; all synthetic gates passed; one authorized real EGFxSet V2 diagnostic executed and froze as FAIL because real MIDI-40 E2 failed the inherited physical-template plausibility gate; user-directed V6 replacement-holdout search rejected GuitarJam, URMP, GAPS, and EGDB pre-media, while AG-PT-set is the first candidate to clear every frozen pre-media metadata/license/alignment/provenance gate; AG-PT-set media remains untouched pending a frozen one-shot PRE and explicit real-media/model authorization
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
Latest real-audio result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The user's `Please try the run again` authorization was consumed by run `34938917218`, attempt 1.

The user's subsequent instruction `Lets take what was learned, repair and run again` authorized one boundary-repair cycle plus exactly one new non-authoritative EGFxSet V2 diagnostic after prospectively frozen synthetic gates. The repair was completed, the synthetic gates passed, and the real authorization is now fully consumed by run `34940292514`, attempt 1.

There is **no authorized retry, threshold variation, alternate candidate, Basic Pitch rerun, or modified-real-rule execution** under that instruction.

## HISTORICAL EGFxSET ALL-EVENTS SMOKE — STILL FROZEN FAIL

Candidate: EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`, truth string 6 / fret 0 / MIDI 40.

Repaired Basic Pitch run `34936227380` emitted immutable proposals `[40,68]`; `basic-pitch.json` SHA-256 is `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`; note identity SHA-256 is `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`.

Historical score remains `PASS_RUNTIME`, `FAIL_PITCH`, `FAIL_POSITION`, overall `FAIL_NON_AUTHORIZING_SMOKE`. Never rewrite it into a PASS.

## PIPELINE HARDENING V1 — CODE/SYNTHETIC GREEN

Combined regression run `34938422696`, job `104281318739`, passed:
- confidence-independent qualification;
- exact identity/population fail-closed behavior;
- explicit rejected-proposal preservation;
- physical-position ambiguity reporting;
- synthetic DSP note-birth tests.

Core design remains:
- Basic Pitch events are proposals only;
- only independently `corroborated` proposals promote;
- `rejected` proposals remain preserved but do not promote;
- `insufficient` remains unresolved/fail-closed;
- Basic Pitch confidence is diagnostic-only.

## HARDENED V1 REAL-AUDIO DIAGNOSTIC — FROZEN FAIL AT LEFT BOUNDARY

PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`, commit `8b741a8b25b61966c832860f4d91f42a018f898e`.

Result: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`, commit `e2935b5f9c3ecb14baf770e492d03ea9d8fcfc3b`.

Run `34938917218`, job `104282855445`, artifact `10384459031` reused the immutable `[40,68]` Basic Pitch artifact and invoked no Basic Pitch inference.

V1 rejected both:
- MIDI 40 near clip start after inserting 3072 zero-padding samples, reason `OK_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`;
- MIDI 68 normally, necessity fraction `0.000513675778819313`.

Frozen V1 score:
- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`.

That V1 result identified the unsafe synthetic-precontext boundary policy and remains immutable history.

## BOUNDARY QUALIFIER V2 — REPAIR COMPLETE

PRE checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
commit `819d7a9a855d6f067aa40a007fdd0570d231d782`.

The V2 repair prospectively removed synthetic pre-context ownership from clip-start decisions.

### Normal in-clip path

When genuine required left context exists, the existing frozen V6 complex-harmonic onset-birth classifier remains unchanged.

### Clip-start path

When onset is earlier than the inherited `3584`-sample left-context requirement:

- never zero-pad or fabricate pre-audio;
- use exactly `8192` genuine post-onset samples at 44.1 kHz;
- demean + Hann + 8192-point real FFT magnitude;
- inherit playable MIDI `40..88`, six-harmonic dictionary, RMS/feature-energy floors, physical-template fundamental ratio `0.20`, and necessity minimum `0.01`;
- use full-vs-selected-removed NNLS necessity;
- detect lower-fundamental harmonic owners for harmonics 2..6 within ±50 cents;
- corroborate only if selected template is physically valid, selected coefficient >0, selected necessity >=0.01, and no dominant lower harmonic owner exists;
- missing genuine post-context or numerical/support failure remains `insufficient`.

No special-case MIDI values, EGFxSet labels, candidate confidences, or real-result measurements were embedded in the rule.

Implemented:

- `scripts/songsterr-fresh/clip_start_pitch_presence_v1.py`, commit `e24aea935058281c5d75b3a700759e055607e735`
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py`, commit `eeed1e8b11a53bfc4e69967de0ad49d0655867ed`
- `scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence_v2.mjs`, commit `5ff87dbf962acc3dad1d474da013299019bb6f03`
- `scripts/songsterr-fresh/adapt_qualified_note_evidence_v2.mjs`, commit `ead4f6c88c4a0337621cb7cfa0072ab540031fe3`
- `scripts/songsterr-fresh/test_qualify_basic_pitch_note_births_v2.py`, commit `8842c2cb9b4702de2bbcd25145c864c82447fc7e`
- `scripts/songsterr-fresh/test_model_note_qualification_v2.mjs`, commit `f7ff6e7b2b1a242a2f513d0b4022d6069cc88eb4`.

## V2 SYNTHETIC PREREQUISITE GATES — ALL PASS

Workflow `.github/workflows/songsterr-egfxset-boundary-v2-one-shot.yml`, commit `02414c689b4210771c0f454acc36b86d41e0aafe`, ran the synthetic gates before fetching real EGFxSet media.

Passed under Python `3.10.21`, NumPy `1.26.4`, SciPy `1.15.3`, Node 20:

- V2 structural/fail-closed builder: 4 cases PASS;
- V2 boundary DSP suite: 8 cases PASS;
- ordinary in-clip E2 birth / later harmonic => `[corroborated,rejected]`;
- confidence inversion invariant;
- true clip-start MIDI 40, 45, 52, 68 each corroborated;
- clip-start E2-only aliases `[40,52,68]` => `[corroborated,rejected,rejected]`;
- genuine clip-start E2 + G#4 polyphony => `[corroborated,corroborated]`;
- noise did not corroborate;
- missing post-context remained insufficient;
- synthetic pre-context was never used;
- physical-position ambiguity regression PASS.

Only after all these gates passed did the one real V2 diagnostic proceed.

## LATEST REAL-AUDIO DIAGNOSTIC — BOUNDARY V2 FROZEN FAIL

Dedicated result:
`docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
result checkpoint commit `42b8fc30de468b123d6c5f5d7df6d5a43db86c81`.

Execution:

- workflow `.github/workflows/songsterr-egfxset-boundary-v2-one-shot.yml`
- workflow execution commit `02414c689b4210771c0f454acc36b86d41e0aafe`
- run `34940292514`
- job `104287207091`
- attempt `1`
- artifact `10385620104`
- artifact ZIP SHA-256 `f7a48267c299eaf3bba564c05913c95d41d07026ebf4245e9b40762274202948`
- artifact size `11816` bytes.

Captured hashes:

- `result-v2.json`: `1416df0edbc9d1b534ac2c4727526ebcf52227327caace10d744ada64236a6cf`
- `qualification-v2.json`: `7d9354196d6bcb12c48f22e003f7d0f7ff9e46d429245319a016722ef3257eda`
- `qualified-evidence-v2.json`: `83fc1f197842c97794a34fcb3fd2ab4985a5b4849271d6f4b1654b307af347d8`
- `adapted-evidence-v2.json`: `e1de6cd744d1b66208931601d63df4d723c819465c52f902b5743b19d71f0c80`
- `context.json`: `a9ef99bb7e580abda9006dbe4ff2fdf31510773498dc5e449c6d6839a7b1768f`
- `duration.json`: `bef1b4c35c25acaf3dcdd77dafa41fd9298b758d37268bbbffce853e52b6b180`
- immutable `basic-pitch.json`: `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`.

All infrastructure and processing steps before final scoring succeeded. Basic Pitch was not invoked.

### Observed MIDI 40

- note `basic-pitch-note-000000`
- start `0.011609977324263039 s`
- V2 mode `clip-start-one-sided-pitch-presence`
- method `clip-start-post-spectrum-harmonic-necessity-v1`
- status `rejected`
- reason `BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`
- original onset sample `512`
- clip-start window `8192` real samples
- left zero padding `0`
- `syntheticPreContextUsed:false`
- analysis RMS `0.2769195787794421`
- selected coefficient `0.0`
- necessity fraction `0.0`
- no dominant lower harmonic owner implicated
- Basic Pitch candidate confidence not used.

The selected MIDI-40 template failed the inherited physical-template plausibility gate before NNLS feature/necessity analysis. The wrapper did not persist the internal template-ratio value, so do not invent that number after the fact.

### Observed MIDI 68

- note `basic-pitch-note-000001`
- start `0.3599092970521542 s`
- normal in-clip unchanged V6 path
- status `rejected`
- reason `OK`
- analysis RMS `0.22146136772942196`
- innovation energy `3.007380617012349`
- feature energy `2.4146259263190646`
- selected coefficient `0.06436904984371984`
- necessity fraction `0.000513675778819313` (< frozen `0.01`).

Thus MIDI 68 remains correctly suppressed and never promotes.

### V2 promotion / score

Observed:

- raw proposals `[40,68]`
- statuses `{40: rejected, 68: rejected}`
- insufficient count `0`
- promoted MIDI list `[]`
- rejected-preserved list `[40,68]`
- unresolved onset count `0`
- promoted positions `[]`.

Frozen score:

- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`.

The user's one real V2 authorization is consumed. Do not retry this run or alter its score.

## KEY LEARNING / CURRENT CONCRETE WEAK POINT

The zero-padding boundary defect is fixed: V2 used no fabricated pre-context and passed broad prospective boundary tests.

The remaining concrete weakness is now the **physical harmonic-template plausibility model**. The inherited single fundamental-to-strongest-harmonic physical gate generalizes poorly to this real electric-guitar E2 timbre in the clip-start post spectrum, rejecting the expected fundamental before the NNLS necessity stage. This is a timbre/template-model generalization problem, not another missing-context problem.

Do **not** lower the frozen `0.20` ratio, remove that gate, special-case MIDI 40, or tune from this EGFxSet observation under the consumed authorization.

## NEXT SAFE ENGINEERING DIRECTION — NO REAL RUN AUTHORIZED

Permitted without a new real-media authorization:

- inspect frozen code and captured metadata;
- design a prospective V3 physical-template criterion against broad synthetic/non-EGFxSet timbre variation;
- test candidate V3 rules only on independent synthetic/non-EGFxSet fixtures;
- preserve harmonic-alias rejection, genuine polyphony recovery, confidence independence, exact identity, and fail-closed behavior.

A plausible V3 research direction is replacing the single fundamental-to-maximum-harmonic plausibility test with a timbre-robust multi-harmonic/support criterion, but the exact rule must be established independently of this EGFxSet result and frozen before any further real-media execution.

Any further EGFxSet/model/media experiment requires **new explicit prospective user authorization**. Do not rerun Basic Pitch, the V2 workflow, or a modified real rule without that authorization.

## USER-DIRECTED V6 REPLACEMENT-HOLDOUT SEARCH — GUITARJAM REJECTED PRE-MEDIA

The separate user-directed V6 audit instruction permits metadata/license/alignment search after Guitar-TECHS decision C, but does not alter the global real-media/correctness authorization fields above.

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_GUITARJAM_PREMEDIA_REJECTION.md`, commit `ff9e82791df33ca48e355df555a25190104b2454`.

GuitarJam public metadata establishes approximately 2.5 hours / 580 clips of clean monophonic electric-guitar DI, WAV 44.1 kHz 16-bit, with repository metadata declaring CC0-1.0. Its public dataset description/repository does not establish synchronized pre-existing note-event ground truth aligned to those performances. Frozen V6 scoring cannot manufacture or infer the holdout reference.

Decision: **REJECT BEFORE MEDIA ACCESS**. No GuitarJam WAV/reference was downloaded or opened; no Basic Pitch/V6 correctness ran; no frozen method/scoring rule changed; no Modal, Vercel heavy-GPU, or L4 work occurred.

Guitar-TECHS run `34754519541`, job `103716527380` was rechecked live on 2026-09-15 and remains `completed/success`; its frozen decision C remains closed and must not be scored.

## USER-DIRECTED V6 REPLACEMENT-HOLDOUT SEARCH — PRE-MEDIA BATCH 2

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_URMP_GAPS_EGDB.md`, commit `9a20dcde71f954d4a1704dfca2985e91366f8cc6`.

The frozen ingress rule remains: before any candidate media access, public evidence must establish a real guitar performance, usable public licensing, synchronized note events aligned to the exact performance, and sufficiently independent reference provenance for frozen V6 scoring.

Metadata-only dispositions:

- **URMP — REJECT_PREMEDIA:** official corpus instrumentation contains strings, woodwinds, and brass but no guitar; therefore it fails the real-guitar domain gate despite strong note-level ground truth.
- **GAPS — REJECT_PREMEDIA:** real guitar and aligned MIDI are established, but the official terms restrict use to non-commercial research by the named individual/group and prohibit transfer/distribution without permission. Its high-resolution alignment also uses DTW plus fine alignment to activations from an existing transcription model, so it does not satisfy the frozen independent-reference requirement.
- **EGDB — REJECT_PREMEDIA:** public metadata establishes real electric-guitar performances and aligned note annotations, but the public project page/repository does not establish a usable dataset license. Public downloadability is not a license grant. Because licensing already fails, alignment independence was not adjudicated.

For all three candidates: no audio/video/reference payload was downloaded or opened; no Basic Pitch ran; no V6 correctness ran; no frozen method/scoring rule changed; no EGFxSet execution occurred; no V143/Gomyway activity occurred.

## USER-DIRECTED V6 REPLACEMENT-HOLDOUT SEARCH — AG-PT-SET CLEARS PRE-MEDIA GATES

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_PREMEDIA_CLEARANCE.md`, commit `636403d0d168700cb77e36462d8f71caf9bc2809`.

AG-PT-set is the first candidate in the current replacement search to clear all frozen pre-media gates:

- **real guitar — PASS:** real monophonic acoustic/electro-acoustic guitar performances by multiple human players on multiple physical guitars;
- **usable public license — PASS:** Zenodo record `10.5281/zenodo.10159492` was directly inspected on 2026-09-15 and reports Open Access under Creative Commons Attribution 4.0 International (`CC BY 4.0` / `CC-BY-4.0`);
- **exact synchronized note reference — PASS:** released `note_labels.csv` ties each onset to the exact WAV and includes onset seconds/samples, ground-truth MIDI pitch, string number, playing technique and intensity; per-file onset/pitch label files are also described;
- **independent provenance — PASS for ingress:** pitched content was prospectively prescribed by string/fret/note sequence; five musician annotators manually corrected and millisecond-aligned onset labels to the actual recordings. `aubioonset` only seeded candidate onset marks, and known note number/pitch/sequence plus a pitch detector were used to find annotation mistakes. The final scoring reference is pre-existing and independent of Basic Pitch/V6.

Decision: **PASS_PREMEDIA**. This is admission to prospective planning only, not permission to touch the data or run the model.

AG-PT-set archive/media/annotation payloads remain untouched: no 6.7-GB ZIP click/download, no WAV opened, no label payload opened, no Basic Pitch, no V6 correctness, no EGFxSet run, and no frozen scoring change.

Before any AG-PT-set media access, freeze a dedicated one-shot PRE that defines candidate selection from metadata, exact reference fields, sample-rate handling, immutable scoring, and no rerun/tuning/candidate substitution after access; then obtain explicit user authorization for the real-media/model action.

## FRESH CHAT — EXACT NEXT STEPS

On a fresh chat:

1. re-fetch live `songsterr-fresh-pipeline-v1` and this checkpoint;
2. treat V2 run `34940292514` and result checkpoint as frozen completed evidence;
3. do not trigger another EGFxSet or Basic Pitch run without new explicit authorization;
4. Guitar-TECHS remains decision C; GuitarJam, URMP, GAPS, and EGDB remain closed pre-media rejections; AG-PT-set is **PASS_PREMEDIA** and is the current prospective V6 replacement-holdout candidate;
5. do not access AG-PT-set media/reference payloads or run V6 yet; first create and commit a prospective one-shot AG-PT-set PRE that freezes candidate-selection rule, exact reference fields, preprocessing/sample-rate treatment, scoring, fail-closed behavior, and no post-access tuning/substitution; then require explicit user authorization for the real-media/model execution;
6. keep historical all-events, hardened-V1, V2, and all V6 rejection/clearance records unchanged;
7. do not reopen V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution, `main`, Production, reserved GFN splits, or physical procurement/calibration/capture unless separately authorized.

## AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.