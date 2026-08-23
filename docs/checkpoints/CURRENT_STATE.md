# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — LIVE PRIORITY: finish Rhythm end-to-end against a clean professional human holdout before Bass/Lead
Branch: `v143-contextual-prune-lobo`

## Safety / immutable rules

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Product contract: user-uploaded audio → selected instrument → reference-free analysis → authenticated structured events → professional preview/full PDF. Preview/full PDFs must derive from the exact same authenticated event stream; renderer/browser may not invent musical placement.

Save this checkpoint frequently.

## Completion order / packaging

1. Rhythm first. Complete only after fresh uploaded-audio-equivalent analysis is frozen reference-free, exact PDF event fidelity is 100%, and isolated post-hoc scoring against the professionally human-written Rhythm TAB is near 100% with no critical musical mismatches. Then package as **`Final Rhythm Pipeline`**.
2. Bass second. Use finalized Rhythm architecture as the mold; adapt instrument-specific separation/range/tuning/string mapping/techniques/scoring/rendering. User will provide Bass professional holdout when scoring is ready. Then package **`Final Bass Pipeline`**.
3. Lead third. Again mold from finalized Rhythm architecture. User will provide Lead professional holdout when scoring is ready. Then package **`Final Lead Pipeline`**.

Do not ask for Bass/Lead references early.

Professional references are benchmark-only holdouts. Analyzer must never read/train/tune/select/infer from them. Human reference may be opened only after analyzer output and exact PDF-driving events are frozen. Scorer diagnostics may guide later general/reference-free algorithm changes, but each rescore requires a fresh audio run from scratch.

## Rhythm structural/product baseline — GREEN, final human score OPEN

Approved audio fixture: `public/gomywayfullaitest.m4a`.

Existing real-audio evidence:
- analyzer `v143-reference-free-rhythm`, version `v143-reference-free-rhythm-output-v2`
- reference-free, deterministic separator seed 143, professional reference not used
- 358 valid render events
- 112 unique measures, measures 1..113, all 16 grid steps represented
- 25 technique events
- sustain coverage 358/358
- tempo 129.19921875, 4/4, E Standard
- exact-response full/preview PDFs rendered, 4 pages each
- compact PDF report says `exactReturnedRenderEventsUsed:true`

Evidence:
- `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`
- `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`
- raw product payload lives only in short-retention artifact `.canary/v143-product-output.json`

Structural consistency is not completion; musical accuracy against the clean professional holdout remains unproven.

## Human-reference inventory — IN PROGRESS / DO NOT FINAL-SCORE YET

Confirmed:
- emailed `ds-music-are-you-gonna-go-my-way-remastered-2025-lenny-kravitz-rhythm-tab.pdf` is generated DadRock output, **not** holdout ground truth
- Library image `1000116180.jpg` is a different dark-theme professional tablature source for *Are You Gonna Go My Way*, showing Chorus measures 33–35, labels including `G6`, `A(tp2)`, `E`, `D`, exact string/fret stacks, rhythm notation and lyrics; treat as holdout material only
- Library images `1000116132.jpg` and `1000116183.jpg` are DadRock/Jimmy PAIge proof PDFs, not holdout
- complete professional human source has not yet been reconstructed/inventoried event-by-event; partial screenshots cannot authorize final score

Historical/contaminated diagnostics are not final holdout authority:
- `analyzer/fixtures/gomyway2_full_tab_reference.json`
- `public/training/v143-musical-reconstruction-calibration/contextual-prune-freeze-manifest.json` (historical development reference, 431 events, measures 17–96)
- `analyzer/modal_analyzer_v7_human_reference_benchmark.py`
- `analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py` (passes reference chords into analyzer context; incompatible with clean holdout)
- `analyzer/fixtures/gomyway_full_chord_sustain_reference.json`

Continue exhausting supplied Library/Gmail/repository provenance before asking user to resend Rhythm reference.

## Isolated Rhythm holdout harness — SELF-TEST GREEN

Scorer-only files:
- `validation/rhythm_holdout/README.md`
- `validation/rhythm_holdout/canonical.py`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `validation/rhythm_holdout/verify_runtime_isolation.py`
- `validation/rhythm_holdout/reference/reference.schema.json`
- `validation/rhythm_holdout/score_rhythm_holdout.py`
- `.github/workflows/rhythm-professional-holdout-self-test.yml`

Current important commits:
- `20779870327370b204529a2582e1b6ec7d75c4ea` — canonical scorer event model aligned to actual V143 renderer (`eventIndex`, `stringIndex` 0..5, fret 0..36, bend/legato fields, exact renderer order)
- `bd3da336c40a0c6396f6bc97b85bf168c1b006b2` — professional reference schema aligned to `stringIndex`, 16-step grid, `completeReference:true`
- `01c0644bf9b111920d40db96ae171360059ab714` — isolated scorer aligned to renderer contract
- `a44198df5353b1690c4c532f8ff6838789339f70` — self-test workflow aligned to renderer contract
- bot evidence commit `cec658a32ecfd952ced917ba270fece6f1f1007b` — `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json`

Observed self-test result:
```text
runtimeIsolationPassed: true
syntheticPerfectScorePassed: true
syntheticPdfEventFidelity: 1.0
syntheticCriticalMismatchCount: 0
negativeSafetyTestsPassed: true
usesSyntheticReferenceOnly: true
realProfessionalReferenceOpened: false
passed: true
```

This proves the holdout machinery, not real transcription accuracy.

## Exact structured-event → PDF identity — FIX IN PROGRESS

A subtle issue was found: `buildJimmyPaigeAnalysisPayload` projects raw events once, while `createAiTabPdf` and `createV143RhythmPdf` projected the already-projected stream again. Reprojection could compact/reset `eventIndex`, which is used by legato connectors. Event count equality alone was therefore not strong enough to prove exact event identity.

Fixes committed:
- `36d7815bce80571176b5a09fa507d5493af60461` — real-audio canary now explicitly records `referenceRuntimeInputUsed:false`
- `b825e88143ecf88e11128d136778cb698c15682f` then `2f7e35f26905b082ef9e7571b539794838def96f` — `lib/v143RenderContract.js` adds strict validation of already-projected render streams and makes projection idempotent by preserving existing authenticated `eventIndex`
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `lib/createAiTabPdf.js` now fail-closes on `validateV143RenderEvents` instead of re-numbering via a fresh projection

`createV143RhythmPdf` still calls `projectV143RenderEvents`, but projection is now idempotent for already-projected events, so event identities should survive unchanged. This must be explicitly tested before calling PDF fidelity closed.

The `v143-ai-tab-real-audio-canary` workflow is triggered by `lib/v143RenderContract.js`; a fresh isolated GPU canary may be running/queued from these commits. Do not start another expensive canary unnecessarily until its result is observed.

## Immediate Rhythm actions

1. Extend/observe the non-GPU holdout self-test with an explicit V143 projection-idempotence assertion (including gapped event indices and legato target relationships).
2. Observe the fresh real-audio canary triggered by the render-contract change; require success and explicit `referenceRuntimeInputUsed:false` before using its raw artifact.
3. Add a pre-holdout real-audio freeze workflow: raw product payload → structured payload → freeze exact render events/hash → render preview/full from frozen stream → exact PDF-event hash proof. Do **not** open professional reference there.
4. Finish locating/inventorying the complete user-supplied professional Rhythm source and convert it to scorer-only event/measure ground truth.
5. Run fresh audio → analyzer → freeze/hash → exact PDF → isolated scorer.
6. If below 0.99 or any critical mismatch, improve only general/reference-free algorithms, rerun audio from scratch, refreeze, regenerate PDF, rescore.
7. Only after near-100 + zero critical mismatches + exact PDF fidelity create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch run `32611529763` passed
- note/timing/playability run `32611818648` passed: 1754 events, 100% structural gates
- conservative techniques run `32612166508` passed: 1757 events, 302 technique events, 332 labels; sustain/slide/hammer-on/pull-off/mute proven
- harmonic run `32613012696` passed safe abstention, 0 harmonic events; harmonic unproven; slap/pop/tap/bend/vibrato disabled/unproven
- structured integration run `32613450912` source `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
