# V6 Onset-Representation and Event-Statistics Adequacy Result V1

Date: 2026-09-29  
Status: **COMPLETED — NO DEVELOPMENT-INTERESTING ONSET OBJECTIVE**

## Frozen experiment

Four paired arms were trained at exactly 500 steps each:

- **O0** — historical exact-frame BCE
- **O1** — fixed ±1-frame soft targets with BCE
- **O2** — exact targets with frozen focal loss (gamma 2.0, alpha+ 0.75, alpha- 0.25)
- **O3** — fixed ±1-frame soft targets plus the same focal loss

Total optimizer work: **2000 / 2000 authorized steps**.

Architecture, parameter count, R3 renderer, exact state objective, initialization, synthetic corpus, batch plan, thresholds, and decoder remained fixed.

## Focused helper verification

The committed onset-objective helper passed **7/7** focused tests:
- soft-window center/adjacent behavior;
- edge behavior;
- BCE finiteness;
- focal finiteness on hard targets;
- focal finiteness on soft targets;
- arm dispatch;
- unknown-arm rejection.

## V6A synthetic sanity

| Arm | Precision | Recall | F1 | Neg FP/s | V2B eligible |
|---|---:|---:|---:|---:|---|
| O0 | 0.7647 | 0.6047 | 0.6753 | 0.000 | Yes |
| O1 | 0.6343 | 0.6589 | 0.6464 | 0.000 | **No** |
| O2 | 0.7500 | 0.6047 | 0.6695 | 0.000 | Yes |
| O3 | 0.7295 | 0.6899 | **0.7092** | 0.000 | Yes |

O1 failed only the frozen precision floor of 0.70 and did not reach V2B.

O2 and O3 passed every synthetic-sanity condition.

## V6B V2B transfer

At unchanged 0.50/0.50 thresholds:

| Arm | Onset admission | State admission | Trusted joint | High-confidence joint | Negative FP/s |
|---|---:|---:|---:|---:|---:|
| O0 | 1/56 (1.79%) | 2/56 (3.57%) | 0/56 | 0/49 | **0.1569** |
| O2 | 1/56 (1.79%) | 10/56 (17.86%) | 0/56 | 0/49 | **0.7847** |
| O3 | 2/56 (3.57%) | 9/56 (16.07%) | 0/56 | 0/49 | **1.6009** |

O2 provides **zero onset-admission gain**.

O3 gains only **+1/56** onset landmark (+0.0179 absolute), far below the frozen +0.20 requirement.

Neither O2 nor O3 recovers a single trusted joint landmark, and both substantially worsen negative false positives.

Therefore **no V6 arm is development-interesting**.

## V6C model-free event-statistics audit

Average onset density is not dramatically different:
- synthetic: **1.654 onsets/s**
- V2B: **1.491 onsets/s**

But the temporal distributions are materially different:

| Statistic | Synthetic | V2B |
|---|---:|---:|
| Clip-rate median | 2.000/s | 1.177/s |
| Clip-rate p90 | 3.000/s | 3.432/s |
| IOI p10 | 0.000 s* | 0.1067 s |
| IOI median | 0.3483 s | **0.2560 s** |
| IOI p90 | 0.4180 s | **0.8824 s** |
| Repeated-attack fraction <=250 ms | 26.67% | **47.02%** |

*Synthetic zero IOIs arise from simultaneous multi-string chord attacks counted as separate onset references.

The real development set therefore has both:
- substantially more short-gap repeated attacks; and
- a much longer sparse-event upper tail.

That shape is not captured by the synthetic corpus even though aggregate events/sec is similar.

V2B does not provide exhaustive sustain-duration annotation for every clip, so real active-duration/onset-to-sustain values are intentionally not fabricated.

## Supported interpretation

Simple onset-label tolerance and a fixed focal loss are not enough.

O3 improves the synthetic onset task, but that improvement does not transfer: it yields only one extra real onset admission and greatly increases false positives.

Combined with V6C, the evidence supports a narrower diagnosis that the synthetic task's **event-timing distribution and learned onset representation are poorly aligned with real guitar audio**.

This is not proof that event statistics are the only cause.

## Boundary

No fresh holdout is warranted because no V6B arm passed the development gate.

V1.1 remains sealed. P1/P2/P3 remain closed. A2 remains closed. Main/Production are unchanged.

The next scientifically useful project should test a **prospectively redesigned synthetic event generator / onset curriculum** that matches real event-timing structure without fitting to model outputs, or separately consider a fresh real-domain training study.
