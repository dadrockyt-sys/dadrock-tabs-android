# GuitarProFX TabCNN Source / Preprocessing Review V1

Status: static source review; no checkpoint download or model execution
Date: 2026-09-21

## Pinned source

- repository: `robust-guitar-tabs/code`
- revision: `f50309ad06dc734ddae5e3a0eda756fca221e2e7`
- repository license: CC0-1.0
- LICENSE blob: `1625c1793607996fcfc46420e8aa2f3d2b7efd1e`

Relevant source blobs:

- GuitarProFX training script: `3531fb19292f8b6198ab48c311bee1d6b87ff162`
- EGSet12 inference script: `cf59fbc2fd6d274d35ea888eb058cdeb7f69b7ed`
- TabCNN model: `e09856db2fffd77642e005ab509846acc894b886`
- CQT wrapper: `7f08cbd3448765c5406b28f8627a8a8fb66f27b7`
- VQT implementation: `a4e5e7d4958ec64d2d149eb51acdaf936e649b00`
- feature post-processing: `79b71e763bc12d9d8a26d5bcce5b8ff9800bea92`
- audio loading/normalization: `3b7c4acce352009393e1b786935704d259888681`
- package setup: `384bcf677809eac33b30101f0ba1e8d8860c5f19`
- unpinned requirements file: `e9fb103e4c1fe3515a8d35ad287577a37c924792`

## Frozen source semantics

The GuitarProFX script defines the model-facing feature contract:

- sample rate: **22,050 Hz**
- hop length: **512 samples**
- CQT bins: **192**
- bins per octave: **24** (2 bins per semitone)
- default CQT/VQT fmin: **C1**
- CQT gamma: **0**
- input audio is loaded mono through `librosa.load(..., mono=True)`
- default dataset audio normalization is RMS (`audio_norm=-1`)
- CQT magnitude is converted with `librosa.amplitude_to_db(..., ref=np.max)`
- the feature wrapper then assumes the ordinary [-80, 0] dB range and maps it to [0, 1] by `feats / 80 + 1`
- TabCNN frame width is **9 feature frames**
- guitar profile uses **19 frets**
- model output is grouped softmax tablature: one independent classification group per string, with fret/none classes.

The model is therefore substantially different from Basic Pitch: it predicts guitar string/fret state directly rather than a generic unordered MIDI-note list.

The official EGSet12 script loads the model through PyTorch and explicitly maps to CPU when `gpu_id < 0`. A CPU code path exists in source; Astra has not measured its latency or memory.

## Critical reproducibility warning

The source preprocessing semantics are now identity-pinned, but the **runtime preprocessing is not reproducibly frozen yet**.

The bundled `setup.py` / requirements only specify lower bounds such as:

- `numpy>=1.21.6`
- `librosa>=0.9.1`
- `torch>=1.11.0`

The VQT wrapper itself contains a warning that librosa alpha/convention behavior has changed and should be re-verified. Therefore Astra must not claim that “same source parameters” are sufficient to reproduce the released checkpoint. Exact package versions must be reconstructed and numerically checked.

## Official artifact boundary

Official Zenodo record 11406378 publishes:

- file: `best_TabCNN_tablature_trancription_model`
- bytes: 3,345,122
- MD5: `ce168b2cd426f81a2a78499214e40605`
- record license metadata: CC-BY-4.0

Astra has not downloaded those bytes and has not computed SHA-256.

Third-party ONNX/GGUF conversions are **not** accepted as the primary Astra artifact. They may later serve as deployment candidates only after:

1. the official checkpoint is verified,
2. the exact preprocessing runtime is frozen,
3. output logits/class layout are compared numerically on controlled synthetic audio,
4. string/fret predictions agree under a prospectively defined tolerance.

## Runtime surface

The bundled amt-tools setup is much broader than inference requires. It lists training/evaluation/interactive dependencies such as matplotlib, sacred, mir_eval, JAMS, tensorboard, pandas, mirdata, sounddevice and pynput in addition to NumPy/librosa/PyTorch.

Astra should **not** install that full surface blindly. The next runtime milestone should derive a minimal inference-only dependency graph from the pinned files and then freeze it with exact hashes.

## Product role boundary

TabCNN is generic-guitar note/tablature inference. It does not determine whether a guitar is lead or rhythm.

For stereo material, Astra's existing spatial role evidence may select a role-supported channel before TabCNN. For mono/high-correlation/overlapping-guitar material, role evidence must abstain or use a separately validated separator. TabCNN output must never be reinterpreted as role truth.

## Next exact action

Build an **offline preprocessing/runtime preflight contract** that pins these source blobs and requires:

- exact 22.05 kHz mono/RMS-normalized input semantics,
- exact CQT parameters,
- exact dB/[0,1] transform,
- exact 9-frame model window,
- 19-fret guitar profile,
- official checkpoint MD5 + locally computed SHA-256,
- exact dependency lock,
- CPU smoke/runtime result,
- training/data rights review.

Until all fields are complete, `tabcnn_guitarprofx_dafx24` remains `developmentExecutionReady:false`.

No model was downloaded/imported/executed; no audio was opened; no main/Production change.
