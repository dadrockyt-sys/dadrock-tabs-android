# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–11 are consumed/sealed. Accepted calibration baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. Family #11 atomic exact-singleton generated-only onset prune completed its single authorized one-shot and STOPPED AT FIT with deterministic family #10 fallback; validation/canary/full were never opened. Family #11 execution surfaces are deleted. No family #12 is pre-registered. Production/main/Bass/Lead untouched.**

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

## Accepted calibration baseline — LOCKED / UNCHANGED
- `singleton-onset-replace-be9e9aa7a734e3cd`; manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events / 113 measures; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / job `98265545933` SUCCESS; exact reference-free chain proven.
- Production false; Rhythm complete false; near-100 false; unseen-generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1 single-event prune; 2 two-signature prune; 3 triple prune; 4 four-signature prune; 5 same-string pitch; 6 pitch+step; 7 pitch+adjacent-string; 8 pitch+step+position; 9 atomic dyad; 10 atomic singleton replacement; 11 atomic exact-singleton generated-only onset prune.
- Family #10 one-shot `32995503662`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; execution surfaces deleted. Never choose another of its 25 candidates.
- Family #11 one-shot `32998471525`; report blob `9d1b46d8fcc45465a55f018363fd32e22e120068`; execution surfaces deleted. Never choose any of its 110 ranked rules / 109 evaluated candidates.

## Accepted-baseline FIT residual diagnostic — COMPLETE / SEALED / CURRENT
- Diagnostic `validation/v144_rhythm_calibration/analyze_singleton_baseline_fit_residuals.py`; blob `27ac8699279db8fc0208d067479ad3751da1a630`; tests blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`.
- Pre-label CPU `32996550172` / job `98267233982` SUCCESS; one-shot `32996989280` / job `98268733558` SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Diagnostic workflow deleted `b5afca0960d5ee7d683d36d427de9d874585f0d7`; trigger deleted `68cc0165678cfe1d32afb9830b00a6c16dc615ec`; replay forbidden while baseline unchanged.
- Isolation: candidate construction/ranking/selection false; rule/shift histogram false; validation/canary false; runtime reference false; V5/main/Production false; GPU false.
- FIT: generated 643 / reference 594; pitch matched 176; tight timing 41; gross timing 90; exact position/timing 34; displaced same-measure pitch 135; tight wrong-position 7.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180; generated-only cardinality `g1-r0=203`, `g2-r0=79`, `g3-r0=12`, `g5-r0=1`; shared cardinality mismatch 84; extra-generated slots after same-onset substitution 431.
- This remains the only permissible current residual-shape evidence while accepted baseline stays `4e6f9f...`. Family #11 search outcomes MUST NOT be used to construct/rank a successor.

## Family #11 — COMPLETE / CONSUMED / SEALED / FIT FALLBACK
### Pre-registration and CPU proofs
- Policy `modal/v144_rhythm_singleton_onset_prune_policy.py`; commit `58eefa8204624f2d457ee2d29e6e8988a03b7920`; blob `1a9df07e29e20784d2b9b6111d22ae10e638a84e`.
- Policy tests commit `2ffee7c2802f127648cd52b402f1d4984370846b`; blob `bffb1295c580e7d30d1068791b34b89baff28ae5`; seven synthetic tests.
- Policy CPU `32997504056` / job `98270480901`: SUCCESS.
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_prunes.py`; commit `eed0e96491033d3a4b643ae11d2c6c580c9bbc42`; blob `2f89bf3f310d60cb609a9556130d9f713942216e`.
- Search tests commit `89dd6bd75b927e464fb222aa5d14a1e0dc8dd566`; blob `f1ecf0945519a5e4e8ef137ee5ef8f4b75cd620a`; seven synthetic invariant tests.
- Broad search-gate wiring commit `bb9e9846f4391520d2fae7c6085df052f56214cb`; workflow blob `54dd20748da1b9bf175e6bf46d3a85140bfe3c65`.
- Search CPU `32997920717` / job `98271890149`: SUCCESS; search compile, seven search tests, seven policy tests, reconstruction tests, immutable/provenance/config guards all passed.

### Fixed family #11 semantics
- Atomic whole-onset deletion only when generated onset contains exactly one event and FIT reference has zero events at that onset for construction.
- Rule identity: one structural onset context + sourceStringIndex + sourcePitchClass.
- Fixed support 3; max candidates 256; no relaxation.
- Runtime reference forbidden; linked/dangling-reference targets excluded; last event in a measure excluded; survivors immutable/in-order.
- Event count may decrease but exact 113 generated-measure set must remain.

### One-shot identity and result
- One-shot workflow `.github/workflows/v144-atomic-singleton-onset-prune-search.yml`; pre-registration commit `1f8b2c8560116914f120ed64ac3252fa881a9e14`; workflow blob `d0202892a86faa97e3f37eb34b8adfb567bef40e`.
- Pre-arm checkpoint commit `8057288538f74dbdaa9cdb1455746077d1dc383f`.
- Trigger commit `115b649f0a4bf2c7c1dff541c11956f03cb59596`; trigger blob `ed659848cd5fce6def6959fa57389a700ece44ce`; exact message `v144 execute atomic singleton onset prune one-shot`; changed only trigger path.
- One-shot run `32998471525`, job `98273767947`: **SUCCESS infrastructure/end-to-end workflow**.
- All workflow steps passed: immutable trigger verification; fixed search; staged-stop verification; independent PDF-event proof; final invariant wrapper; immutable recheck; report-only persistence.
- Report `debug/v144-rhythm-calibration/candidates/atomic-singleton-onset-prune-search.json`; persistence commit `56e2035870b6439f68eb49ebae3489f982fca0c0`; blob `9d1b46d8fcc45465a55f018363fd32e22e120068`.
- Persistence commit is exactly one commit after trigger and added **only the 5715-line report**.
- `rankedRuleCount=110`; `evaluatedCandidateCount=109`; candidate construction/ranking FIT-only; validation/canary construction/ranking false; consumed-family results excluded.
- **FIT RESULT: no candidate qualified.** `fitLock.locked=accepted-v144-baseline`; `lockedReason=deterministic-no-prune-fallback`; `selected=accepted-v144-baseline`; `selectedReason=fit-no-qualified-atomic-singleton-onset-prune-candidate`; `stoppedAt=fit`.
- `validation=null`; `canary=null`; `fullCalibration=null`; `splitPromotionAllowed=false`; `calibrationPromotionAllowed=false`.
- Locked stream remains exact accepted family #10: 1144 events / 113 measures / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; removed events/onsets 0.
- Independent PDF proof passed for fallback: fidelity 1.0, exact same event count/SHA, professional reference not opened during PDF check.
- Safety clean: V5/main/Production false; runtime reference false; GPU false; deterministic true.

### Sealing / replay refusal
- Executable one-shot workflow deleted immediately at commit `a16c4ca689092335954b70f480791ad6668aa0e7`.
- Trigger deleted immediately after at commit `7cd464f3d10294a1b8c27a61e767e2a322629580`.
- Family #11 is consumed. **Never rerun/replay/retune it and never select a runner-up from its 110 ranked rules / 109 evaluated candidates.**
- Accepted baseline remains family #10 unchanged; therefore the sealed current-baseline FIT residual diagnostic remains current.

## Immediate next actions
1. Re-read only the sealed accepted-baseline FIT residual diagnostic aggregate (`b9794a7b...`) to decide whether a materially distinct family #12 unit is justified. Do NOT use family #11 candidate outcomes/ranking/metadata for family shape.
2. Candidate possibility to assess from aggregate only: atomic **multi-note generated-only whole-onset** unit, because the current diagnostic independently reports `g2-r0=79`, `g3-r0=12`, `g5-r0=1`; this would be distinct from family #11 exact-singleton prune and family #9 shared-onset dyad pitch rewrite. Do not pre-register until the aggregate evidence and safety invariants are explicitly checked.
3. If a distinct unit is justified, pre-register policy shape/support/cap and synthetic tests before any candidate search; CPU-gate policy/tests first.
4. If no clear distinct unit exists, stop at diagnostic boundary rather than inventing or retuning a consumed shape.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
