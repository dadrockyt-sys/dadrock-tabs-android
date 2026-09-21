# GuitarProFX TabCNN Source / Preprocessing Review V1

Status: source + official artifact + runtime/preprocessing identity review; no checkpoint import or model execution
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

## Reproducibility result

The bundled `setup.py` / requirements only specify lower bounds such as `numpy>=1.21.6`, `librosa>=0.9.1`, and `torch>=1.11.0`. The VQT wrapper itself warns that librosa conventions changed. Astra therefore reconstructed and froze an exact Linux x86-64 / CPython 3.10.15 runtime instead of trusting those lower bounds.

The successful runtime is committed in `astra_backend/tabcnn_runtime/requirements.lock.txt`. Lock SHA-256: **`0e711709b063a705ad11570f6b7ef4dfe5bcc2d433d98707a1a74897dbb25bc0`**. Exact wheel-manifest SHA-256: **`0796acee36cea76e9784e602da190223a14a89907381882b401986763c371567`**.

Two real dependency-drift failures were found before the lock was stable: unpinned Numba 0.58 rejected NumPy 1.21.6, and SoundFile 0.14 used NumPy typing unavailable in 1.21.6. The final compatible runtime pins NumPy 1.21.6, SciPy 1.8.1, librosa 0.9.1, Numba 0.55.2, llvmlite 0.38.1, SoundFile 0.12.1, and PyTorch 1.11.0+cpu, plus exact transitives.

On deterministic synthetic audio, Astra's minimal preprocessing implementation reproduced the exact pinned upstream source with **0.0 maximum absolute difference** for RMS-normalized waveform, 192-bin CQT/VQT features, and final 9-frame model windows. Receipt SHA-256: **`3a9474ccad43f1b06b76bc2e4b836642c355565a1d86a608aed8780a0bf8c333`**. The checkpoint was not loaded and the model was not invoked.

## Official artifact boundary

Official Zenodo record 11406378 publishes:

- file: `best_TabCNN_tablature_trancription_model`
- bytes: 3,345,122
- MD5: `ce168b2cd426f81a2a78499214e40605`
- record license metadata: CC-BY-4.0

Astra downloaded those exact bytes transiently from the official record in a bounded identity workflow, verified the published byte count and MD5, computed SHA-256 **`1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`**, and deleted the temporary file. The model artifact was not committed or persisted.

Third-party ONNX/GGUF conversions are **not** accepted as the primary Astra artifact. They may later serve as deployment candidates only after:

1. the official checkpoint is verified,
2. the exact preprocessing runtime is frozen,
3. output logits/class layout are compared numerically on controlled synthetic audio,
4. string/fret predictions agree under a prospectively defined tolerance.

## Runtime surface

The bundled amt-tools setup is much broader than inference requires. Astra's preprocessing/runtime lock deliberately excludes the research-only Sacred, dataset, evaluation, visualization, MIDI/JAMS and interactive-device stack.

One checkpoint-load issue remains intentionally unresolved: the training code serializes the full model with `torch.save(model, ...)`, and the official inference code performs `torch.load(...)` before copying `loaded_model.state_dict()` into a fresh TabCNN. Therefore a minimal compatibility surface for the legacy `amt_tools` class/module paths must be frozen before the checkpoint can be deserialized safely. That compatibility path has not been executed yet.

## Product role boundary

TabCNN is generic-guitar note/tablature inference. It does not determine whether a guitar is lead or rhythm.

For stereo material, Astra's existing spatial role evidence may select a role-supported channel before TabCNN. For mono/high-correlation/overlapping-guitar material, role evidence must abstain or use a separately validated separator. TabCNN output must never be reinterpreted as role truth.

## Next exact action

Freeze the **minimal legacy pickle-compatibility source surface** required for the official checkpoint's `amt_tools` class paths, without installing the broad training/evaluation environment and without loading the checkpoint yet. In parallel, complete checkpoint-license and training-data commercial-rights review.

Only after artifact identity, exact runtime, preprocessing reproduction, pickle compatibility, rights review and explicit development authorization are frozen may Astra perform a bounded CPU checkpoint-load/forward smoke test and measure wall time/RSS.

Until those remaining fields are complete, `tabcnn_guitarprofx_dafx24` remains `developmentExecutionReady:false` and customer delivery remains false.

No checkpoint was imported/executed; no customer audio was opened; no main/Production change.

## Portable numerical reproduction correction — 2026-09-21

A second GitHub-hosted run reproduced the pinned upstream preprocessing with **zero Astra-vs-source difference**, identical shapes/dtypes/min/max, and identical normalized-audio bytes, but the raw CQT/model-window float byte hashes differed from the earlier runner. This demonstrates least-significant-bit hardware/FFT variability rather than semantic preprocessing drift.

Astra therefore treats raw CQT/model-window SHA-256 values in the original receipt as **diagnostic**, not portable identity. The portable gate now requires the exact frozen runtime/source identities, exact synthetic/normalized waveform identity, exact feature/window shapes and dtypes, stable numeric bounds, and same-run Astra-vs-pinned-source maximum absolute difference <= 1e-7. No model was loaded or executed.
