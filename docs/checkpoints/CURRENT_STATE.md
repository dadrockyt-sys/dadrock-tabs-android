# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 21:25 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may never read/train/tune/select from it. After any scored failure, corrections must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Completion requires professional score >= `0.99`, critical mismatches = `0`, PDF-event fidelity = `1.0`.

**Rhythm is NOT complete.**

## Protected runtime / approved fixture

Protected runtime:
- `analyzer/v143_reference_free_rhythm_pipeline.py`
- exact Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`

Approved fixture:
- `public/gomywayfullaitest.m4a`
- SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current gates: protected blob exact; Production unchanged.

## Human scorer source — scorer-only

Immutable source:
- `Professionalexample.jpg`
- SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- human-written Rhythm Guitar revision `7868948`, 2026-07-12, measures 1–113

Exact scorer-only structured-source artifact:
- artifact `9502117311`
- artifact SHA256 `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw `rhythm-track.json` SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`

Deterministic scorer reference V2:
- SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- 113 contiguous measures
- 603 playable onset objects
- 946 playable note entries
- 104 populated measures
- completeness passes
- reference payload never committed

Historical manually structured scorer JSON SHA `4d3e7ee...` (577 onsets/925 notes) was temporary and not preserved. Never claim byte identity with V2.

## Retired scored freeze 1 — corrected candidate — NEVER RESCORE

Artifact `9499229323`; event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`.
- 979 attacks
- 2,009 rendered notes
- all 113 measures
- PDF fidelity 1.0

Professional score FAILED:
- pitchContentF1 `0.2463620981387479`
- pitchTimingTolerantF1 `0.07106598984771574`
- stringFretTimingTolerantF1 `0.026395939086294416`
- chordPitchSetTolerantF1 `0.0025284450063211127`
- exactVoicingTolerantF1 `0.0025284450063211127`
- measureCoverageRecall `1.0`
- critical mismatches `2541`

## Retired scored freeze 2 — precision candidate — NEVER RESCORE

Fresh pre-holdout Actions run `32680719988` GREEN.
Artifact:
- name `v143-precision-rhythm-professional-freeze`
- artifact ID `9504147164`
- artifact SHA256 `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`

Freeze:
- 714 attacks
- 967 rendered authenticated notes
- all 113 measures
- event/PDF-event SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`
- PDF fidelity `1.0`
- full/preview PDF 4 pages

Professional score Actions run `32681394580` FAILED:
- generated notes `967`; reference notes `946`
- pitchContentF1 `0.26241505488761113`
- pitchTimingTolerantF1 `0.052273915316257184`
- stringFretTimingTolerantF1 `0.028227914270778882`
- chordPitchSetTolerantF1 `0.007593014426727412`
- exactVoicingTolerantF1 `0.007593014426727412`
- measureCoverageRecall `1.0`
- PDF fidelity `1.0`
- critical mismatches `1649` = generated unmatched `835` + reference unmatched `814`
- rhythmComplete false

Broad/general conclusion only: count inflation is largely fixed; remaining dominant failures are pitch identity + timing/grid identity. Never derive song-specific runtime rules from scorer events.

## BUG 1 — precision-selected fundamental was lost in adapter — FIXED / PROVED

Discovered after score 2:
- `v143_contextual_prune_precision_shadow.py` correctly computed an explicit lower harmonic-family primary/fundamental.
- `v143_contextual_prune_precision_candidate_events.py` passed only the selected pitch set into the old voicing adapter.
- the old adapter then re-ranked those pitches by its own dominant/quality logic, allowing the chosen lower fundamental to be replaced by a stronger overtone.

General/reference-free fix:
- `PrecisionShadowResult` now carries explicit `primary_midis` for every retained attack.
- precision candidate adapter preserves that explicit primary through the proxy/voicing path instead of silently re-ranking it.
- no scorer/reference fields, song labels, or target note counts enter the fix.

Proof:
- `debug/v143-contextual-prune/precision-shadow-cpu-proof.json` schema v2 GREEN
- trigger SHA `05874926efa83e162c2471399618cce0bf19cd1c`
- `explicitPrimaryPreserved: true`
- `primaryPropagationCheckerPassed: true`
- no invented attack/pitch/relocation
- protected blob exact; Production false.

Latest approved-audio precision-primary preservation run:
- Actions run `32682664616`
- trigger SHA `625e20563498d469b4868ac5d14e32041559659f`
- source fixture SHA exact
- corrected attacks `982`
- precision retained attacks `711`
- retained pitch hypotheses `962`
- explicitPrimaryMidiCount `711` == retainedAttackCount; complete true
- fundamental promotions `134`
- all 113 measures populated; fail-safe `0`
- no invented/relocated attack; no invented pitch
- protected blob exact; Production false.

### New determinism concern discovered

The earlier accepted precision run on the same approved fixture reported `714` retained attacks / `968` pitch hypotheses / `136` promotions, while the latest rerun reports `711` / `962` / `134` even though the intended musical precision rule is the same except for explicit-primary propagation.

Do **not** assume this difference is harmless. Before accepting a new musical freeze, prove where this small run-to-run drift comes from (separation/model nondeterminism, carrier aggregation ordering, or another upstream source). Freeze identities are immutable, but runtime reproducibility should be understood and controlled where possible.

## BUG 2 — original beat tracker emits sub-beat duplicates / early stop — CONFIRMED

Approved-audio timing diagnostic established:
- tempo `129.19921875` BPM
- original beat count `447`
- **38 interval outliers** relative to expected beat period
- many intervals are sub-beat duplicates (roughly 0.45–0.75 beat periods)
- no compensating long-gap pattern large enough to justify those extras
- tracker ended substantially before active audio ended.

Bar-phase-only evidence is weak/unstable:
- original accent-only `downbeatIndexMod4=1`, `firstBeatInMeasure=3`, bar confidence about `0.08797`
- multi-signal phase consensus is not stable across halves and does not justify forcing a phase change yet.

Therefore the primary timing bug is currently **beat-grid pulse continuity**, not a proven 4/4 phase rotation.

## Reference-free beat-grid repair shadow — NOT ACCEPTED YET

Files:
- `analyzer/v143_reference_free_beat_grid_repair.py`
- `analyzer/check_v143_reference_free_beat_grid_repair.py`
- workflow `.github/workflows/v143-reference-free-beat-grid-repair.yml`

General design:
- preserve tempo and current bar phase while diagnosing/repairing pulse continuity
- anchor to a long stable interval run
- predict one pulse per beat
- snap only to nearby full-mix transient evidence
- interior weak beats may use tempo continuity
- NEW leading/trailing extension requires audio evidence (transient or RMS energy)
- short weak boundary gaps may bridge only if the next 1–2 predicted beats have physical evidence
- no scorer/reference labels, target measure counts, or song identity enter.

Latest approved-audio repair run:
- run `32682813632`
- trigger SHA `ec426f8093f3a27346c013ad8840cb427dea4d93`
- original `447` beats → repaired `445`
- original interval outliers `38` → repaired `0`
- repaired interval ratio P01 `0.90`, P50 `1.00`, P99 `1.075`
- repaired first beat `0.6965986395s`
- repaired last beat `207.2380952381s`
- active audio end `209.1231746032s`
- trailing extension `9` beats
- lookahead bridge count `0`
- protected blob exact; Production false.

However the repaired subdivision grid currently covers only **112 measures**, not the original 113, and repaired phase consensus remains unstable (`winnerDownbeatIndexMod4=2`, confidence ~`0.198`, stableAcrossHalves false).

**Do not accept this repair yet and do not create/score a new Jimmy freeze from it.** It successfully removes the sub-beat pathology but the boundary/measure extent still needs a general audio-only resolution.

## Current work NOW

1. Prove the source of the small approved-audio precision rerun drift (`714/968/136` vs `711/962/134`) using only internal deterministic hashes/counts at each stage. Do not access human scorer data.
2. Finish the beat-grid boundary repair so it removes sub-beat duplicates without prematurely losing legitimate end-of-audio grid coverage. Do not force a target measure count; use audio evidence only.
3. Re-evaluate four-way bar-phase consensus only after the pulse grid itself is stable. A phase change is allowed only if independent signals become strong/stable after repair.
4. Verify the explicit-primary propagation fix again on the finally accepted timing/carrier path.

## Next steps after those bugs are green

1. Run CPU + approved-audio anti-leakage/protected-runtime proofs for the combined **timing-grid repair + explicit-primary propagation** candidate.
2. Accept the correction only if all behavior is general/reference-free, no unsupported attacks/pitches are invented, boundary behavior is physically justified, and runtime is sufficiently reproducible.
3. Once accepted, create a **brand-new approved-audio Jimmy analysis → authenticated events → immutable freeze → preview/full PDF** identity. Never reuse/rescore the `e693602...` freeze.
4. Verify PDF-event fidelity exactly `1.0`, protected blob exact, Production unchanged.
5. Only after the new freeze/PDF identity is locked, reopen scorer-only human source V2 and run the unchanged >=`0.99` professional holdout.
6. If holdout fails, report exact new metrics but use failures only as broad classes; any further musical correction remains general/reference-free and requires another brand-new freeze before scoring.
7. Continue until >=`0.99`, zero critical mismatches, fidelity `1.0`.
8. Then create `Final Rhythm Pipeline`; only afterward resume Bass, then Lead.
