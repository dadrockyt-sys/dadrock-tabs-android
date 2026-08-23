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
- Library images `1000116132.jpg`, `1000116183.jpg`, and `1000116184.jpg` are DadRock/Jimmy PAIge generated/development proof material, not clean human holdout ground truth
- Library search around the professional screenshot surfaced historical Chorus 33–35 development screenshots/scripts explicitly stating professional-reference scoring/development usage; therefore those historical Chorus artifacts are contaminated and cannot become the clean final completion holdout
- complete professional human source has not yet been reconstructed/inventoried event-by-event; partial screenshots cannot authorize final score

Formal provenance inventory committed:
- `7ee4aedae7f506eb7c7e2df7eb29403fd64e42dc` — `validation/rhythm_holdout/reference/reference-inventory.json`
- inventory explicitly sets `completeReferenceAvailable:false` and `finalScoringAuthorized:false`
- clean policy forbids runtime access, training, tuning, and candidate selection from the human reference; scoring is post-freeze only
- historical coarse/reference-derived files and DadRock-generated PDFs are explicitly excluded

Historical/contaminated diagnostics are not final holdout authority:
- `analyzer/fixtures/gomyway2_full_tab_reference.json`
- `public/training/v143-musical-reconstruction-calibration/contextual-prune-freeze-manifest.json` (`developmentReferenceUsed:true` historically)
- `analyzer/modal_analyzer_v7_human_reference_benchmark.py`
- `analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py` (passes reference chord context into analyzer path; incompatible with clean holdout)
- `analyzer/fixtures/gomyway_full_chord_sustain_reference.json`

Continue exhausting supplied Library/Gmail/repository provenance before asking user to resend Rhythm reference. Some previously uploaded files may no longer be loadable, so if the complete professional source cannot be recovered from accessible Library/history it will need to be re-uploaded later; do not block current reference-free pipeline work on that yet.

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

Observed self-test result from bot evidence `cec658a32ecfd952ced917ba270fece6f1f1007b`:
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

## Exact structured-event → PDF identity — DIRECT PROOF GREEN

A subtle issue was found: `buildJimmyPaigeAnalysisPayload` projects raw events once, while PDF code could project an already-projected stream again. Reprojection previously risked compacting/resetting `eventIndex`, which is used by legato connectors.

Fixes:
- `36d7815bce80571176b5a09fa507d5493af60461` — real-audio canary explicitly records `referenceRuntimeInputUsed:false`
- `2f7e35f26905b082ef9e7571b539794838def96f` — `lib/v143RenderContract.js` makes projection idempotent and preserves authenticated `eventIndex`
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `lib/createAiTabPdf.js` fail-closes on validated authenticated Rhythm events
- `d50adfe58db499ae1eb3c9d470108b1765731ef3` — `validation/rhythm_holdout/verify_render_idempotence.mjs`
- `d6a3f49e424b9c2c0d6693deb72046b925b56706` — non-GPU workflow definition

Independent direct execution of the exact branch render contract + verifier passed and was committed as:
- `23909503afa0de7337d43aa419779627075fbbfe` — `debug/v143-contextual-prune/rhythm-render-contract-idempotence.json`

Verified:
```text
rawEventCount: 5
authenticatedEventCount: 3
authenticatedEventIndices: [0,2,4]
gappedEventIdentityTested: true
legatoTargetIdentityPreserved: true
legatoContinuationIdentityPreserved: true
secondProjectionExactlyEqual: true
validationExactlyEqual: true
passed: true
productionModified: false
```

This closes the local/direct projection-idempotence claim. The GitHub Actions version may still be useful as redundant CI, but it is no longer required to establish the code-level identity invariant.

## Fresh real-audio pre-holdout gate — IMPLEMENTED, RESULT PENDING

New pre-holdout machinery deliberately never opens the human reference:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — `validation/rhythm_holdout/prepare_rhythm_freeze_payload.mjs`
- `a185760b134e38b548711d928b24e559530f9b40` — `validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs`
- `16bc56a5885802c194a77864553681b7634b7112` — freeze manifest records source-audio SHA-256/byte provenance
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — `.github/workflows/rhythm-professional-preholdout-real-audio.yml`

Pre-holdout workflow order:
1. static runtime isolation
2. fresh Modal analysis of approved uploaded-audio-equivalent fixture
3. explicit `referenceFree:true`, `professionalReferenceUsed:false`, `referenceRuntimeInputUsed:false`
4. structured payload construction
5. freeze exact render events + source audio hash before any holdout access
6. render full/preview professional PDFs from frozen stream only
7. compare PDF event SHA-256 to frozen event SHA-256; require fidelity exactly 1.0
8. upload full frozen evidence/PDFs as short-retention artifact and commit compact proof only

Expected compact evidence `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still not present at last check, so the GPU workflow result remains pending/unknown. Do not launch duplicate expensive canaries until status is known.

## Immediate Rhythm actions

1. Observe the existing fresh `v143-ai-tab-real-audio-canary` / `rhythm-professional-preholdout-real-audio` result; require explicit `referenceRuntimeInputUsed:false`, frozen source-audio hash, successful professional preview/full render and `pdfEventFidelity:1.0`.
2. If the workflow does not produce evidence, diagnose the existing run/workflow before starting another expensive GPU run.
3. Continue checkpointing frequently.
4. Finish locating/inventorying the complete user-supplied professional Rhythm source. Do not substitute contaminated historical Chorus labels or DadRock-generated PDFs.
5. Run fresh audio → analyzer → freeze/hash → exact PDF → isolated scorer only when the complete clean professional holdout is available.
6. If below 0.99 or any critical mismatch, improve only general/reference-free algorithms, rerun audio from scratch, refreeze, regenerate PDF, rescore.
7. Only after near-100 + zero critical mismatches + exact PDF fidelity create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch run `32611529763` passed
- note/timing/playability run `32611818648` passed: 1754 events, 100% structural gates
- conservative techniques run `32612166508` passed: 1757 events, 302 technique events, 332 labels; sustain/slide/hammer-on/pull-off/mute proven
- harmonic run `32613012696` passed safe abstention, 0 harmonic events; harmonic unproven; slap/pop/tap/bend/vibrato disabled/unproven
- structured integration run `32613450912` source `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
