# Songsterr Fresh — Synthetic Six-Channel Crosstalk / Debleed Result V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN RESULT — SYNTHETIC SOFTWARE FEASIBILITY ONLY

## Authority and preregistration

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_SYNTHETIC_SIX_CHANNEL_CROSSTALK_DEBLEED_PREREGISTRATION_V1_2026-09-14.md`

Preregistration commit:
`54802e0eda32f8cb65da39ea2bce70c443d16eab`

The method was frozen before official harness-result execution.

## Implementation and CI identity

Implementation:
`scripts/songsterr-fresh/synthetic_six_channel_debleed_v1.py`
blob `a41dbe3131167f09e748a15843143ecfe1e57d8c`
commit `a3d26f1bd399c915466f39ed86529810dabd613d`.

Synthetic contract tests:
`scripts/songsterr-fresh/test_synthetic_six_channel_debleed_v1.py`
blob `55f61041e97c42738865b47d6b614ba829f7455c`
commit `a9626d0e409fca43110516ad9fdc695f1badc64c`.

Workflow:
`.github/workflows/songsterr-fresh-synthetic-six-channel-debleed-v1.yml`
blob `404c53970806eda15a3757192ae5712ae68c6deb`.

Workflow head:
`39f5b2cef2141f7df5377d4ce24ecabebe617011`.

GitHub Actions:
- run ID `34915944228`;
- job ID `104213442029`;
- conclusion `success`;
- 16/16 synthetic contract tests passed before official harness execution;
- official harness result step succeeded;
- summary step succeeded;
- artifact upload succeeded.

Artifact:
- artifact ID `10376620438`;
- artifact name `songsterr-fresh-synthetic-six-channel-debleed-v1`;
- artifact size `9793` bytes;
- uploaded ZIP SHA-256 `53064b9521177251f7e5bb17f672927d8cf7be173fd4a67effa5dd81f7f39b6b`.

Canonical result JSON SHA-256:
`ece7a4525be33329b4f26d05b145f478179d22b1d0472865fd77bc44c05a5a0c`.

## Frozen synthetic identities

NumPy: `2.1.3`.

Source bank:
- exactly 6 channels;
- exactly 8,192 samples/channel;
- SHA-256 `8bceb544b681a5b8a507bb7c70aa0f2f379ceec42f2b7b5bf08643e089f2196c`.

Perturbation bank:
- exactly 6 channels;
- exactly 8,192 samples/channel;
- SHA-256 `9f6e18edb69aeb8d0d68dcc8c2040f4725339f94ef3f73d1c86aa6cda777da51`.

Matrix cases: 13.
Total matrix/perturbation runs: 52.
All result values finite: true.

## Main result — known matrix, no perturbation

For every nonzero bleed matrix, direct `solve(M,Y)` recovered the untouched synthetic source bank to float64 numerical precision when `sigma=0`.

Representative cases:
- `distance_decay`, bleed `0.50`, condition `1.9210943978298836`: raw pooled NRMSE `0.2534198538168074`; direct pooled NRMSE `1.4776946392435133e-16`.
- `paired_conditioning`, bleed `0.85`, condition `12.33333333333333`: raw pooled NRMSE `0.8499999999999999`; direct pooled NRMSE `3.9509759727374615e-16`.
- `paired_conditioning`, bleed `0.95`, condition `39.0000000000001`: raw pooled NRMSE `0.9500000000000001`; direct pooled NRMSE `1.3696597423538845e-15`.

Interpretation: in this synthetic known-matrix setting, crosstalk itself is algebraically removable when there is no perturbation and the matrix remains nonsingular. This is a software/numerical result only.

## Main result — perturbation sensitivity versus conditioning

The direct solve increasingly amplified additive perturbation as matrix conditioning worsened.

At `sigma=0.01`:
- `distance_decay`, bleed `0.50`, condition `1.9211`: raw pooled NRMSE `0.25361707810897127`; direct `0.010751731812211753`; improvement `27.4540 dB`.
- `paired_conditioning`, bleed `0.70`, condition `5.6667`: raw `0.7000714249274855`; direct `0.023934422775948438`; improvement `29.3224 dB`.
- `paired_conditioning`, bleed `0.85`, condition `12.3333`: raw `0.8500588214941363`; direct `0.047295152246510576`; improvement `25.0926 dB`.
- `paired_conditioning`, bleed `0.95`, condition `39.0`: raw `0.9500526301210896`; direct `0.14146783819624328`; improvement `16.5418 dB`.

At the hardest frozen case (`paired_conditioning`, bleed `0.95`, condition `39.0`):
- `sigma=0.0001`: direct pooled NRMSE `0.0014146783819624477`;
- `sigma=0.001`: direct pooled NRMSE `0.014146783819624347`;
- `sigma=0.01`: direct pooled NRMSE `0.14146783819624328`.

This confirms the expected numerical-conditioning effect: exact inversion removes deterministic bleed, but perturbation is magnified as the matrix approaches ill-conditioning.

## Fixed ridge result

The frozen ridge solver used one untuned constant `lambda=1e-4` for every case.

It introduced bias in clean cases. At `paired_conditioning`, bleed `0.95`, condition `39.0`, `sigma=0`, ridge pooled NRMSE was `0.02719642101822556` while direct recovery remained near numerical zero.

In the hardest noisy case (`paired_conditioning`, bleed `0.95`, condition `39.0`, `sigma=0.01`):
- direct pooled NRMSE `0.14146783819624328`;
- ridge pooled NRMSE `0.13872244998157837`;
- direct improvement over untreated baseline `16.5418 dB`;
- ridge improvement `16.7120 dB`.

Thus the fixed ridge rule showed the expected bias/robustness tradeoff: worse when the known system is clean, but slightly better than direct inversion in the most ill-conditioned, highest-perturbation frozen case.

No lambda tuning is authorized from this result.

## What this result establishes

This synthetic harness establishes only that:
- deterministic crosstalk can be removed algebraically when six already-separated source channels exist and the exact invertible mixing matrix is known;
- additive perturbation is amplified according to matrix conditioning;
- one fixed ridge regularizer can trade clean-case bias for limited robustness in the hardest noisy case.

## What this result does not establish

It does not establish:
- that real six-string sensing hardware has the frozen matrices;
- that real crosstalk is linear, time-invariant, or known exactly;
- that real hardware calibration can estimate the required matrix accurately;
- that ordinary mono/stereo guitar audio can be decomposed into authoritative per-string channels;
- that independent physical-reference truth exists;
- that any real holdout/customer event is correct;
- that Basic Pitch, V6, correctness, or delivery may proceed.

The correct engineering implication is prospective only: if a real six-channel hardware design is eventually available, matrix conditioning and calibration error must be measured explicitly before any debleed inversion is trusted.

## Downstream state — unchanged / fail closed

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Hardware procurement, paid vendor work, real calibration capture, and real holdout capture remain paused by budget. Duration remains paused. Policy C remains `UNENROLLED`. Protected-song execution remains embargoed. Archived V143/Gomyway remains closed.
