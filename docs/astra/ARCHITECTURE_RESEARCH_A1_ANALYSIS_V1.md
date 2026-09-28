# Astra Architecture Research A1 — result analysis

Date: 2026-09-28  
Status: **A1 FAILED FROZEN GATE — NO AUTOMATIC A2**

## Experiment

A1 tested one architectural change only: the frozen S11 shared 128-unit encoder was replaced by separate state and onset encoders of the same size.

Unchanged:
- context5 / 960-dimensional input;
- state and onset heads;
- loss weights;
- 32/32/32/32 sampler;
- Adam 0.003;
- 500 steps/model;
- seeds;
- 0.50/0.50 thresholds;
- decoder/evaluator;
- V2 source-domain training support;
- ordinary S9 test;
- V3 challenge.

Execution:
- run **36492748299**
- job **109164963801**
- artifact **11002106213**
- digest `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`
- result JSON SHA-256 `090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3`
- **3 models / 1,500 optimizer steps**
- P1/P2/P3 **none**
- automatic retry **false**

## Scientific outcome

**FAIL.**

Only two preregistered criteria failed.

### 1. Joint-admission architecture-effect floor

A1 improved ordinary joint admission versus the frozen S11 intervention in every seed:

- +0.03876
- +0.03101
- +0.04651

Mean:
- **+0.0387597**

Frozen requirement:
- **>= +0.0400000**

The result misses the gate by approximately **0.0012403**.

The threshold remains unchanged. This is a failure, not a rounded pass.

### 2. Challenge recall versus frozen S11 control

A1 challenge recall deltas versus the frozen S11 control:

- seed 20260927: **-0.003876**
- seed 20260928: **+0.077519**
- seed 20260929: **+0.054264**

Frozen requirement:
- positive in **3/3** seeds.

Observed:
- positive in **2/3**.

## Strong supported effect

The structural hypothesis received meaningful support despite the gate failure.

### State admission versus shared-encoder intervention

Ordinary:
- mean **+0.09302**
- minimum **+0.06977**
- positive **3/3**

V3 challenge:
- mean **+0.07235**
- minimum **+0.02713**
- positive **3/3**

This is consistent with shared-encoder task interference being a real synthetic-model factor, although it does not prove a real-domain causal mechanism.

### Joint admission

A1 improved joint admission over the shared-encoder intervention in all seeds:

Ordinary:
- mean **+0.03876**

Challenge:
- mean **+0.02842**

### Onset behavior

A1 did not purchase state improvement by collapsing onset F1.

Versus frozen S11 intervention:
- ordinary onset F1 mean **+0.03318**, positive 3/3;
- challenge onset F1 mean **+0.05130**, positive 3/3;
- challenge precision mean **+0.09067**, positive 3/3.

Versus frozen S11 control:
- challenge onset F1 mean **+0.11244**, positive 3/3;
- challenge precision mean **+0.20505**, positive 3/3.

Negative-only false positives:
- ordinary **0.0 events/sec in all seeds**
- V3 challenge **0.0 events/sec in all seeds**

## What A1 does not establish

Do not conclude:
- that the +0.04 joint floor should be relaxed;
- that one unfavorable recall seed should be ignored;
- that A1 is real-domain ready;
- that larger encoders, more layers, convolution, recurrence, loss reweighting or threshold changes will necessarily fix the remaining gap.

The evidence supports the narrow structural proposition that decoupling the tasks improves the state/onset tradeoff on the frozen synthetic contract.

It does not satisfy the complete prospective A1 acceptance contract.

## Decision

Reject A1 as the accepted architecture under its frozen gate.

Do not:
- rerun A1;
- alter the +0.04 floor;
- choose two favorable seeds;
- lower thresholds;
- change loss/sampler;
- deepen/widen A1 automatically;
- open P1/P2 or P3.

Any A2 architecture is a new project decision and requires explicit user approval plus a new prospective structural hypothesis before optimizer work.
