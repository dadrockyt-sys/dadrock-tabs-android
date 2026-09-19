# Jimmy PAIge Astra — Engine Installation Smoke V1

Status: package installation verified; model execution remains blocked
Date: 2026-09-19 UTC

## Result

The frozen Milestone 6B dependency lock installed successfully into a new temporary Python `3.10.21` virtual environment on x86_64 Linux. All 57 locked distributions were installed from hash-verified artifacts, including a local build of the pinned `demucs==4.0.1` source distribution. `uv pip check` reported that every installed package was compatible.

The canonical installed-distribution snapshot is `astra_backend/engine/installed-distributions.json`:

- distribution count: 57
- SHA-256: `a286ef69bdc34636cf96bd6ee952c517c44ffebe22b73329f0390e6e987ab846`
- exact match against the 57 names and versions in `requirements.lock`: PASS
- `audio-separator` absent: PASS
- TensorFlow absent: PASS
- matched Torch/Torchaudio `2.11.0+cpu`: PASS
- NumPy `1.26.4` and TFLite Runtime `2.14.0`: PASS

## Commands

The temporary environment was created outside the repository. From the repository root, the install and compatibility check were:

```bash
uv venv --python 3.10 /tmp/astra-engine-smoke-W0bAmw/venv
uv pip sync astra_backend/engine/requirements.lock \
  --python /tmp/astra-engine-smoke-W0bAmw/venv/bin/python \
  --torch-backend cpu \
  --require-hashes
uv pip check --python /tmp/astra-engine-smoke-W0bAmw/venv/bin/python
```

The snapshot was produced from Python distribution metadata only. It did not import Demucs, Basic Pitch, Torch, Torchaudio or TFLite.

## Packaged Basic Pitch model

The installed Basic Pitch distribution contains the frozen TFLite artifact at `basic_pitch/saved_models/icassp_2022/nmp.tflite`. It was read as bytes without loading the model:

- size: 204,448 bytes
- Git blob SHA-1: `85a41befdd036e9b365a052b7c704c6810288b95`
- SHA-256: `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`

The Git blob identity matches the frozen Basic Pitch `v0.4.0` upstream artifact.

## Boundary

This smoke test proves dependency installation and exact packaged Basic Pitch model bytes. It did not import either model runtime, download the Demucs weight, open audio or run inference. It establishes no latency, separation, transcription or tablature-quality result.

The Demucs weight remains unverified on Astra and its weight-specific commercial terms remain unresolved. Those conditions continue to block model execution. Basic Pitch model commercial-use review also remains unrecorded.
