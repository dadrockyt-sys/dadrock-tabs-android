# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Accepted 1144-event triple baseline remains locked. Single/pair/triple/quad deletion families are consumed and two fit-only diagnostics show deletion is structurally insufficient. A materially new reference-free contextual same-string pitch-shift family is now pre-registered and wired into the CPU gate; the final linked-technique regression gate is running. No pitch-shift candidate search has been executed or selected.**

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

## Accepted V144 Rhythm calibration baseline — LOCKED
- Candidate: `prune-triple-67348efe50436fc5` = `register::high && section16::1 && stepParity::0`.
- Event count: **1144**.
- Canonical/PDF-event SHA256: `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
- Generated measures: exact 113/113; missing `[]`; extra `[]`; PDF-event fidelity `1.0`.
- Full gold: critical mismatch `1810`; pitch F1 `0.2909090909090909`; pitch/timing `0.045933014354066985`; string/fret/timing `0.031578947368421054`; chord/voicing `0.023496890117484452`; measure coverage `1.0`; PDF fidelity `1.0`.
- Manifest: `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, blob `ba8dec9a1c3155816f5841a32ee52ced7998c110`.
- Promotion scope remains calibration-baseline only; Production false; Rhythm complete false; near-100% false.

## Consumed families — NEVER REPLAY / RESELECT
1. Single-signature prune: fit winner failed validation; run `32935621669`.
2. Two-signature conjunction prune: passed split but lost a generated measure and failed final invariant.
3. Triple prune family: consumed by accepted baseline above; do not select another triple.
4. Additive four-signature prune: actual one-shot run `32938769540` SUCCESS, exactly 512 fit-only candidates from 577 unmatched fit-generated notes; no candidate cleared fit, deterministic accepted-baseline fallback retained. Persisted report blob `5928e9687414c1e118653f139eda205237584ee0`; workflow sealed commit `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Do not escalate to five-signature/deeper deletion families from current evidence.

## Fit-only diagnostics — COMPLETE / SEALED
### Deletion/pruning ceiling
- Run `32939218722` SUCCESS; report `debug/v144-rhythm-calibration/baseline/v144-fit-only-pruning-ceiling.json`, blob `6064ede57f4ec18a3c961f4c8b82b98aad26efdf`.
- Fit: generated `643`, reference `594`, critical `1105`; pitch matched `138` / F1 `0.2231204527081649`; tight pitch/timing matched `28` / F1 `0.04527081649151172`; exact string/fret/timing matched `20` / F1 `0.03233629749393695`.
- Perfect deletion-only oracle ceilings: pitch F1 `0.3770491803278689`; pitch/timing `0.09003215434083602`; string/fret/timing `0.06514657980456026`.

### Error mechanisms
- Run `32939297662` SUCCESS; report `debug/v144-rhythm-calibration/baseline/v144-fit-error-mechanisms.json`, blob `4d1f143142b15b3cb9270eca291dbc12d30dff80`.
- Fit counts: generated `643`, reference `594`; pitch-content matched `138`; tight pitch/timing `28`; gross ±2-step pitch/timing `66`; exact string/fret/timing `20`.
- Mechanisms: same-onset wrong-pitch substitution slots `184`; displaced same-measure pitch matches `110`; gross-only timing recovery `38`; correct pitch/timing but wrong string/fret `8`; gross unmatched generated/reference `577/528`; pitch FP/FN `505/456`.
- Diagnostic oracle: perfect pitch-FP deletion ceiling `0.3770491803278688`; count-preserving pitch-correction ceiling `0.9603880355699272`.
- Conclusion is shape-only: another deletion family is much less promising than correction. These oracle values are not runtime rules and are not generalization evidence.

## New contextual same-string pitch-shift family — PRE-REGISTERED, NOT SEARCHED
- Canonical policy: `modal/v144_rhythm_pitch_shift_policy.py`.
- Initial pre-registration commit `c03b94dbfa7169255893062a963b4a0aa56a30d3`; linked-technique safety hardening commit `fb2e07b3288e8e1a082281c48856ca004f892586`.
- Duplicate temporary policy was removed in commit `883e5ed218c0ad245f364a4294428fd8926e14b3`; only the canonical module remains.
- Rule shape is **source `pitchClass::<n>` + one reference-free structural context signature + fixed non-zero semitone shift**, bounded to ±12 semitones.
- Construction-time fit evidence uses deterministic same-onset substitution pairing: exact MIDI matches are removed first, then remaining generated/reference notes at the same onset are paired by smallest absolute MIDI distance with deterministic tie-breaking.
- Ranking is fit-only by correction precision/support with default minimum correction support `3` and maximum candidates `256`; validation/canary are not inputs to construction/ranking.
- Runtime application receives only generated events + locked signatures + semitone shift; it never receives the professional reference.
- Runtime transform is count-preserving and timing-preserving: same measure, step, duration, string, event order/count; shifts `midi` and `fret` together on the same string and skips out-of-range frets.
- Bend/legato/slide/hammer/pull linked or labeled events are ineligible so target metadata cannot become inconsistent.
- Tests: `modal/tests/test_v144_rhythm_pitch_shift_policy.py`; original concurrent test commit `9cb2d339702cebc5953b480b1c582eb0675ad012`; explicit linked-technique regression commit `bbb0b14af9c1b890319d26580d2e7bec8a19fd76`.
- CPU gate integration commit `18ad356ce8ca94e18d43f088ad9b7f0ebd560f18`.
- Safety-hardened CPU gate run `32939793740` SUCCESS.
- Final linked-technique regression CPU gate run `32939947264` is currently in progress at this checkpoint.
- **No pitch-shift one-shot search workflow/report exists yet. No correction candidate has been locked, validated, canaried, or promoted.**

## Immediate next actions
1. Confirm CPU gate run `32939947264` passes. If it fails, fix only the policy/test defect and re-gate; do not search.
2. After gate success, checkpoint again before creating any search implementation.
3. Then implement a one-shot **fit-only contextual pitch-shift search** from the unchanged accepted 1144-event baseline. Construction/ranking may use fit labels only.
4. Require event count `1144` and exact 113/113 generated-measure preservation for every candidate considered for fit lock.
5. Lock exactly one fit winner under the existing fixed selector; then gate only that winner through validation → canary → full-gold → independent PDF-event fidelity. No alternate after failure.
6. Seal the search workflow immediately after its single actual execution and never retune/replay this family from its result.
7. Do not promote Rhythm, start Bass/Lead, claim near-100% quality, or use Modal/L4/GPU without fresh explicit user authorization.
