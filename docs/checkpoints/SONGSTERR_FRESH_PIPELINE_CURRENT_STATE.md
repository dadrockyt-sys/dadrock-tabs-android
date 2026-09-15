# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — end-to-end review confirms per-admitted-performance structural-input identity gap; Capture Manifest V2.3 is next
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS rescue/correctness, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution and other explicitly closed/revealed lines remain closed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `realCalibrationAuthorized:false`, `realHoldoutCaptureAuthorized:false`, `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration paused, Policy C `UNENROLLED`, protected-song execution embargoed.
- Budget remains effectively limited to existing Vercel/model costs. No new hardware, bench equipment, audio interfaces, sensors, donor instruments, performers, studios, vendors, rights packages, or paid acquisition may be assumed.
- Synthetic/non-holdout evidence must never be presented as untouched external correctness validation.

## V6 — FROZEN

Preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; implementation `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`; scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials remain unchanged: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve each decoded event and selected integer MIDI exactly once; isolated-guitar DI; one-to-one matching onset <= `0.050 s`, pitch <= `50 cents`; >=`1,000` pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=`0.9900`; strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal; exactly one official correctness run.

Do not alter V6 method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C

Result checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`; official audit run `34754519541`, job `103716527380`, artifact `10317695640`, head `f3c9d4a88740146918c34a3538c565f21079f3bf`.
Frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`. Basic Pitch/V6/correctness were never run. Do not rescue, repair, score, bind, or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all five must be defensible: usable/permissive validation rights; real guitar; immutable independent note-level onset+pitch truth not reconstructed from evaluated audio; plausible >=1,000 V6-positive capacity without duplicate/effect inflation; defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after structural PASS may immutable population identities be bound and exactly one ordinary-GitHub-CPU correctness run occur. No tuning/rerun after correctness exposure.

No currently reviewed public candidate clears all five gates.

## GUITAR FRETBOARD NOTES — NON_HOLDOUT TRAIN-ONLY RESEARCH

Dataset `collegefishiesd/guitar-fretboard-notes`, pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`, declared `CC-BY-SA-4.0`.
Allowed exposed train sources: `ele`, `eqm`, `eqm2`, 78 rows each, 234 total.
Reserved untouched: `deb` (`test`) and `ele_natural` (`validation`), 78 rows each.
Canonical train parquet SHA `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`.
Do not access reserved sources without a later separately frozen authorization.

V1 complete: prereg `ff62869274bd509802f5c4b3e565422eb23741f3`; run `34914789254`, job `104209961023`; result checkpoint `535e6861bb9895f5c38161ec7877a6534cf6fa4e`; pooled accuracy `53.68%` vs `39.71%` chance.

V2 session-invariance complete/frozen `MIXED`: prereg `e528ebd1279ec883da0b786d73dd25e03aa47890`; run `34915518842`, job `104212166273`, 18/18 tests PASS; result checkpoint `4569a2f7970cde7975107146ba9ffb785066864b`; pooled `50.74%`, directional gap `4.41 pp`. No post-result tuning/rerun. Reserved sources remain untouched.

## PURPOSE-BUILT HOLDOUT — SOFTWARE ACTIVE / PHYSICAL ROUTE BUDGET-PAUSED

Prospective authority:
- expanded design `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture QA/gate matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`;
- hardware/calibration necessity + bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`;
- custom/hybrid topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Capture-manifest V2.1 synthetic PASS: run `34908936464`, job `104191861049`, checkpoint `9d3b17b392bd486753cb657318c048a7ae2460a7`.
Structural audit V1 synthetic PASS: prereg `067875e3aa1538ff5483b74cc9071b00e9e82b07`; run `34912172056`, job `104201857367`, checkpoint `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.
Stage-0 contact replay V1 synthetic PASS: run `34913326360`, job `104205441130`, checkpoint `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.
Debleed V1 synthetic PASS: run `34915944228`, job `104213442029`, checkpoint `f233da0000188977334331c4614b6e541ae2490b`.
Hardware-marker clock map V1 synthetic PASS: run `34916421318`, job `104214912711`, checkpoint `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding: hardware procurement, paid vendor/performer/studio work, real calibration capture and real holdout capture are paused; software/documentation/synthetic CI is allowed.

## REFERENCE CALIBRATION PACKAGE PROVENANCE V1 — COMPLETE

Preregistration `cbd99714f655d859af2410374c3245a4afe6b056`; implementation `3dd1140650070342ab9fc4e177870fd39940a4e0`; final tests `3ff9980cad1d16d2621ae5d3bb9fbc9d9fb5955a`; workflow `17c273ff0986c89101d6ff5cf49cb1f2e61eb9ba`.
Official run `34916853723`, job `104216245975`, SUCCESS; 20/20 tests PASS first.
Artifact `10376481781`; ZIP SHA `1a37a529b4c730315268bea21754275cbfb721a2c2238d4ae3fee6f54ad925e6`; result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`; canonical package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`; result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`.

Frozen result `contractValid:true`, `verifiedFileCount:14`, `errors:[]`. Package-level decoder/configuration identity is closed; do not create a duplicate standalone decoder contract.

## CAPTURE-MANIFEST V2.2 CALIBRATION-PACKAGE BRIDGE — COMPLETE / SYNTHETIC PASS

Gap review `abfd10ea953e2be313f847f626c405a2f3607dad`; prereg `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`.
Accepted implementation `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`; tests `8feb390fe2bf506c9d5676774b0584eb65b680a6`; workflow head `f07b86c2149133714646025aa31e21e0017db17b`.
Official run `34917541786`, job `104218329349`, SUCCESS; 24/24 tests PASS first.
Artifact `10376813179`; ZIP SHA `6af8efbb303df43e61154ec605b316a6940eb87072b9393ed99e01e4e76b19df`; result SHA `f315b2000a6c2ef5d270d5340944f325f081b0b2ebc27bc06e8894bfe61165a2`; result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`.

Frozen identities include provenance result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`, package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`, decoder config SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`, and augmented V2.2 admitted-population SHA `6806913257deb635fa5dabae3622015ae9ae7ae9246ff499aaf55a1961197b2e`.

V2.2 closes capture-manifest -> canonical calibration-package identity plumbing in synthetic software but deliberately does not open/verify provenance-result bytes itself.

## STRUCTURAL AUDIT V1.1 PROVENANCE-RESULT BRIDGE — COMPLETE / SYNTHETIC PASS

Gap review `66b1d3d19913e5218c3f1a71a88b399241ea5350`; prereg `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`; pre-implementation contract-literal correction `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`.
Implementation `5bf98194cdc2045c99903d3f9229443061deec2d`; tests `a05cb02b674572144af637dfc43fe989a54934c8`; workflow head `ee3a4d64ec506e8342333ff2c0c218b6b40ad7f9`.
Official run `34918145384`, job `104220137547`, SUCCESS; 27/27 tests PASS first.
Artifact `10376674616`; ZIP SHA `7b47cbd2a641579915a0627328a9183444b227b9d7cd97595e11e928124e3387`; result SHA `11667ec86bbe22a14a22d7bfa46e96596cb07694fc58152d39591c5cf932f34d`; result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

Frozen V1.1 result: provenance expected/actual SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f` matched before parse; package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`; inherited V1 population SHA `98ed182a3cf13c5263eb564e801ed7066eb6df3f4d6ddb28426e914a4e6ca4f5`; augmented V1.1 structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

V1.1 preserves all original V1 source hashes/note events/timing/MIDI/overlap/blockers and closes structural-audit -> V2.2-bound provenance-result byte identity. It still does not prove its four structural streams belong to the same admitted capture performance.

## END-TO-END REFERENCE DECLARATION IDENTITY REVIEW — COMPLETE

Review checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_END_TO_END_REFERENCE_DECLARATION_IDENTITY_REVIEW_V1_2026-09-14.md`
commit `e3e1759b576831128ff0b95ee237b6d131a2fe51`.

Confirmed gaps:
1. structural V1 hardware `configurationId` and `calibrationId` are only nonempty and are not compared to the verified package/capture identities;
2. structural hardware lacks the upstream hardware-configuration SHA and instrument-setup SHA identities;
3. structural `clockSync.syncId` is not compared to the capture/admitted-reference clock-sync ID;
4. structural tuning/event-semantics declarations are not cross-bound to the admitted capture reference;
5. decisive gap: capture-manifest V2.2 does not declare the exact four structural-audit output hashes (`hardware`, `birth`, `pitchLatch`, `clockSync`) for an admitted attempt, and V1.1 does not bind `attemptId`, `slotId`, `underlyingPerformanceId`, or V2.2 admitted-population SHA. Therefore a valid V2.2 population and a valid V1.1 audit can still concern different reference streams/performance while sharing compatible package identity.

Decision: do **not** patch V1.1 with name-only comparisons. First add Capture Manifest V2.3 Structural-Audit Input Binding so every admitted reference/population commits to the exact future V1.x structural input bytes. Only after V2.3 is frozen and synthetically qualified may Structural Audit V1.2 bind its actual input bytes to the admitted attempt/population.

The capture `clockSync.sha256` artifact is not assumed byte-identical to the structural-audit `clockSync` JSON stream; semantic sync ID linkage is justified, raw-byte equality is not currently established. Raw pitch/birth sensor evidence is likewise not conflated with decoded structural birth/pitch-latch streams.

## NEXT ALLOWED ACTION — CAPTURE MANIFEST V2.3

Freeze, before implementation, a Capture Manifest V2.3 Structural-Audit Input Binding preregistration. For each admitted attempt, the frozen `reference.structuralAuditInputs` object should bind at minimum:
- exact future structural `hardwareSourceSha256`, `birthStreamSha256`, `pitchLatchStreamSha256`, `clockSyncSourceSha256`;
- hardware configuration ID + SHA;
- instrument-setup SHA + exact six-value `openStringMidi`;
- calibration ID;
- clock-sync ID;
- exact event-semantics version;
- source pitch/birth evidence SHAs;
- calibration-package binding SHA;
- decoder derivation-configuration SHA.

V2.3 must cross-check those identities against the existing V2.2 corpus/reference declarations, and its admitted-population SHA must commit to the canonical structural-audit-input binding. Failed/non-admitted attempts need not carry it.

After V2.3 synthetic PASS, separately preregister Structural Audit V1.2 to compare its actual source bytes/declarations against that frozen V2.3 binding and augment its structural population identity with admitted attempt/population identity.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-holdout optimizer/threshold sweeps/fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation plus separate policy review; new validation-route hardware/performance/vendor/studio spending under current budget; and any access to reserved GFN `deb` or `ele_natural` before separately frozen authorization.

## FRESH-CHAT HANDOFF / IMMEDIATE NEXT ACTION

Continue only on `songsterr-fresh-pipeline-v1`; re-fetch live head + this file before mutation.

Immediate task: freeze Capture Manifest V2.3 Structural-Audit Input Binding preregistration before code, then implement/test it synthetically as an additive wrapper over accepted V2.2. Do not implement Structural Audit V1.2 until V2.3's exact declaration shape is frozen and successfully qualified.

Keep all authorization false/zero, do not begin real calibration/holdout capture, do not access reserved GFN sources, and do not reopen V143/Gomyway or other closed lines unless explicitly asked.
