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

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

**No completion claim has been made. Rhythm remains incomplete.**

## Locked green product/freeze state

- Static preflight, professional holdout self-test, runtime isolation, product PDF routing, anti-leakage, hard failures, and exact PDF-event fidelity are green.
- Reference-free polyphonic mapper proof remains green (`cc56e645...`, `c235a153...`, verifier `e6820f0...`, workflow `f015715...`).
- Fresh approved-audio run `32642331373` / later final-presentation run `32643978196` use the same exact authenticated event stream.
- Approved fixture: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen structured output: 358 rhythmic attacks, 1,017 rendered note events, 277 polyphonic attacks, 81 single-note attacks, measure range 1–113 with 112 populated measures.
- Frozen event SHA256: `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`.
- Final-presentation artifact: run `32643978196`, artifact `9494412019`, digest `sha256:5ab309e1c86826cb8b5c6ef9c6e3a8edbad334d99d55c07538475c7b61ba519b`.
- Final current-renderer relock V3: 1,017 events, frozen/PDF event SHA identical `a089...`, PDF-event fidelity 1.0, full/preview PDFs green, sections/timing/techniques visible, measure 113 present, no phantom 114, no one-note-per-measure collapse.
- Earlier 358-note monophonic candidate is historical only and must not be scored.

## Professional source — scorer-only

Immutable source:
- `main/public/Professionalexample.jpg` at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`
- recovery run `32624327056`, artifact `9489261810`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- JPEG RGB 2160×3840, 979,815 bytes, 3×3 / nine-panel complete source covering measures 1–113
- source remains scorer-only; never commit the complete event-level professional reference or feed it to runtime.

### Local recovery in current work session

The immutable Actions source artifact has been re-downloaded locally to `/mnt/data/professional-source.zip` and extracted under `/mnt/data/rhythm_scorer_source/`.

Recovered:
- `Professionalexample.jpg` (979,815 bytes)
- source panels 1–9 split locally for visual transcription
- panel 9 confirmed redundant overlap; panels 1–8 contain the complete notation source.

The exact frozen candidate artifact `9494412019` has also been re-downloaded locally to `/mnt/data/rhythm-preholdout.zip` and extracted under `/mnt/data/rhythm_preholdout/`.

Exact freeze directory:
`/mnt/data/rhythm_preholdout/.preholdout/freeze`

It contains the exact `rhythm-frozen-analysis.json` / `rhythm-freeze-manifest.json` bound to `a089...` and PDF fidelity 1.0.

## Professional structured reference — IN PROGRESS, TEMPORARY ONLY

The complete scorer-only reference must remain temporary under a local `validation/rhythm_holdout/reference` path and must **not** be committed.

Validator/scorer contracts checked on this branch:
- `verify_reference_completeness.py` requires complete contiguous measures, source provenance/hash, valid string/fret/MIDI identities, and validates freeze/PDF identity before opening the reference.
- `run_final_holdout_gate.py` runs completeness first, locks exact reference bytes, then runs the scorer with minimum 0.99.
- `score_rhythm_holdout.py` gates pitch content, timing, string/fret timing, chord pitch set, exact voicing, measure coverage, PDF fidelity, and optional duration/technique/tie/rest metrics only when those labels are present.
- Critical mismatch count includes missing reference measures plus gross unmatched reference/generated notes using same-measure/same-MIDI matching within ±2 steps.

Uncertain duration/tie/technique/rest annotations will be omitted rather than invented. Every readable playable attack/note/voicing must still be transcribed.

### High-confidence source templates currently resolved

Standard string indices: `0=high E`, `1=B`, `2=G`, `3=D`, `4=A`, `5=low E`.

Primary E riff, attack steps `[0,3,4,6,8,10,14]`:
- step0 D-string fret2
- step3 D-string fret0
- step4 A-string fret2
- step6 low-E fret0
- step8 A-string fret0
- step10 A-string fret2
- step14 low-E fret0

Intro/even-bar E-riff variation:
- same first six attacks
- step14 is high-E + B double-stop, frets `3/3`.

G-shifted riff, same steps `[0,3,4,6,8,10,14]`:
- D5, D3, A5, low-E3, A3, A5, low-E3.

Resolved chorus voicings:
- `G6`: high-E0, B3, G4, D5
- `A(tp2)`: high-E2, B2, G2, D2, A0
- high-position `E`: top four strings fret9
- high-position `D`: top four strings fret7
- high-position `G`: top four strings fret12

Resolved chorus timing:
- repeated `G6` / `A(tp2)` three-hit figures use early 16th-grid attacks `[0,3,4]` where visually confirmed.
- E/D/E and E/G/E chord figures use `[0,1,2,3,4,6]`.

### Current measure map

High-confidence structural map:
- m1–16 Intro: odd bars primary E; even bars E variation with final high `3/3` double-stop.
- m17–24 Verse 1: primary E riff.
- m25–27 G-shifted riff.
- m28 muted/single-string fill — pitched identities still being finalized; do not invent unreadable X/dead-note events.
- m29–32 primary E riff.
- m33 G6; m34 A(tp2); m35 E/D/E; m36 E/G/E; m37 G6 plus late A(tp2); m38 tie/sustain continuation only.
- m39–46 return riff alternating primary E / intro-even `3/3` variation.
- m47–54 Verse 2: primary E riff.
- m55–57 G-shifted riff.
- m58 muted/single-string fill — pitched identities still being finalized.
- m59–62 primary E riff.
- m63 G6; m64 A(tp2); m65 E/D/E; m66 E/G/E; m67 G6; m68–69 continuation/space.
- Bridge begins m70 and is currently the main remaining detailed chord/string/timing extraction task.
- m94 contains a visible pitched single-string ascending fill after muted attacks; identities/timing still being finalized.
- m95–102 primary E riff.
- Out-chorus begins m103; m103–113 source has been visually mapped, but exact attack steps for sustained/late chord entries are being finalized before JSON creation.

No complete reference JSON has yet been declared. No professional score has yet been run or declared.

## Current candidate general failure classes — diagnostic only

The exact `a089...` candidate already exposes two broad reference-free classes:

1. **Attack under-selection / whole-measure loss**
   - wide candidateCount 1,788; frozen global `q=0.2` retains 358 attacks
   - selection is global rather than per-measure, so quieter valid measures can disappear
   - current candidate populates 112 of source measures 1–113.

2. **Polyphony / harmonic inflation**
   - low-threshold wide-recall Basic Pitch often yields many simultaneous pitch hypotheses
   - current mapper expands many into simultaneous notes
   - 277/358 attacks are polyphonic; 58 attacks have 5–6 notes.

Professional source results may only diagnose general classes. They must never become song-specific runtime rules/features.

## Isolated contextual-prune shadow — protected live files remain restored

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

1. Finish exact bridge, m28/m58/m94 fills, and out-chorus playable event extraction from the immutable professional source.
2. Build the temporary complete measures 1–113 structured professional reference locally; do not commit it.
3. Run `verify_reference_completeness.py` against the exact `a089...` freeze.
4. Run mandatory `run_final_holdout_gate.py --minimum 0.99` against the same exact frozen candidate.
5. Require score >=0.99, `criticalMismatchCount == 0`, and PDF-event fidelity 1.0 before any completion claim.
6. If it fails, use the scorer output only to quantify general error classes.
7. Validate a general/reference-free correction only in isolated contextual-prune shadow code: strict two-stem precision evidence for additive attack rescue and suppression of unsupported secondary chord tones. No professional reference in runtime.
8. Run CPU/static anti-leakage gates before any isolated shadow GPU experiment. If a general correction is later integrated into product code, create a brand-new approved-audio freeze before any new professional rescore.
9. Only after the real gate passes: verify `/ai-tab` E2E multiple-note/chord rendering, timing grid, techniques, sections, preview/full identity, and no collapse; then create `Final Rhythm Pipeline`.
