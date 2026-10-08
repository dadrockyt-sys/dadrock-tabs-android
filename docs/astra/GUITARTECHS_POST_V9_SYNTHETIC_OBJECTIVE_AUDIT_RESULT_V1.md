# Guitar-TECHS post-V9 synthetic objective audit — verified decision V1

**2026-10-08 · branch `astra-work` · status: synthetic source-linked numeric audit PASS; V9 scientific FAIL unchanged.**

## Decision

The previously identified **V9 symmetric-KL reduction scaling is independently verified by an executable, zero-optimizer, no-media test of the frozen loss functions at the real training sequence dimensions**. On deliberately chosen synthetic paired state logits, the KL gradient component can exceed the supervised state-logit gradient even when the mean KL divergence is small. This is a **plausible training-objective imbalance risk**, not proof it caused V9's frozen zero-event result or a measurement of historical model/parameter gradients.

The [post-V9 fixed-output admission audit](./GUITARTECHS_POST_V9_FIXED_OUTPUT_ADMISSION_RESULT_V1.md) remains authoritative for the *observed* failure: the selected epoch-20 V9 models emitted no events from all 256 P1/P2 validation captures because active state probabilities never passed frozen V4 admission thresholds. The present synthetic fixture does not reopen historical training authorization or change those findings.

## Verified run and artifact identity

- Authorized from the user's **“Please continue 💚”**, scoped in `docs/astra/GUITARTECHS_POST_V9_SYNTHETIC_OBJECTIVE_AUDIT_AUTHORIZATION_V1.json`; exactly one non-paid/CPU-only, no-data, no-checkpoint, no-optimizer workflow execution.
- Launch commit `163271528484d4a022465dba6b19972f64851da6`; run [37850081250](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37850081250), job `113560539790`. **Status: SUCCESS**, one attempt. Started 2026-10-08 21:55:15 UTC; updated 21:55:56 UTC (~41 s). Original source Git blob guard, Python 3.10.15, CPU `torch==1.11.0+cpu` and `numpy==1.21.6`, synthetic execution, result upload and cleanup all passed. Log markers: `MINIMAL_FROZEN_CPU_MATH_RUNTIME_PASS`, `POST_V9_SYNTHETIC_OBJECTIVE_AUDIT_PASS`, `OPTIMIZER_STEPS_EXECUTED=0`.
- Artifact ID **11580783636**, `guitar-techs-post-v9-synthetic-objective-audit-v1`; GitHub archive digest `sha256:548e23e4562f1eb917128628196667364d63477f5130df1dddcb1fd07d29fe70` independently verified against downloaded ZIP bytes. Inside: `post-v9-synthetic-objective-audit-v1.json`, SHA-256 **`dd5303f8be46a9e5dd249fe991dc1031cd41cd5beb5f911546f901c05212cd2d`** independently rehashed and matched to Actions log. The detailed JSON remains in this immutable workflow artifact, **not committed** into source control.
- Frozen implementation under test: `astra_backend/guitartechs_training_v7/objective_decoder.py::v7_sequence_loss` (Git blob `7e0f3a297e4ce8fa20b4bcca74842964e08aafd2`), `astra_backend/guitartechs_training_v9/paired_view.py::symmetric_kl_consistency` (blob `9b704ea9c5bf153197dfde260c1b995142d062b5`), V9 trainer composition `0.5*(loss_a+loss_b)+0.10*consistency` (blob `99cae61a0a299de27a24e367afccdf7b13a7c81b`). New diagnostic-only script `verify_post_v9_synthetic_objective_audit_v1.py` (blob `a35de5fe648a37a8672442698cbdcd42d48f0180`).

## Exact synthetic test

Used **B=1, T=200, strings=6, classes=21**, the original frozen V9 consistency weight **0.10**, and illustrative content weight **1.125**. The 200-frame synthetic label sequence includes explicit active frets, silence, and masked positions. Two independent synthetic output dictionaries contain the actual V7 state/activity/pitch/event heads' required tensor shapes; no trained network, optimizer, checkpoint, audio or reference data is loaded. A fixed seed `20261008` and prospectively fixed paired-state-logit difference scales **[0, 0.05, 0.25, 0.75]** determine all scenarios.

The checks:
- Recompose the exact V7 supervised term from its **stateCE + 0.10 continuity + 0.25 identity margin + 0.25 activity + 0.20 pitch + 0.60 event rank**, including content weight, for both views; assert equivalence to `v7_sequence_loss`.
- Run original V9 symmetric KL with `F.kl_div(..., reduction="batchmean")` and original V9 0.10 weighting. At the real V9 dimension it divides by **B**, not **B×T×6**, resulting in `batchmean KL = 1200 × mean per-position KL`, and weighted term `=120 × mean per-position KL`. This is an exact property for this fixed shape, not a guess.
- Independently differentiate the symmetric supervised pair loss, weighted KL, and their sum w.r.t. **synthetic state-logit leaves**; assert gradient additivity. **These are neither model-parameter gradients nor actual V9 training gradients**, and auxiliary outputs are separate synthetic leaves rather than sharing a learned representation.

### Results from the SHA-verified artifact

| Fixed paired-logit difference scale | Supervised mean loss | V9 weighted batchmean KL | Mean per-position KL | Weighted KL / supervised **state-logit gradient norm** |
| --- | ---: | ---: | ---: | ---: |
| 0.00 | 3.921323 | 0 | 0 | 0× |
| 0.05 | 3.921655 | 0.142531 | 0.001187755 | **2.3293×** |
| 0.25 | 3.929644 | 3.560256 | 0.029668795 | **11.6599×** |
| 0.75 | 3.995958 | 31.809204 | 0.265076697 | **35.3225×** |

All four scenarios passed total-loss reconstruction, finite-value checks and gradient additivity. The independent state-logit supervised norm was approximately **0.02269–0.02278**; weighted KL state-logit gradient norm grew from **0** to **0.05286**, **0.26471**, and **0.80465** across the prescribed scales. Their magnitude ratios in this synthetic fixture do **not** establish the ratios for a real network's shared parameters, different representations, feature views or training distribution. **No new performance gate or checkpoint selection was conducted.**

For clarity, `0.10 × mean per-position KL` at synthetic difference 0.25 would be **0.0029669** versus V9's **3.5603**; this is only a mathematical counterfactual used to expose units. It is **not** an authorized loss modification, approved V10 hypothesis or recommendation to relaunch V9.

## Feature-augmentation semantic audit

Source inspection and deterministic feature-tensor fixtures confirm that V9's training gain, frequency tilt, noise and masking are implemented in **post-CQT, relative-dB-derived feature/window space**, not on physical audio pressure samples:
- On an illustrative feature value **0.5**, multiplication by the linear amplitude factor for +3 dB gives **0.70627**, whereas a simple 3/80 additive normalized-dB-coordinate change would be **0.53750**. Because preprocessing uses dB **relative to the sample maximum**, real global gain would introduce an additional normalization effect. Neither operation is an exact physical gain model here.
- The current tilt coefficient of `±1.5` is applied across a normalized `[-1,1]` coordinate, giving **3 dB end-to-end** over **191/24 ≈ 7.958 octaves**, or **~0.37696 dB/octave**, not **1.5 dB/octave**.
- Deterministic `make_tensor_training_view` repeated with the same seed produced byte-identical output and did not mutate the source. For a deliberately constant synthetic feature/window source, **38,208 of 38,208** redundant neighbouring-window positions were different after the single random feature-view transform, showing that repeated appearances of a source frame need not receive the same window-level perturbation. This is a representation consistency concern, **not** demonstrated label corruption or auditory invalidity in real captures.

## What we can and cannot conclude

**Proved:** the actual frozen V7+V9 loss composition has a substantial units mismatch between normalized supervised CE and KL batchmean; the exact KL dimension factor is 1,200, and synthetic independent state logits can show KL-dominant gradients even at a mean per-position KL of ~0.00119. The original feature-space augmentation name/physical-unit assumptions are not supported by its code. The frozen V9 admission failure was previously confirmed by a separate authorized real-development evaluation.

**Not proved:** actual per-batch KL magnitude during original V9 training, model shared-parameter gradient ratios, optimizer dynamics, label preservation under real augmentations, model representation collapse, or the causal explanation of V9's no-note output. No V9 checkpoint or scientific result is reinterpreted as a pass.

## Decision and explicit next steps

**Decision:** Close this bounded synthetic audit as **PASS for implementation risk localization**; keep Guitar-TECHS V9 **scientific FAIL** and the V8 clean macro F1 `0.24680584415601026` unchanged.

**Next appropriate boundary:** produce **one prospective research design** (not a run) isolating **normalization semantics of the consistency objective** from **feature-space augmentation semantics**, with a synthetic exact-model-forward/parameter-gradient test as a possible preparatory stage, explicit parameter-level telemetry, masks and content-weight normalization, shared-trunk gradient norms, exact deterministic seed/resume contract, and a mutually exclusive scientific comparison plan if a later real-data experiment is separately authorized. Do not change the frozen V9 implementation under the label of infrastructure repair. Do not tune against Go My Way or P3. Obtain a **fresh explicit user decision** before creating a new training candidate or granting any real-data/model checkpoint forward-pass access. Do not automatically run synthetic model experiments beyond this consumed one-run scope.

**Stop conditions:** no V9 rerun, threshold/checkpoint/seed rescue, V10 training, P3, protected-song tuning, Stage-B holdout, paid compute, Production or `main` change. Preserve separate hardware/rights Stage-B work, frozen Go My Way quantized candidate, spectral bass and unresolved `guitar-fl.pth` checkpoint training-lineage rights.

