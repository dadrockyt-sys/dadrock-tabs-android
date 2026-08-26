# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The accepted baseline is `pitch-shift-41b7a7470fa3245a` at 1144 events / 113 measures / SHA `b6e1f8a8...`. Its pitch-shift family is consumed/sealed. A new fit-only diagnostic on this accepted baseline is complete and shows the strongest remaining actionable shape is joint pitch+onset correction: 110 existing pitch matches are outside tight timing, only 8 tight pitch matches have wrong string/fret, and 179 same-onset wrong-pitch substitutions remain. A timing-only family cannot satisfy the unchanged fit gate because pitch-content gain must be >= 0.005. Next is to pre-register a materially new family requiring both a non-zero pitch shift and a non-zero within-measure step shift.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed; never rerun/retry or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration semantics
- Professional target is a **gold calibration benchmark, not an unseen holdout**.
- Exact structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; completeness 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Never claim unbiased generalization from this benchmark.

## Fixed selector / invariant safety
- Split is deterministic measure+step, seed 144, 60% fit / 20% validation / 20% canary.
- Fit labels may construct/rank; validation/canary only gate one locked winner.
- Fixed fit gate remains: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Every candidate must preserve all 113 accepted-baseline generated measures; count-preserving families must also preserve 1144 events.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later failure means deterministic accepted-baseline fallback; never choose an alternate.
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
4. Additive four-signature prune: run `32938769540`; 512 candidates, none cleared fit; report blob `5928e9687414c1e118653f139eda205237584ee0`; workflow sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch-shift: one-shot run `32940695879` SUCCESS; winner became current accepted baseline; report blob `a49e48368d2a45276d09e5746ce7cb4798828470`; workflow sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.

## Current-baseline fit-only mechanism diagnostic — COMPLETE / SEALED
- Diagnostic implementation `validation/v144_rhythm_calibration/analyze_current_baseline_fit_mechanisms.py`, commit `5d3a93d7653e6dab046b78eec7eb9b3bfabec12b`, blob `4a82232f8c7fe65be137b6627f553f7aa3416a31`.
- Helper tests `modal/tests/test_v144_rhythm_current_baseline_fit_mechanisms.py`, commit `75629202f5a2cb9e76a3a1a28510de69980d5dc6`, blob `85e2e69a013dc96584118e82749a1ba08251ad4e`.
- CPU-gate integration commit `bb7d91b4e589f7d49b65d5e178c4e198ad1ba356`; run `32941364938` SUCCESS. This gate compiled/tested only; it did not open fit labels.
- Exact diagnostic arming commit `ab561106900f56a425c9f329d73675cbcf41cc63`; single diagnostic run `32941513185` SUCCESS.
- Report `debug/v144-rhythm-calibration/baseline/v144-current-baseline-fit-mechanisms.json`; bot commit `699d9cf2bfb55be5fe269fd57bba261b66c7d323`; report blob `9a187bba4159c0454089d40644a89d6859870fcc`.
- Workflow archived commit `c76f733a3ae91c7136ab7e81a68e5b20c264c923`, archived blob `5c20e347d114a5b39ed0103701e6e235976ec4e4`.
- Diagnostic performed **no candidate construction/ranking/selection**; validation/canary labels were not used.

### Current fit score / mechanism counts
- Generated notes `643`; reference notes `594`; critical mismatch `1101`.
- Pitch-content matched `143`, F1 `0.23120452708164918`.
- Tight pitch/timing matched `33`, F1 `0.053354890864995966`.
- Gross ±2-step pitch/timing matched `68`.
- Exact string/fret/timing matched `25`, F1 `0.04042037186742118`.
- Same-onset exact pitch notes `33`.
- Same-onset wrong-pitch substitution slots `179`.
- Existing same-measure pitch matches displaced from exact onset `110`.
- Gross-only timing recoveries `35`; pitch matches still outside gross tolerance/competing `75`.
- Correct tight pitch/timing but wrong string/fret `8`.
- Pitch FP/FN `500/451`; gross unmatched gen/ref `575/526`.

### Shape signals / diagnostic ceilings
- Timing opportunity among existing pitch matches: **110**.
- Position-remap opportunity inside tight pitch matches: **8**.
- Remaining same-onset pitch-substitution opportunity: **179**.
- Perfect timing alignment of existing pitch-content matches would cap pitch/timing F1 at `0.23120452708164915` (diagnostic oracle only).
- Perfect string/fret remap of current tight pitch matches caps string/fret/timing F1 at `0.05335489086499596` (diagnostic oracle only).
- Perfect count-preserving pitch correction pitch-content ceiling remains `0.9603880355699272`; perfect pitch-FP deletion ceiling `0.3880597014925373`.

## Next materially new family — DESIGN BOUNDARY
- Do **not** build a timing-only family: moving onset/step alone cannot change pitch-content F1 and therefore cannot meet the fixed `>=0.005` pitch-content gain gate.
- Do **not** replay same-string pitch-only correction: that family is consumed.
- Safe next shape: **joint contextual pitch + within-measure onset correction**, requiring both:
  - non-zero fixed semitone shift, and
  - non-zero fixed step shift.
- Runtime must remain reference-free after locking, preserve event count and all 113 measures, preserve duration/string/non-pitch metadata, shift MIDI+fret together, and keep step within the same 16-step measure.
- Construction/ranking may use only current-baseline fit labels. Validation/canary remain closed until one fit winner locks.
- Reuse existing semantic bounds rather than outcome-tuning: semitone shift bounded to ±12; timing shift should be bounded by the existing scorer gross timing tolerance (±2 steps), with zero excluded so the family cannot collapse into the consumed pitch-only family.

## Immediate next actions
1. Pre-register a canonical joint pitch+step correction policy with fixed non-zero semitone and step shifts; no search yet.
2. Exclude linked pitch-technique events and any transform that would leave step 0..15 or fret 0..36; skip rather than clamp.
3. Add deterministic pairing/ranking/apply tests proving fit-only construction, runtime reference-free behavior, event-count/measure preservation, non-pitch metadata preservation, and no overlap with pitch-only rules (`stepShift != 0`).
4. Wire policy/tests into the CPU gate and require SUCCESS before implementing any one-shot search.
5. Never replay/reselect consumed families; do not start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
