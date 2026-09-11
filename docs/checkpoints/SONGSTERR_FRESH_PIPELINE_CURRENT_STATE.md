# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 21:30 America/Toronto
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

## UPSTREAM EXECUTION POLICY — POLICY B SELECTED

Policy B permits bounded upstream numerical variation only through reference-blind, fail-closed downstream invariants.

Hard rules:
- hashes/vendor/CPU/image/region are provenance diagnostics, never correctness selectors
- no reference tab, archived/pro scorer, or downstream agreement may define variation bounds
- missing/invalid comparison evidence fails closed
- observed maxima never automatically become tolerances
- no preferred hosted output, CPU, vendor, hash, or runner may be selected
- `modelValidationComplete` stays false until a justified admission contract is implemented, tested, and independently demonstrated

Demucs evidence already established: same-run exact determinism (`34435154554`), hosted cross-run exact variation (`34436134514`), dispatch causality (`34438368530`), and failed cross-vendor common-AVX2 byte portability (`34439594582`, five observations, three exact groups). No branch-tracked fresh pinned compute surface is identified.

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

## DECODER TRACE CANARY INTEGRATION — IN PROGRESS

- Target: integrate exact per-observation decoder traces and pairwise decoder-trace comparisons into the existing decision-enabled cross-run measurement canary, diagnostic-only and non-promotional.
- Temporary helper run `34550779925` was rejected before job creation because an embedded multiline fragment broke helper YAML parsing. No canary or pipeline code changed.
- Corrected helper run `34550819480`, job `103113160920`, parsed and ran but failed closed before commit at `observation-upload:EXPECTED_ONE_MATCH:GOT:0`. Cause: GitHub Actions pre-expanded literal `` tokens inside the helper where no matrix context existed, producing empty sample tokens. No canary or pipeline code changed.
- Current repair constructs the literal downstream matrix token inside Python as `'$' + '{{ matrix.sample }}'`, preventing helper-time expression expansion. Validation still pending.
- `modelValidationComplete` remains false; customer-eligible events remain 0; duration research remains paused.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 authoritative; V3 candidate-only. Basic Pitch is not ground truth. No reference scorer/tab/archive logic. No BP end as duration. No generic next-onset duration. No same-pitch-reattack default. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, or downstream agreement.

## FRESH-CHAT NEXT ENGINEERING STEPS

1. Treat the A/B/C decision-surface inspection, exact decoder replay, and decoder-trace comparison as completed evidence. Do not rerun them merely to rediscover the current sample.
2. Keep `modelValidationComplete:false`, customer-eligible events at 0, and duration research paused. The B-only MIDI-55 event is a proven `threshold-onset-pass` toggle around the fixed Basic Pitch onset threshold, but its observed margins and the 7/20-frame common-event span drift are measurement evidence only.
3. Integrate exact decoder traces and pairwise decoder-trace comparisons into the decision-enabled cross-run measurement canary so future independent observations automatically preserve mechanism-level evidence. Keep this integration diagnostic-only and non-promotional.
4. Before proposing any onset-boundary admission rule, look for an independent reference-blind justification for a decision uncertainty boundary. Do not derive a tolerance from the current observed margins, matrix maxima, frame spacing, CPU/vendor grouping, event frequency, or downstream agreement.
5. If no independent bound exists, record that Policy B still lacks a justified admission contract for threshold-boundary inventory toggles. Do not manufacture one from more samples alone.
6. If additional independent observations are later collected, use the existing frozen settings and automatic trace-comparison path; treat them as measurement/history evidence, not as a way to tune thresholds to this fixture.
7. Keep the archived V143/Gomyway implementation/reference/pro scorer path out of scope and keep V2/V3 duration work paused until upstream model-evidence validation is actually resolved.

The archived V143/Gomyway pipeline remains out of scope unless explicitly requested.
