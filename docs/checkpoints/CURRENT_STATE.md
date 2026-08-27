# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C real-audio artifact-first protocol is FROZEN BEFORE REAL-AUDIO ACCESS. Phase A and Phase B remain COMPLETE/GO/SEALED. Current authorization permits only reference-free implementation/tests for Phase C; actual audio decoding/analysis remains STOP pending fresh explicit authorization. Accepted Rhythm family #10 remains active.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Canonical event count `1144`; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; generated measures `113`; critical mismatch `1712`.
- Scores: **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.

## V145 / V146
- Frozen V145 decoder `modal/v145_rhythm_decoder.py`: blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V146 remains CLOSED/SEALED after regression; no replay/retuning/promotion.

## V147 Phase A — COMPLETE / GO / SEALED
- Prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Successful run `33034629948`, job `98394561968`: 13 tests passed; proof GO 11/11.
- Proof payload SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Workflow deleted/sealed `da1e7378c238a0715f005b96da5b0a91c7a5d662`.

## V147 Phase B — COMPLETE / GO / SEALED
- Prereg `docs/v147-phase-b-generated-decoder-integration-preregistration.md`; freeze commit `1078b0b3ac2ef688065ced5fa7968e214093e5ec`; blob `7d375755824dbf1dfc90fc7f62d85b11fb4d06b4`.
- Adapter blob `76ce80ef998ca54797b1df8b6fb7ab46440d9a04`; tests blob `9a1fc8671a9e2f43c6c2161d70c0a242f929a4dc`; proof harness blob `969403fd12963ccfefc4a9d379dbc800656b021e`.
- Run `33035123962`, job `98396067875`: SUCCESS; 8 tests passed; generated proof GO 5/5.
- Metrics: pitchChanges `2`; controlFlips `0`; strongAlternatesRecovered `2/2`; ambiguousKept `1/1`; malformedKept `1/1`; cardinality/position/mutation violations `0`; deterministic `true`.
- Proof payload SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.
- Workflow deleted/sealed `7259c433589d505d9e9de56f45b0e1db9d4c975e`.

## V147 Phase C — REAL-AUDIO ARTIFACT-FIRST / PREREG FROZEN / NOT EXECUTED
- Prereg: `docs/v147-phase-c-real-audio-artifact-preregistration.md`.
- Freeze commit: `9a452bc29f6e1edcad9ef2a45a1c2a52267277b4`.
- Frozen prereg Git blob: `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Purpose: construct exactly one real-audio-derived candidate from accepted family #10, then seal it **without opening gold/reference or scoring**. A later separately frozen Phase D would score the immutable artifact exactly once.
- Exact accepted source must materialize to 1144 canonical events and SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881` before any audio read.
- Historical source-audio raw SHA recovered from sealed V144 workflow blob `a9bef022032f2d5195dc54ba2a5bd9d7629686da`: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Raw source audio bytes are not present on the current branch. No substitute encode/song/upload is allowed; exact bytes must hash to the frozen value before decoding.
- Frozen Phase-C front end: 22050 Hz mono; harmonic component via HPSS margin `(1.0,6.0)`; CQT hop 128; 48 bins/octave; fmin MIDI 40; 243 bins; fixed event-time mapping at 129.19921875 BPM, 4 steps/beat; frozen frame window and frozen Phase-A candidate evidence aggregation/thresholds.
- Candidate timing/order/count/measure/metadata must remain fixed; only MIDI/string/fret may change; V145 timing lattice is forbidden in Phase C.
- Real-audio analysis has **NOT** run. Calibration/gold/reference has **NOT** been opened. Modal/GPU has **NOT** been used.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`
- accepted manifest `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`

## EXPLICIT NEXT STEPS
1. Keep V146, V147 Phase A, and V147 Phase B sealed; accepted family #10 remains active.
2. Keep V147 Phase C prereg frozen; do not change its CQT/window/threshold/candidate rules after future real-audio results.
3. Without reading audio, implement and CPU-test only: (a) reference-free accepted-family materialization/identity guard, (b) fixed-time fingering adapter, (c) generated numeric/CQT evidence aggregation, (d) raw-audio SHA guard.
4. Checkpoint all Phase-C support-code/test/proof identities before any real-audio execution.
5. **STOP before actual audio decoding/CQT analysis. Fresh explicit authorization is required for real-audio execution.**
6. Phase D/reference scoring remains unauthorized and requires a separate frozen preregistration after a Phase-C GO artifact exists.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 A = GO/SEALED; V147 B = GO/SEALED.
- V147 Phase C protocol is now frozen but has not touched real audio.
- No calibration/gold/reference access, real-audio decode, analyzer integration, Modal/L4/GPU, main, or Production changes occurred in Phase C.
- Proceed only with generated/reference-free Phase-C implementation/tests, then STOP before real audio.
