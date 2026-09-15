# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — repaired EGFxSet one-shot completed; runtime fixed; model emitted expected MIDI 40 plus extra MIDI 68; frozen smoke score FAIL
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other closed/revealed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched unless separately frozen authorization is created later.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; research/DSP tooling stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding: no new hardware/bench/interface/sensor/donor instrument/performer/studio/vendor/rights-package spending; real calibration and real holdout capture remain paused.
- Synthetic/non-holdout/smoke evidence must never be represented as untouched authoritative correctness validation.
- Do not create another purpose-built software-lineage gate unless a new, concrete, non-duplicative gap is first identified and documented.

## CURRENT GLOBAL AUTHORIZATION BOUNDARY — UNCHANGED

Still exactly:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The user's first scoped smoke authorization (`I authorize one set 💪💚`) was consumed by run `34935565328` and ended in a NumPy/TFLite runtime initialization failure before decoded output.

The user's subsequent explicit instruction `Please fix and rerun` authorized exactly one repaired, non-authorizing rerun of the same frozen candidate. That repaired authorization has now also been consumed by run `34936227380` attempt 1. It did not change any global authorization field.

## V6 — FROZEN / UNCHANGED

Authority: preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; implementation `3a6cbb144fec5613ab6350deb6539297d713df28`; scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; isolated-guitar DI; one-to-one matching onset <= `0.050 s`, pitch <= `50 cents`; >=1,000 pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=0.9900; strata >=100 positives require point precision >=0.9500; exactly one official correctness run after all upstream real gates. Do not tune from holdout observations.

Neither EGFxSet smoke attempt is the official correctness run. EGFxSet provides no independent onset truth for V6 onset-match scoring.

## CLOSED / RESERVED DATA LINES

- Guitar-TECHS remains frozen `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; result checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`. Never rescue/repair/score/rerun.
- Guitar Fretboard Notes train-only research remains non-holdout at pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`. Exposed train sources: `ele`, `eqm`, `eqm2`; reserved untouched: `deb`, `ele_natural`.
- Do not use archived V143/Gomyway, Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, or reserved GFN splits as a replacement for the EGFxSet smoke result.

## PURPOSE-BUILT HOLDOUT — SOFTWARE LINEAGE COMPLETE / PHYSICAL ROUTE BUDGET-PAUSED

Key physical design authority remains:

- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`
- QA matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`
- bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`
- topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`

Completed software-lineage chain includes:

- Capture Manifest V2.1 `9d3b17b392bd486753cb657318c048a7ae2460a7`
- Structural Audit V1 `df7eb9edacb170ab24e2c200b1c0a8028625f87a`
- Stage-0 Contact Replay `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`
- debleed `f233da0000188977334331c4614b6e541ae2490b`
- hardware-marker clock map `79293a7632915fc67f5b7ee0ac2242466ec83ea7`
- Reference Calibration Package Provenance V1 result `c57156fec7c5000563552c8cb128366956b8c95b`
- Capture Manifest V2.2 result `7d2d05ec365bbdb1aced574f7caf1865795fbc23`
- Structural Audit V1.1 result `96bb0aec9b02f16cb82ba78f16d3164af78474ec`
- Capture Manifest V2.3 result `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`
- Structural Audit V1.2 result `f4c63134f8b49723f342f5ba5f648498af317f73`
- Structural Audit Population Completeness V1 result `ad2d9405793f41c20c74328f3abddd22256c686b`
- Reference Evidence Derivation Replay Review `0a50220a089f22733d7066e5772da7e73d71f557`
- Reference Evidence Derivation Replay Population V1 result `e8f202c1a9ccee32a6f3883c06c79f89c4e77159`
- Final Software-Lineage No-Gap Review `docs/checkpoints/SONGSTERR_FRESH_FINAL_SOFTWARE_LINEAGE_NO_GAP_REVIEW_2026-09-14.md`, commit `54f25a793f66b4d9fe53f11c041122fdb41d057c`

Frozen conclusion remains:

**NO CONCRETE, NON-DUPLICATIVE SOFTWARE DECLARATION / SUBSTITUTION / POPULATION-COMPLETENESS / FUNCTIONAL-LINEAGE GAP REMAINS IN THE CURRENT PURPOSE-BUILT REFERENCE CONTRACT CHAIN.**

Hardware configuration / calibration / timing / sensor truth remains a physical qualification question, not another identified synthetic software gate.

## AUTHORITATIVE NEXT VALIDATION ROUTE — PHYSICAL, CURRENTLY PAUSED

The next authoritative route remains:

1. procure/assemble the frozen reference hardware/topology if budget authorization later permits;
2. perform frozen bench/hardware qualification and real calibration;
3. preserve exact package/raw/derived identities under the completed software contracts;
4. after legitimate real calibration authority, perform real holdout capture under frozen rules;
5. only after real structural gates pass may the separately frozen V6/correctness path be considered.

Under budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58`, physical procurement/calibration/capture remains paused and unauthorized.

## OPTIONAL $0 EGFxSET EXTERNAL SMOKE — FINAL CURRENT RESULT

### Candidate identity

- EGFxSet v1.0, Zenodo DOI `10.5281/zenodo.7044411`
- archive `Clean.zip`
- published archive MD5 `cdb1b401960f56becc8640387910e78a`
- member `Clean/Bridge/6-0.wav`
- exact member bytes `722976`
- exact member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- independent label: standard-tuned string 6, fret 0
- expected MIDI: `40` (E2)

### Original attempt — runtime failure only

Dedicated historical checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_PRE_MEDIA.md`

Original run:

- workflow `.github/workflows/songsterr-egfxset-one-shot.yml`
- workflow commit `9ee39e3daf462e4b15f9e72564a4a937a3424088`
- run `34935565328`
- job `104272581611`
- attempt `1`
- result checkpoint commit `e1223ab8a51f6df241840912f4783be71bf6c4b0`

Original failure cause: `basic-pitch==0.4.0` resolved to `numpy==2.2.6` plus `tflite-runtime==2.14.0`; TFLite was compiled against NumPy 1.x and failed at model initialization with `AttributeError: _ARRAY_API not found`. No decoded note output existed, so that attempt provided no pitch/position evidence.

### Repaired attempt — environment fixed prospectively

Pre-run repair freeze:
`docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_REPAIR_RERUN_PRE.md`
commit `779313c06382bd875fe314d798d149c4208b3141`.

Frozen repaired environment:

- Python `3.10.21`
- Basic Pitch `0.4.0`
- TFLite Runtime `2.14.0`
- NumPy `1.26.4`
- CPU only

No audio/model threshold or algorithm setting changed.

Repaired workflow:
`.github/workflows/songsterr-egfxset-repaired-one-shot.yml`
commit `b37d400b186a926985bb16b91702e2f88e55d785`.

Execution:

- run `34936227380`
- job `104274605954`
- attempt `1`
- artifact `10383413992`, `songsterr-egfxset-repaired-one-shot`
- artifact ZIP SHA-256 `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- result JSON SHA-256 `5f1f78c7c9bd153d98ad31854c29aa46c6a200a763fbf49292320752a9b239b9`
- primary Basic Pitch JSON SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`

All environment/media/runtime gates passed. `predictInvocationCount` is exactly `1`.

### Observed decoded output

Exactly two note events were emitted:

1. MIDI `40`, confidence `0.7906091809272766`, start `0.011609977324263039 s`, diagnostic end `4.948418140589569 s`. This maps uniquely to string 6 / fret 0 and matches the independent label.
2. MIDI `68`, confidence `0.3487236797809601`, start `0.3599092970521542 s`, diagnostic end `1.5325170068027212 s`. This is an extra emitted note and does not satisfy the frozen candidate truth.

MIDI histogram:

- `40`: 1
- `68`: 1

Complete emitted MIDI set: `{40,68}`.

### Frozen smoke score

The prospective scoring rule required all emitted MIDI values to equal exactly `{40}` and every event to resolve uniquely to string 6 / fret 0 / reconstructed MIDI 40.

Result:

- `PASS_RUNTIME`
- `FAIL_PITCH`
- `FAIL_POSITION`
- overall `FAIL_NON_AUTHORIZING_SMOKE`

Dedicated result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_REPAIR_RERUN_RESULT.md`
commit `3879231e9331b5771325de6715ed0839090875b8`.

### Interpretation constraint

This repaired result is a genuine one-file diagnostic model-output failure under the predeclared all-events rule. The expected E2/MIDI-40 note was recognized, but an additional MIDI-68 event prevents a PASS.

Do not drop the MIDI-68 event after observing it. Do not post-filter, tune thresholds, rerun, switch candidate, or claim the MIDI-40 event alone as a PASS under this contract.

This remains non-authoritative smoke evidence and is statistically insufficient for correctness claims. It does not alter V6/correctness/customer-delivery authority and does not replace the physical calibrated holdout.

## IMMEDIATE HANDOFF / NEXT ACTION

Re-fetch live branch head + this checkpoint before mutation.

The repaired EGFxSet authorization is consumed. There is **no authorized additional smoke inference, retry, threshold tuning, output filtering, or alternate-candidate run**.

Permitted non-execution work may analyze the extra MIDI-68 event from the already captured immutable artifact, provided it does not silently alter/drop event identity or convert this frozen FAIL into a PASS.

Any new inference experiment requires new explicit prospective user authorization and a frozen procedure before execution.

There is no authorized immediate purpose-built software-lineage implementation task. Do not manufacture another gate. Keep all global authorization fields false/zero, do not begin physical procurement/calibration/capture while budget-paused, and do not reopen V143/Gomyway or any other closed line unless the user explicitly asks.
