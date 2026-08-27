# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Stage 1 is CPU-proven/sealed. V145 Stage 2 is preregistered and implemented CPU-only; definitive Stage 2 CPU proof is next. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only.

## Permanent progress percentages — ACCEPTED BASELINE UNCHANGED
- Family #10: **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord/voicing `0.0580511402902557`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.

## V144 consumed state
- Families #1–#14 consumed; never replay/reselect/retune or use their observed candidate outcomes to shape successors.
- Family #14 run `33025902769` / job `98367025091`; no qualifying FIT rule; baseline unchanged.
- Family #14 workflow deletion `443031fd2294e05b23290c71b0e2b712198d842a`; trigger deletion `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Family #14 report blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; proofs preserved.
- Current accepted-baseline FIT residual remains blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Stage 1 — FROZEN / CPU-PROVEN / SEALED
- Preregistration commit `5a5c59d305dffba16090bc7dc37d33ecbb17e295`.
- Core `modal/v145_rhythm_decoder.py`; frozen blob **`2fd979aebb4685e86c7f24a0162f69de306c06e9`**.
- Tests blob `9d48b02316f4eb364b163b3027c6c4d79304ac27`.
- CPU proof run `33026865312`, job `98370167258`: SUCCESS.
- Proof blob `978c2b7cd984f2cece23d2bc152f6acca28980e1`; persistence commit `5878764dbc747b17578eeeb9955204459adce503`; schema14501.
- Proof workflow deletion `e802d7a867ee5f965be0c6abe51f70b6c0e6af6b`.
- Stage1 blob rechecked after Stage2 implementation and remains exactly `2fd979a...`.

## V145 Stage 2 — PREREGISTERED / IMPLEMENTED / PROOF PENDING
- Preregistration `docs/v145-rhythm-decoder-stage2-preregistration.md`; commit **`9fe0396fc1c320e3da5f5955d823df615a787603`**.
- Stage2 module `modal/v145_rhythm_sequence_decoder.py`; creation commit **`887330bcd31c91014bf40609ea89065554356ec2`**; frozen pre-proof blob **`5f86f57d0fd10774690d50528d51bad6e0392bf3`**.
- Stage2 tests `modal/tests/test_v145_rhythm_sequence_decoder.py`; creation commit **`71ae2b7e101d1f37a24fdef12fedebac314d947d`**; frozen pre-proof blob **`b16b8d2060e1ea3b47225f1c7c6072cb260c0db8`**.
- Architecture: generated Rhythm evidence -> frozen Stage1 normalization -> runtime timing-grid inference -> simultaneity clusters -> common-onset guitar-state options -> global bounded sequence search.
- Runtime grid inference: quantum0.050..0.500s; candidates from consecutive generated onset deltas + median divided1..4; support>=0.80 within normalized residual<=0.18; median residual<=0.12; min4 events.
- Grid ranking: higher support, lower median residual, lower mean residual, larger quantum, smaller phase.
- Clustering window `0.30*quantum`; cluster members must share the exact selected grid onset.
- Global beam width64; separate attacks strictly increasing in decoded onset; transition uses frozen Stage1 hand-position continuity cost.
- Exact MIDI preserved; no new pitch invention; unique simultaneous strings; max fret24; max fret span7; unsupported/unplayable clusters fail closed.
- Stage2 imports Stage1 and does not modify its frozen blob.
- 14 synthetic/contract tests added: jittered-grid recovery, unsupported-grid rejection, minimum evidence gate, deterministic clustering, shared-onset options, unique strings, one-use source events, strict onset sequence, continuity overriding local fingering, >6-note fail closed, unplayable fail closed, unsupported decode no fabrication, runtime label isolation, no Modal dependency, determinism.
- Definitive Stage2 CPU proof has not run yet at this checkpoint.

## EXPLICIT NEXT STEPS
1. Stay only on `v143-contextual-prune-lobo`; preserve family #10 and Stage1 frozen blob.
2. Run a definitive GitHub CPU-only Stage2 proof verifying Stage1 `2fd979...`, Stage2 `5f86f5...`, tests `b16b8d...`, and preregistration `9fe0396f...`.
3. Compile Stage1/Stage2/tests and run exact Stage2 unittest module.
4. If tests fail, fix only within the frozen Stage2 preregistration and checkpoint changed blobs before rerun.
5. If tests pass, persist proof metadata, delete/seal proof workflow, and checkpoint.
6. No live Modal/L4/GPU/audio benchmark until separately and explicitly authorized.

## Current stop point
- V144 accepted scores unchanged: **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V145 Stage1 proven/sealed.
- V145 Stage2 implemented at blobs `5f86f5...` / `b16b8d...`; immediate next action is definitive CPU proof only.
