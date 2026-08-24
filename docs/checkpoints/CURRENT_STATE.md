# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 21:41 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`.
Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, corrections remain general/reference-free. After accepting any correction, create a BRAND-NEW approved-audio run/freeze/PDF identity before another professional score.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`.

**Rhythm is NOT complete.**

## Protected runtime / approved fixture

- protected runtime `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current gates: protected exact; Production unchanged.

## Scorer-only human source

- immutable JPG SHA `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured source artifact `9502117311`, artifact SHA `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw `rhythm-track.json` SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- deterministic scorer reference V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 = 113 measures / 603 playable onsets / 946 notes / 104 populated measures; completeness passes; payload never committed.
- historical manual temp JSON `4d3e7ee...` was not preserved; never claim byte identity with V2.

## Retired scored freezes — NEVER RESCORE

Freeze 1 corrected candidate:
- artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`
- 979 attacks / 2,009 notes / 113 measures / fidelity 1.0
- failed: pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord/voicing `.00252845`, critical `2541`.

Freeze 2 precision candidate:
- preholdout run `32680719988`
- artifact `9504147164`, artifact SHA `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`
- event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`
- 714 attacks / 967 notes / 113 measures / fidelity 1.0
- score run `32681394580` failed: pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord/voicing `.00759301443`, coverage 1.0, critical `1649`.

Broad score diagnosis only: event-count inflation largely fixed; dominant remaining classes are pitch identity and timing/grid identity. Do not derive song-specific runtime rules from scorer events.

## BUG 1 — promoted lower fundamental lost in adapter — FIXED / PROVED

- precision shadow now carries explicit `primary_midis`.
- downstream precision candidate adapter preserves that primary through legal voicing rather than silently re-ranking back to a stronger overtone.
- CPU proof `debug/v143-contextual-prune/precision-shadow-cpu-proof.json` schema2 GREEN: `explicitPrimaryPreserved=true`, `primaryPropagationCheckerPassed=true`, no invented attack/pitch/relocation, protected exact, Production false.
- latest approved-audio primary proof run `32682664616`: corrected `982`, precision attacks `711`, pitch hypotheses `962`, explicit primary `711/711`, promotions `134`, all113 measures, fail-safe0.

## BUG 2 — sub-beat duplicate tracker + early tail — REPAIR SHADOW GREEN

Original timing:
- tempo `129.19921875`
- 447 beats
- 38 interval outliers/sub-beat duplicates
- premature end before active audio tail.

Reference-free repair:
- `analyzer/v143_reference_free_beat_grid_repair.py`
- `analyzer/check_v143_reference_free_beat_grid_repair.py`
- `.github/workflows/v143-reference-free-beat-grid-repair.yml`
- preserve tempo/current phase; one pulse per beat from a stable anchor; snap only to nearby full-mix physical evidence; interior weak beats may use continuity; boundary extension stays inside active audio; at most one 4/4 bar of weak boundary beats can bridge only when a later beat in that bar has independent transient/RMS proof.

Latest approved-audio run `32683424669` GREEN:
- `447 → 449` beats
- interval outliers `38 → 0`
- repaired first `0.6965986395s`, last `209.0956916100s`, active audio end `209.1231746032s`
- three weak tail beats bridged because the fourth predicted beat at `209.095692s` has strong accent `1.64477` and RMS `0.24525`
- next beat `209.560091s` is outside active-audio bound and unsupported, so repair stops cleanly
- repaired grid = **113 measures / 1796 slots**
- protected exact; Production false.

## Bar phase — KEEP CURRENT PHASE

Repaired-grid multi-signal winner is phase2, but confidence only ~`0.1978`, signals disagree, and `stableAcrossHalves=false`. This is insufficient evidence for a general phase change. Keep current `downbeatIndexMod4=1` / `firstBeatInMeasure=3` unless stronger stable audio evidence appears.

## Determinism investigation — CURRENT TWO-PASS PROOF GREEN

Why investigated:
- early accepted precision shadow reported `714 / 968 / 136` (attacks/pitches/promotions)
- later explicit-primary run reported `711 / 962 / 134`.

Current exact stage-hash diagnostic:
- `debug/v143-contextual-prune/precision-determinism-proof.json`
- Actions run `32683174815` SUCCESS
- source, normalized WAV, both separated guitar stems, carrier grid, **entire carrier rows**, base events, corrected events/pitches, precision events/pitches, and explicit primaries were hashed.
- two complete approved-audio passes are exact at **every stage**.
- `firstMismatchStage=null`
- `allStageHashesExact=true`
- current stable output is corrected `982`, retained `711`, pitches `962`, promotions `134`.
- protected exact; Production false.

Code-version comparison also shows no selection-threshold or attack-selection change in the precision module; the current additions are explicit-primary propagation/bookkeeping. Upstream carrier/correction source files did not change between the earlier 714 run trigger and the current primary-preservation trigger. Therefore the historical 714→711 difference is not explained by the new primary bookkeeping itself.

### Stronger cold/session proof now running

The successful two-pass proof could theoretically reuse a warm Modal function container. To eliminate that ambiguity, added:
- `.github/workflows/v143-precision-cross-session-determinism.yml`
- two independent GitHub matrix jobs each start a separate `modal run` session on the exact same fixture/commit;
- outputs are compared stage-by-stage with the same full hashes before any result is accepted.
- status workflow `.github/workflows/v143-precision-cross-session-status.yml`.

Do not create the next Jimmy freeze until this independent-session proof is green.

## Current work NOW

1. Finish independent-session determinism proof; require exact hashes through precision event/pitch/primary identity.
2. If it diverges, repair the FIRST differing stage and rerun until exact/stable.
3. If it is green, treat current 711/962/134 path as reproducible and retire the unexplained historical 714 result as an older environment/run identity rather than a target.
4. Build an isolated combined reference-free path using the **green repaired beat grid + explicit-primary precision**. Inject `repair.timing` into `build_contextual_prune_reference_free_carrier(... timing_estimator=...)`; do not modify protected runtime.
5. Run CPU + approved-audio anti-leakage/protected-runtime proofs on the combined path. Phase remains unchanged.

## Next steps after combined proof is green

1. Accept the combined correction only if no attack/pitch is invented, all audio-supported coverage invariants pass, and deterministic identity is proven.
2. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
3. Verify event/PDF hashes, PDF-event fidelity `1.0`, protected exact, Production unchanged.
4. ONLY THEN reopen scorer-only human reference V2 and run unchanged professional threshold `>=0.99`.
5. If it fails, report exact metrics but use them only as broad failure classes; any further correction remains general/reference-free and requires another fresh freeze before scoring.
6. Continue until >=`0.99`, zero critical mismatches, fidelity1.0.
7. Then create `Final Rhythm Pipeline`; only afterward resume Bass, then Lead.
