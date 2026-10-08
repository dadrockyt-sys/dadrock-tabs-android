# Guitar-TECHS post-V9 prospective scientific decision contract V1 — DESIGN ONLY

**2026-10-08 · `astra-work` · status `PROPOSAL_NOT_LAUNCH_AUTHORIZATION`**

## Scientific question and current truth

**Observed:** The authorized full-development zero-training diagnostic verified **0 V4-admitted runs and 0 V8-decoded note events** for both selected V9 epoch-20 checkpoints across all **256 P1/P2 capture views**. Its frozen F1 remains 0, versus V8 macro F1 **0.24680584415601026**.

**Source and synthetic fact:** V9's `symmetric_kl_consistency` uses `batchmean` on `B×200×6×21`; unlike normalized supervised state CE, this sums across 200 frames and 6 strings before dividing by batch, magnifying mean per-position KL **1,200×**. Its original 0.10 coefficient is **120× mean per-position KL**. Fixed synthetic independent-logit experiments yielded a KL/supervised state-logit gradient norm ratio of **2.329×** at only `0.05` paired-state-logit perturbation (mean per-position KL **0.001188**), **11.660×** at `0.25` and **35.322×** at `0.75`. See `GUITARTECHS_POST_V9_SYNTHETIC_OBJECTIVE_AUDIT_RESULT_V1.md`. **No real model/parameter gradient telemetry was available and the hypothesis is not causally established.**

The scientific question is whether excessive invariance pressure (not merely that the historical loss has different normalization units) is responsible for suppressing V9's ability to emit active-fret states, and whether augmentation semantics confound that hypothesis. A successful product outcome is not established by correcting either implementation property alone.

## Prospective sequence (not permission to execute)

### Stage 0 — review-only prerequisites

1. Keep V9 source blobs, selected models, training/result receipts and the original V8 decoder thresholds **immutable**. Do not label a new KL reduction a repair to the frozen V9 study: it would be a **new objective / new scientific hypothesis**.
2. Declare primary causal question **H1: consistency normalization**; separate possible feature-domain shift **H2: feature-space augmentation semantics**. Do not simultaneously change both in the first empirical comparison.
3. Verify version of PyTorch, frozen loss definitions, activity/identity/event heads, target masks, content weights, batch-size/per-sequence normalization, paired augmentation seed derivation and resume selection. Enumerate known unknowns, including missing KL logs and lack of an independent unexposed test population. No source-domain score may be promoted to holdout or customer accuracy.
4. Identify any actual computational/legal/data budget before selecting a new experiment. Neither synthetic numerical audit nor these notes grant real forward-pass/training authority.

### Stage 1 — **proposed**, separately bounded no-media shared-network diagnostic

Potential goal: test whether the synthetic **shared-parameter trunk** sees KL-dominant updates, rather than relying on leaf-state-logit gradients. This requires a distinct small synthetic-model permission/scope despite no media. Freeze:
- Exact pinned upstream TabCNN source / V7-V9 architecture identity and short deterministic synthetic feature/label fixtures (B=1, T=200, six strings, 21 state classes), with both active and silence labels and valid mask patterns.
- Exact original composite V9 objective with **0.10 batchmean KL**; observe `supervised_a`, `supervised_b`, all weighted V7 components, raw KL, weighted KL, mean-per-position KL, gradient norms/cosines on named groups (conv, acoustic, GRU/temporal, state and auxiliary heads). Separate gradient contributions by `torch.autograd.grad`, without taking any optimizer step or modifying source weights.
- Check a mathematically normalized KL **only as a diagnostic counterfactual**, not as an authorized code change or trained candidate. Use fixed, preregistered perturbations; include identical-view zero-KL control and reference-of-no-loss-flow control.
- Verify source/blob identities, finite outputs, shape, deterministic seed, no reference leakage, no non-synthetic media, no saved weights and no checkpoint access. Do not dispatch from this planning document.

### Stage 2 — possible **future** new controlled development study requiring fresh user authorization

**Question H1 only:** Is the **prospective** per-position-normalized consistency objective better behaved than the frozen original V9 objective when all other training semantics are held fixed? If yes, preregister a new, uniquely named candidate/study, preserving:
- Same P1/P2 developer-only population and known exposure limits; same V7 family, V8 decoder, fixed thresholds, training seed(s) chosen before results, original feature-space augmentations (unchanged during H1), single frozen contrast normalization, accepted alignment keys and deterministic preprocessing.
- Explicit timeout-safe persisted checkpoints, exact seeding/resume equivalence test that covers **the complete two-view composite objective**, and exact per-term/gradient telemetry incl. KL, stateCE, activity, event rank, pitch, continuity, identity and content-weight factors.
- Independent, named metrics **both for V4 admission (before/after pruning)** and final decoded events; frame/string argmax activity, fixed state-probability quantiles, predicted/reference/TP counts, mask/probability validity, fold F1 and completeness, plus resource/time ceilings and hashes.
- **No seed/checkpoint/threshold rescue** after results. No best-of-many study; if exploratory arms are later compared, pre-budget the family of comparisons and do not overstate causal inference. Protect P3, held-out captures and protected songs. No customer-readiness claim from exposed P1/P2.
- A **new** frozen advancement gate, precise success/failure stop conditions, authorization and launch receipt prepared **before optimizer steps**. A green CI job or improved training loss cannot count as scientific success without admitted events and preregistered fold generalization criteria.

H2 (feature-augmentation physics/semantics) must be a **separately preregistered next question** with a single frozen candidate and its own data/compute approval if pursued. Do **not** silently replace gain/noise/tilt/masking along with KL normalization in the H1 contrast. A physically meaningful amplitude gain on audio may not affect relative-to-peak CQT features as naively expected; validate units before making any substitution.

## Evidence and approval gates

- **Completed:** original V9 frozen FAIL; full 256-capture post-V9 output-admission run `37836761676` (result `GUITARTECHS_POST_V9_FIXED_OUTPUT_ADMISSION_RESULT_V1.md`); no-media exact-loss synthetic run `37850081250` (result `GUITARTECHS_POST_V9_SYNTHETIC_OBJECTIVE_AUDIT_RESULT_V1.md`).
- **Not completed / not authorized by this document:** a synthetic trained-model/shared-parameter diagnostic; any P1/P2 model forward passes beyond prior consumed scope; new optimizer steps; a normalized-loss V10 candidate; H2 augment ablation; opening P3; song-derived tuning; Stage-B reference capture/evaluation; paid compute; Production; `main`.
- **Decision required:** after reviewing this proposal, user may separately approve one bounded stage at a time. Do not reuse prior Green / "I authorize" / "Please continue" approvals for a new independent experiment.

**Recommendation:** Stage 1, if separately approved, is the smallest next empirical study that discriminates "large state-logit derivative" from "large learned shared-parameter derivative". It still cannot retroactively establish the cause of the completed V9 run. Only if it strengthens the hypothesis should an explicitly budgeted H1 development-training comparison be considered. Until then, preserve V8 clean baseline, frozen Go My Way and spectral bass results, and independent `guitar-fl.pth` checkpoint-lineage/commercial-use blockers.

