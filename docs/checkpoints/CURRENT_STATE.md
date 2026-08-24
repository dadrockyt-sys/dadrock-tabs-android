# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 01:57 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged.
Scorer V2 remains CLOSED until a new deterministic immutable freeze/PDF. Never rescore retired Freeze2.

## Determinism gates — GREEN
- oneDNN-off Demucs direct stem byte-exact across AWS Intel and GCP AMD: WAV `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`, PCM `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`.
- Full separator single-pass smoke GREEN.
- Combined repaired-timing/precision single-pass GREEN: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, 984 correction attacks, 725 retained precision attacks, 987 pitch hypotheses, 725/725 explicit primaries, all 113 measures populated, no invented/relocated attack or pitch.

## FINAL 2-PASS COMBINED EXACT PROOF — GREEN
`debug/v143-contextual-prune/repaired-timing-precision-cold-exact-proof.json`, run `32697939613`:
- `passed=true`; 2 independent passes
- every required stage hash exact; every required section exact
- no mismatches; no invariant failures
- protected pipeline exact; Production unchanged.

## ACTIVE compute — ONE CANDIDATE/PRE-FREEZE PRODUCT
All determinism acceptance gates are green. Exactly one approved-audio candidate/pre-freeze product was launched at commit `1861f7a2a4aec814dd8b8504e5cca7c1f8ce6ae1`.
Workflow was restored manual-only immediately at `470180eff851b4552f53dfdb553dda94c5d724f6`.
Expected output: `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json`.
Do not launch additional compute until this resolves.

## Modal cost-control — ACTIVE
No debugging loops. Scorer remains closed until a BRAND-NEW candidate freeze/PDF is locked.

## Current work NOW
1. Poll only for candidate product output.
2. Require candidate/reference-free/safety invariants, protected exact, Production unchanged, nonzero events/notes, and immutable pre-freeze events SHA.
3. If green, create a BRAND-NEW Jimmy analysis/authenticated events/freeze/PDF identity.
4. Verify PDF-event fidelity `1.0`, protected exact, Production unchanged.
5. ONLY THEN reopen scorer V2 and score at unchanged >= `0.99` threshold.
