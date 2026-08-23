# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-score musical improvement must remain general/reference-free and requires a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

## CPU gate 1 — GREEN

Canonical `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` is schema 7, `passed:true` from source commit `f84e4b1504fb648799341fbf68255664fb95dc0b` / Actions run `32622951910`.

Key proof: 400 events, 100 measures, frozen/PDF SHA `6475a7d68071a8810890982e1c06c0d39f99e85d646680706233ceed5a58b37e`, fidelity 1.0, polished full+preview PDF rendered, product/real-audio/runtime safety contracts green, reference unopened, Production unchanged.
Canonical promotion commit: `1f995f876e52f091c404002e340b062e373cbe05`.

## CPU gate 2 — GREEN

`debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` is now schema 6, `passed:true`, source commit `1c64d91fff0fb13f4982c212267c22f2951061f7`.

It proves runtime isolation, complete synthetic scorer reference contract, final wrapper positive path >=0.99, PDF fidelity 1.0, zero critical mismatches, partial-reference hard failure, leakage hard failure, PDF mismatch hard failure, static product→professional-PDF glue, branding, event/hash identity. Real professional reference was not opened and Production was not modified.

Both required CPU gates are established green.

## Fresh real-audio pre-holdout — EXACTLY ONE RUN LAUNCHED

Updated `.github/workflows/rhythm-professional-preholdout-real-audio.yml` once at commit:
`1df4a6c55123ae1c4c4b37530f306d43da69bbdd` — `Run locked fresh Rhythm real-audio preholdout`.

That workflow-file write is the intentional single GPU trigger. Do not edit that workflow again while this run is active.

The run now:
- checks out exact `${{ github.sha }}`;
- uses branch concurrency/cancel-in-progress to avoid duplicates;
- installs isolated `pdf-lib@1.17.1` plus Modal CLI rather than the full Next.js dependency graph;
- runs approved fixture `public/gomywayfullaitest.m4a` through the exact V143 Rhythm product canary/live Rhythm image on L4;
- verifies runtime isolation before analysis;
- freezes exact structured renderEvents before any reference access;
- requires `referenceFree:true`, `professionalReferenceUsed:false`, `referenceRuntimeInputUsed:false`, `runtimeLabelsRequired:false`, derived `v143RuntimeSafetyVerified:true`;
- requires freeze input and frozen snapshot to carry the same complete safety state;
- explicitly requires the live endpoint and Production to remain unmodified and promotion unauthorized;
- binds source commit and approved-audio hash/bytes;
- renders full+preview professional PDFs from frozen events only;
- requires renderer projection equality, fidelity 1.0 and frozen/PDF hash identity;
- uploads frozen evidence/PDF artifact and commits compact schema-v2 proof;
- never opens the professional holdout and never runs professional-human scoring.

## Professional holdout remains sealed

Do not recover/open the professional human reference until the fresh GPU proof is green and locked.
`validation/rhythm_holdout/reference/reference-inventory.json` remains `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.

## Immediate next steps

1. Observe `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` from the single run triggered by `1df4a6c5...`.
2. If red, diagnose only the fresh failure without touching holdout reference; no second GPU run unless a concrete general/reference-free fix requires it.
3. If green, fetch/download the run artifact by its `workflowRunId` and lock the frozen analysis/manifest/PDF fidelity/full+preview PDFs.
4. Only after that lock, recover/re-supply the complete professional human-written Rhythm reference strictly scorer-side.
5. Run completeness → isolated scorer → final wrapper. Require score >=0.99, zero critical mismatch, fidelity 1.0.
6. If score misses, improve only general/reference-free musical logic, rerun fresh approved audio, then rescore.
7. Once real gate passes, verify DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
