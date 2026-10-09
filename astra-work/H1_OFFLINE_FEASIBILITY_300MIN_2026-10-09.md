# Astra H1 — independent read-only 300-minute feasibility assessment

**Date:** 2026-10-09. **Branch:** `astra-work`. **Decision: NO-GO / insufficient evidence for a 300-minute, no-paid-compute H1 launch.** This is a technical feasibility review, **not** an authorization, training execution, or claim that H1 cannot possibly fit. Written OpenAI Support case **#16795041** clearance is separately pending.

## Evidence inspected (no new jobs or media)

- Dormant workflow: [`.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml`](../.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml), Git blob **`90e8168fc1ca40738ba07291ca1001a36718f4e3`**; GitHub `ubuntu-22.04` runner, **300-minute job timeout**, 160 optimization steps and 20 epochs per arm/fold; two arms × two P1/P2 folds. It acquires **eight P1/P2 archive files sequentially** using two URLs, each with `curl --max-time 300 --retry 0`. It is **inactive without the blocked launch JSON**; no workflow or preflight dispatched.
- Original V9 Actions evidence: `docs/astra/GUITARTECHS_H1_EXISTING_ACTIONS_TIMING_EVIDENCE_V1.json`, Git blob **`9ac43020268cc4be624c45b66343a283d8081e92`**; historical run **37573544151**, jobs **112637586381**, **113058245257**, **112986816044**, **113346922946**. These are **not H1 timings**. Epoch-20 intervals may include existing diagnostics; epoch-1000 terminal intervals are evaluation **plus** reporting and are not isolated H1 full V4 assessments.
- Existing offline-only budget tool: `astra_backend/guitartechs_training_v10/h1_offline_budget_v1.py` with its tests. It correctly records **`readiness=UNPROVEN_BLOCKED`** and requires twelve provenance-bearing stage durations. We did not execute this tool against an actual full checkout.
- Reproducible, **non-launch** arithmetic receipt in `astra-work/H1_FEASIBILITY_READ_ONLY_2026-10-09.json`. Calculations were checked using Python 3.13.5 and `decimal.Decimal`, including the prior recorded subtotal and the number/bytes of the eight archives; **no tests of actual H1 compute were run**.
- GitHub [standard-hosted-runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) document **4 vCPU, 16 GB RAM, 14 GB SSD** for a standard **public-repository** `ubuntu-22.04` VM. The repository's GitHub API indicates `private=false`. These are **nominal** runner specs, not proof of free usable disk/RAM, timing consistency, compute quota or actual preinstalled image footprint.

## Computed, historical V9-derived estimate — **NOT a bound**

| Stage / conditional proxy | Seconds | Minutes | Evidence quality |
| --- | ---: | ---: | --- |
| Maximum *observed* single historical V9 preparation interval | 3,429.715 | 57.162 | Prior V9 job; includes its historical archive acquisition/preparation |
| Two original fold-specific epoch-20 intervals, each repeated for both arms | 3,900.648 | 65.011 | Extrapolated V9 first-20 proxy, **not four H1 measured arm durations** |
| Two original V9 terminal eval/report intervals, each repeated for both arms | 3,692.806 | 61.547 | Extrapolated V9 evaluation/report proxy, **not four H1 evaluations** |
| **Historical conditional subtotal** | **11,023.169** | **183.719** | Illustration only |
| **Nominal difference versus 18,000-second ceiling** | **6,976.831** | **116.281** | Not validated spare capacity; unknown stages consume it |

The calculation is identical to the existing documented **11,023.169-second** illustration. **Do not treat this as a proven minimum or a safe upper bound.** There is no measured H1 full V4 admission/evaluation time, original-control SHA reproducibility, source dependency/install time, pinned upstream preparation overhead, gradient instrumentation overhead, peak disk/RAM, upload/cleanup or failure reserve.

## Sensitivity to revised H1 training + evaluation runtime

This table holds the historical V9 maximum preparation proxy **fixed at 3,429.715 seconds**, multiplies only the V9-derived **7,593.454 seconds** for training plus four evaluations, and subtracts from **300 minutes**. The multipliers are **hypothetical stress factors**, not measured H1 slowdown estimates.

| Hypothetical training/evaluation multiplier | Conditional total | Unallocated before unknown stages |
| --- | ---: | ---: |
| 1× | 183.719 min | 116.281 min |
| 1.25× | 215.359 min | 84.641 min |
| 1.5× | 246.998 min | 53.002 min |
| 1.75× | 278.638 min | 21.362 min |
| 2× | **310.277 min** | **−10.277 min (already exceeds limit)** |

The formal zero-overhead break-even multiplier would be approximately **1.919×**; any positive unmeasured costs lower that threshold. For orientation only, reserving a *hypothetical* additional **30 minutes** (not an approved reserve) lowers it to approximately **1.682×**; this is a planning stress exercise, not an accepted margin.

## Archive transfer and storage: two distinct STOP uncertainties

**Transfer:** 8 archives × 2 URLs/archive × 300 seconds/request = **4,800 seconds = 80 minutes for archive HTTP requests alone**. Other downloads (dependencies/upstream source), extraction, SHA checks, preparation, training, evaluation and cleanup are **outside** that figure. The historical maximum preparation interval already encompassed its own download/preparation. Therefore **adding 80 minutes directly to the 183.72-minute illustration would double count unknown overlapping activities**, and is not a justified worst-case.

One **alternative conditional envelope** starts instead from the 80-minute upper bound on archive HTTP *requests*, plus the unscaled V9 training/evaluation proxy (**126.558 minutes**), totaling **206.558 minutes**; this leaves **93.442 minutes** for all remaining **non-HTTP** prep, environment/setup, upstream acquisition, diagnostics, filesystems, artifacts and reserve. It is a scenario, **not a proven upper bound** (H1 CPU/evaluation time itself can change, and other stage bounds are unknown).

**Disk/RAM:** Eight compressed archive entries total **4,004,045,267 bytes = 3.729 GiB**; the largest single compressed archive is **1,150,819,056 bytes = 1.072 GiB**. The workflow processes archives serially and deletes individual downloaded files, but prepared features/labels accumulate. Disk peak also includes unpacked audio/current archive, repository, installed wheels/packages and caches, working arrays and output artifacts. On a nominal **14 GB SSD / 16 GB RAM** public standard runner, neither **effective free disk** nor decompressed/feature-memory peak has been measured. A four-gigabyte *total* archive manifest is **not** proof that prepared outputs fit.

## Stage-evidence ledger and explicit non-readiness

The existing `h1_offline_budget_v1.py` requires **12** separately attributable stages: environment/dependencies; source acquisition; archives/preparation; original fold-1 and fold-2 training; treatment fold-1 and fold-2 training; original fold-1 and fold-2 evaluation; treatment fold-1 and fold-2 evaluation; upload/cleanup reserve. This review supplies **no authoritative measured H1 timings** for these twelve stages; historic V9 durations are **proxies only**. CPU/RAM/disk peak, network failure reserve, V4 admission-trace completeness, and runner/environment comparability also lack independent evidence.

**Readiness assessment:** time **UNPROVEN**; disk **UNPROVEN**; RAM **UNPROVEN**; 4 revised full-fold evaluation durations **UNMEASURED**; pinned runtime/source independent review **PENDING**; globally durable atomic single-use **NOT ESTABLISHED**; written OpenAI Support approval **NOT RECEIVED**. The 300-minute GitHub timeout is only a **stop-on-overrun limit**, not evidence the study can complete.

## Exact next permitted steps (offline-only)

1. **Independent budget desk review:** Validate historic V9 job-log interval boundaries and run IDs; document the distinct existing-setup and expected-H1 workload costs without adding overlapping network/preparation durations. Keep the actual science frozen (20 epochs/arm/fold, two arms × two folds, 160 steps).
2. **Storage capacity model:** Use existing permitted manifests/source metadata (not raw protected or real audio) to derive an independently reviewed **upper bound** for prepared float32 features and int16 labels by total frames; model simultaneously live archive, extraction, prep arrays, package install caches, and artifact outputs. Require headroom below effective measured free disk and RAM. If no trustworthy input metadata exists, remain **UNPROVEN** rather than inventing bytes.
3. **Environment and stage evidence:** Review pinned install and full V4 admission/evaluation overhead using existing historical artifacts or a separately allowed **synthetic-only** pinned offline probe. Do **not** dispatch the H1 Actions/preflight, download P1/P2 media, or initiate paid compute to collect timing evidence.
4. **Require reviewer-signed full budget and safety gates** before any future launch proposal. If worst-case verified stage bounds cannot be established under **≤18,000 seconds** and actual runner disk/RAM, retain **NO-GO**; do not increase CPU budget or switch to paid/larger runners as a shortcut.
5. Await an explicit **written** Support outcome for case **#16795041**. The blocked JSON file remains absent and must not be created through another tool or workflow; our read-only assessment cannot grant safety clearance.

**No-GO means insufficient evidence to authorize launching, not that the experiment is scientifically or technically impossible.** This document changes only offline-review records, not the dormant workflow, user authorization, source lock, scientific protocol, training inputs or `main`. Do **not** retry the separately safety-blocked `docs/checkpoints/CURRENT_STATE.md` write.
