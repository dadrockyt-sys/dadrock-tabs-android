# H1 Phase 3 — historical runtime evidence and source-identity review draft

**Date:** 2026-10-08. **Branch:** `astra-work`. **Status:** `OFFLINE_REVIEW_PREPARED / REAL_LAUNCH_BLOCKED`. OpenAI Support escalation is pending; no permission to use the blocked launch operation through GitHub, Codex, Codespaces or any alternate surface has been confirmed.

## 1. Evidence obtained without starting anything

Read existing run `37573544151` through the connected GitHub job listing and **previously recorded timestamped job logs**. No new Actions dispatch, model inference, P1/P2 archive access or optimizer steps.

| Existing job ID | Work/fold | Preparation seconds | Training start to epoch-20 emission | Epoch-1000 emission to next step (full-fold eval + reporting) |
| --- | --- | ---: | ---: | ---: |
| `112637586381` | P1 train → P2 validate, first segment | 1,551.817 | 1,384.671 | not measured here |
| `113058245257` | P2 train → P1 validate, first segment | 1,554.092 | 565.653 | not measured here |
| `112986816044` | P1 train → P2 validate, final segment | 1,886.481 | not applicable | 647.582 |
| `113346922946` | P2 train → P1 validate, final segment | 3,429.715 | not applicable | 1,198.821 |

Calculation conventions: `preparation` spans the historical prepare-step entry timestamp through the subsequent training-step entry; `first-20` spans training-step entry to `V9_CHECKPOINT` epoch 20 (including whatever limited V9 checkpoint diagnostics precede the log message); `full-fold terminal` spans epoch-1000 checkpoint log to the subsequent job step, including full validation and reporting. The logs come from differing runner instances and original-V9 rather than revised H1. These are **observed intervals**, not measured H1 stage budgets.

The numerical receipt is `docs/astra/GUITARTECHS_H1_EXISTING_ACTIONS_TIMING_EVIDENCE_V1.json`. For orientation only: using the **maximum observed single preparation** (3,429.715 s), both first-20 fold intervals each repeated twice (3,900.648 s) and both final-fold terminal intervals each repeated twice (3,692.806 s), the subtotal is **11,023.169 seconds = 183.72 minutes** under an 18,000 s runner ceiling. **This is not a conservative upper bound or a launch-readiness pass**; it excludes installation/source downloads, H1 added V4 admission traces, gradient instrumentation, changed full-evaluation implementation, archive retry faults, disk/RAM peaks, artifact upload/cleanup reserves, runner variability and other uncertainty. Earlier Phase 2 demonstrated current nested `curl` retries have a theoretical 120-hour upper bound, which must still be tightened under a separately reviewed plan. Do not increase the frozen 300-minute authorization or launch a media probe.

Read-only run history links:
- [Run 37573544151](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37573544151)
- [Original P1 first-segment job 112637586381](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37573544151/job/112637586381)
- [Original P2 first-segment job 113058245257](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37573544151/job/113058245257)

## 2. Source identity preparations — NO LIVE LAUNCH

Created `docs/astra/GUITARTECHS_H1_REVISED_SOURCE_LOCK_REVIEW_DRAFT_V1.json` containing GitHub-reported blob IDs for **17 dormant-workflow inputs** plus **7 offline guard, test and budget files**. The live-file list corresponds to the existing workflow's literal `required={...}` set. It is a **non-launch REVIEW DRAFT**, not a peer-approved source freeze, not a replacement authorization and not a credential or launch file.

Created `astra_backend/guitartechs_training_v10/h1_source_lock_audit_v1.py` and its `test_h1_source_lock_audit_v1.py`. The verifier is completely read-only. It (a) verifies expected file Git blob bytes and rejects absent/symlink/traversal paths; (b) requires the dormant workflow's literal `required` path set to exactly equal the separately named draft paths; (c) fails on missing/mismatched inputs and malformed or empty draft identity, and (d) returns `reviewStatus=PENDING` and `launchPermission=false`. The draft still needs independent approval, upstream four-file identity verification, pinned environment/runner assumptions, dependency closure and a new source-appropriate authorized preflight; it does not protect against a malicious same-branch change to both code and draft.

The blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` was **NOT** created, altered, or simulated via GitHub Actions. The old green run `37852114708` covers previous source only.

## 3. Actual no-media local tests

Local mirror under `/mnt/data/h1prep_local`:

```
cd /mnt/data/h1prep_local
PYTHONPATH=. python -m unittest -v \
  guitartechs_training_v10.test_h1_source_lock_audit_v1 \
  guitartechs_training_v10.test_h1_synthetic_parity_v1 \
  guitartechs_training_v10.test_h1_offline_budget_v1
python -m py_compile \
  guitartechs_training_v10/h1_source_lock_audit_v1.py \
  guitartechs_training_v10/test_h1_source_lock_audit_v1.py
```

**Result: 9 local tests PASS (4 new lock-guard fixtures + 2 prior tiny-network parity + 3 prior static-budget tests).** The test runner is local Torch `2.10.0+cpu`, not the historical pinned Torch `1.11.0+cpu`. No actual frozen V9 model was instantiated and no authentic V7 supervised objective/full `train_arm` / `evaluate` equivalence was proven. `git hash-object` confirmed the exact local files match committed GitHub blob `822214e47e5ed5bbd577fa59a152eafa7c575047` (verifier) and `3957169567aa15367ec03e9198d7d48796602bb5` (tests).

## 4. Next exact work and stop gates

**Allowed offline follow-up:** (1) build synthetic V7-objective / actual full-core failure-path coverage using pinned Torch/source whenever technically feasible without media; (2) independently review source lock and outstanding dependency closure, and design a durable single-use receipt, not a self-attested Boolean; (3) use the existing timing evidence with realistic worst-case acquisition, four H1 evaluations, CPU/disk/RAM peak and cleanup/upload reserve to issue a defensible 300-minute feasibility verdict; (4) update both handoffs after verified progress. No need for Codespaces until an approved operation specifically requires it.

**Do NOT** create/edit the blocked launch JSON, try another tool/provider to evade the rejection, dispatch new workflows or training, spend money, run P3/protected songs/Stage-B, modify frozen V9/V8 results, `main` or Production, change seeds/decoder/thresholds/epoch counts or promote pilot results to independent science. **Await written platform escalation outcome** and technical-review pass before any real launch.

This phase is preparation and evidence collection only. 💚
