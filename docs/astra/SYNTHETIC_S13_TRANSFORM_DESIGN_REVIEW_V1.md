# Synthetic S13 transform-design review V1

Date: 2026-09-28
Status: **MODEL-FREE CANDIDATE TRANSFORM REVIEW — PROSPECTIVE**

## Purpose

The prior preimplementation review rejected the S12 frame-wide recursive blend as a label/identity-preserving clean/soft view. This review defines exactly one replacement transform and tests its preservation properties on handcrafted feature arrays only.

No model is loaded or trained. No full synthetic corpus is regenerated. No P1/P2/P3 data are used. The demonstration retain fraction of 0.50 is an engineering example only, not a value fit to real data.

## Candidate transform

Name: **positive-onset-increment compression**.

For each labeled onset frame `f > 0`, using the immutable original feature array:

`positive_delta = max(x[f] - x[f-1], 0)`

`x_soft[f] = x[f] - (1-r) * positive_delta`

where `r` is a retain fraction in `(0,1]`.

Everything else is unchanged:
- no following-frame mutation;
- no change to bins that are flat or decreasing;
- no recursive use of already-transformed frames;
- simultaneous string onsets at one frame transform that frame once;
- frame zero is unchanged because there is no preceding representation frame.

This is a **representation-motivated stress transform**, not a validated physical guitar/capture simulator. CQT bins are shared acoustic features, so the operation is not string-source-selective.

## Why this is materially different from S12

S12 blended all 192 bins toward the preceding frame and then recursively blended the following frame toward the already-modified onset frame. That could alter unrelated sustaining evidence and couple adjacent onsets.

This candidate changes only positive frame-to-frame increments at the labeled onset frame. For any `r > 0`, a positive increment remains positive and retains exactly fraction `r` of its original increment. Non-rising bins are bit-preserved.

## Handcrafted review at r = 0.50

- isolated new pitch: `[0,1,1,1,1] -> [0,0.5,1,1,1]`;
- repeated same pitch: `[0.8,1,1,0.9,0.8] -> [0.8,0.9,1,0.9,0.8]`;
- attack over a decaying sustain: the decaying sustain trace is unchanged, while the new attack rise is halved at the onset frame;
- adjacent onsets: `[0,1,0.2,1,1] -> [0,0.5,0.2,1,1]`; the second onset does not inherit the first onset's transformed value;
- frame-zero onset remains unchanged; a final-frame positive rise is safely compressed;
- a separate unrelated bin that is also rising at the same frame is compressed too. This is an explicit limitation: the transform is representation-local, not source-separated.

## Preservation claims supported by construction

For valid frozen-range inputs and `0 < r <= 1`:
1. input arrays are not mutated;
2. only labeled onset frames can change;
3. only positive increments can change;
4. flat/decreasing bins are preserved exactly;
5. positive increments retain their sign and a known nonzero fraction;
6. no following frame is modified;
7. adjacent onset frames are computed from immutable source values, so there is no recursive order coupling.

These are mathematical/implementation properties. They do **not** prove that every transformed frame corresponds to a physically plausible recording or that every rising bin belongs to the attacking string.

## Go / no-go decision

**GO for prospective S13 design work, not for training yet.**

The candidate passes the specific preservation defects that blocked the S12 view: it does not erase a new rise, does not rewrite declining/sustaining bins, does not modify the following frame, and does not recursively couple adjacent onsets.

The known non-string-selective limitation is acceptable for a bounded synthetic representation-robustness hypothesis because rising evidence is attenuated rather than reassigned or erased, but it must be stated in the S13 design and cannot be described as a physical attack-envelope simulator.

## Next action

Write one prospective S13 design/spec using this transform as the **only intervention variable**. Do not add a new consistency loss, sampler, architecture, threshold, or decoder change in the same experiment.

Before any optimizer work, freeze:
- one exact retain fraction chosen without P1/P2 fitting;
- whether all or a fixed predeclared fraction of training examples are transformed;
- a corrected synthetic challenge using the same nonrecursive transform;
- the existing S12 minimum benefit/regression floors plus ordinary precision/negative-only/family guards;
- three fixed seeds, 500 steps/model, maximum six models/3000 steps;
- complete source/data dependency pins and single-use launch controls.

P1/P2 remain closed, P3 sealed, thresholds remain 0.50/0.50, and main/Production remain unchanged.
