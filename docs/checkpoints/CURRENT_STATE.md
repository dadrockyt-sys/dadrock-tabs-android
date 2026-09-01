# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`

> This CURRENT_STATE checkpoint is intentionally compacted for safe continuation. Older dedicated checkpoint files under `docs/checkpoints/` remain authoritative for the detailed history. Do not infer that omitted historical detail was revoked.

## Active project state
**V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL.**

- GOAT restricted-dataset access request was submitted successfully through Zenodo and is still awaiting the owner's decision as of 2026-09-01.
- Submission is not approval. No GOAT bytes, owner grant, conditions, or admitted holdout assets are present.
- V168 prospective reference-facing score calls remain exactly **0**.
- `main` and Production remain untouched.
- CPU only. Fresh explicit user authorization is required immediately before any GPU/CUDA/Modal use.

## Percentage reporting — standing instruction
Use separate progress/test percentages in future updates.

### Project Progress Score — fixed five-gate rubric
1. Preregistration + frozen Policy A/B complete — 20%.
2. Admission/provenance validators frozen + self-tested — 20%.
3. External candidate screening completed to a defensible stop boundary — 20%.
4. >=2 admissible independent professional holdout songs acquired, rights/provenance frozen, exact source/reference SHA256-bound, both validators passed — 20%.
5. Reference-blind Policy A/B candidates frozen for all admitted songs + prospective holdout scoring completed under the frozen evaluation rule — 20%.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

Never inflate or round a test score upward. Diagnostic work on AYGGMW/SplitMySong does not change the V168 Project Progress Score or count as a V168 holdout test.

## GOAT access path — frozen pending external decision
Dedicated checkpoints:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_SUBMITTED_20260829.md`

Record: `https://zenodo.org/records/15690894`, DOI `10.5281/zenodo.15690894`, version v1, restricted/request-access, research purposes only / not intended for commercial product use.

If access is granted, before any admission:
1. freeze exact grant wording/date/conditions/restrictions;
2. freeze exact record/version and file bytes/SHA256;
3. freeze source/reference pair binding and chosen reference layer;
4. inspect reported item_67/item_96/item_110 duration/EOF anomalies prospectively;
5. freeze deterministic score-blind integrity/song-selection rules;
6. pass BOTH frozen V168 validators for >=2 independent songs before arming any scorer/candidate workflow.

Do not continue broad public holdout searching by default. Dedicated stop checkpoint: `docs/checkpoints/V168_OPEN_HOLDOUT_SEARCH_STOP_20260829.md`.

## Frozen V168 machinery — unchanged
- Admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Provenance validator: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Holdout preregistration: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, commit `64d724e816808aa60d766923bb1a9ce241e89e89`, blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Frozen V154 scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

### Policy A — `v168-baseline-i005-policy`
Frozen V167 I005 `gss-active-only`: active Basic Pitch context required; `fundamentalPresent`; template rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template-score ratio >=1.00; reject nearest different active intervals {12,19,24}; max 1 addition/site; Guitar cap 6; inactive branch disabled.

### Policy B — `v168-gap1-earliest-policy`
Exact Policy A stream, then collapse same-MIDI connected components with consecutive grid gaps <=1 to the earliest event; singletons unchanged.

Prospective Policy B passes only if ALL: macro F1 >= A +0.10pp; macro precision >= A; no individual song loses >0.25pp F1; >=2 independent songs scored; no holdout-driven retuning/exclusion/variant mutation.

## V167 terminal handoff — immutable
Promoted I005 `gss-active-only`:
- Guitar F1 **42.7940586109996%**; P **48.54280510018215%**; R **38.26274228284279%**; TP/pred/ref **533/1098/1393**; FP565/FN860; promoted rich SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass F1 **80.45325779036827%**; P **83.203125%**; R **77.87934186471663%**; TP/pred/ref **426/512/547**.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, +0.08607010983709418pp vs I005, below frozen +0.10pp promotion threshold; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- No I006 exists. V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## SplitMySong AYGGMW diagnostic — separate from V168 prospective evaluation
User-supplied external model-separated Guitar diagnostic input only. It is **not** a professional reference or admissible V168 holdout asset.

Frozen private source:
- source SHA256 `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`;
- deterministic 22.05 kHz mono S16LE normalized WAV SHA256 `fdb0578d71f77c150e7fe66766a03953be55e7028fef4c24dc777416f2e7ff4f`;
- alignment offset 0.000 s, no time stretch.

Frozen CPU environment:
- Python 3.10.21;
- Basic Pitch 0.4.0;
- TFLite Runtime 2.14.0;
- Torch 2.8.0+cpu, CUDA unavailable;
- Basic Pitch model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`;
- Debian 13 / FFmpeg package `7:7.1.5-0+deb13u1`.

Private Codespace ARM preflight is frozen **PASS**:
- FFmpeg normalizer receipt SHA256 `e7713b47a4f3bf468b706bb0eef8c683ea3e2ec3571e3170f203e28bf9ee1f1f`;
- CPU environment receipt SHA256 `c7bf81f59220808cef01a7e399830dbf8a23df4b052fac10bac75c498ad78847`;
- ARM receipt SHA256 `f34aef34a729d4ca32ba42975717a1b8e79b568aa1a8dc44d13c2eb1bcd6ef6f`.

No SplitMySong Basic Pitch inference has yet been run. No diagnostic candidate or scorer result exists. Diagnostic reference-facing score calls remain 0.

## Historical Demucs reproducibility issue — preserved fail-closed
Authoritative V166 normalized mix SHA256: `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.

Authoritative V166 stem SHA256 values:
- Guitar `4c71e9e15dd07e60a5442923b86523bafe4313056ca3c892054a607aa7e4e9d2`;
- Bass `4b34b2bc3367d9f8ed4dce39b95ad3d60c49d6541186df6b0d24a4211b03c7ef`;
- Drums `05890ac9cad62eacf0099c962b137a458228811a85b8ea828bb15f238d2c1e50`.

Fresh CPU replay reproduced the known runtime/model surface but not exact stem bytes. Do **not** weaken those frozen historical stem hashes or claim full-WAV Demucs equivalence.

## Shared-context functional-equivalence diagnostic — frozen result
Checker: `validation/v168_splitmysong_diagnostic/check_shared_context_equivalence_v168.py`, creation commit `73af04264c13e5daddb5b7fc1db4e0bd9dcea149`, blob `2e9a8dc2ec60a311b3e6bca5f8dc9390aea48b0f`.

Frozen V166 identities:
- candidate SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`;
- candidate Git blob `c36a4d1e14ca66235b51a866ad3908322834efff`;
- timebase SHA256 `899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0`;
- timebase Git blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`;
- 1050 combined-Guitar events + 402 Bass events = 1452 persisted events;
- 4356 persisted `stepSelection.candidates` option rows;
- 1805 lattice steps.

Run `33564860461` returned preregistered **FAIL_CLOSED** because historical persisted option rows cover only **1617/1805 = 89.58448753462604%** lattice steps; 188 steps are uncovered.

Within all historically observed neighborhoods:
- selected-step changes 0;
- frozen-winner recomputation mismatches 0;
- stored-score recomputation mismatches 0;
- inconsistent repeated historical-support steps 0;
- max absolute shared-support drift `0.0001594903414565696`;
- max absolute event-step-score drift `1.5949034145645857e-05`.

The old 1805/1805 checker remains a valid failed diagnostic and is **not** being reinterpreted as PASS.

## 2026-09-01 artifact-provenance audit of the 188 missing steps
Repository-only audit found no admissible artifact that fills the 188 steps while satisfying exact V166 timebase + reference-blind historical shared-support provenance:
- V167 recovery/I005 additions do not persist new `stepSelection.sharedSupport` rows;
- V167 I002 and downstream calibration outputs are excluded as independent support evidence because the whole-stream timing rule was reference-facing selected;
- V165 timebase SHA256 `eaef13457f7a2d357d9f288afdeb8b9d0364f85be29b367247245cf9ed636426` differs from V166;
- V163 timebase SHA256 `bd36e645c9777719ecbbe9602fe6b25b920ccfee11204c26554d34c314d8f78d` differs from V166.

Do not interpolate/extrapolate missing shared-support values.

## 2026-09-01 new preregistered path — exact historical support at actual SplitMySong neighborhoods
A separate candidate-specific gate was preregistered **before any SplitMySong pitch inference or result was observed**. This does not alter the failed 1805/1805 diagnostic.

Preregistration:
- `debug/v168-splitmysong-diagnostic/historical-shared-support-neighborhood-preregistration.json`
- creation commit `d46eab8aa60df50ee977736857a67c9d3f53b0b1`
- Git blob `f34661e2d67f9f1c541b80ac01af2c6ea82e2159`
- status `PREREGISTERED_BEFORE_SPLITMYSONG_PITCH_INFERENCE_OR_NEIGHBORHOOD_RESULT`.

Frozen rule:
1. Historical `sharedSupport` may come only from the frozen V166 candidate's already-persisted `stepSelection.candidates` rows.
2. Repeated rows for a step must agree exactly on `sharedSupport` and shared-normalization provenance or fail closed.
3. No interpolation, extrapolation, new Demucs support substitution, reference data, or scorer data.
4. Run exactly one reference-blind SplitMySong Basic Pitch observation under the already-frozen V166 front-end.
5. After the observation, for every actual pre-grid Guitar event, determine exact frozen V166 timing options `{nearest-1, nearest, nearest+1}`.
6. **PASS only if 100% of the unique option steps actually required by the observed SplitMySong events exist in the frozen historical support table.**
7. If even one required option step is uncovered, stop with `FAIL_CLOSED_NO_CANDIDATE`; do not produce mapped/final I005 candidate and do not run a scorer.
8. If PASS, recompute only the new Guitar instrument support while using exact persisted historical V166 shared support for every consulted option; then apply frozen V167 global -12, frozen I002 `max_score_x_shared`, and exact frozen I005 `gss-active-only` downstream logic.

This is scientifically narrower than full-lattice equivalence: it claims exact historical shared-support preservation only at every timing option actually consulted by the new reference-blind candidate, not full-WAV or full-lattice Demucs equivalence.

## Historical shared-support helper — frozen and self-tested
Helper:
- `validation/v168_splitmysong_diagnostic/historical_shared_support_v168.py`
- creation commit `82b47855c1acd00a52593fde915c07bf6b5fc5b1`
- Git blob `c9b5cc1bc4076be77780d64f73d53f2a7083f94f`.

No-audio static verification workflow:
- `.github/workflows/v168-historical-shared-support-static.yml`
- current blob `4859f0fc88ac4147f9d4c7c6f2a1570a3de8ca2c` at commit `955f399273e34f684a50b6db4407af5e5b11368a`.

GitHub Actions run `33566943703`, job `100052185689`, completed **SUCCESS** on Ubuntu 24.04 / Python 3.10.21.

Static/self-test results:
- frozen identities matched;
- helper + generator Python compile PASS;
- private launcher shell syntax PASS;
- generator CLI exposes exactly `--repo-root`, `--source`, `--normalized-guitar`, `--arm-receipt`, `--environment-receipt`, `--ffmpeg-receipt`, `--output-dir`; no reference/scorer CLI input exists;
- reconstructed historical table contains 1617 covered steps from exactly 1452 events / 4356 option rows;
- historical self-validation inspected all 1452 events;
- option-step mismatches 0;
- score-recompute mismatches 0;
- winner-recompute mismatches 0;
- static report SHA256 `4f46836a084424dc0535965bcacaf4b6edced68a6cc724fa27c826b88f0a8c30`;
- no audio read, Basic Pitch inference, reference/scorer access, GPU/CUDA, or Modal use occurred in the static workflow.

## Private one-shot historical-support generator — frozen code, NOT RUN
Generator:
- `validation/v168_splitmysong_diagnostic/generate_splitmysong_historical_support_v168.py`
- creation commit `45e7847e88195d0f30609851eb239dcbc1fd350a`
- Git blob `5adfb45a69f922dc409f35350683935df518bf07`.

Private launcher:
- `validation/v168_splitmysong_diagnostic/run_private_historical_support_generation.sh`
- creation commit `898f015df6012ba4ab1f5dacc5eafb73f49d61ae`
- Git blob `9630986e86010177be3d8756185bdbded2309495`.

One-shot behavior is fail-closed:
- writes persistent attempt marker before the Basic Pitch observation;
- performs exactly one cached Basic Pitch inference through the exact frozen V166 Guitar front-end;
- immediately writes/hash-freezes `splitmysong-basic-pitch-observation.json` before evaluating the neighborhood result;
- writes/hash-freezes `splitmysong-historical-support-neighborhood-gate.json`;
- if gate fails, exits 2 with **no candidate** and launcher instructs not to rerun and not to score;
- if gate passes, builds/freeze-writes `splitmysong-i005-candidate.json`, `splitmysong-generation-receipt.json`, and `splitmysong-candidate-freeze.json` before any scorer/reference access;
- accepts no reference/scorer path.

At this checkpoint the private one-shot launcher has **NOT** been run. Therefore:
- SplitMySong Basic Pitch attempts = **0**;
- SplitMySong candidate generated = **false**;
- diagnostic reference-facing score calls = **0**;
- V168 prospective reference-facing score calls = **0**.

## NEXT SAFE ACTION
The repository/static work is complete up to the one-shot private observation boundary.

In the already-verified private Codespace, after pulling branch `v143-contextual-prune-lobo` to at least commit `955f399273e34f684a50b6db4407af5e5b11368a`, the next command is the frozen private launcher:

```bash
bash validation/v168_splitmysong_diagnostic/run_private_historical_support_generation.sh
```

Do this only in the private Codespace where the frozen input files/receipts already exist under `$HOME/v168-splitmysong-private`.

Interpretation is predetermined:
- exit/status PASS -> checkpoint the printed observation/gate/candidate/receipt/freeze SHA256 values **before** any legacy AYGGMW scorer/reference access;
- exit 2 / `FAIL_CLOSED_NO_CANDIDATE` -> checkpoint the observation + gate SHA256 and missing required steps; **do not rerun** the Basic Pitch observation and do not score;
- any other failure after the attempt marker exists -> preserve the private output directory and diagnose read-only; **do not rerun** until the failure is understood.

I cannot directly access or execute inside the user's private Codespace from the GitHub repository connector, so the one-shot private command itself remains the next execution boundary.

## Standing safety / methodology
- V168 prospective evaluation is not calibration continuation.
- Professional-reference content cannot be exposed to candidate-generation/policy code.
- Freeze candidates before any professional-reference scoring.
- No per-event reference choices, reference-event copying, post-score mutation, retuning, adverse-result song exclusion, gate weakening, or missing-support interpolation.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save this `CURRENT_STATE.md` before any future holdout admission, candidate-generation arm, scorer arm, reference-facing score call, or after receiving the private one-shot output hashes.
