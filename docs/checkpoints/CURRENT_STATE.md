# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 23:36 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After a scored failure correction remains general/reference-free. After accepting correction create a BRAND-NEW approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. Rhythm is NOT complete.

## Protected runtime / fixture
- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- restore commit `4ff233346b8dc7b80d8f4316fe1317338b5be718`
- fixture `public/gomywayfullaitest.m4a`
- fixture SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- protected exact; Production unchanged.

## Scorer-only source — DO NOT OPEN UNTIL NEW FREEZE LOCKED
- source JPG SHA `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- structured source artifact `9502117311`, artifact SHA `380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`
- raw track SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`
- scorer V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 =113 measures /603 playable onsets /946 notes /104 populated; payload never committed.

## Retired scored freezes — NEVER RESCORE
Freeze1: artifact `9499229323`, event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks /2009 notes /113 measures/fidelity1.0; pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord `.00252845`, critical2541.
Freeze2: artifact `9504147164`, event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`, 714 attacks /967 notes /113 measures/fidelity1.0; score pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord `.00759301443`, critical1649.
Allowed diagnosis only: count inflation largely fixed; broad remaining classes pitch identity and timing/grid identity.

## General reference-free fixes already green
- Explicit-primary propagation green; no invented attack/pitch/relocation.
- Beat-grid repair run `32683424669`: 447→449 beats, interval outliers38→0, repaired last `209.0956916100s`, active end `209.1231746032s`, 113 measures/1796 slots; keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.
- Combined repaired-timing/primary run `32684108550` attempt1 passed invariants but attempt2 exposed separator stem drift, so no new freeze accepted.

## Separator graph — musically unchanged
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

## Modal cost-control — ACTIVE
Billing screenshot: L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`.
Rules: free/static first; one CPU-only direct-Demucs diagnostic at a time; no repeated 3-pass L4 during debugging; multi-pass L4 final-only; repaired-timing/precision and scorer closed until separator exactness.
Expensive 3-pass workflow is manual-only. Prepared manual `.github/workflows/v143-separator-single-pass-smoke.yml` at `e9138129493b84727dccd5a186eff7df9254fb17`; do not run until CPU cross-host exactness is green.

## Confirmed cause class — CPU host numerical dispatch
Unpinned CPU probes with same fixture/normalized bytes/model/settings/one thread/shift `0,22050,6026` mapped old states to host:
- AMD/AVX2 WAV `7999b372...`, PCM `820cec70...`
- Intel/AVX512 WAV `be081481...`, PCM `a15084b5...`
Thus RNG/event logic is ruled out; drift occurs in CPU numerical inference.

## Common AVX2 candidate — CROSS-HOST FAILED
Candidate pinned Demucs child only:
`ATEN_CPU_CAPABILITY=avx2`, oneDNN/DNNL `AVX2`, `MKL_CBWR=COMPATIBLE`, fixed one thread/dynamic false; musical settings unchanged.

Probe1 `debug/v143-contextual-prune/demucs-cpu-avx2-probe-1.json`:
- host `AuthenticAMD`
- WAV `2abd5b447969af2e9aedc89d19050d4ae658e6d4d6f34ecec1b0398654a6ae32`
- PCM `8bbe56527107faf402741df8ffde78cb3051e53b8bdd5f02e94037f405d146a5`
- shift exact `0,22050,6026`.

Probe2 `debug/v143-contextual-prune/demucs-cpu-avx2-probe-2.json`:
- host `GenuineIntel` with AVX512 physically available
- WAV `4b4ff912dd17b921228eaf6b6217f3fe763e111c31a6633c49ff43e00a827705`
- PCM `39e8edfa23a7d902ead4c4198e9c7301cb57227da83fc7076ff155186061daa3`
- same source/normalized bytes, same shift `0,22050,6026`, same requested AVX2/MKL controls.

Therefore common AVX2 requested controls are NOT sufficient for byte-exact cross-vendor Demucs. Do not run full separator/L4 from this candidate.

## New baseline candidate — PREPARED, NOT YET PROVEN
PyTorch source inspection confirms `ATEN_CPU_CAPABILITY=default` is a supported explicit baseline dispatch and bypasses AVX2/AVX512 DispatchStub branches.
Research-only updates:
- `b379a3bb822ba67e69f12ed1e70ced7e45d1b3b1`: optional child runtime trace records effective Torch CPU capability/control env only; no audio/reference data.
- `103307503a5d9dc4046818292379a77ac9219aed`: Demucs research child now pins `ATEN_CPU_CAPABILITY=default`, oneDNN/DNNL `SSE41`, oneMKL `COMPATIBLE`, one thread/dynamic false. Model/shifts1/overlap.10/segment6 unchanged.
- `5788dae54d0f55d67e53d0bee9ece94888b5c537`: static checker updated for baseline controls.
- `a9a2d9dc14493f0db0b6c585f45fac3548a5a88b`: CPU probe captures effective child runtime trace.
- `7ea4c56a60dcb1789333f48b4b1ad4626448860c`: cross-host checker requires effective child `DEFAULT` plus exact WAV/PCM/shift across different vendors.

This is still general/reference-free and changes no musical rule, Production, protected runtime, or scorer.

## Current work NOW
1. Run free/static preflight for baseline candidate through workflow gate.
2. Launch exactly ONE cheap CPU-only baseline direct-Demucs probe with child runtime trace; no L4.
3. If effective child capability is `DEFAULT` and invariants green, run ONE second cold CPU probe and require AMD/Intel exact WAV+PCM+shift.
4. If baseline still differs, do not spend L4; next cheapest isolation is disabling oneDNN only in research child while keeping ATen DEFAULT + MKL CNR.
5. Only after cross-host CPU exactness run one manual full separator smoke; final 3-pass L4 proof remains last determinism gate.
6. Keep repaired timing/precision and scorer closed until separator exactness/fresh freeze.

## After separator + combined determinism are green
1. Run prepared combined candidate product + fresh pre-freeze proof.
2. Create BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity. Never reuse `e693602...`.
3. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
4. ONLY THEN reopen scorer V2 and run unchanged threshold >=0.99.
5. If failed, use only broad failure classes; correction remains general/reference-free and requires another fresh freeze.
6. Continue until >=0.99, zero critical mismatches, fidelity1.0; then Final Rhythm Pipeline, Bass, Lead.
