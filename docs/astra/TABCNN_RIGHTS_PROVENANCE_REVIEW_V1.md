# TabCNN GuitarProFX Rights / Provenance Review V1

Status: **review complete; commercial training-lineage clearance unresolved; model execution remains unauthorized**
Date: 2026-09-21
Candidate: `tabcnn_guitarprofx_dafx24`

This is a technical provenance gate, not legal advice. It records what the upstream sources actually say and keeps Astra fail-closed where those sources do not establish a clear commercial chain.

## Reviewed evidence

### Released code and checkpoint

- The pinned `robust-guitar-tabs/code` repository at revision `f50309ad06dc734ddae5e3a0eda756fca221e2e7` carries CC0-1.0 for the repository work.
- Zenodo record 11406378 publishes `best_TabCNN_tablature_trancription_model` and labels the record CC-BY-4.0. Astra independently verified the exact deposited bytes: 3,345,122 bytes; MD5 `ce168b2cd426f81a2a78499214e40605`; SHA-256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`.
- The DAFx-24 paper itself is distributed under CC-BY-4.0.

These facts support the identity and published license metadata of the released code/checkpoint. They do **not** by themselves establish that every underlying training-data right needed for a paid downstream product has been cleared.

## Training lineage identified from the paper

The DAFx-24 paper states that:

1. TabCNN is trained with GuitarSet as the base training/cross-validation dataset.
2. The GuitarProFX model adds all synthetic GuitarProFX tracks to the training split.
3. GuitarProFX contains 360 randomly chosen solo-performance tracks from DadaGP.
4. The synthetic tone pool includes EGFxSet clean/effected single-guitar tones plus additional clean notes recorded by the paper authors.

Therefore the published GuitarProFX checkpoint is not a code-only artifact. Its training lineage includes at least GuitarSet, DadaGP-derived symbolic performances, EGFxSet tones, and author-recorded tones.

## Commercial-lineage findings

### DadaGP — unresolved / blocking

- The DadaGP software repository is MIT-licensed.
- The same repository explicitly says the **dataset** must be requested from the authors **for research purposes**.
- The DAFx-24 paper says GuitarProFX used 360 randomly selected DadaGP solo-performance tracks.
- The software MIT license must not be treated as a commercial license for the separate GuitarPro dataset.

Result: **commercial training-lineage clearance is not established** for DadaGP-derived material. This is a hard blocker for treating the released checkpoint as cleared for a paid customer-delivery path.

### GuitarSet — conflicting public metadata / blocking

- The canonical Zenodo distribution is open and links the MARL repository, but the current Zenodo UI captured in this review does not render a concrete license value.
- The MARL GitHub repository has an MIT license, but that license is phrased for software and must not automatically be applied to the separately distributed audio dataset.
- OpenAIRE/DataCite indexing currently reports GuitarSet as **CC BY-NC**, while newer third-party mirrors label it **CC BY 4.0**.

Result: the authoritative dataset license must be reconciled from the original licensor/record before commercial clearance. Astra must not select the more permissive third-party interpretation by convenience.

### EGFxSet — attribution-friendly publication, dataset metadata still needs authoritative confirmation

- The EGFxSet publication is CC-BY-4.0.
- Public mirrors and later users describe EGFxSet as CC-BY-4.0, while other catalog metadata has reported different Creative Commons variants.
- The captured Zenodo page does not render the license value clearly enough to resolve the discrepancy by itself.

Result: keep EGFxSet dataset rights as **needs authoritative confirmation**. This is secondary to the already-blocking DadaGP lineage but should still be resolved before commercial clearance.

## Gate decision

- `checkpointLicenseReviewed`: **reviewed**, because the released checkpoint record has explicit CC-BY-4.0 metadata.
- `trainingDataCommercialRightsReviewed`: **reviewed**, in the literal sense that the chain has been investigated.
- `trainingDataCommercialRightsCleared`: **false / unresolved**.
- `developmentUseAuthorized`: **false** for any checkpoint import, deserialization, forward pass, Gomyway evaluation, customer-facing use, or paid-product integration until the project owner has a documented basis for development use.
- Customer delivery remains **false** regardless.

Static byte hashing, archive listing, and pickle-opcode inspection are permitted because they do not import, deserialize, or execute the model.

## Required evidence to clear the blocker

At least one defensible path must be documented before model execution:

1. written permission / license clarification from the GuitarProFX checkpoint authors covering development and intended commercial use of the released weights despite the DadaGP/GuitarSet lineage; **or**
2. authoritative license evidence for every training substrate showing the intended use is permitted; **or**
3. replace this candidate with a checkpoint whose code, weights, and training lineage are already commercially clear.

Do not reinterpret a model-card/record license as a warranty that third-party training inputs were cleared. No main/Production change.
