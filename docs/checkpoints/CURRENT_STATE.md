# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The contextual same-string pitch-shift winner is now the accepted V144 calibration baseline via a dedicated manifest. Its search family is consumed/sealed and may never be replayed or retuned. The accepted stream remains 1144 events / 113 measures but now has improved full-gold calibration metrics. Production remains untouched; Rhythm is not complete and near-100% quality is not proven. Next is a fit-only residual/error-mechanism diagnostic from this new accepted baseline to pre-register the next materially new correction family.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob: `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 final-result sentinel blob: `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Frozen V5 PDF SHA256: `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`.
- Frozen V5 canonical event SHA256: `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed; never rerun/retry or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration reference
- Visual target: `main/public/Professionalexample.jpg`, main blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Exact structured reference SHA256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- This is a **gold calibration benchmark, not an unseen holdout**; never claim unbiased generalization from it.

## Fixed selector / invariant safety
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary.
- Fit labels may construct/rank; validation/canary only gate one locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Candidate must preserve all 113 accepted-baseline generated measure IDs before fit lock.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later gate failure returns to deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed candidate outcomes.

## Accepted V144 Rhythm calibration baseline — LOCKED
- **Current accepted candidate:** `pitch-shift-41b7a7470fa3245a`.
- Transform chain: previous triple `register::high && section16::1 && stepParity::0`, then same-string contextual pitch shift `pitchClass::4 && stepQuarter::0 => -2 semitones`.
- Selected manifest: `debug/v144-rhythm-calibration/selected/v144-pitch-shift-selected-baseline.json`.
- Manifest commit: `1f19e2de2199dbcca5f7259fc364e2cac3bea8ce`; manifest blob: `ee86c40d68e5c5b8e85bc4d008d9713c35e37a6c`.
- Event count: **1144**.
- Canonical/PDF-event SHA256: `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`.
- Generated measures: exact 113/113; missing `[]`; extra `[]`; PDF-event fidelity `1.0`.
- Full gold: critical mismatch `1802`; pitch F1 `0.3043062200956938`; pitch/timing `0.052631578947368425`; string/fret/timing `0.03923444976076555`; chord/voicing `0.0359364201796821`; measure coverage `1.0`; PDF fidelity `1.0`.
- Versus previous triple baseline: critical `-8`; pitch `+0.013397129186602907`; pitch/timing `+0.00669856459330144`; string/fret/timing `+0.007655502392344499`; chord/voicing `+0.012439530062197647`; no gated regression.
- Promotion scope is **calibration baseline only**: Production false; Rhythm complete false; near-100% false; unseen generalization false.

## Previous accepted calibration baseline — SUPERSEDED, still immutable historical evidence
- Triple candidate `prune-triple-67348efe50436fc5` = `register::high && section16::1 && stepParity::0`.
- Event/PDF SHA256 `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`; 1144 events / 113 measures.
- Historical manifest `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, blob `ba8dec9a1c3155816f5841a32ee52ced7998c110`.
- Do not use this as the baseline for any future new family now that the pitch-shift manifest exists.

## Consumed historical families — NEVER REPLAY / RESELECT
1. Single-signature prune: run `32935621669`; fit winner failed validation.
2. Two-signature conjunction prune: passed split but lost a generated measure and failed final invariant.
3. Triple prune family: consumed by the historical triple baseline; never select another triple candidate.
4. Additive four-signature prune: run `32938769540` SUCCESS; 512 fit-only candidates; none cleared fit; deterministic fallback. Report blob `5928e9687414c1e118653f139eda205237584ee0`; workflow sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Contextual same-string pitch-shift family: consumed by current accepted winner. Never replay, retune support/shift bounds, enlarge/reorder its candidate set, or select a runner-up later.

## Fit-only diagnostics that motivated pitch correction — COMPLETE / SEALED
- Pruning ceiling run `32939218722` SUCCESS; report blob `6064ede57f4ec18a3c961f4c8b82b98aad26efdf`; perfect deletion-only pitch ceiling `0.3770491803278689`.
- Error mechanism run `32939297662` SUCCESS; report blob `4d1f143142b15b3cb9270eca291dbc12d30dff80`; old accepted baseline had same-onset wrong-pitch substitutions `184` and count-preserving pitch-correction diagnostic ceiling `0.9603880355699272`.
- These diagnostics belong to the superseded triple baseline. Do not reuse their residual counts as current-baseline construction evidence.

## Contextual pitch-shift family — CONSUMED / PASSED / SEALED
- Policy blob `d9998c59acddba070069668d62bcb1c3cdaf2b05`; search hardened blob `9b35de6cf94a190a8700274334fcc85c5ad986c2`.
- Search-level tests commit `e29e82c090905b4b33eaf88147556b2162e1922d`; CPU-gate wiring commit `6fe747756ec253134d812e77d23bcd4ac8c39472`; gate run `32940560733` SUCCESS.
- Arming commit `876ba06fdc557ba695d542bacc31a90aa244c5a3`; **single actual one-shot run `32940695879` SUCCESS**.
- 41 fit-ranked / 41 evaluated candidates; no validation/canary/historical outcomes used for construction/ranking.
- Winner `pitch-shift-41b7a7470fa3245a`: correction support `10`, eligible generated support `40`, correction precision `0.25`; changed exactly `68` events.
- Fit passed: pitch gain `+0.008084074373484268`, critical delta `-4`, no regression.
- Validation passed: pitch gain `+0.017316017316017313`, critical delta `-6`, no regression.
- Canary passed: pitch gain `+0.005115089514066473`, critical delta `-2`, no regression.
- Full invariant passed; independent PDF-event fidelity `1.0`.
- Persisted search report commit `8142a942c234c4f00fe7f53deff8a34f4122448b`; report blob `a49e48368d2a45276d09e5746ce7cb4798828470`.
- Workflow sealed commit `21ca074f3917fb72614686ca5b46a3894ea53374`; archived workflow blob `e960b0d97118de533f68271ccefdfa7766e4e17d`; seal caused no pitch-shift replay.

## Immediate next actions
1. Reconstruct the **current** accepted baseline deterministically from immutable V5 by applying the historical triple transform then the accepted pitch-shift transform, and hard-check 1144 events / SHA `b6e1f8a8...` / 113 measures.
2. Run a new **fit-only residual/error-mechanism diagnostic** on this current baseline. It may inspect current fit labels only and must perform no candidate construction/ranking/selection.
3. Use that diagnostic only to choose the *shape* of a materially new pre-registered family (for example onset/timing correction vs string/fret remap); do not replay another same-string pitch-shift search.
4. Before any new one-shot family, add deterministic policy tests + 113-measure/event-count invariants + CPU gate.
5. Never replay/reselect consumed single/pair/triple/quad/pitch-shift families or alter their fixed gates after seeing outcomes.
6. Do not start Bass/Lead, modify main/Production, claim near-100% quality, or use Modal/L4/GPU without fresh explicit user authorization.
