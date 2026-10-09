# H1 Phase 8 — offline single-use threat review and budget evidence (2026-10-09)

**Status: REVIEW ONLY / REAL H1 LAUNCH BLOCKED.** Branch: `astra-work`. OpenAI Support case **#16795041** is pending a written decision. This document and its companion test are **not** an implementation of a launch gate, a new launch artifact, an approved source lock, or permission to run workflows or access real development media.

## Inputs and identity

- Latest primary handoff before this increment: `astra-work/CURRENT_STATE.md` (Support follow-up commit `51f7ff01cb89f6290feaf83fb92dd418ff6379c2`).
- Existing dormant workflow: `.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml`, Git blob `90e8168fc1ca40738ba07291ca1001a36718f4e3`. Its push-path trigger is **only** the safety-blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json`, which remains absent. No workflow was dispatched for this review.
- Draft lock: `docs/astra/GUITARTECHS_H1_REVISED_SOURCE_LOCK_REVIEW_DRAFT_V1.json`, Git blob `f778836783c831224b5467d304353b9c73f0496e`. Independently compared all **36 path/blob pairs** (22 live sources + 14 auxiliary files) with the GitHub tree for `astra-work`; **36/36 match**, and the API tree was **not truncated** (8,201 entries). This is snapshot integrity only; independent approval, import closure, and external dependency verification remain unproven.
- Frozen historical timing receipt: `docs/astra/GUITARTECHS_H1_EXISTING_ACTIONS_TIMING_EVIDENCE_V1.json`, blob `9ac43020268cc4be624c45b66343a283d8081e92`. These are **prior V9 Actions log intervals, not new H1 measurements**.
- Companion test: `astra-work/h1_one_use_synthetic_review_v1.py`, Git blob `8723d1e526ada7c735f602444ecfcf0880ab57d3`, exactly matched the locally executed bytes via `git hash-object`. It uses a wholly unrelated `synthetic-only-claim-marker.txt` inside disposable Git repositories; it never references or creates the blocked trigger file.

## Actual offline test execution

Environment: local Python **3.13.5**, Git **2.47.3**, isolated temporary directories; no repository checkout, network, Codespaces, GitHub Actions, audio, training or model inference. Command:

```bash
python astra-work/h1_one_use_synthetic_review_v1.py
```

The exact locally tested file, matched above to the committed Git blob, finished **5 tests PASS / 0 failures / 0 errors** after correcting an initial synthetic Git-orphan fixture setup mistake. The five tests cover:

1. New synthetic marker passes the current history-check abstraction, but a later edit and a second attempt **within one run** fail.
2. Two independent first-attempt **events referencing the identical first-add commit** both pass the history-check abstraction. `GITHUB_RUN_ATTEMPT=1` is per-run, not global.
3. A separate orphan-root Git history containing a first addition can pass again. A reachable-history count is not durable across history replacement.
4. A toy compare-and-set `UNUSED→CONSUMED` state rejects a second claim. **This is an illustrative model, not implemented in any trusted external backend**, and does not establish actual race safety.
5. Historical runtime arithmetic reproduces the illustrative gap under the five-hour ceiling, **not** a safe execution budget.

**Interpretation:** These synthetic counterexamples reinforce the existing STOP gate. Branch ancestry, event attempt count and workflow concurrency are not equivalent to a globally durable single-use claim. A real solution would require an independently administered, shared, tamper-resistant and atomic one-use consumption service with a stable operation identity; fail closed on errors, missing state, ambiguous results and already-consumed claims. Do not implement or attach it to the blocked workflow while platform review is pending. External design and independent security approval remain open.

## Read-only runtime and resource ledger

The dormant workflow configures `timeout-minutes: 300`, two URL choices for each of eight exact P1/P2 archives, with one `curl --max-time 300 --retry 0` attempt per URL. The **HTTP request-time ceiling only** is `8 × 2 × 300 = 4,800 seconds = 80 minutes`; it is **not** the archive-preparation or job-completion bound. Eight frozen compressed inputs total **4,004,045,267 bytes** (~3.73 GiB), before extraction and feature arrays.

| Historical V9 illustration, previously recorded | Seconds | What it means |
| --- | ---: | --- |
| Maximum observed single preparation | 3,429.715 | Historical original-V9 prepare interval, already encompasses its own download/prep activities |
| Two control/treatment repetitions of both fold-specific early-20 intervals | 3,900.648 | Extrapolation, not measured two-arm H1 compute |
| Two repetitions of both fold-specific terminal evaluation/report intervals | 3,692.806 | Different V9 job segments, not four observed H1 evaluations |
| **Arithmetic subtotal** | **11,023.169** | **183.7195 minutes** illustrative only |
| **Nominal unallocated difference to 18,000-second ceiling** | **6,976.831** | **116.2805 minutes, not verified slack or reserve** |

The 80-minute theoretical HTTP bound **must not simply be added** to historical preparation (double-counting would be possible). Conversely, historical V9 timing **cannot bound** the fresh H1 run: revised four full-fold evaluations and V4 admission diagnostics, initial gradient probes, pinned dependency install, upstream sources, environmental skew, archive retry/failure behavior, SHA verification, CQT preparation, disk/RAM peaks, artifact upload/cleanup and a failure reserve still lack end-to-end evidence. A real worst-case under **≤300 minutes** remains **UNPROVEN**. No increase in compute budget or paid fallback was authorized.

## Next independently permissible work and hard stops

1. Seek a **permitted, complete local checkout** for the exact no-media H1 stdlib test suite and report actual results; current sandbox cannot resolve `github.com` for cloning. Local Python 3.13.5/Torch 2.10+cpu does **not** satisfy frozen Python 3.10.15/Torch 1.11.0+cpu, so pinned full-`TemporalTabCNNV9` parity is **NOT RUN**.
2. When a full checkout is available, perform read-only static/dynamic local import closure and verify the four pinned upstream AMT-Tools blobs and generated init files; keep the source lock explicitly **DRAFT** until independent authority approves it.
3. Obtain independent review of cross-run atomic one-use design, source integrity and a realistic complete wall-time/CPU/RAM/disk feasibility ledger. Today's five synthetic tests are *negative evidence* about the existing scheme, not a production validation.
4. Await the actual **written OpenAI Support escalation outcome**; review incoming reply before choosing a further action. If the blocked JSON itself is requested, ask Support for an explicitly permitted *non-executing submission method*. No alternate-tool workaround.

**STOP:** No creation/edit of the blocked launch JSON; no Actions/preflight, real P1/P2 downloads, training, inference, paid compute, source/model weights export, P3/protected song/Stage-B access, changes to `main`/Production, frozen V8/V9 science or the separately blocked `docs/checkpoints/CURRENT_STATE.md` write. This increment does not claim full-repository tests, pinned synthetic parity, independent review, Support clearance or real training.
