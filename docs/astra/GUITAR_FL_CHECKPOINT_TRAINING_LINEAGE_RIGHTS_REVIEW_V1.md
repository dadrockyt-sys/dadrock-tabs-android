# Guitar-FL checkpoint training-lineage rights review V1

Date: 2026-10-06
Branch: `astra-work`
Status: **PRODUCT USE BLOCKED / INTERNAL TECHNICAL EVALUATION MAY CONTINUE**

## Question

Does the public licensing record establish sufficient rights to use the frozen `guitar-fl.pth` checkpoint in a commercial/customer-facing DadRock product?

## Evidence reviewed

### Checkpoint/model repository

The public `xavriley/midi-transcription-models` repository labels the model collection MIT. The exact frozen checkpoint `guitar-fl.pth` is publicly distributed there and retains the frozen SHA-256:

`50d93dba89bdd3401849bc735614478e83d9f46d21fa3f71d8aca5acc0a52028`.

This is strong evidence that the checkpoint artifact itself is intentionally published under the repository's MIT-labeled package.

### Newer François Leduc dataset package

The current Hugging Face dataset `xavriley/FrancoisLeducGuitarDataset` labels the dataset MIT and says it contains 79 solo-guitar audio/aligned-MIDI performances used to train the guitar transcription model.

### Original authoritative dataset record

The original Zenodo record remains explicit:

- dataset status: restricted;
- made available by request for research projects;
- original scores could not be distributed for copyright reasons;
- non-research applications require separate permission from the original copyright holder, François Leduc.

The Zenodo record now points users to the newer Hugging Face package, but the reviewed public materials do not contain a clear statement that the earlier non-research restriction / underlying score and recording rights were affirmatively relicensed or superseded for commercial product use.

## Decision

**Do not treat the MIT labels alone as sufficient commercial/product-rights clearance for DadRock Production use of `guitar-fl.pth`.**

Reason:

1. The checkpoint/model repository is MIT-labeled.
2. The newer dataset package is MIT-labeled.
3. The original authoritative dataset record expressly restricted non-research use absent separate rights-holder permission.
4. No reviewed public record explicitly reconciles that conflict or grants commercial-product rights to all underlying training substrates.

The conservative product-rights interpretation is therefore:

- internal research / technical feasibility work: **may continue under the project's existing development boundary**;
- shipping/customer-facing checkpoint use: **BLOCKED**;
- commercial product integration: **BLOCKED**;
- redistribution of underlying FLGD media/scores: **BLOCKED unless independently licensed**.

## Clearance path

Before any Production adoption, obtain an authoritative written clarification covering the exact checkpoint lineage and commercial/product use. The clarification should establish at minimum:

- whether `guitar-fl.pth` may be used in a commercial software product;
- whether its training on François-Leduc-derived material creates any restriction beyond the MIT checkpoint label;
- whether any underlying score/audio rightsholder permission is required for model deployment;
- whether model-weight redistribution is allowed;
- whether inference-as-a-service is allowed;
- whether attribution obligations apply.

The preferred authority is the checkpoint/dataset authors and, if they cannot grant the underlying rights, François Leduc / applicable recording or score rightsholders.

## Boundary

This review does not invalidate the successful feasibility or Stage-A results.

It only preserves the existing rule:

> technical validation may proceed, but no Production/customer promotion of `guitar-fl.pth` until the lineage conflict is affirmatively resolved.

No outreach is sent by this review.
