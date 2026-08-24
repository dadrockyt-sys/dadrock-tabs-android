# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 21:58 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, musical corrections stay general/reference-free. After accepting any correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another professional score**.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`.

**Rhythm is NOT complete. No completion claim has been made.**

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

Freeze 1: artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks / 2,009 notes / 113 measures / fidelity1.0. Failed pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord/voicing `.00252845`, critical `2541`.

Freeze 2: preholdout run `32680719988`, artifact `9504147164`, artifact SHA `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`, event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`, 714 attacks / 967 notes / 113 measures / fidelity1.0. Score run `32681394580` failed pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord/voicing `.00759301443`, coverage1.0, critical1649.

Broad score diagnosis only: count inflation largely fixed; dominant remaining classes are pitch identity and timing/grid identity. Never derive song-specific runtime rules from scorer events.

## General reference-free fixes already green in isolation

### Explicit-primary propagation
- precision shadow carries explicit `primary_midis`;
- downstream candidate adapter preserves selected primary through legal voicing;
- CPU/approved-audio proofs passed; no invented attack/pitch/relocation.

### Beat-grid repair
- original 447 beats / 38 interval outliers / premature tail;
- audio-only repair preserves tempo/current phase, anchors stable pulse, removes sub-beat duplicates, bridges weak boundary beats only when later physical evidence exists within one 4/4 bar;
- approved run `32683424669`: 447→449 beats, outliers38→0, repaired last `209.0956916100s`, active audio end `209.1231746032s`, audio-derived grid 113 measures / 1796 slots;
- current phase stays `downbeatIndexMod4=1`, `firstBeatInMeasure=3`; alternate phase evidence remains weak/unstable.

## Combined repaired-timing + explicit-primary shadow

Files:
- `analyzer/v143_repaired_timing_precision_shadow_modal.py`
- `.github/workflows/v143-repaired-timing-precision-shadow.yml`
- prepared candidate product `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`

Run `32684108550`, attempt 1 was musically/invariant green:
- repaired timing outliers `0`
- audio-derived 113 measures / carrier grid 1796
- correction 987 attacks
- precision 722 retained attacks / 998 retained pitch hypotheses / 153 fundamental promotions
- all 113 measures populated
- explicit primary complete
- no invented/relocated attack or pitch
- protected exact; Production false.

### CRITICAL NEW FINDING — separator nondeterminism is REAL; combined correction NOT accepted yet

A deliberate independent rerun of the exact same workflow/run identity (`32684108550`, attempt 2) completed the entire musical analysis but produced a different separator identity before the final git-push step:
- normalized WAV SHA stayed exact: `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- repaired beat-times SHA stayed exact: `c74915787c824d91ba82b1314f3ce52e83bc40c6b72fec13efbf0b23d954e6aa`
- direct guitar stem changed from attempt1 `a19d90e123714f0273f359a8ec51cc1d603806878abe3f244d65ae5d44495f1b` to attempt2 `afd1037bc7d62572ac9b99644d13d95b8593e25b4f442aa4a8f85c1111d97c78`
- cascade guitar stem changed from attempt1 `6dac205fcd4bc9217a294cb9cb8279efb3b6a66a5846da90e539b00105c8ae9c` to attempt2 `44e0fe8874b07bcd4bca7e28f4a512b61214061f6bbf8771426c1b1237ffa201`
- downstream carrier rows/base/correction/precision hashes therefore changed
- precision moved `722/998/153` → `728/1004/154` (attacks / pitch hypotheses / promotions)
- all113 coverage and safety invariants still passed.

Attempt2 workflow conclusion is `failure` ONLY because its final diagnostic commit rebased into an add/add conflict with the already committed attempt1 JSON. **Do not mistake that git failure for the musical issue: the musical hash drift occurred earlier and is real.**

Previous sequential and two-job cross-session proofs were green, but this later cold rerun disproves the stronger assumption that the current GPU separator is reproducible across all fresh executions. Seed=143 alone is insufficient.

Current separator chain:
- `v143_deterministic_separator.py` wraps `v143_seeded_separator.py`
- child CLI `v143_seeded_audio_separator_cli.py` seeds Python/NumPy/Torch but does not yet force deterministic CUDA/cuDNN/cuBLAS algorithms.
- earliest observed differing stage is the **direct Demucs guitar stem**, before Basic Pitch/carrier selection. The cascade also differs.

**Do NOT create a new Jimmy freeze and do NOT access the human scorer until separator identity is deterministic.**

## Current work NOW

1. Fix the earliest nondeterministic boundary in the isolated/reference-free separator path, without touching protected runtime or Production.
2. Add deterministic child-process controls before separator inference: startup `CUBLAS_WORKSPACE_CONFIG`, deterministic Torch/cuDNN settings, TF32 disabled where applicable; preserve all frozen model choices and Demucs/RoFormer musical parameters.
3. Prove direct Demucs stem byte/hash identity across multiple genuinely independent fresh Modal sessions first; then prove the BS-RoFormer→Demucs cascade identity.
4. If GPU kernels remain nondeterministic, isolate only the unstable separator inference onto deterministic CPU execution rather than accepting tolerance that changes event identity.
5. Once direct + cascade hashes are stable across cold sessions, rerun the full repaired-timing + precision path at least twice and require exact hashes through carrier rows, correction events/pitches, precision attacks/pitches/primaries.
6. Update this checkpoint immediately with the stable separator hashes and combined identity.

## Next steps after separator + combined determinism are green

1. Accept the combined general/reference-free correction only after exact cold-session reproducibility and all safety/coverage invariants pass.
2. Run the prepared combined candidate product and a fresh pre-freeze proof.
3. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
4. Verify event/PDF hashes, PDF-event fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
6. If failed, exact metrics may define only broad failure classes; any further correction remains general/reference-free and requires another fresh freeze.
7. Continue until >=0.99, zero critical mismatches, fidelity1.0; then create `Final Rhythm Pipeline`, then Bass, then Lead.
