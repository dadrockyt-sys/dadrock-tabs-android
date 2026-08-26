# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 are consumed/sealed. Accepted calibration baseline is family #10 winner `singleton-onset-replace-be9e9aa7a734e3cd` / event SHA `4e6f9f...`. The accepted-baseline FIT aggregate residual diagnostic is COMPLETE, SUCCESSFUL, PERSISTED, and SEALED. Its aggregate residuals justify pre-registering one materially distinct family #11 shape: atomic exact-singleton generated-only onset pruning. No family #11 candidate/rule has been constructed or evaluated yet. Production/main/Bass/Lead remain untouched.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout permanently consumed; never rerun/retry/retune V5 from V144 evidence.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false` untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None used in V144.**

## Gold calibration / fixed selector
- Professional target is a **gold calibration benchmark, not unseen holdout**; structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Split measure+step seed 144: 60% fit / 20% validation / 20% canary.
- FIT may construct/rank; validation/canary gate only ONE locked winner.
- Fixed FIT gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant. Later failure => accepted-baseline fallback, never alternate selection.
- Never tune thresholds/support from observed outcomes; never claim unseen generalization.

## ACCEPTED V144 Rhythm calibration baseline — LOCKED / CALIBRATION ONLY
- Name `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Chain: frozen V5 → triple prune → same-string pitch shift → pitch+adjacent-string position revoice → singleton replacement `stepParity::0`, source string `0`, pitch class `4`, target string `3`, semitone `-12`.
- 1144 events / 113 measures; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity `1.0`; 110 changed singleton events/onsets.
- Full gold: critical `1712`; pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set/exact voicing `0.0580511402902557`; coverage `1.0`.
- Reconstruction test blob `e6acdd8b49dc6d87f04f7cf89367c97a3ca49041`; CPU run `32996069426`, job `98265545933` SUCCESS; exact `4e6f9f...` reconstructed reference-free before labels.
- Calibration baseline true; Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature event prune — failed validation.
2. Two-signature event prune — failed measure-set invariant.
3. Triple event prune — historical accepted baseline.
4. Additive four-signature event prune — no fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint pitch+adjacent-string position — prior accepted; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint pitch+step+position — no fit-qualified; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero supported rules; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`.
10. Atomic singleton pitch+explicit-string replacement — successful locked winner; run `32995503662`; report commit `ff6165982e8e3036404489c954a7d06ab8a1b015`; blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; execution surfaces deleted; consumed/sealed; never choose another of its 25 candidates.

## Accepted-singleton-baseline FIT residual diagnostic — COMPLETE / SEALED
- Diagnostic `validation/v144_rhythm_calibration/analyze_singleton_baseline_fit_residuals.py`; commit `dbc2ff96252a7069b928a31d0cf38771d45e9a1f`; blob `27ac8699279db8fc0208d067479ad3751da1a630`.
- Synthetic tests commit `9dae8b40170d20d31a618bc2ea5bd5d61564fc79`; blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`.
- Required pre-label CPU run `32996550172`, job `98267233982`: SUCCESS; compile + all six diagnostic tests + reconstruction guards passed without executing the FIT diagnostic.
- One-shot workflow preregistration commit `f931f39b62ccbb6b8245f615e47ebf233480660e`; workflow blob `b3d00151d6082b8f8c5e182e3469b5d10b22bb3e`.
- Trigger-only arming commit `517f81c227baa6c536fe82923d5a6a49b43cc44f`; trigger blob `2453a46d6832368ca10f499ba09834dffd58bfb6`; exact message `v144 execute singleton baseline fit residual diagnostic one-shot`.
- One-shot run `32996989280`, job `98268733558`: **SUCCESS**. Pre-label identity checks, diagnostic execution, aggregate-only verification, protected-identity recheck, and report-only persistence all SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; persistence commit `dd06bd96061170e6c25a8ffe6b4d91db941491fc`; blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.
- Persistence commit is exactly one commit after the trigger and added **only** the 131-line report.
- Isolation: candidate construction/ranking/selection false; candidate rule/shift histogram false; validation/canary false; runtime reference false; V5/main/Production false; GPU false.
- Sealed immediately after success: executable workflow deleted commit `b5afca0960d5ee7d683d36d427de9d874585f0d7`; trigger deleted commit `68cc0165678cfe1d32afb9830b00a6c16dc615ec`; replay forbidden while baseline unchanged.

### Current accepted-baseline FIT aggregate residuals
- Generated notes `643`; reference `594`; pitch-content matched `176`; tight pitch/timing matched `41`; gross pitch/timing matched `90`; exact string/fret/timing matched `34`.
- Same-measure pitch matches displaced from exact onset `135`; gross ±2-step recovered-only matches `49`; pitch matches still outside gross/competing `86`; correct-pitch/tight-timing but wrong string/fret only `7`.
- Onset topology unchanged in count: generated onsets `485`; reference `370`; shared `190`; generated-only `295`; reference-only `180`; shared cardinality mismatch `84` (`27` generated-heavier / `57` reference-heavier).
- Cardinality pair `g1-r0 = 203` generated-only singleton onsets; `g2-r0 = 79`; `g3-r0 = 12`; `g5-r0 = 1`.
- Shared singleton→singleton `100`: exact pitch/same string `25`; wrong pitch/different string `62`; wrong pitch/same string `13`.
- Same-onset wrong-pitch substitution slots `171`; same-string wrong-pitch slots `66`; extra generated slots after substitution `431`; missing reference slots `382`.

## Family #11 shape decision — PRE-REGISTRATION BOUNDARY
- A pure timing-only family is **not eligible** under the immutable selector because changing step without pitch cannot improve measure-level pitch-content and therefore cannot meet the fixed `>=0.005` FIT pitch-content gain gate, despite the large timing-displacement signal.
- The strongest lower-complexity residual shape that can improve the required pitch-content metric is generated false-positive removal: `295` generated-only FIT onsets, including `203` exact-singleton generated-only onsets, plus `431` extra generated slots after same-onset substitution.
- Proposed materially distinct family #11 unit: **atomic exact-singleton generated-only onset prune**.
- Distinct from consumed prune families 1–4: those delete individual events based on event context signatures regardless of onset cardinality; family #11 must first group by `(measure, step)`, require exactly one generated event at the onset, and prune that entire singleton onset atomically.
- Proposed fixed rule identity before any candidate outcomes: one structural onset context signature (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep`) + explicit `sourceStringIndex` + `sourcePitchClass`. No validation/canary/consumed-family result may choose the identity.
- Runtime must be reference-free; generated onset must remain exact singleton; source identity/context must match; linked/dangling-reference events must be ineligible; deleting the last event in a measure must be ineligible; all surviving event data/order/timing/metadata remain unchanged.
- Fixed support/max candidates should remain pre-registered at `3` / `256`; no result-driven relaxation.
- **No concrete family #11 context/string/pitch rule has been constructed/ranked/evaluated yet.**

## Immediate next actions
1. Implement only the family #11 atomic singleton-onset prune policy with the fixed shape above; add deterministic synthetic tests.
2. Wire policy/tests into broad CPU gate and require SUCCESS before creating any FIT search.
3. Only after policy CPU success, pre-register a deterministic FIT-only search with support `3`, max candidates `256`, accepted baseline `4e6f9f...`, exact measure-set guard, and unchanged staged selector thresholds/order.
4. If no family #11 rule meets fixed support/gates, seal at FIT; do not relax or switch shapes based on outcomes.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
