# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S8 FAILED; OFFLINE REVIEW COMPLETE; S9 CHORD-VOICING DIVERSITY HYPOTHESIS FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized. Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical S8 result

- run **36378097322**
- job **108787949275**
- launch head `7fbefd629c4827818cd79cd86e6819f1471c4639`
- workflow **SUCCESS**
- artifact **10951214111**
- artifact digest `sha256:f4291e10aa04a29c68f9a7455cf5e20a53f568cdbcd4a5e7d25bb2beb895a5ab`
- focused tests **4/4 passed**
- optimizer 500 + 500
- no threshold search/retry/P1/P2/P3/Codespaces/Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S8_RESULT_V1.json`

Uniform -> token-balanced:
- mean selected positive strings/frame **1.2289 -> 1.5570**
- chord F1 **0.3077 -> 0.2667**
- chord recall **0.2222 -> 0.1667**
- state admission **0.4109 -> 0.3798**
- joint admission **0.3566 -> 0.3411**
- overall recall **0.6279 -> 0.6047**
- overall F1 **0.7105 -> 0.7256**
- precision **0.8182 -> 0.9070**
- repeated recall **0.5952 -> 0.6905**

S8 gate **FAILED (6/15 passed)**.

## Offline S8 review

Increasing repeats of existing multi-string attack frames did not improve chord generalization.

The control training set has 30 chord clips but only **10 unique chord voicings**, each repeated across three timbres.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S8_FAILURE_ANALYSIS_V1.md`

## Frozen S9 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S9_DESIGN_V1.md`

S9 keeps exactly 30 chord training clips in each arm:

1. control = 10 unique voicings x 3 timbre variants;
2. intervention = 30 unique voicings, with the same 30 paired timbre RNG keys.

Validation/test and every non-chord example must be bit-identical.

Both arms use the S6 nonlinear state head, original uniform 32/32/32/32 sampler, state weight 9, onset weight 8, identical model initialization and identical minibatch indices.

## Exact next step

**Do not execute S9 yet.**

Fresh explicit model authorization is required.

No P1/P2/P3, Codespaces, Vercel, threshold rescue, deployment or main mutation.
