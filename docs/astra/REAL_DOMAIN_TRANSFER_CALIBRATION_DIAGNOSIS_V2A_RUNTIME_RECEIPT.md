# V2A Exact-Runtime Reproduction Attempt

Date: 2026-09-28  
Status: **BLOCKED BEFORE MODEL INFERENCE**

The V2 diagnostic design was frozen before this attempt.

Target historical runtime:
- Python 3.10.15
- torch 1.11.0+cpu
- librosa 0.9.1
- numpy 1.21.6
- scipy 1.8.1
- resampy 0.4.3

Observed local runtime:
- Python 3.13.5

Attempts:
1. checked for a local Python 3.10 interpreter — none available;
2. attempted `uv python install 3.10.15` — failed because this sandbox has no outbound DNS/network access;
3. searched the repository for a vendored Python 3.10 runtime or compatible locked wheels — none found.

No candidate model was loaded or run during V2A.
No thresholds, decoder, frontend, gain, checkpoint or candidate were changed.
The sealed V1.1 set was not used for tuning.

A GitHub Actions environment can recreate Python 3.10, but the 24 evaluation audio files are intentionally not stored in the public repository because their source license does not permit standalone redistribution. Therefore the current setup cannot combine the exact historical runtime with the private/local V1.1 audio without introducing a new file-transfer mechanism.

## Decision boundary

V2A is **not scientifically failed**; it is **infrastructure-blocked**.

Two legitimate next paths exist:

1. provide or enable an exact-runtime environment that can access the existing private V1.1 audio; or
2. explicitly open V2B and collect a fresh calibration-development set, leaving V1.1 sealed.

Do not substitute another non-historical runtime rerun and call it V2A.
