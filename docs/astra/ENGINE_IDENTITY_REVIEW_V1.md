# Jimmy PAIge Astra — Engine Identity Review V1

Status: static identity review; execution remains blocked
Date: 2026-09-19 UTC

## Result

The first Astra development candidate now has a machine-readable manifest with exact identities for every upstream source artifact that could be verified without downloading or executing a model. The manifest is intentionally not execution-ready.

Verified source identities:

- `audio-separator` tag `v0.30.2` -> commit `99840eea955a19305413639c21ee58e320a1fd14`;
- official Meta Demucs tag `v4.0.1` -> commit `ef66d254cd6d558e207eeff2c4b8d053db2e77dd`;
- Demucs `htdemucs_6s.yaml` -> Git blob `651a0fa536038a3e6d650f7b2bcc0b50ff7a4be9`, selecting weight file `5c90dfd2-34c22ccb.th`;
- Basic Pitch tag `v0.4.0` -> commit `9991303bba609a3b93089d13ec80d1d495083596`;
- Basic Pitch TFLite model -> Git blob `85a41befdd036e9b365a052b7c704c6810288b95`, 204448 bytes.

The archived Fresh authority manifest recorded SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411` for the Demucs asset. Astra preserves that value as a historical observation only. It must be checked against the exact downloaded asset before execution.

## Correction from the archive

The archived authority manifest claimed `demucs==4.1.0` and `torch==2.14.0`. The official Meta Demucs repository currently exposes `v4.0.0` and `v4.0.1` tags, not `v4.1.0`. Astra therefore does not inherit that package set. It pins the official `v4.0.1` source identity and leaves the complete install lock unresolved until it can be generated and reviewed on the intended execution surface.

This is exactly why archived manifests are evidence rather than authority for the new line.

## Rights boundary

The tagged software repositories publish MIT licenses for `audio-separator` and Demucs and Apache-2.0 for Basic Pitch. The Basic Pitch model is stored in the tagged licensed repository, but commercial-use review is not recorded yet. The separately downloaded Demucs weight has no weight-specific terms captured by Astra. Both remain explicit blockers; this document is not legal clearance.

## Remaining blockers

- generate an exact complete Python distribution lock and artifact digest on the intended CPU environment;
- download nothing until the Demucs weight source and applicable terms are reviewed;
- verify the Demucs weight SHA-256 and Basic Pitch model identity inside the Astra execution environment;
- identify authorized development audio and keep it separate from any future locked evaluation;
- measure the 1200-second/4096-MB service target;
- solve lead-versus-rhythm evidence independently; the generic guitar stem cannot do this.

`astra_backend/engineExecutionManifest.mjs` rejects identity substitutions and reports these blockers without opening audio, invoking a model or accessing the network.
