# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted baseline remains `pitch-shift-41b7a7470fa3245a` (1144 events / 113 measures / SHA `b6e1f8a8...`). Six prior families are consumed and sealed. A materially new joint contextual pitch + adjacent-string position family has now been pre-registered from permissible current-baseline fit-only evidence, with deterministic policy tests and a successful CPU gate. No search/evaluation workflow or candidate evaluation for this new family exists yet.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA remains `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed; never rerun/retry or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration semantics
- Professional target is a **gold calibration benchmark, not an unseen holdout**.
- Exact structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; completeness 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Never claim unbiased generalization from this benchmark.

## Fixed selector / invariant safety
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary.
- Fit labels may construct/rank; validation/canary only gate one locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Every candidate must preserve all 113 current-baseline generated measures; count-preserving correction families must preserve 1144 events.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later failure means deterministic current-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes.

## Accepted V144 Rhythm calibration baseline — LOCKED / UNCHANGED
- Name `pitch-shift-41b7a7470fa3245a`.
- Transform chain: historical triple `register::high && section16::1 && stepParity::0`, then same-string pitch shift `pitchClass::4 && stepQuarter::0 => -2 semitones`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-shift-selected-baseline.json`; commit `1f19e2de2199dbcca5f7259fc364e2cac3bea8ce`; blob `ee86c40d68e5c5b8e85bc4d008d9713c35e37a6c`.
- 1144 events; canonical/PDF SHA256 `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`; exact 113/113 generated measures; PDF fidelity `1.0`.
- Full gold: critical `1802`; pitch F1 `0.3043062200956938`; pitch/timing `0.052631578947368425`; string/fret/timing `0.03923444976076555`; chord/voicing `0.0359364201796821`; measure coverage `1.0`; PDF fidelity `1.0`.
- Promotion scope: calibration baseline true; Production false; Rhythm complete false; near-100% false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune: run `32935621669`; fit winner failed validation.
2. Two-signature prune: passed split but lost a generated measure and failed final invariant.
3. Triple prune: consumed by historical triple baseline.
4. Additive four-signature prune: run `32938769540`; 512 candidates, none cleared fit; report blob `5928e9687414c1e118653f139eda205237584ee0`; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch-shift: one-shot `32940695879` SUCCESS; winner became current accepted baseline; report blob `a49e48368d2a45276d09e5746ce7cb4798828470`; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Same-string contextual joint pitch+step shift: one-shot `32970149662` SUCCESS; fit-locked winner passed validation but failed canary, so current baseline remained selected; report blob `9fb212e5877dee91ef189f2aaaa15298cdf8cef2`; persisted report commit `64c067662cc8ba0129f63fa72a6b971cd5a2823d`; sealed workflow commit `215fc49106ef3501b71452b1f6c9f6d638cafd77`, archived workflow blob `47b8667d86fdaf9d82ca9db0d79ce65dea7ad42c`.

## Current-baseline fit-only diagnostic — COMPLETE / SEALED
- Implementation commit `5d3a93d7653e6dab046b78eec7eb9b3bfabec12b`, blob `4a82232f8c7fe65be137b6627f553f7aa3416a31`.
- Helper tests commit `75629202f5a2cb9e76a3a1a28510de69980d5dc6`, blob `85e2e69a013dc96584118e82749a1ba08251ad4e`.
- CPU gate run `32941364938` SUCCESS.
- Diagnostic run `32941513185` SUCCESS; report bot commit `699d9cf2bfb55be5fe269fd57bba261b66c7d323`; report blob `9a187bba4159c0454089d40644a89d6859870fcc`.
- No candidate construction/ranking/selection; no validation/canary labels used.
- Fit: generated `643`, reference `594`, critical `1101`; pitch matched `143` / F1 `0.23120452708164918`; tight pitch/timing `33` / F1 `0.053354890864995966`; gross ±2-step pitch/timing `68`; exact string/fret/timing `25` / F1 `0.04042037186742118`.
- Shape signals: timing opportunity `110`; position-remap opportunity `8`; same-onset wrong-pitch substitutions `179`.
- Diagnostic ceilings only: timing alignment of existing pitch matches -> pitch/timing F1 `0.23120452708164915`; position remap of tight pitch matches -> string/fret/timing F1 `0.05335489086499596`; count-preserving pitch correction pitch ceiling `0.9603880355699272`.

## Joint contextual pitch+step correction family — COMPLETE / CONSUMED / SEALED
- Policy `modal/v144_rhythm_pitch_step_shift_policy.py`; pre-registration commit `6f1a8e633d052729c102d35fb487b903fe5af65c`; blob `b769522c1e083bd989e3b64297cb726ff6e6bf3c`.
- Search implementation `validation/v144_rhythm_calibration/search_contextual_pitch_step_shifts.py`; blob `b2d2c044c586178fbd755f1ac411dffe3131cfd6`.
- CPU search gate run `32969889867` SUCCESS.
- One-shot run `32970149662` SUCCESS; fit locked `pitch-step-shift-07ac05faf49bf435` (`pitchClass::2 && registerStep::high:1 => pitch -1, step -1`, 28 changed events, SHA `77036154faaf692f857d460e6550a8775f0398950e0dcefcc89f36b6c308d2b6`).
- Fit passed; validation passed; canary failed on pitch-content regression `-0.0047085054757688705`; fallback retained current baseline; no alternate selection; no full calibration.
- Independent PDF-event fidelity passed at `1.0`.
- Report blob `9fb212e5877dee91ef189f2aaaa15298cdf8cef2`; workflow archived in `215fc49106ef3501b71452b1f6c9f6d638cafd77` / blob `47b8667d86fdaf9d82ca9db0d79ce65dea7ad42c`.
- **Consumed: never replay/reselect/retune or use its validation/canary outcomes to construct/rank a successor family.**

## Joint contextual pitch + adjacent-string position family — PRE-REGISTERED / POLICY-GATED / NOT SEARCHED
- Fit-only rationale: the sealed current-baseline diagnostic exposes both large same-onset wrong-pitch opportunity (`179`) and a distinct string/fret positioning gap (`8`) without reading validation/canary labels. A family that requires both pitch and string-position changes can improve the mandatory pitch-content metric while being materially distinct from consumed pitch-only and pitch+step families.
- Policy `modal/v144_rhythm_pitch_position_shift_policy.py`; pre-registration commit `28f14cfd5cc8bdd64160732cac8343a7553bbaa3`.
- Deterministic policy tests `modal/tests/test_v144_rhythm_pitch_position_shift_policy.py`; commit `e72efebcb827abfa47eda01cc0be79f332cb72e0`.
- CPU-gate wiring commit `effe6144a4a7652817a7ab4f587ffa4c8ccff396`; run `32970902634` **SUCCESS**.
- Rule identity is source `pitchClass::<n>` + one reference-free structural context signature + fixed non-zero semitone shift + fixed non-zero adjacent-string shift.
- Fixed semantic bounds: semitone shift within ±12; string shift exactly one adjacent string (`-1` or `+1`); zero string shift is forbidden so the family cannot collapse into the consumed pitch-only family.
- Fit-only construction inherits deterministic same-onset exact-pitch-removal then minimum-absolute-MIDI-distance pairing, then retains only pairs whose reference target requires both non-zero pitch and adjacent-string changes and exactly matches a valid guitar tuning position.
- Runtime receives only generated events + locked signatures + fixed pitch/string shifts; no reference runtime input.
- Runtime preserves event count, eventIndex/list order, measure, step/timing, duration and all non-position metadata; recomputes fret from E-standard open-string MIDI for the shifted string and shifted pitch; invalid string/fret targets are skipped, never clamped.
- Linked bend/legato/slide/hammer/pull events remain ineligible.
- **No search implementation, search invariant test, candidate evaluation, report, fit lock, validation, canary, full-gold result, one-shot workflow, or promotion exists yet.**

## Immediate next actions
1. Implement search-level logic for the pre-registered joint pitch+position family against the locked current baseline, with deterministic candidate naming and strict proof that only MIDI/string/fret may change together while timing/measure/order/count/other metadata remain fixed.
2. Add deterministic search-level invariant tests and wire the search implementation/tests into the CPU gate; do not evaluate candidates before that gate succeeds.
3. Only after the search-level CPU gate succeeds, permit one exact-message/path-gated CPU one-shot with fixed support `3`, max candidates `256`, pitch bound `12`, adjacent-string bound `1`.
4. One-shot semantics remain fit-only construction/ranking → one locked winner → validation → canary → full-gold → independent PDF-event invariant; later failure means current-baseline fallback with no alternate selection; archive workflow immediately after one run.
5. Never replay/reselect/retune any consumed family; do not start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
