# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V146 is CLOSED/SEALED after regression. V147 Phase A preregistration is frozen and implemented. The single-use CPU/reference-free GitHub Actions proof workflow is now committed and execution is pending/being observed. No calibration/gold access, no Modal/L4/GPU/live audio, no production promotion.**

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
- Run `33032332238`, job `98387433761`, attempt1: **SUCCESS**.
- Persistence commit `6e6bc3fd0831b149d3e99323c20162ccd32fddc8`; workflow deletion/sealing `9f2f1aeef4a730e919cceee2eccc31c3a25dfd37`.
- Score `debug/v146-rhythm-artifact/calibration-score.json`; blob `bed3325573e86748c3fc409d4bca00970e087ce2`.
- Proof `debug/v146-rhythm-artifact/calibration-evaluation-proof.json`; blob `7bfd6fe6eee33cd2012652c4aeb2186ed5657b5b`; schema14602.
- V146 metrics: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.0064965197215777265`; chord pitch-set `0.022757697456492636`; exact voicing `0.004016064257028112`; coverage/PDF `1.0`; critical mismatch count1875.
- Candidate minus accepted: pitch `-0.07100434063433214`; pitch/timing `-0.02243808212790995`; string/fret/timing `-0.048048934823876815`; chord pitch-set `-0.03529344283376307`; exact voicing `-0.05403507603322759`; critical mismatches `+163`.
- Interpretation: V146 materially regressed musical calibration metrics. No replay, retuning, alternate construction, or promotion is authorized.

## V147 Phase A — PITCH HYPOTHESIS BEFORE FINGERING / FROZEN / IMPLEMENTED / CPU PROOF IN PROGRESS
- Preregistration: `docs/v147-pitch-hypothesis-preregistration.md`; initial freeze commit `a0bb5412be8830fca27726ad2067a713e8441089`; pre-implementation aggregation clarification `d1dcb96943af758cdd54843637366701f25b4b22`; prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Both prereg commits occurred before any V147 implementation code.
- Structural diagnosis: `modal/v145_rhythm_decoder.py` preserves incoming event MIDI and optimizes timing/playable string-fret states around that immutable pitch. This explains V146 `pitchChanges = 0` and establishes the V147 signal boundary.
- Existing reference-free signal path:
  - `analyzer/modal_analyzer.py`: Basic Pitch event MIDI/confidence.
  - `analyzer/modal_bend_harmonic_evidence_benchmark.py`: HPSS harmonic audio + 48-bin/octave CQT evidence.
  - `modal/v144_rhythm_pitch_shift_policy.py`: precedent for bounded ±1 alternatives only; its sequence/slope heuristic is not reused.
- Frozen candidate family `{midi-1,midi,midi+1}` within `[40,88]`; fail closed on missing/non-finite/tied/weak/ambiguous evidence.
- Frozen CQT aggregation: explicit frames; ±0.30 summed candidate band; ±2.0 baseline excluding ±0.75; width-normalized median baseline; per-frame dB delta; median across frames; +12 octave support only when fully represented.

### V147 implementation committed
- Pure decision + prepared-CQT adapter: `modal/v147_pitch_hypothesis.py`; creation commit `ef08f480eea0bc0907ca5c686bc65bae60e858eb`; blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Contract tests: `modal/tests/test_v147_pitch_hypothesis.py`; creation commit `e02823b82ff259b0bf3cb173245f382c37f5dda1`; blob `f71d1da6c52a6a737faca7ab4f8989fb702be96d`.
- Standalone generated proof harness: `modal/v147_pitch_hypothesis_cpu_proof.py`; creation commit `ac6b92618f2cc52971e6b42c769f0345617d51bf`; blob `e9d28739cd19f095cb83807fd0b23c2b14b7c966`; schema14701.
- Implementation keeps V145 files untouched and has no calibration/gold, Modal/GPU, live-audio, or production integration path.
- Tests cover: original-control keep; strong ±1 recovery; ambiguous/weak/tie keep; low/high guitar boundaries; missing/non-finite evidence fail closed; deterministic serialization; prepared-CQT strong-neighbor smoke; prepared-CQT shape-error fail closed.
- Proof harness contains only generated evidence and reports the frozen metrics + payload SHA and `GO`/`STOP` gate.

### V147 CPU proof execution state
- Single-use workflow `.github/workflows/v147-phase-a-cpu-proof.yml` created in commit `aa7c3dc69367749a228137b7e2cb14cbf72c8610`.
- Workflow is restricted to this branch/path and runs only the frozen V147 contract tests + generated proof on CPU; it records source blob identities and uploads proof/runtime/log artifacts.
- A local reconstruction preflight using the exact three frozen GitHub file contents completed before the workflow commit: `13 passed`; generated proof gate `GO`; 11/11 proof cases passed; proof payload SHA256 `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`; formatted proof file SHA256 `2cba17eaf5158fdcbe73f3207eb8a58c6b3100429c1065e524a42c2937cab67d`. This is supporting preflight evidence only; repository-native GitHub Actions evidence remains the authoritative Phase-A execution to persist.
- No calibration/gold reference, Modal/L4/GPU, live audio, V145 modification, or production integration was used in this execution path.

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
1. Keep V146 sealed; accepted family #10 remains active.
2. Observe only the single-use V147 CPU/reference-free workflow created at `aa7c3dc69367749a228137b7e2cb14cbf72c8610`; do not read calibration/gold evidence.
3. Persist exact GitHub Actions proof/runtime evidence and checkpoint the run/job/artifact identities.
4. If Phase A fails, STOP rather than retuning frozen thresholds. If it passes, checkpoint `GO`, delete/seal the single-use workflow, and stop. Any later live/reference/Modal/GPU evaluation or production integration requires a separately authorized/frozen next phase.
5. Continue frequent checkpoint saves on this branch.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V146 remains consumed/closed/sealed with regression.
- V147 preregistration and implementation are frozen.
- Local exact-source CPU preflight passed; repository-native single-use CPU proof workflow is committed and is the next authoritative evidence source.
- **Next: capture the GitHub Actions V147 Phase-A run result, persist artifacts, checkpoint GO/STOP, then seal the workflow.**
