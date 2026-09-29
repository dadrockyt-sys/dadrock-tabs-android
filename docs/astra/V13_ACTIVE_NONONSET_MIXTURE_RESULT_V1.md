# V13 active-non-onset family-mixture result V1

Date: 2026-09-29 UTC  
Status: **COMPLETE — HYPOTHESIS NOT SUPPORTED**

V13 executed once under launch identity `v13-active-nononset-v1-20260929-01`.

Run identity:
- run **36540511146**
- job **109314523890**
- head `fe293c9446e5ed4b5afc632bbf1fdabc0136df3a`
- artifact **11020985149**
- artifact digest `sha256:1610b51364e8589f812b1084a2d090ccf34be062cdfbe2ad6edbda26e8435109`
- workflow conclusion **success**
- 2 models, 500 updates/model, 1,000 updates total
- no retry, no threshold search, no real-audio inference, no V2B

## Control reproduction

The V13 control reproduced frozen V9 common-test metrics exactly:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

Control batch plan:
`8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

## Intervention identity

Only the active-non-onset family selection changed.

Control sampled active-non-onset slots:
- isolated 1,907
- scales 3,193
- chords 1,207
- repeated 3,304
- legato 1,798
- palm-mute 3,711
- mixed-positive 880

Historical-mixture intervention:
- isolated 2,511
- scales 2,569
- chords 2,219
- repeated 2,861
- legato 3,037
- palm-mute 1,752
- mixed-positive 1,051

Intervention batch plan:
`1627721cd6f541edbf37bd58e4e5f92264d10b39f264855b195dbb6089539de4`

Positive-onset selections, negative-structure-inactive selections, other-inactive selections, per-step permutation, and sampled attacked-note-label exposure were identical across arms.

Both arms sampled:
- 64,000 total frames
- 16,000 onset frames
- 17,676 attacked note labels

## Primary common comparator-test result

| Metric | Control | Historical active-non-onset mix | Delta |
|---|---:|---:|---:|
| Precision | 0.324427 | 0.336066 | +0.011638 |
| Recall | 0.658915 | 0.635659 | -0.023256 |
| F1 | 0.434783 | 0.439678 | +0.004896 |
| Negative FP/s | 0.000000 | 0.000000 | 0.000000 |
| State admission | 0.310078 | 0.263566 | -0.046512 |
| Onset admission | 0.682171 | 0.674419 | -0.007752 |
| Joint admission | 0.286822 | 0.240310 | -0.046512 |

Frozen support gates:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <= 0.05: PASS
- negative FP/s <= 0.10: PASS

## Secondary frozen-V9 test

| Metric | Control | Historical active-non-onset mix | Delta |
|---|---:|---:|---:|
| Precision | 0.486631 | 0.492021 | +0.005390 |
| Recall | 0.705426 | 0.717054 | +0.011628 |
| F1 | 0.575949 | 0.583596 | +0.007647 |

The secondary F1 gate passed.

## Decision

**The V13 active-non-onset family-mixture hypothesis is not supported.**

Changing only this within-stratum family mixture produced only a very small common-test precision/F1 improvement and did not meet the prospectively frozen material-recovery thresholds.

This is a relatively clean negative result because the other three sampler strata and attacked-note-label exposure were held fixed.

The remaining unresolved factors are broader context/domain factors such as negative-structure-inactive composition, 2-second versus 4-second background/context structure, longer-range sequence structure, or multi-factor interactions.

No V2B evaluation or automatic next project is authorized.

Artifact hashes:
- ZIP `1610b51364e8589f812b1084a2d090ccf34be062cdfbe2ad6edbda26e8435109`
- result `f2fa222cacbca5d796767938d093649004dac24425bb826bb4a5e4eb798e2ab1`
- receipt `f65cfbbe10d90053121468d34fa78734bc93efe1cce4b3469a3cae166ad79fae`
- control model `bdba8a2dab99fc61ea057a9511cc2ef7677eb88db889f00a517d546c446fd3d1`
- intervention model `889bab7c5eb1386ab1dd33c20ea99ed3914fecd2beae52e63693aaeece5b0448`
