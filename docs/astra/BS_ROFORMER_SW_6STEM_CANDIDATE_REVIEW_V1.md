# BS-Roformer-SW 6-Stem Candidate Review V1

Date: 2026-10-02
Status: **TECHNICALLY FROZEN / RIGHTS-BLOCKED**

## Why this candidate

BS-Roformer-SW exposes exactly the six stems needed by the current architecture:

1. bass
2. drums
3. other
4. vocals
5. guitar
6. piano

The ONNX export has a precise, reproducible I/O contract:
- 44.1 kHz stereo
- STFT n_fft 2048
- hop 512
- win length 2048
- 4 s / 176400-sample fixed chunks
- 25% overlap is the published browser-pipeline convention

## Frozen identities

Original rehost:
- repository: `jarredou/BS-ROFO-SW-Fixed`
- checkpoint revision: `ad54168acf271482ad51702953e162a385b8fdcb`
- original checkpoint SHA-256: `24e7d35ee9c64415673d3fd33e06a67cac2c103c5df6267ba1576459c775916e`
- size: 699,412,152 bytes
- published model-card license: **unknown**

ONNX export:
- repository: `elicwhite/bs-roformer-sw-6stem-onnx`
- export revision: `a744f80957374e1735ad70fa122670b7961da8cc`
- FP16 SHA-256: `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`
- FP32 SHA-256: `224f5f54a7ff9ff0e487aabca0a365d94513d51a6cdb7778152f2371716f2b68`
- export repository/model card declares MIT for the export/code lineage

## Rights conclusion

Do **not** treat the ONNX MIT label as resolving the original pretrained-weight rights.

The ONNX model card itself states that the pretrained weights were rehosted without a stated license and that the rehost owner did not have provenance information.

Therefore:
- code/export pipeline: technically usable under their stated MIT licenses;
- pretrained weights: **rights unresolved**;
- empirical run: blocked;
- production/commercial use: blocked.

No model was downloaded.

## Adapter

Prepared:
`astra_backend/evaluation/bs_roformer_sw_6stem_adapter_v1.py`

It freezes:
- exact stem order;
- sample rate/chunk/STFT parameters;
- upstream and export revisions;
- original and ONNX SHA-256 values.

The adapter is deliberately fail-closed.

## Next separator action

Either:
1. obtain explicit enough pretrained-weight rights/provenance for this checkpoint; or
2. reject it and select a different separator whose model-weight license is explicit.

Until then, keep the already-built S0 mixture fixture and bleed-cleanup evaluator unchanged.
