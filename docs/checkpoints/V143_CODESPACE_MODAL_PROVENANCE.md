# V143 Codespace / Modal provenance lead

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Historical baseline: `4d735846fbd834cc4c722f2cb48727e4629647f1`

## Purpose

Record the newly clarified provenance priority for the remaining V143 separator/runtime archaeology without changing production, retraining, retuning, or launching a new GPU replay.

The historical Modal work was primarily driven from a GitHub Codespace. Repository evidence is consistent with important runtime artifacts having existed only in that Codespace filesystem rather than in committed GitHub Actions artifacts.

## Repository evidence supporting a Codespace-local execution trail

### 1. Historical Modal worker was designed for a local Codespace entrypoint

Archived source:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/v143_ai_tab_gpu_worker.py`

The worker defines a Modal `@app.local_entrypoint()` and expects local repository files before invoking the remote L4 function.

For direct replay it expects:

- source: `public/gomywayfullaitest.m4a`
- historical comparison stem: `public/separator-benchmark-v2/gomyway-demucs6s-direct-guitar.wav`

It then writes the returned Modal WAV locally under:

`public/v143-modal-replay/gomyway-modal-l4-direct-guitar.wav`

This is strong evidence that at least part of the replay/deployment workflow was intended to be initiated from a developer filesystem such as the historical Codespace.

### 2. The expected historical direct stem is not Git-tracked at the historical baseline

The directory:

`public/separator-benchmark-v2/`

is absent at historical commit `4d735846fbd834cc4c722f2cb48727e4629647f1` through the repository contents API.

Therefore the exact historical direct WAV referenced by the Modal worker cannot currently be authenticated from Git history at that baseline. It may have existed only as an untracked/local Codespace artifact or may have been removed before the baseline commit.

The same caution applies to generated GPU benchmark paths referenced by grading code, including:

`public/separator-benchmark-gpu-v1/gomyway-bsroformer-demucs6s-gpu-hq-guitar.wav`

No claim is made here that these files still exist anywhere; only that the historical code expected generated/local artifacts not preserved in the committed baseline.

### 3. The preserved Codespace snapshot is intentionally partial

Preserved snapshot provenance:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/PROVENANCE.txt`

The snapshot states that its source directory was only:

`public/training/v143-musical-reconstruction-calibration`

It therefore preserves the training/calibration evidence copied from the Codespace, but it is not a complete filesystem or environment snapshot.

It does not by itself preserve:

- shell history;
- the Codespace Python environment;
- a complete `pip freeze`;
- home-directory caches;
- Modal CLI/client cache/state;
- downloaded separator model payloads;
- untracked benchmark WAV directories outside the copied source directory;
- ignored `.env` state.

### 4. Historical separator model filenames could be overridden by environment

Archived source:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/v143_production_separator.py`

The historical separator resolves model identifiers through:

- `JIMMY_BS_ROFORMER_MODEL`
- `JIMMY_DEMUCS_6S_MODEL`

with defaults:

- `model_bs_roformer_ep_317_sdr_12.9755.ckpt`
- `htdemucs_6s.yaml`

This means repository source proves the defaults, but a historical Codespace environment override could have altered the actual model identifier used for a run unless the environment state is recovered or otherwise disproven.

### 5. Relevant local state was eligible to remain outside Git

The historical `.gitignore` excludes at least:

- `.cache/`
- `.env`
- `.env.*`
- `*.env`
- Python virtual environments
- logs/debug dependency noise

Those exclusions are normal, but they mean important historical runtime/download context could have existed in the Codespace without ever becoming Git evidence.

## Revised provenance priority

For the unresolved external separator/runtime gate, the evidence priority is now:

1. **Surviving historical Codespace filesystem/state**, if it still exists and can be inspected safely.
2. Git commit/diff history originating from that Codespace.
3. Preserved repository-side Codespace snapshot and archived first-party source.
4. Historical GitHub Actions artifacts/logs as secondary corroboration.
5. Fresh compatibility execution only after the historical evidence search is exhausted, and never labelled bit-exact historical reproduction without authenticated dependency/model closure.

## If the historical Codespace becomes accessible

Inspect read-only first and do not commit secrets. High-value recovery targets include:

- local/untracked `public/separator-benchmark-v2/`;
- local/untracked `public/separator-benchmark-gpu-v1/`;
- local/untracked `public/v143-modal-replay/`;
- shell command history showing `modal run` / `modal deploy` invocations;
- the active Python environment and any retained package metadata;
- audio-separator/model download caches and metadata;
- exact downloaded BS-RoFormer and Demucs payload files for SHA-256 hashing;
- any Modal build/deploy identifiers printed by the CLI;
- environment-variable names/values relevant to model selection, while taking care not to expose or commit credentials.

If model payload files are recovered, hash the bytes before any replay and preserve only non-secret provenance needed for authentication.

## Current gate

No new GPU replay was launched during this investigation.

The existing fail-closed rule remains in force:

- static V143 measures 1–16 producer/feature chain remains proven;
- source audio identity remains proven;
- exact third-party runtime/model byte provenance remains unresolved;
- no fresh execution may be described as a bit-exact historical reproduction until that closure is authenticated.

No production files were changed.
