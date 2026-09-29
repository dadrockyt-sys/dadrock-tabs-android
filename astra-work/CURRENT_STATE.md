# Astra — explicit next steps

Updated: 2026-09-28 UTC  
Branch: `astra-work`

Latest instructions: **Post-A1 supervisory evidence reconciliation complete** at the end of this file. Stop at the new project-decision boundary.

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


## Post-A1 supervisory evidence reconciliation complete — 2026-09-28

This section supersedes the earlier instruction to perform the evidence reconciliation. That bounded task is now complete.

Created:
- `docs/astra/POST_A1_SUPERVISORY_EVIDENCE_REVIEW_V1.md`
- `docs/astra/POST_A1_SUPERVISORY_EVIDENCE_REVIEW_V1.json`
- `astra_backend/synthetic/post_a1_result_validator_v1.py`
- `astra_backend/synthetic/test_post_a1_result_validator_v1.py`

Artifact verification:
- A1 artifact **11002106213** still reports digest `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`.
- Downloaded A1 `result.json` SHA-256 = `090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3`, exactly matching the frozen record.
- V3 training artifact **11000187208** still reports digest `sha256:84f2566c656c37d5fe20bdc26bfdaa699d5e2c4089c0c91f99434d8f0282e3f3`.
- Downloaded V3 `result.json` SHA-256 = `5b5b9be61196d6e40abb2182f5dd0cff4b21f7c9fe927592324bc20df471f36d`, exactly matching the frozen record.

The evidence review now restores all available per-seed absolute state/joint/onset metrics, deltas, TP/FP/FN counts, negative-only event counts and negative duration for both comparators. It also preserves the qualifications that:
- A1 has **279,556** parameters vs S11 **156,548** (**+123,008 / +78.6%**);
- same seeds and batch plans do not mean paired downstream initialization because A1 initializes an extra encoder;
- A1 remains a frozen scientific **FAIL**;
- ordinary joint admission remains below the clean S11 control in every seed;
- reused S9/V3 populations are development evidence, not independent confirmation;
- zero A1 negative-only events were observed only on the bounded synthetic durations (**6 s ordinary, 12 s challenge per seed**), not in real-world use.

Prospective pure result validator:
- rejects duplicate/missing/extra seeds;
- rejects missing metrics, booleans as numbers, NaN/infinity, impossible fractions, inconsistent deltas, inconsistent FP rates, mismatched identities and step totals;
- does not import torch or instantiate a model;
- is prospective only and does not modify A1/V3 frozen outputs.

Focused model-free check:
- exact command: `python -m unittest -v astra_backend.synthetic.test_post_a1_result_validator_v1`
- result: **10/10 tests passed**
- model imports **0**
- optimizer steps **0**
- workflow dispatches **0**
- P1/P2/P3 access **none**

### Concrete decision brief

Existing evidence establishes that the dual-encoder **package** improves several fixed synthetic measurements relative to the source-domain-trained S11 intervention. It does not isolate encoder sharing from capacity/initialization effects, does not pass A1's prospective gate, and does not establish independent real-domain/product performance.

The smallest direct evidence for product relevance would be a new prospectively frozen **independent real-development evaluation**, separate from P3 and not a silent reuse of closed P1/P2. A capacity/initialization-controlled architecture-identification study would answer only the narrower causal architecture question.

**Current recommendation: pause model research.** If the user explicitly opens a new project, prefer independent real-development evidence before another synthetic architecture iteration.

### Current authorization boundary

No A2 is open.
P1/P2 remain closed.
P3 remains sealed.
Main/Production remain unchanged.

Do not:
- run A1 again;
- create/train A2 automatically;
- run another synthetic model experiment from this review;
- access P1/P2 or P3;
- dispatch a model workflow;
- mutate main/Production.

**Resume instruction:** Stop at the project-decision boundary. The next empirical step requires explicit user authorization for a new independent real-development evidence program; a new architecture-identification/A2 project likewise requires its own explicit decision. Do not infer either authorization from a generic “continue.”


## Independent real-development evidence program authorized and intake package frozen — 2026-09-28

The user explicitly selected **option 1** and authorized a new independent real-development evidence program.

This authorization opens the **program design/intake scope**. It does not reopen P1/P2/P3, does not open A2, and does not authorize training, tuning, paid inference, deployment, or main/Production changes.

Prospective design/spec now frozen:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_V1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_V1.json`

Intake package:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`
- `astra_backend/synthetic/independent_real_development_intake_validator_v1.py`
- `astra_backend/synthetic/test_independent_real_development_intake_validator_v1.py`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_PACKAGE_VERIFICATION_V1.json`

The frozen V1 first-tranche contract requires:
- **24 new clips** total;
- at least **18 positive** clips;
- at least **6 negative-only** clips;
- at least **90 s positive audio**;
- at least **30 s negative-only audio**;
- clips created or sourced only after this design freeze;
- explicit no-overlap with P1/P2/P3 and previously inspected/tuned audio;
- prospectively frozen annotations before model output;
- fixed historical thresholds **0.50 / 0.50**;
- no threshold, decoder, frontend, candidate, seed, architecture, loss or sampler tuning from these clips.

Required coverage includes single notes, repeated attacks, legato, palm mute, dyad/chord material, clean capture, and distorted/overdriven capture.

The intake validator fails closed on independence declarations, clip counts/durations, coverage, annotation presence, candidate/runtime pins, summary consistency, zero pre-verification inference, zero optimizer steps, and continued P1/P2/P3 closure.

Focused local model-free verification:
- command: `python -m unittest -v test_independent_real_development_intake_validator_v1.py`
- result: **10/10 passed**
- model imports/inference: **0**
- optimizer steps: **0**
- real clips accessed: **0**
- workflow dispatches: **0**
- P1/P2/P3 access: **none**
- main/Production mutation: **none**

### Current blocking dependency

No genuinely new independent real-development clip set is currently present in the authorized intake package.

Do not fill the manifest using P1, P2, P3, previously examined audio, synthetic renders, or clips selected after looking at model output.

A durable frozen candidate weight identity must also be available before inference. If A1 weights are unavailable, record that as missing evidence; **do not retrain A1** to recreate them.

### Exact next task

Acquire or receive a genuinely new real-development clip set that satisfies the frozen V1 intake contract. Then:
1. hash every clip;
2. record durations/provenance/coverage;
3. freeze annotations before model output;
4. pin exactly one eligible frozen candidate and evaluator/frontend/runtime identity;
5. populate `INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`;
6. run the pure intake validator;
7. freeze a zero-inference offline verification receipt;
8. stop before any model inference if any intake criterion fails.

If the user supplies or identifies qualifying new audio, intake/annotation work is within the authorized program. P1/P2 and P3 remain excluded.

**Resume instruction:** Continue only with the independent real-development intake package. Do not train, tune, dispatch model inference, open A2, reuse P1/P2, or access P3. The next empirical inference may occur only after a complete new clip set passes the frozen pre-inference intake verification.


## Independent real-development web sourcing completed — 2026-09-28

A web sourcing pass was completed under the authorized independent real-development program.

Frozen sourcing review:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_WEB_SOURCE_REVIEW_V1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_WEB_SOURCE_REVIEW_V1.json`

The shortlist contains:
- **18 positive guitar candidates**, nominal total **139 s**;
- **6 negative-only candidates**, nominal total **39 s**;
- one reserve dedicated legato source that must be prospectively cropped to 4–10 s before model output if used.

Primary source is Pixabay sound effects. Individual pages were checked for the Pixabay Content License; this project will use any downloaded audio only for internal evaluation and will not commit or redistribute original standalone audio.

The positive pool spans multiple creators and includes:
- clean electric;
- distorted/hard-rock/metal;
- acoustic;
- baritone;
- single-note/pluck material;
- repeated attacks/loops;
- bends and slide;
- palm-muted chord material;
- strumming;
- arpeggio;
- riff and chord material.

The negative pool includes keyboard typing, drums, applause, crowd cheer and speech so false-positive behavior is tested on transient-rich non-guitar audio rather than silence only.

Research-dataset review:
- GuitarSet remains a possible CC-BY backup source but was not selected for V1 because the new creator-clip pool better serves the independent-development objective.
- IDMT-SMT-Guitar was not selected because its CC BY-NC-ND evaluation license creates unnecessary downstream-use ambiguity for this product project.
- Guitar-TECHS/P1/P2/P3 material remains excluded.

No audio was downloaded during this sourcing pass.
No model inference was run.
No optimizer steps were run.
No P1/P2/P3 data was accessed.
No workflow was dispatched.
Main/Production remain unchanged.

### Exact next task

Use only the frozen web shortlist as the candidate pool. For each selected clip:
1. download the original audio without adding it to Git;
2. preserve source URL/title/creator/license metadata;
3. hash original bytes immediately;
4. human-audition and reject any mixed/ambiguous clip before model output;
5. choose any necessary 4–10 s crop only from audio/annotation quality, never model behavior;
6. freeze pitch/onset annotations before model inference;
7. populate `INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`;
8. run the pure intake validator;
9. freeze a zero-inference verification receipt;
10. only then advance to the one bounded real-development inference.

**Resume instruction:** Web sourcing is complete. Continue with download/hash/human-screen/annotation of the frozen shortlist only. Do not train, tune, open A2, reuse P1/P2, access P3, or run model inference until the complete intake passes zero-inference verification.
