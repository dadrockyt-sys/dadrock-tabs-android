# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 21:48 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, musical corrections stay general/reference-free. After accepting any correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another professional score**.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`.

**Rhythm is NOT complete.**

## Protected runtime / approved fixture

- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current gates: protected exact; Production unchanged.

## Scorer-only human source

- source JPG SHA `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured source artifact `9502117311`, artifact SHA `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw track SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- deterministic scorer ref V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 = 113 measures / 603 playable onsets / 946 notes / 104 populated; payload never committed.
- old manual temp JSON `4d3e7ee...` was not preserved; never claim byte identity with V2.

## Retired scored freezes — NEVER RESCORE

Freeze 1:
- artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- 979 attacks / 2,009 notes / 113 measures / fidelity1.0
- failed: pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord/voicing `.00252845`, critical `2541`.

Freeze 2:
- preholdout run `32680719988`, artifact `9504147164`, artifact SHA `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`
- event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`
- 714 attacks / 967 notes / 113 measures / fidelity1.0
- score run `32681394580`: pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord/voicing `.00759301443`, coverage1.0, critical1649.

Broad score diagnosis only: count inflation largely fixed; dominant remaining classes are pitch identity and timing/grid identity. Never derive song-specific runtime rules from scorer events.

## BUG 1 — promoted lower fundamental lost downstream — FIXED / PROVED

- precision shadow carries explicit `primary_midis`.
- candidate adapter preserves selected primary through legal voicing instead of re-ranking to stronger overtone.
- CPU proof `precision-shadow-cpu-proof.json` schema2 GREEN: explicitPrimaryPreserved true; primaryPropagationCheckerPassed true; no invented attack/pitch/relocation.
- latest approved-audio primary run `32682664616`: corrected982; retained711; pitch hypotheses962; explicit primary711/711; promotions134; all113 measures; fail-safe0.

## BUG 2 — sub-beat duplicates + premature tail — REPAIR GREEN

Original timing: tempo129.19921875, 447 beats, 38 interval outliers/sub-beat duplicates, premature tail stop.

General reference-free repair:
- stable pulse anchor, one pulse/beat, nearby full-mix transient snapping;
- weak interior beats may use continuity;
- boundary extension remains inside active audio;
- at most one 4/4 bar of weak boundary beats may bridge only if a later beat in that bar has independent transient/RMS proof;
- tempo/current phase remain unchanged;
- no target measure count/song/reference/scorer data enter.

Approved run `32683424669` GREEN:
- 447→449 beats
- outliers38→0
- repaired last `209.0956916100s`, active end `209.1231746032s`
- 3 weak beats bridged because fourth predicted beat has accent1.64477 / RMS0.24525
- next predicted beat outside active audio and unsupported
- audio-derived repaired grid = **113 measures / 1796 slots**
- protected exact, Production false.

## Bar phase — KEEP CURRENT

Repaired multi-signal winner is phase2 but confidence ~0.1978, signals disagree, stableAcrossHalves=false. Insufficient evidence for phase rotation. Keep current `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.

## Determinism — GREEN INCLUDING INDEPENDENT MODAL SESSIONS

Initial concern: older precision run 714/968/136 vs current 711/962/134.

Sequential exact proof:
- run `32683174815` SUCCESS
- source → normalized WAV → both guitar stems → grid → full carrier rows → base → correction → precision events/pitches/primaries all hash-exact across two full passes
- firstMismatchStage null; allStageHashesExact true.

Stronger independent-session proof:
- workflow `.github/workflows/v143-precision-cross-session-determinism.yml`
- run `32683791740` SUCCESS
- two independent GitHub jobs each opened a separate `modal run` session
- compare job passed exactly
- diagnostic `debug/v143-contextual-prune/precision-cross-session-determinism.json`
- every stage hash exact, including full carrier rows, correction events/pitches, precision attacks/pitches/primaries
- `firstMismatchStage=null`, `allStageHashesExact=true`, `independentModalSessions=true`
- protected exact, Production false.

Current 711/962/134 path is therefore reproducible in the current locked environment. The historical 714 identity is retired as an older run/environment identity; it is not a target count.

## Combined repaired-timing + explicit-primary precision — ACTIVE

New isolated shadow:
- `analyzer/v143_repaired_timing_precision_shadow_modal.py`
- workflow `.github/workflows/v143-repaired-timing-precision-shadow.yml`
- current run `32684108550` (run2) is in progress; CPU invariants + anti-leakage/protected-runtime gate already GREEN.
- run1 `32683937365` was intentionally cancelled by concurrency after improving the combined path to derive its measure range from repaired audio timing instead of hardcoding 113.

Combined path now:
1. reference-free original timing
2. green audio-only beat repair
3. deterministic guitar separation
4. carrier built with injected `repair.timing`
5. **measure range derived from repaired audio** (`measure_end=None`), never a human target count
6. contextual base selector → general shadow correction → precision → explicit primary preservation
7. no attack/pitch invention or relocation allowed.

Prepared but NOT yet executed as a freeze:
- `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`
- same audio-derived measure range + repaired timing + explicit-primary candidate path through bends/legato/semantic guard/two-view sustain.

## Current work NOW

1. Finish combined shadow run `32684108550`.
2. Require: repaired outliers0, carrier uses repaired timing, measure range derived from audio, all derived measures populated, precision subset invariants, explicit primary complete, protected exact, Production false.
3. Inspect counts/hashes and accept only if physically coherent and reference-free.
4. If green, run the prepared combined candidate product and create CPU/approved-audio pre-freeze proof.
5. Do NOT access human scorer data during these steps.

## Next steps after combined proof is green

1. Accept combined correction only after all safety/determinism/coverage invariants pass.
2. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
3. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
4. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
5. If failed, exact metrics may define only broad failure classes; any further musical correction remains general/reference-free and requires another fresh freeze.
6. Continue until >=0.99, zero critical mismatches, fidelity1.0.
7. Create `Final Rhythm Pipeline`; only then resume Bass, then Lead.
