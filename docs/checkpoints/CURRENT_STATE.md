# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — LIVE PRIORITY: finish Rhythm end-to-end against a clean professional human holdout before Bass/Lead
Branch: `v143-contextual-prune-lobo`

## Safety / immutable rules

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Product contract: user-uploaded audio → selected instrument → reference-free analysis → authenticated structured events → professional preview/full PDF. Preview/full PDF must derive from the exact same authenticated event stream; renderer/browser may not invent musical placement.

Save this checkpoint frequently.

## Completion order / packaging

1. Rhythm first. Complete only after fresh uploaded-audio-equivalent analysis is frozen reference-free, exact PDF event fidelity is 100%, and isolated post-hoc scoring against the professionally human-written Rhythm TAB is near 100% with no critical musical mismatches. Then package as **`Final Rhythm Pipeline`**.
2. Bass second. Use finalized Rhythm architecture as the mold; adapt instrument-specific separation/range/tuning/string mapping/techniques/scoring/rendering. User will provide Bass professional holdout when scoring is ready. Then package **`Final Bass Pipeline`**.
3. Lead third. Again mold from finalized Rhythm architecture. User will provide Lead professional holdout when scoring is ready. Then package **`Final Lead Pipeline`**.

Do not ask for Bass/Lead references early.

Professional references are benchmark-only holdouts. Analyzer must never read/train/tune/select/infer from them. Human reference may be opened only after analyzer output and exact PDF-driving events are frozen. Scorer diagnostics may guide later general/reference-free algorithm changes, but each rescore requires a fresh audio run from scratch.

## Rhythm current state — structural/render GREEN, final human score OPEN

Approved audio fixture: `public/gomywayfullaitest.m4a`.

Existing real-audio proof:
- analyzer engine `v143-reference-free-rhythm`, version `v143-reference-free-rhythm-output-v2`
- `referenceFree:true`, `professionalReferenceUsed:false`, deterministic separator seed 143
- 358 raw/valid render events, 100% render survival/playability/placement/pitch validity
- measures 1..113, 112 unique measures, all 16 grid steps covered
- 25 technique events; bend, bend-release, hammer-on, pull-off, slide-down, slide-up
- sustain coverage 358/358
- tempo 129.19921875, 4/4, E Standard
- exact-response full/preview PDFs both rendered successfully from the returned 358 events; 4 pages each
- real-audio PDF validation explicitly reports `exactReturnedRenderEventsUsed:true`

Evidence:
- `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`
- `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`
- workflow `.github/workflows/v143-ai-tab-real-audio-canary.yml`
- raw authoritative analyzer payload is `.canary/v143-product-output.json` inside the short-retention workflow artifact `v143-ai-tab-real-audio-product-canary`; compact repo JSON intentionally does not retain the 358-event list
- historical local built-Next gate green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`

Structural consistency is not completion; musical accuracy against clean professional holdout remains unproven.

## Human-reference inventory — IN PROGRESS / DO NOT FINAL-SCORE YET

Confirmed:
- emailed `ds-music-are-you-gonna-go-my-way-remastered-2025-lenny-kravitz-rhythm-tab.pdf` is generated DadRock output, **not** holdout ground truth
- Library image `1000116180.jpg` is a different dark-theme professional tablature source for *Are You Gonna Go My Way*, showing Chorus measures 33–35, labels such as `G6`, `A(tp2)`, `E`, `D`, exact string/fret stacks, rhythmic notation and lyrics; treat as holdout/reference material only
- Library images `1000116132.jpg` and `1000116183.jpg` are DadRock/Jimmy PAIge generated proof PDFs, not holdout
- complete professional human source has not yet been reconstructed/inventoried event-by-event; partial screenshots cannot authorize final scoring

Historical/contaminated diagnostics must not become the new completion authority:
- `analyzer/fixtures/gomyway2_full_tab_reference.json` is coarse inventory/motif data only
- `public/training/v143-musical-reconstruction-calibration/contextual-prune-freeze-manifest.json` records historical development reference use (431 reference events, measures 17–96); contaminated for a clean holdout
- `analyzer/modal_analyzer_v7_human_reference_benchmark.py` is coarse historical benchmark material
- `analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py` passes reference chords into analyzer context and therefore explicitly violates the new holdout methodology
- `analyzer/fixtures/gomyway_full_chord_sustain_reference.json` is coarse historical expectation data only

Continue exhausting supplied Library/Gmail/repository provenance before asking user to resend Rhythm reference.

## New isolated Rhythm holdout harness — IMPLEMENTED, REAL HOLDOUT STILL SEALED

Scorer-only files on this branch:
- `ade4cfeaf4d9e340cb06c9c6a11daf96f67ebad4` — `validation/rhythm_holdout/README.md`
- `e76bfb70bd4b6659e578b485bb4bdceec3654d0c` — `validation/rhythm_holdout/canonical.py`
- `83a52eaceaa50fca069fd15320919b4c1811ce38` — `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `dc2ab6ef4da553889455e93af8d2198ac37b92e8` — `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `067f593d27f76a08e4544754fb579353ae1ce268` — `validation/rhythm_holdout/verify_runtime_isolation.py`
- `62e435d7e128d38c129195bcfc735b70cccb190d` — final `validation/rhythm_holdout/reference/reference.schema.json` requiring `completeReference:true` and professional provenance
- `e085296ac107f98dde2b67bc076bec3fbd240d57` — `validation/rhythm_holdout/score_rhythm_holdout.py`
- `d2154355f4e94aba77eb9b48d4374fdf011f6e4c` — `.github/workflows/rhythm-professional-holdout-self-test.yml`

Harness behavior:
1. freeze script has no reference argument and refuses reference-directory input/output
2. requires `referenceFree:true`, `professionalReferenceUsed:false`, `referenceRuntimeInputUsed:false`
3. requires exact nonempty `renderEvents`; no fallback to raw candidates
4. canonicalizes/hashes frozen events before scorer access
5. PDF fidelity verifier requires exact canonical event list/hash equality and sets `pdfEventFidelity:1.0` only on exact identity
6. runtime isolation guard scans production analyzer/API/PDF files for holdout/historical-reference imports/tokens
7. scorer validates safety/freeze/PDF identity **before opening reference**, then scores pitch, exact/tolerant timing, string/fret, chord pitch set, voicing, duration, techniques, ties, rests, measure coverage, FP/FN and critical mismatches
8. default professional gate is 0.99; PDF fidelity must be exactly 1.0; critical mismatch count must be 0
9. reference schema requires `completeReference:true`; partial screenshots cannot accidentally pass as a whole-song authority

The self-test workflow includes a perfect synthetic positive path plus hard-failure tests for professional-reference use during analysis and non-identical PDF events. **Its GitHub Actions result has not yet been observed; do not claim it passed until run status/log is confirmed.**

## Immediate Rhythm actions

1. Confirm/fix the new holdout self-test workflow result.
2. Recover the raw 358-event real-audio analyzer artifact (or run a fresh isolated reference-free Rhythm canary) and wire freeze/PDF-event hash evidence around that exact payload.
3. Finish locating/inventorying the complete user-supplied professional Rhythm source and convert it into `validation/rhythm_holdout/reference` event/measure ground truth without exposing it to runtime.
4. Run fresh audio → analyzer → freeze/hash → exact preview/full PDF evidence → isolated scorer.
5. If score is below 0.99 or critical mismatches exist, improve only general/reference-free algorithms, rerun audio from scratch, refreeze, regenerate PDF and rescore.
6. Only after near-100 + zero critical mismatches + exact PDF fidelity, create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, NOW PAUSED

Keep all Bass expansion paused until Rhythm passes.
- separation/pitch run `32611529763` passed
- note/timing/playability run `32611818648` passed: 1754 events, 100% structural gates
- conservative techniques run `32612166508` passed: 1757 events, 302 technique events, 332 labels; sustain/slide/hammer-on/pull-off/mute proven
- harmonic run `32613012696` passed safe abstention, 0 harmonic events; harmonic remains unproven; slap/pop/tap/bend/vibrato disabled/unproven
- structured integration run `32613450912` at source `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success at 2026-08-23T02:44:56Z

No new Bass capability work before Rhythm completion.
