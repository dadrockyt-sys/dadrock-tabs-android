# Jimmy PAIge Astra — Direct Demucs CPU Runtime Lock V1

Status: dependency resolution complete; installation/model execution not performed
Date: 2026-09-19 UTC

## Decision

Use the official `demucs==4.0.1` CLI directly for the first bounded CPU development candidate, followed by `basic-pitch==0.4.0`. Do not route this candidate through `audio-separator==0.30.2`.

The tagged `audio-separator` source does not declare the official `demucs` package as a dependency. It carries its own Demucs architecture and also requires a broad ONNX-oriented stack. The direct official CLI already loads `htdemucs_6s`, downloads the exact model named by the official repository, verifies the filename checksum prefix and emits the six sources Astra needs. Removing the wrapper reduces the runtime surface and makes the model source easier to audit.

This replaces the wrapper portion of the Milestone 4 recommendation. It does not change the quality claim: bass is a direct stem candidate; guitar is still generic and cannot establish lead versus rhythm.

## Frozen target

- Python: `3.10`
- platform: `x86_64-manylinux_2_28`
- device/backend: CPU
- separator: `demucs==4.0.1`, direct CLI, `htdemucs_6s`
- transcription: `basic-pitch==0.4.0`, TFLite runtime
- resolver cutoff: packages uploaded no later than `2026-09-19T00:00:00Z`
- complete resolved package count: 57
- lock: `astra_backend/engine/requirements.lock`
- lock SHA-256: `a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7`

Critical compatibility pins:

- `numpy==1.26.4`
- `tflite-runtime==2.14.0`
- `torch==2.11.0+cpu`
- `torchaudio==2.11.0+cpu`

Torch and Torchaudio are deliberately the same release. NumPy remains on the 1.x ABI because the archived Basic Pitch attempt demonstrated that TFLite 2.14 could not initialize against NumPy 2.2.6.

## Resolution command

Run from `astra_backend/engine/`:

```bash
uv pip compile requirements.in \
  --constraints constraints.txt \
  --python-version 3.10 \
  --python-platform x86_64-manylinux_2_28 \
  --torch-backend cpu \
  --generate-hashes \
  --exclude-newer 2026-09-19T00:00:00Z \
  --no-header \
  -o requirements.lock
```

Two consecutive resolutions produced byte-identical lock files and the same SHA-256. Every resolved package declares at least one artifact hash.

## Failed preflight retained as evidence

The first binary-only resolution failed because `demucs==4.0.1` has no usable wheel for the target. A deployment must allow the pinned Demucs source distribution to build, or produce and verify an internal wheel before installation.

The first unconstrained resolution also selected incompatible risk points:

- `torch==2.14.0+cpu` with `torchaudio==2.11.0+cpu`;
- `numpy==2.2.6` with `tflite-runtime==2.14.0`.

Those values were rejected before installation. The checked-in constraints prevent their return.

## Evidence boundary

Dependency resolution and deterministic lock reproduction are complete. Installation remains unverified because no environment was created and no packages were installed. No weight was downloaded, no audio was opened and neither Demucs nor Basic Pitch was imported or executed.

The exact Demucs weight terms remain unresolved. The official repository connects `htdemucs_6s.yaml` to `5c90dfd2-34c22ccb.th` under `https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/` and verifies the filename's checksum prefix, but no separate weight-specific license statement was found in the reviewed official source. The project-level MIT statement is recorded as evidence and is not being promoted into weight-specific commercial clearance.
