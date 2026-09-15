# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — structural population completeness closed; final raw-evidence derivation replay gap confirmed
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

Preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; implementation `3a6cbb144fec5613ab6350deb6539297d713df28`; scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; isolated-guitar DI; one-to-one onset <= `0.050 s`, pitch <= `50 cents`; >=1,000 pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=0.9900; strata >=100 positives require point precision >=0.9500; exactly one official correctness run after all gates.

## CLOSED / RESERVED DATA LINES

Guitar-TECHS remains frozen `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; result checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`. Do not rescue/repair/score/rerun.

Guitar Fretboard Notes train-only research remains non-holdout. Pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`; exposed train sources `ele`, `eqm`, `eqm2`; reserved untouched `deb` and `ele_natural`. V1 result checkpoint `535e6861bb9895f5c38161ec7877a6534cf6fa4e`; V2 session-invariance checkpoint `4569a2f7970cde7975107146ba9ffb785066864b`, frozen classification `MIXED`. Never access reserved sources without separately frozen authorization.

## PURPOSE-BUILT HOLDOUT — SOFTWARE LINEAGE NEAR-COMPLETE / PHYSICAL ROUTE BUDGET-PAUSED

Prospective authority includes expanded design `e37d2b4662db949157d2cf4797370f05648b6940`, physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`, QA matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`, bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`, and topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding: hardware procurement, paid vendor/performer/studio work, real calibration capture and real holdout capture are paused. Software/documentation/synthetic CI is allowed, but further software gates must be justified by an actual identified gap rather than invented activity.

Earlier synthetic software gates remain complete: Capture Manifest V2.1 checkpoint `9d3b17b392bd486753cb657318c048a7ae2460a7`; Structural Audit V1 checkpoint `df7eb9edacb170ab24e2c200b1c0a8028625f87a`; Stage-0 contact replay `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`; debleed `f233da0000188977334331c4614b6e541ae2490b`; hardware-marker clock map `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

## REFERENCE CALIBRATION PACKAGE PROVENANCE V1 — COMPLETE

Preregistration `cbd99714f655d859af2410374c3245a4afe6b056`; implementation `3dd1140650070342ab9fc4e177870fd39940a4e0`; clean run `34916853723`, job `104216245975`, 20/20 tests PASS.
Result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`; result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`; package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`; decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Provenance V1 proves exact package/decoder code/configuration file identity. It does not execute the decoder on admitted capture evidence.

## CAPTURE MANIFEST V2.2 — COMPLETE / SYNTHETIC PASS

Review `abfd10ea953e2be313f847f626c405a2f3607dad`; preregistration `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`; implementation `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`; run `34917541786`, job `104218329349`, 24/24 tests PASS; result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`.

## STRUCTURAL AUDIT V1.1 — COMPLETE / SYNTHETIC PASS

Review `66b1d3d19913e5218c3f1a71a88b399241ea5350`; preregistration `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`; correction `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`; implementation `5bf98194cdc2045c99903d3f9229443061deec2d`; run `34918145384`, job `104220137547`, 27/27 tests PASS; result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.
V1.1 structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

## CAPTURE MANIFEST V2.3 STRUCTURAL-AUDIT INPUT BINDING — COMPLETE / SYNTHETIC PASS

Preregistration `c79fbd1d728a9d3dac86f036998108cb9765628e`; implementation `ae320ced78ebc5ce2cac15cc90a4564a9fa24502`; tests `b0af7344b71a4637087f5b112e4c239d4ac484cd`; workflow head `be814017f0ea4e4c89bb25824be66ff0bd63c6c7`.
Official run `34918802857`, job `104222117869`, SUCCESS; 27/27 tests PASS. Artifact `10376723782`; ZIP SHA `63559ef6c5c7bdca79a33c8a9e5bb754edb699e6d70a6bbfb499d3ad58d1b211`; result SHA `0d0372f1123468a9ae1fd90b9c830f233c33d2104e3dc76656fcb5d8147cdb08`; result checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`.

V2.3 co-binds admitted raw `pitchEvidenceSha256` / `birthEvidenceSha256` identities with future decoded `pitchLatchStreamSha256` / `birthStreamSha256` identities and package/decoder lineage, but intentionally does not execute a decoder.

## STRUCTURAL AUDIT V1.2 CAPTURE-POPULATION BINDING — COMPLETE / SYNTHETIC PASS PER ATTEMPT

Result-byte review `866c673bc7728a8e0943eb45b0109910c28a36f6`; preregistration `617cdc71be4fea6ccdafec1aadf47c13d66726cb`.
Implementation `eacbb06adcbb9c2e4f7a2c5ed697c50a87c5c6ac`, blob `4a52046103ea328259c891c327ab9a12d72f23ee`.
Tests `09aaccb6acac67c96e136ff57a298a39ce8107e8`, blob `fa16515c9a9772e59990f8112814b08b83f8d3b2`.
Workflow head `a3ecef8cf9a827149f99e7af383b0d94957decb1`, blob `cdd295d8b6b40c7500e5a7280c5e6754c273a5d3`.
Official run `34919179891`, job `104223229264`, SUCCESS; 35/35 tests PASS first.
Artifact `10377581430`, size `1,848` bytes; ZIP SHA `1cb3fc511735d709603e3b336af6ec63bcb41e1e634297145cbc955838c0cb09`; result SHA `b9aece4790ce4fb9820b21187d551a4374636c341718f7ed75e10456c38a8145`; result checkpoint `f4c63134f8b49723f342f5ba5f648498af317f73`.

Frozen official synthetic attempt chain:
- admitted attempt `slot-1-attempt-2`, slot `slot-1`, underlying performance `performance-1`;
- structural binding SHA `f590833680769034a7c5e9fc6efb5b0f21e67249c6c77c4ad2ee7b6eae1c5fff`;
- V2.3 validation-result SHA `6b57317d28098fbc2c8f26c30ba9ccdc8f2173b67940d3696557a7861acf8126`;
- V2.3 admitted-population SHA `85a3fb6c56e46b001fd752c6f128a5264e477f7d1b9b9a89a8cf6542d0aa267d`;
- Provenance V1 result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`;
- package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`;
- decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`;
- inherited V1.1 structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`;
- final V1.2 per-attempt population SHA `43cba53b0ae925b39576081a30ed83a44146f56fd0a60cd30691121afbbae703`;
- `capturePopulationBindingViolationCount:0`.

V1.2 closes per-attempt decoded-byte substitution: actual decoded structural streams must carry exactly the V2.3-bound identities. It does not consume the admitted raw pitch/birth evidence bytes or execute the package decoder.

## STRUCTURAL AUDIT POPULATION COMPLETENESS V1 — COMPLETE / SYNTHETIC MULTI-ATTEMPT PASS

Completeness review `9c85176001a62031299a036594f6d3273fb7b759`; preregistration `642f96898c209044c8f408ef473227fe4e9c4caa`.
Implementation `baeaf50ed3f4436d6be527009164052d1df813c1`, blob `afcdda31509260ffbb936f8dae8b69958ad0d48c`.
Tests `4acb317af8cd69f0521cb2354c0dfef379c60ad2`, blob `cda5d6793d28df4301639c6e662273c280635638`.
Workflow head `3b3b530b5d8db0b5134db55ade494dc2487dd4d6`, blob `f41a795208c79dcc89162f2d5251335664a98802`.
Official run `34920035528`, job `104225879209`, SUCCESS; 37/37 tests PASS before official harness.
Artifact `10378040469`, size `1,161` bytes; ZIP SHA `c8ed38f5b78b8e24597ad6052a230d834ca49cfd90037faee02f6a3faaf5a339`; result SHA `d5cb80562141bd32302cf23caf3e53c8dab7b05115b98d92e078e030519cff4e`; result checkpoint `ad2d9405793f41c20c74328f3abddd22256c686b`.

Frozen official synthetic population:
- V2.3 validation-result SHA `a63cfb41f9e2417c683cffbfaf8eaa908a872b669e0c2b626743d8909f13bd96`;
- V2.3 admitted-population SHA `e3a644eca442ae95af48c37d1b1aff4ad6f88e4ad2b9c32aac61468b9d3086bc`;
- exact admitted and verified V1.2 set count `2`;
- attempt `slot-1-attempt-2`: binding SHA `f590833680769034a7c5e9fc6efb5b0f21e67249c6c77c4ad2ee7b6eae1c5fff`, V1.2 result SHA `5370e7e4a1ef0ac09a0dab689f205668e258c47139c92866efb9a307513e685b`, V1.2 derived population SHA `2d3268930e26649e25457cd95196cf226b0f224f4c861d847052b331ba9c9df3`;
- attempt `slot-2-attempt-1`: binding SHA `9bec537222e4b3150717d2c8d4f92fb73f512f6575fdfd052c06a060ef6950fc`, V1.2 result SHA `20f3f19cd98ab316ccd48a71515a3835404a76b6500ce1870d895b97f592af2c`, V1.2 derived population SHA `31e8c210acbfc58932220a2d2d2aa843cf9ebef5f3c592a1cc7b9bc061b7d3c2`;
- population structural completeness SHA `d920fa66aa7cca4c6a186690060b4335151caf906203dbd8bb2e048a75e66856`;
- `populationStructurallySuitable:true` and `populationStructuralCompletenessEstablished:true` for synthetic fixture only.

This closes all-admitted-attempt structural-audit coverage/completeness. It does not prove functional raw-evidence decoding.

## REFERENCE EVIDENCE DERIVATION REPLAY REVIEW — COMPLETE / FINAL FUNCTIONAL LINEAGE GAP CONFIRMED

Review checkpoint `0a50220a089f22733d7066e5772da7e73d71f557`.

Confirmed gap: the chain currently proves which decoder code/configuration is authoritative, co-declares raw evidence and decoded target SHAs, verifies the actual decoded bytes, and verifies all admitted attempts were audited. It does **not** execute the exact package-bound decoder on each admitted raw pitch/birth evidence pair and require the generated `pitchLatch` / `birth` byte hashes to equal the V2.3 targets.

Stage-0 Contact Replay V1 does not close this gap: it is `NON_HOLDOUT_STAGE0` topology replay over configuration/fixture/scan-log bytes, not admitted pitch/birth evidence derivation.

Decision: add one final **Reference Evidence Derivation Replay Population V1** gate, population-wide rather than another per-attempt bridge + aggregator. It should hash-before-parse verify V2.3, Population Completeness V1 and Provenance V1 results; verify exact decoder code/config bytes; verify each full V2.3 structural binding and raw pitch/birth evidence byte identity; execute the frozen decoder interface for every admitted attempt; and require exact output SHA equality to each binding's `pitchLatchStreamSha256` / `birthStreamSha256`.

The replay preregistration must freeze the decoder runtime interface before implementation. Synthetic CI must use a new executable synthetic decoder/package valid under the unchanged Provenance V1 contract; do not pretend the existing identity-only synthetic decoder fixture is executable.

If this replay gate passes and a final no-gap review finds no concrete remaining software lineage gap, stop creating software gates. The next objectively necessary route is physical procurement/calibration/capture and remains budget-paused/unauthorized.

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

Reserved GFN `deb` / `ele_natural` remain untouched. Archived V143/Gomyway remains closed.

## IMMEDIATE NEXT ACTION

Freeze `Reference Evidence Derivation Replay Population V1` preregistration before code, including the exact executable decoder interface and population-level cross-bindings described in review commit `0a50220a089f22733d7066e5772da7e73d71f557`. Then implement tests-first synthetic CI with an executable synthetic decoder package and at least two admitted attempts. Freeze result identities and perform the final software-lineage no-gap review. Do not begin real calibration/capture, do not open correctness/Basic Pitch/V6, do not access reserved GFN sources, and do not reopen V143/Gomyway unless explicitly asked.
