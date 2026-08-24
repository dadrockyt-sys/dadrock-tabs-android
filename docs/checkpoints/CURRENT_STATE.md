# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 08:11 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged. Never rescore retired freezes.

## Determinism + candidate gates — GREEN
- oneDNN-off Demucs byte-exact across AWS Intel / GCP AMD.
- Full separator single-pass GREEN.
- Combined repaired timing + precision single-pass GREEN: 449 repaired beats, 0 outliers, 113 measures/1796 slots, 725 retained attacks, 987 pitch hypotheses, explicit primary complete, all 113 measures populated.
- Final 2-pass exact proof run `32697939613`: `passed=true`, every stage hash/section exact, no invariant failures, protected exact, Production unchanged.
- Candidate product `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` GREEN at bot commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`, blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`. Candidate pre-freeze run `32699399835`, raw candidate events SHA `641a3928d7389e3c3e1593fc3b8432206434655bd798df79aeaa4b09666cf012`. Do not rerun candidate.

## Fresh Jimmy freeze/PDF — GREEN
`debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json`, workflow run `32702772593`, source/trigger commit `23a64776333a8fd44dd092890d87e08a4a767e14`:
- `passed=true`, failed checks `[]`
- source audio exact `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- reference-free true; professional reference/runtime input/labels false; reference remained sealed
- 725 selected attacks / 985 render notes / 985 frozen events
- all 113 measures, 725 unique onsets, 236 polyphonic onsets, max chord size 6
- 28 technique events; hammer-on, pull-off, slide-down, slide-up
- 8 reference-free sections spanning measures 1–113
- BRAND-NEW frozen/PDF event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
- PDF-event fidelity `1.0`
- full PDF 1,734,110 bytes / 4 pages; preview 1,707,709 bytes / 4 pages
- protected/Production unchanged.

## Permanent artifact lock — GREEN / CURRENT
`debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json` is now schemaVersion 3 and independently locks the exact current fresh artifact:
- `passed=true`, `locked=true`
- workflowRunId `32702772593`
- artifactId `9511117529`
- artifact digest/ZIP SHA `e51777f07b2505b47f5dcf280e1eb9c758c89461ae431f879cdd102f13be05d9`
- headCommit `23a64776333a8fd44dd092890d87e08a4a767e14`
- source audio SHA exact `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- 725 attack locations / 985 events / 113 measures
- 236 polyphonic attacks; max 6 notes at an attack
- all rendered MIDIs trace to frozen pitch hypotheses
- unique measure/step/string occupancy true
- frozen/PDF event SHA exact `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
- PDF-event fidelity `1.0`
- timing/technique/section display verified
- reference-free safety true; reference not opened during freeze; Production/live endpoint unchanged.
This supersedes the old lock (`a089a829...`) for the next score. Retired locks/freezes remain forbidden for rescoring.

## Cost control
Candidate compute and fresh freeze/PDF are complete. Do not rerun them. No additional Modal/L4 analysis is needed before scoring.

## Current work NOW
1. Inspect scorer workflow/code only and bind it to THIS exact current lock/artifact; do not alter scorer semantics or threshold.
2. Verify scorer-only V2 identity remains expected and runtime/reference isolation stays intact.
3. Run exactly ONE professional holdout score on event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`.
4. Require unchanged threshold >= `0.99`, critical mismatches `0`, and already-locked PDF-event fidelity `1.0` for completion.
5. If score fails, expose broad failure classes only; correction must remain general/reference-free and require another brand-new freeze before rescoring.
