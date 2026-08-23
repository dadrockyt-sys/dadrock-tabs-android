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

The professional source remains **scorer-only**. It may now be opened/transcribed/scored against the fresh locked candidate below, but must never feed runtime or runtime tuning.

## Reference-free polyphonic mapper — implemented and proven

General/reference-free musical correction:
- `cc56e64589fcc9bae3032b55133e8b73ba5fd956` — polyphonic Rhythm note mapping from the detector's existing same-attack `pitchHypotheses`; deterministic six-string voicing; dominant MIDI retained; no professional reference/runtime labels.
- `c235a1535138f86ea44c4bbcb8334500c45cba7b` — assembly semantics hardened so `selectedCount` is rhythmic attacks and rendered note count may be larger; all rendered MIDIs must trace to hypotheses; unique `(measure, step, stringIndex)` required.
- `e6820f0782eba3d79854b9a140851ffc1d99afb0` — CPU verifier.
- `f015715a291ff3f9c2a9da9f633f1b5bef63352a` — CPU workflow.

Downstream product contracts were checked: output adapter, Jimmy PAIge payload, analyze route, render contract, and professional PDF renderer already support multiple same-onset notes on unique strings and do not require `selectedCount == noteCount`.

## Fresh post-polyphony approved-audio freeze — GREEN AND LOCKED

The viable candidate trigger is commit `580550c7cfa6d7a2204aac70052c4c5ab88aa130` (`Fix pre-GPU ESM rewrite and retrigger Rhythm freeze`). It ran only the isolated product canary and did not deploy/alter live V143 Modal or Production.

Fresh Actions run:
- run `32642331373`, completed `success`
- source commit `580550c7cfa6d7a2204aac70052c4c5ab88aa130`
- approved fixture `public/gomywayfullaitest.m4a`
- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- source bytes 3,478,611
- `referenceFree:true`
- `professionalReferenceUsed:false`
- `referenceRuntimeInputUsed:false`
- `runtimeLabelsRequired:false`
- `v143RuntimeSafetyVerified:true`
- live endpoint unchanged
- Production unchanged
- promotion unauthorized
- human reference remained sealed during freeze

Fresh structured output:
- selected rhythmic attacks: **358**
- rendered guitar-note events: **1,017**
- distinct attack locations: 358
- polyphonic attacks: 277
- single-note attacks: 81
- notes/attack distribution: 1→81, 2→100, 3→64, 4→55, 5→24, 6→34
- median notes/attack: 2.0
- max notes/attack: 6
- all 1,017 events use `noteMapping.version:2`
- all chord voicings jointly resolved
- every rendered MIDI traces to the attack's frozen pitch hypotheses
- dominant MIDI preserved at every attack
- unique `(measure, step, stringIndex)` occupancy: true
- assembly v2 `polyphonicExpansion:true`, `selectionChanged:false`, `attackTimingChanged:false`, `pitchEvidenceChanged:false`
- measure range 1–113, 112 unique measures

Fresh PDF/freeze proof:
- frozen event SHA256 `a089a82996f51bfddc182abdf1e0f07732c135c7c6e7bfd6105b6daf37c1175e`
- PDF event SHA256 identical
- PDF-event fidelity **1.0**
- full PDF 1,704,133 bytes / 4 pages
- preview PDF 1,680,565 bytes / 4 pages
- compact proof `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` passed with no failed checks.

Fresh artifact lock:
- artifact ID `9493999904`
- name `rhythm-professional-preholdout-real-audio`
- artifact digest / ZIP SHA256 `bdd8a7617455e571b2dbeaaeb83ad5c40310e6581e21dde0e5bcb51e28684223`
- permanent lock `debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json`
- lock commit `c6762427c28b0aebaaae454f12931aee313674cc`
- `locked:true`, `passed:true`

Per-file fresh artifact hashes are recorded in the artifact-lock JSON. The earlier 358-note monophonic run `32623173615` is historical only and must not be professionally scored as the current candidate.

## Final-render presentation hardening — IN PROGRESS BEFORE PROFESSIONAL SCORE

User specifically flagged the prior end-to-end failure where V143 effectively displayed only one note per measure and asked that final Rhythm rendering preserve timing, techniques, and section display.

Fresh locked run `32642331373` is **not** collapsed: it contains 1,017 note events across 112 populated measures and 358 distinct attack locations; median populated measure density is 8 notes and 277 attacks are polyphonic.

Presentation hardening now committed on this branch, without professional-reference input and without changing analyzer note selection:
- `c776722069ec7859278309fc8ef1f2d9ecde8005` — extends `lib/v143RenderContract.js` with deterministic reference-free section grouping from authenticated render-event self-similarity, presentation-density metrics, and a one-note-per-measure collapse detector.
- `6099f818c8ee3828e1a7908f85a29ff1506942a5` — hardens `lib/createV143RhythmPdf.js` so the final structured Rhythm PDF visibly includes a 16th-note timing grid/beat guides, section labels, a technique legend, bend/release notation, legato/slide connectors with fallback symbols, sustain lines, and a fail-closed one-note-per-measure collapse guard. The renderer still receives and validates the exact authenticated event stream and does not alter note placement.
- `0932a76b0e427368f95a2bbacc81bdfb51358548` — adds CPU-only `.github/workflows/rhythm-render-presentation-proof.yml` to prove multi-note density, polyphonic onsets, section generation, technique visibility, timing legend, PDF generation, and the collapse negative case before any new GPU run.

The presentation CPU proof is currently pending/being observed. Do **not** run the professional human score until this presentation gate is green and the final-code fresh approved-audio freeze is regenerated/locked, because the final user-visible renderer must be part of the candidate being scored/end-to-end verified.

## Scorer phase status

Professional scorer access is authorized in principle because the earlier post-polyphony freeze is green and locked, but scoring is intentionally held while final-render presentation hardening is validated. The recovered professional source remains scorer-only; no valid final professional score has yet been declared.

## Immediate next steps

1. Wait for `rhythm-render-presentation-proof` CPU gate; inspect its proof/PDF and fix presentation only if needed.
2. Once CPU presentation proof is green, update the real-audio pre-holdout gate with explicit final-render density/timing/technique/section assertions and intentionally trigger one fresh approved-audio run on the final presentation code. Do not trigger extra GPU runs.
3. Require the new final-code freeze to preserve runtime safety, exact event/PDF hash identity and fidelity 1.0, while also proving the 1,017-style multi-note/polyphonic stream is not collapsed and the final PDF exposes timing/technique/section presentation.
4. Lock that final-code artifact as the scoring candidate.
5. Build the complete scorer-only structured professional reference for measures 1–113 from the immutable source. Do not invent unreadable notes/events.
6. Run `verify_reference_completeness.py` and mandatory `run_final_holdout_gate.py` against the exact final-code frozen candidate.
7. Require professional score >=0.99, `criticalMismatchCount == 0`, and PDF-event fidelity 1.0 before declaring Rhythm complete.
8. If the score misses, use the professional result only to diagnose general error classes. Any musical code correction must be reference-free/general, followed by a brand-new approved-audio freeze before another professional score.
9. Once the real professional gate passes, verify DadRock `/ai-tab` user end-to-end — specifically multiple notes/chords per measure, timing grid, techniques, sections, preview/full identity — then create `Final Rhythm Pipeline`.
