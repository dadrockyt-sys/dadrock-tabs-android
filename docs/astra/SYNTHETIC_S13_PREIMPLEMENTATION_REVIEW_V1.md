# Synthetic S13 preimplementation review V1

Date: 2026-09-28
Status: **COMPLETE — NO-GO FOR REUSING THE S12 SOFT VIEW AS A LABEL-PRESERVING S13 CONSISTENCY VIEW**

## Scope

This was the required model-free review after the frozen S12 failure. It used only existing repository source plus small handcrafted arrays. It did **not** regenerate the full corpus, run an optimizer, load a trained model, access P1/P2/P3, use Codespaces/Vercel, or change main/Production.

Reviewed path:
- S12 transform: `synthetic.s12_pilot_v1.soften_features`
- 5-frame input construction: `synthetic.s0_pilot_v1.context5`
- S11 targets/loss: separate per-string state cross-entropy plus per-string onset BCE, with state active weight 9, onset positive weight 8 and onset-loss multiplier 4.

New diagnostic module:
- `astra_backend/synthetic/s13_preimplementation_review_v1.py`
- `astra_backend/synthetic/test_s13_preimplementation_review_v1.py`

## What the S12 transform actually does

`soften_features` copies the feature array, finds any frame with at least one onset label, and then mutates **all 192 feature bins** at the onset frame toward the preceding frame. It also mutates the following frame toward the **already-mutated** onset frame. Adjacent onsets therefore interact in mutation order.

`context5` then exposes each changed frame in overlapping five-frame windows, so one local transform changes inputs for multiple neighboring training examples while the state/onset targets remain unchanged.

The S11 loss has no mechanism that knows which feature bins belonged to the attacking string. It continues to require the original per-string state class and onset bit from a shared representation whose entire spectral vector may have been changed.

## Handcrafted findings

All values below are actual deterministic outputs of the new diagnostic.

### Isolated new pitch, blend 0.70

Single-bin trace before: `[0.0, 1.0, 1.0, 1.0]`

After: `[0.0, 0.3, 0.51, 1.0]`

The onset target remains at frame 1. The onset frame loses 70% of its new evidence, and the following frame is recursively blended toward the already-modified onset frame. The five-frame context at the labeled onset therefore changes both the center and future context values.

### Repeated same pitch, blend 0.70

Before: `[0.8, 1.0, 1.0, 0.9, 0.8]`

After: approximately `[0.8, 0.86, 0.902, 0.9, 0.8]`

This case remains closer to the prior state because the preceding frame already contains the pitch. The transform therefore changes different musical situations by very different amounts even though the same onset target is retained.

### One attack over another changing/sustaining component, blend 0.70

Unrelated component before: `[0.9, 0.8, 0.6, 0.5, 0.4]`

Unrelated component after: approximately `[0.9, 0.8, 0.74, 0.668, 0.4]`

New attack component before: `[0.0, 0.0, 1.0, 1.0, 1.0]`

New attack component after: approximately `[0.0, 0.0, 0.3, 0.51, 1.0]`

Because the transform is frame-wide, a string-specific onset changes spectral evidence that can belong to another sustaining/decaying string. Bit-identical labels do not establish that the transformed observation remains an identity-preserving view.

### Adjacent onsets, blend 0.50

Before: `[0.0, 1.0, 0.2, 1.0, 1.0]`

After: approximately `[0.0, 0.5, 0.425, 0.7125, 1.0]`

Frame 2 is changed first as the following frame of onset 1, then changed again as its own onset. Thus the transform is order-coupled for adjacent attacks.

### Boundaries

An onset label at frame 0 is ignored by `onset_frames`. A final-frame onset is transformed but has no following-frame update. These are safe from indexing errors but create asymmetric treatment at clip boundaries.

## Validation findings

Focused tests additionally enforce:
- input immutability;
- exact features shape `frames x 192`;
- exact onset shape `6 x frames`;
- aligned frame count;
- rejection of nonfinite feature or onset inputs.

These validation guards are new diagnostics only. They do not alter frozen S12 source or results.

## Go / no-go decision

**NO-GO:** do not build S13 by applying a state/onset consistency loss between clean data and the existing S12 softened view while claiming that the view is label/identity preserving.

Reason: simple constructed cases demonstrate that the S12 operation can attenuate or partially replace the observable new-pitch evidence, alter unrelated spectral components, recursively change the next frame, and interact across adjacent onsets. Because `context5` spreads those changes into neighboring model inputs while the targets stay fixed, a clean-vs-S12 consistency objective would risk enforcing agreement across observations that are not demonstrably equivalent.

This does **not** prove S12's transform caused the entire ordinary-domain regression, and it does not invalidate the frozen S12 result. It establishes only that the prerequisite for treating that transform as a clean label-preserving consistency view is not justified.

## Exact next action

Stop before optimizer work. Do not create or launch an S13 model experiment using the S12 transform as the consistency/augmentation view.

If work continues, the next scientific step must be a separately versioned **transform-design** review: define one physically/representation-motivated onset-robustness transform whose preservation properties can be justified on isolated, repeated, polyphonic and adjacent-onset cases *before* combining it with any new loss or sampler. That transform correction would itself be the intervention and would require a new prospective design and frozen tests before any training.

Current boundaries remain:
- S12 result stays failed and frozen;
- thresholds stay 0.50 / 0.50;
- P1/P2 remain closed;
- P3 remains sealed;
- no S13 launch is authorized by this no-go review because no concrete valid S13 package has been frozen.
