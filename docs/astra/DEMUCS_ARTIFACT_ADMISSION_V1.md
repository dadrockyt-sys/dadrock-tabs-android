# Jimmy PAIge Astra — Demucs Artifact Admission V1

Status: offline admission gate complete; rights decision and local artifact absent
Date: 2026-09-19 UTC

## Frozen artifact

The Astra Demucs candidate recognizes only this artifact:

- candidate: `htdemucs6s-basic-pitch`
- model: `htdemucs_6s`
- filename: `5c90dfd2-34c22ccb.th`
- official source: `https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/5c90dfd2-34c22ccb.th`
- expected SHA-256: `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`

The expected digest is a preserved historical observation. It is the admission target, not a claim that Astra has downloaded or verified the bytes.

`astra_backend/demucsArtifactAdmission.mjs` rejects a different candidate, model name, filename, source URL or digest. It performs no file access, download, import, inference, audio processing or network access.

## Required external rights decision

The official Demucs `v4.0.1` repository carries an MIT license and maps `htdemucs_6s` to the Meta-hosted artifact above. The reviewed official repository does not state a separate license for that exact weight. Astra therefore does not infer commercial weight permission from the software license alone.

Before downloading or executing the weight, the project needs one owner-approved rights-review record that:

1. identifies the exact filename and SHA-256 above;
2. cites the authoritative terms or permission relied upon;
3. states whether `development-quality-evaluation` is permitted;
4. states whether `commercial-customer-inference` for paid tablature is permitted;
5. names the reviewer and records the review date; and
6. records any attribution, notice, redistribution, data or output restrictions.

The finalized record must be committed, its SHA-256 frozen into the admission contract and the corresponding manifest rights fields updated. A chat statement, the repository's software-license label or possession of the file cannot clear this gate.

If authoritative terms cannot support both required uses, the candidate must remain blocked. The next practical path is a separation model with explicit model-artifact terms or a separately licensed/trained replacement.

## Current blockers

- `DEMUCS_WEIGHT_BYTES_NOT_OBSERVED_ON_ASTRA`
- `DEMUCS_WEIGHT_RIGHTS_DECISION_NOT_FROZEN`

Even after artifact admission, customer delivery remains false until runtime, musical quality, development-material authorization, lead/rhythm handling and the full delivery policy are separately validated.
