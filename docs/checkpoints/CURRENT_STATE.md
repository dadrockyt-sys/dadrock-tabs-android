# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The contextual same-string pitch-shift family has completed its single guarded CPU one-shot, passed every fixed gate and the independent PDF-event invariant, and is now consumed/sealed. Its winner is eligible for calibration-baseline promotion only. Production remains untouched; Rhythm is not complete and near-100% quality is not proven. Next is to persist a dedicated selected-calibration-baseline manifest for the accepted pitch-shift winner, then continue only from that new calibration baseline.**

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
- Fit labels may construct/rank; validation/canary only gate the one locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity must be `1.0`.
- Candidate must preserve all 113 accepted-baseline generated measure IDs before fit lock.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later gate failure returns to deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed candidate outcomes.

## Previous accepted calibration baseline — triple, now superseded if manifest promotion is persisted
- Candidate: `prune-triple-67348efe50436fc5` = `register::high && section16::1 && stepParity::0`.
- Event count: `1144`; event/PDF SHA256: `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
- Generated measures: exact 113/113; PDF-event fidelity `1.0`.
- Full gold: critical `1810`; pitch F1 `0.2909090909090909`; pitch/timing `0.045933014354066985`; string/fret/timing `0.031578947368421054`; chord/voicing `0.023496890117484452`; measure coverage `1.0`; PDF fidelity `1.0`.
- Manifest: `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, blob `ba8dec9a1c3155816f5841a32ee52ced7998c110`.

## Consumed historical families — NEVER REPLAY / RESELECT
1. Single-signature prune: run `32935621669`; fit winner failed validation.
2. Two-signature conjunction prune: passed split but lost a generated measure and failed final invariant.
3. Triple prune family: consumed by the previous accepted triple baseline; never select another triple candidate.
4. Additive four-signature prune: run `32938769540` SUCCESS; 512 fit-only candidates; none cleared fit; deterministic triple-baseline fallback. Report blob `5928e9687414c1e118653f139eda205237584ee0`; workflow sealed commit `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Contextual same-string pitch-shift family: **consumed by successful winner below**. Never replay, retune support/shift bounds, enlarge/reorder its candidate set, or select a runner-up later.

## Fit-only diagnostics that motivated correction — COMPLETE / SEALED
### Deletion/pruning ceiling
- Run `32939218722` SUCCESS; report blob `6064ede57f4ec18a3c961f4c8b82b98aad26efdf`.
- Fit: generated `643`, reference `594`, critical `1105`; pitch matched `138` / F1 `0.2231204527081649`; tight pitch/timing matched `28` / F1 `0.04527081649151172`; exact string/fret/timing matched `20` / F1 `0.03233629749393695`.
- Perfect deletion-only oracle ceilings: pitch `0.3770491803278689`; pitch/timing `0.09003215434083602`; string/fret/timing `0.06514657980456026`.

### Error mechanisms
- Run `32939297662` SUCCESS; report blob `4d1f143142b15b3cb9270eca291dbc12d30dff80`.
- Same-onset wrong-pitch substitutions `184`; displaced same-measure pitch matches `110`; gross-only timing recovery `38`; correct pitch/timing but wrong string/fret `8`; gross unmatched gen/ref `577/528`; pitch FP/FN `505/456`.
- Count-preserving pitch-correction diagnostic ceiling `0.9603880355699272`; diagnostic shape guidance only, never a runtime oracle/generalization claim.

## Contextual same-string pitch-shift implementation — FROZEN FOR THIS CONSUMED FAMILY
- Policy: `modal/v144_rhythm_pitch_shift_policy.py`, blob `d9998c59acddba070069668d62bcb1c3cdaf2b05`.
- Rule shape: source `pitchClass::<n>` + one reference-free structural context signature + fixed non-zero semitone shift bounded to ±12.
- Fit construction: deterministic same-onset substitution pairing; exact MIDI matches removed first, then minimum absolute MIDI distance with deterministic tie-breaking.
- Fixed family values: minimum correction support `3`, maximum candidates `256`, maximum absolute semitone shift `12`.
- Runtime gets only generated events + locked signatures + fixed shift; professional reference is not a runtime input.
- Runtime is event-count/timing/string preserving and shifts MIDI/fret together; bend/legato/slide/hammer/pull linked/labeled events are ineligible.
- Search: `validation/v144_rhythm_calibration/search_contextual_pitch_shifts.py`, hardened blob `9b35de6cf94a190a8700274334fcc85c5ad986c2`, invariant-hardening commit `619d60f5bb8293dd860deb499ccb8b0e85ac2e78`.
- Search-level regression tests: `modal/tests/test_v144_rhythm_pitch_shift_search.py`, commit `e29e82c090905b4b33eaf88147556b2162e1922d`.
- CPU-gate wiring commit `6fe747756ec253134d812e77d23bcd4ac8c39472`; run `32940560733` SUCCESS. Candidate construction did not run in this gate.

## Contextual pitch-shift one-shot — CONSUMED / PASSED / SEALED
- Exact arming commit: `876ba06fdc557ba695d542bacc31a90aa244c5a3`, message `v144 execute contextual pitch shift one-shot`.
- **Single actual search run `32940695879` SUCCESS. Never rerun/retry it.**
- Every substantive step passed: immutable inputs, exact implementation pins, fit-only construction/search, stream invariants, locked-stream checks, independent PDF-event identity, full invariant, immutable recheck, and single-report persistence.
- Candidate construction: `41` ranked / `41` evaluated candidates from accepted-baseline fit evidence only; fit canonical generated events `643`, fit reference notes `594`; validation/canary/historical family outcomes were not used for construction/ranking.
- Persisted report: `debug/v144-rhythm-calibration/candidates/contextual-pitch-shift-search.json`; bot commit `8142a942c234c4f00fe7f53deff8a34f4122448b`; report blob `a49e48368d2a45276d09e5746ce7cb4798828470`.
- **Locked/selected winner:** `pitch-shift-41b7a7470fa3245a`.
- Runtime rule: `pitchClass::4 && stepQuarter::0 => -2 semitones`.
- Fit construction metadata for winner: correction support `10`, eligible generated support `40`, correction precision `0.25`.
- Winner changes exactly `68` of `1144` events; event order/count and all non-pitch metadata are preserved; MIDI/fret move together.
- Winner canonical/PDF-event SHA256: `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`.
- Generated measures: exact 113/113, missing `[]`, extra `[]`.
- Fit gate passed: pitch-content gain `+0.008084074373484268`; no required metric regression; PDF-event fidelity `1.0`.
- Validation passed: pitch-content gain `+0.017316017316017313`; critical mismatch delta `-6`; no regressions; PDF-event fidelity `1.0`.
- Canary passed: pitch-content gain `+0.005115089514066473`; critical mismatch delta `-2`; no regressions; PDF-event fidelity `1.0`.
- Full-gold invariant passed: critical mismatch `1802` (`-8` vs triple baseline); pitch F1 `0.3043062200956938` (`+0.013397129186602907`); pitch/timing `0.052631578947368425` (`+0.00669856459330144`); string/fret/timing `0.03923444976076555` (`+0.007655502392344499`); chord/voicing `0.0359364201796821` (`+0.012439530062197647`); measure coverage `1.0`; independent PDF-event fidelity `1.0`.
- Report result: `calibrationPromotionAllowed=true`, `splitPromotionAllowed=true`, `selectedReason=locked-pitch-shift-candidate-passed-split-and-full-calibration-invariants`, `stoppedAt=complete`.
- Workflow archived/sealed commit `21ca074f3917fb72614686ca5b46a3894ea53374`, archived workflow blob `e960b0d97118de533f68271ccefdfa7766e4e17d`.
- Seal triggered **no pitch-shift search replay**; only unrelated `cleanup-tab-preview` reacted.

## Promotion scope and interpretation
- The successful pitch-shift winner is eligible to become the next **V144 calibration baseline only**.
- It does **not** authorize Production/main changes, does not prove unseen generalization, does not make Rhythm complete, and does not establish near-100% quality.
- The professional target remains a calibration benchmark; all reported gains are calibration gains.

## Immediate next actions
1. Persist a dedicated selected calibration-baseline manifest for `pitch-shift-41b7a7470fa3245a`, explicitly chaining from the prior triple baseline and recording run/report/blob/rule/event SHA/invariant evidence.
2. Mark Production promotion false, Rhythm complete false, near-100% false, unseen generalization false in that manifest.
3. After the manifest is committed, treat event SHA `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6` as the only accepted V144 Rhythm calibration baseline for any future materially new family.
4. Never replay/reselect any consumed single/pair/triple/quad/pitch-shift family or alter their fixed gates after seeing outcomes.
5. Do not start Bass/Lead, modify main/Production, claim near-100% quality, or use Modal/L4/GPU without fresh explicit user authorization.
