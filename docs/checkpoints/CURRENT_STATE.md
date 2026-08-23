# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — LIVE PRIORITY: complete Rhythm end-to-end before Bass/Lead
Branch: `v143-contextual-prune-lobo`

## Immutable safety / product contract

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, deploy/alter live V143 Modal, promote Production, make payments, redeem customer tokens, send customer emails, weaken quality thresholds, or relabel legacy Bass/Lead as professional structured output without separate authorization.

Required product path:
`user-uploaded audio → Rhythm selection → reference-free analysis → authenticated structured events → professional preview/full PDF → isolated post-freeze professional-human scoring`

Preview/full PDF must derive from the exact frozen event stream. Renderer/browser may not invent musical placement.

Professional human reference is scorer-only holdout material. Analyzer may never read/train/tune/select/infer from it. Every improvement after scoring must be general/reference-free and requires a fresh audio run from scratch before rescoring.

Save this checkpoint frequently.

## Required completion order / finalized folders

1. Rhythm: near-100 professional human agreement, zero critical mismatches, exact PDF-event fidelity 1.0 → package **`Final Rhythm Pipeline`**.
2. Bass: mold from finalized Rhythm architecture; user supplies Bass professional reference when scoring is ready → package **`Final Bass Pipeline`**.
3. Lead: mold from finalized Rhythm architecture; user supplies Lead professional reference when scoring is ready → package **`Final Lead Pipeline`**.

Bass remains paused until Rhythm is truly complete.

## Rhythm real-audio structural baseline — GREEN, musical holdout score still OPEN

Approved audio fixture: `public/gomywayfullaitest.m4a`.

Existing real-audio proof:
- engine `v143-reference-free-rhythm`, output version `v143-reference-free-rhythm-output-v2`
- reference-free; deterministic separator seed 143; professional reference not used
- 358 valid render events
- measures 1..113, 112 unique measures, all 16 grid steps represented
- 25 technique events
- sustain coverage 358/358
- tempo 129.19921875, 4/4, E Standard
- prior exact-response preview/full PDFs rendered from those 358 events

Evidence:
- `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`
- `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`

Structural consistency is not final musical correctness.

## Human professional Rhythm reference — CLEAN HOLDOUT NOT YET COMPLETE

Accessible clean material currently confirmed:
- Library `1000116180.jpg`: dark-theme professional human tablature, Chorus measures 33–35, labels `G6`, `A(tp2)`, `E`, `D`, exact fret stacks/rhythm/lyrics.

Explicitly **not** clean final holdout:
- DadRock/Jimmy generated/development images `1000116132.jpg`, `1000116183.jpg`, `1000116184.jpg`
- emailed DadRock generated Rhythm PDFs
- historical coarse fixtures/benchmarks
- old Chorus 33–35 development artifacts that explicitly used professional reference for scoring/development
- contextual-prune development material where `developmentReferenceUsed:true`

Formal inventory:
- `7ee4aedae7f506eb7c7e2df7eb29403fd64e42dc` — `validation/rhythm_holdout/reference/reference-inventory.json`
- `completeReferenceAvailable:false`
- `finalScoringAuthorized:false`

Some earlier uploads may no longer be loadable. If the complete clean professional source cannot be recovered, it will need to be re-uploaded when final scoring is ready. Do not block reference-free pipeline work on that yet.

## Holdout architecture — STRICT SELF-TEST GREEN

Core files:
- `validation/rhythm_holdout/canonical.py`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `validation/rhythm_holdout/verify_runtime_isolation.py`
- `validation/rhythm_holdout/verify_reference_completeness.py`
- `validation/rhythm_holdout/score_rhythm_holdout.py`
- `validation/rhythm_holdout/run_final_holdout_gate.py`
- `validation/rhythm_holdout/reference/reference.schema.json`
- `validation/rhythm_holdout/reference/reference-inventory.json`
- `validation/rhythm_holdout/reference/.gitignore`

Important commits:
- `10ae14101cff959a7b90822b33c44df229ad0b61` — reference schema now requires complete-source provenance, page count, source SHA-256, `transcribedFromCompleteSource:true`, contiguous measure range.
- `4169e44522815539cdc4a299730a9ca8e32d53da` — strict reference completeness verifier. It validates frozen/PDF safety **before opening the reference**, then rejects partial/non-contiguous/duplicate/inconsistent ground truth.
- `ac0fd9f2587ab4f5568c6ee3d4d980792478e4d2` — self-test updated to enforce completeness and prove partial references hard-fail.
- bot evidence `7e5085c77aa4248890b652767f2784a7d881bebe` (later refreshed by bot) — strict self-test green.
- `669f4445d6b98391754de25276cd6cb1ed54b7cf` — `reference/.gitignore` prevents real professional source/event transcription being committed; only schema/inventory/policy remain in repo.
- `4f9c0d83686f56853a5b6ba2edb1035ed323a542` — mandatory final wrapper `run_final_holdout_gate.py` binds completeness + scorer + frozen/PDF hashes into one fail-closed final result.
- `21c4e08eaa4dae8c798a65a3a23f37b0925ea40c` — README updated with exact final sequence/storage policy.

Latest observed strict synthetic evidence (`debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json`):
```text
schemaVersion: 2
runtimeIsolationPassed: true
syntheticReferenceCompletenessPassed: true
syntheticReferenceComplete: true
syntheticSourceComplete: true
syntheticContiguousMeasureCoverage: true
referenceOpenedOnlyAfterFreezeValidation: true
syntheticPerfectScorePassed: true
syntheticPdfEventFidelity: 1.0
syntheticCriticalMismatchCount: 0
partialReferenceHardFailurePassed: true
negativeSafetyTestsPassed: true
realProfessionalReferenceOpened: false
passed: true
```

This proves holdout machinery only, not real transcription accuracy.

## Exact authenticated event → PDF identity — DIRECT PROOF GREEN

Bug fixed: a second projection could previously compact/reset `eventIndex`, risking broken legato connector identities despite equal event counts.

Key commits:
- `2f7e35f26905b082ef9e7571b539794838def96f` — projection is idempotent and preserves existing authenticated event IDs.
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `createAiTabPdf` fail-closes on validated authenticated Rhythm events.
- `23909503afa0de7337d43aa419779627075fbbfe` — direct proof `debug/v143-contextual-prune/rhythm-render-contract-idempotence.json`.

Verified gapped IDs `[0,2,4]`, legato source/target identity, exact second-projection equality and exact validation equality. Production unchanged.

## Fresh real-audio pre-holdout freeze/PDF gate — CODED, authoritative result still pending

Committed machinery:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — raw product response → structured freeze input only after explicit no-reference safety checks.
- `a185760b134e38b548711d928b24e559530f9b40` — render preview/full professional PDFs from frozen events only.
- `16bc56a5885802c194a77864553681b7634b7112` — freeze records source-audio SHA-256/bytes.
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — `.github/workflows/rhythm-professional-preholdout-real-audio.yml`.

Required proof from this gate:
1. fresh approved user-upload-equivalent audio analysis
2. `referenceFree:true`
3. `professionalReferenceUsed:false`
4. `referenceRuntimeInputUsed:false`
5. exact frozen event hash
6. professional preview/full PDF generated from frozen events
7. PDF event hash exactly equals frozen hash; fidelity 1.0
8. human reference remains sealed/unopened

Expected compact evidence `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still absent. Do not call this gate green yet.

## Static preflight diagnostic — RUNNING / NOT YET GREEN

A CPU-only preflight was added to exercise the exact raw-response → structured payload → freeze → professional PDF → hash-fidelity glue before spending another GPU run:
- `e89b206a0d8b7dcfea2a86804bd973f902330c0a` — initial static workflow.
- `92d66619cfdb2864d573f7c64c57dc5bd391ea46` — self-diagnosing version with per-stage outcomes and 400 synthetic authenticated events.
- workflow `.github/workflows/rhythm-preholdout-static-preflight.yml`.

Expected diagnostic `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` has not appeared yet. Continue observing/diagnosing this CPU gate before retriggering expensive real-audio GPU work.

## Immediate next actions

1. Get `rhythm-preholdout-static-preflight` to emit a diagnostic and pass.
2. Then diagnose/retrigger exactly one fresh real-audio pre-holdout GPU run if necessary; require frozen audio/event hashes + exact professional PDF fidelity 1.0 and no-reference flags.
3. Keep saving this checkpoint frequently.
4. Recover/re-supply a **clean complete** professional Rhythm source only when the reference-free freeze/PDF evidence is safely locked.
5. Run: freeze/PDF proof → reference completeness verifier → isolated professional scorer → `run_final_holdout_gate.py`.
6. If score <0.99 or any critical mismatch, change only general/reference-free algorithms; rerun audio from scratch and rescore.
7. Only after the real gate passes create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch `32611529763` passed
- note/timing/playability `32611818648` passed
- conservative techniques `32612166508` passed
- harmonic `32613012696` passed safe abstention; harmonic remains unproven
- structured integration `32613450912` at `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
