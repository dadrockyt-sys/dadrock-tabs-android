# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 are consumed/sealed. Accepted calibration baseline is family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. The accepted-baseline FIT residual diagnostic is complete/sealed. Family #11 — atomic exact-singleton generated-only onset prune — has a pre-registered policy, synthetic policy tests, pre-registered FIT-only search, synthetic search tests, and broad CPU-gate wiring. Search CPU run `32997920717` on exact head `bb9e9846...` is currently pending/in progress. **No family #11 candidate evaluation has executed yet.** Production/main/Bass/Lead untouched.**

## Permanent safety
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 events `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Professional reference is **gold calibration, not unseen holdout**; structured SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- V5 holdout permanently consumed; never rerun/retune it.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false` untouched.

## Fixed selector / gates
- measure+step seed 144: 60 fit / 20 validation / 20 canary.
- FIT constructs/ranks; validation/canary gate one locked winner only.
- FIT pitch-content gain >= `0.005`; zero musical regressions; zero critical mismatch increase; PDF fidelity `1.0`.
- Gate order fit → validation → canary → full-gold → independent PDF-event proof; later failure => accepted-baseline fallback, never alternate.
- Never tune support/thresholds from outcomes; never claim unseen generalization.

## Accepted calibration baseline — LOCKED
- `singleton-onset-replace-be9e9aa7a734e3cd`; manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / job `98265545933` SUCCESS; exact reference-free chain proven.
- Production false; Rhythm complete false; near-100 false; unseen-generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1 single-event prune; 2 two-signature prune; 3 triple prune; 4 four-signature prune; 5 same-string pitch; 6 pitch+step; 7 pitch+adjacent-string; 8 pitch+step+position; 9 atomic dyad; 10 atomic singleton replacement.
- Family #10 one-shot `32995503662`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; execution surfaces deleted. Never choose another of its 25 candidates.

## Accepted-baseline FIT residual diagnostic — COMPLETE / SEALED
- Diagnostic `validation/v144_rhythm_calibration/analyze_singleton_baseline_fit_residuals.py`; blob `27ac8699279db8fc0208d067479ad3751da1a630`.
- Tests blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`.
- Pre-label CPU `32996550172` / job `98267233982` SUCCESS.
- One-shot `32996989280` / job `98268733558` SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; persistence added only report.
- Workflow deleted `b5afca0960d5ee7d683d36d427de9d874585f0d7`; trigger deleted `68cc0165678cfe1d32afb9830b00a6c16dc615ec`; replay forbidden while baseline unchanged.
- Isolation: candidate construction/ranking/selection false; rule/shift histogram false; validation/canary false; runtime reference false; V5/main/Production false; GPU false.
- FIT: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34; displaced same-measure pitch 135; tight wrong-position 7.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180; generated-only cardinality `g1-r0=203`, `g2-r0=79`, `g3-r0=12`, `g5-r0=1`; shared cardinality mismatch 84; extra generated slots after substitution 431.
- Pure timing-only successor is ineligible because it cannot satisfy fixed pitch-content gain >=0.005.

## Family #11 — atomic exact-singleton generated-only onset prune
### Policy — PRE-REGISTERED
- Shape justified only by current accepted-baseline aggregate FIT report: 295 generated-only onsets, including 203 exact generated singletons (`g1-r0`).
- Materially distinct from consumed event-prune families 1–4: groups by `(measure, step)` first and may delete only an entire onset containing exactly one generated event.
- Rule identity: one structural onset context signature (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep`) + explicit `sourceStringIndex` + `sourcePitchClass`.
- Runtime reference forbidden; exact singleton required; linked/dangling-reference targets excluded; last event in a measure cannot be deleted; survivors preserve order/timing/metadata.
- Fixed minimum false-positive support `3`; max candidates `256`; no outcome-driven relaxation.
- Policy `modal/v144_rhythm_singleton_onset_prune_policy.py`; commit `58eefa8204624f2d457ee2d29e6e8988a03b7920`; blob `1a9df07e29e20784d2b9b6111d22ae10e638a84e`.
- Policy tests `modal/tests/test_v144_rhythm_singleton_onset_prune_policy.py`; commit `2ffee7c2802f127648cd52b402f1d4984370846b`; blob `bffb1295c580e7d30d1068791b34b89baff28ae5`; seven synthetic tests.
- Initial policy CPU wiring commit `14eb87b6fdfb68fc35b55a01c5d38cb8b849ba1d`; workflow blob then `fdd9ac64a6e59d8c9b02a2d7eb6d8f3bc3426bd3`.

### FIT-only search — PRE-REGISTERED / CPU PENDING
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_prunes.py`; creation commit `eed0e96491033d3a4b643ae11d2c6c580c9bbc42`; blob `2f89bf3f310d60cb609a9556130d9f713942216e`.
- Search tests `modal/tests/test_v144_rhythm_singleton_onset_prune_search.py`; creation commit `89dd6bd75b927e464fb222aa5d14a1e0dc8dd566`; blob `f1ecf0945519a5e4e8ef137ee5ef8f4b75cd620a`; seven synthetic invariant tests.
- Search locks accepted family #10 baseline name/SHA/1144/113, fixed support `3`, max `256`, deletion-only survivor subsequence, exact measure-set preservation, staged selector fallback, and reference-free runtime transform.
- Search opens gold only after reference-free reconstruction of accepted baseline identity; FIT constructs/ranks; validation/canary only gate the single locked winner; later failure deterministically falls back to family #10.
- Broad CPU-gate wiring/current head commit `bb9e9846f4391520d2fae7c6085df052f56214cb`; workflow blob `54dd20748da1b9bf175e6bf46d3a85140bfe3c65`.
- Exact CPU run `32997920717`, job `98271890149`, currently **in progress** at this checkpoint.
- **No family #11 one-shot workflow exists. No family #11 search has executed. No candidate rules have been constructed/ranked/evaluated. Validation/canary remain closed.**

## Immediate next actions
1. Require exact family #11 search CPU run `32997920717` to finish SUCCESS and verify logs show search compile + seven search tests + immutable/provenance/config guards.
2. If CPU fails, fix search/tests only; do not execute calibration search.
3. Only after CPU SUCCESS, create one tightly locked CPU-only one-shot for family #11 with exact support 3/max 256, current baseline `4e6f9f...`, fixed staged gates, report-only persistence, and independent PDF-event proof for the locked stream.
4. Execute at most once; archive/delete workflow + trigger immediately regardless outcome; never retry/retune/select an alternate.
5. If no fit winner or later gate fails, baseline remains family #10. If a winner passes all gates/invariants, create a calibration-only promotion manifest + reference-free reconstruction proof before calling it accepted.
6. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
