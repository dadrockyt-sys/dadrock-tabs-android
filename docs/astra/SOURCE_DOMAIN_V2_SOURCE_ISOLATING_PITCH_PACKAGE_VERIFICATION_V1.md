# Astra V2 source-isolating pitch diagnostic package verification V1

Date: 2026-09-28
Status: **OFFLINE PACKAGE VERIFIED — DISABLED / NON-AUTO-RUNNING**

Verified files:
- `astra_backend/synthetic/source_domain_v2_source_isolating_pitch_v1.py`
- `astra_backend/synthetic/test_source_domain_v2_source_isolating_pitch_v1.py`
- `.github/workflows/astra-source-domain-v2-source-isolating-pitch-v1.yml`

Git blobs:
- runner `b0dc62ffe99ed0d03c6a82f3cd7a68306d130e7b`
- tests `7e30524e454bd3db947cfea03d407d0cd7d95809`
- workflow `1a030b131705d24da7e2c1e240835523e6a6b0a5`

Static safety:
- workflow trigger: `workflow_dispatch` only;
- no push / PR / schedule / workflow-run trigger;
- only job hard-disabled by `if: ${{ false }}`;
- no source-isolating diagnostic check run appeared after the package commit.

Frozen inputs pinned:
- V1 preparation run 36475263654;
- S9 control SHA-256 `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`;
- V2 manifest run 36481373445;
- manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`;
- failed Stage-A run 36484128430;
- Stage-A result SHA-256 `5778104fe505f5a38b4e2a0ed3e049a9993db92a9a1a3a078851c6cb7df8e0c2`.

No waveform execution occurred during package verification.

Decision: package is safe to arm as one separately versioned, single-use synthetic/model-free diagnostic attempt.
