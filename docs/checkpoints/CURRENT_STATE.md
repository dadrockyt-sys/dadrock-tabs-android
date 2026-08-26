# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 are consumed/sealed. Accepted calibration baseline is family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. The accepted-baseline FIT residual diagnostic is complete/sealed. Family #11 — atomic exact-singleton generated-only onset prune — has pre-registered policy/search implementations, synthetic policy/search tests, BOTH required broad CPU gates GREEN, and a tightly locked one-shot workflow PRE-REGISTERED but UNARMED. No family #11 search execution has occurred yet. Production/main/Bass/Lead untouched.**

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
- Diagnostic blob `27ac8699279db8fc0208d067479ad3751da1a630`; tests blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`.
- Pre-label CPU `32996550172` / job `98267233982` SUCCESS; one-shot `32996989280` / job `98268733558` SUCCESS.
- Report commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; workflow deleted `b5afca0960d5ee7d683d36d427de9d874585f0d7`; trigger deleted `68cc0165678cfe1d32afb9830b00a6c16dc615ec`.
- FIT: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34; generated-only onsets 295, including `g1-r0=203`.

## Family #11 — atomic exact-singleton generated-only onset prune
### Policy — PRE-REGISTERED / CPU GREEN
- Rule identity fixed before outcomes: one structural onset context signature (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep`) + explicit `sourceStringIndex` + `sourcePitchClass`.
- Runtime reference forbidden; exact singleton required; linked/dangling-reference targets excluded; last event in a measure cannot be deleted; survivors preserve order/timing/metadata.
- Fixed support `3`; max candidates `256`; no relaxation.
- Policy `modal/v144_rhythm_singleton_onset_prune_policy.py`; commit `58eefa8204624f2d457ee2d29e6e8988a03b7920`; blob `1a9df07e29e20784d2b9b6111d22ae10e638a84e`.
- Policy tests commit `2ffee7c2802f127648cd52b402f1d4984370846b`; blob `bffb1295c580e7d30d1068791b34b89baff28ae5`; seven synthetic tests.
- Policy CPU run `32997504056`, job `98270480901`: **SUCCESS**; policy compile + seven policy tests PASS.

### FIT-only search — PRE-REGISTERED / CPU GREEN / NOT EXECUTED
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_prunes.py`; commit `eed0e96491033d3a4b643ae11d2c6c580c9bbc42`; blob `2f89bf3f310d60cb609a9556130d9f713942216e`.
- Search tests `modal/tests/test_v144_rhythm_singleton_onset_prune_search.py`; commit `89dd6bd75b927e464fb222aa5d14a1e0dc8dd566`; blob `f1ecf0945519a5e4e8ef137ee5ef8f4b75cd620a`; seven synthetic invariant tests.
- Search locks accepted family #10 baseline `4e6f9f...` / 1144 / 113, fixed support 3/max 256, deletion-only survivor subsequence, exact measure-set preservation, staged-selector fallback, and reference-free runtime transform.
- Count-changing candidates are permitted only with exact 113-measure preservation; event-count preservation is intentionally false for this family.
- FIT constructs/ranks only after reference-free accepted-baseline reconstruction; validation/canary only gate the single FIT-locked winner; any later failure falls back to family #10, never an alternate.
- Broad search-gate wiring commit `bb9e9846f4391520d2fae7c6085df052f56214cb`; workflow blob `54dd20748da1b9bf175e6bf46d3a85140bfe3c65`.
- Search CPU run `32997920717`, job `98271890149`: **SUCCESS**. Search compiled; all seven `AtomicSingletonOnsetPruneSearchInvariantTests` PASSED; all seven policy tests PASSED; accepted singleton baseline reconstruction tests PASSED; immutable V5/provenance/config guards PASSED.
- Broad CPU gate did not execute search or construct/rank candidates.

### One-shot — PRE-REGISTERED / UNARMED
- Workflow `.github/workflows/v144-atomic-singleton-onset-prune-search.yml`.
- Pre-registration commit `1f8b2c8560116914f120ed64ac3252fa881a9e14`; workflow blob `d0202892a86faa97e3f37eb34b8adfb567bef40e`.
- Exact trigger path: `debug/v144-rhythm-calibration/candidates/.v144-atomic-singleton-onset-prune-trigger`.
- Exact trigger commit message: `v144 execute atomic singleton onset prune one-shot`.
- Locks immutable V5/result/render/PDF, gold SHA, accepted family #10 manifest, residual/reconstruction chain, family #11 policy/search/tests, CPU workflow/run/job, staged selector/measure guard/context split/config, canonical/scorer/scoring helpers, freeze/PDF verifier, and renderer contract.
- Search fixed support `3`, max candidates `256`; FIT-only construction/ranking; validation/canary cannot construct/rank; runtime reference false; GPU false; replay false.
- Independent PDF-event proof accepts the locked count-changing stream only if renderer/frozen event count and SHA exactly match; full invariant requires 113 measures, deletion-only exact-singleton semantics, zero musical regressions, critical mismatch delta <= 0, coverage 1.0, PDF fidelity 1.0.
- Workflow persists **only** `debug/v144-rhythm-calibration/candidates/atomic-singleton-onset-prune-search.json`.
- **Trigger does not exist yet. No family #11 candidate evaluation has executed.**

## Immediate next actions
1. Create exactly one trigger-only commit with exact message `v144 execute atomic singleton onset prune one-shot`; trigger must lock workflow blob `d0202892...`, search CPU `32997920717`/`98271890149`, support 3/max 256, baseline `4e6f9f...`, runtime reference/GPU/replay false.
2. Freeze branch and poll only the exact trigger SHA. Do not retrigger/retry.
3. Inspect one-shot result. If FIT baseline wins, validation/canary/full remain null. If one FIT winner locks, only it may see validation then canary. Any later failure => family #10 fallback.
4. Require independent PDF proof regardless of gate outcome; promotion only if split gates + full invariant all pass.
5. After the single run, immediately delete/archive workflow + trigger and mark family #11 consumed regardless outcome. Never select an alternate from its candidate list.
6. If fully passing, create a separate calibration-only promotion manifest + reference-free reconstruction proof before calling family #11 accepted. Otherwise accepted baseline remains family #10.
7. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
