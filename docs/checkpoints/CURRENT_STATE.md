# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
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

## Human scorer source

Immutable source:
- `Professionalexample.jpg`
- SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- human-written Rhythm Guitar revision `7868948`, 2026-07-12, measures 1–113

Exact scorer-only structured-source artifact:
- artifact `9502117311`
- artifact SHA256 `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw `rhythm-track.json` SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`

Deterministic scorer reference V2 from that immutable human source:
- SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- 113 contiguous measures
- 603 playable onset objects
- 946 playable note entries
- 104 populated measures
- completeness passes
- reference payload never committed

Historical manually structured scorer JSON SHA `4d3e7ee...` (577 onsets/925 notes) was temporary and not preserved. Never claim byte identity with V2.

## Retired scored freeze 1 — corrected candidate

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

Never rescore after tuning.

## General/reference-free precision correction — ACCEPTED

Files:
- `analyzer/v143_contextual_prune_precision_shadow.py`
- `analyzer/check_v143_contextual_prune_precision_shadow.py`
- `analyzer/v143_contextual_prune_precision_shadow_modal.py`
- `analyzer/v143_contextual_prune_precision_candidate_events.py`
- `analyzer/v143_contextual_prune_precision_candidate_product_modal.py`
- `validation/rhythm_holdout/prepare_precision_candidate_freeze_payload.mjs`

Approved-audio internal result from Actions run `32680288667`:
- 979 → 714 attacks
- 7,595 raw candidate pitch hypotheses → 968 retained
- 487 attacks with 1 pitch; 201 with 2; 25 with 3; 1 with 4
- max retained pitch hypotheses per attack 4
- 136 general harmonic-family fundamental promotions
- all 113 measures preserved
- fail-safe attack count `0`
- no invented/relocated attack
- no invented pitch
- protected runtime exact
- Production unchanged

The workflow's Modal analysis + invariant validation succeeded; its final git push lost a race. Exact result was recovered from job log and recorded in `debug/v143-contextual-prune/precision-shadow-approved-audio-summary.json`.

## Retired scored freeze 2 — precision candidate

Fresh pre-holdout Actions run `32680719988` GREEN.
Artifact:
- name `v143-precision-rhythm-professional-freeze`
- artifact ID `9504147164`
- artifact SHA256 `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`

Freeze:
- 714 attacks
- 967 rendered authenticated notes
- 968 supported pitches before legal voicing; only 1 voicing drop
- all 113 measures
- event SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`
- PDF event SHA identical
- PDF fidelity `1.0`
- full/preview PDF 4 pages
- reference not opened before freeze
- protected/live/Production unchanged

Professional score Actions run `32681394580` FAILED:
- generated notes `967`
- reference notes `946`
- pitchContentF1 `0.26241505488761113`
- pitchTimingTolerantF1 `0.052273915316257184`
- stringFretTimingTolerantF1 `0.028227914270778882`
- chordPitchSetTolerantF1 `0.007593014426727412`
- exactVoicingTolerantF1 `0.007593014426727412`
- measureCoverageRecall `1.0`
- PDF fidelity `1.0`
- critical mismatches `1649`
  - gross unmatched generated `835`
  - gross unmatched reference `814`
- no missing measures
- rhythmComplete false

This freeze is now retired and must never be rescored after tuning.

## What score 2 established — broad/general only

1. **Attack/polyphony count inflation is largely fixed.** Generated note count (967) is now close to scorer reference note count (946); critical mismatches fell 2541 → 1649.
2. **Remaining dominant failures are pitch and timing identity, not total count.** Gross unmatched counts are nearly symmetric (835 vs 814).
3. Pitch content improved slightly (~0.246 → ~0.262), but timing-tolerant F1 degraded (~0.071 → ~0.052). This strongly elevates timing/bar-phase/grid identity as a general failure class.
4. String/fret and exact chord/voicing remain near zero, consistent with incorrect pitch identities and/or metrical placement.
5. Measure coverage remains fixed at 1.0.

Never derive song-specific correction rules from scorer labels/events.

## Current bug work — timing/bar phase

Important code observation:
- current `v143_reference_free_timing.py` estimates 4/4 phase only from beat accent contrast (`onset + 0.25*low_energy`).
- approved-audio bar confidence was only about `0.08797`, so the chosen `downbeatIndexMod4=1` / `firstBeatInMeasure=3` is weakly supported.
- `build_subdivision_grid()` then assigns every attack's measure/step from that phase; a wrong phase shifts essentially the whole tab by 4/8/12 sixteenth steps within measures.
- current beat tracker also begins the grid at the first tracked beat rather than proving whether earlier audio-supported beats exist.

New isolated diagnostic:
- `analyzer/v143_reference_free_bar_phase_consensus.py`
- `analyzer/check_v143_reference_free_bar_phase_consensus.py`
- workflow `.github/workflows/v143-reference-free-bar-phase-consensus.yml`

The new diagnostic scores all four bar phases from independent **audio-only** signals:
- transient accent
- low-band accent
- broad harmonic spectral change
- bass-band spectral change
- first-half/second-half stability

It does not change phase or runtime yet. No scorer/reference tokens or target event counts enter the module. Approved-audio workflow was just launched at this checkpoint.

## Immediate next work

1. Finish approved-audio bar-phase consensus diagnostic and inspect its four phase candidates + first/last tracked beat boundary evidence.
2. If independent audio signals strongly and stably select a phase different from the weak accent-only phase, implement it as a general reference-free shadow only; otherwise do not force a phase change.
3. Add evidence-gated leading/trailing beat recovery only if strong audio transients prove the beat tracker starts/ends late; do not synthesize unsupported boundary slots.
4. In parallel, diagnose remaining pitch identity using only approved-audio internal evidence: cross-view score margins, octave/harmonic-family ambiguity, repeated-pattern stability, and guitar-playability — no human note labels.
5. Accept corrections only after CPU/approved-audio anti-leakage/protected-runtime gates.
6. Any accepted correction => brand-new approved-audio Jimmy analysis/freeze/PDF identity before another professional score.
7. Repeat until >=0.99, zero critical mismatches, fidelity 1.0; then create `Final Rhythm Pipeline`, then Bass, then Lead.
