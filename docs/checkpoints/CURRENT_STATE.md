# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V146 is CLOSED/SEALED after regression. V147 Phase A is STARTED under a separately frozen pitch-hypothesis-before-fingering preregistration, including a pre-implementation CQT aggregation clarification. V147 construction is reference-free and CPU/generated-evidence only; no calibration/gold access, no Modal/L4/GPU/live audio, no production promotion.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion. Family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; critical mismatch count 1712.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68` (re-verified unchanged after V146 sealing).

## V145 frozen/proven foundation
- Stage1 blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; proof run `33026865312` SUCCESS.
- Stage2 blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; proof run `33027229509` SUCCESS.
- Stage3 adapter blob `434d4b2582991c216df411455f232b8d211337c6`; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; run `33029862099` SUCCESS.
- Stage3 evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; run `33031101564` SUCCESS.
- Frozen evaluator order: candidate-only validation -> pre-reference freeze/PDF gate -> candidate/freeze/PDF identity -> accepted manifest -> only then gold hash/validate -> exactly one score.

## First real V145 execution — CONSUMED / FAILED CLOSED / SEALED
- Run `33031523386`, job `98384901171`: workflow identity failure before candidate/calibration work.
- No candidate, gold read, score, or result existed. Workflow/trigger sealed. Never retry that execution.

## V146 artifact-first protocol — CLOSED / SEALED
### Overall preregistration
- `docs/v146-rhythm-artifact-first-calibration-preregistration.md`; creation commit `86729595bab64ac80b82180532ee4dc94fca9817`; blob `0125201e86389b21dee3ceb2e7ecd25dc67dfe84`.
- V146 separates generated-only artifact construction from later evaluation; no musical parameter changed from V145.

### Phase A — GENERATED-ONLY ARTIFACT / SUCCESS / SEALED
- Workflow creation commit `246d7dba0f7b3d2955feed90446353de8302da6f`; workflow blob `63812af5182795995129b961f8926b9a2b04dd1d`.
- Run `33031802198`, job `98385781107`: SUCCESS; persistence commit `e5d7d9dd9bdce8bf0eeee7f2a8207475ddbd31d3`; workflow deletion `a79e9717e0dbebdd730dfabaef068c78b45a5109`.
- Candidate `debug/v146-rhythm-artifact/generated-only-candidate.json`; Git blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`.
- Construction proof `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`; blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`; schema14601.
- Candidate: **1209 events /113 measures / canonical event SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`**.
- Generated-only changes vs V5 source: 871 events changed; stringIndex871; fret871; measure0; step0. MIDI/event count/order/measure set preserved.
- Phase A proof: referenceFree=true, acceptedManifestRead=false, realGoldRead=false, calibrationScoreRun=false, alternateCandidateConstructed=false, acceptedBaselineChanged=false, modalGpuUsed=false.

### Phase B — FIXED-ARTIFACT CALIBRATION / SUCCESS / CONSUMED / SEALED
- Prereg `docs/v146-rhythm-phase-b-calibration-evaluation-preregistration.md`; creation commit `791aef9a0e8f48cd7d1e3672b2fa0b2469fa6a2c`; frozen prereg blob `82bd04d819f26106a831f67a1a61ccba6e876c08`.
- Workflow creation commit `0008c69cc05e7dac67eb9684ef022e10dc375336`; workflow blob `1331b350525865008907b1f9107b9363a2cc91dc`.
- Run `33032332238`, job `98387433761`, attempt1: **SUCCESS**. Every step through dependency identity, independent candidate validation, freeze, renderer contract, PDF fidelity, exactly-one evaluator call, proof creation, and two-file persistence succeeded.
- Persistence commit `6e6bc3fd0831b149d3e99323c20162ccd32fddc8`.
- Workflow deletion/sealing commit `9f2f1aeef4a730e919cceee2eccc31c3a25dfd37`. Workflow is absent on branch after sealing. No second V146 Phase B run was observed; run `33032332238` remains the sole Phase B calibration execution.
- Score `debug/v146-rhythm-artifact/calibration-score.json`; blob `bed3325573e86748c3fc409d4bca00970e087ce2` (re-verified unchanged after sealing).
- Proof `debug/v146-rhythm-artifact/calibration-evaluation-proof.json`; blob `7bfd6fe6eee33cd2012652c4aeb2186ed5657b5b`; schema14602 (re-verified unchanged after sealing).
- Candidate identity remained exact: 1209 events /113 measures / event+PDF SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`; PDF fidelity `1.0`; candidateMutatedDuringEvaluation=false; referenceOpenedOnlyAfterPreReferenceGate=true; acceptedBaselineChanged=false; promotionAllowed=false; modalGpuUsed=false; liveAudioBenchmarkRun=false.
- V146 metrics: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.0064965197215777265`; chord pitch-set `0.022757697456492636`; exact voicing `0.004016064257028112`; coverage/PDF `1.0`; critical mismatch count1875.
- Candidate minus accepted deltas: pitch `-0.07100434063433214`; pitch/timing `-0.02243808212790995`; string/fret/timing `-0.048048934823876815`; chord pitch-set `-0.03529344283376307`; exact voicing `-0.05403507603322759`; coverage/PDF `0`; critical mismatches `+163`.
- Interpretation: the fixed V146 decoder/adapter artifact materially regressed all musical calibration metrics vs accepted family #10. No V146 replay, retuning, alternate construction, or promotion is authorized.

## V147 Phase A — PITCH HYPOTHESIS BEFORE FINGERING / FROZEN / IN PROGRESS
- Preregistration: `docs/v147-pitch-hypothesis-preregistration.md`; initial freeze commit `a0bb5412be8830fca27726ad2067a713e8441089`; pre-implementation CQT aggregation clarification commit `d1dcb96943af758cdd54843637366701f25b4b22`, blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Both prereg commits occurred before any V147 implementation code.
- Structural diagnosis: `modal/v145_rhythm_decoder.py` copies incoming event MIDI into Stage 1 and Stage 2 searches only timing/playable string-fret states for that immutable MIDI. This explains why V146 could move 871 fingerings while emitting `pitchChanges = 0` and establishes the new-signal boundary without using reference labels to tune a candidate.
- Existing reference-free signal path identified:
  - `analyzer/modal_analyzer.py` receives Basic Pitch `note_events` with event MIDI/confidence but does not construct alternate pitch hypotheses from the richer model output.
  - `analyzer/modal_bend_harmonic_evidence_benchmark.py` already supplies HPSS harmonic audio plus 48-bin/octave CQT harmonic-energy evidence that can score nearby pitch bands. Existing harmonic benchmark uses 48 bins/octave and a 128-sample hop, but Phase-A adapter intentionally accepts an already-computed CQT instead of freezing a second audio frontend.
  - `modal/v144_rhythm_pitch_shift_policy.py` is precedent for bounded ±1 event-MIDI alternatives, but its sequence/slope heuristic is NOT being reused as the V147 decision signal.
- Frozen V147 candidate family: only `{midi-1, midi, midi+1}` within guitar MIDI `[40,88]`.
- Frozen decision is fail-closed to original MIDI; alternate requires explicit harmonic evidence and frozen margins. Missing/non-finite/tied/weak/ambiguous evidence preserves original MIDI.
- Frozen CQT adapter aggregation: explicit event frames; ±0.30-semitone summed candidate band; ±2.0 baseline excluding ±0.75; baseline width-normalized by candidate-bin count; per-frame dB deltas; median across frames; octave support at +12 only when fully represented.
- V145 decoder stays untouched during initial V147 proof.
- Phase A allowed evidence: CPU/reference-free generated cases only. No V145/V146 gold/reference access; no Modal/L4/GPU/live audio; no automatic production integration/promotion.
- Next implementation: pure deterministic pitch-hypothesis function + reference-free prepared-CQT adapter + CPU generated proof against the frozen preregistration.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`
- accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`
- calibration gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## EXPLICIT NEXT STEPS
1. Keep V146 sealed; never replay or tune from consumed V146 calibration evidence.
2. Keep accepted family #10 as the active Rhythm baseline.
3. Implement V147 Phase-A pure pitch-hypothesis decision code and prepared-CQT evidence adapter exactly against `docs/v147-pitch-hypothesis-preregistration.md`; do not modify V145 in place.
4. Build/run only the frozen CPU/reference-free generated proof. Save exact proof/results and checkpoint before any integration decision.
5. If Phase A fails, STOP rather than retuning frozen thresholds. If it passes, checkpoint the result; any later live/reference/Modal/GPU evaluation or production integration needs its own authorized/frozen next phase.
6. Continue frequent checkpoint saves on this branch.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V146 remains consumed/closed/sealed with regression; no replay or retuning.
- V147 Phase-A preregistration and deterministic CQT aggregation are frozen before implementation; latest prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Existing reference-free Basic Pitch + harmonic CQT evidence path has been identified.
- **Next: implement and CPU-prove the pure V147 pitch-hypothesis layer without reading calibration/gold evidence.**
