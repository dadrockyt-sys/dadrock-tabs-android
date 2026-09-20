# Oracle Basic Pitch transcription preregistration V1

This contract is frozen before any Basic Pitch prediction on the guitar-only oracle exists. Its purpose is to separate a genuine isolation/transcription experiment from post-hoc alignment or threshold tuning.

The exact oracle is the first 30 seconds of the existing guitar-only development asset (WAV SHA256 `e294d78c8c0f853861ab5bb1effed2dd54799bfb308ef48e036c144dfaec71d6`). The reviewed score remains on the canonical source clock (SHA256 `60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb`). The independently established audio relation is fixed as `isolated = 0.5229997583867022 + 1.010758763429986 * source`; it must not be refit after oracle predictions are visible.

The inference identity is also frozen: Python 3.10.21, the committed hashed requirements lock, Basic Pitch 0.4.0, packaged model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`, runner blob `95950c50e00777ba3c0398b917f95dcece70065c`, and the same onset/frame/note-length/frequency/pitch-bend/Melodia settings as the whole-mix first30 baseline.

Once the exact runtime is restored, run the existing `run_basic_pitch_development.py` on the verified oracle WAV. Do not modify its output. Then run:

```sh
python astra_backend/evaluation/project_oracle_predictions.py \
  --prediction /private/GOMYWAY_ORACLE_BASIC_PITCH_NATIVE_V1.json \
  --preregistration docs/astra/GOMYWAY_ORACLE_TRANSCRIPTION_PREREGISTRATION_V1.json \
  --output /private/GOMYWAY_ORACLE_BASIC_PITCH_SOURCE_CLOCK_V1.json
```

The projection validates every frozen identity and uses only `source=(isolated-offset)/scale`. It does not alter MIDI, infer role, retune alignment, optimize against matches or grant customer delivery. Events projected before source time zero are dropped rather than clipped because the onset scorer rejects negative timestamps.

The active workspace currently lacks the exact frozen runtime and has no usable cached Basic Pitch/TFLite/Python3.10 environment. Package/runtime restoration is blocked by current download/DNS availability. This is an execution blocker, not permission to substitute an unpinned environment.
