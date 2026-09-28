# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **S7 FAILED; OFFLINE REVIEW COMPLETE; S8 TOKEN-BALANCED POSITIVE-FRAME SAMPLING FROZEN — MODEL EXECUTION NOT AUTHORIZED; P1/P2/P3 SEALED**

## Standing authorization policy

Routine GitHub-only code/tests/docs/metadata work is pre-authorized. Explicit approval is required for model execution, Codespaces, and potentially billable Vercel operations.

## Canonical S7 result

- run **36377220039**
- job **108785403550**
- launch head `87e6f2c3fd2f658ff34ae3357ea74412257a7a47`
- workflow **SUCCESS**
- artifact **10951013712**
- artifact digest `sha256:c39c2789814d8b1b2dc0f8198e7dbc360900ff5344b01c9e862547258ea942f3`
- identity tests **3/3 passed**
- 294 clips / 588 s
- optimizer 500 + 500
- no threshold search/retry/P1/P2/P3/Codespaces/Vercel

Frozen result:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S7_RESULT_V1.json`

Control -> residual:
- state admission **0.3256 -> 0.2946**
- joint admission **0.3178 -> 0.2868**
- onset recall **0.5969 -> 0.5969**
- onset F1 **0.7230 -> 0.7130**
- repeated recall **0.5714 -> 0.5952**
- chord F1 **0.3830 -> 0.3404**
- residual norm after training **17.6719**

S7 gate **FAILED (6/15 criteria passed)**. The residual learned but harmed the state bottleneck.

## Offline S7 review

Persistent chord/polyphonic weakness is now the strongest bounded sampling hypothesis.

Train positive frames/tokens:
- total positive onset frames **525**
- positive string-onset tokens **645**
- chord positive frames **60 = 11.43%**
- chord positive tokens **180 = 27.91%**

Current sampling is uniform over positive frames, not positive string tokens.

Analysis:
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S7_FAILURE_ANALYSIS_V1.md`

## Frozen S8 design

- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S8_DESIGN_V1.md`

Both arms fix the S6 nonlinear replacement state head and all S5/S6 loss/threshold settings.

Only positive-onset-frame sampling changes:
1. control = uniform positive-frame sampling;
2. intervention = sampling probability proportional to number of positive onset strings in that frame.

The other 96 frame positions in every paired minibatch must be identical.

## Exact next step

**Do not execute S8 yet.**

Fresh explicit model authorization is required.

No P1/P2/P3, Codespaces, Vercel, threshold rescue, deployment or main mutation.
