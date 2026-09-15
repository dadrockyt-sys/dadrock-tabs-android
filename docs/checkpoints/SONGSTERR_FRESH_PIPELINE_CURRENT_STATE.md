# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — final derivation-replay population method frozen before implementation
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
- Synthetic/non-holdout evidence must never be represented as untouched external correctness validation.

## CURRENT AUTHORIZATION BOUNDARY

Still exactly:
- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## V6 — FROZEN / UNCHANGED

Authority: preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; implementation `3a6cbb144fec5613ab6350deb6539297d713df28`; scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; isolated-guitar DI; one-to-one matching onset <= `0.050 s`, pitch <= `50 cents`; >=1,000 pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=0.9900; strata >=100 positives require point precision >=0.9500; exactly one official correctness run after all upstream gates. Do not tune from holdout observations.

## CLOSED / RESERVED DATA LINES

- Guitar-TECHS remains frozen `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; result checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`. Never rescue/repair/score/rerun.
- Guitar Fretboard Notes train-only research remains non-holdout at pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`. Exposed train sources: `ele`, `eqm`, `eqm2`; reserved untouched: `deb`, `ele_natural`. V1 result `535e6861bb9895f5c38161ec7877a6534cf6fa4e`; V2 session-invariance result `4569a2f7970cde7975107146ba9ffb785066864b`, classification `MIXED`.

## PURPOSE-BUILT HOLDOUT — SOFTWARE LINEAGE FINAL GATE IN PROGRESS / PHYSICAL ROUTE BUDGET-PAUSED

Prospective design authority includes expanded design `e37d2b4662db949157d2cf4797370f05648b6940`, physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`, QA matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`, bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`, and topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Earlier synthetic software gates remain complete: Capture Manifest V2.1 `9d3b17b392bd486753cb657318c048a7ae2460a7`; Structural Audit V1 `df7eb9edacb170ab24e2c200b1c0a8028625f87a`; Stage-0 Contact Replay `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`; debleed `f233da0000188977334331c4614b6e541ae2490b`; hardware-marker clock map `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

## REFERENCE CALIBRATION PACKAGE PROVENANCE V1 — COMPLETE

Preregistration `cbd99714f655d859af2410374c3245a4afe6b056`; implementation `3dd1140650070342ab9fc4e177870fd39940a4e0`; official run `34916853723`, job `104216245975`, 20/20 tests PASS; result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`.

Frozen identities:
- result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`;
- decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Provenance V1 proves exact package/decoder file identity; it intentionally does not execute the decoder on admitted capture evidence.

## CAPTURE MANIFEST V2.2 — COMPLETE / SYNTHETIC PASS

Review `abfd10ea953e2be313f847f626c405a2f3607dad`; preregistration `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`; implementation `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`; run `34917541786`, job `104218329349`, 24/24 PASS; result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`.

## STRUCTURAL AUDIT V1.1 — COMPLETE / SYNTHETIC PASS

Review `66b1d3d19913e5218c3f1a71a88b399241ea5350`; preregistration `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`; correction `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`; implementation `5bf98194cdc2045c99903d3f9229443061deec2d`; run `34918145384`, job `104220137547`, 27/27 PASS; result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

V1.1 structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

## CAPTURE MANIFEST V2.3 STRUCTURAL-AUDIT INPUT BINDING — COMPLETE / SYNTHETIC PASS

Preregistration `c79fbd1d728a9d3dac86f036998108cb9765628e`; implementation `ae320ced78ebc5ce2cac15cc90a4564a9fa24502`; tests `b0af7344b71a4637087f5b112e4c239d4ac484cd`; workflow head `be814017f0ea4e4c89bb25824be66ff0bd63c6c7`.
Official run `34918802857`, job `104222117869`, 27/27 PASS; artifact `10376723782`; ZIP SHA `63559ef6c5c7bdca79a33c8a9e5bb754edb699e6d70a6bbfb499d3ad58d1b211`; result SHA `0d0372f1123468a9ae1fd90b9c830f233c33d2104e3dc76656fcb5d8147cdb08`; checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`.

V2.3 co-binds admitted raw pitch/birth evidence SHAs, decoded structural target SHAs, package binding, decoder configuration and attempt/population identity. It does not execute a decoder.

## STRUCTURAL AUDIT V1.2 CAPTURE-POPULATION BINDING — COMPLETE / SYNTHETIC PASS PER ATTEMPT

Result-byte review `866c673bc7728a8e0943eb45b0109910c28a36f6`; preregistration `617cdc71be4fea6ccdafec1aadf47c13d66726cb`; implementation `eacbb06adcbb9c2e4f7a2c5ed697c50a87c5c6ac`; tests `09aaccb6acac67c96e136ff57a298a39ce8107e8`; workflow head `a3ecef8cf9a827149f99e7af383b0d94957decb1`.
Official run `34919179891`, job `104223229264`, 35/35 PASS; artifact `10377581430`; ZIP SHA `1cb3fc511735d709603e3b336af6ec63bcb41e1e634297145cbc955838c0cb09`; result SHA `b9aece4790ce4fb9820b21187d551a4374636c341718f7ed75e10456c38a8145`; checkpoint `f4c63134f8b49723f342f5ba5f648498af317f73`.

Official synthetic attempt population SHA `43cba53b0ae925b39576081a30ed83a44146f56fd0a60cd30691121afbbae703`. V1.2 proves the actual decoded structural bytes match the V2.3-bound target identities for one admitted attempt and pass inherited structural/provenance rules. It does not consume the admitted raw pitch/birth evidence or execute the decoder.

## STRUCTURAL AUDIT POPULATION COMPLETENESS V1 — COMPLETE / SYNTHETIC MULTI-ATTEMPT PASS

Completeness review `9c85176001a62031299a036594f6d3273fb7b759`; preregistration `642f96898c209044c8f408ef473227fe4e9c4caa`; implementation `baeaf50ed3f4436d6be527009164052d1df813c1`; tests `4acb317af8cd69f0521cb2354c0dfef379c60ad2`; workflow head `3b3b530b5d8db0b5134db55ade494dc2487dd4d6`.
Official run `34920035528`, job `104225879209`, 37/37 PASS; artifact `10378040469`; ZIP SHA `c8ed38f5b78b8e24597ad6052a230d834ca49cfd90037faee02f6a3faaf5a339`; result SHA `d5cb80562141bd32302cf23caf3e53c8dab7b05115b98d92e078e030519cff4e`; result checkpoint `ad2d9405793f41c20c74328f3abddd22256c686b`.

Frozen official synthetic population:
- V2.3 result SHA `a63cfb41f9e2417c683cffbfaf8eaa908a872b669e0c2b626743d8909f13bd96`;
- V2.3 admitted-population SHA `e3a644eca442ae95af48c37d1b1aff4ad6f88e4ad2b9c32aac61468b9d3086bc`;
- exact admitted/verified count `2`;
- population structural completeness SHA `d920fa66aa7cca4c6a186690060b4335151caf906203dbd8bb2e048a75e66856`.

This closes exact all-admitted-attempt structural coverage. It still does not prove raw-evidence -> decoded-stream functional derivation.

## REFERENCE EVIDENCE DERIVATION REPLAY REVIEW — COMPLETE / FINAL FUNCTIONAL LINEAGE GAP CONFIRMED

Review checkpoint `0a50220a089f22733d7066e5772da7e73d71f557`.

Confirmed gap: current contracts can co-declare legitimate raw pitch/birth evidence hashes, legitimate package decoder identity, and arbitrary-but-structurally-valid decoded target stream hashes without ever proving that execution of that exact decoder on those exact raw bytes produces those targets.

Stage-0 Contact Replay V1 is not this proof: it is `NON_HOLDOUT_STAGE0` topology replay over configuration/fixture/scan-log bytes.

Decision: one final population-wide **Reference Evidence Derivation Replay Population V1** gate, not another per-attempt bridge plus another aggregator.

## REFERENCE EVIDENCE DERIVATION REPLAY POPULATION V1 — PREREGISTRATION FROZEN

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_EVIDENCE_DERIVATION_REPLAY_POPULATION_V1_PREREGISTRATION_2026-09-14.md`
commit `3aa4518bf1bc7b183f1e7025dbc1a4d182245db2`.

Frozen essentials:
- hash-before-parse verify successful V2.3, Structural Population Completeness V1 and Provenance V1 result bytes;
- verify exact Provenance-bound decoder code/configuration bytes before execution;
- exact executable Python decoder interface frozen before code: `python -I decoder.py --pitch-evidence ... --birth-evidence ... --configuration ... --pitch-latch-output ... --birth-output ...`;
- one fresh temp directory per admitted attempt; 10-second timeout; nonzero exit/missing/unreadable output fails closed;
- exact full V2.3 structural binding supplied for every admitted attempt and canonical binding SHA must match V2.3/completeness admitted set;
- actual raw pitch/birth evidence byte SHAs must equal binding raw-evidence identities before decoder execution;
- generated output bytes are hashed exactly without normalization; generated pitch-latch/birth SHA must equal binding target identities exactly;
- replay attempt set must equal full admitted V2.3/completeness set exactly;
- population replay identity binds V2.3 result/population, structural completeness result/identity, Provenance result/package, decoder code/config and all per-attempt raw/replayed identities;
- 38 synthetic contract test categories frozen;
- synthetic CI must build a **new executable synthetic decoder package** valid under unchanged Provenance V1; do not relabel the existing identity-only synthetic package fixture;
- at least two admitted attempts required in the official synthetic harness;
- all authorization remains false/zero even on PASS.

## IMMEDIATE NEXT ACTION

Implement Reference Evidence Derivation Replay Population V1 strictly against preregistration commit `3aa4518bf1bc7b183f1e7025dbc1a4d182245db2`: validator first, executable synthetic package/population fixture + 38-category tests before official harness, ordinary GitHub CPU tests-first workflow, result checkpoint, then final no-gap software-lineage review.

If the replay gate passes and the final review finds no concrete software gap, stop creating software gates. The next objectively necessary purpose-built route is physical procurement/calibration/capture, which remains budget-paused and unauthorized under `e7f0146d4f01605b642f8aeaa100962254b5ce58`.
