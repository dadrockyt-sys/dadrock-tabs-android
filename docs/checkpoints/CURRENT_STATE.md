# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 00:35 America/Thunder_Bay
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
Billing screenshot: L4 `$11.92`, memory `$1.40`, CPU `$1.09`, total `$14.41`. Free/static first; one diagnostic at a time; no repeated 3-pass L4 debugging; final multi-pass L4 only after deterministic fix. Scorer remains closed. Expensive workflows manual-only except a single one-shot gate when explicitly recorded here.

## Prior failed execution candidates
RNG ruled out: exact shift `0,22050,6026` throughout. Unpinned output mapped to host/ISA; common AVX2 failed cross-vendor; ATen DEFAULT + oneDNN SSE41 failed even across AMD microarchitectures. Do not spend L4 on those candidates.

## oneDNN-OFF candidate — CROSS-CLOUD / CROSS-VENDOR BYTE-EXACT
Research-only Demucs child sets `torch.backends.mkldnn.enabled=False` before audio-separator/model import while keeping ATen `DEFAULT`, oneMKL `COMPATIBLE`, one thread/dynamic false, private shift seed, model/shifts1/overlap0.10/segment6 unchanged. No Production/protected/scorer file changed.

Probe1 `debug/v143-contextual-prune/demucs-cpu-nomkldnn-probe-1.json`, bot commit `34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`:
- AWS `us-east-2`, `GenuineIntel` family6/model85, physical AVX512
- effective child `torchCpuCapability=DEFAULT`, `mkldnnEnabled=false`, threads1/inter-op1
- source `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- normalized `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
- shift `0,22050,6026`
- WAV `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
- PCM `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`
- safety/reference-free invariants green.

Probe2 `debug/v143-contextual-prune/demucs-cpu-nomkldnn-probe-2.json`:
- GCP `us-east5`, `AuthenticAMD` family175/model1, AVX2
- effective child `torchCpuCapability=DEFAULT`, `mkldnnEnabled=false`, threads1/inter-op1
- source/normalized/shift **exactly match probe1**
- WAV **exactly matches probe1** `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
- PCM **exactly matches probe1** `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`
- safety/reference-free invariants green.

This is the first successful diverse-host exactness proof: AWS Intel ↔ GCP AMD, same source/normalized bytes, same deliberate shift, same effective baseline CPU controls, same WAV and decoded PCM. The configured cross-host checker conditions are satisfied.

## Current work NOW
1. Run the cross-host checker again inside the free preflight of the next gate.
2. Launch **exactly one** full-separator single-pass smoke; this is the first allowed L4 bridge run after the deterministic fix. No 3-pass proof yet.
3. If separator smoke is green, run exactly one combined repaired-timing/precision smoke.
4. Then run the prepared candidate/pre-freeze path and create a BRAND-NEW Jimmy analysis/authenticated events/freeze/PDF identity.
5. Verify PDF-event fidelity1.0, protected exact, Production unchanged.
6. ONLY THEN reopen scorer V2 and score at unchanged >=0.99 threshold.

## Prepared continuation
- `.github/workflows/v143-separator-single-pass-smoke.yml` — one full graph pass only.
- `.github/workflows/v143-repaired-timing-precision-single-pass-smoke.yml` — one combined pass only; requires separator smoke file.
- candidate product workflow hardened at `ec1390e908a30ab009655dfd6087923c2c9e07f5` to require deterministic proof artifacts.
- Final multi-pass L4 proof remains last determinism gate, not a debugging loop.
