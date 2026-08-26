# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted baseline is `pitch-shift-41b7a7470fa3245a` (1144 events / 113 measures / SHA `b6e1f8a8...`). Its consumed pitch-only family is sealed. Current-baseline fit diagnostics are complete. The materially new joint contextual pitch+within-measure-step correction family is pre-registered and policy-gated. Search-level implementation + deterministic invariant tests now exist and are wired into the CPU gate; CPU gate run `32969889867` is currently in progress. No joint-family candidate evaluation, one-shot workflow, report, locked candidate, validation, canary, or promotion exists yet.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA256 `7ed5166a73793e95544195204d99c6bec1` is NOT correct — canonical event SHA remains `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
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

## Accepted V144 Rhythm calibration baseline — LOCKED
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

## Current-baseline fit-only diagnostic — COMPLETE / SEALED
- Implementation commit `5d3a93d7653e6dab046b78eec7eb9b3bfabec12b`, blob `4a82232f8c7fe65be137b6627f553f7aa3416a31`.
- Helper tests commit `75629202f5a2cb9e76a3a1a28510de69980d5dc6`, blob `85e2e69a013dc96584118e82749a1ba08251ad4e`.
- CPU gate run `32941364938` SUCCESS.
- Diagnostic run `32941513185` SUCCESS; report bot commit `699d9cf2bfb55be5fe269fd57bba261b66c7d323`; report blob `9a187bba4159c0454089d40644a89d6859870fcc`.
- Diagnostic workflow sealed `c76f733a3ae91c7136ab7e81a68e5b20c264c923`, blob `5c20e347d114a5b39ed0103701e6e235976ec4e4`.
- No candidate construction/ranking/selection; no validation/canary labels used.
- Fit: generated `643`, reference `594`, critical `1101`; pitch matched `143` / F1 `0.23120452708164918`; tight pitch/timing `33` / F1 `0.053354890864995966`; gross ±2-step pitch/timing `68`; exact string/fret/timing `25` / F1 `0.04042037186742118`.
- Shape signals: timing opportunity `110`; position-remap opportunity `8`; same-onset wrong-pitch substitutions `179`.
- Diagnostic ceilings only: timing alignment of existing pitch matches -> pitch/timing F1 `0.23120452708164915`; position remap of tight pitch matches -> string/fret/timing F1 `0.05335489086499596`; count-preserving pitch correction pitch ceiling `0.9603880355699272`.

## Joint contextual pitch+step correction family — SEARCH LOGIC IMPLEMENTED / CPU GATE IN PROGRESS / NOT SEARCHED
- Rationale: timing-only cannot pass the unchanged fit gate because it cannot improve pitch-content F1; pitch-only family is consumed. New family therefore requires **both** pitch and step changes.
- Policy `modal/v144_rhythm_pitch_step_shift_policy.py`; pre-registration commit `6f1a8e633d052729c102d35fb487b903fe5af65c`; blob `b769522c1e083bd989e3b64297cb726ff6e6bf3c`.
- Policy tests `modal/tests/test_v144_rhythm_pitch_step_shift_policy.py`; commit `1fe3d8e95cc8d3be587602328ed69e065796d7f3`; blob `fd8da156208deee90795519bc1e072efd10ec46d`.
- Initial CPU-gate integration commit `0dcd404607952ab73ab14cc238c5921bcc76289e`; run `32941861368` **SUCCESS**.
- Search implementation `validation/v144_rhythm_calibration/search_contextual_pitch_step_shifts.py`; commit `80d055d0b1c1f4eec86a3ae11104222e0e4292e1`.
- Search invariant tests `modal/tests/test_v144_rhythm_pitch_step_shift_search.py`; commit `8fe0e396c95d6a42c8c3af3310bb2bb12a0ebb51`.
- CPU gate wiring commit `490a85256a6cb2e3e6df806188f1762c8e7eddec`; run `32969889867` currently **IN PROGRESS**.
- Search reconstructs current accepted baseline reference-free from frozen V5 via historical triple + sealed pitch shift and hard-checks current event SHA `b6e1f8a8...` before any fit construction.
- Search construction/ranking uses current-baseline **fit labels only** via the pre-registered deterministic same-measure pairing policy.
- Search-level invariants require 1144 events, stable eventIndex/list order, protected measure/string/duration/other metadata, equal MIDI/fret delta, both pitch+step changing together, bounded non-zero deltas, within-measure step, and exact locked per-candidate deltas.
- Rule identity: source `pitchClass::<n>` + one reference-free structural context signature + fixed semitone shift + fixed step shift.
- Both shifts are required non-zero, preventing collapse into consumed pitch-only or timing-only families.
- Fixed semantic bounds: semitone shift within ±12; step shift within ±2 (existing gross timing tolerance), zero excluded.
- Construction-time fit pairing removes exact pitch+step matches first, then pairs remaining same-measure notes deterministically by smallest absolute step delta, then pitch delta, with stable tie-breaking.
- Runtime receives only generated events + locked signatures + fixed pitch/step shifts; no reference runtime input.
- Runtime preserves event count, eventIndex/list order, measure, string, duration and other metadata; MIDI/fret move together; step stays within the same 16-step measure.
- Linked bend/legato/slide/hammer/pull events are excluded; out-of-range fret/step transformations are skipped, never clamped.
- **No joint-family candidate evaluation, report, locked candidate, validation, canary, full-gold result, PDF invariant, one-shot workflow, or promotion exists yet.**

## Immediate next actions
1. Resolve CPU gate run `32969889867`; if it fails, fix only search-level implementation/tests and gate again without evaluating candidates.
2. Only after the search-level CPU gate succeeds, create one exact-message/path-gated CPU one-shot workflow with fixed family values: support `3`, max candidates `256`, pitch bound `12`, step bound `2`.
3. That one-shot must use fit labels only for construction/ranking, lock exactly one fit winner, then gate validation → canary → full-gold → independent PDF-event invariant; later failure means current-baseline fallback with no alternate selection.
4. Immediately seal/archive the one-shot workflow after its single run and record report/commit/blob/run identities here.
5. Never replay/reselect consumed families; do not start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
