# S0 Synthetic Mixture Fixture V1

Generated on 2026-10-02 from the user's cataloged Pixabay guitar, bass and control uploads.

## Result

- 12 deterministic mixtures
- 94.602 seconds total
- 44.1 kHz stereo PCM float32
- fixed -6 dB global headroom applied to every rendered component
- component-relative gains frozen in the manifest
- exact rendered mix hashes frozen
- maximum observed absolute sample peak: 0.644333
- clipping observed: no
- numerical mixture reconstruction from rendered component stems: exact in verification pass (maximum absolute error 0.0)

The generated WAV files remain outside Git. Only the deterministic generator, manifest and verification record are committed.

## Purpose

This is exact-component ground truth for testing future separator bleed and cleanup behavior.

It is suitable for questions such as:
- how much target energy is preserved?
- how much known bass leaks into guitar and vice versa?
- how much drum/speech interference remains?
- does a cleanup stage improve separation without deleting target content?

It is not evidence of commercial-song separation quality.

## Execution boundary

Mixture generation has been performed and verified.

No separator, recognizer, Basic Pitch model, training job or tab decoder was run.
