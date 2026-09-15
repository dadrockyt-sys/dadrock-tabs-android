# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — train-only V2 session-invariance method frozen before V2 result execution
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
- Budget remains effectively limited to existing Vercel/model costs. No new hardware, bench equipment, audio interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or paid acquisition may be assumed.
- Do not weaken validation standards to fit budget. Synthetic/non-holdout evidence must never be represented as untouched external correctness validation.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve each decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance matching with onset <= `0.050 s` and pitch <= `50 cents`; V6-positive precision uses one-sided 95% Wilson lower bound; >=`1,000` pooled V6-positive estimates; pooled Wilson LB >=`0.9900`; strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.

Reverified evidence: 104 DI/MIDI pairs, 18,934 reference events, all 104 alignment statuses `OK`; 5 same-key overlaps + 7 unmatched note-ons; frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run on Guitar-TECHS. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all five must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after structural PASS may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

No currently reviewed public candidate clears all five gates.

## ZERO-COST EXTERNAL-CORPUS RESEARCH — GUITAR FRETBOARD NOTES

Dataset: `collegefishiesd/guitar-fretboard-notes`.
Pinned revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`.
Declared license: `CC-BY-SA-4.0`.

This corpus is NON_HOLDOUT feasibility research only. It contains isolated real-guitar notes labeled by exact physical string and fret and can probe whether timbre contains repeatable physical-position information. It is not an admissible Songsterr Fresh correctness holdout.

### Frozen source boundary

Already-exposed `train` only:
- `ele`: 78 rows;
- `eqm`: 78 rows;
- `eqm2`: 78 rows;
- total: 234 rows.

Reserved and untouched:
- `test`, source `deb`: 78 rows;
- `validation`, source `ele_natural`: 78 rows.

Do not load, stream, download, decode, inspect, feature-extract, listen to, score, debug against, tune on, normalize from, or otherwise consume `deb` or `ele_natural` without a later separate preregistration frozen before access.

Canonical pinned train parquet SHA-256 observed in V1: `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`.

### Train-only V1 — COMPLETE / NON_HOLDOUT

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_DISCRIMINABILITY_PREREGISTRATION_V1_2026-09-14.md`
commit `ff62869274bd509802f5c4b3e565422eb23741f3`.

Implementation/test/workflow integration head: `7ab93ec73848b9f0fee366cbf19f1dc13b39930f`.
GitHub CPU run `34914789254`, job `104209961023`, SUCCESS.
Canonical artifact ID `10375479293`, uploaded ZIP SHA-256 `580b08c329459b94e6a000c51f66dc59cabc893f642d6713f9e8bf55d35e57ec`.
Result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_DISCRIMINABILITY_RESULT_V1_2026-09-14.md`, commit `535e6861bb9895f5c38161ec7877a6534cf6fa4e`.

V1 frozen result:
- `eqm` -> `eqm2`: 68 eligible, 41 correct, accuracy `60.29%`;
- `eqm2` -> `eqm`: 68 eligible, 32 correct, accuracy `47.06%`;
- pooled: 136 eligible, 73 correct, accuracy `53.68%`;
- pooled chance baseline `39.71%`;
- pooled lift `+13.97` percentage points;
- absolute directional gap `13.24` percentage points.

Interpretation remains limited: repeatable physical-position information exists above chance in these isolated-note train recordings under the frozen V1 method, but the directional asymmetry is material and indicates substantial session sensitivity. This says nothing authoritative about chords, simultaneous same-pitch notes, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, full-song audio, noisy deployment audio, or frozen V6 correctness.

### Train-only V2 session-invariance — PREREGISTRATION FROZEN / IMPLEMENTATION NEXT

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_FRETBOARD_NOTES_TRAIN_ONLY_SESSION_INVARIANCE_PREREGISTRATION_V2_2026-09-14.md`
commit `e528ebd1279ec883da0b786d73dd25e03aa47890`.

V2 was frozen before any V2 real-audio result execution or observation.

Frozen V2 method:
- same pinned dataset revision and train-only source boundary as V1;
- exact train parquet SHA-256 must match the V1 canonical SHA before extraction;
- exact V1 16-D per-row feature extraction is retained to isolate normalization effect;
- per-source robust normalization is independent for `ele`, `eqm`, `eqm2` using median and `1.4826 * MAD` per feature over all 78 rows of that source;
- if robust scale is non-finite or `<1e-9`, fallback is source population standard deviation; if still non-finite or `<1e-9`, scale `1.0`;
- normalized row = `(x - source_median) / source_scale`;
- primary matching remains exact labeled-MIDI candidates only, ordinary Euclidean distance, deterministic `(string,fret)` tie-break;
- primary directions remain `eqm` -> `eqm2` and reverse;
- frozen `ele` diagnostic/domain-stress directions are `eqm` -> `ele`, `ele` -> `eqm`, `eqm2` -> `ele`, `ele` -> `eqm2` and cannot enter primary pooled metrics;
- V2 explicitly permits train-only transductive query-source distribution normalization and therefore must never be described as untouched validation.

Frozen descriptive interpretation rule relative to V1:
- `SESSION_INVARIANCE_IMPROVED` only if pooled V2 accuracy is strictly greater than `0.5367647058823529` **and** V2 absolute directional gap is strictly less than `0.13235294117647056`;
- `MIXED` if exactly one condition improves;
- `NO_IMPROVEMENT` if neither improves;
- equality does not count as improvement.

There is no production PASS threshold. Every V2 outcome remains NON_HOLDOUT descriptive feasibility only.

Next mandatory V2 order:
1. implement the frozen contract without altering it;
2. add synthetic contract tests before any real V2 result execution;
3. tests must enforce pinned revision, exact train-only/allowed/reserved source boundaries, train SHA gate, deterministic 16-D extraction, source-wise median/MAD normalization and fallbacks, order independence, exact same-MIDI candidate restriction, deterministic tie-break, fixed primary directions, isolation of `ele` diagnostics, canonical JSON determinism, and downstream authorization remaining false/zero;
4. run ordinary GitHub CPU CI only after implementation/tests/workflow are committed;
5. record the real train-only V2 result in a dedicated checkpoint;
6. update this canonical checkpoint with immutable run/job/artifact/result identities and interpretation.

All downstream authorization remains closed during and after V2 unless separately authorized by a future admissible process:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## PURPOSE-BUILT HOLDOUT — SOFTWARE ACTIVE, PHYSICAL ROUTE BUDGET-PAUSED

The purpose-built independent-sensor route remains the technically authoritative prospective validation design, but under the current budget it may advance only through zero-additional-cost software/documentation/synthetic CI. Real hardware procurement, non-holdout physical calibration and real holdout capture remain paused.

Design authority:
- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture QA/gate matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`.

Capture-manifest V2.1:
- implementation commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`;
- tests commit `ff5717a4aeb9b74e971694703f6d6cb785389845`;
- workflow head `3d7f1770a3b8df0018008a49defe189db306de39`;
- successful GitHub CPU run `34908936464`, job `104191861049`;
- evidence checkpoint commit `9d3b17b392bd486753cb657318c048a7ae2460a7`.

Reference-blind structural audit V1:
- preregistration commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`;
- implementation/test/workflow head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`;
- successful GitHub CPU run `34912172056`, job `104201857367`;
- evidence checkpoint commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.

A structural PASS establishes only structural suitability of a real audited reference population; it never authorizes Basic Pitch/V6/correctness by itself.

Hardware/calibration necessity and topology:
- necessity + bench-gate commit `a0279b8c48c51176678229abfa92576b1d1c0c95`;
- initial hardware document/API screen commit `39e9e0bb3667874534e6aa8cc4a8522299e0a140`;
- custom/hybrid topology commit `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Budget checkpoint commit `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding:
- `HARDWARE_PROCUREMENT_PAUSED:true`
- `PAID_VENDOR_CONTACT_PAUSED:true`
- `PAID_PERFORMER_OR_STUDIO_WORK_PAUSED:true`
- `REAL_CALIBRATION_CAPTURE_PAUSED:true`
- `REAL_HOLDOUT_CAPTURE_PAUSED:true`
- `SOFTWARE_DOCUMENTATION_SYNTHETIC_CI_ALLOWED:true`

Earlier minimum-BOM purchase recommendation `9ddb612a7dbf1ad42210514728c4af604599142b` is planning history only and operationally superseded by the budget boundary.

Stage-0 contact replay V1:
- preregistration commit `c5082e8357e674f401bbc37fd42961e91e5d1606`;
- integration head `fdcad7bcb3f48dd75630b694f7b27d23b037f016`;
- implementation blob `14cd141aa21301887e1edf2a7d99a8dab0e43d58`;
- tests blob `956c518eef8e1ea2e1e87a42575e68dde6e636a0`; 16/16 local PASS;
- workflow blob `fd51102d34be8446eebec36ff65e5aa1a0e4afe7`;
- successful GitHub CPU run `34913326360`, job `104205441130`;
- evidence checkpoint commit `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.

This proves only software-contract behavior, not real physical sensing performance.

## SECONDARY $0 LINE AFTER V2

Only after V2 is recorded, the next allowed secondary software-only line is a deterministic synthetic six-channel crosstalk/debleed harness for already-separated per-string channels. Inject controlled bleed matrices, recover with frozen linear/regularized unmixing, quantify reconstruction error versus bleed level/conditioning, and preserve untouched raw synthetic channels. Do not claim this creates authoritative six-string truth from ordinary mono/stereo audio.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation plus separate policy review; new validation-route hardware/performance/vendor/studio spending under the current budget; and any access to reserved Guitar Fretboard Notes `deb` or `ele_natural` before a later separately frozen authorization.

## FRESH-CHAT HANDOFF / IMMEDIATE NEXT ACTION

Continue only on `songsterr-fresh-pipeline-v1` and re-fetch the live branch head plus this file before mutation.

Immediate task: implement the already-frozen Guitar Fretboard Notes train-only V2 session-invariance contract at preregistration commit `e528ebd1279ec883da0b786d73dd25e03aa47890`, add synthetic contract tests first, then ordinary GitHub CPU CI. Use only `ele`, `eqm`, and `eqm2`. Keep `deb` and `ele_natural` untouched. Do not modify the frozen V2 method based on any observed V2 result.

Do not reopen archived V143/Gomyway or any other closed line unless the user explicitly asks.
