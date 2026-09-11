# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 01:02 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the canonical current-state checkpoint for the fresh workstream. Use Git history for older verbose diagnostics.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference/professional scorer logic, training/fine-tuning, or broad optimizer/ISA sweeps unless explicitly requested.
- The `gomyway` filename authorizes the exact audio fixture only; it does not authorize the archived pipeline.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP execution stays in `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop MIDI/event identity. Raw sequential Basic Pitch indices are not cross-run identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.
- Duration research remains paused while upstream model-evidence validation is unresolved. Ignore unrelated duration/V3 workflows that may be auto-triggered by shared-path edits; they are not authority for this workstream.

## AUTHORIZED FIXTURE / FROZEN STRUCTURE

Fixture `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a` on `main`:
- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s
- decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- structure identity `fnv1a32:2f493225`, canonical length `19653`
- 4/4, first downbeat ~0.65016 s, 115 measures, 113 tempo segments
- beat-grid MAE ~7.14 ms, RMSE ~10.63 ms, max ~58.05 ms, accepted true
- historical structure canary run `34192662439`, job `101953726302`, commit `2a598f0f38d755faf0cd3d46543221253f1c8997`, artifact `10042777518`, digest `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

## GUARDED CPU BASELINE

`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`, contract `songsterr-fresh-cpu-note-evidence-v4`:
- 492 onsets, 1,130 candidates, 139 local unambiguous, 353 ambiguous, MIDI 40 in 97/139 selections
- role relevance/polyphony unresolved; customer eligible 0
- regression run `34309259214`, job `102332311684`, head `54d9e4792d8255d56f6aec82977ac083b9c2bae4`, artifact `10087798684`, digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`, 97/97 tests

## FIXED MODEL PATH

Architecture: frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → dedicated release authority.

Pinned where applicable: numpy 1.26.4; torch 2.14.0; huggingface-hub 1.30.0; safetensors 0.8.0; sphn 0.2.1; demucs 4.1.0; basic-pitch 0.4.0; librosa 0.11.0; soundfile 0.13.1; tflite-runtime 2.14.0; OMP/MKL/OpenBLAS/NumExpr threads = 1; `PYTHONHASHSEED=0`.

Fixed Demucs: `htdemucs_6s`, CPU, shifts 0, overlap 0.25, segment 7 s.

Model asset authority `verify_demucs_model_asset.py`:
- contract `songsterr-fresh-demucs-model-asset-v2`
- HF `adefossez/HTDemucs-6s`; pinned revision `3c5ee475be622df764938de97e4281a7b07ffa58`
- upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- `5c90dfd2.safetensors`, SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback not primary

## DURATION AUTHORITY — UNCHANGED / PAUSED

V2 remains authoritative: `estimate_selected_pitch_releases.py`, contract `songsterr-fresh-cpu-spectral-release-evidence-v2`. Input must be duration-free. Decoded BP note-off is diagnostic only; generic next onset is never duration; same-pitch reattack is censor/search boundary only. Fixed V2: hop 512, sustained-low 5 frames, minimum 0.07 s, max search 4.0 s, onset >=12 dB above floor, drop >=18 dB, floor margin >=6 dB.

V3 remains candidate-only: `estimate_selected_pitch_releases_v3.py`, contract `songsterr-fresh-spectral-activation-release-evidence-v3`; V2 executes first unchanged; fallback only for `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`. Representative 577 resolved → 661 resolved remains descriptive only.

## UPSTREAM EXECUTION POLICY — POLICY B HOSTED MEASUREMENT BASELINE / POLICY C AUTHORITY SELECTED

Policy B permits bounded upstream numerical variation only through reference-blind, fail-closed downstream invariants.

Hard rules:
- hashes/vendor/CPU/image/region are provenance diagnostics, never correctness selectors
- no reference tab, archived/pro scorer, or downstream agreement may define variation bounds
- missing/invalid comparison evidence fails closed
- observed maxima never automatically become tolerances
- no preferred hosted output, CPU, vendor, hash, or runner may be selected
- `modelValidationComplete` stays false until a justified admission contract is implemented, tested, and independently demonstrated

Demucs evidence already established: same-run exact determinism (`34435154554`), hosted cross-run exact variation (`34436134514`), dispatch causality (`34438368530`), and failed cross-vendor common-AVX2 byte portability (`34439594582`, five observations, three exact groups). Those hosted portability failures motivated the separately defined Policy C pinned-compute authority; they are not authority-selection evidence themselves.

## MODEL-EVIDENCE MEASUREMENT CONTRACTS — GREEN / NON-PROMOTIONAL

Pair comparator `compare_basic_pitch_cross_run_evidence.py`:
- contract `songsterr-fresh-basic-pitch-cross-run-variation-measurement-v1`
- commit `aae62eba938814a9d38dcf08f39cfdfa0456b4d9`; CI `34539883074` green
- semantic key `(nearestStructureSlot, selectedMidi)`; argument-order invariant; malformed/incomparable evidence fails closed
- measurements only; no threshold/admission/validation/delivery promotion

Per-run aggregator `aggregate_basic_pitch_cross_run_measurements.py`:
- contract `songsterr-fresh-basic-pitch-cross-run-variation-measurement-set-v1`
- commit `d3b99a1c1fffd6fde8c13c0a0b9af89673749391`; CI `34544408404`, job `103093808844`, green
- recomputes every pair, requires complete pair set, binds runtime/evidence identities, validates fixed source/structure/model/packages/thread env; envelope is descriptive-only

History accumulator `accumulate_basic_pitch_measurement_sets.py`:
- contract `songsterr-fresh-basic-pitch-cross-run-measurement-history-v1`
- commit `3951e61d75720bad855dc3d7f0d85c60af02df1f`; CI `34545931556`, job `103098411035`, green
- rejects duplicate sets, contract drift, incomplete pairs, altered envelopes/hash groups, or promotional boundaries
- historical frequency/runtime associations remain non-admissible diagnostics

History-only canary:
- `.github/workflows/songsterr-fresh-model-evidence-history-canary.yml`, commit `21f72e8cf7bd8528b6a2d686452133b4d8ae1095`
- run `34546052846`, job `103098786394`, success; artifact `10179043243`, digest `sha256:ef50a11df633bc6da5e795e64880e56ebed38bbb4a99f036f096c197a1f23cd7`
- machine-produced history: 2 sets, 6 observations, 6 within-set pairs, identical descriptive envelopes, 2 exact stem/evidence outcomes
- formal set digests `11794be2d8aab09301cef2e391926a30bc7f3bb1dd7931901f9b7971a2e4b451` and `d66206cc2db467c46150c9e0069fcc38ba5f82cebc1a253cf235aa91cd7df019`

## AUTHORITATIVE REAL-MODEL REPRODUCIBILITY BASE

Run 3 `34540837228`: A/B = 1,139-event outcome; C = 1,138-event outcome.
Run 4 `34544587948`: A/C = 1,138-event outcome; B = 1,139-event outcome; formal aggregate job `103095712976`; artifact `10178691537`, digest `sha256:a7d195f273a95e82691aea15d3dd40e3ad32f9039b8976eb0b851db634d5b4d0`.

Across six independent observations:
- exactly two repeated stem/note/activation/evidence outcomes
- 1,139-event: stem `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`, note `1e41a51a3463aa87b3d4c76f8e4cccadcb708dd3d1f51ae6895b950269a61024`, activation bundle `4d2c1c7af035e26ff86919fb169354676bc35b56658d306c7410a94f573f1151`, canonical evidence `30abdfa67dd43547629bba10c19474e5b6b304ab07bc521bd57b76c0839d3c86`; observed 3/3 on EPYC 9V74
- 1,138-event: stem `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`, note `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`, activation bundle `5e1aa1f76bfb2b3dae77f6aeb6bf6dd1fc5f84e102292dd12a5432683b330159`, canonical evidence `475c501a5d44b605eab623f2c5a6b22e962aaf13d7baa9a9d208566d01eca501`; observed 3/3 on EPYC 7763
- CPU association is descriptive only; neither CPU/output is preferred
- only semantic inventory difference: one MIDI-64 event at frozen slot `206.22657596371883`, present in 1,139 outcome
- 1,138 common events: source-start delta exactly 0.0 s
- note-span amplitude (`confidence`) max delta `0.0124053955078125`; diagnostic model-end max delta `0.6398326530612053` s
- no observed value is an admission tolerance

## BASIC PITCH 0.4.0 REPRESENTATION SEMANTICS

Exact upstream `v0.4.0` source was inspected.

Timing:
- `FFT_HOP=256`, `AUDIO_SAMPLE_RATE=22050`, nominal frame spacing ~11.61 ms
- note starts are frame indices mapped through `model_frames_to_time`, which includes window alignment correction and a hard-coded 0.0018 s alignment term
- this is a representation scale, not a justified one-frame acceptance tolerance; common-event onset drift observed so far is exactly 0

Candidate confidence:
- decoder tuple amplitude is mean note-frame activation across decoded note span, not onset peak/probability
- current field names `confidence` / `onsetConfidence` are legacy/misleading, although calibration already says `basic-pitch-note-amplitude-not-calibrated-probability`
- V2/V3 do not use it; deterministic evaluator uses it only in descriptive diagnostics
- evaluator contract commit `272b8430ff6d016fff2692ed621380b9a63e9115` explicitly declares `candidateConfidenceUsedForAcceptance:false`, `candidateConfidenceDiagnosticsOnly:true`
- behavior/contract test `test_candidate_confidence_diagnostic_only.mjs`; final focused CI run `34546370247`, job `103099775575`, success
- therefore do not define a confidence admission threshold

Decoder mechanics relevant to the MIDI-64 toggle:
- Basic Pitch 0.4.0 constrains returned model matrices to the requested frequency range in-place before decoding
- effective onsets are `max(raw onset, inferred onset from positive note-frame differences)` via `get_infered_onsets(..., n_diff=2)`
- thresholded strict local peaks are one decoder path, but `melodia_trick=True` can create notes from residual frame energy without a thresholded onset peak
- therefore an unmatched event must not be presumed to be a simple 0.5 onset-threshold crossing

## DECISION-SURFACE DIAGNOSTICS — IMPLEMENTED / MEASUREMENT ONLY

Same-inference sidecar `scripts/songsterr-fresh/basic_pitch_decision_surface_diagnostic.py`:
- contract `songsterr-fresh-basic-pitch-decision-surface-diagnostic-v1`
- commit `31ab584a2fe97ca9f29e2d0ed90a351d150aa18b`
- captures frequency-constrained raw onset surface and exactly reconstructed v0.4.0 effective onset surface over MIDI 40–88
- binds to existing same-inference note identity + activation bundle; frame times remain owned by activation bundle
- hard guards: diagnostic-only, not acceptance, not duration, no sourceEnd/duration writes, no pitch/inventory mutation, no reference/pro/V143
- focused CI `34546596926` green

Reference-blind comparator `scripts/songsterr-fresh/compare_basic_pitch_decision_surfaces.py`:
- contract `songsterr-fresh-basic-pitch-decision-surface-comparison-v1`
- commit `6233f3ba6d1d78bf82951884184c055d80f070cc`; test wiring `73ad82969ff54df4c9a888c1c4cacae5b5a05f29`
- focused CI run `34546754254`, job `103100986508`, success
- verifies evidence/activation/decision same-inference binding and equal frame-time identity
- measures full raw-onset/effective-onset/note-frame surface variation
- for each unmatched semantic event samples both outputs at the event's decoded frame/MIDI: raw/effective onset, note-frame activation, threshold margin, strict-peak state, and local three-frame maxima
- threshold margin is descriptive only; unmatched event is explicitly not automatically a threshold failure

Transcriber integration:
- commit `36d72001d913c756bfd1ce0e9373ed1224a8b3cf`
- optional `--decision-surface-output` requires activation output and derives from the same single `predict()` return
- main decoded-note JSON is intentionally unchanged by this optional sidecar, preserving historical note/evidence identity semantics
- shared-path edit auto-triggered several unrelated fresh workflows, including duration/V3 workflows. They are out of scope and must not be used to resume paused duration research.

Exact decoder-mechanism replay tracer:
- `scripts/songsterr-fresh/trace_basic_pitch_decoder_mechanisms.py`
- implementation commit `9b4515fddd2ed6605a5494b0e75dc3cdfa390463`
- replays Basic Pitch 0.4.0 decoder mechanics from captured same-inference matrices only; no second model invocation
- must reproduce the existing evidence event multiset before labeling events by decoder pass (`threshold-onset` vs `melodia-residual`)
- remains measurement-only/reference-blind/non-promotional and may not define acceptance or duration
- focused-CI wiring commit `b5a625a4ce12f530af2a63a0e52c5c8728fa9fef`; fresh chat should verify that focused CI result/self-test before relying on tracer output

Decision-enabled real model canary — COMPLETED GREEN:
- `.github/workflows/songsterr-fresh-model-evidence-cross-run-measurement-canary.yml`
- head `a9671f746935fe18da1c0c48807b81ce4d1ce590`
- run `34546969446`, success
- observation jobs: A `103101649728`, B `103101649915`, C `103101649838`; all success
- aggregate comparison job `103103047931`, success
- aggregate artifact `10179540711`, digest `sha256:b278ab9b685bec32e9771083a158f9a51eed82f43db3c6e29d34346acaaee22f`
- observation artifacts: A `10179528439` (`sha256:64824573cb007b4878c5b34299b2d4838909b44bd2a1f3bae158a66017ccbf6b`), B `10179504174` (`sha256:1f60d0da7a6d39ef9ec4af42a0c1b2025a4209c456d196e4a6108b9519786b2b`), C `10179525061` (`sha256:e5ebea045452b0e8d2fe74b1f2bc94f0dc923162f8cb817a6823b992ec78c524`)
- all three observations used unchanged Demucs/Basic Pitch numerical settings, one `predict()` each, label-specific activation/decision sidecars, duration-free evidence, and all pairwise model-evidence + decision-surface comparisons
- aggregate non-promotion guard passed; no numeric diagnostic became pass/fail or an admission bound
- preliminary inspection of observation B: hosted runner CPU `Intel Xeon Platinum 8573C`, 1,139 decoded events, new exact stem/note/activation hashes relative to the earlier six-observation AMD history, and the historical MIDI-64 event at frozen slot `206.22657596371883` is absent
- therefore event count alone is not a semantic-output signature, and the earlier AMD CPU/output association must not be generalized or used as an admission selector

## ACTIVE WORK LOG — A/B/C DECISION SURFACE + DECODER REPLAY

- Inspected completed green run `34546969446` directly: aggregate artifact `10179540711`; observations A `10179528439`, B `10179504174`, C `10179525061`. No Demucs or Basic Pitch rerun was performed.
- A=1138 events, B=1139, C=1138. Across A/B/C there is exactly one unmatched semantic event: MIDI `55` at frozen slot `46.151111111111106`, source start `46.20240952380952` s, present only in B.
- Historical MIDI-64 slot `206.22657596371883` presence is A=0, B=0, C=0; new MIDI-55 slot presence is A=0, B=1, C=0. B's 1,139-event result is therefore not the historical 1,139 semantic inventory.
- At the unmatched MIDI-55 frame, B's captured effective onset is `0.5000237822532654` with threshold margin `2.378225326538086e-05`; A/C is `0.49999192357063293` with margin `-8.07642936706543e-06`. Both are strict local peaks. This observed sample toggles on the threshold-onset path; these margins are descriptive only and are not admission tolerances.
- Tracer focused CI wiring commit `b5a625a4ce12f530af2a63a0e52c5c8728fa9fef` failed in run `34547372731`, job `103102811353` because the synthetic intended-melodia activation `0.7` scaled to inferred onset about `0.7875`, so it entered the threshold-onset pass. The synthetic fixture only is now `0.4`, which remains above frame threshold `0.3` while inferred onset is about `0.45`, below onset threshold `0.5`. No model, production threshold, admission, or duration setting changed.
- Repaired tracer self-test passed in helper run `34550328840`. Exact replay against captured sidecars: A PASS eventCount=1138 mechanisms={'melodia-residual-pass': 128, 'threshold-onset-pass': 1010} target55=none; B PASS eventCount=1139 mechanisms={'melodia-residual-pass': 128, 'threshold-onset-pass': 1011} target55=threshold-onset-pass; C PASS eventCount=1138 mechanisms={'melodia-residual-pass': 128, 'threshold-onset-pass': 1010} target55=none. Decoder labels are trusted only where exact replay succeeded.
- Official focused variation-test CI for tracer-fix commit `ab87287d1d951fcd9988d9d4c017b7a765660cb0`: run `34550351149`, conclusion `success`, jobs `103111767249:success`.
- `modelValidationComplete` remains false; customer-eligible events remain 0; duration research remains paused.

## DECODER TRACE COMPARISON — IMPLEMENTED / REAL A-B-C MEASURED

- `scripts/songsterr-fresh/compare_basic_pitch_decoder_traces.py`, contract `songsterr-fresh-basic-pitch-decoder-trace-comparison-v1`, commit `6a752b820db3e572ce23167f346954b80123de6b`.
- Reference-blind, argument-order invariant, measurement-only, and fail-closed unless each input trace declares exact evidence replay plus all non-promotion guards. It compares semantic inventory, common-event decoder mechanism, and decoder frame-span variation; observed values cannot become admission tolerances.
- Focused CI wiring commit `ce9f28b9ae4ecb5bc60331349f4e70ff2a6f8442`; run `34550527914`, job `103112287283`, success.
- Real trace comparison execution run `34550610640` reused exact traces from replay artifact `10180559766` (`sha256:46f918d841c86f3c15c3c2177791d95fb0e414cd3a52196cd34625e490cb49e4`); no model rerun.
- A/B: 1138 common paired events, 1 unmatched semantic event, 0 common mechanism mismatches; decoder-start differs for 1 common event (max 7 frames), decoder-end differs for 1 (max 20 frames). Max common source-start delta `0.08126984126983672` s; diagnostic model-end delta `0.23219954648526198` s; note-span mean-activation delta `0.09106314182281494`.
- A/C: 1138 common paired events, 0 unmatched, 0 mechanism mismatches; start/end different counts 0/0 with maxima 0/0 frames. A and C remain exact at trace level.
- B/C matches the A/B pattern: 1138 common, 1 unmatched, 0 common mechanism mismatches; start/end maxima 7/20 frames.
- Mechanism identity is stable for every common A/B/C semantic event in this sample. The only semantic inventory instability remains the B-only MIDI-55 threshold-onset event; this does not justify an admission band around 0.5.

## DECODER TRACE CANARY FOLLOW-UP — AUTOMATED / LATEST GREEN

- Permanent workflow `.github/workflows/songsterr-fresh-decoder-trace-followup.yml` automatically runs after each successful `Songsterr Fresh Model Evidence Cross-Run Measurement Canary` on `songsterr-fresh-pipeline-v1`.
- It reuses that canary run’s already-captured A/B/C evidence + activation + decision sidecars; it does not invoke Demucs or Basic Pitch. Each trace must exactly reproduce its bound evidence before pairwise mechanism labels are accepted.
- It runs the tracer/comparator self-tests, writes A/B/C exact decoder traces, writes pairwise decoder-trace comparisons, enforces all non-promotion guards, and uploads one trace-evidence artifact.
- Latest source canary run `34546969446` at head `a9671f746935fe18da1c0c48807b81ce4d1ce590`; automatic trace follow-up run `34551100451`.
- Latest trace artifact `10180829255`; digest `sha256:3e30caba4a420bd8204cd95e7b34b66294bcfd8a9bfd492762be097728422b42`; expires `2026-09-25T01:33:09Z`.
- A/B: common=1138, unmatched=1, mechanismMismatch=0, startDiff=1 max=7, endDiff=1 max=20.
- A/C: common=1138, unmatched=0, mechanismMismatch=0, startDiff=0 max=0, endDiff=0 max=0.
- B/C: common=1138, unmatched=1, mechanismMismatch=0, startDiff=1 max=7, endDiff=1 max=20.
- This automation preserves mechanism-level measurement evidence for future independent canaries. It does not create an onset tolerance, choose a preferred CPU/output, mark model validation complete, or resume duration work.
- Prior helper failures `34550779925`, `34550819480`, and `34550900008` were integration mechanics only. The last helper successfully built the intended canary diff but GitHub correctly rejected its workflow-file push because Actions `GITHUB_TOKEN` lacks workflow-file write scope; no model/pipeline behavior was changed by those failures.
- `modelValidationComplete` remains false; customer-eligible events remain 0; duration research remains paused.

## POLICY B INDEPENDENT NUMERICAL-GUARANTEE REVIEW — NO JUSTIFIED BOUND

- Reviewed upstream framework contracts rather than fitting the observed A/B/C envelope.
- PyTorch reproducibility documentation states that complete reproducibility is not guaranteed across releases, commits, or platforms, and its deterministic-algorithm guarantee is scoped to the same software and hardware with the same input. Source: https://docs.pytorch.org/docs/stable/notes/randomness.html
- PyTorch numerical-accuracy documentation states that floating-point computations that are mathematically identical are not guaranteed to be bitwise identical across platforms because finite precision and operation ordering affect results. Source: https://docs.pytorch.org/docs/main/notes/numerical_accuracy.html
- TensorFlow's compatibility policy explicitly excludes floating-point numerical details from compatibility guarantees and tells users to rely on approximate accuracy/numerical stability rather than specific computed bits. Source: https://www.tensorflow.org/guide/versions
- TensorFlow Lite/LiteRT documentation exposes implementation-dependent/platform-dependent CPU execution choices (for example interpreter threading/default delegates) but does not provide an end-to-end numerical error bound that can be propagated through Demucs → Basic Pitch into a safe onset-threshold uncertainty interval. Source: https://www.tensorflow.org/api_docs/python/tf/lite/Interpreter
- Therefore there is no documented upstream contract that independently justifies turning the observed `0.5000237822532654` versus `0.49999192357063293` crossing, the 7/20-frame trace drift, float32 ULP scale, or any current historical envelope into an admission tolerance.
- Policy B consequently has **no justified admission contract for threshold-boundary semantic inventory toggles** under the current supported stack. Additional observations may characterize frequency/shape of variation but cannot manufacture a correctness bound.
- This is a fail-closed result, not a model-quality verdict: `modelValidationComplete` remains false, customer-eligible events remain 0, and duration research remains paused.

## POLICY B NUMERICAL BOUND RESEARCH — COMPLETED / NO JUSTIFIED END-TO-END BOUND

- Detailed research: `docs/checkpoints/SONGSTERR_FRESH_POLICY_B_NUMERICAL_BOUND_RESEARCH.md`, commit `5baa4d7837401b68f2f8198bc522c48f705cdaf9`.
- Basic Pitch v0.4.0 decoder semantics use strict local maxima followed by `peak_thresh_mat >= onset_thresh`; the library defines a hard threshold, not an uncertainty/dead-band around 0.5.
- Spotify Basic Pitch v0.4.0 tests use `atol=1e-4, rtol=0` for the fixed `vocadito_10.wav` model-output arrays and expected note events, and its CI spans Ubuntu, Windows, and macOS. This is project regression-test tolerance for that fixture, not a documented arbitrary-input or end-to-end error guarantee.
- The fresh Linux/Python 3.10 Basic Pitch path uses `tflite-runtime`, while the full fresh chain also includes Demucs/PyTorch upstream. PyTorch does not provide complete reproducibility across releases/platforms, and TensorFlow determinism guidance likewise depends on controlled hardware/software conditions. No independent worst-case activation-error envelope for Demucs → Basic Pitch was found.
- Float32 machine epsilon alone cannot justify a decoder-threshold band because no independently established forward-error/Lipschitz bound exists for the full decoding/resampling → Demucs → Basic Pitch → inferred-onset/local-peak chain.
- Therefore Spotify’s `1e-4`, the observed A/B/C margins, current matrix maxima, current 7/20-frame drift, CPU/vendor identity, exact hashes, event frequency/count, candidate confidence, downstream agreement, or reference/professional tabs may not be used as an admission tolerance.
- Policy B currently has **no independently justified numerical admission contract** for threshold-boundary inventory toggles. The B-only MIDI-55 threshold-onset event remains unresolved model-evidence variation rather than something that may be absorbed into a fitted band.
- `MODEL_EVIDENCE_VALIDATION_PENDING` remains active. `modelValidationComplete` remains false; customer-eligible events remain 0; duration research remains paused.

## SEMANTIC CONSENSUS GATE ANALYSIS — REJECTED AS POLICY B ADMISSION PROOF

- Added `scripts/songsterr-fresh/analyze_semantic_consensus_gate.py`, contract `songsterr-fresh-semantic-consensus-gate-analysis-v1`, as a reference-blind/non-promotional policy analysis; it implements no admission rule.
- Focused CI wiring commit `80a5d375bd205c23567ebc7d8980255ca6025cc7`; run `34551361626`, job `103114768116`; the consensus analysis self-test and all existing fresh measurement/non-promotion checks passed.
- For N independent executions with semantic-mode probabilities p_i, an unanimity gate passes with probability `sum(p_i^N)`. If more than one semantic mode is possible, unanimity can still pass on one non-universal mode.
- Distribution-free worst case: for any finite N and any desired error delta > 0, choose a two-mode process with probabilities `1-epsilon` and `epsilon` small enough that `(1-epsilon)^N + epsilon^N > 1-delta`. Thus no finite unanimity count has a false-pass upper bound below 1 without an independently justified execution-distribution assumption.
- Hosted runs are also not proven independent draws across all supported compute surfaces; correlated runs can agree because they share a hidden environment while another supported environment produces different semantics.
- Historical outcome frequencies cannot repair this because current policy forbids promoting observed frequency into correctness. Requiring more runs therefore characterizes reproducibility but does not prove universal semantic portability.
- Result: finite semantic-consensus/repeated-execution gating is **not justified as a Policy B customer-admission contract**. `modelValidationComplete` remains false, customer-eligible events remain 0, and duration research remains paused.

## POLICY C PINNED COMPUTE AUTHORITY — IMPLEMENTED / HARDENED / UNENROLLED

- User explicitly authorized the architecture/policy change after Policy B numerical-bound and finite-consensus approaches were shown insufficient.
- Policy C defines one explicitly enrolled Linux x64 reproducibility surface as the only authority-eligible Demucs → Basic Pitch execution surface. GitHub-hosted model runs remain measurement/history evidence only; there is no hosted fallback.
- Architecture contract: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`, original architecture commit `31a351e33e952686de4d8e9a5d6fe6239a3b35e1`.
- Manifest `scripts/songsterr-fresh/pinned_compute_authority_v1.json`: current `enrollmentStatus=UNENROLLED`; no enrolled fingerprint exists and no model output has authority status yet.
- Fail-closed verifier `verify_pinned_compute_authority.py` binds CPU/model/family/stepping/microcode/features, logical CPU count, kernel/libc, Python interpreter hash/version, Node/FFmpeg executable hashes/versions, exact named package versions, NumPy/PyTorch build configuration, deterministic thread/hash environment, and a full installed Python-distribution lock. Full-distribution-lock hardening commit `1701dabd40d52517df8fa09e4c8d4f9bfbcfe9af` catches transitive/package-content drift as authority drift.
- Hardened focused CI run `34552705768`, job `103118742497`, success: verifier, full-distribution drift, single-canary non-promotion, three-canary exactness/non-promotion, and all previous fresh measurement guards passed.
- Dedicated bootstrap `scripts/songsterr-fresh/bootstrap_pinned_compute_authority.sh`, commit `77a5261e05267eed3b8e3501a3a36becc0b16538`, creates `/opt/songsterr-fresh-authority/venv` once and installs the exact named model package set; it does not accept or persist GitHub runner credentials.
- Authority workflow `.github/workflows/songsterr-fresh-pinned-compute-authority.yml`, hardened commit `c69059ab1939ca69ed4eec9b27679c5bb15e06de`, requires `[self-hosted, linux, x64, songsterr-fresh-authority-v1]`, prepends only the dedicated authority venv, verifies Python 3.10 / Node 22 / FFmpeg and the enrolled fingerprint before model execution, has no automatic model trigger, installs no model dependencies during a canary, and has no hosted fallback.
- Enrollment runbook `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_ENROLLMENT.md`, commit `d370e9728164d7985b5590beb187e5324508780d`, defines persistent-host provisioning, GitHub runner registration with `--disableupdate`, safe probe, deliberate fingerprint enrollment, ≥3 separate exact canaries, aggregation, and drift/re-enrollment procedure.
- Bootstrap/static coverage commit `adf8146f8ca2ed7efa0b7ff71948bee1b0bed898`; run `34553026675`, job `103119686510`, success. Bootstrap shell syntax plus all Policy C fail-closed/non-promotion contracts passed.
- Cloud/VM use is acceptable only as a reproducibility surface because every canary verifies the exact enrolled fingerprint before model execution. A materially changed VM/hardware/software surface fails closed and requires re-enrollment; Policy C is not a physical-host security attestation.
- Current budget path: a persistent DigitalOcean authority host is deferred because the available $24-$48/month options are over the user budget; the connected DigitalOcean team also still reports a billing restriction. A separate non-authority GitHub Codespaces workbench is now implemented at `.devcontainer/songsterr-fresh-workbench/devcontainer.json`, targeting the smallest 2-core / 8 GB / 32 GB Codespaces class. Bootstrap `.devcontainer/songsterr-fresh-workbench/setup.sh` installs/reuses the exact pinned model stack and writes a prerequisite-valid workbench probe; `scripts/songsterr-fresh/run_codespaces_workbench_measurement.sh` runs one full measurement-only frozen-structure → Demucs → Basic Pitch → duration-free-evidence path while recording runtime, max RSS, and output identities. Codespaces output is explicitly `authorityEligible=false`, `modelValidationComplete=false`, customer eligible events 0, and cannot change duration authority. The first Codespaces measurement attempt stopped before structure/Demucs/Basic Pitch because the exact authorized source blob matched `4dd709e3fa177b4daeed71ca97f0199757729d4b` but the Codespaces FFmpeg decode produced separation WAV SHA-256 `2d6e13d1a8e1f1ec8e35acaaebe9f8877ee3a308302063e753ce75fee1e208c1` instead of the authority baseline `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`. This is an environment/decode-byte difference, not a source-fixture or model failure. Workbench measurement contract v2 now records decode/structure differences diagnostically and continues the performance benchmark while remaining `authorityEligible=false`; the Policy C authority workflow and manifest remain strict and unchanged. Codespaces workbench measurement v2 has now completed successfully on the user-available 4-core Codespace at source commit `3faf16b740846ebd3106d81cb1cf1dcefe1001d5`. Measured wall times: structure 31 s, Demucs 236 s, Basic Pitch 11 s, total 283 s (4 min 43 s). Peak resident memory: Demucs 2,492,104 KiB (~2.38 GiB) and Basic Pitch 396,552 KiB (~387 MiB). The frozen structure remained accepted and exactly matched `fnv1a32:2f493225`. This establishes that the 4-core / 8 GB Codespaces workbench is operationally sufficient with substantial memory headroom; it is performance/capacity evidence only, not authority evidence. The observed ~2.38 GiB Demucs peak means a future fixed authority surface should have at least 4 GB RAM for practical headroom; 2 GB is not sufficient. Policy C remains `UNENROLLED`; `authorityEligible=false`, `modelValidationComplete=false`, customer-eligible events remain 0, and no authority host, enrolled fingerprint, authority probe, or authority canary exists. Next: stop the 4-core Codespace when idle, use the completed measurement as capacity evidence, and choose the lowest-cost fixed authority surface with at least 4 GB RAM; do not pay for a larger 8 GB authority host solely on memory grounds.
- Measurement preservation helper `scripts/songsterr-fresh/preserve_codespaces_workbench_measurement.sh`, commit `69a293c334e8d8d1f130910b5372ef1faff7c184`, validates the completed workbench v2 summary and copies only the small non-authoritative JSON into `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_WORKBENCH_MEASUREMENT_V2.json`; all promotion guards must remain false and all five output identities must be valid SHA-256 values.
- Low-cost authority review `docs/checkpoints/SONGSTERR_FRESH_LOW_COST_AUTHORITY_OPTIONS.md`, commit `2a790a309449ef93c1fc8bda2252ffa081dd69cc`: completed Codespaces capacity evidence makes 4 GB RAM the minimum practical target. Provider-owned pricing checked 2026-09-10 makes OVHcloud Canada VPS-1 the current preferred budget candidate at 2 vCores / 4 GB / 40 GB NVMe from CAD $6.20/month with Ubuntu 22.04 available. IONOS Canada is a fallback; DigitalOcean 4 GiB remains USD $24/month and over budget. No provider has been purchased or enrolled.
- Provider-specific provisioning runbook `docs/checkpoints/SONGSTERR_FRESH_OVHCLOUD_AUTHORITY_RUNBOOK.md`, commit `ce2c206d8a883b5776ec657bf5f1e2078b9c6b6b`, pins the first paid candidate to OVHcloud Canada VPS-1 only: 2 vCores / 4 GB / 40 GB NVMe, Ubuntu 22.04 x64, no paid extras, fail closed on plan mismatch/OOM/drift, then existing Policy C bootstrap → sole self-hosted runner → probe → deliberate enrollment → ≥3 exact canaries. Purchase has NOT occurred; this remains the explicit spending boundary.
- Preserved Codespaces measurement committed at `c7c1d5ef1d8c44fe40db597fec554bf590e76028` in `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_WORKBENCH_MEASUREMENT_V2.json`; verification passed. Exact identities: guitar stem `4bbcefd2b8bdf057af407640604106dc6438560155c378290ccc8b3e1ac9c656`, note inference `8691a162c53b9894b5e3c4f9ddf86695ae8b7b33dc2d465517d2388c99535f63`, activation bundle `92f14a4c18c53b6e1b0490adde45e72da17de0e32e565770a1d8fc7e1246273d`, decision surface `1d089df0116313f20252d3db84fdc21a142e7101e083a0a881d8e6cc508a619f`, canonical evidence `dacd303abb868eb5d5e15877337ac67afeb6f23ebb2aa0cd3f5550810a6172da`. Source blob and frozen structure identity both match their authorized baselines; decode-byte identity differs only diagnostically. All non-promotion guards remain false/zero. The Codespace may now be stopped or deleted without losing this summary evidence; do not enroll its fingerprint.
- `modelValidationComplete` remains false; customer-eligible events remain 0; duration research remains paused. V2 remains authoritative and V3 candidate-only.

## POLICY C-S CODESPACES SESSION AUTHORITY — IMPLEMENTED / NOT YET REAL-QUALIFIED

- User has GitHub Pro Codespaces available and a payment method configured. Official GitHub billing docs checked 2026-09-10 show 180 included Codespaces core-hours/month and 20 GB-month storage for personal GitHub Pro. On the user-available 4-core machine this is about 45 active wall-clock hours before paid compute overage, assuming personal-account billing and remaining monthly quota. Because payment details are present, a Codespaces budget with `Stop usage when budget limit is reached` is recommended; stopped Codespaces stop compute billing but storage remains metered while the Codespace exists.
- Policy C-S is an alternate zero-cost-first authority mode and does NOT alter persistent Policy C. `scripts/songsterr-fresh/pinned_compute_authority_v1.json` remains `UNENROLLED`; Codespaces must not be enrolled into that persistent manifest.
- Architecture/runbook: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`, implementation-doc commit `172a857a1b4af8a7579efb04f48274992cf40548`.
- Session verifier `scripts/songsterr-fresh/codespaces_session_authority.py` binds one authority epoch to GitHub Codespaces Linux x64, a clean exact `songsterr-fresh-pipeline-v1` source commit, the existing hardened Policy C compute/toolchain fingerprint, SHA-256 of the current Linux boot ID, >=4 logical CPUs, and >=4 GiB reported RAM. Raw boot ID, machine-id, network identity, and user identity are not persisted.
- Explicit `probe` does not enroll. Explicit `enroll` creates a new UUID authority epoch only after the literal `SESSION_BOUND_AUTHORITY_EXPIRES_ON_RESTART` acknowledgement. Enrollment alone does not qualify the session. Stop/restart/rebuild, source change, or compute/toolchain drift fails closed; a fresh epoch never inherits prior model-validation or delivery state.
- Canary path: `run_codespaces_session_authority_canary.sh` verifies the exact enrolled epoch immediately before model execution, reuses the already-proven workbench full model path, verifies the same epoch immediately afterward, then `build_codespaces_session_authority_canary.py` validates authorized source, frozen reference-blind structure, exact Demucs asset, duration-free evidence, same-inference note/activation binding, decision-surface non-promotion guards, and exact output identities.
- Qualification path: `qualify_codespaces_session_authority.sh` executes three distinct canaries (IDs 1/2/3), then `aggregate_codespaces_session_authority_canaries.py` requires the same epoch/session/boot/source/fixed-input identity and exact stem/note/activation/decision/evidence/event-count identity across all three. A green result sets only `sessionAuthoritySurfaceQualified=true` for that current boot session.
- Pure contract CI run `34560456258`, job `103141926595`, succeeded: Python compile, shell syntax, boot/source/compute drift fail-closed tests, single-canary non-promotion, and exact three-canary aggregation tests all passed. No Demucs/Basic Pitch model run occurred in that CI test.
- `.devcontainer/songsterr-fresh-workbench/setup.sh` now distinguishes persistent Policy C (never enrolled by Codespaces) from optional explicit Policy C-S. Setup itself enrolls neither authority mode.
- LIVE POLICY C-S QUALIFICATION SUCCEEDED on the user's active 4-core Codespace boot session at source commit `b2f246769340e4f7f6929e679692956c731efd93`. Terminal output reported `CODESPACES_SESSION_AUTHORITY_QUALIFICATION_COMPLETE`, `surfaceQualifiedForCurrentBootSession=true`, `canaryExecutions=3`, authority epoch `263237f0-b5dc-4710-bef4-e0ac855c2312`, session fingerprint `665db72ea170c6ebc51ad34348158bb12a5ded423068519f0281f4c67121ccef`, base compute fingerprint `f2ef7b579bc41b071e3856b1e02e46bc60acfc43f5d0ef7f440026ddc00bd449`, and boot-id SHA-256 `df14d2784ffff900225b7c48b2d231ee6154ab14eae95b787a55c7c59499db2d`. The exact three-canary aggregator therefore demonstrated reproducibility for this current boot session only. `modelValidationComplete=false`, customer-eligible events remain 0, `durationAuthorityChanged=false`. Stopping/restarting/rebuilding or source/fingerprint drift invalidates this qualification.
- Even after a green C-S qualification: `modelValidationComplete:false`, customer-eligible events remain 0, duration research remains paused, and a separate model-evidence validation review is still required. A new Codespaces epoch may not inherit that review automatically.

## QUALIFIED CODESPACES MODEL-EVIDENCE REVIEW — COMPLETED / NON-PROMOTIONAL

- Policy C-S live session remained verified before and after the read-only model-evidence review; source commit `b2f246769340e4f7f6929e679692956c731efd93`, session fingerprint `665db72ea170c6ebc51ad34348158bb12a5ded423068519f0281f4c67121ccef`.
- Qualified session produced exactly 1,140 events across its three qualification canaries. Hosted observation A baseline contains 1,138 events. The qualified-session decoder inventory is 1,012 threshold-onset-pass + 128 melodia-residual-pass.
- Exactly two semantic count mismatches exist relative to hosted A.
- MIDI 55 at frozen slot `46.151111111111106`, source start `46.20240952380952`, is the historical boundary event. It is reproducible on the qualified C-S surface and uses `threshold-onset-pass`, but independent CQT support is weak/contradictory: local semitone rank 2, octave rank 2, selected-minus-best-semitone `-0.09838294982910156 dB`, selected-minus-best-compared-alternative `-10.063761711120605 dB`.
- MIDI 64 at frozen slot `79.60816326530613`, source start `79.62614058956916`, is the second qualified-session-only event. It uses `threshold-onset-pass` and has stronger independent CQT support: local semitone rank 1, octave rank 1, selected-minus-best-semitone and selected-minus-best-compared-alternative both `+3.947506904602051 dB`.
- These observations explicitly separate reproducibility from model correctness. The MIDI-55 event is a concrete counterexample to promoting a stable C-S output merely because it is exact across repeated executions.
- The independent pitch-support probe remains descriptive only. No threshold may be back-fit from these observed examples, and neither mismatch may be used to define an admission cutoff post hoc.
- Detailed record: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_MODEL_EVIDENCE_REVIEW.md`.
- Next model-validation research is preregistered in `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`: a new two-channel audio-domain corroborator (harmonic-stack spectral competition + independent time-domain periodicity competition) must be frozen and pass controlled synthetic fixtures before any execution on the authorized song. The already-observed CQT values may not tune it. A new Policy C-S epoch will be required for eventual authorized-song evaluation.
- Therefore `modelValidationComplete:false`, customer-eligible events remain 0, `mayAdvanceDelivery:false`, and duration research remains paused.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 authoritative; V3 candidate-only. Basic Pitch is not ground truth. No reference scorer/tab/archive logic. No BP end as duration. No generic next-onset duration. No same-pitch-reattack default. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, or downstream agreement.

## FRESH-CHAT NEXT ENGINEERING STEPS

1. Treat Policy B numerical-bound research and finite semantic-consensus analysis as completed negative results; do not revive threshold fitting or hosted unanimity as customer admission rules.
2. Policy C code, hardening, bootstrap, enrollment runbook, and focused CI are complete and green, but authority remains `UNENROLLED`. Keep `modelValidationComplete:false`, customer-eligible events at 0, and duration research paused.
3. Budget-first Codespaces capacity test is complete: the available 4-core / 8 GB workbench finished the path in 283 s with Demucs peak RSS ~2.38 GiB. The workbench remains non-authority by default; optional Policy C-S may qualify one exact active Codespaces boot session only after explicit probe/enrollment and three exact canaries.
4. Before real Policy C-S work, ensure GitHub Codespaces usage/budget is acceptable, update the existing Codespace to the final branch commit, keep the worktree clean, and do not pull/commit/rebuild/restart after enrollment. Setup must still report persistent Policy C authority false and model validation false.
5. Policy C-S probe/enrollment/three-canary qualification is complete and green for the currently active Codespace epoch `263237f0-b5dc-4710-bef4-e0ac855c2312` at source commit `b2f246769340e4f7f6929e679692956c731efd93`. Do not pull, commit, rebuild, stop, or restart this Codespace while using the qualified session.
6. Use the still-active qualified Policy C-S session for the separate model-evidence validation review. Reproducibility qualification alone does not establish Basic Pitch correctness and must not change model-validation or delivery state.
7. If Policy C-S qualification is green, keep that exact Codespace session active for the separate model-evidence validation review. Do not treat surface reproducibility as model correctness. If the Codespace stops/restarts or the fingerprint/source changes, that epoch expires and a new epoch starts from zero.
8. Persistent paid Policy C remains a fallback, not the immediate path. If session-bound Codespaces proves operationally inadequate, use the low-cost 4-GB host runbooks; do not purchase or enroll one merely because persistent Policy C exists.
9. Whether authority is persistent Policy C or session-bound Policy C-S, exact canaries demonstrate reproducibility scope only. Model-evidence validation is a separate review; keep `modelValidationComplete:false`, customer-eligible events 0, duration research paused, and archived V143/Gomyway/reference/pro-scorer work out of scope until independently justified.

The archived V143/Gomyway pipeline remains out of scope unless explicitly requested.
