# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1 is CPU-proven and sealed. V145 Stage 2 timing-grid inference + global sequence decoding is now preregistered CPU-only and ready for implementation. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.

## Permanent progress-percentage reporting
- Accepted family #10: **Pitch Content 35.4%** (`0.35406698564593303`), **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate; recompute only if accepted baseline changes.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity1.0.
- Full gold critical1712; pitch0.35406698564593303; pitch/timing0.06698564593301436; string/fret/timing0.05454545454545454; chord/voicing0.0580511402902557; coverage1.0.

## V144 consumed state
- Families #1–#14 are consumed. Never replay/reselect/retune them or use their candidate rankings/outcomes to shape a successor.
- Family #14 run `33025902769` / job `98367025091`; no qualifying FIT rule; accepted baseline unchanged.
- Family #14 one-shot workflow deletion `443031fd2294e05b23290c71b0e2b712198d842a`; trigger deletion `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; CPU proof JSONs preserved.
- Current accepted-baseline FIT residual remains `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`, blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Stage 1 — FROZEN / IMPLEMENTED / CPU-PROVEN
- Preregistration `docs/v145-rhythm-decoder-preregistration.md`; commit `5a5c59d305dffba16090bc7dc37d33ecbb17e295`.
- Core `modal/v145_rhythm_decoder.py`; frozen blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- Tests `modal/tests/test_v145_rhythm_decoder.py`; frozen blob `9d48b02316f4eb364b163b3027c6c4d79304ac27`.
- CPU proof run `33026865312`, job `98370167258`: COMPLETED/SUCCESS.
- Proof `debug/v145-rhythm-decoder/proofs/cpu-core-proof.json`; blob `978c2b7cd984f2cece23d2bc152f6acca28980e1`; persistence commit `5878764dbc747b17578eeeb9955204459adce503`; schema14501.
- Proof: no gold/reference/FIT/validation/canary inputs; no Modal dependency/GPU/live audio; accepted baseline unchanged.
- Proof workflow deletion/sealing commit `e802d7a867ee5f965be0c6abe51f70b6c0e6af6b`. Never rerun it.

## V145 Stage 2 — PREREGISTERED / CPU-ONLY / NOT YET IMPLEMENTED
- Frozen preregistration: `docs/v145-rhythm-decoder-stage2-preregistration.md`.
- Preregistration commit: **`9fe0396fc1c320e3da5f5955d823df615a787603`**.
- Architecture: **V5 Rhythm evidence -> frozen Stage1 normalization -> runtime timing-grid inference -> raw-onset simultaneity clusters -> cluster timing/guitar-state options -> global bounded beam sequence -> decoded notes**.
- Runtime grid candidates come only from positive consecutive generated onset deltas and median delta divided by integers1..4; allowed quantum0.050..0.500s.
- Grid support gates: support>=0.80 within normalized residual<=0.18; median normalized residual<=0.12; minimum4 evidence events.
- Eligible grids rank by higher support, lower median residual, lower mean residual, larger quantum, smaller phase.
- Simultaneity cluster window is `0.30 * quantum` from first raw onset in cluster.
- Cluster onset must be present in every member's Stage1 timing lattice; no independent member drift inside a chord cluster.
- Standard tuning/max fret24/max fret span7; exact MIDI preservation; unique strings.
- Global beam width64; separate clusters require strictly increasing decoded onsets; transition cost uses frozen Stage1 hand-position movement.
- Stage2 does not invent new MIDI pitches and may leave unsupported/unplayable clusters undecoded.
- Stage2 public runtime APIs may not accept gold/reference/FIT/validation/canary inputs.
- No live Modal/L4/GPU/audio run authorized.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead.
2. Preserve family #10 accepted baseline and percentages **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
3. Implement Stage2 exactly to preregistration commit `9fe0396f...` in a new CPU-only module importing frozen Stage1; do not modify Stage1 blobs.
4. Add synthetic/contract tests for jittered-grid recovery, unsupported-grid rejection, deterministic clustering, common-onset requirement, one source event once, exact MIDI, unique strings, continuity-aware global choice, fail-closed invalid clusters, input immutability, runtime label isolation, no Modal dependency.
5. Checkpoint implementation before proof.
6. Run and seal a definitive CPU-only Stage2 proof; checkpoint it.
7. No live Modal/L4/GPU/audio benchmark until separately and explicitly authorized.

## Current stop point
- V144 accepted baseline unchanged and protected.
- V145 Stage1 CPU proof SUCCESS/sealed.
- V145 Stage2 preregistered at commit `9fe0396f...`; safe next action is CPU implementation only.
