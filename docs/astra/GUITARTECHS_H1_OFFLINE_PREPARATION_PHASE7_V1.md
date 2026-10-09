# Guitar-TECHS H1 Phase 7 — pre-optimizer prepared-data guard and full remote source-blob audit

**2026-10-08, branch `astra-work` · OFFLINE PREPARATION ONLY · NO REAL H1 LAUNCH.** Continued from verified Phase-6 commit `000404e0c56f4533ee9fa845edec8f819ee9cada`. OpenAI Support's review of the safety-rejected training launch remains unresolved; there is **no approved workaround through Codespaces, Codex, GitHub UI or alternate APIs**. No Codespaces session, new Actions/preflight dispatch, real P1/P2 media download, inference, model checkpoint, optimizer updates or spending occurred.

## Identified pre-optimizer input gap

Before Phase 7, `run_h1_20epoch_paired_pilot_v1.py` accepted any hash-matched `.npy` arrays if their **shapes alone** were 192×T and 6×T. That did not independently reject nonfinite CQT values, unexpected feature/label dtypes, or invalid fret/target classes after preparation, which could later produce nonfinite losses or ambiguous training failures.

**New ordinary source module:** `astra_backend/guitartechs_training_v10/h1_prepared_array_guard_v1.py` validates, before the first optimizer call, each frozen-manifest prepared pair:
- exact 192×T float32 feature and 6×T int16 label shapes/dtypes, with at least 200 frames (matching frozen 200-frame sampler);
- no NaN or infinity anywhere in features;
- labels only `-100` (mask), `-1` (silence), or frets 0 through 19;
- `np.load(..., allow_pickle=False, mmap_mode='r')`, 4,096-frame read-only chunking with small bounded working memory and explicit fail-closed errors on corrupted `.npy`.

**Driver integration:** replaced the previous shape-only loop with `prepared.verify_prepared_pair(row['_features'], row['_labels'], row['frames'])`, after the independently pinned population/hash guard and **before** creating the scalar progress journal or training a model. A failed preparation check therefore causes **zero optimizer steps and no journal**, a deliberately fail-closed early termination; it is not a complete recorded failure receipt. Existing frozen P1/P2 capture population, original-V9 model objective, 20 epochs, two arms/two folds, 160-step cap, masks and thresholds are unchanged.

**New tests:** `test_h1_prepared_array_guard_v1.py` uses synthetic dummy `.npy` pairs with >4096 frames and confirms valid data pass and incorrect dtypes, NaN at the final chunk, illegal fret 20, frame/shape mismatch and unreadable `.npy` fail. Added a driver-level AST mock that requires semantic rejection before any mocked train call or journal; this new driver-level test has been **committed but not executed in the available local mirror**.

Updated the **dormant** `.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml` required source-blobs allowlist to include the new guard. The trigger remains exactly the previously blocked launch JSON path; that file **is still absent** and was not created/edited. Current workflow blob `90e8168fc1ca40738ba07291ca1001a36718f4e3`. No new real-data workflow execution/preflight.

## Verification performed

**Actual local tests** (no internet/data; Python 3.13, Torch 2.10 CPU, earlier V7/V9 modules manually mirrored):

```bash
cd /mnt/data/h1prep_local
PYTHONPATH=. python -m unittest -q \
  guitartechs_training_v10.test_h1_static_import_closure_v1 \
  guitartechs_training_v10.test_h1_source_lock_audit_v1 \
  guitartechs_training_v10.test_h1_offline_budget_v1 \
  guitartechs_training_v10.test_h1_real_v7_objective_parity_v1 \
  guitartechs_training_v10.test_h1_core_failclosed_v1 \
  guitartechs_training_v10.test_h1_launch_ancestry_guard_v1 \
  guitartechs_training_v10.test_h1_prepared_array_guard_v1 \
  guitartechs_training_v10.test_h1_synthetic_parity_v1
```

**29 local tests PASS** (27 from Phase 6/this increment's combined suite plus 2 original tiny-model synthetic parity fixtures), in ~2 seconds. Full remote branch and pinned Torch 1.11 runtime are **not** what these local tests ran; do not claim full model parity.

Local `git hash-object` for both new files **exactly matches remote Git blobs**: guard `b589b7118e2d23ec3d1557195954c65a7727a928`; tests `02cd76361e979a2aaf602e230441f5bd5f9191cb`. The revised driver blob is `ad38a33b87b85f676f6342eeaec569a031a327f2`; revised driver/mock test blob is `9520996b491569df5320423d92d4d615546ef268`. These latter sources were inspected and pinned, **not** exercised via the complete GitHub suite.

**Complete remote identity audit of the current draft map:** fetched the blob SHA for each of **22 required workflow inputs + 14 auxiliary offline files**, through independent read-only GitHub file calls on `astra-work`. **36/36 current remote blob IDs matched** `docs/astra/GUITARTECHS_H1_REVISED_SOURCE_LOCK_REVIEW_DRAFT_V1.json`. This verifies the present branch snapshot matches the draft; it is **not** an independently approved source freeze, a full import-closure/dynamic-dependency proof, or authorization to dispatch training.

A separate attempt to obtain upstream source via local runtime network is unavailable in this sandbox, and only Python 3.13/Torch 2.10 is installed. The existing full-`TemporalTabCNNV9` synthetic two-step parity CLI remains **prepared but NOT RUN under pinned Python 3.10.15/Torch 1.11.0+cpu**. No Codespaces hours were consumed to bypass that limitation.

## Remaining independent STOP gates

1. **Pinned full-model synthetic parity execution:** on an explicitly permitted, ephemeral, no-media Python 3.10.15/Torch 1.11+cpu environment with a source-tree verified against frozen four upstream AMT-Tools Git blobs plus three init files. Run only `h1_full_model_synthetic_parity_v1.py` without any launch JSON/Actions, and check the original-vs-H1 two-step SHA, optimizer, RNG and probes. Historical original P1/P2 epoch-20 SHA/F1 remains unknowable without authorized real training and therefore is NOT resolved here.
2. **Independent source security review** of 22+14 draft, executable dynamic imports, external packages, source-signature/commit identity, followed by an approved immutably frozen reviewed manifest; mutable same-branch source maps are not an independent authority.
3. **Durable global one-use launch authorization** against duplicate first-attempt jobs/force-push/branch rewrite; current `GITHUB_RUN_ATTEMPT=1` and ancestry first-add checks reject simple edits but do not solve cross-run consumption.
4. **300-minute compute feasibility:** revised archive HTTP limit 80 min, historical V9 partial illustration ~184 min, but no validated end-to-end H1 CPU/RAM/storage ceiling, hardware and four H1 evaluations, retries/unpack/CQT preparation, artifact/cleanup reserve. Do not add worst-case 80 min as if independent of historical measured preparation (which included downloads).
5. **Written platform escalation decision:** no evidence OpenAI Support has removed or approved the blocked launch action. Do not reroute through Codespaces/Codex/UI or create the blocked file.

**Historical checkpoint caution:** A previous attempt to update `docs/checkpoints/CURRENT_STATE.md` was blocked by OpenAI safety checks. This increment **does not retry that write or use another route**. Only `astra-work/CURRENT_STATE.md` is the current mutable handoff destination.

**Preserve:** no P3, protected song material, Stage B, paid compute, new real capture/vendor contact, `main` or Production changes, trained-weight exports, threshold/seed/decoder choices, or claims of new scientific improvement. Historical V9=FAIL/F1=0 and V8 clean baseline macro-F1=0.24680584415601026 remain authoritative. 💚
