# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 02:46 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged. Scorer V2 remains CLOSED until the new permanent artifact lock is confirmed. Never rescore retired freezes.

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
- BRAND-NEW frozen event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
- PDF event SHA exact same `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
- PDF-event fidelity `1.0`
- full PDF 1,734,110 bytes / 4 pages; preview 1,707,709 bytes / 4 pages
- protected/Production unchanged.
Workflow artifact exists and is bound to the exact source run: artifact id `9511117529`, digest `sha256:e51777f07b2505b47f5dcf280e1eb9c758c89461ae431f879cdd102f13be05d9`, head SHA `23a64776333a8fd44dd092890d87e08a4a767e14`.

## Permanent artifact lock — PENDING
`rhythm-final-preholdout-lock.yml` should automatically consume the new compact proof and exact artifact and independently verify event/PDF identity, presentation, pitch traceability, occupancy, safety and artifact digest.
Current committed `debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json` is still the OLD retired lock (schema2, run `32642331373`, event SHA `a089a829...`, 1017 events /112 measures). Do NOT treat it as current and do NOT open scorer yet.
Required new lock identity:
- schemaVersion 3
- workflowRunId `32702772593`
- headCommit `23a64776333a8fd44dd092890d87e08a4a767e14`
- artifactId `9511117529`
- eventCount 985 / uniqueMeasureCount 113
- frozen/PDF event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
- PDF-event fidelity 1.0
- reference-free safety true, Production false, `locked=true`, `passed=true`.

## Cost control
Fresh freeze/PDF used no new Modal/L4 analysis. Do not rerun candidate or launch other compute while lock resolves. Scorer remains closed.

## Current work NOW
1. Poll only for replacement permanent lock.
2. Require exact new run/artifact/event identity and every lock invariant green.
3. Save checkpoint immediately when lock lands.
4. ONLY THEN reopen scorer V2 and run exactly one unchanged >= `0.99` professional holdout score.
