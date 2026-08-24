# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 00:30 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute boundary
Work only on `v143-contextual-prune-lobo`. Never modify/merge `main`, deploy/change live V143 Modal/Production, promote Production, make payments, send customer emails, or weaken professional threshold.
Required path: `user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`.
Human professional reference is scorer-only. Runtime may NEVER read/train/tune/select from it. After scored failure, corrections remain general/reference-free. After accepting correction create a **BRAND-NEW** approved-audio run/freeze/PDF identity before another score.
Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**

## Protected/runtime boundary
Protected `analyzer/v143_reference_free_rhythm_pipeline.py` required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`. Fixture `public/gomywayfullaitest.m4a` SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`. Protected exact; Production unchanged.
Scorer V2 SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac` remains CLOSED until a new deterministic immutable freeze/PDF. Never rescore retired Freeze2 `e693602ade26256851dc0d77b003bf6ba0d5014dfaec7e35103ecdf25d33c32f`.

## Reference-free musical fixes already green
Explicit-primary propagation green; no invented attack/pitch/relocation. Beat-grid repair `32683424669`: 447→449 beats, outliers38→0, 113 measures/1796 slots; phase remains `downbeatIndexMod4=1`, `firstBeatInMeasure=3`. Combined repaired-timing/primary attempt1 green, but separator drift blocked acceptance.

## Separator graph — musically unchanged
Demucs6s Guitar shifts1/overlap0.10/segment6; BS-RoFormer Instrumental batch1; cascade = RoFormer Instrumental → same Demucs6s Guitar.

## Modal cost-control — ACTIVE
Billing screenshot: L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`. Free/static first; exactly one CPU-only direct-Demucs diagnostic at a time; no repeated 3-pass L4 debugging; final multi-pass L4 only after deterministic fix. Full combined and scorer remain closed. Expensive workflows manual-only.

## Prior failed execution candidates
RNG ruled out: exact shift `0,22050,6026` throughout. Unpinned output mapped to host/ISA; common AVX2 failed cross-vendor; ATen DEFAULT + oneDNN SSE41 failed even across AMD microarchitectures. Do not spend L4 on those candidates.

## Current oneDNN-OFF candidate
Research-only. Demucs child sets `torch.backends.mkldnn.enabled=False` before audio-separator/model import while keeping ATen `DEFAULT`, oneMKL `COMPATIBLE`, one thread/dynamic false, private shift seed, model/shifts1/overlap0.10/segment6 unchanged. Static checker and cross-host checker require effective oneDNN off. Probe supports targeted cloud selection and records Modal provider/region. No Production/protected/scorer file changed.
Key commits: `3c5eb669b909a7d56e130b325e66eeab144553ff`, `0b3d73bb5f68fee0f76e4fb2827c1f982ea117eb`, `a49d30ce85cb1ecd7d6f927b6c8e71c5bce895ae`, `ab7182a10da664d92ca19ff1f8613b51092baf75`, `63152be78cdde2b18a761e431cecadb3c4f02c09`.

### oneDNN-off probe 1 — GREEN
`debug/v143-contextual-prune/demucs-cpu-nomkldnn-probe-1.json`, bot commit `34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`:
- source SHA exact `215bd5...`; normalized SHA exact `ab64e7...`; shift exact `0,22050,6026`
- host `GenuineIntel` family6/model85, physically AVX512
- Modal provider `CLOUD_PROVIDER_AWS`, region `us-east-2`
- effective child `torchCpuCapability=DEFAULT`, `mkldnnEnabled=false`, Torch threads1/inter-op1
- WAV **`0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`**
- PCM **`2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`**
- reference-free/no-GPU/Production/protected invariants green.

## ACTIVE compute — ONE TARGETED CPU-ONLY GCP RUN
Launch `bf9e16a84d3e1618c17d5a3b6c765872260ba145`: exactly one second oneDNN-off CPU probe with `--cloud gcp`; workflow restored manual immediately at `8927316f8738b64b1ce0afae67cdac2f578ca4b1`. Expected file `debug/v143-contextual-prune/demucs-cpu-nomkldnn-probe-2.json`. No L4 requested.
At 00:30 America/Thunder_Bay the expected probe2 file is still not committed. No additional compute has been launched while it is unresolved.

## Validation continuation prepared
- Cross-host checker is ready to require exact source/normalized/WAV/PCM/shift, effective ATen `DEFAULT`, and effective oneDNN disabled across two different host vendors/providers.
- Manual full-separator single-pass smoke remains gated behind successful CPU cross-host exactness.
- Manual repaired-timing/precision single-pass smoke was prepared at `7aca7545c5f05288f4b4777cb4dd3e99b2972de6`; it requires the full-separator smoke artifact first.
- Candidate-product workflow was hardened at `ec1390e908a30ab009655dfd6087923c2c9e07f5` so it cannot proceed before deterministic proof artifacts are present.

## Current work NOW
1. Continue polling only for targeted GCP probe2; do not launch another compute job until it resolves.
2. Require effective ATen `DEFAULT`, oneDNN false, same source/normalized/shift and safety invariants.
3. Compare WAV/PCM to probe1 (`0ac47da6...` / `2c22f040...`) and record GCP host vendor/microarchitecture/region.
4. If exact across provider/host diversity, run cross-host checker; only then one manual full-separator smoke. If mismatch, do not spend L4; continue CPU/source isolation only.
5. After separator smoke green, run exactly one combined repaired-timing/precision smoke, then fresh pre-freeze/candidate path.
6. Keep scorer closed until separator + combined path exact and BRAND-NEW Jimmy freeze/PDF locked.

## After determinism is green
Run combined candidate/pre-freeze → new Jimmy analysis/authenticated events/freeze/PDF → fidelity1.0/protected exact/Production unchanged → ONLY THEN scorer V2 at unchanged >=0.99. If failed, broad failure classes only and another fresh freeze.
