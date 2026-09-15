# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — Capture Manifest V2.3 complete; Structural Audit V1.2 capture-population binding preregistered before implementation
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other closed/revealed lines remain closed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `realCalibrationAuthorized:false`, `realHoldoutCaptureAuthorized:false`, `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`.
- Budget remains effectively limited to existing Vercel/model costs. No new hardware, bench equipment, interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or paid acquisition may be assumed.
- Synthetic/non-holdout evidence must never be presented as untouched external correctness validation.

## V6 — FROZEN

Method preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; implementation `3a6cbb144fec5613ab6350deb6539297d713df28`; scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; isolated-guitar DI; one-to-one onset <= `0.050 s`, pitch <= `50 cents`; >=1,000 pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=0.9900; strata >=100 positives require point precision >=0.9500; exactly one official correctness run after all gates.

## CLOSED / RESERVED DATA LINES

Guitar-TECHS is frozen `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`. Do not rescue/repair/score/rerun.

Guitar Fretboard Notes train-only research remains non-holdout. Pinned dataset revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`; exposed train sources `ele`, `eqm`, `eqm2`; reserved untouched `deb` and `ele_natural`. V1 result checkpoint `535e6861bb9895f5c38161ec7877a6534cf6fa4e`; V2 session-invariance checkpoint `4569a2f7970cde7975107146ba9ffb785066864b`, frozen classification `MIXED`. Never access reserved sources without separately frozen authorization.

## PURPOSE-BUILT HOLDOUT — SOFTWARE ACTIVE / PHYSICAL ROUTE BUDGET-PAUSED

Prospective authority includes expanded design `e37d2b4662db949157d2cf4797370f05648b6940`, physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`, QA matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`, bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`, and topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding: hardware procurement, paid vendor/performer/studio work, real calibration capture and real holdout capture are paused; software/documentation/synthetic CI is allowed.

Earlier synthetic software gates remain completed: Capture Manifest V2.1 checkpoint `9d3b17b392bd486753cb657318c048a7ae2460a7`; Structural Audit V1 checkpoint `df7eb9edacb170ab24e2c200b1c0a8028625f87a`; Stage-0 replay checkpoint `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`; debleed checkpoint `f233da0000188977334331c4614b6e541ae2490b`; hardware-marker clock map checkpoint `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

## REFERENCE CALIBRATION PACKAGE PROVENANCE V1 — COMPLETE

Preregistration `cbd99714f655d859af2410374c3245a4afe6b056`; implementation `3dd1140650070342ab9fc4e177870fd39940a4e0`; clean run `34916853723`, job `104216245975`, 20/20 tests PASS.

Frozen result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`; result JSON SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`; canonical package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`; decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Package-level decoder/configuration identity is closed; do not create a duplicate standalone decoder contract.

## CAPTURE MANIFEST V2.2 — COMPLETE / SYNTHETIC PASS

Bridge review `abfd10ea953e2be313f847f626c405a2f3607dad`; preregistration `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`; accepted implementation `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`.

Official run `34917541786`, job `104218329349`, 24/24 tests PASS. Result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`. V2.2 links admitted references/population identity to the canonical calibration package/provenance/decoder identity but does not open provenance-result bytes itself.

## STRUCTURAL AUDIT V1.1 — COMPLETE / SYNTHETIC PASS

Provenance-result bridge review `66b1d3d19913e5218c3f1a71a88b399241ea5350`; preregistration `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`; pre-implementation contract-literal correction `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`.

Implementation `5bf98194cdc2045c99903d3f9229443061deec2d`; official run `34918145384`, job `104220137547`, 27/27 tests PASS. Result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`; V1.1 augmented structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

V1.1 hash-verifies the Provenance V1 result before parse and binds package identity into structural population identity while preserving all original V1 structural rules.

## END-TO-END IDENTITY REVIEW — COMPLETE

Review checkpoint `e3e1759b576831128ff0b95ee237b6d131a2fe51` confirmed the remaining decisive gap: V1.1's exact four structural streams were not bound to the same admitted V2.2 performance/population. Name-only hardware/calibration comparisons were insufficient.

Decision: Capture Manifest V2.3 must first bind exact future structural input bytes per admitted performance; Structural Audit V1.2 may then verify actual bytes against that binding and admitted population.

## CAPTURE MANIFEST V2.3 STRUCTURAL-AUDIT INPUT BINDING — COMPLETE / SYNTHETIC PASS

Preregistration `c79fbd1d728a9d3dac86f036998108cb9765628e`.
Implementation `ae320ced78ebc5ce2cac15cc90a4564a9fa24502`, blob `3c67cf14dd7b34239307e72deca992b6adcb712f`.
Tests `b0af7344b71a4637087f5b112e4c239d4ac484cd`, blob `48b13284c191c3fb36657c787a2efa84fea4bbcc`.
Workflow head `be814017f0ea4e4c89bb25824be66ff0bd63c6c7`, blob `236f571a2cf52d53e3e742abfcb42b7404f1dfb0`.

Official run `34918802857`, job `104222117869`, SUCCESS; 27/27 tests PASS first.
Artifact `10376723782`, ZIP SHA `63559ef6c5c7bdca79a33c8a9e5bb754edb699e6d70a6bbfb499d3ad58d1b211`; result JSON SHA `0d0372f1123468a9ae1fd90b9c830f233c33d2104e3dc76656fcb5d8147cdb08`; result checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`.

Frozen synthetic identities:
- admitted attempt `slot-1-attempt-2`;
- structural binding SHA `8e0b3bdc1b356f5e31f8872cf0b72c10375d67b6cc18dc87ce9ddeac2077cd45`;
- inherited V2.2 population SHA `598c6bf2b0e092c73cbce7d27c7f9ae4ce162edc2d7efced6ff10bd6afebf60c`;
- V2.3 population SHA `8d4053d89597c94ea9d87fd11867c6f15faa4678e9ba56158682d99fa9fdf60d`;
- package binding SHA remains `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`;
- decoder configuration SHA remains `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

V2.3 now makes each admitted capture population commit to exact future structural-audit source hashes plus admitted-performance/configuration/calibration/setup/clock/evidence/package/decoder lineage. It does not verify those future structural bytes.

## STRUCTURAL AUDIT V1.2 RESULT-BYTE REVIEW — COMPLETE

Review commit `866c673bc7728a8e0943eb45b0109910c28a36f6` concluded metadata-only handoff is insufficient. V1.2 must hash-before-parse verify the exact successful V2.3 validation-result bytes, then verify the supplied full admitted structural binding is the binding hash referenced by that result.

This prevents a final substitution between a valid V2.3 capture declaration and the structural audit.

## STRUCTURAL AUDIT V1.2 CAPTURE-POPULATION BINDING — PREREGISTRATION FROZEN

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_V1_2_CAPTURE_POPULATION_BINDING_PREREGISTRATION_2026-09-14.md`
commit `617cdc71be4fea6ccdafec1aadf47c13d66726cb`.

Frozen V1.2 essentials:
- additive wrapper over V1.1; all V1/V1.1 source/timing/MIDI/overlap/provenance blockers unchanged;
- hash-before-parse verify exact V2.3 validation-result bytes;
- require V2.3 `contractValid:true`, `errors:[]`, `v23SemanticGuardPassed:true`, and `mayAdvanceToReferenceBlindStructuralAudit:true`;
- canonical-hash supplied full `structuralAuditInputs` and require its hash to be the audited attempt's binding hash in the verified V2.3 result;
- require verified V2.3 population SHA, provenance-result SHA, package-binding SHA and decoder-configuration SHA to agree with V1.1;
- compare all four actual V1.1 structural source hashes to V2.3 binding hashes;
- compare parsed structural configuration ID, calibration ID, exact tuning, event semantics and clock sync ID to the V2.3 binding;
- preserve V1.1 population SHA and compute V1.2 population SHA over V1.1 population + verified V2.3 result SHA + V2.3 population SHA + admitted attempt/slot/underlying-performance + structural binding SHA;
- expose upstream configuration/setup SHA lineage without inventing absent SHA fields inside the V1 structural hardware schema;
- add only `capturePopulationBindingViolationCount`;
- 35 frozen synthetic test categories before official harness;
- all downstream authorization remains false/zero.

## IMMEDIATE NEXT ACTION

Implement the already-frozen Structural Audit V1.2 contract at preregistration commit `617cdc71be4fea6ccdafec1aadf47c13d66726cb` as an additive wrapper over V1.1. Add all synthetic tests before official harness execution, add ordinary GitHub CPU workflow with tests first, freeze result identities, and update this checkpoint again.

Do not begin real calibration/holdout capture, do not alter frozen physical/V6/correctness thresholds, do not access reserved GFN sources, and do not reopen archived V143/Gomyway or other closed lines unless explicitly asked.
