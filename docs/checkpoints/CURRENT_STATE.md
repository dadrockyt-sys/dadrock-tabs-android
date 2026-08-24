# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken scoring thresholds.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Professional human reference is scorer-only. Runtime may never read/train/tune/select from it. After a holdout failure, musical corrections must remain general/reference-free. After accepting any correction, create a **brand-new approved-audio run/freeze/PDF identity before another professional score**.

Rhythm completion requires professional score >= `0.99`, critical mismatches = `0`, PDF-event fidelity = `1.0`.

**Rhythm is NOT complete.**

## Protected runtime / approved fixture

Protected runtime file:
- `analyzer/v143_reference_free_rhythm_pipeline.py`
- required Git blob: `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit: `4ff233346b8dc7b80d8f4316fe1317338b5be718`

Approved fixture:
- `public/gomywayfullaitest.m4a`
- SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current scorer/shadow diagnostics prove protected pipeline unchanged and Production modified false.

## Historical scored freeze — never rescore

Old freeze:
- 358 attacks / 1,017 rendered notes
- 112 populated measures; missing m101
- event SHA `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF fidelity 1.0

Old temporary manually structured scorer reference:
- SHA256 `4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`
- 113 contiguous measures
- 577 playable onset objects
- 925 playable note entries
- 104 populated measures
- exact bytes were temporary and were not preserved/committed.

Old holdout failed:
- pitchContentF1 `0.2626158599382081`
- pitchTimingTolerantF1 `0.07209062821833163`
- stringFretTimingTolerantF1 `0.030895983522142123`
- chordPitchSetTolerantF1 `0.0`
- exactVoicingTolerantF1 `0.0`
- measureCoverageRecall `0.9911504424778761`
- PDF fidelity `1.0`
- critical mismatches `1653`

## Corrected candidate / first fresh corrected professional freeze

Reference-free correction path already green before scoring:
- boundary-grid correction
- strict physical attack rescue
- unsupported pitch suppression
- semantic primary-note guard
- two-view sustain consensus
- corrected candidate event adapter
- isolated corrected candidate → Jimmy structured product/PDF path

Fresh corrected freeze artifact:
- Actions run `32662674725`
- artifact ID `9499229323`
- artifact SHA256 `980070d12011c3c6724d9d7c26da3b2158b0161d6ed54c561454ab254ba1706a`
- 979 corrected attacks
- 2,009 rendered authenticated notes
- 2,055 physically supported pitches before legal voicing
- 46 voicing-only drops
- all 113 measures populated
- event SHA256 `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- frozen/PDF event SHA identical
- PDF-event fidelity `1.0`
- full/preview PDF green
- reference not opened during freeze
- protected/live pipeline unchanged; Production unchanged.

This freeze is now scored and must never be rescored after tuning.

## Professional human source / reproducible scorer reference V2

Immutable professional source:
- `Professionalexample.jpg`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- human-written `Are You Gonna Go My Way`, Rhythm Guitar, revision `7868948` dated 2026-07-12
- complete measures 1–113

Exact scorer-only structured-source artifact:
- artifact ID `9502117311`
- artifact SHA256 `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- `rhythm-track.json` SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- AI-generated flag false; source is human-written.

Because the old 577/925 temporary JSON bytes were not preserved, a deterministic scorer-only reference V2 was generated directly from the exact immutable human-written structured source **only after the corrected freeze/PDF identity gate passed**. It excludes tied continuation notes, dead/muted X notes, and rests as attack pitches; it quantizes human beat positions to the fixed 16-step scorer grid and merges same-step duplicate notes.

Reference V2:
- SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- 113 contiguous measures
- 603 playable onset objects
- 946 playable note entries
- 104 populated measures
- completeness verifier passed
- reference payload was never committed
- runtime/reference inputs remained false.

Score diagnostic:
- `debug/v143-contextual-prune/corrected-candidate-professional-score.json`
- Actions run `32679830055`

## Corrected candidate professional score — FAILED

Scored exact corrected freeze `c621ab...` against deterministic scorer-only human source V2 at unchanged minimum `0.99`.

Results:
- generated notes: `2009`
- reference notes: `946`
- pitchContentF1: `0.2463620981387479`
- pitchTimingTolerantF1: `0.07106598984771574`
- stringFretTimingTolerantF1: `0.026395939086294416`
- chordPitchSetTolerantF1: `0.0025284450063211127`
- exactVoicingTolerantF1: `0.0025284450063211127`
- measureCoverageRecall: `1.0`
- PDF-event fidelity: `1.0`
- criticalMismatchCount: `2541`
  - gross unmatched generated notes: `1802`
  - gross unmatched reference notes: `739`
  - missing reference measures: none
- near100ProfessionalGatePassed: false
- rhythmComplete: false
- scorer return code: `2`

Safety stayed green:
- professionalReferenceUsedByAnalyzer false
- referenceRuntimeInputUsed false
- runtimeLabelsRequired false
- protected pipeline exact
- Production modified false
- reference payload not committed.

## Allowed failure diagnosis — GENERAL CLASSES ONLY

Use the score only to quantify broad failure classes, never to derive song-specific runtime rules.

Confirmed general classes on the corrected candidate:

1. **Attack over-selection**
   - corrected candidate has 979 attack locations and complete coverage; rescue/retention is too permissive.
2. **Polyphony / harmonic inflation remains severe**
   - 2,009 generated notes from 979 attacks; chord pitch-set and exact voicing effectively zero.
3. **Pitch/position/timing mismatch remains severe**
   - pitch content ~0.246; tolerant timing ~0.071; string/fret timing ~0.026.
4. **Measure coverage is fixed**
   - all source measures covered; no missing reference measures.

## New isolated general/reference-free precision shadow

Implemented after the failed corrected-candidate holdout, without reopening/using the human reference in runtime:
- `analyzer/v143_contextual_prune_precision_shadow.py`
- creation commit `818a6409f39a7efec5a286636e8b806e31277a0e`
- `analyzer/check_v143_contextual_prune_precision_shadow.py`
- creation commit `edcf00b67d92080c05f8c1cf516871c9138100a6`
- CPU gate workflow `.github/workflows/v143-contextual-prune-precision-shadow.yml`
- CPU proof workflow `.github/workflows/v143-contextual-prune-precision-shadow-proof.yml`
- CPU proof diagnostic `debug/v143-contextual-prune/precision-shadow-cpu-proof.json`

CPU proof is GREEN:
- checkerPassed true
- no unobserved attacks
- no relocated attacks
- no unobserved pitches
- referenceFree true
- protected pipeline blob exact `7f72f8...`
- Production unchanged.

General rule only:
- an attack must have substantial two-view transient energy relative to its local body (`attack/body >= 0.70`), with a narrow `>=0.60` local-prominence exception;
- if pruning would erase a whole measure, retain only the strongest already-observed physically supported attack as a coverage fail-safe;
- pitches are selected only from the carrier's observed candidate set;
- lower observed fundamentals can be promoted when upper observed candidates form a physically supported harmonic family;
- secondary tones require strong independent physical support, with stricter support for candidates explainable as upper harmonics;
- no key/chord/section/song/reference labels or target event counts enter the rule.

Approved-audio precision shadow runner:
- `analyzer/v143_contextual_prune_precision_shadow_modal.py`
- workflow `.github/workflows/v143-contextual-prune-precision-shadow-approved-audio.yml`
- current Actions run `32680288667`
- preflight anti-leakage/protected-runtime step GREEN
- Modal approved-audio precision shadow currently running at this checkpoint.

Do not accept/integrate this precision correction until its approved-audio internal invariants and coverage/pitch-support diagnostics are reviewed. Do not score any shadow output. If accepted, a brand-new approved-audio Jimmy freeze/PDF must be created before scorer access.

## Immediate next work

1. Finish run `32680288667`; inspect `debug/v143-contextual-prune/precision-shadow-approved-audio.json`.
2. Accept only if reference-free invariants hold, all 113 measures remain populated, pruning is physically coherent, and fail-safe use is not pathological.
3. If not acceptable, adjust only on internal physical diagnostics — never on human reference/event counts.
4. Once accepted, adapt the precision result into isolated candidate event assembly without adding/relocating attacks or pitches.
5. Run a **brand-new approved-audio analysis → precision events → Jimmy payload → freeze → full/preview PDF** identity.
6. Only then reopen scorer-only human source and score the new immutable freeze.
7. Repeat only through general/reference-free corrections until >=0.99, 0 critical mismatches, fidelity 1.0.
8. Then create `Final Rhythm Pipeline`; only afterward resume Bass, then Lead.
