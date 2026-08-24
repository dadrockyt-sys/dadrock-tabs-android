# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 00:07 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected runtime / fixture
- protected `analyzer/v143_reference_free_rhythm_pipeline.py`
- required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`
- fixture `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- protected exact; Production unchanged.

## Scorer-only — CLOSED
Scorer V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated. Do not open until a brand-new deterministic freeze/PDF identity is locked.
Retired Freeze2 event/PDF SHA `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`; never rescore it. Last score: pitch `.2624150549`, timing `.0522739153`, string/fret `.0282279143`, chord `.00759301443`, critical1649. Allowed diagnosis only: broad pitch identity + timing/grid identity.

## Reference-free musical fixes already green
- explicit-primary propagation green; no invented attack/pitch/relocation.
- beat-grid repair run `32683424669`: 447→449 beats, outliers38→0, 113 measures/1796 slots; keep `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.
- combined repaired-timing/primary attempt1 green, but separator drift blocked acceptance. No new freeze accepted.

## Separator graph — musically unchanged
Demucs6s Guitar, shifts1, overlap0.10, segment6; BS-RoFormer Instrumental batch1; cascade = RoFormer Instrumental → same Demucs6s Guitar.

## Modal cost-control — ACTIVE
Billing screenshot showed L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`. Rules: free/static first; exactly one CPU-only direct-Demucs diagnostic at a time; no repeated 3-pass L4 during debugging; final multi-pass L4 only after a concrete deterministic fix. Full repaired-timing/precision and scorer remain closed.
Expensive separator proof and full combined exact workflows are manual-only. Prepared one-pass full separator smoke remains dormant.

## Confirmed failure class
Unpinned output mapped to CPU host/ISA. Common AVX2 pin also failed cross-vendor exactness. RNG is ruled out: every probe uses exact private shift `0,22050,6026` with identical source/normalized bytes.

## ATen DEFAULT + oneDNN SSE41 baseline — FAILED ACROSS AMD MICROARCHITECTURES
Probe1 `demucs-cpu-baseline-probe-1.json`: AuthenticAMD family175/model1, WAV `a58e260f4b91d208b5d6f0bf33590b503cb47ea3b316d3b34841e69329a4c48a`, PCM `551e22e13abe4f8e47182db9c868817141ed8fa702235099364521d9c6d18654`.
Probe2 `demucs-cpu-baseline-probe-2.json`: AuthenticAMD family175/model1, byte-exact with probe1.
Probe3 `demucs-cpu-baseline-probe-3.json`, bot commit `52f0c112b46f99bd228e2ed6d4aa3f22ed036ea2`: AuthenticAMD family175/model17 with AVX512 physically exposed, effective child still `torchCpuCapability=DEFAULT`, oneDNN SSE41 requested, one thread, same shift/source/normalized bytes, but WAV **`5d27860c04cf7ac25c13ab7f264fea4a8959ab3e811c9c4f8db3319a306506e1`**, PCM **`bddb7e52dd4a4707741d19be8f65eda8bfab1b8743df504c4068c4fa732b28f6`**.
Therefore baseline with oneDNN enabled is not byte-exact even inside AMD across microarchitectures. Do NOT spend L4 on it.

## New cheapest isolation — oneDNN OFF, PREPARED
Research-only, no musical change:
- commit `3c5eb669b909a7d56e130b325e66eeab144553ff`: optional `V143_DEMUCS_DISABLE_MKLDNN=1` makes Demucs child set `torch.backends.mkldnn.enabled=False` before audio-separator/model import; runtime trace records effective state.
- commit `0b3d73bb5f68fee0f76e4fb2827c1f982ea117eb`: Demucs research env enables that switch while keeping `ATEN_CPU_CAPABILITY=default`, `MKL_CBWR=COMPATIBLE`, one thread/dynamic false, model/shifts1/overlap.10/segment6 unchanged.
- commit `a49d30ce85cb1ecd7d6f927b6c8e71c5bce895ae`: static checker requires oneDNN-off implementation/settings.
- commit `293bfe5777e951b9532328e718d03fea153801c1`: CPU probe now records Modal cloud provider/region for cheaper host-placement diagnosis on future runs.
No Production/protected/scorer file changed.

## Current work NOW
1. Run free/static gate for oneDNN-off candidate.
2. Launch exactly ONE cheap CPU-only direct-Demucs probe, no L4, and require effective child `mkldnnEnabled=false`, ATen `DEFAULT`, exact shift/source/normalized bytes.
3. If green, run only one second cold CPU probe; compare exact WAV/PCM. Prefer a different microarchitecture/provider/region if placement evidence allows, rather than random repeated spend.
4. Only after cross-host exactness run one manual full-separator smoke. Final 3-pass L4 proof stays last.
5. Keep scorer closed until separator + combined path are exact and a BRAND-NEW immutable Jimmy freeze/PDF is locked.

## After determinism is green
Run combined candidate/pre-freeze → create new Jimmy analysis/authenticated events/freeze/PDF → fidelity1.0/protected exact/Production unchanged → ONLY THEN scorer V2 at unchanged threshold >=0.99. If failed, use broad failure classes only and require another fresh freeze.
