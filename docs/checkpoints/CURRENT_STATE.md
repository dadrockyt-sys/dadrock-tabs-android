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

Formal provenance inventory:
- `7ee4aedae7f506eb7c7e2df7eb29403fd64e42dc` — `validation/rhythm_holdout/reference/reference-inventory.json`
- sets `completeReferenceAvailable:false`, `finalScoringAuthorized:false`
- forbids runtime access, training, tuning and candidate selection from the human reference; scoring post-freeze only

Strict source/reference completeness protection added:
- `10ae14101cff959a7b90822b33c44df229ad0b61` — strengthened `validation/rhythm_holdout/reference/reference.schema.json`
- final reference must now explicitly assert `transcribedFromCompleteSource:true`, `source.completeSource:true`, source `pageCount`, source SHA-256, and a contiguous `measureRange`
- `4169e44522815539cdc4a299730a9ca8e32d53da` — `validation/rhythm_holdout/verify_reference_completeness.py`
- verifier checks freeze/PDF safety **before opening the reference**, then rejects partial/non-contiguous references, duplicate onset objects, duplicate note identities, invalid string/fret/MIDI mappings, incomplete source provenance, or inconsistent measure counts
- this new completeness verifier still needs to be wired into the synthetic self-test/final scoring orchestration before the holdout harness is considered fully closed

Historical/contaminated diagnostics are not final holdout authority:
- `analyzer/fixtures/gomyway2_full_tab_reference.json`
- `public/training/v143-musical-reconstruction-calibration/contextual-prune-freeze-manifest.json` (`developmentReferenceUsed:true` historically)
- `analyzer/modal_analyzer_v7_human_reference_benchmark.py`
- `analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py`
- `analyzer/fixtures/gomyway_full_chord_sustain_reference.json`

Some previously uploaded files may no longer be loadable. If the complete professional human Rhythm source cannot be recovered from accessible Library/history, it will need to be re-uploaded when final scoring is ready. Do not block current reference-free pipeline work on that yet.

## Isolated Rhythm holdout harness — CORE SELF-TEST GREEN; STRICT COMPLETENESS TEST UPDATE PENDING

Scorer-only files:
- `validation/rhythm_holdout/README.md`
- `validation/rhythm_holdout/canonical.py`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `validation/rhythm_holdout/verify_runtime_isolation.py`
- `validation/rhythm_holdout/verify_reference_completeness.py`
- `validation/rhythm_holdout/reference/reference.schema.json`
- `validation/rhythm_holdout/score_rhythm_holdout.py`
- `.github/workflows/rhythm-professional-holdout-self-test.yml`

Existing observed synthetic self-test bot evidence `cec658a32ecfd952ced917ba270fece6f1f1007b` passed the original core harness:
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

Next harness task: update the synthetic fixture to satisfy the stricter complete-source schema and run `verify_reference_completeness.py` before `score_rhythm_holdout.py`.

## Exact structured-event → PDF identity — DIRECT PROOF GREEN

Fixes:
- `36d7815bce80571176b5a09fa507d5493af60461` — real-audio canary records `referenceRuntimeInputUsed:false`
- `2f7e35f26905b082ef9e7571b539794838def96f` — render projection idempotent; authenticated `eventIndex` preserved
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `createAiTabPdf` fail-closes on validated authenticated Rhythm events
- `d50adfe58db499ae1eb3c9d470108b1765731ef3` — direct identity verifier
- `23909503afa0de7337d43aa419779627075fbbfe` — committed direct proof `debug/v143-contextual-prune/rhythm-render-contract-idempotence.json`

Verified `[0,2,4]` gapped identities, legato target/continuation identity, exact second projection equality, exact validation equality, `passed:true`, Production unchanged.

## Fresh real-audio pre-holdout gate — IMPLEMENTED, RESULT PENDING

Files/commits:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — prepare exact structured freeze payload
- `a185760b134e38b548711d928b24e559530f9b40` — render professional preview/full PDF from frozen events only
- `16bc56a5885802c194a77864553681b7634b7112` — freeze records source-audio SHA-256/bytes
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — `.github/workflows/rhythm-professional-preholdout-real-audio.yml`

Workflow order: runtime isolation → fresh reference-free Modal audio analysis → structured payload → freeze/hash exact events → render preview/full from frozen events → prove PDF event hash equals frozen hash exactly → preserve evidence. Human reference is never opened in this workflow.

Expected compact evidence `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still not present at last check. Do not launch duplicate expensive canaries until the existing attempt is diagnosed/observed.

## Immediate Rhythm actions

1. Wire strict reference completeness validation into the synthetic self-test and make that gate green.
2. Observe/diagnose the existing fresh real-audio pre-holdout workflow without starting duplicate GPU work.
3. Continue checkpointing frequently.
4. Finish recovering the complete clean professional Rhythm source when possible; never substitute contaminated historical Chorus labels or DadRock-generated PDFs.
5. When complete source is available: fresh audio → analyzer → freeze/hash → exact PDF → reference completeness verifier → isolated scorer.
6. If below 0.99 or any critical mismatch, improve only general/reference-free algorithms, rerun audio from scratch, refreeze, regenerate PDF, rescore.
7. Only after near-100 + zero critical mismatches + exact PDF fidelity create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch run `32611529763` passed
- note/timing/playability run `32611818648` passed
- conservative techniques run `32612166508` passed
- harmonic run `32613012696` passed safe abstention; harmonic remains unproven
- structured integration run `32613450912` source `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
