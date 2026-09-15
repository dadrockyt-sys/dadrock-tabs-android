# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — fresh-chat next work order frozen after train-only real-audio physical-position feasibility signal
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other explicitly closed/revealed lines remain closed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration authority remains paused, Policy C `UNENROLLED`, protected-song execution embargoed.
- Ordinary metadata research/coding/GitHub/CPU/checkpoint work may proceed.
- **Budget boundary:** available spend is effectively limited to existing Vercel/model costs. Do not assume new hardware, bench equipment, audio interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or other paid acquisition. The purpose-built physical route is software-prepared but hardware-paused.
- Do not weaken the validation standard to fit budget. Synthetic/non-holdout evidence must never be presented as untouched external correctness validation.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve every decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance match onset <= `0.050 s`, pitch <= `50 cents`; V6-positive precision with one-sided 95% Wilson LB; >=`1,000` pooled V6-positive estimates; pooled Wilson LB >=`0.9900`; player/category strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.

Reverified evidence: 104 DI/MIDI pairs, 18,934 reference events, all 104 alignment statuses `OK`; 5 same-key overlaps + 7 unmatched note-ons; frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run on Guitar-TECHS. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after a structural pass may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

No currently reviewed public candidate clears all five gates. The new Guitar Fretboard Notes work below is explicitly **NON_HOLDOUT feasibility research** and does not change this status.

## ZERO-COST EXTERNAL-CORPUS RESEARCH — GUITAR FRETBOARD NOTES TRAIN-ONLY V1

Dataset: `collegefishiesd/guitar-fretboard-notes`.
Pinned dataset revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`.
Declared license: `CC-BY-SA-4.0`.

This route was added because the public corpus contains isolated real-guitar notes labeled by exact physical string and fret. It is useful for asking whether audio timbre contains repeatable physical-position information, but it is not an admissible Songsterr Fresh correctness holdout.

### Split boundary — FROZEN BEFORE AUDIO ACCESS

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_DISCRIMINABILITY_PREREGISTRATION_V1_2026-09-14.md`
commit `ff62869274bd509802f5c4b3e565422eb23741f3`.

Only `train` was authorized for this NON_HOLDOUT study:
- `ele`: 78 rows;
- `eqm`: 78 rows;
- `eqm2`: 78 rows;
- total: 234 rows.

Reserved and **untouched**:
- `test`, source `deb`: 78 rows;
- `validation`, source `ele_natural`: 78 rows.

Do not load, stream, download, decode, inspect, feature-extract, score, or otherwise consume either reserved source unless a later separate preregistration is frozen before access.

### Frozen V1 question / method

Question: conditional on the exact corpus-labeled MIDI pitch, can a deterministic audio feature set distinguish which physical `(string,fret)` produced that pitch across recording sessions?

This deliberately removes pitch recognition from the decision: each query may be matched only against prototype notes having exactly the same labeled MIDI number.

Feature contract `gfn-train-position-features-v1` is frozen in the preregistration: deterministic onset selection, fixed 65,536-sample segment, RMS normalization, Hann/RFFT, relative log-power for harmonics 1..12, plus four fixed temporal RMS fractions. No learned embedding, neural network, pitch detector, source separator, adaptive feature selection, Basic Pitch, V6, or archived pipeline is permitted.

Primary cross-session comparison is only:
- `eqm` prototypes -> `eqm2` queries;
- `eqm2` prototypes -> `eqm` queries.

### Implementation / CI — SUCCESS

Implementation/test/workflow integration head: `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`.

- implementation: `scripts/songsterr-fresh/guitar_fretboard_notes_train_discriminability_v1.py`, blob `7d62fc354d8667742f796af5145b0a04203f4f7a`;
- tests: `scripts/songsterr-fresh/test_guitar_fretboard_notes_train_discriminability_v1.py`, blob `2e039d0ce3c83e6bb7d5097ca5ea31202ca96042`;
- workflow: `.github/workflows/songsterr-fresh-gfn-train-position-discriminability-v1.yml`, blob `efd64ba1575789c0a2311b412823c94822aea21e`;
- GitHub CPU run `34914789254`, job `104209961023`, conclusion `success`;
- 13/13 synthetic contract tests PASS;
- real train-only feature extraction failure count `0`;
- pinned train parquet SHA-256 `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`;
- canonical artifact ID `10375479293`, uploaded ZIP SHA-256 `580b08c329459b94e6a000c51f66dc59cabc893f642d6713f9e8bf55d35e57ec`.

Result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_DISCRIMINABILITY_RESULT_V1_2026-09-14.md`, commit `535e6861bb9895f5c38161ec7877a6534cf6fa4e`.

### Frozen train-only result

`eqm` -> `eqm2`:
- 68 eligible same-pitch ambiguous-position queries;
- 41 correct;
- exact physical-position accuracy `60.29%`;
- chance baseline `39.71%`;
- lift `+20.59` percentage points.

`eqm2` -> `eqm`:
- 68 eligible queries;
- 32 correct;
- exact physical-position accuracy `47.06%`;
- chance baseline `39.71%`;
- lift `+7.35` percentage points.

Pooled:
- 136 eligible queries;
- 73 correct;
- exact physical-position accuracy `53.68%`;
- chance baseline `39.71%`;
- lift `+13.97` percentage points.

Interpretation: the frozen simple feature set recovered physical string/fret identity above chance while pitch was held constant. This is useful evidence that repeatable physical-position timbral information exists in these isolated-note recordings. The 60.29% vs 47.06% directional asymmetry is material and shows substantial session sensitivity; audio-alone physical-position recovery is not solved or robust.

The corpus does not establish behavior for chords, simultaneous same-pitch notes, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, full-song performance, noisy deployment audio, or the frozen V6 correctness objective. The purpose-built independent-reference design remains the authoritative technical route for eventual correctness validation.

All downstream authorization remains closed:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## PURPOSE-BUILT HOLDOUT — ACTIVE IN SOFTWARE, PHYSICAL ROUTE PAUSED BY BUDGET

The purpose-built independent-sensor route remains the best technically defensible validation design, but under the current budget it may advance only through zero-additional-cost software/documentation/synthetic CI. Real hardware procurement, non-holdout physical calibration and real holdout capture are paused until equivalent hardware becomes available at no additional cost or the budget constraint changes.

Design authority:
- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture QA/gate matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`.

### Capture-manifest V2.1 — SYNTHETIC CI PASS

Implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`, commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`.
Tests commit `ff5717a4aeb9b74e971694703f6d6cb785389845`.
Workflow head `3d7f1770a3b8df0018008a49defe189db306de39`.
Successful GitHub CPU run `34908936464`, job `104191861049`.
Evidence checkpoint commit `9d3b17b392bd486753cb657318c048a7ae2460a7`.

V2.1 resolves the known retry/underlying-performance identity contradiction while leaving all downstream authorization false.

### Reference-blind structural audit V1 — PREREGISTRATION FROZEN / SYNTHETIC CI PASS

Preregistration commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`.
It consumes exactly four independent reference-side JSON byte streams plus expected SHA-256 identities and verifies hashes before parse. Evaluated DI/audio, model outputs, correctness matches and model-score data are forbidden. Frozen timing bound is `0.025 s`.

Implementation/test/workflow integration head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`.
GitHub CPU run `34912172056`, job `104201857367`, success.
Evidence checkpoint commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.

A structural PASS can establish only structural suitability of a real audited reference population; it never by itself authorizes Basic Pitch/V6/correctness.

### Real hardware / calibration necessity — TECHNICALLY REQUIRED, BUDGET-PAUSED

Necessity + bench-gate commit `a0279b8c48c51176678229abfa92576b1d1c0c95`.
Initial hardware document/API screen commit `39e9e0bb3667874534e6aa8cc4a8522299e0a140` found no complete off-the-shelf authoritative physical-reference qualifier.
Custom/hybrid topology commit `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf` separates clean evaluated DI, physical fret/contact truth, six raw per-string excitation channels, and common-clock sync. Its conceptual eight-channel layout is architecture only, not a current purchase plan.

### Budget constraint — SOFTWARE-ONLY ROUTE ACTIVE

Budget checkpoint commit `e7f0146d4f01605b642f8aeaa100962254b5ce58`.
Binding state:
- `HARDWARE_PROCUREMENT_PAUSED:true`
- `PAID_VENDOR_CONTACT_PAUSED:true`
- `PAID_PERFORMER_OR_STUDIO_WORK_PAUSED:true`
- `REAL_CALIBRATION_CAPTURE_PAUSED:true`
- `REAL_HOLDOUT_CAPTURE_PAUSED:true`
- `SOFTWARE_DOCUMENTATION_SYNTHETIC_CI_ALLOWED:true`

Earlier minimum-BOM purchase recommendation `9ddb612a7dbf1ad42210514728c4af604599142b` is planning history only and is operationally superseded by the budget boundary.

### Stage-0 contact replay V1 — SOFTWARE-ONLY SYNTHETIC CI PASS

Preregistration commit `c5082e8357e674f401bbc37fd42961e91e5d1606`.
Integration head `fdcad7bcb3f48dd75630b694f7b27d23b037f016`.
Implementation blob `14cd141aa21301887e1edf2a7d99a8dab0e43d58`.
Tests blob `956c518eef8e1ea2e1e87a42575e68dde6e636a0`; 16/16 local PASS.
Workflow blob `fd51102d34be8446eebec36ff65e5aa1a0e4afe7`.
Successful GitHub CPU run `34913326360`, job `104205441130`.
Evidence checkpoint commit `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.

This proves only software-contract behavior. It is not evidence that real physical sensing hardware works.

## NEXT ALLOWED ACTION — START HERE IN A FRESH CHAT

1. **Verify live branch + checkpoint first.** Re-fetch `songsterr-fresh-pipeline-v1` head and reread this file before mutation. Do not assume the head from a prior chat is still current.
2. **Freeze a train-only V2 preregistration before any new result is observed.** The next primary experiment should target session invariance for same-pitch physical-position discrimination using only already-exposed train sources `ele`, `eqm`, `eqm2`. The preregistration must specify the exact feature/normalization transformations, matching rule, metrics, and interpretation boundary before execution.
3. **Prefer small deterministic session-invariance changes, not a large learned model.** Good V2 candidates are source/session-level spectral-envelope normalization, robust per-harmonic normalization, log-spectral slope/relative harmonic-shape descriptors, attack/decay ratios, and deterministic per-source centering/scaling. Keep the exact labeled MIDI conditioning so the experiment remains about physical position rather than pitch recognition.
4. **Use train-only cross-session structure to avoid self-comparison.** The core comparison should remain cross-session (`eqm` <-> `eqm2`), with `ele` usable only as an already-exposed train diagnostic/domain-stress source. Do not redefine success after observing results.
5. **Keep `deb` and `ele_natural` completely untouched.** Do not load, stream, download, decode, inspect, feature-extract, listen to, score, debug against, tune on, or use either source for normalization/threshold/feature/model choices. They remain valuable reserved external sources for a later separately frozen decision.
6. **Implement V2 with synthetic contract tests first, then ordinary GitHub CPU CI.** Required tests should enforce train-only source access, pinned dataset revision, deterministic feature bytes/results, fail-closed metadata/integrity gates, exact same-MIDI candidate restriction, and all downstream authorization remaining false.
7. **Record the V2 train-only result in a dedicated checkpoint and update this canonical file.** Interpret it only as NON_HOLDOUT feasibility. Improvement or failure must not authorize Basic Pitch, V6, correctness, customer delivery, or access to the reserved sources.
8. **Secondary $0 line after V2:** build a deterministic synthetic six-channel crosstalk/debleed harness for already-separated per-string channels. Inject controlled bleed matrices, recover with frozen linear/regularized unmixing, quantify reconstruction error versus bleed level/conditioning, and preserve untouched raw synthetic channels. Do not claim this creates authoritative six-string truth from ordinary mono/stereo audio.
9. **Do not redesign the frozen V6/correctness gates because of feasibility results.** The purpose-built structural/capture/hardware contracts remain the prospective authority for eventual real validation.
10. **For any eventual real admitted holdout population, structural audit must precede correctness.** Any nonzero blocker makes the population structurally unsuitable; do not rescue it from evaluated audio. Exactly one official correctness run remains the eventual maximum after rights, reference, calibration, structural, population-binding and governance gates pass. No tuning/rerun after correctness exposure.
11. **Keep all closed lines closed unless explicitly reopened by the user.** Do not resume archived V143/Gomyway, GOAT/reference scoring, Guitar-TECHS rescue, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, or protected-song execution.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation + separate policy review; new validation-route hardware/performance/vendor/studio spending under the current budget; and any access to reserved Guitar Fretboard Notes `deb` or `ele_natural` before a later separately frozen authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and begin by rereading this file. The immediate task is **not** to touch holdout/correctness or the reserved Guitar Fretboard Notes sources. Start by freezing a train-only V2 session-invariance preregistration, then implement it with synthetic contract tests and ordinary GitHub CPU CI using only `ele`, `eqm`, and `eqm2`.

Current $0 evidence: Guitar Fretboard Notes train-only V1 was preregistered before audio access at commit `ff62869274bd509802f5c4b3e565422eb23741f3`; implementation/workflow head `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`; GitHub CPU run `34914789254`, job `104209961023`, SUCCESS; result checkpoint `535e6861bb9895f5c38161ec7877a6534cf6fa4e`. Pooled same-pitch exact physical-position accuracy was `53.68%` versus `39.71%` chance (`+13.97 pp`), with strong session asymmetry (`60.29%` one direction, `47.06%` reverse). Treat this only as NON_HOLDOUT feasibility evidence. Reserved `deb` and `ele_natural` remain untouched.

Purpose-built software gates remain: capture-manifest V2.1 CPU PASS run `34908936464`; structural-audit V1 synthetic CPU PASS run `34912172056`; Stage-0 contact replay synthetic CPU PASS run `34913326360`. The physical route remains hardware-paused by budget.

Keep `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration paused, Policy C `UNENROLLED`, protected-song execution embargoed. Do not reopen V143/Gomyway or GOAT/reference scoring unless separately explicit.
