# H1 Phase 2 — offline preparation while platform escalation is pending

**Date:** 2026-10-08. **Branch:** `astra-work`. **Decision:** `BLOCKED` for real training and any attempt to create/edit the safety-rejected launch JSON. **No Codespaces hours**, no new GitHub Actions dispatch, no data access, no optimizer steps or model checkpoint creation in this increment.

This is a continuation of `docs/astra/GUITARTECHS_H1_OFFLINE_HARDENING_PHASE1_V1.md`; all original V9/V8 and scientific/frozen results remain unchanged.

## Tested source additions

1. `astra_backend/guitartechs_training_v10/test_h1_synthetic_parity_v1.py`: a tiny, **randomly initialized synthetic network** with the frozen `paired_tensor_views` and `symmetric_kl_consistency` helpers. Compares two Adadelta updates with and without first-microbatch `torch.autograd.grad` probes. Checks bitwise model parameter states, optimizer state, step-level hashes and Torch RNG states. A distinct normalized-KL objective takes a different parameter path, as expected. Uses exact 200-frame/6-string/21-class output dimensions, the V9-style view-seed recipe, microbatch accumulation and the original 0.10 KL multiplier. **Important limitation:** uses a lightweight supervised CE stand-in and *not* the original V7 loss or full original V9 network. This demonstrates the probe need not perturb this synthetic network; it **does not establish** exact original control epoch-20 SHA reproduction or real-run equivalence.
2. `astra_backend/guitartechs_training_v10/h1_offline_budget_v1.py` and `test_h1_offline_budget_v1.py`: no-network, read-only parsing of the existing inactive H1 workflow, with frozen archive count/byte checks, retries audit and a strictly evidence-gated stage feasibility calculator. Missing any of the 12 required timing stages returns `UNPROVEN_BLOCKED`; exceeding the 300-minute ceiling reports `INFEASIBLE_BOUND`. Even complete timings below the ceiling do **not** automatically confer launch readiness; disk/RAM, hardware reproducibility and source evidence require separate review.

**Actual local command:** `cd /mnt/data/h1prep_local && PYTHONPATH=. python -m unittest -v guitartechs_training_v10.test_h1_synthetic_parity_v1 guitartechs_training_v10.test_h1_offline_budget_v1` — **5 tests passed**, local Torch `2.10.0+cpu`, Python stdlib; no media/model checkpoints/network. The parity fixture used a locally mirrored copy of the frozen paired-view functions; actual code must be retested under the historical pinned Torch `1.11.0+cpu` environment. No CI run was launched. `git hash-object` verified the exact local test/audit files against GitHub blobs: parity `9975a9b62d5b62300ae6adce7da4f7011581b75b`; audit `9c3ef85aec7c69b7a8a941acd39a790bb013a14b`; audit tests `09840b703d237de749a1e39458ad4c16f910b474`.

## Budget risk verified directly from the inactive workflow

- Eight frozen P1/P2 archive entries: **4,004,045,267 compressed bytes** (~3.73 GiB), excluding unpacked data, derived CQT, Python/Torch dependencies, tmp partial downloads and filesystem overhead.
- Current workflow's **per-archive** download loop: two URLs × five outer attempts per URL × up to three inner curl requests (`--retry 2`) × up to 1,800 seconds per request (`--max-time 1800`). The pessimistic transfer-only allowance can reach **54,000 seconds (15 hours) per archive**, **432,000 seconds (120 hours) across eight archives**, before sleep, preparation, two original controls, two treatment folds, four evaluations, upload and cleanup. This is a ceiling of the nested retry configuration, not a forecast of expected network time or a claim all retries would actually occur.
- One GitHub Actions job has a frozen limit of **18,000 seconds (300 minutes)**. The old green preflight did not test the full data-preparation/4-evaluation path and predates the revised source.
- **Result:** Runtime/disk/memory feasibility remains **UNPROVEN**. Do not increase the authorized budget, cut folds/epochs, obtain new media timing runs, or infer feasibility by comparing theoretical maximum retries to likely network success. A separately reviewed bound for acquisition and a historical measurement-based stage schedule are still needed.

## Strict gates before considering a launch

**Platform clearance (independent):** Support has escalated the rejected GitHub training-launch JSON creation and has **not supplied confirmed clearance**. GitHub UI, Codex, Codespaces, alternative APIs and user authorizations must not be used to get around that block; evaluate Support's written response first.

**Technical readiness (independent):** (a) actual full V9 vs H1 control loss/probe/RNG/optimizer-state equivalence on synthetic fixtures under pinned dependencies; (b) complete mocked train_arm/evaluate failure schema tests; (c) independently frozen exhaustive source and data lineage bound to revised preflight; (d) **durable one-use** authorization consumption beyond `GITHUB_RUN_ATTEMPT=1` and a Boolean `singleUse`; (e) evidence-backed 300-minute runner budget including acquisition, preparation, all four validations, resource peaks, cleanup and artifact reserve; (f) independent review of the revised workflow and any prospective preflight. No existing success run of the *earlier* source proves these revised checks.

**Proposed low-Codespaces approach, only if Support confirms it is permitted and technical readiness passes:** finish code/tests/docs within ChatGPT + GitHub; use a short, smallest practical Codespace session only for explicitly authorized final checks. Prefer a separately authorized GitHub Actions CPU runner for longer training, then stop the Codespace immediately. **This is a conditional planning suggestion, not launch authorization.** Do not create a launch receipt or training run now.

## Exact next offline task

1. Extend real `h1_pilot_core_v1.train_arm` and `evaluate` synthetic/stubbed failure paths and original V9 equivalence under the actual pinned environment; keep no-media and no historical checkpoint use.
2. Gather **existing** action log stage-duration and resource evidence (read-only) to populate the budget calculator. Distinguish unknown values explicitly; do not substitute illustrative timings or run a media probe.
3. Design/review immutable launch identity and durable consumption independently; no implementation that generates the currently blocked launch receipt.
4. After the escalation response, reconcile authorized execution path with the remaining code/scientific/compute stop gates. Do **not** dispatch automatically.

Frozen scope: one-factor 20 epochs × 2 arms × 2 P1/P2 folds, maximum 160 optimizer updates, maximum 300 non-paid CPU minutes; no P3, protected songs, Stage-B holdout, third-party contact, paid infrastructure, extra runs, alternate seeds/thresholds/decoder, exported trained weights, Production or `main` changes. Preserved V9 failure and V8 clean comparator remain authoritative.
