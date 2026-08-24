# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23 23:58 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.

Required path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

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
- scorer V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- V2 = 113 measures / 603 playable onsets / 946 notes / 104 populated; payload never committed.

## Retired scored freezes — NEVER RESCORE
Freeze1: event SHA `c621ab4fd3a14849946a349b1ce2ed430322e3a8b49310f073b51cd8f417a194`, 979 attacks / 2009 notes / 113 measures / fidelity1.0; pitch `.2463621`, timing `.0710660`, string/fret `.0263959`, chord `.00252845`, critical2541.
Freeze2: event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`, 714 attacks / 967 notes / 113 measures / fidelity1.0; score pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord `.00759301443`, critical1649.
Allowed diagnosis only: count inflation largely fixed; broad remaining classes pitch identity and timing/grid identity.

## General reference-free fixes already green
- explicit-primary propagation green; no invented attack/pitch/relocation.
- beat-grid repair run `32683424669`: 447→449 beats, interval outliers38→0, repaired last `209.0956916100s`, active end `209.1231746032s`, 113 measures/1796 slots; keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.
- combined repaired-timing/primary run `32684108550` attempt1 passed invariants; attempt2 exposed separator stem drift, so no new freeze accepted.

## Separator graph — musically unchanged
- Demucs6s `htdemucs_6s.yaml`, Guitar, shifts1, overlap0.10, segment6
- BS-RoFormer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, Instrumental, batch1
- cascade = BS-RoFormer Instrumental → same Demucs6s Guitar.

## Modal cost-control — ACTIVE
Billing screenshot showed L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`.
Rules: free/static first; one CPU-only direct-Demucs diagnostic at a time; no repeated 3-pass L4 during debugging; multi-pass L4 final-only; repaired-timing/precision and scorer closed until separator exactness.
Expensive 3-pass workflow is manual-only. Prepared manual `.github/workflows/v143-separator-single-pass-smoke.yml`; do not run until CPU cross-host exactness is green.

## Confirmed cause class — CPU host numerical dispatch
Unpinned direct-Demucs probes with identical fixture/normalized bytes/model/settings/one thread/shift `0,22050,6026` mapped old states to host class:
- AMD/AVX2 WAV `7999b372...`, PCM `820cec70...`
- Intel/AVX512 WAV `be081481...`, PCM `a15084b5...`
RNG/event logic ruled out. Common AVX2 pin later also failed cross-vendor exactness, so do not spend L4 on that candidate.

## Current baseline candidate
Research-only Demucs child controls:
- `ATEN_CPU_CAPABILITY=default`
- `ONEDNN_MAX_CPU_ISA=SSE41`
- `DNNL_MAX_CPU_ISA=SSE41`
- `MKL_CBWR=COMPATIBLE`
- one thread; `MKL_DYNAMIC=FALSE`, `OMP_DYNAMIC=FALSE`
- private shift seed unchanged; model/shifts1/overlap.10/segment6 unchanged.
Child runtime trace confirms effective Torch capability and control environment. No song/reference/scorer data enters this path.

### Baseline probe 1 — GREEN
`debug/v143-contextual-prune/demucs-cpu-baseline-probe-1.json`
- host `AuthenticAMD`
- source/normalized exact
- WAV `a58e260f4b91d208b5d6f0bf33590b503cb47ea3b316d3b34841e69329a4c48a`
- PCM `551e22e13abe4f8e47182db9c868817141ed8fa702235099364521d9c6d18654`
- shift exact `0,22050,6026`
- child runtime `torchCpuCapability=DEFAULT`, Torch threads1/inter-op1, oneDNN enabled, requested baseline env present
- no GPU; invariants green.

### Baseline probe 2 — GREEN AND BYTE-EXACT, BUT SAME VENDOR
`debug/v143-contextual-prune/demucs-cpu-baseline-probe-2.json`, bot commit `fa6932021d62853bc037af58e7bf6f3827c15e46`
- host `AuthenticAMD`
- source/normalized exact
- WAV **exactly same as probe1** `a58e260f4b91d208b5d6f0bf33590b503cb47ea3b316d3b34841e69329a4c48a`
- PCM **exactly same as probe1** `551e22e13abe4f8e47182db9c868817141ed8fa702235099364521d9c6d18654`
- shift exact `0,22050,6026`
- child runtime effective `DEFAULT`; requested baseline env present; invariants green.

This proves cold-session exactness on two AMD hosts but **does not yet prove AMD↔Intel cross-host exactness**.

## Current work NOW
1. Launch exactly ONE third cheap CPU-only baseline probe; no L4.
2. If it lands on Intel, require exact WAV `a58e260f...`, PCM `551e22e1...`, shift `0,22050,6026`, effective child `DEFAULT`.
3. If third is AMD again, do not claim cross-host proof and avoid uncontrolled repeated spending; choose the cheapest deterministic host-selection/isolation route.
4. Only after AMD↔Intel exactness run one manual full-separator smoke; final 3-pass L4 proof remains last determinism gate.
5. Keep repaired timing/precision and scorer closed until separator exactness and a fresh immutable freeze.

## After separator + combined determinism are green
1. Run prepared combined candidate product + fresh pre-freeze proof.
2. Create BRAND-NEW approved-audio Jimmy analysis → authenticated events → immutable freeze → exact preview/full PDF identity. Never reuse `e693602...`.
3. Verify event/PDF hashes, fidelity1.0, protected exact, Production unchanged.
4. ONLY THEN reopen scorer V2 and run unchanged threshold >=0.99.
5. If failed, use only broad failure classes; correction remains general/reference-free and requires another fresh freeze.
6. Continue until >=0.99, zero critical mismatches, fidelity1.0; then Final Rhythm Pipeline, Bass, Lead.
