# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — purpose-built software lineage complete; optional $0 EGFxSet one-file smoke candidate and scoring frozen metadata-only; execution blocked before media by Basic Pitch authorization boundary
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
- **Do not create another purpose-built software lineage gate unless a new, concrete, non-duplicative gap is first identified and documented.**

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

Frozen essentials remain: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; isolated-guitar DI; one-to-one matching onset <= `0.050 s`, pitch <= `50 cents`; >=1,000 pooled V6-positive estimates; pooled one-sided 95% Wilson LB >=0.9900; strata >=100 positives require point precision >=0.9500; exactly one official correctness run after all upstream real gates. Do not tune from holdout observations.

## CLOSED / RESERVED DATA LINES

- Guitar-TECHS remains frozen `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; result checkpoint `9ec1dcf396341f5e95d76a32d90183cb7f70b725`. Never rescue/repair/score/rerun.
- Guitar Fretboard Notes train-only research remains non-holdout at pinned revision `a33a26243e88e7ccd4893bee30eac3219ec8bef8`. Exposed train sources: `ele`, `eqm`, `eqm2`; reserved untouched: `deb`, `ele_natural`. V1 result `535e6861bb9895f5c38161ec7877a6534cf6fa4e`; V2 session-invariance result `4569a2f7970cde7975107146ba9ffb785066864b`, classification `MIXED`.

## PURPOSE-BUILT HOLDOUT — SOFTWARE LINEAGE COMPLETE / PHYSICAL ROUTE BUDGET-PAUSED

Prospective design authority includes expanded design `e37d2b4662db949157d2cf4797370f05648b6940`, physical-reference semantics `ea5f50212cd1cd3794c65cb648a4d781e49e4082`, QA matrix `2b191b39f2f1c19564f1353381779acbc96fbeda`, bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`, and topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Earlier synthetic software gates remain complete: Capture Manifest V2.1 `9d3b17b392bd486753cb657318c048a7ae2460a7`; Structural Audit V1 `df7eb9edacb170ab24e2c200b1c0a8028625f87a`; Stage-0 Contact Replay `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`; debleed `f233da0000188977334331c4614b6e541ae2490b`; hardware-marker clock map `79293a7632915fc67f5b7ee0ac2242466ec83ea7`.

### Reference Calibration Package Provenance V1 — COMPLETE

Preregistration `cbd99714f655d859af2410374c3245a4afe6b056`; implementation `3dd1140650070342ab9fc4e177870fd39940a4e0`; official run `34916853723`, job `104216245975`, 20/20 PASS; result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`.

Original identity-only synthetic fixture result SHA `4fd62e62a855031bd3c189253bc04f004d271d53bf2b636c586c15b93e59e98f`; package binding SHA `735d276afc5bac7cd8e0e905ae42f8d4dc4bfae835ae013403ccdc31c4cf857c`; decoder configuration SHA `3c9850cdd5085c2dc5230211b18d3362b7f0cef2d23be19b9af3b456df9a2777`.

Provenance V1 verifies exact package/decoder file identity; later Derivation Replay uses a **new executable synthetic package** validated under this unchanged contract.

### Capture Manifest V2.2 — COMPLETE / SYNTHETIC PASS

Review `abfd10ea953e2be313f847f626c405a2f3607dad`; preregistration `9596bfc745a5acdbb47b403eb3d39688ceb20ebd`; implementation `e3e3ae05ab0ab4a94a77e6c6e5be2466f618cf46`; run `34917541786`, job `104218329349`, 24/24 PASS; result checkpoint `7d2d05ec365bbdb1aced574f7caf1865795fbc23`.

V2.2 links admitted reference/population identity to canonical package/provenance/decoder identity.

### Structural Audit V1.1 — COMPLETE / SYNTHETIC PASS

Review `66b1d3d19913e5218c3f1a71a88b399241ea5350`; preregistration `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`; correction `3839d43dae9881fb2c98a5cac7c6f0b634eb944c`; implementation `5bf98194cdc2045c99903d3f9229443061deec2d`; run `34918145384`, job `104220137547`, 27/27 PASS; result checkpoint `96bb0aec9b02f16cb82ba78f16d3164af78474ec`.

V1.1 structural population SHA `603f69c1fa716784e23767255b4305b82eb6bde6187859db645a883694ff08b6`.

### Capture Manifest V2.3 Structural-Audit Input Binding — COMPLETE / SYNTHETIC PASS

Preregistration `c79fbd1d728a9d3dac86f036998108cb9765628e`; implementation `ae320ced78ebc5ce2cac15cc90a4564a9fa24502`; tests `b0af7344b71a4637087f5b112e4c239d4ac484cd`; workflow head `be814017f0ea4e4c89bb25824be66ff0bd63c6c7`.
Official run `34918802857`, job `104222117869`, 27/27 PASS; artifact `10376723782`; ZIP SHA `63559ef6c5c7bdca79a33c8a9e5bb754edb699e6d70a6bbfb499d3ad58d1b211`; result SHA `0d0372f1123468a9ae1fd90b9c830f233c33d2104e3dc76656fcb5d8147cdb08`; checkpoint `3ba759566258a49c2fd9b198f686bb1d9a6edc5d`.

V2.3 co-binds admitted raw pitch/birth evidence SHAs, decoded structural target SHAs, package binding, decoder configuration and attempt/population identity.

### Structural Audit V1.2 Capture-Population Binding — COMPLETE / SYNTHETIC PASS PER ATTEMPT

Result-byte review `866c673bc7728a8e0943eb45b0109910c28a36f6`; preregistration `617cdc71be4fea6ccdafec1aadf47c13d66726cb`; implementation `eacbb06adcbb9c2e4f7a2c5ed697c50a87c5c6ac`; tests `09aaccb6acac67c96e136ff57a298a39ce8107e8`; workflow head `a3ecef8cf9a827149f99e7af383b0d94957decb1`.
Official run `34919179891`, job `104223229264`, 35/35 PASS; artifact `10377581430`; ZIP SHA `1cb3fc511735d709603e3b336af6ec63bcb41e1e634297145cbc955838c0cb09`; result SHA `b9aece4790ce4fb9820b21187d551a4374636c341718f7ed75e10456c38a8145`; checkpoint `f4c63134f8b49723f342f5ba5f648498af317f73`.

V1.2 proves actual structural source bytes match the admitted V2.3 binding/population and pass inherited structural/provenance rules.

### Structural Audit Population Completeness V1 — COMPLETE / SYNTHETIC MULTI-ATTEMPT PASS

Completeness review `9c85176001a62031299a036594f6d3273fb7b759`; preregistration `642f96898c209044c8f408ef473227fe4e9c4caa`; implementation `baeaf50ed3f4436d6be527009164052d1df813c1`; tests `4acb317af8cd69f0521cb2354c0dfef379c60ad2`; workflow head `3b3b530b5d8db0b5134db55ade494dc2487dd4d6`.
Official run `34920035528`, job `104225879209`, 37/37 PASS; artifact `10378040469`; ZIP SHA `c8ed38f5b78b8e24597ad6052a230d834ca49cfd90037faee02f6a3faaf5a339`; result SHA `d5cb80562141bd32302cf23caf3e53c8dab7b05115b98d92e078e030519cff4e`; result checkpoint `ad2d9405793f41c20c74328f3abddd22256c686b`.

This closes exact all-admitted-attempt structural coverage.

### Reference Evidence Derivation Replay Review — COMPLETE

Review checkpoint `0a50220a089f22733d7066e5772da7e73d71f557` confirmed the final functional gap at that stage: exact raw pitch/birth evidence + exact package decoder identity could coexist with arbitrary structurally valid decoded targets without proving actual execution produced them.

### Reference Evidence Derivation Replay Population V1 — COMPLETE / SYNTHETIC MULTI-ATTEMPT PASS

Preregistration `3aa4518bf1bc7b183f1e7025dbc1a4d182245db2`; method recorded pre-implementation at `8f70849696b1e1a66157e68d29a541a60390a241`.
Implementation `fa3883a6089d93501c9e2a59e607b1a668eea259`, blob `62c0a7ae08bd136fca9f72ad303203d214ea5782`.
Tests `8afd45fcb117bfa7914479c7cb68b9e25794d06b`, blob `8f45d892cbcea707f1a14341cc143ca7335390b7`.
Workflow head `3f98ae44490b616e04dd003b46b76b5afcbfe433`, blob `7e514084f9cf0919968e798a47216134be46cc48`.

Official run `34920805043`, job `104228294085`, SUCCESS; **38/38 tests PASS first** on Python `3.12.14`.
Artifact `10377539320`, size `1,670` bytes; ZIP SHA `6970bc7c29d275a8cac221d3270a3ce5aacc0c62b219c021d929d81fc54975e5`; canonical result SHA `7fb41331f9b382987b579df228edfb504276317e3efb3428011f35c561151109`.
Result checkpoint `e8f202c1a9ccee32a6f3883c06c79f89c4e77159`.

Frozen official executable synthetic chain:
- `contractValid:true`, `populationDerivationReplayEstablished:true`, `errors:[]`;
- admitted/submitted/verified replay count `2/2/2`;
- V2.3 result SHA `7b0cdc9ac655c95773dca1cd4c6b4b71215b3c3438db650a37bfca13fe4b941b`;
- V2.3 admitted-population SHA `6f649fae8391178524acc817443945849b9105c5030fa6e1195dc664a23b4d53`;
- structural completeness result SHA `ee5209672b9d246e63caa6c797822376cb95b504bdd55c8eb42e10e7b2717970`;
- structural completeness identity `7e4b7d08b7747d78d8a922821ac4ff3e79631c861b6f9e620c51f545a831fd6b`;
- executable Provenance V1 result SHA `ec45533583c90ba235508ed5e9d728f3b1d85d910f86f9f1c567908c013563a4`;
- executable package binding SHA `46aaa082c4f1aada2006fdc55e75a14588fbc9f0fb1cd8ec6119bf60309ccead`;
- decoder ID/version `synthetic-executable-reference-decoder-v1` / `1.0.0-executable-synthetic`;
- decoder code SHA `5a695bab11b9b3dbe883298de9cd3444e491c4d9199220c550b6295bb37ff8dc`;
- decoder configuration SHA `3202544052895862da14adb3834f7f1b56b2ea3abd08864d5b51769c43791ce1`;
- population derivation replay SHA `3d560d13732be33bd84cd8e228e805ea454e2d86c56a89215c08739164be709c`.

The official fixture uses raw evidence bytes deliberately different from decoded output bytes. The exact package-bound decoder was executed in isolated mode on those exact raw bytes and reproduced the exact V2.3-bound pitch-latch/birth output byte hashes for every admitted synthetic attempt. This closes the identified raw-evidence -> decoded-stream functional software-lineage gap.

### Final Software-Lineage No-Gap Review — COMPLETE

Checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_FINAL_SOFTWARE_LINEAGE_NO_GAP_REVIEW_2026-09-14.md`
commit `54f25a793f66b4d9fe53f11c041122fdb41d057c`.

Frozen conclusion:

**NO CONCRETE, NON-DUPLICATIVE SOFTWARE DECLARATION / SUBSTITUTION / POPULATION-COMPLETENESS / FUNCTIONAL-LINEAGE GAP REMAINS IN THE CURRENT PURPOSE-BUILT REFERENCE CONTRACT CHAIN.**

The completed synthetic chain now covers package/decoder byte identity, capture/package binding, provenance-result byte verification, admitted attempt/population identity, exact structural source binding, structural semantics, all-admitted population coverage, exact raw evidence binding, exact package-bound decoder execution, exact raw-evidence -> decoded-output replay, and deterministic final population identities.

Hardware configuration / calibration / timing / sensor truth is now a **physical qualification question**, not another identified synthetic software gate. Replaying additional synthetic declarations would not establish real sensor accuracy, real clock behavior, or real calibration validity.

## NEXT OBJECTIVELY NECESSARY ROUTE — PHYSICAL, CURRENTLY PAUSED

Stop creating purpose-built software lineage gates unless a later review identifies a specific new gap not already covered above.

The next necessary route is physical:
1. procure/assemble the frozen reference hardware/topology if budget authorization later permits;
2. perform frozen bench/hardware qualification and real calibration;
3. preserve exact package/raw/derived identities under the completed software contracts;
4. after legitimate real calibration authority, perform real holdout capture under frozen rules;
5. only after real structural gates pass may the separately frozen V6/correctness path be considered.

Under budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58`, physical procurement/calibration/capture remains paused and unauthorized.

## OPTIONAL $0 EXTERNAL AUDIO SMOKE TEST — METADATA CANDIDATE + SCORING FROZEN / EXECUTION BLOCKED

The user wants to try a **small, clean guitar audio file with an independently published physical fret-position label** as a one-file blind external smoke test.

This is allowed only as non-authorizing $0 research. It is **not** the authoritative purpose-built holdout and cannot set `correctnessAuthorized`, `modelValidationComplete`, customer eligibility, or delivery authority.

Fresh-chat sequence:
1. Re-fetch the live branch head and this checkpoint before mutation.
2. Search public/academic sources for a very small clean isolated-guitar WAV/FLAC with an independent metadata label giving exact physical `string + fret` (and preferably MIDI/pitch), a usable validation/research license, and a direct immutable file/repository identity.
3. **Do not use or inspect reserved Guitar Fretboard Notes `deb` or `ele_natural`.** Do not use Guitar-TECHS, archived V143/Gomyway, or any corpus/file already exposed for tuning of the fresh method.
4. Prefer a corpus/file never previously accessed in this project. Before decoding/listening/processing the audio bytes, record the candidate dataset/repository, revision if available, exact path/file identity, license, published physical label, and why it is plausibly untouched.
5. If a suitable candidate exists, freeze a tiny dedicated **ONE-FILE EXTERNAL AUDIO SMOKE TEST** procedure before executing it. Freeze the candidate identity, expected label from independent metadata, exact pipeline entry point/settings, and scoring rule. No tuning, threshold changes, retries with alternate files, or candidate shopping after observing the output.
6. Keep the interpretation narrow: report whether the one file ran successfully and what physical position/pitch the current pipeline produced versus the independently published label. A PASS is encouraging smoke-test evidence only; a FAIL is diagnostic. Neither outcome authorizes V6/correctness or replaces physical validation.
7. Before execution, confirm the chosen entry point does not violate the frozen authorization boundary. If it requires Basic Pitch/V6/correctness execution that is presently unauthorized, stop and document the required explicit non-authorizing test authorization instead of silently running it.
8. If no eligible $0 candidate with true independent string/fret truth can be found, stop and report that result. Do not consume a reserved split merely to obtain a convenient test file.

### 2026-09-15 EGFxSet metadata-only research log

Dedicated checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_PRE_MEDIA.md`, first committed at `aa1e3f910b9d019b0cecbb7b479e7314306d6e85`; scoring freeze refined at `f7ed423141407459660818b3da0f12e92b7e2fb8`.

Current result: `BLOCKED_AUTHORIZATION_PRE_MEDIA`; `MEDIA_DELTA=0`.

- Candidate dataset: EGFxSet version 1.0, Zenodo DOI `10.5281/zenodo.7044411`.
- Clean archive identity: `Clean.zip`, MD5 `cdb1b401960f56becc8640387910e78a`.
- Exact metadata-selected member: `Clean/Bridge/6-0.wav`, preview size about `723.0 kB`.
- Independent physical label: standard-tuned guitar string `6`, fret `0`; expected MIDI `40` (E2).
- The official project documentation states standard tuning and independent string/fret annotation; the ISMIR 2022 publication is CC BY 4.0.
- No candidate audio bytes were downloaded, decoded, listened to, waveform-inspected, or processed.
- Search of the latest 100 active-branch commit metadata entries found no `EGFx` / `EGFxSet` reference. This supports but does not prove prior non-exposure.
- Existing `transcribe_isolated_guitar_basic_pitch.py` directly invokes Basic Pitch and emits decoded MIDI note events; it does not itself emit physical string/fret.
- The unchanged deterministic fresh core uses standard guitar tuning MIDI `[40,45,50,55,59,64]`; MIDI `40` maps uniquely to string `6`, fret `0`, so this candidate avoids physical-position ambiguity if the decoder emits MIDI 40.
- Missing independent onset truth is not being filled in or fabricated. This optional smoke test is file-level, not official V6 onset-match scoring.
- Scoring is now fully frozen without event selection: decoded notes must be non-empty and the set of all emitted MIDI values must be exactly `{40}`; repeated MIDI-40 segments are allowed, but any other MIDI or an empty artifact is `FAIL_PITCH`. Every emitted event must map to string `6`, fret `0`, reconstructed MIDI `40` for `PASS_POSITION`. Overall PASS also requires one-shot runtime success. No scoring choice remains after output is seen.
- **Execution is currently forbidden** because `basicPitchAuthorized:false`. Per the checkpoint rule, stop before media access/inference unless the user explicitly authorizes exactly one non-authorizing Basic Pitch smoke run on this frozen candidate. That permission would not authorize V6/correctness, tuning, retries, alternate candidates, customer eligibility, delivery, or any closed/reserved dataset line.

The authoritative next validation route remains the physical calibrated holdout described above and remains budget-paused.

## FRESH-CHAT HANDOFF / IMMEDIATE ACTION

Re-fetch live branch head + this checkpoint before any mutation.

**Immediate fresh-chat task:** candidate and scoring are already frozen. Do not search for or switch to another candidate. The frozen candidate is EGFxSet `Clean/Bridge/6-0.wav` inside Zenodo version 1.0 `Clean.zip` (MD5 `cdb1b401960f56becc8640387910e78a`), expected string 6 / fret 0 / MIDI 40. No media has been touched. Before any media access or inference, preserve the dedicated pre-media checkpoint and enforce the current authorization blocker.

The next executable step requires explicit user permission for exactly one **non-authorizing Basic Pitch smoke run** on that frozen candidate under the existing defaults and deterministic mapper. Without that permission, stop with `BLOCKED_AUTHORIZATION_PRE_MEDIA`; do not download/decode/listen/run, do not tune, do not retry, and do not candidate-shop.

There is **no authorized immediate purpose-built software-lineage implementation task**. Do not manufacture another gate. Keep all authorization fields false/zero, do not begin physical procurement/calibration/capture while budget-paused, and do not reopen V143/Gomyway or other closed lines unless the user explicitly asks.
