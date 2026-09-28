# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.  
Updated: 2026-09-27.

## Current position

The authoritative offline review task is complete.

Created:

- `docs/astra/EVALUATION_PROTOCOL_AUDIT_V1.md`
- `astra_backend/evaluation/evaluation_protocol_v2.py`
- `astra_backend/evaluation/test_evaluation_protocol_v2.py`
- `docs/astra/SYNTHETIC_DATA_DIVERSITY_S0_V1.md`

Focused fabricated-event verification: **7/7 tests passed** locally.

Main audit findings:

- frozen Basic Pitch / MR-MT3 crop predictions and prepared references do not use symmetric boundary eligibility;
- frozen greedy matching can undercount true positives;
- onset and offset same-pitch ambiguity need separate policies;
- future runners need one frozen manifest binding all crop/source/feature/target identities;
- MR-MT3 still fails under the frozen program contract; this audit does not prove why its programs were incompatible and does not authorize a remap.

Historical receipts remain frozen.

## S0 design

Recommended synthetic hypothesis: repo-owned Karplus-Strong / short digital-waveguide guitar generator with no external sample/IR assets.

Hard future pilot ceiling:

- <= 3,000 examples / <= 6,000 s audio / <= 350 MB;
- one 5-frame temporal-context MLP candidate versus the current per-frame MLP comparator;
- <= 500 optimizer steps each, two models total, <= 60 CPU minutes, $0 paid compute;
- fixed seed and thresholds, zero retries;
- no P1/P2 media during synthetic pilot;
- P3 sealed.

## Exact next action

**STOP until Stephen explicitly authorizes the bounded synthetic-only S0 pilot.**

Do not create a launch, render the corpus, run optimizer steps, reopen P1/P2, alter thresholds, open P3, deploy, or change main without that authorization.

If the synthetic pilot is later authorized and passes its frozen synthetic gates, real P1/P2 transfer still requires its own separate scoped authorization and a V2 manifest/runner.
