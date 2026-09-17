# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` has valid post-freeze user authorization (`Please continue 💚`) and remains the governing EGSet12 evaluation PRE. The conservative pre-media blocker at `5ccbfab92cf7fe3f714c972847359b6036b63f47` is now **superseded as a current blocker** by correction `d0cb42061c9417ccf8b69d276e77a88accce630b`: frozen V2 blob `f9bef389f848c8f003ffa844b1eb2eea5754002d` already prospectively defines WAV decode, stereo mean reduction and `scipy.signal.resample_poly` conversion to the frozen `44100 Hz` DSP grid, and frozen V7 blob `54b1a4be41dcac1fe3f8e70cda1245a76036a4d2` already reuses that loader. Both blobs were present unchanged at PRE parent `08a87028f5ea683b670e96f4b71625ebfdbbb7fb`. **No EGSet12 WAV/JAMS correctness, prediction, qualification or score has yet been opened.**

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

## GLOBAL AUTHORIZATION — EXACT EGSET12 PRE AUTHORIZED / FIRST EVIDENCE RUN NOT YET STARTED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Authorization chronology:

1. `I authorize a model run when your ready` was pre-PRE willingness/intent only.
2. `Record pre with my authorization` authorized recording PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` only.
3. After that exact PRE/corpus/action was frozen and presented, the user said `Please continue 💚`. This is the valid post-freeze authorization for the exact PRE: EGSet12 v1 / Zenodo `11406378` / provenance preflight -> exact prior Basic Pitch proposal run per track -> exact frozen `S AND E AND O AND K` qualification -> frozen note-birth scoring -> immutable first-result record.
4. The interim blocker was reached and recorded before media. Read-only lineage inspection then proved the missing preparation rule was already frozen. Correction `d0cb42061c9417ccf8b69d276e77a88accce630b` changes no corpus, candidate, score, preprocessing lineage or action, so the existing post-freeze authorization remains applicable to this same PRE.

## FROZEN CANDIDATE

Final candidate is exactly:

`S AND E AND O AND K`

Authority:

- positive-core PRE `b7cfc43b6bd7e80d9a05694b37d332f1ef540696`;
- composer `scripts/songsterr-fresh/v7_fail_closed_positive_core_v1.py`;
- composer commit `5683830ebd0573b902bf205fe972a540fbaf37a9`, blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`;
- mechanical result `99b37c2875a1c2551418fc8422ae4c302bf17eae`;
- run `35121000102`, job `104878449999`, artifact `10457970208`;
- immutable label `PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS`.

State mapping for EGSet12:

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

Frozen input preparation already present at EGSet12 PRE parent:

- V2 loader/validator blob `f9bef389f848c8f003ffa844b1eb2eea5754002d`;
- WAV decode `scipy.io.wavfile.read`;
- deterministic PCM -> finite float64 conversion;
- multichannel -> `np.mean(..., axis=1, dtype=np.float64)`;
- sample-rate conversion uses `gcd(source_rate,44100)` and `scipy.signal.resample_poly`; for `48000 -> 44100`, `up=147`, `down=160`;
- V7 qualifier blob `54b1a4be41dcac1fe3f8e70cda1245a76036a4d2` already calls `frozen_v2.load_analysis_audio()` and maps onset seconds with `int(round(startSeconds * 44100))`.

The EGSet12 execution adapter may reuse the frozen V2 loader and model-note validator as input plumbing, but must call the **final positive-core composer** for verdicts rather than substituting the historical V7 wrapper verdict.

## EGSET12 EVALUATION PRE — FROZEN AND AUTHORIZED

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_PRE.md`;
- commit `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`;
- parent `08a87028f5ea683b670e96f4b71625ebfdbbb7fb`;
- corpus EGSet12 v1 / Zenodo `11406378` / exact official `01..12` WAV+JAMS pairs and 24 MD5s frozen in PRE;
- first score exact MIDI + one-to-one onset match within `<=0.050 s`;
- report per-track raw and positive-core TP/FP/FN/precision/recall/F1, corpus micro, arithmetic macro, raw/corroborated/rejected/insufficient counts and retention fraction;
- no prospective performance pass threshold;
- all 12 tracks mandatory;
- no post-hoc exclusions, tolerance sweep, octave forgiveness, pitch-class forgiveness, manual rematching or rescue rerun;
- predictions/qualification artifacts must be materialized before reference-score reveal.

## INTERIM BLOCKER / CORRECTION AUDIT TRAIL

Interim blocker:

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_EXECUTION_PREMEDIA_BLOCKER.md`;
- commit `5ccbfab92cf7fe3f714c972847359b6036b63f47`;
- label `BLOCKED_PRE_MEDIA_AUDIO_PREPARATION_UNFROZEN`;
- it was a conservative stop based on incomplete dependency inspection and produced no EGSet12 evidence.

Correction:

- file `docs/checkpoints/SONGSTERR_FRESH_EGSET12_PREMEDIA_BLOCKER_CORRECTION.md`;
- commit `d0cb42061c9417ccf8b69d276e77a88accce630b`;
- proves V2 loader blob `f9bef389...` and V7 caller blob `54b1a4be...` were already frozen at PRE parent;
- supersedes the blocker as a current stopping condition without erasing it from history;
- untouched-lineage status remains preserved because no corpus/model/correctness output had been opened.

## RECOVERED BASIC PITCH PROPOSAL IDENTITY

Source authority:

- prior successful proposal run `34936227380`, attempt 1;
- workflow `.github/workflows/songsterr-egfxset-repaired-one-shot.yml`;
- workflow head `b37d400b186a926985bb16b91702e2f88e55d785`;
- Python `3.10.21`;
- NumPy `1.26.4`;
- `tflite-runtime==2.14.0`;
- `basic-pitch==0.4.0`;
- transcriber `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` historical/current blob `e9137496363f14cbe6194e32304c8b17b0b6569c`;
- `basic_pitch.inference.predict()` exactly once per input;
- MIDI `40..88`;
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.7 ms`;
- `multiple_pitch_bends=False`;
- `melodia_trick=True`;
- deterministic sort and reissued proposal IDs;
- native input path is passed directly to Basic Pitch.

Execution must still record the installed Basic Pitch default model-file identity/hash before inference when available.

## HISTORICAL NO-RERUN LEDGER

Do not rerun or reconstruct:

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

The candidate method and evaluation score are prospectively frozen; post-freeze execution is authorized; the temporary sample-rate blocker is resolved from pre-existing frozen code; real correctness is still unknown because the first EGSet12 evidence-producing run has not begun.

## NEXT ENGINEERING / EXECUTION BOUNDARY

Continue the already-authorized PRE without opening corpus output until every pre-media gate passes:

1. run a full-history untouched-lineage provenance preflight over repository history before PRE parent `08a87028...`, failing closed on prior EGSet12 Songsterr-fresh exposure that could have influenced the candidate;
2. freeze/verify exact Basic Pitch environment and default model-file identity/hash before inference;
3. verify frozen transcriber/V2 loader/V6/KKT/positive-core implementation blobs and pinned dependency versions;
4. prepare a research-only execution adapter that reuses frozen V2 audio/model validation and invokes frozen final positive-core composition for every exact proposal;
5. prepare deterministic JAMS parsing and frozen `50 ms` note-birth scorer without consulting EGSet12 correctness content;
6. mechanically test the adapter/scorer on synthetic/non-EGSet12 fixtures only;
7. create the exact one-shot workflow **last** so its path-restricted push is the single authoritative trigger;
8. in that workflow, perform provenance/runtime/blob gates before any EGSet12 download;
9. after gates pass, fetch and hash-verify all 24 files, invoke Basic Pitch exactly once per WAV, qualify exactly once, materialize raw/qualified artifacts, then parse references/score once and upload complete artifacts;
10. reveal/record only the first authoritative result; no retry/repair/tuning to improve outcome.

If any pre-media gate fails, record it and stop. If infrastructure fails after the evidence-producing boundary, follow the frozen PRE's first-run policy rather than silently rerun.

## FRESH CHAT RESUME POINT

1. Reconcile live branch and read this checkpoint first.
2. Governing PRE: `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`; post-freeze authorization `Please continue 💚` is recorded and active for this unchanged PRE/corpus/action.
3. Interim blocker `5ccbfab...` is historical and superseded by correction `d0cb42061c9417ccf8b69d276e77a88accce630b`.
4. Do not write a competing resampling PRE; frozen V2 loader `f9bef389...` already defines the preparation path.
5. Build/verify the execution adapter and scorer without opening EGSet12 media; workflow must gate provenance/runtime/blob identity before download and be created last.
6. Final candidate authority remains `99b37c2875a1c2551418fc8422ae4c302bf17eae`; KKT authority remains `cfe72ac6fb2459166a25cdd0789a59d257c846d1`.
7. Historical raw `0.01`, rank/top-K, weighted score, candidate subset and reattack fallback remain forbidden.
8. Archived V143/Gomyway remains untouched.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not switch Production or `main`.
- Do not rerun frozen historical one-shots.
- Do not reconstruct the blocked temporal diagnostic.
- Do not tune from synthetic or real post-result values.
- Do not treat synthetic 12/2/9 routing as correctness evidence.
- Do not transfer historical `0.01` into broad fixed raw fit or positive-core composition.
- Do not introduce rank/top-K, majority vote, weighted score, maximum-only rescue, per-MIDI exceptions, candidate subset search or reattack fallback.
- Do not rescue support/context-unavailable cases.
- Do not alter frozen V6/V3/V7/KKT/positive-core logic in place.
- Do not substitute the historical V7 wrapper verdict for final positive-core composition.
- Do not open EGSet12 correctness/model output before the PRE's provenance/runtime/blob gates.
- Do not silently rerun after observed failure.

Archived V143/Gomyway remains untouched.
