# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 23:28 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken the professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure, correction remains general/reference-free. After accepting a correction, create a **BRAND-NEW approved-audio run/freeze/PDF identity before another score**.

Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. Rhythm is NOT complete.

## Protected runtime / fixture
- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- protected exact and Production unchanged throughout current work.

## Scorer-only source — DO NOT OPEN UNTIL NEW FREEZE LOCKED
- source JPG SHA `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured source artifact `9502117311`, artifact SHA `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw track SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- scorer ref V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 = 113 measures / 603 playable onsets / 946 notes / 104 populated; payload never committed.

## Retired freezes — NEVER RESCORE
Freeze1: artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks / 2,009 notes /113 measures/fidelity1.0; failed pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord `.00252845`, critical2541.

Freeze2: preholdout run `32680719988`, artifact `9504147164`, event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`, 714 attacks /967 notes /113 measures/fidelity1.0; score run `32681394580`: pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord `.00759301443`, coverage1.0, critical1649.

Allowed diagnosis only: count inflation largely fixed; remaining broad classes pitch identity and timing/grid identity. Never derive song-specific runtime rules from scorer events.

## General reference-free fixes already green
- Explicit-primary propagation green; candidate adapter preserves selected primary; no invented attack/pitch/relocation.
- Beat-grid repair run `32683424669`: 447→449 beats, interval outliers38→0, repaired last `209.0956916100s`, active end `209.1231746032s`, 113 measures/1796 slots; keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.

## Combined repaired timing + primary — NOT ACCEPTED
Run `32684108550` attempt1 passed invariants: correction987 attacks, precision722 attacks /998 pitch hypotheses /153 promotions, all113 measures, explicit primary complete, no invented/relocated attack/pitch.
Attempt2 exposed separator drift before scorer: normalized/repaired timing exact, direct/cascade stems changed; precision `722/998/153 → 728/1004/154`.
No new Jimmy freeze accepted; scorer remains closed.

## Separator graph — musically unchanged
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

## Modal cost-control mode — ACTIVE
Billing screenshot showed L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`; L4 is dominant.
Rules: free/static checks first; one CPU-only direct-Demucs diagnostic at a time; no repeated 3-pass L4 during debugging; multi-pass L4 final-only; full repaired-timing/precision and scorer stay closed until separator exactness.
Expensive 3-pass separator workflow manual-only since `4e366290c52f7b54b2d5b1ac087f6050f97ecbf2`.

## ROOT CAUSE — CPU ISA/kernel dispatch
Two cheap CPU-only direct-Demucs probes had identical fixture, normalized WAV, model/settings, one thread and shift `0,22050,6026` but mapped the old two output states to CPU host class:
- AMD/AVX2: WAV `7999b372798b2b92a2172e42176a194ba73f36b09435ba0d939a2eb208b3ab6c`, PCM `820cec705b357eaee03369cb183840216214b98c76f62885184a6259c023efd0`.
- Intel/AVX512: WAV `be081481a9b33f60806707ca79bc974e954ab5e74ad2d588df2b6f1d57269849`, PCM `a15084b514701163ae4ff9029d077f814f75fe74d6d3f83479311a85384109c3`.
RNG/event logic ruled out as source of the two-state drift.

## Dispatch controls
SSE41 control experiment produced a third state (`b6cc6404...` WAV / `8f0cf1c8...` PCM), proving CPU dispatch controls affect inference but that candidate was not final.

Current refined common-AVX2 research wrapper pins Demucs child only:
- `ATEN_CPU_CAPABILITY=avx2`
- `ONEDNN_MAX_CPU_ISA=AVX2`
- `DNNL_MAX_CPU_ISA=AVX2`
- `MKL_CBWR=COMPATIBLE`
- `MKL_DYNAMIC=FALSE`, `OMP_DYNAMIC=FALSE`
- one thread, private shift seed unchanged, model/shifts1/overlap.10/segment6 unchanged.
Research commits include `1661a86bfb79239efbb3a7e3f5b9a41ac1bb4ddc`, probe reporting `6ce928b0e5ad846304115ce945fc86a7013b9fae`, static checker `d722b7a1612367b13fa66243a5b546ff9006b95c`, cross-host checker `9bc894676a2a78fc50fed9fddb2157a4f1fbdd31`.

## First corrected common-AVX2 CPU probe — GREEN
Artifact now exists: `debug/v143-contextual-prune/demucs-cpu-avx2-probe-1.json`.
Result:
- source SHA exact `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- normalized SHA exact `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- direct WAV SHA **`2abd5b447969af2e9aedc89d19050d4ae658e6d4d6f34ecec1b0398654a6ae32`**
- decoded PCM SHA **`8bbe56527107faf402741df8ffde78cb3051e53b8bdd5f02e94037f405d146a5`**
- exact shift trace `0,22050,6026`
- host `AuthenticAMD`, AVX2
- requested controls recorded: ATen avx2, oneDNN/DNNL AVX2, MKL COMPATIBLE, dynamic threading false
- no GPU requested; protected/Production/reference-free invariants passed.

This is the first valid result for the refined candidate. It is green on AMD. Cross-host exactness is NOT yet proven.

## Current work NOW
1. Launch exactly ONE second cheap cold-host CPU AVX2 pass, no L4.
2. Require exact WAV `2abd5b44...`, PCM `8bbe5652...`, shift `0,22050,6026` and ideally a different CPU vendor using `check_v143_demucs_cpu_cross_host_exact.py`.
3. If second host is same vendor, do not claim cross-host proof; decide cheapest next validation.
4. Only after CPU cross-host exactness run one full separator graph pass; multi-pass L4 remains final-only.
5. Keep repaired-timing/precision and scorer closed until separator exactness.

## After separator + combined determinism are green
1. Accept combined correction only after exact cold-session reproducibility and all invariants pass.
2. Run prepared combined candidate product + fresh pre-freeze proof.
3. Create a BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity. Never reuse/rescore `e693602...`.
4. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
5. ONLY THEN reopen scorer-only human reference V2 and run unchanged threshold >=0.99.
6. If failed, use only broad failure classes; correction remains general/reference-free and requires another fresh freeze.
7. Continue until >=0.99, zero critical mismatches, fidelity1.0; then Final Rhythm Pipeline, then Bass, then Lead.
