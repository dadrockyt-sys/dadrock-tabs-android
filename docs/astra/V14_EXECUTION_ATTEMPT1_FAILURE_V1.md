# V14 empirical execution attempt 1 — INVALID / NON-INTERPRETABLE

Date: 2026-09-29 UTC  
Status: **EXECUTION FAILED AT CONTROL REPRODUCTION GUARD — NO SCIENTIFIC V14 RESULT**

## Run identity

- launch identity: `v14-matched-context-v1-20260929-01`
- workflow run: **36546933952**
- job: **109335463434**
- head: `8487cc3a433df177285582b966d36ed54bec368f`
- run attempt: **1**
- workflow conclusion: **failure**
- uploaded artifacts: **0**

## What passed

The fail-closed validator suite ran before empirical execution:
- **7/7 tests passed**
- frozen schedule identity passed
- frozen recovery gates passed validation
- no gate weakening was detected

## What actually executed

The empirical runner then:
- generated the two synthetic 2-second arms;
- trained exactly **2 models**;
- completed **500 optimizer updates/model**;
- completed **1,000 optimizer updates total**;
- performed synthetic evaluation needed for the control reproduction guard.

No V2B, P1, P2, P3, or other real-audio inference occurred.

## Failure

The runner stopped with:

`RuntimeError: control reproduction failed`

The failure happened after both models had trained, but before a valid V14 result file or model artifact was uploaded.

Therefore this attempt is **not** a V14 scientific pass or fail. It is invalid/non-interpretable.

Do not reconstruct hidden bridge metrics from logs or rerun automatically.

## Root cause

The runner accidentally reused the new V14 schedule root `20260929` for paired batch sampling:

`np.random.RandomState(ROOT + 17001)`

The frozen historical V9 control used root `20260927`, so its paired-batch RNG was:

`np.random.RandomState(20260927 + 17001)`

That changed the control training batch plan, violating the exact-control reproduction requirement.

A second runtime mismatch also existed:
- failed attempt: `ubuntu-latest`, Python 3.11, newly resolved packages;
- historical V9: **ubuntu-22.04**, **Python 3.10.15**, exact `astra_backend/tabcnn_runtime/requirements.lock.txt`.

Because exact reproduction was a hard guard, the abort was correct.

## Corrections prepared, not executed

After freezing the failed attempt, the branch was corrected prospectively:

- V14 schedule seed remains **20260929**.
- V14 batch root is now separately frozen to **20260927**.
- workflow runtime now matches historical V9:
  - ubuntu-22.04
  - Python 3.10.15
  - pip 24.0
  - exact CPU runtime from `requirements.lock.txt`
- future control-reproduction failures now persist a diagnostic JSON before raising;
- a focused test now asserts `BATCH_ROOT == 20260927`.

Corrected blobs:
- runner: `68fd78964acc474337988182fc7c619adff691b2`
- workflow: `8be667ab11f6e1548c227f2d3b1ddb762ecfa408`
- tests: `c0ffdcf95759c0a5e54e95b1f4349f866f704a29`

These corrections have **not** been empirically executed.

## Authorization boundary

The user's empirical authorization was consumed by attempt 1.

There is **no automatic retry**.

A fresh explicit authorization is required before a corrected V14 execution may be launched.

At any future corrected launch:
1. run the focused validator/tests first;
2. require exact historical runtime pins;
3. require exact historical control batch identity;
4. abort before interpretation if control reproduction fails;
5. execute only one corrected attempt;
6. freeze the result and stop.

Main and Production remain unchanged.
