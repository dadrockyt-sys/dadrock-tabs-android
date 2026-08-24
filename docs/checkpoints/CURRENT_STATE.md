# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 22:55 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, correction remains general/reference-free. After accepting a correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another score**.

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
Freeze 1: artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks / 2,009 notes / 113 measures / fidelity1.0; failed pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord/voicing `.00252845`, critical `2541`.

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
Run `32684108550` attempt1 passed invariants: repaired outliers0, 113 measures/1796 slots, correction987 attacks, precision722 attacks /998 pitch hypotheses /153 promotions, all113 measures, explicit primary complete, no invented/relocated attack/pitch.

Attempt2 exposed separator drift before scorer: normalized SHA exact `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`; repaired beat SHA exact `c74915787c824d91ba82b1314f3ce52e83bc40c6b72fec13efbf0b23d954e6aa`; direct/cascade stems changed; precision `722/998/153 → 728/1004/154`.

No new Jimmy freeze accepted; scorer remains closed.

## Separator graph — musically unchanged
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

Research wrappers only:
- `analyzer/v143_deterministic_separator.py`
- `analyzer/v143_seeded_separator.py`
- `analyzer/v143_seeded_audio_separator_cli.py`
- `analyzer/v143_separator_cold_determinism_probe_modal.py`
- `analyzer/v143_demucs_cpu_host_probe_modal.py`

## Determinism history
### GPU controls insufficient
Run `32684922439`: normalized and RoFormer exact all3; direct Demucs two-state; first mismatch direct Demucs.

### CPU / single-thread insufficient
Run `32685233870`: direct CPU Demucs two-state `7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c` / `be081481a9b33f60806707ca79bc974e954ab5e74ad2d588df2b6f1d57269849`.
Run `32685887212`: same exact two-state despite Torch/native single-thread controls; diagnostic `debug/v143-contextual-prune/separator-single-thread-cold-proof.json`; protected exact; Production false.

### Dedicated Demucs shift RNG insufficient
Commits `10ad1f129c5266465fe3c590f241c70af200c718`, `c8f18da8a2f6c5017ddb8935b993b2a0429cf453`, proof workflow `57ec69007194579d574238a6026b9e1524e13dcc`.
Run `32686215820`: source/normalized/RoFormer exact; direct still `be081481...` / `7999b372...`; cascade still two-state; first mismatch direct; protected exact; Production false.

## Modal cost-control mode — ACTIVE
Billing screenshot: L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`; L4 is dominant.

Rules now:
1. no repeated 3-pass full-song Modal during bug iteration;
2. static/source/syntax/anti-leakage/protected-blob/fixture checks first;
3. direct Demucs only and CPU-only when runtime evidence is genuinely needed;
4. one diagnostic run at a time;
5. reserve multi-pass L4 for final determinism proof after a concrete fix;
6. do not run full repaired-timing/precision until separator exactness;
7. scorer stays closed until deterministic fresh freeze.

Expensive `.github/workflows/v143-separator-private-shift-cold-proof.yml` is manual-only since commit `4e366290c52f7b54b2d5b1ac087f6050f97ecbf2`. CPU probe workflow is also manual-only outside explicit one-shot launches.

## ROOT CAUSE CONFIRMED — CPU host ISA/kernel dispatch
Two cheap CPU-only direct-Demucs probes now isolate the exact two states while proving the Demucs shift integer is identical.

### CPU probe 1 — AMD / AVX2
Artifact `debug/v143-contextual-prune/demucs-cpu-host-probe.json`, bot commit `ff339c08df4b8bfb4774af1102ddcbb85f33ffca`:
- source SHA `215bd5...`
- normalized SHA `ab64e7...`
- direct WAV SHA **`7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c`**
- decoded int16 PCM SHA `820cec705b357eaee03369cb183840216214b98c76f62885184a6259c023efd0`
- private shift trace **`0,22050,6026`**
- host `AuthenticAMD`, family175/model1, AVX2, no AVX512 exposed
- PyTorch reports CPU capability usage AVX2.

### CPU probe 2 — Intel / AVX512
Artifact `debug/v143-contextual-prune/demucs-cpu-host-probe-2.json`, bot commit `961161f48018da29a85d10ddefd149f8aa53b1b8`:
- source SHA same `215bd5...`
- normalized SHA same `ab64e7...`
- direct WAV SHA **`be081481a9b33f60806707ca79bc974e954ab5e74ad2d588df2b6f1d57269849`**
- decoded int16 PCM SHA `a15084b514701163ae4ff9029d077f814f75fe74d6d3f83479311a85384109c3`
- private shift trace **`0,22050,6026`** — identical to AMD probe
- host `GenuineIntel`, family6/model85, AVX512 exposed
- same PyTorch `2.13.0+cu130` build reports CPU capability usage AVX512.

This is the decisive isolation: **same fixture + same normalized bytes + same model/settings + same exact Demucs shift offset + single-thread CPU, but AMD/AVX2 produces `7999...` while Intel/AVX512 produces `be081...`.** The old two-state drift is CPU-family/ISA numerical kernel dispatch, not RNG or event logic.

## Current general/reference-free fix under preparation
Official docs checked without Modal:
- PyTorch states bitwise identity is not guaranteed across different platforms/hardware even with deterministic algorithms.
- Intel oneMKL CNR provides `MKL_CBWR=COMPATIBLE` for Intel and Intel-compatible CPUs and forces a common SSE2-compatible code path; fixed thread count and `MKL_DYNAMIC=FALSE`, `OMP_DYNAMIC=FALSE` are required/recommended for reproducibility.
- oneDNN provides `ONEDNN_MAX_CPU_ISA`/`DNNL_MAX_CPU_ISA` to cap JIT CPU dispatch; `SSE41` is a supported common x86 cap.

Research-only commit `7713f13f18d23917d71813b87b5cfa793ea1d488` updates `DEMUCS_SINGLE_THREAD_ENV` in `analyzer/v143_seeded_separator.py` with:
- `OMP_DYNAMIC=FALSE`
- `MKL_DYNAMIC=FALSE`
- `MKL_CBWR=COMPATIBLE`
- `ONEDNN_MAX_CPU_ISA=SSE41`
- `DNNL_MAX_CPU_ISA=SSE41`
while preserving model, shifts1, overlap.10, segment6, PCM input, private shift seed, and all musical logic.

Commit `3a36624ee1612a8549880a4da8fe593ae47b83f3` updates the cheap CPU probe to report those effective requested controls. No Production file changed.

## Current work NOW
1. Prove the dispatch-pin candidate with exactly one cheap CPU-only direct-Demucs run.
2. If its hash is stable, obtain one second cheap CPU-only run on another cold host class and require exact WAV + decoded PCM + shift trace across hosts.
3. Only after CPU cross-host exactness: run one full separator graph pass; defer multi-pass L4 exact proof until final determinism gate.
4. Keep repaired-timing/precision and professional scorer closed until separator exactness.
5. Save every result here frequently.

## After separator + combined determinism are green
1. Accept combined correction only after exact cold-session reproducibility and all safety/coverage invariants pass.
2. Run prepared combined candidate product + fresh pre-freeze proof.
3. Create a **BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity**. Never reuse/rescore `e693602...`.
4. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
6. If failed, use only broad failure classes; correction remains general/reference-free and requires another fresh freeze.
7. Continue until >=0.99, zero critical mismatches, fidelity1.0; then `Final Rhythm Pipeline`, then Bass, then Lead.
