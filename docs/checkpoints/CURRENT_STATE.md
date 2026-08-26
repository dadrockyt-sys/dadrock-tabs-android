# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 consumed/sealed. Accepted calibration baseline remains family #10 `singleton-onset-replace-be9e9aa7a734e3cd` / SHA `4e6f9f...`. The accepted-baseline FIT residual diagnostic is complete/sealed. Family #11 atomic exact-singleton generated-only onset prune is now POLICY PRE-REGISTERED with synthetic tests and broad CPU-gate wiring; no search/candidate evaluation exists yet. Production/main/Bass/Lead untouched.**

## Permanent safety
- Work only `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 events `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Professional reference is gold calibration, not unseen holdout; structured SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- V5 holdout permanently consumed; never rerun/retune it.
- No Modal/L4/GPU without fresh explicit authorization. `/ai-tab` frontend, Bass/Lead, `freezeReady=false` untouched.

## Fixed selector
- measure+step seed 144: 60 fit / 20 validation / 20 canary.
- FIT constructs/ranks; validation/canary gate one locked winner only.
- FIT pitch-content gain >= `0.005`; zero musical regressions; zero critical mismatch increase; PDF fidelity `1.0`.
- Gate order fit → validation → canary → full-gold → independent PDF event proof; later failure => accepted-baseline fallback, never alternate.
- Never tune support/thresholds from outcomes; never claim unseen generalization.

## Accepted calibration baseline
- `singleton-onset-replace-be9e9aa7a734e3cd`; manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`; manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`.
- 1144 events / 113 measures; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity 1.0.
- Full gold: critical 1712; pitch 0.35406698564593303; pitch/timing 0.06698564593301436; string/fret/timing 0.05454545454545454; chord/voicing 0.0580511402902557; coverage 1.0.
- Reconstruction CPU `32996069426` / job `98265545933` SUCCESS; reference-free exact reconstruction proven.
- Production false; Rhythm complete false; near-100 false; unseen-generalization false.

## Consumed families — never replay/reselect/retune
1 single event prune; 2 two-signature event prune; 3 triple event prune; 4 four-signature event prune; 5 same-string pitch; 6 pitch+step; 7 pitch+adjacent-string; 8 pitch+step+position; 9 atomic dyad; 10 atomic singleton replacement.
- Family #10 one-shot `32995503662`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; execution surfaces deleted. Never choose another of its 25 candidates.

## Accepted-baseline FIT residual diagnostic — COMPLETE / SEALED
- Diagnostic blob `27ac8699279db8fc0208d067479ad3751da1a630`; tests blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`.
- Pre-label CPU `32996550172` / job `98267233982` SUCCESS.
- One-shot `32996989280` / job `98268733558` SUCCESS.
- Report commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`; persistence added only report.
- Workflow deleted `b5afca0960d5ee7d683d36d427de9d874585f0d7`; trigger deleted `68cc0165678cfe1d32afb9830b00a6c16dc615ec`; replay forbidden while baseline unchanged.
- Isolation: candidate construction/ranking/selection false; rule/shift histogram false; validation/canary false; runtime reference false; V5/main/Production false; GPU false.
- FIT: generated 643 / reference 594; pitch-content matched 176; tight timing 41; gross timing 90; exact position/timing 34. Displaced same-measure pitch matches 135; tight wrong-position only 7.
- Onsets: generated 485 / reference 370 / shared 190 / generated-only 295 / reference-only 180; `g1-r0=203`, `g2-r0=79`, `g3-r0=12`, `g5-r0=1`; shared cardinality mismatch 84.
- Pure timing-only family is ineligible because it cannot satisfy fixed pitch-content gain >=0.005.

## Family #11 — atomic exact-singleton generated-only onset prune — POLICY PRE-REGISTERED / CPU PENDING
- Shape justified only by current accepted-baseline aggregate FIT report: 295 generated-only onsets, including 203 `g1-r0`, and 431 extra generated slots after substitution.
- Materially distinct from consumed event-prune families 1–4: groups by `(measure, step)` first and may delete only an entire onset containing exactly one generated event.
- Rule identity fixed before outcomes: one structural onset context signature (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep`) + explicit `sourceStringIndex` + `sourcePitchClass`.
- Runtime reference forbidden; exact singleton required; linked/dangling-reference targets excluded; last event in a measure cannot be deleted; surviving order/timing/metadata unchanged.
- Fixed minimum false-positive support `3`; max candidates `256`; no outcome-driven relaxation.
- Policy `modal/v144_rhythm_singleton_onset_prune_policy.py`; pre-registration commit `58eefa8204624f2d457ee2d29e6e8988a03b7920`; blob `1a9df07e29e20784d2b9b6111d22ae10e638a84e`.
- Tests `modal/tests/test_v144_rhythm_singleton_onset_prune_policy.py`; commit `2ffee7c2802f127648cd52b402f1d4984370846b`; blob `bffb1295c580e7d30d1068791b34b89baff28ae5`; seven synthetic tests.
- Broad CPU gate wiring commit `14eb87b6fdfb68fc35b55a01c5d38cb8b849ba1d`; workflow blob `fdd9ac64a6e59d8c9b02a2d7eb6d8f3bc3426bd3`.
- **No FIT labels have been used to construct/rank family #11 rules. No family #11 search file exists.**

## Immediate next actions
1. Require broad CPU SUCCESS on `14eb87b6...`; if failure, fix policy/tests only.
2. Only after success, pre-register FIT-only family #11 search with support 3/max 256 and accepted baseline `4e6f9f...`, exact measure-set guard and unchanged staged gates.
3. Search must construct/rank from FIT only; validation/canary closed until one winner locks; any later failure falls back to family #10 baseline.
4. If no rule qualifies, seal family #11 at FIT without relaxing/switching shape.
5. Never start Bass/Lead, main/Production, near-100 claims, or Modal/L4/GPU.
