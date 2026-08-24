# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 02:42 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged. Scorer V2 remains CLOSED until a new deterministic immutable freeze/PDF. Never rescore retired freezes.

## Determinism + candidate gates — GREEN
- oneDNN-off Demucs byte-exact across AWS Intel / GCP AMD.
- Full separator single-pass GREEN.
- Combined repaired timing + precision single-pass GREEN: 449 repaired beats, 0 outliers, 113 measures/1796 slots, 725 retained attacks, 987 pitch hypotheses, explicit primary complete, all 113 measures populated.
- Final 2-pass exact proof run `32697939613`: `passed=true`, every stage hash/section exact, no invariant failures, protected exact, Production unchanged.
- Candidate product `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` GREEN at bot commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`, blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`. Do not rerun candidate.

## Fresh Jimmy freeze/PDF path — ACTIVE
A new reference-free preholdout workflow was prepared at `.github/workflows/v143-repaired-timing-precision-final-preholdout.yml`. It consumes the exact committed green candidate instead of rerunning Modal, revalidates candidate `preFreezeTrace`, deterministic proof, fixture/protected hashes and runtime isolation, then builds the Jimmy structured payload, freezes exact render events, renders full+preview PDFs, verifies PDF-event fidelity, presentation/visible contract, and rejects retired event identities.
One-shot launch commit: `23a64776333a8fd44dd092890d87e08a4a767e14`.
Workflow restored manual-only immediately at `31949e5b42b1f9bad99e6b7bff8ddf7afb708394`.
Expected compact result: `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json`; artifact name `rhythm-professional-preholdout-real-audio`.
If green, existing `rhythm-final-preholdout-lock.yml` automatically locks that exact run/artifact and independently re-verifies event/PDF identity and presentation. No scorer/reference file is opened by this path.

## Cost control
No new Modal/L4 analysis is used for this fresh freeze/PDF gate. Scorer remains closed. Do not launch any other compute until the fresh preholdout result is assessed.

## Current work NOW
1. Poll only for fresh preholdout compact proof.
2. Require brand-new frozen event SHA, PDF-event fidelity `1.0`, all 113 measures, reference-free safety, protected exact, Production unchanged.
3. Require automatic permanent artifact lock to pass.
4. ONLY THEN reopen scorer V2 and run the unchanged >= `0.99` professional holdout score.
