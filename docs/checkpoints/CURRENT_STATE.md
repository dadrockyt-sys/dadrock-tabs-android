# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 21:35 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`.
Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, corrections must remain general/reference-free. After accepting any correction, create a BRAND-NEW approved-audio run/freeze/PDF identity before another professional score.

Completion requires:
- professional score >= `0.99`
- critical mismatches = `0`
- PDF-event fidelity = `1.0`

**Rhythm is NOT complete. No completion claim has been made.**

## Protected runtime / fixture

Protected runtime:
- `analyzer/v143_reference_free_rhythm_pipeline.py`
- exact Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`

Approved fixture:
- `public/gomywayfullaitest.m4a`
- SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current gates: protected blob exact; Production unchanged.

## Scorer-only human source

Immutable human-written source:
- `Professionalexample.jpg` SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured-source artifact `9502117311`
- artifact SHA256 `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- `rhythm-track.json` SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`

Deterministic scorer reference V2:
- SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- 113 measures / 603 playable onsets / 946 playable notes / 104 populated measures
- completeness passes
- payload never committed

Historical manual temp JSON `4d3e7ee...` was not preserved. Never claim byte identity with V2.

## Retired scored freezes — NEVER RESCORE AFTER TUNING

Freeze 1 corrected candidate:
- artifact `9499229323`
- event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- 979 attacks / 2,009 notes / 113 measures / fidelity 1.0
- score FAILED: pitch `0.2463621`, timing `0.0710660`, string/fret `0.0263959`, chord/voicing `0.00252845`, critical `2541`.

Freeze 2 precision candidate:
- pre-holdout run `32680719988`
- artifact ID `9504147164`, artifact SHA `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`
- event/PDF-event SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`
- 714 attacks / 967 notes / 113 measures / fidelity 1.0
- professional score run `32681394580` FAILED:
  - pitchContentF1 `0.26241505488761113`
  - pitchTimingTolerantF1 `0.052273915316257184`
  - stringFretTimingTolerantF1 `0.028227914270778882`
  - chordPitchSetTolerantF1 `0.007593014426727412`
  - exactVoicingTolerantF1 `0.007593014426727412`
  - coverage `1.0`, fidelity `1.0`
  - critical mismatches `1649` = generated unmatched `835` + reference unmatched `814`.

Broad/general conclusion only: count inflation is largely fixed; remaining dominant classes are pitch identity and timing/grid identity. Never derive song-specific runtime rules from scorer events.

## BUG 1 — selected lower fundamental lost in voicing adapter — FIXED / PROVED

Problem:
- precision shadow chose a lower harmonic-family primary/fundamental correctly;
- downstream candidate adapter passed only the pitch set and re-ranked it, sometimes restoring the stronger overtone instead of the selected primary.

General/reference-free fix:
- `PrecisionShadowResult` carries explicit `primary_midis` for every retained attack;
- precision candidate adapter preserves explicit primary through legal voicing;
- no scorer/reference data, song labels, or target counts enter.

Proof:
- `debug/v143-contextual-prune/precision-shadow-cpu-proof.json` schema v2 GREEN
- trigger `05874926efa83e162c2471399618cce0bf19cd1c`
- `explicitPrimaryPreserved: true`
- `primaryPropagationCheckerPassed: true`
- no invented attack/pitch/relocation; protected exact; Production false.

Latest approved-audio primary-preservation run `32682664616`:
- corrected attacks `982`
- precision retained attacks `711`
- retained pitch hypotheses `962`
- explicit primary count `711/711`, complete true
- fundamental promotions `134`
- all 113 measures, fail-safe `0`
- protected exact; Production false.

## BUG 2 — beat tracker sub-beat duplicates + premature tail stop — REPAIR SHADOW GREEN

Root issue in original timing:
- tempo `129.19921875`
- original beat count `447`
- `38` interval outliers, including sub-beat duplicate intervals
- tracker stopped before physically active tail audio.

General/reference-free repair files:
- `analyzer/v143_reference_free_beat_grid_repair.py`
- `analyzer/check_v143_reference_free_beat_grid_repair.py`
- `.github/workflows/v143-reference-free-beat-grid-repair.yml`

Repair rule:
- preserve tempo and existing 4/4 phase;
- anchor to long stable pulse run;
- one pulse per beat;
- snap to nearby full-mix transient evidence;
- interior weak beats may use metrical continuity;
- new boundary extension stays inside active audio;
- weak boundary beats may bridge for at most ONE 4/4 bar only when a later pulse within that bar has independent transient/RMS evidence;
- no target measure count, song identity, or scorer data enter.

Why one-bar lookahead was justified from audio only:
- previous repair stopped at `207.238095s`;
- next three predicted beats were weak but still inside active audio;
- fourth predicted beat at `209.095692s` had very strong physical evidence: accent `1.64477`, local RMS `0.24525`;
- after it, predicted beats are outside active-audio bound and rapidly decay toward silence.

Latest approved-audio repair run `32683424669` GREEN:
- original `447` beats → repaired `449`
- interval outliers `38 → 0`
- repaired first beat `0.6965986395s`
- repaired last beat `209.0956916100s`
- active audio end `209.1231746032s`
- lookahead bridge count `3`
- repaired grid = **113 measures**
- repaired slot count `1796`
- next predicted beat `209.560091s` is outside active-audio bound and unsupported; repair stops cleanly
- protected exact; Production false.

**Beat-grid pulse repair itself is now internally green.**

## Bar phase — DO NOT CHANGE YET

Original phase: `downbeatIndexMod4=1`, `firstBeatInMeasure=3`, low bar confidence ~`0.08797`.
After the repaired pulse grid, multi-signal consensus winner is phase `2`, but:
- confidence only ~`0.1978`
- independent signal winners disagree
- `stableAcrossHalves=false`

Therefore there is NOT enough general audio evidence to force a phase rotation. Keep existing phase unchanged unless stronger/stable independent evidence appears later.

## CURRENT ACTIVE BUG — precision run-to-run determinism

Observed drift on the same approved fixture:
- earlier precision run: `714` retained attacks / `968` pitch hypotheses / `136` promotions
- latest primary-preservation rerun: `711` / `962` / `134`

This may indicate nondeterminism upstream (separator, Basic Pitch/carrier, aggregation, etc.). Do not ignore it.

New diagnostic added:
- `analyzer/v143_contextual_prune_precision_shadow_modal.py` now emits exact stage hashes:
  - source bytes
  - normalized WAV
  - direct/cascade deterministic guitar stems
  - timing/carrier grid
  - carrier rows
  - base events
  - corrected events/pitches
  - precision events/pitches/explicit primaries
- workflow `.github/workflows/v143-precision-determinism-proof.yml`
- diagnostic runs **two complete approved-audio passes** and reports the FIRST stage whose hash differs.

Current determinism Actions run:
- run ID `32683174815`
- anti-leakage/protected-runtime gate GREEN
- two complete Modal passes are still running at this checkpoint.

## Current work NOW

1. Finish run `32683174815` and inspect `debug/v143-contextual-prune/precision-determinism-proof.json`.
2. If normalized audio/stems are exact but carrier rows diverge, isolate Basic Pitch/inference determinism and force a general deterministic inference boundary (likely CPU or deterministic TensorFlow ops) before accepting any new freeze.
3. If divergence begins earlier, repair the earliest differing stage instead.
4. Re-run two-pass stage-hash proof until all accepted stages are exact/reproducible or any unavoidable numerical tolerance is explicitly demonstrated not to change event identity.
5. Then run the **repaired timing grid + explicit-primary precision path together** on approved audio with anti-leakage/protected-runtime gates.
6. Re-evaluate phase only as a diagnostic; keep current phase unless stable independent audio evidence supports changing it.

## Next steps after determinism is green

1. Accept the combined general/reference-free correction only after its CPU + approved-audio proofs are green.
2. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
3. Verify all event/PDF identity hashes, PDF-event fidelity `1.0`, protected blob exact, Production unchanged.
4. ONLY THEN reopen scorer-only human reference V2 and run unchanged professional threshold `>=0.99`.
5. If it fails, report exact metrics but use them only as broad failure classes; any further correction remains general/reference-free and requires another fresh freeze before scoring.
6. Continue until >=`0.99`, zero critical mismatches, fidelity `1.0`.
7. Then create `Final Rhythm Pipeline`; only afterward resume Bass, then Lead.
