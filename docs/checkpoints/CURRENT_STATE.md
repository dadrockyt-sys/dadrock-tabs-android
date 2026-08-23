# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-reference musical improvement must remain general/reference-free and requires a brand-new fresh real-audio run/freeze before any professional rescore.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`.

**Rhythm is NOT complete. A real professional holdout was run and failed. No completion claim is authorized.**

## Locked frozen candidate / presentation identity

Exact frozen/current candidate:
- 358 attacks
- 1,017 rendered notes
- 277 polyphonic attacks
- 112 populated measures of source 1–113
- event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- approved fixture `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- final-presentation run `32643978196`, artifact `9494412019`, digest `sha256:5ab309e1c86826cb8b5c6ef9c6e3a8edbad334d99d55c07538475c7b61ba519b`
- frozen/PDF event hashes identical
- PDF-event fidelity exactly `1.0`
- full/preview presentation remains green; no phantom 114 and no one-note-per-measure presentation collapse.

Earlier 358-note monophonic candidate is historical only and must not be scored.

## Professional scorer-only source

Immutable professional source:
- `main/public/Professionalexample.jpg` at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`
- recovery run `32624327056`, artifact `9489261810`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- JPEG 2160×3840, 979,815 bytes
- title `Are You Gonna Go My Way`, artist `Lenny Kravitz`, tempo 129
- 3×3 / nine-panel source; panels 1–8 contain complete notation and panel 9 is redundant overlap
- source remains scorer-only and must never become a runtime/tuning feature.

Current session local recovery:
- source artifact `/mnt/data/professional-source.zip`
- extracted under `/mnt/data/rhythm_scorer_source/`
- frozen artifact `/mnt/data/rhythm-preholdout.zip`
- exact freeze `/mnt/data/rhythm_preholdout/.preholdout/freeze`

## Complete temporary structured human reference — BUILT AND COMPLETENESS-PASSED

A scorer-only measures 1–113 structured reference was built locally at:
`/mnt/data/scorer_workspace/validation/rhythm_holdout/reference/professional-rhythm-complete.json`

It is temporary and **must not be committed**.

Reference byte SHA256:
`4d3e7ee6b5485c747bc917077b0648747da7f7d7325c8ccce5058fc41090d8cd`

Reference contents:
- contiguous measures 1–113
- 577 playable onset objects
- 925 playable note entries
- 104 measures with playable attacks; intentional continuation/sustain/empty measures remain declared
- uncertain duration/tie/technique/rest labels omitted rather than invented
- dead/muted `X` attacks that cannot be represented as pitched notes were not invented as pitches.

Important corrected source template (standard string indices `0=high E, 1=B, 2=G, 3=D, 4=A, 5=low E`):

Primary E riff steps `[0,3,4,6,8,10,14]`:
- step0 G-string fret2
- step3 G-string fret0
- step4 D-string fret2
- step6 low-E fret0
- step8 D-string fret0
- step10 D-string fret2
- step14 low-E fret0

Intro/even variation uses the same first six attacks but replaces the final low-E attack with high-E+B `3/3` double-stop at step14.

G-shifted riff uses the same string pattern/steps with frets:
G5, G3, D5, low-E3, D3, D5, low-E3.

High-confidence chorus voicings/timing:
- G6 = high-E0, B3, G4, D5
- A(tp2) = high-E2, B2, G2, D2, A0
- chorus E/D/G four-note stacks occupy B/G/D/A strings at fret 9/7/12
- repeated G6/A figures use `[0,3,4]`
- E/D/E and E/G/E figures use `[0,1,2,3,4,6]`.

Other transcribed source structure:
- m1–16 Intro: odd primary E; even 3/3 variation
- m17–24 primary E
- m25–27 G-shifted
- m28 pitched fill on G string among dead notes
- m29–32 primary E
- m33–38 Chorus 1
- m39–46 alternating primary/3-3 return riff
- m47–54 primary E
- m55–57 G-shifted
- m58 pitched G-string fill among dead notes
- m59–62 primary E
- m63–69 Chorus 2
- m70–94 Bridge, including x7999x / x5777x bridge voicings, B/G/D A/D/E triads, and low-E 4-5-6 pickup in m94
- m95–102 primary E with no 3/3 endings
- m103–113 Out-Chorus including sustained G6/A figures, E/D/E, E/G/E, long A sustain, and final muted ending.

Completeness verifier was run against exact frozen `a089...` candidate and **PASSED**:
- contiguousMeasureCoverage true
- measureCount 113
- playableNoteCount 925
- duplicateOnsets 0
- duplicateNotes 0
- pitchPositionConsistency true
- source SHA bound correctly
- reference opened only after freeze validation
- frozen/PDF SHA identical `a089...`
- PDF-event fidelity 1.0
- runtime labels not required
- V143 runtime safety verified.

## REAL mandatory professional holdout — RUN AND FAILED

`run_final_holdout_gate.py --minimum 0.99` was run locally against the exact frozen `a089...` stream and the completeness-passed temporary human reference.

Gate return code: `2` (failed, as expected from the visible error classes).

Professional score:
- generated notes: `1017`
- reference notes: `925`
- `pitchContentF1 = 0.2626158599382081`
- `pitchTimingTolerantF1 = 0.07209062821833163`
- `stringFretTimingTolerantF1 = 0.030895983522142123`
- `chordPitchSetTolerantF1 = 0.0`
- `exactVoicingTolerantF1 = 0.0`
- `measureCoverageRecall = 0.9911504424778761`
- `pdfEventFidelity = 1.0`
- `criticalMismatchCount = 1653`
  - gross unmatched generated notes `872`
  - gross unmatched reference notes `780`
  - missing reference measures `1`
- missing generated measure is **101**.

Final gate failed checks:
- `professionalScorePassed`
- `near100ProfessionalGatePassed`
- `zeroCriticalMismatches`

PDF identity/safety checks stayed green. Production modified false. Production promotion remains unauthorized.

Local score outputs:
- `/mnt/data/scorer_workspace/final-holdout/rhythm-reference-completeness.json`
- `/mnt/data/scorer_workspace/final-holdout/rhythm-professional-holdout-score.json`
- `/mnt/data/scorer_workspace/final-holdout/rhythm-final-holdout-gate.json`

## Failure diagnosis — GENERAL CLASSES ONLY

The real holdout confirms the pre-existing broad reference-free diagnosis:

1. **Attack under-selection / whole-measure loss**
   - wide candidate count 1,788; frozen global `q=0.2` retains only 358 attacks
   - one whole source measure is absent: m101
   - global selection can discard quieter valid measures.

2. **Polyphony / harmonic inflation**
   - candidate has 1,017 notes against 925 professional reference notes despite only 358 retained attacks
   - 277/358 retained attacks are polyphonic; 58 attacks contain 5–6 notes
   - chord pitch-set and exact-voicing F1 are both 0, proving simultaneous-note expansion is not musically controlled enough.

3. **Pitch/position/timing mismatch remains severe**
   - pitch-content F1 only ~0.263
   - timing F1 ~0.072
   - string/fret timing F1 ~0.031.

Professional source/score may only be used to name/quantify these general classes. It must not become a song-specific runtime rule.

## Isolated contextual-prune shadow safety

Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain byte-for-byte blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`.

Restore commit:
- `4ff233346b8dc7b80d8f4316fe1317338b5be718`

Static shadow safety proof:
- `7af7b81f7b08f14563b1586d8da2c31ffab855ed`
- historical carrier constants / four wide-recall sweeps / whole-onset CQT windows preserved
- Section-5 label-free replay prepared
- frozen contextual model fingerprint matches
- isolated shadow app has no HTTP endpoint
- protected live V143 blobs unchanged
- professional reference absent from shadow runtime sources
- Production modified false.

Any next musical experiment must remain only in isolated shadow modules until independently validated.

## Immediate next steps

1. Inspect the existing isolated contextual-prune shadow modules and raw reference-free evidence for this exact approved-audio run.
2. Validate a **general/reference-free** shadow correction for the two confirmed classes:
   - per-measure/additive attack rescue using strict two-stem precision evidence rather than global quantile alone
   - suppress unsupported secondary chord tones using local carrier/CQT/stem agreement rather than song-specific chord rules.
3. Run static/CPU anti-leakage and protected-blob checks before any GPU experiment.
4. Do **not** rescore this same frozen candidate after tuning. If a general correction is accepted for product integration, produce a brand-new approved-audio run/freeze/PDF identity first, then run the professional scorer only afterward.
5. Require >=0.99, zero critical mismatches, fidelity 1.0 before Rhythm completion.
6. Only after passing: verify `/ai-tab` E2E and create `Final Rhythm Pipeline`; then resume Bass, then Lead.
