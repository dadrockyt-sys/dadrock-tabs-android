# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 08:13 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged. Never rescore retired or already-scored freezes.

## Determinism + candidate gates — GREEN
- oneDNN-off Demucs byte-exact across AWS Intel / GCP AMD.
- Full separator single-pass GREEN.
- Combined repaired timing + precision single-pass GREEN: 449 repaired beats, 0 outliers, 113 measures/1796 slots, 725 retained attacks, 987 pitch hypotheses, explicit primary complete, all 113 measures populated.
- Final 2-pass exact proof run `32697939613`: `passed=true`, every stage hash/section exact, no invariant failures, protected exact, Production unchanged.
- Candidate product `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` GREEN at bot commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`, blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`. Candidate pre-freeze run `32699399835`, raw candidate events SHA `641a3928d7389e3c3e1593fc3b8432206434655bd798df79aeaa4b09666cf012`. Do not rerun candidate.

## Fresh Jimmy freeze/PDF + permanent lock — GREEN / SCORED ONCE
Fresh preholdout run `32702772593`, source commit `23a64776333a8fd44dd092890d87e08a4a767e14`, artifact `9511117529`, artifact digest `sha256:e51777f07b2505b47f5dcf280e1eb9c758c89461ae431f879cdd102f13be05d9`.
Permanent lock `debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json` schema3: `passed=true`, `locked=true`, 725 attack locations / 985 events / all 113 measures, frozen/PDF event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, PDF-event fidelity `1.0`, all rendered MIDIs trace to frozen pitch hypotheses, unique measure/step/string occupancy true, reference-free safety true, Production/live endpoint unchanged.
This freeze has now been professionally scored exactly once. It is retired from any future rescore.

## Professional holdout score — FAILED, DIAGNOSIS BROAD ONLY
New one-shot scorer workflow `.github/workflows/v143-repaired-timing-precision-professional-score.yml` bound to the exact current lock before reference access, then opened immutable scorer-only V2 and used the unchanged scorer + `--minimum 0.99`.
Score diagnostic: `debug/v143-contextual-prune/repaired-timing-precision-professional-score.json`, run `32731885778`:
- scorer V2 SHA exact `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 completeness passed: 113 measures / 603 playable onsets / 946 notes / 104 populated measures
- reference opened only after freeze validation; reference payload not committed
- PDF-event fidelity `1.0`; lock/event identity exact; protected pipeline unchanged; Production unchanged
- measure coverage recall `1.0`
- pitch-content F1 `0.23718280683583634`
- pitch+timing tolerant F1 `0.033143448990160536`
- string/fret+timing tolerant F1 `0.018643190056965304`
- chord pitch-set tolerant F1 `0.006024096385542168`
- exact voicing tolerant F1 `0.006024096385542168`
- critical mismatches `1723`
- gross unmatched generated notes `881`; gross unmatched reference notes `842`
- near-100 gate false; `rhythmComplete=false`; scorer return code `2`.
Allowed broad diagnosis only: measure coverage is solved, but pitch identity and especially timing/grid identity remain fundamentally wrong; string/fret and chord/voicing necessarily remain low downstream. Do NOT derive song-specific corrections from professional-reference events.

## Cost control
Do not rescore event SHA `a81190d...`. Do not rerun candidate/freeze. No repeated L4 loops. Next correction must be justified using source/static/audio-only/reference-free evidence first.

## Current work NOW
1. Keep scorer/reference CLOSED again.
2. Inspect current reference-free carrier/timing/pitch-selection logic and existing audio-only diagnostics only.
3. Identify a GENERAL reference-free explanation for the very low pitch/timing self-consistency; no professional event-level data may be read or used.
4. Build static/CPU/reference-free shadow proof first; use at most one targeted inference run only when a concrete general fix requires it.
5. If a correction is accepted, create a BRAND-NEW approved-audio candidate → immutable freeze/PDF → lock before another single professional score.
