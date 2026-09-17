# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — the authorized EGSet12 untouched-lineage evaluation attempt is complete at the mandatory **pre-media provenance gate**. The first authoritative attempt, run `35176277018` / job `105058572244`, failed closed because repository history proves prior Songsterr-fresh EGSet12 exposure at commit `9c0ad09436f74b6168043a2e779b25fb3922199b`. Steps that would download EGSet12 media, install/run Basic Pitch, qualify `S AND E AND O AND K`, parse JAMS, or score correctness were all skipped. Result commit `1d3192adce476110c1bfa12658590e2e179d0a04` is frozen as **`BLOCKED_UNTOUCHED_LINEAGE_PROVENANCE / REAL_EVALUATION_NOT_EXECUTED`**. Real correctness remains unknown.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Never rewrite, soften or reinterpret frozen historical FAIL/C/PASS results.

## GLOBAL AUTHORIZATION — EGSET12 ATTEMPT CONSUMED / NO SUCCESSOR RUN AUTHORIZED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Authorization chronology:

1. `I authorize a model run when your ready` was pre-PRE willingness/intent only.
2. `Record pre with my authorization` authorized recording PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` only.
3. After that exact PRE/corpus/action was frozen and presented, the user said `Please continue 💚`. This was valid post-freeze authorization for the exact EGSet12 v1 / Zenodo `11406378` one-shot governed by PRE `2a2ed0...`.
4. That authorization is now **consumed** by first authoritative attempt run `35176277018`, job `105058572244`, attempt 1.
5. The attempt stopped at provenance before media/model/reference/scoring. It must not be retried or rescued under the same PRE.
6. No alternate/successor corpus execution is authorized. A genuinely untouched corpus requires a new prospective PRE and a new post-freeze authorization.

## FROZEN CANDIDATE

Final candidate remains exactly:

`S AND E AND O AND K`

Authority:

- positive-core PRE `b7cfc43b6bd7e80d9a05694b37d332f1ef540696`;
- composer `scripts/songsterr-fresh/v7_fail_closed_positive_core_v1.py`;
- composer commit `5683830ebd0573b902bf205fe972a540fbaf37a9`, blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`;
- mechanical result `99b37c2875a1c2551418fc8422ae4c302bf17eae`;
- run `35121000102`, job `104878449999`, artifact `10457970208`;
- immutable label `PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS`.

State mapping:

- `POSITIVE_CORE_CANDIDATE` -> `corroborated`;
- `PROTECTION_REJECTED` -> `rejected`;
- `UNRESOLVED_SUPPORT_OR_CONTEXT` -> `insufficient` / abstention.

No raw `0.01`, rank/top-K, weighted score, maximum-only rule, candidate subset, candidate-confidence rescue or reattack fallback is permitted.

## FROZEN KKT / SUPPORT / AUDIO PREPARATION LINEAGE

KKT authority:

- PRE `4ea9c075ea02231206a7602457e028b65c2e7a9e`;
- module commit `7020dc21d1cbcc89597f24511bd40bd37b4c9f60`;
- module blob `2daa9f7f6983a3ec894fc08a86e9bced7b1f96c4`;
- result `cfe72ac6fb2459166a25cdd0789a59d257c846d1`;
- run `35119500201`, job `104873352558`, artifact `10456247666`.

V6 DSP dependency:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `SAMPLE_RATE=44100`, `FFT_SIZE=8192`.

Frozen input preparation present at the EGSet12 PRE parent remains historical/prepared but was not exercised on EGSet12 in the blocked attempt:

- V2 loader/validator blob `f9bef389f848c8f003ffa844b1eb2eea5754002d`;
- deterministic WAV decode / float64 conversion / stereo mean reduction;
- `scipy.signal.resample_poly` to `44100 Hz` using reduced integer ratio;
- V7 qualifier blob `54b1a4be41dcac1fe3f8e70cda1245a76036a4d2` reuses the frozen V2 loader.

## EGSET12 EVALUATION PRE — FROZEN, AUTHORIZED, NOW CONSUMED

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_PRE.md`;
- commit `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`;
- parent `08a87028f5ea683b670e96f4b71625ebfdbbb7fb`;
- corpus EGSet12 v1 / Zenodo `11406378` / exact official `01..12` WAV+JAMS pairs and 24 MD5s frozen in PRE;
- first score would have been exact MIDI + one-to-one onset match within `<=0.050 s`;
- no prospective performance pass threshold;
- all 12 tracks mandatory;
- no post-hoc exclusions, tolerance sweep, octave forgiveness, pitch-class forgiveness, manual rematching or rescue rerun;
- PRE explicitly states: if contamination is found, do not run; record the provenance failure and require a new prospective corpus/PRE.

## EGSET12 AUTHORITATIVE RESULT — BLOCKED BEFORE MEDIA

Immutable result:

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_RESULT.md`;
- result commit `1d3192adce476110c1bfa12658590e2e179d0a04`;
- workflow/head `b6cc09f1d1576f5e14586ed640e87691c38d714b`;
- workflow `.github/workflows/songsterr-egset12-positive-core-one-shot.yml`;
- run `35176277018`;
- job `105058572244`;
- attempt `1`;
- artifact `songsterr-egset12-positive-core-one-shot-attempt-1`;
- artifact ID `10478985810`;
- artifact digest `sha256:da71074013e67c09b7ae85bcafcb914ff2858bf9abb6941a27c769e403c8a53c`;
- frozen status **`BLOCKED_UNTOUCHED_LINEAGE_PROVENANCE / REAL_EVALUATION_NOT_EXECUTED`**.

Mandatory step ordering observed:

- setup and full-history checkout succeeded;
- step 3 `Verify PRE ancestry and untouched-lineage provenance before media` failed;
- Python/runtime/model setup was skipped;
- implementation/support verification was skipped;
- synthetic support tests were skipped;
- all 24 EGSet12 file downloads/hash checks were skipped;
- Basic Pitch was skipped;
- positive-core qualification was skipped;
- prediction sealing was skipped;
- JAMS parsing/scoring was skipped;
- execution-manifest generation was skipped;
- authoritative evidence upload succeeded.

Therefore this attempt produced **no EGSet12 prediction or correctness evidence**.

### Exact provenance reason

The preserved artifact `gates/provenance-hits.txt` identifies prior Songsterr-fresh history including:

- commit `9c0ad09436f74b6168043a2e779b25fb3922199b`;
- file `docs/checkpoints/SONGSTERR_FRESH_V6_EGSET12_PREMEDIA_REJECTION.md`;
- explicit EGSet12 / Zenodo `11406378` metadata review on 2026-09-15.

That historical V6 review rejected EGSet12 before media because its amplifier-microphone signal path did not satisfy the then-frozen DI holdout gate, and it states no EGSet12 WAV/JAMS/model/correctness was opened. Even so, the newer EGSet12 PRE's stricter untouched-lineage criterion requires fail-closed treatment of prior lineage exposure that could have influenced candidate/corpus selection. It cannot be waived after the run.

EGSet12 is therefore **ineligible as the untouched-lineage population under PRE `2a2ed0...`**. This is not a model correctness FAIL.

## INTERIM BLOCKER / CORRECTION AUDIT TRAIL

Historical interim blocker:

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_EXECUTION_PREMEDIA_BLOCKER.md`;
- commit `5ccbfab92cf7fe3f714c972847359b6036b63f47`;
- label `BLOCKED_PRE_MEDIA_AUDIO_PREPARATION_UNFROZEN`.

Correction:

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_PREMEDIA_BLOCKER_CORRECTION.md`;
- commit `d0cb42061c9417ccf8b69d276e77a88accce630b`;
- established that the V2 loader and V7 caller already froze the needed audio preparation at the PRE parent;
- superseded that interim audio-preparation blocker without erasing it from history.

That correction does **not** alter the later authoritative provenance failure.

## RECOVERED BASIC PITCH PROPOSAL IDENTITY — PREPARED BUT NOT RUN ON EGSET12

Historical source authority:

- prior successful proposal run `34936227380`, attempt 1;
- workflow `.github/workflows/songsterr-egfxset-repaired-one-shot.yml`;
- workflow head `b37d400b186a926985bb16b91702e2f88e55d785`;
- Python `3.10.21`;
- NumPy `1.26.4`;
- `tflite-runtime==2.14.0`;
- `basic-pitch==0.4.0`;
- transcriber blob `e9137496363f14cbe6194e32304c8b17b0b6569c`;
- `basic_pitch.inference.predict()` once per input;
- MIDI `40..88`;
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.7 ms`;
- `multiple_pitch_bends=False`;
- `melodia_trick=True`.

Because provenance failed first, the EGSet12 run never reached runtime installation/model identity freeze or inference.

## HISTORICAL NO-RERUN LEDGER

Do not rerun or reconstruct:

- EGSet12 attempt `35176277018`, job `105058572244` — provenance-blocked; authorization consumed;
- temporal/support `35053450282`, job `104658560061`, result `86549fcf3f15898aa551064b522ce42ca32b1b86` — stored measurement inaccessible;
- candidate-breadth `35057264267`;
- gate-free `35057812575`;
- fixed-feature `35058404820`;
- protection/raw-fit `35059307767`;
- support-conditioned landscape `35060032406`;
- KKT `35119500201`;
- positive-core `35121000102`;
- V7 first real attempt `35051186125` remains `FAIL_V7_BOUNDARY_SYNTHETIC_PREREQUISITE / REAL_EVALUATION_NOT_EXECUTED`.

Prior EGFxSet/V2/V7 observations remain exposed historical evidence, not untouched populations.

## CURRENT TECHNICAL CONCLUSION

The candidate method remains mechanically frozen and unchanged. EGSet12 did not produce a real correctness measurement because its prospective untouched-lineage provenance gate failed before media access. Real correctness therefore remains **unknown**.

The provenance gate worked as intended: it prevented an already-exposed corpus from being silently treated as untouched. There is no scientific basis to rerun EGSet12 under this PRE or to weaken the gate after observing the failure.

## NEXT ENGINEERING / RESEARCH BOUNDARY

The next permitted work is **read-only successor-corpus provenance research**, not model execution.

Proceed in this order:

1. identify one or more external real-guitar candidate corpora without opening their correctness/model outputs;
2. audit repository/history first for exact corpus/name/source identifiers and any prior Songsterr-fresh exposure;
3. reject any candidate that cannot honestly satisfy the desired untouched-lineage definition;
4. for a surviving candidate, establish source/version/rights, signal path, annotation structure, population and feasibility using metadata only;
5. write a new prospective real-evaluation/scoring PRE for that exact corpus and frozen candidate `S AND E AND O AND K`;
6. update this checkpoint to the new PRE commit;
7. stop and obtain fresh post-freeze user authorization before any new corpus/model correctness execution.

Do **not** silently substitute another corpus under the EGSet12 PRE. Do not reuse the consumed `Please continue 💚` authorization for a different corpus.

## FRESH CHAT RESUME POINT

1. Reconcile live branch and read this checkpoint first.
2. Governing latest result: `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_RESULT.md`, commit `1d3192adce476110c1bfa12658590e2e179d0a04`.
3. EGSet12 run `35176277018` / job `105058572244` is permanently no-rerun under PRE `2a2ed0...`.
4. Preserve artifact `10478985810`, digest `sha256:da71074013e67c09b7ae85bcafcb914ff2858bf9abb6941a27c769e403c8a53c` as authoritative provenance evidence.
5. Do not call EGSet12 an untouched-lineage correctness population; no EGSet12 correctness was measured.
6. Candidate authority remains `99b37c2875a1c2551418fc8422ae4c302bf17eae`; KKT authority remains `cfe72ac6fb2459166a25cdd0789a59d257c846d1`.
7. Historical raw `0.01`, rank/top-K, weighted score, candidate subset and reattack fallback remain forbidden.
8. Next work, if continuing without a new user instruction, is metadata/provenance-only search for a genuinely untouched successor corpus and prospective PRE preparation. Do not execute a successor corpus without fresh post-freeze authorization.
9. Archived V143/Gomyway remains untouched.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not switch Production or `main`.
- Do not rerun EGSet12 attempt `35176277018` or alter its provenance search to force a pass.
- Do not silently substitute another corpus under PRE `2a2ed0...`.
- Do not rerun frozen historical one-shots.
- Do not reconstruct the blocked temporal diagnostic.
- Do not tune from synthetic or real post-result values.
- Do not treat synthetic 12/2/9 routing as correctness evidence.
- Do not transfer historical `0.01` into broad fixed raw fit or positive-core composition.
- Do not introduce rank/top-K, majority vote, weighted score, maximum-only rescue, per-MIDI exceptions, candidate subset search or reattack fallback.
- Do not rescue support/context-unavailable cases.
- Do not alter frozen V6/V3/V7/KKT/positive-core logic in place.
- Do not use a historical wrapper verdict instead of final positive-core composition.
- Do not open any successor corpus correctness/model output before a new prospective PRE plus fresh post-freeze authorization.

Archived V143/Gomyway remains untouched.
