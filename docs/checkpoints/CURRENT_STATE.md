# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 01:36 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged.
Scorer V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac` remains CLOSED until a new deterministic immutable freeze/PDF. Never rescore retired Freeze2 `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`.

## Reference-free musical fixes already green
Explicit-primary propagation green; no invented attack/pitch/relocation. Beat-grid repair: 447→449 beats, outliers38→0, 113 measures/1796 slots; phase remains `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.

## Separator determinism — GREEN THROUGH SINGLE-PASS FULL GRAPH
oneDNN-off CPU proof is byte-exact across AWS Intel and GCP AMD with same source/normalized bytes, exact private shift `0,22050,6026`, effective ATen `DEFAULT`, oneDNN disabled, WAV `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`, PCM `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`.

`debug/v143-contextual-prune/separator-single-pass-smoke.json` GREEN:
- normalized `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- direct Demucs `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
- RoFormer `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`
- cascade `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`
- deterministic/reference-free true; protected/Production unchanged; musical settings unchanged.

## Combined repaired-timing + precision single-pass — GREEN
`debug/v143-contextual-prune/repaired-timing-precision-single-pass-smoke.json` completed successfully:
- repaired beats 449, interval outliers 0, 113 measures / 1796 grid slots
- correction 984 attacks
- precision 725 retained attacks / 987 pitch hypotheses / 144 fundamental promotions
- explicit primary MIDI complete 725/725; all 113 target measures populated
- no unobserved attack, relocation, or unobserved pitch; reference-free; Production unchanged
- direct stem `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
- cascade stem `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`
- repaired beats SHA `c74915787c824d91ba82b1314f3ce52e83bc40c6b72fec13efbf0b23d954e6aa`
- precision events SHA `a418118222079a423b4319c7362867c13710620e506f5b211d73e974015392cc`
- precision pitch sets SHA `4a986b255002fe2fce2e1a74df73b9b2ed73ebea9a611a857779ccbcbba839e9`
- precision primary MIDI SHA `bd08caf874fc3afd969cadc1595f87f1fb68a539bf1ff9af2977f976bf46a6a8`

## ACTIVE compute — FINAL 2-PASS COMBINED EXACT PROOF
- Final proof preflight hardened at commit `0b6e7a58801e7bdd84e0528e98c7dce89def479b`.
- It now requires current dispatch controls, exact AWS/GCP cross-host proof, separator single-pass smoke, combined single-pass smoke, fixture/protected hashes, and anti-leakage before Modal compute.
- One-shot launch commit: `4288dbf8551a0746a7eadf137d1ebf834f6d1178`.
- Workflow restored manual-only immediately at `e4bb2c8956ce1b314fe6d0f1e788607d56322575`.
- Exactly two independent combined passes are active. Expected result: `debug/v143-contextual-prune/repaired-timing-precision-cold-exact-proof.json`.
- Do not launch any more compute until this result is assessed.

## Modal cost-control — ACTIVE
No debugging loops. This is the final 2-pass combined acceptance proof, not a repeated diagnostic. Scorer remains closed.

## Current work NOW
1. Poll only for `repaired-timing-precision-cold-exact-proof.json`.
2. Require `passed=true`, every stage hash exact, every section exact, no invariant failures, protected exact, Production unchanged.
3. If green, run candidate/pre-freeze path.
4. Create BRAND-NEW Jimmy analysis/authenticated events/freeze/PDF identity; verify fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer V2 and score at unchanged >=0.99 threshold.
