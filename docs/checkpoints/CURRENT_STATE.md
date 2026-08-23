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

## Green CPU gates

- Static preflight: schema 7 / green / PDF-event fidelity 1.0.
- Professional holdout self-test: schema 6 / green.
- Dedicated reference-free polyphony CPU proof: green, latest observed run `32641304362`, source commit `f015715a291ff3f9c2a9da9f633f1b5bef63352a`.
- Runtime isolation, product PDF routing, branding, reference anti-leakage, hard failures, and exact PDF-event fidelity are green.
- Polished final-render CPU presentation proof: schema 2 / green after section/tempo/phantom-measure fixes.
- Real frozen-stream presentation diagnostic: green on the exact 1,017-note candidate.
- Current-renderer execution diagnostic: green, including exact event fidelity and extracted PDF text checks.
- Final current-renderer relock V3: schema 3 / green.

## Professional scorer source recovery

The immutable professional source was recovered scorer-side only after an earlier fresh reference-free freeze was green.

Recovery proof:
- source: `main/public/Professionalexample.jpg` at immutable commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`
- Actions run `32624327056`
- scorer-only artifact ID `9489261810`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- JPEG RGB 2160×3840, 979,815 bytes
- 3×3 / nine-panel complete professional source covering measures 1–113
- clean Library screenshot `1000116180.jpg` independently matches the recovered Chorus around measures 33–35
- `validation/rhythm_holdout/reference/reference-inventory.json` records complete source availability.

The professional source remains **scorer-only**. It may now be opened/transcribed/scored against the final relocked candidate below, but must never feed runtime or runtime tuning.

### Corrected scorer-only PDF source — LOCKED LOCALLY

A scorer-only eight-page PDF was constructed from the immutable professional source without changing notation:
- `/mnt/data/rhythm_scorer_source/Professionalexample-scorer-source-v2.pdf`
- pageCount **8**, using source panels 1–8; panel 9 excluded as redundant overlap
- PDF SHA256 `c356ebcbfd6d435f96a84ff8960c55c35cc2d388b617b7d62212bbcc485d38ef`
- PDF bytes 2,731,718
- source composite remains SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- manifest `/mnt/data/rhythm_scorer_source/Professionalexample-scorer-source-v2.manifest.json`
- manifest SHA256 `724f1edd4236920ab8e1e9a5b4aed11807947cf0ff3829bbeb4c0e6216c4a13e`
- scorerOnly true; runtimeAccessAllowed false; referenceModified false
- rendered page inspection completed on all eight pages.

Do not commit the professional PDF, source image, or complete event-level human reference. They remain temporary scorer-side inputs only.

## Reference-free polyphonic mapper — implemented and proven

General/reference-free musical correction:
- `cc56e64589fcc9bae3032b55133e8b73ba5fd956` — polyphonic Rhythm note mapping from the detector's existing same-attack `pitchHypotheses`; deterministic six-string voicing; dominant MIDI retained; no professional reference/runtime labels.
- `c235a1535138f86ea44c4bbcb8334500c45cba7b` — assembly semantics hardened so `selectedCount` is rhythmic attacks and rendered note count may be larger; all rendered MIDIs must trace to hypotheses; unique `(measure, step, stringIndex)` required.
- `e6820f0782eba3d79854b9a140851ffc1d99afb0` — CPU verifier.
- `f015715a291ff3f9c2a9da9f633f1b5bef63352a` — CPU workflow.

Downstream product contracts were checked: output adapter, Jimmy PAIge payload, analyze route, render contract, and professional PDF renderer support multiple same-onset notes on unique strings and do not require `selectedCount == noteCount`.

## Fresh post-polyphony approved-audio stream — GREEN AND IMMUTABLY BOUND

Fresh approved-audio run:
- run `32642331373`, source commit `580550c7cfa6d7a2204aac70052c4c5ab88aa130`
- approved fixture `public/gomywayfullaitest.m4a`
- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- source bytes 3,478,611
- runtime safety all correct: reference-free true; professional/runtime reference inputs false; runtime labels false; V143 safety verified true
- live endpoint unchanged; Production unchanged; promotion unauthorized; human reference sealed during freeze.

Structured output:
- selected rhythmic attacks: **358**
- rendered note events: **1,017**
- distinct attack locations: 358
- polyphonic attacks: 277
- single-note attacks: 81
- notes/attack distribution: 1→81, 2→100, 3→64, 4→55, 5→24, 6→34
- max chord size 6
- all 1,017 events use noteMapping v2
- every rendered MIDI traces to the frozen pitch hypotheses; dominant MIDI preserved
- unique `(measure, step, stringIndex)` occupancy true
- measure range 1–113, 112 populated measures
- frozen event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`.

Original post-polyphony artifact lock remains historical source proof:
- artifact ID `9493999904`
- digest `sha256:bdd8a7617455e571b2dbeaaeb83ad5c40310e6581e21dde0e5bcb51e28684223`
- lock commit `c6762427c28b0aebaaae454f12931aee313674cc`.

A later final-presentation fresh run `32643978196` used the same exact authenticated event hash `a089...`, 1,017 notes, and PDF fidelity 1.0. Its artifact is `9494412019`, digest `sha256:5ab309e1c86826cb8b5c6ef9c6e3a8edbad334d99d55c07538475c7b61ba519b`. This exact immutable frozen stream is now the source stream used by the CPU-only final renderer relock.

The earlier 358-note monophonic run `32623173615` is historical only and must never be professionally scored as the current candidate.

## Final-render presentation — GREEN AND RELOCKED

User specifically flagged the prior E2E failure where V143 effectively displayed only one note per measure and asked that final Rhythm rendering preserve timing, techniques, and section display.

Presentation code now includes, without changing authenticated note placement:
- 16th-note timing grid and beat guides
- section labels derived only from reference-free event change points
- technique legend and visible bend/release, hammer-on, pull-off, slide and sustain notation
- fail-closed one-note-per-measure collapse guard
- clean integer tempo display
- no phantom measure labels beyond the actual final measure.

Key commits:
- `c776722069ec7859278309fc8ef1f2d9ecde8005` initial reference-free presentation summary/collapse guard
- `6099f818c8ee3828e1a7908f85a29ff1506942a5` initial timing/technique/section renderer display
- `838f3c02e02733cef9ad620826d0efa66da25456` section logic changed to reference-free change-point segmentation with sensible 8–16-measure spans
- `2116c7ac38233eecce39d5187b1d9a044811b82f` rounded tempo, improved timing grid, removed phantom final measures
- `24c407b7bbd477a10b6815afec159115197d6467` polished CPU presentation proof
- Actions proof commit `920d4b52caeb407f11a8157fd760a0568779fab9`.

Real frozen-stream section diagnostic (`debug/v143-contextual-prune/rhythm-relock-presentation-diagnostic.json`) is green:
- 1,017 events / 358 onsets / 112 populated measures
- average 9.08 notes/populated measure
- 277 multi-note onsets; max chord size 6
- 82 technique events; bend, bend-release, hammer-on, pull-off, slide-down, slide-up
- eight reference-free sections: 1–16, 17–32, 33–40, 41–56, 57–72, 73–88, 89–104, 105–113
- no one-note-per-measure collapse.

Current renderer execution diagnostic (`debug/v143-contextual-prune/rhythm-relock-render-diagnostic.json`) is green:
- render succeeds on exact locked 1,017-event stream
- PDF-event fidelity 1.0, frozen/PDF hash both `a089...`
- full PDF 4 pages; preview 4 pages
- extracted-text checks all green: timing legend, `129 BPM`, no unrounded tempo, eight section labels, hammer-on/pull-off/slide/bend labels, measure 113 present, measure 114 absent, preview lock/timing/sections present.

Final observable CPU relock:
- workflow commit `e52beadfad35156d541ea0cd4d5bd75e8fd0c446`
- proof commit `11a2fc02e4f8943c5de2ba89108b3f61f84c8f2b`
- proof `debug/v143-contextual-prune/rhythm-final-render-relock-v3.json`, schema 3, `passed:true`, no failed checks
- exact event count 1,017
- frozen/PDF event SHA both `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF-event fidelity **1.0**
- full final-render PDF: 1,730,922 bytes / 4 pages / SHA256 `5ea3ed1f382268d649dd54fcda9b3154ff81e2cc0712ddbbd7ae7aa593ed6cad`
- preview final-render PDF: 1,705,648 bytes / 4 pages / SHA256 `bb5ce7da9783527b8dd4055adfbace3ab7d8d461153531ee553e7fa14348c99e`
- eight section labels, correct song end at measure 113, no phantom 114
- timing/technique/preview presentation checks all true
- professional reference not opened by renderer relock
- Production unchanged.

Because the changes after run `32643978196` are presentation-only and the V3 relock proves the current renderer consumes the exact immutable frozen stream with fidelity 1.0, another GPU analyzer run is not required merely to re-engrave the unchanged authenticated events.

## Scorer phase — NOW READY

The musical event stream and current final renderer are both locked and green. Professional scorer work can proceed against the exact `a089...` candidate. The recovered professional human source remains scorer-only.

No valid final professional score has yet been declared.

### Current source-transcription progress

The complete 8-page professional notation has been visually mapped through measures 1–113. High-confidence structural templates now include:
- primary E riff: 16th-grid attack steps `[0,3,4,6,8,10,14]`; fret/string identities resolved
- intro/even-bar E-riff variation: same first six attacks, final step 14 is the high-string 3/3 double-stop
- G-shifted riff: same grid `[0,3,4,6,8,10,14]`; transposed fret/string identities resolved
- G6 and A(tp2) chorus voicings and repeated attacks resolved
- chorus E/D/E and E/G/E chord figures resolved to attack steps `[0,1,2,3,4,6]`
- Bridge and Out-Chorus source regions enlarged for final event extraction.

Uncertain duration/tie/technique/rest annotations will be omitted from the scorer JSON rather than invented; every playable attack/note/voicing required by the source must still be transcribed.

## Jimmy failure diagnosis — GENERAL CLASSES ONLY

The current `a089...` candidate exposes two broad reference-free error classes that will be tested in isolated shadow code before any protected/live integration:

1. **Attack under-selection / whole-measure loss**
   - candidateCount 1,788 but frozen V143 global `q=0.2` retains 358 attacks
   - selection is global rather than per-measure, so quieter valid measures can disappear
   - current candidate populates only 112 of source measures 1–113.

2. **Polyphony / harmonic inflation**
   - the low-threshold wide-recall Basic Pitch pass often exposes roughly two dozen pitch hypotheses at one attack
   - current mapper expands many into simultaneous notes
   - 277/358 attacks are polyphonic, including 58 attacks with 5–6 notes, far above plausible chord density outside chord sections.

These findings are diagnostics only. Professional source information must not become runtime features or song-specific rules.

## Isolated contextual-prune shadow — PROTECTED LIVE FILES RESTORED / STATIC GREEN

An attempted direct prototype touched protected `analyzer/v143_reference_free_rhythm_pipeline.py`; it was immediately reverted before any GPU/product run. The protected file is restored byte-for-byte to blob:
`7f72f8ed9b14af8bc93e95544195204d99c6bec1`.

Restore commit:
- `4ff233346b8dc7b80d8f4316fe1317338b5be718` — `Restore protected V143 pipeline before shadow testing`

Static shadow safety gate then passed and recorded:
- `7af7b81f7b08f14563b1586d8da2c31ffab855ed` — `Record V143 contextual prune shadow static gate`
- carrier constants match historical research
- all four historical wide-recall sweeps required
- whole-onset CQT windows match research
- Section-5 label-free replay is prepared
- frozen contextual model fingerprint matches
- isolated shadow app has no HTTP endpoint
- all protected live V143 blobs unchanged
- professional reference path absent from shadow runtime sources
- Production modified false.

Any next musical experiment must remain only in isolated shadow modules until independently validated. Do not modify protected live/runtime files merely to test a hypothesis.

## Immediate next steps

1. Finish the temporary scorer-only complete structured professional reference for measures 1–113 from immutable `Professionalexample.jpg` / corrected 8-page scorer PDF; do not invent unreadable events and do not use generated DadRock PDFs as ground truth.
2. Run `verify_reference_completeness.py` and mandatory `run_final_holdout_gate.py` against the exact relocked/frozen `a089...` candidate.
3. Require professional score >=0.99, `criticalMismatchCount == 0`, and PDF-event fidelity 1.0 before declaring Rhythm complete.
4. If the score misses, use professional results only to diagnose general error classes.
5. Develop the next correction only in isolated contextual-prune shadow code: evaluate strict two-stem precision evidence for additive attack rescue and for suppressing unsupported secondary chord tones. Keep professional reference out of runtime entirely.
6. Run CPU/static anti-leakage gates before any isolated shadow GPU experiment. If a general correction is eventually integrated into the product pipeline, create a brand-new approved-audio freeze before any professional rescore.
7. Once the real professional gate passes, verify DadRock `/ai-tab` user E2E — specifically multiple notes/chords per measure, timing grid, techniques, sections, preview/full identity, and no one-note-per-measure collapse — then create `Final Rhythm Pipeline`.
