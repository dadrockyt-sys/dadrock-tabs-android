# Astra — explicit next steps

Updated: 2026-09-28 UTC  
Branch: `astra-work`

## Current status

**Architecture Research A1 is complete and FAILED its frozen acceptance gate.**

A1 must remain frozen. Do not reinterpret it as a pass.

Key frozen files:
- `docs/astra/ARCHITECTURE_RESEARCH_A1_RESULT_V1.json`
- `docs/astra/ARCHITECTURE_RESEARCH_A1_ANALYSIS_V1.md`
- `docs/astra/ARCHITECTURE_RESEARCH_A1_DESIGN_V1.md`
- `docs/astra/ARCHITECTURE_RESEARCH_A1_SPEC_V1.json`

Full historical handoff:
- `docs/checkpoints/CURRENT_STATE.md`

Latest known A1 execution:
- workflow run: **36492748299**
- job: **109164963801**
- artifact: **11002106213**
- artifact digest: `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`
- result JSON SHA-256: `090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3`
- models: **3**
- optimizer steps/model: **500**
- total optimizer steps: **1,500**
- thresholds: **0.50 / 0.50**
- threshold search/retuning: **false**
- P1 access: **false**
- P2 access: **false**
- P3 opened: **false**
- automatic retry: **false**

## A1 result that must be preserved

A1 changed only one architectural property:
- S11 shared encoder -> separate state and onset encoders.

Strong positive evidence:
- ordinary state-admission gain vs frozen S11 intervention: mean **+0.0930233**, positive **3/3**
- V3 challenge state-admission gain: mean **+0.0723514**, positive **3/3**
- ordinary joint-admission gain: mean **+0.0387597**, positive **3/3**
- challenge joint-admission gain: mean **+0.0284238**, positive **3/3**
- challenge onset-F1 gain vs frozen S11 intervention: mean **+0.0513049**, positive **3/3**
- challenge onset-F1 gain vs frozen S11 control: mean **+0.112441**, positive **3/3**
- ordinary and challenge negative-only false positives: **0.0 events/sec in every seed**

Frozen failed criteria:
1. mean ordinary joint-admission gain vs frozen S11 intervention:
   - observed **+0.0387597**
   - required **>= +0.0400000**
2. challenge recall gain vs frozen S11 control:
   - positive in **2/3** seeds
   - required positive in **3/3**
   - seed 20260927 delta: **-0.003876**

Therefore A1 is a scientific **FAIL** under its prospective contract.

## Explicit next steps

### 1. Stop A1

Do **not**:
- rerun A1;
- relax or round the +0.04 joint-admission gate;
- ignore or drop seed 20260927;
- lower state/onset thresholds;
- tune loss weights;
- tune sampler ratios;
- tune decoder windows;
- increase steps;
- select a favorable seed;
- reopen P1/P2;
- open P3.

### 2. Do not create A2 automatically

Any A2 architecture is a **new project version**.

Before any A2 optimizer work, require a fresh explicit user approval such as:

> I approve A2 research.

Generic requests like “continue” are **not** sufficient to open A2 if no explicit A2 approval has been given.

### 3. If A2 is explicitly approved

First perform **design-only work**.

A2 must have:
- a new structural hypothesis that is not just “make A1 bigger”;
- a clearly isolated architectural change;
- no simultaneous threshold/loss/sampler/decoder tuning;
- the A1 and V3 results kept immutable;
- exact frozen control, intervention and V3 challenge identities;
- a prospectively frozen evaluation contract;
- explicit pass/fail gates;
- hard CPU/model/optimizer/time ceilings;
- no P1/P2/P3 access.

Only after the A2 design/spec is committed should implementation begin.

### 4. Required A2 offline verification before any optimizer run

Before training A2:
- add structural unit tests proving the intended architectural property;
- verify exact source Git blobs;
- verify exact control/intervention/V3 challenge file hashes;
- verify frozen seed set and batch-plan hashes;
- verify evaluator and thresholds remain unchanged;
- run zero optimizer steps;
- freeze an offline verification receipt;
- use a unique one-shot launch identity;
- automatic retry must remain false.

### 5. If A2 package passes offline verification

One bounded synthetic execution may be run only under its frozen prospective contract.

After the run:
- freeze exact workflow/run/job/artifact/result hashes;
- preserve every failed criterion honestly;
- do not post-hoc relax gates;
- do not auto-rerun;
- do not auto-create A3.

### 6. Real-data boundary remains closed

P1/P2 remain **closed** for architecture evaluation unless separately and explicitly authorized under a new real-development plan.

P3 remains **sealed**.

Do not use the failed A1 or any future synthetic candidate on P3 automatically.

## Current authorization boundary

At this checkpoint, there is **no authorization for A2**.

The next model/architecture research action requiring explicit user approval is:

**Open Architecture Research A2 as a new prospective project version.**

Until that approval is received:
- documentation/review work is allowed;
- no new architecture optimizer run;
- no new real-data access;
- no P3 access;
- main/Production unchanged.

## Resume instruction

Read this file first.

If the user explicitly approves A2:
1. freeze a new A2 structural hypothesis and spec;
2. keep all non-architecture variables fixed;
3. build and verify the package with zero optimizer steps;
4. only then run one bounded A2 synthetic execution if verification passes.

If A2 is not explicitly approved, stop before model execution.
