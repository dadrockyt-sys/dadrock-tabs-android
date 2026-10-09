# H1 Phase 5 — transitive source-pinning correction (offline)

**Date:** 2026-10-08. **Branch:** `astra-work`. **Status:** `SOURCE_CLOSURE_IMPROVED / PLATFORM_LAUNCH_BLOCKED`. This is ordinary, reversible source/test/documentation work following Phase 4; OpenAI Support's escalation remains outstanding. No Codespaces session, new GitHub Actions dispatch, training-launch JSON creation/change, real audio access, inference or real optimizer steps.

## Concrete finding

The dormant H1 workflow's `sourceBlobs` allowlist covered 17 files, including `guitartechs_training_v9/model.py`, `guitartechs_training_v7/objective_decoder.py`, `guitartechs_training_v8/decoder.py`, and `guitartechs_real_training/real_training.py`. GitHub inspection showed additional **repository-local transitive imports** that were **not required in the allowlist**:

| Required transitive import | Pinned Git blob |
| --- | --- |
| `astra_backend/guitartechs_training_v7/model.py` | `cdb80274494782fc42774f3dd5c6859e9beb97d3` |
| `astra_backend/guitartechs_training_v6/model.py` | `78a17dd174bd86e804af0e9c75056055d6048295` |
| `astra_backend/guitartechs_training_v4/objective_decoder.py` | `b9a96f6b256de52bfbb5076482a03263415213cb` |
| `astra_backend/tabcnn_runtime/preprocessing.py` | `e1d251a341b811b1b8e2df97d78b754d3379046b` |

Chain examples: V9 model → V7 model → V6 model; frozen V8 decoder/post-V9 admission audit → V4 objective decoder; real-data preparation `real_training.py` explicitly adds `tabcnn_runtime` to `sys.path` and imports `preprocessing`. Pinning these matters for exact model architecture, fixed V4/V8 evaluation and deterministic feature preparation. This finding does **not** establish full dependency closure.

## Change set

1. **Updated the existing *dormant* `.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml` source allowlist** to require all four transitive files. No change to event trigger, launch-file name, budgets, P1/P2 datasets, original V9 scientific files, model training objective, or permission surface. Current workflow Git blob: `4fb88dc9eeebb62cbd13ac160d5e4536bd855f7e`.
2. Added `astra_backend/guitartechs_training_v10/h1_static_import_closure_v1.py`. It reuses the existing offline draft blob verifier, parses Python files with the standard-library AST, resolves internal absolute and relative static imports plus the explicit frozen `preprocessing` sys.path mapping, and **fails closed** when a present, statically imported repository file is not listed in the workflow's exact pinned-source set. Returns `launchPermission=false` even when the fixture passes. Dynamic imports, installed packages, upstream AMT-Tools sources, runtime environment and independent review are **not** covered.
3. Added `astra_backend/guitartechs_training_v10/test_h1_static_import_closure_v1.py` — tests valid pin coverage, missing pin when the source and workflow allowlist otherwise match, relative/preprocessing imports, and byte mutation. Tests use tiny synthetic module trees and **no media/network**.
4. Updated `docs/astra/GUITARTECHS_H1_REVISED_SOURCE_LOCK_REVIEW_DRAFT_V1.json` to **21 required workflow files + 11 offline verifier/test/budget files**. This is still a `DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION`; editing a draft in the same branch is not an independent trust anchor and must not substitute for official review.

## Actual test evidence

Locally re-executed the available mirror suite in `/mnt/data/h1prep_local` using Python 3.13 and Torch 2.10 CPU:

```bash
PYTHONPATH=. python -m unittest -q \
  guitartechs_training_v10.test_h1_static_import_closure_v1 \
  guitartechs_training_v10.test_h1_source_lock_audit_v1 \
  guitartechs_training_v10.test_h1_offline_budget_v1 \
  guitartechs_training_v10.test_h1_real_v7_objective_parity_v1 \
  guitartechs_training_v10.test_h1_core_failclosed_v1
python -m py_compile \
  guitartechs_training_v10/h1_source_lock_audit_v1.py \
  guitartechs_training_v10/h1_static_import_closure_v1.py \
  guitartechs_training_v10/test_h1_static_import_closure_v1.py
```

**Observed: 20 local tests passed** (4 new static-closure + 4 lock + 3 budget + 2 tiny V7-expression parity + 7 core mock tests). The local tree includes manually mirrored historical V7/V9/H1 functions and is **not a complete, byte-identical repository checkout**; earlier fixture limitations remain. The **exact two new files** were byte-verified via `git hash-object` against GitHub blobs:
- checker: `e5aa04aa395feb76254d7a383558e1bca2ac2f5c`
- tests: `d7694a517f1cdfae6172fcb1682032f7e2965132`

Actual live-repository import-closure check **was not executed** because a complete checkout is unavailable in the no-network local environment. It is designed to be run read-only on a permitted full checkout. No new GitHub Actions tests, preflight or real-data runs were dispatched.

## Exact subsequent preparation

1. In a **permitted offline, no-media full repository checkout**, run the static closure verifier against the draft lock. Resolve additional missing imports, symlink/dynamic-import uncertainties and verify the original external TabCNN four-source hashes and installed package lock from independent evidence. Repeat only nonlaunch source/test/documentation updates, with frozen V9/V8 results untouched.
2. Test the full frozen `TemporalTabCNNV9` original-loss/optimizer/RNG controls with synthetic fixtures on a pinned Torch `1.11.0+cpu` runtime. Current tiny local Torch `2.10.0+cpu` objective tests are **not** a true full-model or epoch-20 real-data SHA proof.
3. Independently review the source-lock and durable, cross-run single-use launch semantics. A file's `singleUse=true` Boolean plus `GITHUB_RUN_ATTEMPT=1` cannot guarantee no second run from a second push.
4. Produce an evidence-backed CPU/disk/RAM and retry-bounded 300-minute H1 budget that includes setup, preparation, all four original/treatment evaluations and cleanup/upload. Prior historical ~184-minute illustration is **not** a verified upper bound.
5. **Await OpenAI Support's written escalation outcome.** A new execution surface does not itself authorize a safety-rejected launch. Use Codespaces only for necessary separately permitted work; **zero Codespaces hours used in this phase**.

**Preserved hard stops:** no `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` mutation, workflow dispatch, media/P3/protected-song/Stage-B/paid compute, original V9/V8 modifications, production or `main` changes, checkpoint/seed/threshold rescue, or scientific advancement claims. 💚
