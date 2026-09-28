# Astra — explicit next steps

Updated: 2026-09-28 UTC  
Branch: `astra-work`

Latest instructions: **Supervisory review for GPT-5.6 after A1** at the end of this file. Start with its bounded model-free evidence review.

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


## Supervisory review for GPT-5.6 after A1 — 2026-09-28

**This section supersedes earlier next-step wording where it conflicts. A1 remains FAILED and closed. The current user request authorizes analysis and saving instructions; it does not open A2 or authorize model/data execution.**

### Review evidence and limits

Reviewed remote head `fc7b56b7ef559dfec1a95fbfab682561a4b6e971`, AGENTS.md, this explicit handoff, the historical checkpoint, A1 design/spec/result/analysis, A1 runner and six structural tests, and inherited S11 model/initializer/loss/batching/evaluator wrapper. GitHub independently reports run 36492748299/job 109164963801 completed successfully, including structural tests, input verification and artifact upload.

This review did not download/recompute the full result artifact, inspect corpus audio, execute tests, instantiate/train models, or audit every historical workflow. Numerical findings rely on the committed frozen summary; parameter counts below are arithmetic from the inspected layer definitions. Do not describe this as independent reproduction of A1.

Local checkouts found in the workspace are older and contain uncommitted work. Preserve that work. Do not push a stale checkout over the current remote branch.

### Assessment

GPT-5.6 correctly preserved failed gates, separated successful workflow completion from scientific acceptance, and stopped A1 without reopening P1/P2/P3. The progression produced useful synthetic evidence, but the result does not yet establish a successful transcription product. Continue preserving honest failures; do not turn a near miss into an acceptance.

### Corrections to carry forward

1. **A1 is a package comparison, not an isolated proof of task interference.** S11 has 156,548 trainable parameters from the inspected definitions; A1 has 279,556, an increase of 123,008 (78.6%). Removing sharing also increased total capacity and changed initialization of downstream modules. The same seed does not make those tensors identical: A1 initializes an extra encoder before the state/onset heads. Exact batch-plan pairing remains useful, but do not claim paired initialization or causal isolation of gradient interference. Say: “The dual-encoder package improved several metrics on these fixed synthetic data; capacity, initialization and sharing effects were not separated.” Structural gradient-isolation tests prove connectivity, not that harmful task interference caused S11's errors.

2. **Always report both comparators.** Against the source-domain-trained S11 intervention, ordinary joint admission improved by +0.0387597. Against the clean-trained S11 control, it remained lower in all three seeds: mean -0.0284238, minimum -0.0310078. Ordinary state gain against that clean control was only +0.0155039 on average and positive in 2/3 seeds. Recovery from a degraded intervention is not superiority to the clean baseline. Preserve these absolute-reference findings alongside the favorable intervention deltas.

3. **Architecture admission is not restoration of the V3 system gate.** A1 prospectively omitted the earlier +0.08 mean challenge-recall floor. That is documented as a distinct research contract, not a retroactive V3 pass. A1's mean recall gain against the clean control was +0.0426357, with one negative seed, and A1 failed even its own contract. Neither acceptance system passed. Future reports must distinguish hypothesis-level architecture evidence, synthetic system admission, and real-domain/product acceptance.

4. **Reused synthetic tests are exposed development evidence.** V3's challenge and S9 ordinary test now inform successive decisions. They remain useful fixed benchmarks but are not independent confirmation of a later architecture. Family-wise marginal stratification and 35 marginal descriptor checks also do not establish full multivariate joint support. Preserve the recorded coverage passes while stating their limited meaning. Do not keep changing benchmark versions until one passes or claim three training seeds are three independent datasets.

5. **Do not overstate zero false positives.** Report the zero counts with the exact negative-only duration and row counts from existing evidence. Zero on this bounded synthetic sample is not a zero real-world false-positive rate. Restore absolute metrics and numerators/denominators before discussing effect size or product accuracy. State/joint admission and pitch-onset F1 are different quantities; none alone proves full-song, offset, playable fingering, or bass/rhythm/lead separation quality.

6. **Admission enforcement still needs strengthening.** A1's six tests check shapes, disjointness, simple backward connectivity, constants and deterministic initialization. They do not test gate rejection. `evaluate_gate` checks selected finiteness but not all ranges or exact unique row seeds; `threeModels500Steps` uses `all(...)` without itself checking row count. Some guard fields are literal True declarations. The fixed execution loop/input hashes provide separate safeguards, so this is not evidence A1 actually violated its budget. It is a prospective validation gap. Do not repair historical outputs or rerun A1 to improve its receipt.

### Exact next authorized task — evidence reconciliation, no experiment

Complete this bounded offline task before requesting a new research decision:

1. Create `docs/astra/POST_A1_SUPERVISORY_EVIDENCE_REVIEW_V1.md` and a small machine-readable companion. Use existing committed summaries/source only initially. Include one table per comparator with all three seeds where available, absolute state/joint/onset metrics, deltas, event counts, negative duration, and the exact definition of each metric. Mark unavailable values “not available in committed summary”; never infer absolute accuracy from deltas.
2. If the existing synthetic A1/V3 result artifacts are needed for missing counts, retrieve only those already-produced result artifacts through authorized GitHub access, verify their recorded digest/result SHA, and parse the JSON. Do not acquire training datasets, audio, weights, or run inference to fill a gap. If an artifact is unavailable, record that limitation without a rerun.
3. Trace existing comparator/source/runtime pins and record which controls are verified versus merely declared. Explain parameter counts, RNG construction order, identical batch plans versus unequal initialization, reused evaluation populations, and the different V3/A1 gates. Preserve every frozen result unchanged.
4. Add a separate prospective pure-Python result validator and focused JSON-fixture tests only if needed to make the next evaluation contract reliable. No torch/model import or optimizer is needed. Require exactly the declared unique seeds/rows; expected step totals; complete finite numeric metrics; fractions in [0,1]; nonnegative FP counts/rates and valid durations; internally consistent counts/rates; and deltas recomputed from absolute operands. Reject booleans masquerading as numbers, duplicate/missing/extra seeds, missing metrics, NaN/infinity, impossible ranges, inconsistent deltas and mismatched expected identities. Keep missing evidence distinct from scientific failure. Do not retrofit it into A1's frozen result or gate.
5. Run only focused model-free checks for that new helper, if implemented, and record the exact command/results. No broad suite, renderer, model instantiation, inference, optimizer, workflow dispatch, launch marker, new dataset, threshold/seed/loss/sampler search or real-data access is part of this task.
6. Finish with a concise decision brief: what existing evidence establishes; what remains uncertain; the smallest kind of evidence that could resolve it; and the cost/access boundary. Recommend a decision without opening a new project. The options are to pause model research, propose independent real development evidence, or seek a bounded architecture-identification study. Do not prepare several runnable alternatives.
7. Commit the evidence review, any pure validator/tests and updated handoffs to `astra-work`; verify remote content/ref. Synchronize this file and `docs/checkpoints/CURRENT_STATE.md` so the next session cannot resume an obsolete experiment. Then stop at the concrete decision brief.

### Requirements if a later A2 is explicitly approved

Approval is determined from the actual conversation and its scope, not a mandatory magic phrase. Honor explicit applicable approval once; do not repeatedly ask for the same authorized preparation.

Before optimizer work, freeze exactly one question and a finite plan. If the question is whether sharing itself causes the tradeoff, address capacity and initialization confounds with prospectively justified controls and common-tensor initialization mappings, or narrow the claim to an architecture-package comparison. A simple width change is not automatically a capacity-matched causal control. Do not silently add more arms, seeds or steps.

Preserve thresholds, loss, sampler, decoder and frozen data identities unless the separately approved question explicitly requires a different isolated variable. Label reused benchmarks development-only. State whether gates assess mechanism, synthetic acceptance or product performance; changing a research gate cannot cure a historical system failure. Define exact model/update/compute budgets, source/dependency pins, fail-closed admission, deadline checks, partial-failure receipts, consumed-scope enforcement and one launch identity before execution. Run-attempt=1 alone does not prevent a second new workflow run. A new study's pass or fail must end in a frozen result, not automatic A3.

P1/P2 remain closed and P3 sealed. Any new real development program requires its own explicit access and evaluation scope. Main/Production stay unchanged.

**Resume instruction:** Complete the model-free post-A1 evidence reconciliation and concrete decision brief above. Do not rerun A1 or open A2. Keep favorable synthetic findings qualified, preserve failed gates, and ask for a new project decision only after the reviewable brief is saved.
