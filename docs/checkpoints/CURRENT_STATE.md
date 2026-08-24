# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 22:15 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary

Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, corrections remain general/reference-free. After accepting any correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another professional score**.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`.

**Rhythm is NOT complete. No completion claim has been made.**

## Protected runtime / approved fixture

- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

All current gates: protected exact; Production unchanged.

## Scorer-only human source — DO NOT OPEN UNTIL NEW FREEZE LOCKED

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

## General reference-free fixes already green

### Explicit-primary propagation
- precision shadow carries explicit `primary_midis`;
- downstream candidate adapter preserves selected primary through legal voicing;
- CPU/approved-audio proofs passed; no invented attack/pitch/relocation.

### Beat-grid repair
- original 447 beats / 38 interval outliers / premature tail;
- audio-only repair preserves tempo/current phase, anchors stable pulse, removes sub-beat duplicates, bridges weak boundary beats only when later physical evidence exists within one 4/4 bar;
- approved run `32683424669`: 447→449 beats, outliers38→0, repaired last `209.0956916100s`, active audio end `209.1231746032s`, audio-derived grid113 measures /1796 slots;
- keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`; alternate phase evidence weak/unstable.

## Combined repaired-timing + explicit-primary shadow — NOT ACCEPTED YET

Files:
- `analyzer/v143_repaired_timing_precision_shadow_modal.py`
- `.github/workflows/v143-repaired-timing-precision-shadow.yml`
- prepared `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`

Run `32684108550` attempt1 passed all musical/safety invariants:
- repaired outliers0, audio-derived113 measures /1796 grid slots
- correction987 attacks
- precision722 attacks /998 pitch hypotheses /153 promotions
- all113 measures, explicit primary complete, no invented/relocated attack/pitch.

Attempt2 revealed real separator drift before any scorer access:
- normalized SHA exact `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- repaired beat SHA exact `c74915787c824d91ba82b1314f3ce52e83bc40c6b72fec13efbf0b23d954e6aa`
- direct and cascade guitar stems changed; precision moved `722/998/153 → 728/1004/154`.

Therefore NO new Jimmy freeze has been accepted and human scorer remains closed.

## Separator determinism investigation — CURRENT ACTIVE WORK

Separator graph remains musically unchanged:
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

Research-only deterministic wrappers:
- `analyzer/v143_deterministic_separator.py`
- `analyzer/v143_seeded_separator.py`
- `analyzer/v143_seeded_audio_separator_cli.py`
- probe `analyzer/v143_separator_cold_determinism_probe_modal.py`
- workflow `.github/workflows/v143-separator-cold-determinism.yml`

### Cold proof 1 — deterministic GPU controls NOT sufficient

Run `32684922439`, three genuinely independent Modal sessions:
- normalized exact all3: `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- **BS-RoFormer intermediate exact all3:** `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`
- direct Demucs: pass1=pass3 `5820375b67d6d3ad38386c267f8e21b721a06446ba9d8b4de14260d832d2f5a4`; pass2 `41ad8bc3fd1d484ce14322df6da337ea30d626895d788d12e5a5fc0f6e928a8b`
- cascade Demucs: pass1=pass3 `599a51f583312f05784becd7d104bb5ded21b43a2e884b905e397e8b275d2029`; pass2 `277ec12dafe3809974e93a5a2df80e7e1c3f3e79275f389e0a318cc22fba86c8`
- first mismatch = direct Demucs.

Conclusion: RoFormer is deterministic; Demucs is the unstable component.

### Cold proof 2 — CPU Demucs alone NOT sufficient

Demucs was moved to CPU only, keeping identical model/parameters; RoFormer stayed accelerated/proven deterministic.
Run `32685233870`, three independent sessions:
- normalized exact all3
- RoFormer intermediate exact all3 at same SHA `ce7ae8c...`
- direct CPU Demucs: pass1=pass3 `7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c`; pass2 `be081481a9b33f60806707ca79bc974e954ab5e74ad2d588df2b6f1d57269849`
- cascade CPU Demucs: pass1=pass3 `76d8dec2f9db08261594235daed86cb3d4cb04ff92b95761067c30b3b458a2b0`; pass2 `ffec952349534fd1bc0eef5126c42d337998482e8bcd0096dcc94cbbd09a755a`
- `firstMismatchStage=directGuitarSha256`, protected exact, Production false.

The same two-state pass1/pass3 vs pass2 pattern on CPU strongly suggests native CPU parallel reduction/thread scheduling rather than song logic or scorer influence.

### Current correction now committed — single-thread CPU Demucs

- child CLI commit `731d5524...`: `torch.set_num_threads(1)`, `torch.set_num_interop_threads(1)`, deterministic algorithms, seeded RNGs.
- parent separator commit `b1520a8e...`: Demucs children CPU-only plus `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`, `TBB_NUM_THREADS=1`.
- RoFormer remains unchanged accelerated path because it has already proven byte-exact.
- protected runtime/Production untouched.

## Current work NOW

1. Re-run the 3-cold-session separator proof with **single-thread CPU Demucs**.
2. Require exact source, normalized WAV, direct Demucs, RoFormer intermediate, and cascade Demucs hashes across all three sessions.
3. If still divergent, inspect Demucs shift/window implementation and output-write order for the next earliest nondeterministic operation; do not accept a tolerance that can alter event identity.
4. Once separator hashes are exact, rerun the entire repaired-timing + precision path at least twice in fresh sessions and require exact carrier rows, base/correction events, pitch sets, precision attacks/pitches/primaries.
5. Checkpoint exact stable hashes/counts immediately.

## Next steps after separator + combined determinism are green

1. Accept combined correction only after exact cold-session reproducibility and all safety/coverage invariants pass.
2. Run prepared combined candidate product + fresh pre-freeze proof.
3. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
4. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
6. If failed, exact metrics may define only broad failure classes; further correction remains general/reference-free and requires another fresh freeze.
7. Continue until >=0.99, zero critical mismatches, fidelity1.0; then `Final Rhythm Pipeline`, then Bass, then Lead.
