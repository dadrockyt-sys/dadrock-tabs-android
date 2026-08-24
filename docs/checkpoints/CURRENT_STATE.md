# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 02:29 America/Thunder_Bay
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
- Final two-pass combined exact proof `debug/v143-contextual-prune/repaired-timing-precision-cold-exact-proof.json`, run `32697939613`: `passed=true`, every required stage hash/section exact, no invariant failures, protected exact, Production unchanged.

## Candidate / pre-freeze product — GREEN
`debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` completed and was committed by `github-actions[bot]` at commit `289a04e0fe30b5668ddaf39427404d8472ca1f51` (`Record repaired-timing precision candidate product`), result blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`.
The workflow only commits after approved-fixture, audio-derived measure range, repaired timing, reference-free assembly/live path, nonzero events/notes, no unobserved attack/pitch/relocation, protected-blob exactness, Production unchanged, and pre-freeze trace validation are green. No scorer/reference input was opened.

## Modal cost-control — ACTIVE
Candidate compute is complete. Do not rerun it. No debugging loops. Scorer remains closed until a BRAND-NEW candidate freeze/PDF is locked.

## Current work NOW
1. Inspect only the non-scorer preholdout/freeze/render workflows and select or prepare a safe current-candidate path.
2. Require current candidate events as input; do not reuse retired Freeze2 identity or hashes.
3. Create a BRAND-NEW Jimmy analysis/authenticated event identity + immutable freeze + professional preview/full PDF.
4. Verify PDF-event fidelity `1.0`, protected exact, Production unchanged, reference-free runtime path.
5. ONLY THEN reopen scorer V2 and score at unchanged >= `0.99` threshold.
