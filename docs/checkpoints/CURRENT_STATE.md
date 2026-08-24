# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 22:49 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, corrections remain general/reference-free. After accepting a correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another score**.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`.

**Rhythm is NOT complete. No completion claim has been made.**

## Protected runtime / fixture
- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- protected exact and Production unchanged throughout current work.

## Scorer-only human source — DO NOT OPEN UNTIL NEW FREEZE LOCKED
- source JPG SHA `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured source artifact `9502117311`, artifact SHA `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw track SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- scorer ref V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 = 113 measures / 603 playable onsets / 946 notes / 104 populated; payload never committed.
- old manual temp JSON `4d3e7ee...` not preserved; never claim byte identity with V2.

## Retired scored freezes — NEVER RESCORE
Freeze 1: artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks / 2,009 notes / 113 measures / fidelity1.0; pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord/voicing `.00252845`, critical `2541`.

Freeze 2: preholdout run `32680719988`, artifact `9504147164`, artifact SHA `ded8c8be04c78f46ed05f61a8600e49baab1a2c2c13d9f596f4cffa85e0f22aa`, event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`, 714 attacks / 967 notes / 113 measures / fidelity1.0; score run `32681394580`: pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord/voicing `.00759301443`, coverage1.0, critical1649.

Allowed broad diagnosis only: count inflation largely fixed; dominant remaining classes pitch identity and timing/grid identity. Never derive song-specific runtime rules from scorer events.

## General reference-free fixes already green
### Explicit primary
- precision carries explicit `primary_midis`;
- candidate adapter preserves selected primary through legal voicing;
- CPU/approved-audio proofs passed; no invented attack/pitch/relocation.

### Beat-grid repair
- original 447 beats / 38 interval outliers / premature tail;
- audio-only repair preserves tempo/current phase, anchors stable pulse, removes sub-beat duplicates, bridges weak boundary beats only when later physical evidence exists within one 4/4 bar;
- run `32683424669`: 447→449 beats, outliers38→0, repaired last `209.0956916100s`, active audio end `209.1231746032s`, grid113 measures /1796 slots;
- keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.

## Combined repaired timing + explicit primary — NOT ACCEPTED
Run `32684108550` attempt1 passed musical/safety invariants: repaired outliers0, 113 measures/1796 slots, correction987 attacks, precision722 attacks /998 pitch hypotheses /153 promotions, all113 measures, explicit primary complete, no invented/relocated attack/pitch.

Attempt2 exposed separator drift before scorer: normalized SHA exact `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`; repaired beat SHA exact `c74915787c824d91ba82b1314f3ce52e83bc40c6b72fec13efbf0b23d954e6aa`; direct/cascade stems changed; precision `722/998/153 → 728/1004/154`.

No new Jimmy freeze accepted; scorer remains closed.

## Separator graph — unchanged musically
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

Research wrappers:
- `analyzer/v143_deterministic_separator.py`
- `analyzer/v143_seeded_separator.py`
- `analyzer/v143_seeded_audio_separator_cli.py`
- `analyzer/v143_separator_cold_determinism_probe_modal.py`

## Determinism proofs so far
### Cold proof 1 — GPU deterministic controls insufficient
Run `32684922439`: normalized exact all3 `ab64e7...`; RoFormer exact all3 `ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14`; direct Demucs two-state `5820375b...` / `41ad8bc3...`; cascade two-state `599a51f5...` / `277ec12d...`; first mismatch direct Demucs.

### Cold proof 2 — CPU Demucs insufficient
Run `32685233870`: source/normalized/RoFormer exact; direct CPU Demucs two-state `7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c` / `be081481a9b33f60806707ca79bc974e954ab5e74ad2d588df2b6f1d57269849`; cascade `76d8dec2...` / `ffec9523...`; first mismatch direct.

### Cold proof 3 — CPU single-thread insufficient
Run `32685887212`, diagnostic `debug/v143-contextual-prune/separator-single-thread-cold-proof.json`, result commit `a8136fdb181bd7930e03f92aa62dc2298b04fdbc`: source exact; normalized exact; RoFormer exact; direct pass1=pass2 `be081481...`, pass3 `7999b372...`; cascade pass1=pass2 `ffec9523...`, pass3 `76d8dec2...`; first mismatch direct; protected exact; Production false.

CPU parallel reduction alone is not the explanation.

### Dedicated Demucs shift RNG — FAILED
Commits:
- `10ad1f129c5266465fe3c590f241c70af200c718` private module-like RNG in `v143_seeded_audio_separator_cli.py`
- `c8f18da8a2f6c5017ddb8935b993b2a0429cf453` enable only for Demucs child
- `57ec69007194579d574238a6026b9e1524e13dcc` three-pass proof workflow.

Run `32686215820` completed three independent passes, compare failed; diagnostic bot commit `d2cee67a55c72ba9eddfafe1fcb9b2d744d05493`:
- source exact all3 `215bd5...`
- normalized exact all3 `ab64e7...`
- RoFormer exact all3 `ce7ae8c...`
- direct: `be081481...`, `7999b372...`, `be081481...`
- cascade: `ffec9523...`, `76d8dec2...`, `ffec9523...`
- first mismatch `directGuitarSha256`; protected exact; Production false; `passed=false`.

Patching `apply.py` shift RNG alone did NOT remove the exact same two-state divergence. Do not repeat this with L4 spend.

## Modal cost-control mode — ACTIVE
User billing screenshot at this checkpoint: L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`. L4 is the dominant cost.

Cost-control commits:
- `4e366290c52f7b54b2d5b1ac087f6050f97ecbf2`: expensive separator 3-pass proof changed to manual `workflow_dispatch` only.
- `03b4d41b52d8dd49cffee954ed427c68fd88dff3`: optional `V143_DEMUCS_SHIFT_TRACE_PATH`, off by default, records only randint bounds/value in research diagnostics.
- `7ed9cba0c8f4edfa06ae5e33f99822bb39e7d23b`: added `analyzer/v143_demucs_cpu_host_probe_modal.py`, direct Demucs only, **no GPU request**, 1 CPU, WAV hash + decoded PCM hash + exact shift trace + host/PyTorch fingerprint.
- `d4bf65c1d93e558c2be8b088b947486da8c9a58a`: one-time launch of exactly one cheap CPU-only diagnostic pass.
- `9296e3580796423bbf23c19dc90ad589cde19b16`: CPU probe workflow changed immediately to manual-only; future edits cannot create compute automatically.
- `ff339c08df4b8bfb4774af1102ddcbb85f33ffca`: GitHub Actions committed the one CPU-only probe result.

Low-cost rules:
1. no repeated 3-pass full-song Modal during bug iteration;
2. static/source/syntax/anti-leakage/protected-blob/fixture checks first;
3. direct Demucs only and CPU-only when inference evidence is genuinely needed;
4. one diagnostic run at a time;
5. reserve multi-pass L4 for final determinism gate after a concrete fix;
6. do not run repaired-timing/precision full path until separator exactness;
7. scorer stays closed until deterministic fresh freeze.

## CPU-only direct Demucs probe — RESULT
Artifact committed as `debug/v143-contextual-prune/demucs-cpu-host-probe.json` at bot commit `ff339c08df4b8bfb4774af1102ddcbb85f33ffca`.

Result:
- source SHA exact `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- normalized SHA exact `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- direct WAV SHA `7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c` — one of the two previously observed CPU states
- decoded int16 PCM SHA `820cec705b357eaee03369cb183840216214b98c76f62885184a6259c023efd0`
- bytes `37298220`, sampleRate44100, frames9324544, channels2
- exact private shift trace: **`0,22050,6026`**
- expected seed143 first shift = `6026`; exact match
- no GPU requested; Torch reports CUDA unavailable in this CPU worker
- host exposed by gVisor: `AuthenticAMD`, CPU family175/model1, AVX2 available, no AVX512 flags exposed
- PyTorch `2.13.0+cu130`, built with oneMKL 2024.2 and MKL-DNN/oneDNN 3.12.0, `USE_MKL=ON`, `USE_MKLDNN=ON`, CPU capability usage AVX2
- protected/Production/reference-free invariants passed.

This **rules out “private shift hook was not actually exercised”**: the Demucs shift hook executed and selected the exact deterministic offset 6026 while the output still landed in the known `7999b372...` state. The remaining two-state drift is therefore after/further inside the CPU inference/numerical path, not the selected shift integer.

## Current source-level diagnosis
Upstream `audio-separator==0.44.5` inspected without Modal:
- `demucs/apply.py`: shift trick uses `random.randint`; now directly proven fixed at offset6026.
- `architectures/demucs_separator.py`: `.eval()` then namespaced `apply_model`, same shifts/split/overlap/device settings.
- `demucs/transformer.py`: sinusoidal positional path has `random.randrange`, but htdemucs_6s has `t_sin_random_shift=0`; dropout disabled by `.eval()`.
- no obvious remaining inference RNG explains exact two-state behavior.

Strong current hypothesis: **CPU numerical/kernel dispatch variation across host classes**. PyTorch documents that deterministic algorithms guarantee same results on the same software/hardware but bitwise identity is not guaranteed across different platforms/hardware. Current worker confirms a CPU stack containing both oneMKL and oneDNN. oneDNN documents runtime ISA dispatch controls (`ONEDNN_MAX_CPU_ISA`); Intel oneMKL documents `MKL_CBWR=COMPATIBLE` specifically for reproducibility across Intel and Intel-compatible CPUs, forcing a common code path. This is now the next general/reference-free execution-control avenue; do not change musical settings.

## Current work NOW
1. No more Modal runs in this checkpoint window; the promised single bug-diagnostic run is complete.
2. Research/prepare a general CPU-dispatch pin only in the research wrapper (not Production): likely evaluate oneDNN ISA cap plus oneMKL cross-vendor CNR control, preserving shifts1/overlap.10/segment6/model/PCM input unchanged.
3. Before any next CPU inference, do static/syntax/anti-leakage/protected checks and record the exact proposed dispatch controls.
4. Any next runtime test is one CPU-only direct-Demucs pass, not L4 and not the full separator graph.
5. Keep `.github/workflows/v143-separator-private-shift-cold-proof.yml` and `.github/workflows/v143-repaired-timing-precision-cold-exact.yml` dormant/manual.
6. Do not open scorer reference until separator + full combined path are exact and a brand-new approved-audio freeze/PDF identity is locked.

## After separator + combined determinism are green
1. Accept combined correction only after exact cold-session reproducibility and all safety/coverage invariants pass.
2. Run prepared combined candidate product + fresh pre-freeze proof.
3. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
4. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
6. If failed, use only broad failure classes; correction remains general/reference-free and requires another fresh freeze.
7. Continue until >=0.99, zero critical mismatches, fidelity1.0; then `Final Rhythm Pipeline`, then Bass, then Lead.
