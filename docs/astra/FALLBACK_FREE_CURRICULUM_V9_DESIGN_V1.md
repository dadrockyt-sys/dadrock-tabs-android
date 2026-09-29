# Fallback-free curriculum V9 design V1 — SUPERSEDED BY FINAL CONTRACT

Date: 2026-09-29 UTC  
Status: historical draft. The common-unit measurement is complete and `FALLBACK_FREE_CURRICULUM_V9_FINAL_CONTRACT_V1` now supersedes this draft. Empirical execution remains unauthorized.

## Single hypothesis

A **native 4-second event generator** that samples feasible acoustic attack groups, note-level chord labels, and note offsets/sustains jointly—without post-placement shifting, clipping, compression, event deletion, hidden rejection loops, or reseeding—can better represent the corrected real-development timing distribution than the frozen 2-second baseline while preserving valid full note labels.

This is a package hypothesis, not a claim that duration alone is causal. V8's 4-second package moved the historical scalar substantially but failed its fallback gate and used a unit-inconsistent timing metric.

## One 4-second arm

V9 V1 drafts exactly one intervention duration: **4.0 s**. V8 L1 already demonstrated enough support for long gaps to make 4 s a plausible bounded choice; 6 s added exposure/compute and had more fallback operations. This choice is frozen before corrected V9 candidate output is generated. There is no 6-second V9 arm.

The comparator will be a same-runtime reproduction of the frozen 2-second content baseline under the new measurement contract. Historical V8 values remain archival, not silently corrected.

## Event representation

Each positive clip has two linked layers:

1. **Acoustic attack groups** `g_i = (t_i, family_i)` with strictly increasing times `0 <= t_1 < ... < t_n < T`.
2. **Note labels** attached to each attack group. A chord group can contain multiple string/fret/pitch labels at one `t_i` while counting once for attack timing.

Every synthetic note also has an offset `o_ij` satisfying `t_i < o_ij <= T`. Full string/fret/pitch validity and overlap constraints are checked separately from timing metrics.

Negative-only clips contain zero attack groups and zero note labels by construction.

## Native conditional generator

Intervention clip duration: `T = 4.0 s`.

Content family/base-template identity comes from a prospectively frozen split manifest. No base motif identity may cross train/test.

For a positive clip with declared attack-group count `n` and frozen family-conditioned gap supports, derive deterministic uniforms:

`u_i = H(seed, split, family, base_id, variant_id, i) / 2^64`

where `H` is SHA-256 interpreted from the first 64 bits. No stateful retry sequence is permitted.

For each gap support `[a_i,b_i]`, define:

`remaining_min_i = sum(a_k for k=i+1..n-1) + final_margin`

`upper_i = min(b_i, T - t_i - remaining_min_i)`

If `upper_i < a_i`, the declared content instance is **infeasible** and the run fails closed. It is not resampled, shifted, clipped, deleted, compressed, or reseeded.

Otherwise:

`gap_i = a_i + u_i * (upper_i - a_i)`

`t_(i+1) = t_i + gap_i`

First-attack support and final margin are frozen before generation. There is no post-placement boundary-correction path, so fallback is structurally absent.

## Offsets and sustains

Each synthetic note at attack group `i` gets a desired sustain with frozen support `[s_min,s_max]`. With independent deterministic uniform `v_ij`:

`o_ij = t_i + s_min + v_ij * (min(s_max, T - t_i) - s_min)`

This is valid only if `T - t_i >= s_min`; otherwise the clip fails closed as infeasible.

No offset is clipped after generation. Real V2B sustain truth is not fabricated; this rule applies only to synthetic labels.

## Distribution freeze dependency

V9 V1 intentionally does **not** select numerical short/ordinary/long gap mixture weights from the historical unit-inconsistent summaries. PRE-V9-MEASUREMENT-V1 must first produce the common-unit reference table.

After that table exists, the final launch spec may freeze one gap-support/mixture package **before candidate generation**. It may not search a grid, compare several mixture variants, or retune after seeing candidate output.

The final spec must freeze:

- positive/negative clip counts;
- family proportions;
- attack-group count distribution by family;
- simultaneous note multiplicity separately from attack timing;
- gap supports and weights;
- sustain supports;
- first-attack support and final margin;
- exact seed set/hash-to-uniform identity;
- train/test split identities;
- all numerical gates.

## Pre-render timing gate

Numerical values are **not yet frozen**.

The eventual gate must operate on acoustic attack groups and include at least:

- aggregate positive attack-group density;
- pooled IOI p50 and p90;
- repeat250 over positive IOIs only;
- prospectively frozen long-gap fraction;
- per-clip rate distribution;
- per-family synthetic counts/summaries;
- zero infeasible clips;
- zero invalid note labels/offsets;
- zero fallback paths in source and result.

At most one intervention arm exists. Failure of any gate stops V9 before rendering, training, or V2B inference.

## Downstream experiment on paper

Only after the measurement dependency is resolved, gates are frozen, and a future explicit empirical authorization exists:

- exactly 2 models: same-runtime 2 s baseline + 4 s V9 intervention;
- 500 optimizer updates/model, 1,000 total maximum;
- 0 scientific retries;
- identical frozen architecture/package between arms;
- verified common-tensor initialization mapping before optimizer step 1;
- frozen R3 renderer;
- exact pinned frontend/runtime;
- exact-string/fret state objective;
- O0 exact-frame BCE onset objective unless a separately approved design version changes it before launch;
- thresholds state 0.50 / onset 0.50;
- decoder unchanged;
- paired frozen batch/stratum schedule;
- masks/padding/frame weighting explicitly pinned;
- report update count **and** actual frames/events/positive seconds seen so equal update count is not mislabeled equal compute/exposure;
- numeric render, inference, CPU-time, and storage ceilings required in the launch spec;
- non-overwriting durable source/spec/manifest/checkpoint/raw-result retention.

Synthetic sanity must use one common fixed comparison population; any duration-stress population must be separately frozen before training. Train/test motif identities must be disjoint.

## Execution order

1. PRE-V9-MEASUREMENT-V1 common-unit target table.
2. Freeze final V9 spec/gates/source identities and consumed launch scope.
3. Generate timing manifests only.
4. Fail-closed pre-render timing and full-label validity gate.
5. Render baseline + intervention only if step 4 passes.
6. Train only if render/data identity verification passes.
7. Run synthetic sanity.
8. Permit one V2B development inference only if synthetic sanity passes technically.
9. Freeze result. No automatic V10.

A synthetic sanity failure must prevent real-development inference in code, not merely in prose. V2B scoring populations/functions must be pinned, including the 56/49 scored-reference provenance or an explicitly corrected successor.

## Launch integrity requirements

Before empirical authorization, implementation must provide:

- immutable source/spec/manifest pins;
- one consumed launch scope across every invocation path;
- no automatic retry;
- deadline/CPU/storage ceilings;
- partial-failure receipts;
- fail-if-output-exists behavior;
- durable exact source/manifests/checkpoints/raw results;
- no original sound files or credentials in Git.

Infrastructure repair must be distinguished from scientific retry and may not silently alter scientific inputs.

## Current stop boundary

This design is **not launch-ready** because common-unit targets and numerical gates are intentionally unresolved.

No authorization is implied for candidate timing generation, waveform rendering, weights, inference, optimizer steps, workflow dispatch, new sound collection/annotation, V1.1/P1/P2/P3/A2, main, or production.
