# Guitar-TECHS post-V9 shared-network synthetic gradient audit — verified result V1

**2026-10-08 · branch `astra-work` · synthetic model test PASS · original V9 scientific FAIL UNCHANGED**

## Decision

**Source-linked synthetic shared-parameter gradients confirm a plausible excess-consistency-pressure mechanism in the actual V9 architecture, not causation of V9's historical scientific failure.** In a randomly initialized `TemporalTabCNNV9`, artificial features/labels, the original V7 loss, and frozen `0.10 × symmetric_kl_consistency`, gradients from the weighted KL term exceeded those of the paired supervised loss in the convolution, acoustic embedding, GRU, and routing layers. Training-mode **dropout alone** generated nonzero KL even for identical synthetic inputs; the eval-mode identical-input control correctly gave KL=0 and zero KL gradients.

This is a **zero-optimizer, no-media experiment**, not training, inference with frozen checkpoints, a real development experiment, a recovered V9 candidate, or a product performance result.

## Exactly one authorized launch and independent artifact verification

- The user explicitly requested **“Launch the study”** after the [prospective Stage-1 design](./GUITARTECHS_POST_V9_PROSPECTIVE_CAUSAL_STUDY_CONTRACT_V1.md). Authorization and exclusive scope are in `GUITARTECHS_POST_V9_SHARED_NETWORK_SYNTHETIC_GRADIENT_AUTHORIZATION_V1.json`. The **one-use authorization is now consumed**.
- Frozen launch commit **`64d654f4a2e3f50396290cd1f8ac32d770b903c0`**; [GitHub Actions run **37851005111**](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37851005111), job **113563597750**, **success**, one attempt. Started 2026-10-08 **22:03:30 UTC**, updated 22:04:42 UTC (~72 seconds), below the 20-minute CPU-only ceiling. Source checks, pinned dependencies, four exact upstream TabCNN blob hashes, synthetic evaluation, JSON upload and cleanup were all successful.
- Frozen scientific sources unchanged: `TemporalTabCNNV9` from original `guitartechs_training_v9/model.py` (Git blob `b930555e6c816fd45e2e77dc292702bf46fc6d02`), V7 inherited model (blob `cdb80274494782fc42774f3dd5c6859e9beb97d3`), V6 architecture (blob `78a17dd174bd86e804af0e9c75056055d6048295`), original V7 objective (blob `7e0f3a297e4ce8fa20b4bcca74842964e08aafd2`), original V9 paired augmentation/KL (blob `9b704ea9c5bf153197dfde260c1b995142d062b5`). New separate script `verify_post_v9_shared_parameter_gradient_v1.py` (blob `bb904a2bbd67139574ce41bdb78628316a208365`).
- Artifact **11581379212**, name `guitar-techs-post-v9-synthetic-shared-network-gradient-v1`; independently SHA-256 verified downloaded archive `15d0ff596ea6d2577c47c0bb65ae87a27a6c4bfbcc2c9598ab446c813c98f9cd`, matching GitHub's archive digest. Its only file `post-v9-synthetic-shared-network-gradient-v1.json` independently hashed as **`d6825e128c84c1742c082774138250431c5749ebd9300713d16e7d21794e9356`**, matching the job log. Artifact JSON remains in GitHub Actions, not committed in full. `optimizerSteps=0`; the model weights were rehashed to confirm no mutation and were **not exported**.
- Deterministic randomly initialized model seed `20261008`; abstract synthetic B=1×T=200×C=1×F=192×W=9 input and synthetic string/fret labels (six strings, 21 state classes, including silence/active/masks). V7 content weight **1.125**, frozen KL coefficient **0.10**. Synthetic initialized model digest `517ac913cfa6192d1421fab032d7f71985f8318ce35fdfd4eb6298f40ab88eea`. The upstream Python runtime was pinned to Python 3.10.15 / torch 1.11.0+cpu, NumPy 1.21.6 and original dependencies.

## Frozen three-control results

| Scenario | Supervised paired loss | Original weighted KL | Full-model KL/supervised parameter-gradient ratio | Acoustic ratio | GRU/temporal ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Same synthetic input, **eval mode** (dropout off) | 4.163958 | **0** | **0×** | 0× | 0× |
| Same synthetic input, **training mode** (dropout on) | 4.167218 | **0.205603** | **1.3735×** | **1.6623×** | **1.8597×** |
| Original **paired feature augmentation + training-mode dropout** | 4.163703 | **0.198828** | **1.3259×** | **1.6113×** | **1.7780×** |

All scenarios passed reconstruction of the exact six components of V7 supervision and additivity of supervised and KL gradients on four named true model-parameter tensors. Under **paired augmentation + dropout**, selected per-group KL/supervised gradient L2 ratios were:

| Exact parameter group | KL/supervised norm ratio | Supervised gradient L2 | Weighted original KL gradient L2 |
| --- | ---: | ---: | ---: |
| `conv` | **1.4485×** | 0.0438050 | 0.0634534 |
| `acoustic` | **1.6113×** | 0.1408976 | 0.2270330 |
| `temporal` (GRU) | **1.7780×** | 0.0950975 | 0.1690848 |
| `routing` | **1.7924×** | 0.7376444 | 1.3221341 |
| `state_head` | **0.2449×** | 0.6600247 | 0.1616380 |
| `activity_head` | **0.1522×** | 0.0627317 | 0.0095501 |
| `event_head` | **0.1531×** | 0.2077458 | 0.0318036 |
| `onset_head` | **1.4401×** | 0.0061821 | 0.0089025 |
| `pitch_head` | **1.3471×** | 0.0259063 | 0.0348990 |

The direction of KL relative to supervised gradients is also measured in the artifact as **cosine**, not simply assumed to align. Most shared-trunk cosines were close to zero, so a larger KL norm **does not mean KL cancels a supervised gradient, causes suppression or necessarily degrades training**. Different model weights, labels, feature inputs and optimizer state can change all ratios.

The original V9 KL batchmean still has a mathematically verified **1,200× scaling relative to a mean over 200 frames × six strings**; for this paired synthetic case mean per-position KL **0.001656902**, so original 0.10-weighted KL **0.198828**, whereas **counterfactual** 0.10-weighted mean-per-position KL would be only **0.000165690**. These counterfactual numbers were calculated without editing model or trainer code and **not trained**.

## Important limits and non-inferences

1. **Random initialization only:** No historical V7/V8/V9 checkpoint or actual training trace was loaded. This cannot reconstruct the original V9 learned weights, saved optimizer trajectory, or training-step KL/supervised gradient ratios.
2. **Dropout versus augmentation:** Training-mode dropout produced KL=0.205603 even from identical features. The paired-augmentation training-mode case produced KL=0.198828. **Their fixed draws of dropout were different** (intentional scenario-specific RNG seeding), so subtracting these numbers would **not** isolate augmentation's incremental effect; do not claim augmentation lowered or raised KL relative to dropout from this experiment.
3. **Normalization unit semantics:** The per-position-normalized comparison is only a numerical counterfactual; it is not a new approved training loss, a loss fix retroactively applied to V9, or evidence that V10 would work.
4. **Zero admitted events remain an independent real-development observation:** The separate authorized [256-capture post-V9 admission audit](./GUITARTECHS_POST_V9_FIXED_OUTPUT_ADMISSION_RESULT_V1.md) confirmed zero active probabilities admitted by V4 on the *selected epoch-20 V9 models*. This study increases plausibility of a training-pressure imbalance but **does not link it causally** to those models.
5. **No performance promotion:** The strongest already-frozen clean development F1 is V8 macro **0.24680584415601026**. Original V9 scientific advancement remains **FAIL** (macro F1 0.0). This study did not check generalization or Stage-B holdouts.

## Next guarded decision

**Scientific status:** shared-parameter *synthetic* audit **PASS** for the prospectively specified gradient-control question. **Causal explanation of the real V9 failure remains unresolved**; training, decoder, thresholds and held-out scores remain unchanged.

**Next proposal only (NOT AUTHORIZED):** A preregistered **one-factor H1 development study** could compare the original frozen 0.10 batchmean KL objective against **per-position-normalized KL**, preserving source-domain augmentations, model architecture, preprocessing, optimizer setup, original fixed V8 decoder, seed and fold protocol, with explicit per-step KL/supervised *parameter gradients* and V4 note-admission diagnostics. Declare separate candidate(s), compute/time ceiling, checkpoint/resume equivalence and stop/gate criteria **before any real data or optimizer step**. Do not confound H1 with H2 augmentation redesign. Any such real training requires fresh explicit user approval; this study does **not** authorize it.

**Stop:** The single-use Stage-1 run is finished and consumed. No automatic rerun, seed selection, V9 rescue/V10 optimizer, fresh P1/P2 data processing, P3, protected-song tuning, Stage-B holdout, paid compute, Production or `main` changes. Preserve original Guitar-TECHS V8/V9, Go My Way quantized evidence, spectral-bass baseline, and unresolved model-lineage/commercial-rights gate.

