> Current review (2026-10-02): see `astra-work/POST_V14_GPT56_HANDOFF_2026-10-02.md` and the final resume pointer below. Review complete; prepare an independent bass feasibility packet only. No empirical execution authorized.

# Astra — explicit next steps

Updated: 2026-09-29 UTC  
Branch: `astra-work`

Latest instructions: **V14 empirical execution complete — FAILED material-recovery gate — serial micro-optimization closed — 2026-09-29** at the end of this file.

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


## Web acquisition probes exhausted; frozen candidate pinned — 2026-09-28

Continuation from the frozen web shortlist attempted two bounded **model-free** acquisition paths for candidate P01.

### Acquisition probe V1 — failed before audio access

Frozen failure:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_ACQUISITION_PROBE_FAILURE_V1.json`

Workflow:
- run **36508296736**
- job **109214593700**
- head `321391803e96dee3b2f9f13c705f9fe2a6654225`
- attempt **1**
- conclusion **FAILURE**

Method:
- public Pixabay page;
- headless Playwright;
- attempted to observe a public audio response after normal page/play/download interaction.

Failure:
- no public Pixabay audio URL was observed by the GitHub runner.

No audio was downloaded.
No model was loaded.
No inference or optimizer work occurred.
P1/P2/P3 remained untouched.

### Acquisition probe V2 — failed before audio access

Frozen failure:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_ACQUISITION_PROBE_FAILURE_V2.json`

Workflow:
- run **36508495937**
- job **109215211120**
- head `b2e28dfa31f4f6f35f03a874d6d029d3684da2fd`
- attempt **1**
- conclusion **FAILURE**

Method:
- exact public CDN URL resolved during the earlier read-only browser session;
- direct request from GitHub Actions with ordinary User-Agent/Referer headers.

Failure:
- CDN returned **HTTP 403 Forbidden**.

This is an access-control/automation limitation, not a scientific result. Do not escalate with anti-bot bypass, credential circumvention, or repeated automated retries.

### Durable candidate identity now pinned

A1 and S11 result artifacts do not contain durable trained weight files, so they cannot be recreated by retraining under this program.

The newest verified durable compatible checkpoint in the frozen synthetic line has therefore been pinned **before any new real-development model output**:

- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_CANDIDATE_PIN_V1.json`
- candidate: **S9 30-voicing intervention**
- source run **36379258174**
- artifact **10952098012**
- artifact digest `sha256:30b4596731c0445e6c38e046c4e628f75dbd55562a97901966746b2e99d7b596`
- artifact currently unexpired; expiry **2026-10-28T04:50:19Z**
- weight file `intervention.pt`
- weight SHA-256 independently rechecked: `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`
- model not loaded;
- inference **0**;
- optimizer **0**.

The candidate's historical S9 gate remains **FAILED**. Pinning it only provides a durable preselected checkpoint for the independent real-development evaluation; it does not reinterpret the historical outcome.

The candidate identity has been written into:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`

### Exact current blocker

Automated Pixabay acquisition is blocked before audio bytes are available. The authorized intake still lacks the actual 24 real-development audio files.

**Next required action is user-mediated lawful acquisition** of the frozen shortlisted files: download them from their Pixabay source pages using the normal site download control, then upload the files here (a ZIP is preferable). Do not rename or edit them before upload if avoidable.

Once supplied, the existing authorization permits:
1. SHA-256 hashing;
2. exact duration/media verification;
3. source-to-file matching;
4. human/annotation screening before any model output;
5. manifest population;
6. pure intake validation;
7. zero-inference verification receipt.

Only after that checkpoint may one bounded real-development inference run.

Do not:
- automate around Pixabay anti-bot/access controls;
- substitute P1/P2/P3;
- retrain A1/S11;
- train/tune any candidate;
- run inference before intake verification;
- open A2;
- mutate main/Production.

**Resume instruction:** Wait for the user to upload the lawfully downloaded frozen shortlist (preferably one ZIP). Then continue automatically through hash/duration/provenance verification and intake preparation, stopping before inference if any clip or annotation criterion fails.


## Real-development audio collection complete — 2026-09-28

The user completed the one-by-one lawful upload of the frozen web shortlist.

Collection receipt:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_COLLECTED_AUDIO_V1.json`

Frozen admitted set:
- **24 clips total**
- **18 positive guitar**
- **6 negative-only**
- **145.416 s positive evaluation audio**
- **41.367 s negative-only evaluation audio**

Important prospective adjustments frozen before model output:
- P01: use 0.000–10.000 s;
- P08: use 0.000–10.000 s;
- N06: use 0.000–10.000 s;
- original palm-muted P12 (3.840 s) excluded because it violated the frozen 4 s minimum;
- replacement P12 is `imij-legato-in-b-standard-322656.mp3`, SHA-256 `b944e3e8aeee48c5baca86516658d0ccfe8cb32a8a4618673c38b1a924a57b31`;
- replacement P12 evaluation crop frozen at **16.000–24.000 s**, chosen from audio quality/legato content before any model output;
- duplicate P18 upload excluded.

No model inference has occurred.
No optimizer step has occurred.
P1/P2/P3 remain untouched.
A2 remains closed.
Main/Production remain unchanged.

### Exact next task

Proceed to **pre-inference annotation and intake closure only**:
1. human/model-free annotate pitch/onset events for all positive evaluation segments;
2. mark confidence and only include string/fret where unambiguous;
3. confirm each negative-only segment contains no target guitar;
4. populate `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json` with the 24 frozen clip identities and annotations;
5. run the pure intake validator;
6. freeze the zero-inference verification receipt;
7. stop if any criterion fails.

Only after that zero-inference checkpoint may the one bounded real-development model evaluation run.

**Resume instruction:** Collection is complete. Continue with annotation and intake validation; do not run the candidate model yet.


## Pre-inference annotation draft complete; scientific QA block frozen — 2026-09-28

The 24-clip independent real-development intake has now been populated and structurally validated before any candidate-model output.

New frozen files:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_MODEL_FREE_ANNOTATIONS_V1.json`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_COLLECTED_AUDIO_CORRECTION_V2.json`
- updated `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_ANNOTATION_QA_V1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_ZERO_INFERENCE_VERIFICATION_V1.json`

Verified intake:
- 24 clips;
- 18 positive / 6 negative-only;
- 145.415094 s positive evaluation audio;
- 41.366531 s negative-only evaluation audio;
- all frozen coverage categories present;
- 105 model-free pitch/onset draft labels;
- confidence: 81 high / 5 medium / 19 low;
- candidate remains S9 30-voicing intervention;
- thresholds remain 0.50 / 0.50;
- model inference 0;
- optimizer steps 0;
- P1/P2/P3 none;
- A2 closed;
- main/Production unchanged.

A pre-inference clerical correction was necessary and frozen before any model output:
- P02 SHA-256 corrected from the earlier recorded value to `e4a57932d02b3e925d9e76a04067bd623fe1023c9e37da19f4011e93a8e0483e` after recomputation from uploaded bytes;
- P05/P09/P11/N05 evaluation endpoints were reduced by tiny amounts where the nominal endpoint exceeded decoded MP3 duration.

These are bookkeeping corrections, not result-responsive changes.

### Structural vs scientific status

**Frozen structural intake validator: PASS.**

**Scientific annotation completeness: NOT YET PASSED.**

The draft uses spectral-flux onset detection plus YIN fundamental estimation. This is model-free but fundamentally monophonic, so chordal/polyphonic clips can be under-annotated. Do not let structural validity substitute for reference-label completeness.

Mandatory human QA before inference:
- P01
- P02
- P05
- P06
- P07
- P10
- P13
- P16

Recommended additional QA:
- P03
- P08
- P11
- P12
- P18

Human QA must be completed without viewing candidate output. Add every reliably audible simultaneous pitch for chord events; use MIDI pitch; preserve onset relative to the frozen crop; string/fret only when unambiguous.

### Exact next task

Complete human QA of the reference annotations. Then:
1. freeze corrected annotations;
2. update intake;
3. rerun pure structural validator;
4. freeze a new zero-inference receipt with scientific readiness true only if the reference set is adequate;
5. only then run the single bounded candidate-model evaluation.

**Resume instruction:** Do not run the candidate model yet. Continue only with pre-inference human annotation QA. No training/tuning/A2/P1/P2/P3.


## Trustworthy scoring contract V1.1 frozen — 2026-09-28

The pre-inference annotation QA has been converted into a narrower, scientifically supportable scoring contract rather than forcing uncertain polyphonic chord tones into the reference set.

New frozen files:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_TRUSTED_SCORING_CONTRACT_V1_1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_TRUSTED_SCORING_CONTRACT_V1_1.json`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_ZERO_INFERENCE_VERIFICATION_V1_1.json`

### Trusted pitch population

Exact MIDI pitch-onset landmark scoring is now limited to:

P01, P03, P04, P05, P08, P09, P11, P12, P14, P15, P17, P18

Combined duration: **97.803094 s**

Frozen landmarks:
- 84 total
- 68 high-confidence
- 4 medium-confidence
- 12 low-confidence

Primary trusted set:
- **72 high+medium-confidence landmarks**

The 12 low-confidence landmarks are sensitivity-only.

### Polyphonic/onset-only population

These remain in the real-development set but are explicitly excluded from exhaustive exact-pitch claims:

P02, P06, P07, P10, P13, P16

Combined duration: **47.612 s**

They may be used only for onset/activity/prediction-density and qualitative behavior after primary metrics are frozen.

### Negative-only population

N01-N06 remain unchanged:
- **41.366531 s**
- primary negative metric remains raw decoded guitar false-positive events/sec.

### Primary V1.1 metrics

1. high+medium trusted pitch-landmark hit rate (72 landmarks)
2. high-only trusted pitch-landmark hit rate (68 landmarks)
3. negative-only false-positive events/sec
4. per-clip trusted landmark hit rate

### Claims now explicitly prohibited

Do not report:
- exhaustive positive precision;
- exhaustive positive recall;
- exhaustive positive F1;
- exact string/fret accuracy;
- production readiness

from this V1.1 dataset.

The original V1 exhaustive PR/F1 objective remains scientifically unmet because several positive clips are polyphonic and the prospectively created model-free annotations are not exhaustive simultaneous-note transcriptions.

### Scientific readiness

**PASS for one bounded candidate evaluation under V1.1 only.**

This readiness is narrower than the original V1 objective and is intentionally claim-limited.

No candidate-model output has been viewed.
No thresholds changed.
No decoder tuning.
No retraining.
No candidate reselection.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production remain unchanged.

**Resume instruction:** The next authorized empirical action is one bounded evaluation of the already pinned S9 30-voicing intervention candidate under the frozen V1.1 scoring contract only. Do not restore exhaustive pitch PR/F1 claims, tune anything from these clips, or open P1/P2/P3/A2.


## Independent real-development evaluation V1.1 completed — 2026-09-28

The user explicitly authorized the one bounded evaluation under the frozen trusted-scoring contract V1.1.

Frozen result files:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_RESULT_V1_1.json`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_RESULT_V1_1.md`

Candidate:
- S9 30-voicing intervention
- checkpoint SHA-256 `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`
- state/onset thresholds fixed at 0.50 / 0.50
- no threshold search/retuning
- no candidate reselection
- no training/fine-tuning
- no optimizer steps

### Primary V1.1 result

Trusted high+medium landmarks:
- **1 / 72 hit**
- hit rate **0.0138889 (1.389%)**

High-confidence landmarks:
- **1 / 68 hit**
- hit rate **0.0147059 (1.471%)**

Sensitivity including low-confidence landmarks:
- **1 / 84 hit**
- hit rate **0.0119048 (1.190%)**

Negative-only:
- **1 false-positive event**
- duration **41.366531 s**
- FP rate **0.0241741 events/s**

Positive behavior:
- P01 produced 3 decoded events and 1 trusted landmark hit.
- Every other positive clip produced 0 admitted events.
- All six onset-only/polyphonic clips produced 0 admitted events.

The sole negative false positive occurred on N02:
- string 0
- fret 9
- MIDI pitch 49
- 4.0867–4.1332 s

### Supported interpretation

The pinned synthetic S9 checkpoint does **not transfer adequately** to this independent real-development audio under the frozen decoder and 0.50/0.50 thresholds.

The low negative FP rate is not evidence of useful selectivity by itself because positive admission also collapsed.

This is a transfer result, not proof that the S9 intervention caused the failure. It does not isolate:
- frontend/domain mismatch;
- calibration;
- representation limits;
- architecture;
- historical-runtime differences.

### Runtime qualification

Historical lock:
- Python 3.10.15 workflow
- torch 1.11.0+cpu
- librosa 0.9.1
- numpy 1.21.6

Local uploaded-audio runtime:
- Python 3.13.5
- torch 2.10.0+cpu
- librosa 0.11.0
- numpy 2.3.5

Exact checkpoint bytes, architecture, frontend mathematics, decoder semantics, thresholds, crops and landmarks were preserved, but this is **not a bit-for-bit historical-runtime reproduction**.

Local evidence hashes:
- full local result SHA-256 `f435d64dc92c939f4b7c5bc354c989b03c902abc7987da69752bc8278645207b`
- summary local result SHA-256 `33ee13da962ec35c5ef0f3a41074a7c7f6bf32019049d3fdf6ee63ab5fd29fb3`

### Boundaries after result

Do not automatically:
- lower thresholds;
- tune decoder/frontend/gain;
- retrain or fine-tune;
- replace candidate based on this result;
- reuse this V1.1 set as a tuning target;
- open A2;
- access P1/P2/P3;
- mutate main/Production.

The smallest next research question would be a **new prospectively frozen real-domain transfer/calibration diagnosis**, with a fresh development/training split if any tuning is to occur.

**Resume instruction:** Stop at this decision boundary. The one authorized V1.1 evaluation is complete. Any calibration/domain-adaptation/fine-tuning/new-candidate work is a new project decision and must not silently tune on the V1.1 evidence set.


## Real-domain transfer/calibration diagnosis V2 opened; V2A infrastructure-blocked — 2026-09-28

A new diagnostic design was frozen without tuning on the sealed V1.1 evaluation set:

- `docs/astra/REAL_DOMAIN_TRANSFER_CALIBRATION_DIAGNOSIS_V2.md`
- `docs/astra/REAL_DOMAIN_TRANSFER_CALIBRATION_DIAGNOSIS_V2.json`

The design explicitly seals V1.1 against:
- threshold selection;
- calibration fitting;
- gain selection;
- frontend retuning;
- decoder tuning;
- fine-tuning;
- candidate selection;
- architecture selection.

### V2A exact-runtime reproduction attempt

Frozen receipts:
- `docs/astra/REAL_DOMAIN_TRANSFER_CALIBRATION_DIAGNOSIS_V2A_RUNTIME_RECEIPT.json`
- `docs/astra/REAL_DOMAIN_TRANSFER_CALIBRATION_DIAGNOSIS_V2A_RUNTIME_RECEIPT.md`

Target historical runtime:
- Python 3.10.15
- torch 1.11.0+cpu
- librosa 0.9.1
- numpy 1.21.6
- scipy 1.8.1
- resampy 0.4.3

Current local runtime:
- Python 3.13.5

Attempts:
1. local Python 3.10 discovery — unavailable;
2. `uv python install 3.10.15` — blocked by sandbox DNS/network restriction;
3. repository search for vendored Python 3.10 / historical wheels / wheelhouse — none found.

No candidate model was loaded during V2A.
No inference was run.
No optimizer step occurred.
No threshold/frontend/decoder/candidate change occurred.
V1.1 was not used for tuning.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production remain unchanged.

A GitHub Actions runner could recreate Python 3.10, but the 24 V1.1 audio files are intentionally not stored in the public repository because their source license does not permit standalone redistribution. The current tooling therefore cannot combine the exact historical runtime with the private uploaded V1.1 audio.

### Current decision boundary

V2A is **infrastructure-blocked**, not scientifically failed.

Two legitimate next paths:
1. provide/enable an exact historical-runtime environment that can access the private V1.1 audio; or
2. explicitly open V2B and collect a fresh calibration-development set while keeping V1.1 sealed.

Do not silently substitute another non-historical runtime rerun and call it V2A.
Do not begin V2B/V2C/V2D automatically.

**Resume instruction:** Stop at the V2A infrastructure boundary. Generic continuation may extend design/documentation only. Any fresh calibration-development data collection or calibration search is a separate empirical project step and should be explicitly authorized.


## V2B calibration-development design prepared — collection still not authorized — 2026-09-28

Generic continuation was used only for design/documentation, per the V2A handoff boundary.

New files:
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_DESIGN.md`
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_DESIGN.json`
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_INTAKE.json`
- `astra_backend/synthetic/v2b_calibration_intake_validator_v1.py`

Frozen minimum V2B collection:
- 16 clips total;
- >=12 positive;
- >=4 negative-only;
- >=60 s positive;
- >=20 s negative;
- >=2 creators/capture chains;
- clean + distorted;
- >=4 primarily single-note;
- >=3 repeated-attack;
- >=2 legato/bend/slide;
- >=2 chordal/polyphonic.

V1.1 remains sealed and cannot be used for threshold selection, calibration fitting, gain selection, frontend retuning, decoder tuning, fine-tuning, candidate selection, or architecture selection.

The V2B intake validator fails closed on:
- V1.1 overlap and near-duplicate declarations;
- P1/P2/P3 overlap;
- previously model-inspected audio;
- clip counts/durations;
- creator diversity;
- required coverage;
- annotation freeze before inference;
- zero model inference/optimizer steps;
- no V1.1 tuning access.

No new web sourcing occurred.
No new audio was downloaded or inspected.
No model inference occurred.
No threshold search occurred.
No training/fine-tuning occurred.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

**Resume instruction:** V2B design is ready, but collection is still a separate empirical step. Do not scrape/source/download new calibration audio or run inference/calibration until the user explicitly authorizes V2B collection.


## V2B collection explicitly authorized; fresh web shortlist frozen — 2026-09-28

The user explicitly authorized V2B collection.

Fresh shortlist files:
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_WEB_SHORTLIST_V1.json`
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_WEB_SHORTLIST_V1.md`

Frozen pool:
- **13 positive guitar candidates** (one spare beyond minimum);
- **4 negative-only candidates**;
- no V1.1 clip IDs/titles reused;
- no P1/P2/P3;
- no synthetic audio.

Positive coverage includes:
- clean;
- distorted/overdriven;
- >=4 primarily single-note candidates;
- >=3 repeated-attack candidates;
- >=2 bend/slide/legato-style candidates;
- >=2 chordal/polyphonic candidates;
- multiple creators/capture sources.

Negative pool:
- keyboard typing;
- war drums/percussion;
- applause/cheer;
- cheering crowd.

All candidates are Pixabay pages under the same internal-evaluation source policy used previously. Original standalone audio must not be committed to the public repository.

Longer candidates are **not yet cropped**. Any 4–10 s crop must be selected from audio quality/coverage and frozen before any candidate-model output.

Automated Pixabay download remains known-blocked in the current tooling. Acquisition therefore proceeds through the user's normal Pixabay **Free download** control.

No V2B audio has been supplied yet.
No model inference has occurred on V2B.
No threshold search/calibration has occurred.
V1.1 remains sealed from tuning.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

### Exact next task

Collect the frozen shortlist. One-by-one is acceptable and preferred for provenance:
1. user downloads the next frozen source through the normal Pixabay control;
2. user uploads the untouched file;
3. hash and decoded duration are verified immediately;
4. source identity is matched;
5. any needed 4–10 s crop is frozen before model output;
6. continue until at least 12 positive + 4 negative clips pass intake.

Start with **C01 Electric guitar Tapping**:
`https://pixabay.com/sound-effects/musical-electric-guitar-tapping-34546/`

**Resume instruction:** Continue V2B collection from C01. Do not inspect candidate-model output, tune thresholds, or reuse V1.1 while collecting.


## V2B pre-inference intake closed — 2026-09-28

V2B collection and annotation are complete before any candidate-model output.

Frozen files:
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_ANNOTATIONS_V1.json`
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_COLLECTION_CORRECTION_V2.json`
- updated `docs/astra/V2B_CALIBRATION_DEVELOPMENT_INTAKE.json`
- `docs/astra/V2B_CALIBRATION_DEVELOPMENT_ZERO_INFERENCE_VERIFICATION_V1.json`

Validated set:
- 17 clips total
- 13 positive / 4 negative-only
- 110.023184 s positive
- 31.857959 s negative
- 9 creator/capture identities
- all required V2B coverage present

Frozen annotations:
- 164 onset landmarks
- 57 trusted pitch landmarks
- 50 high-confidence pitch landmarks
- 7 medium-confidence pitch landmarks
- pitch-trusted clips: C01, C02, C05, C06, C07, C12
- onset-only positive clips: C03, C04, C08, C09, C10, C11, C13

Polyphonic/effect-heavy material is not treated as exhaustive pitch ground truth.

Pre-inference clerical corrections:
- C04 evaluation duration corrected from 5.806 s to 5.799184 s using decoded uploaded bytes
- D01 evaluation duration corrected from 8.098 s to 8.097959 s
- corrections occurred before any V2B candidate output

Zero-inference verification:
- structural intake: PASS
- annotation readiness for calibration diagnostics: PASS
- model inference: 0
- optimizer steps: 0
- threshold search: none
- calibration fitting: none
- V1.1 tuning use: none
- P1/P2/P3: none
- A2: closed
- main/Production: unchanged

**Resume instruction:** V2B is complete. Stop before V2C. Do not run the candidate on V2B, inspect raw model probabilities, search thresholds, fit calibration, or tune anything until V2C is explicitly authorized. V1.1 remains sealed.


## V2C calibration diagnostic complete — no calibration candidate — 2026-09-28

V2C was explicitly authorized and completed on the fresh V2B calibration-development set only.

Frozen execution contract:
- `docs/astra/V2C_CALIBRATION_DIAGNOSTIC_EXECUTION_CONTRACT_V1.md`
- `docs/astra/V2C_CALIBRATION_DIAGNOSTIC_EXECUTION_CONTRACT_V1.json`

Preflight correction:
- `docs/astra/V2C_PREFLIGHT_LANDMARK_SUPPORT_CORRECTION_V1.json`

Frozen result:
- `docs/astra/V2C_CALIBRATION_DIAGNOSTIC_RESULT_V1.json`
- `docs/astra/V2C_CALIBRATION_DIAGNOSTIC_RESULT_V1.md`

### Preflight support correction

One C06 landmark at MIDI 37 was outside the pinned six-string model's representable pitch range and was excluded as unscorable rather than counted as a miss.

Final scorable trusted set:
- **56 high+medium landmarks**
- **49 high-confidence**
- **7 medium-confidence**

The correction was frozen before grid metrics were produced.

### Historical 0.50 / 0.50 raw diagnosis

At the 56 true representable landmarks:
- joint state+onset gate pass: **0**
- state-only failure: **2**
- onset-only failure: **1**
- both gates fail: **53 (94.64%)**

Raw landmark probability summaries:
- median max compatible active-state probability: **1.3265e-9**
- mean max active probability: **0.03445**
- maximum active probability: **0.63777**
- median max compatible onset probability: **5.2315e-14**
- mean max onset probability: **0.03462**
- maximum onset probability: **0.88764**

At 0.50 / 0.50:
- trusted pitch hits: **0 / 56**
- high-confidence hits: **0 / 49**
- negative false positives: **14 / 31.858 s**
- negative FP rate: **0.43945 events/s**
- all 14 baseline negative events occurred on D02 Ancient War Drums.

### Frozen 4x4 threshold grid

State: 0.20 / 0.30 / 0.40 / 0.50
Onset: 0.20 / 0.30 / 0.40 / 0.50

Frozen eligibility constraint:
- negative FP rate <= **0.10 events/s**

**No one of the 16 pairs was eligible.**

Most permissive 0.20 / 0.20:
- trusted hits: **1 / 56 (1.79%)**
- high-confidence hits: **0 / 49**
- negative events: **38**
- negative FP rate: **1.193 events/s**

Every pair with onset threshold >=0.30 produced **0 trusted hits**.
Pairs with onset 0.20 produced at most **1 / 56**, never a high-confidence hit, while negative FP rates remained far above the frozen constraint.

### V2C decision

**No calibration candidate selected.**

The evidence does not support a simple threshold-calibration explanation. Lower thresholds mainly create negative false positives without restoring meaningful real-guitar admission.

Within the current local runtime, the failure is more consistent with an upstream representation/frontend/domain mismatch than with thresholds merely being too conservative. This is a diagnostic interpretation, not a causal isolation.

Historical-runtime mismatch remains unresolved because V2A was infrastructure-blocked.

### Execution identity / guards

- checkpoint SHA-256 `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`
- local V2C runner SHA-256 `26c8dc57b544ad9547347a41d47c1665b975c0e5d6b7369b148e538afc79be39`
- full local result SHA-256 `bdac8be1f5d25f51fd23a17e9a85cc28d27f0e8eec63bb640e18cf9552d60489`
- training: none
- optimizer steps: 0
- frontend/decoder/gain changes: none
- candidate reselection: none
- V1.1 used for calibration selection: no
- P1/P2/P3: none
- A2: closed
- main/Production: unchanged

### Current decision boundary

Do **not** run V2D because there is no eligible V2C threshold pair to confirm.

Do not continue lowering thresholds outside the frozen grid.

The next scientifically useful project would be a new, prospectively frozen upstream transfer diagnosis aimed at representation/frontend/synthetic-to-real feature mismatch. It should not silently reuse V1.1 as a tuning target.

**Resume instruction:** Stop at the V2C no-candidate boundary. Any upstream representation/frontend/domain-transfer experiment is a new project decision and requires explicit authorization.


## Upstream transfer diagnosis V3 design frozen — 2026-09-28

Generic continuation was used only for design/documentation, per the V2C decision boundary.

New files:
- `docs/astra/UPSTREAM_TRANSFER_DIAGNOSIS_V3_DESIGN_V1.md`
- `docs/astra/UPSTREAM_TRANSFER_DIAGNOSIS_V3_DESIGN_V1.json`

V3 separates two hypotheses:
1. real-audio frontend features occupy a materially different distribution from historical synthetic features;
2. the frozen model representation fails even after simple feature-statistic alignment.

### V3A — frontend distribution audit

No model inference.

Compare historical synthetic features vs V2B real features using:
- per-bin mean/std;
- median/MAD;
- floor occupancy;
- dynamic-range percentiles;
- frame and temporal-difference norms;
- context-window norms;
- standardized mean differences;
- Wasserstein summaries;
- feature-range overlap.

### V3B — prospectively frozen diagnostic transforms

Only if V3A shows substantial feature shift:
- identity;
- global affine;
- per-bin affine.

Transforms may match V2B feature mean/std toward historical synthetic mean/std.

No nonlinear transform search, clipping search, gain search, threshold changes, decoder changes, or V1.1 fitting.

### V3C — representation probe

At historical thresholds 0.50 / 0.50 only.

A transform is diagnostically interesting only if:
- trusted joint-admission gain >= +0.20 absolute vs identity;
- >=25% of high-confidence landmarks jointly pass;
- negative FP <=0.10 events/s.

This is diagnostic only and does not authorize adoption.

### V3D

Any apparent improvement requires a fresh holdout. Do not use V1.1 as the confirming holdout.

No empirical V3 work has been run.
No model inference.
No optimizer steps.
No threshold/frontend/decoder changes.
V1.1 remains sealed.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

**Resume instruction:** V3 design is ready, but empirical V3A/V3B/V3C execution is a new project step. Do not run it until the user explicitly authorizes V3 empirical execution.


## V3A execution package prepared — empirical execution still gated — 2026-09-28

Generic continuation was used only to prepare the execution package. No V3A audit was run.

New files:
- `astra_backend/synthetic/v3a_frontend_distribution_audit_v1.py`
- `astra_backend/synthetic/v3a_frontend_distribution_validator_v1.py`
- `docs/astra/V3A_FRONTEND_AUDIT_EXECUTION_PACKAGE_V1.json`

The V3A runner is model-free. It:
- loads the historical synthetic feature NPZ;
- decodes the private V2B audio using the existing frozen frontend math;
- verifies every V2B file hash against the frozen collection manifest;
- applies only the already-frozen V2B crop boundaries;
- computes per-bin mean/std/median/MAD/floor occupancy;
- computes dynamic-range, frame-L2, temporal-difference-L2 and 5-frame context-norm summaries;
- computes per-bin standardized mean differences, Wasserstein distances and robust range overlap;
- emits no model output and performs no thresholding or calibration.

The validator fails closed on:
- wrong schema;
- non-192-bin feature summaries/distances;
- non-finite values;
- any model inference or optimizer work;
- threshold search;
- frontend mutation;
- V1.1/P1/P2/P3/A2 access.

No V3A empirical execution occurred.
No model inference occurred.
No optimizer steps occurred.
No threshold/frontend/decoder changes occurred.
V1.1 remains sealed.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

**Resume instruction:** V3A tooling is ready. Do not execute V3A until the user explicitly authorizes V3 empirical execution. Generic continuation remains documentation/tooling-only.


## V3 empirical execution complete — 2026-09-28

The user explicitly authorized V3 empirical execution.

Frozen results:
- `docs/astra/V3A_HISTORICAL_SYNTHETIC_EXPORT_FAILURE_V1.json`
- `docs/astra/V3A_FRONTEND_DISTRIBUTION_AUDIT_RESULT_V1.json`
- `docs/astra/V3C_REPRESENTATION_PROBE_RESULT_V1.json`
- `docs/astra/V3_UPSTREAM_TRANSFER_DIAGNOSIS_RESULT_V1.md`

### Exact-lock synthetic export limitation

GitHub Actions run **36518666947**, job **109246542435**, recreated Python 3.10.15 / torch 1.11.0+cpu / librosa 0.9.1 / numpy 1.21.6 and regenerated the S9 synthetic dataset.

The workflow failed closed because regenerated control feature SHA:
`a9603d7997c6d8bc3d553f3605369bb0c6e02cecaf15475ca2c7db4fc3ef09ad`

did not equal historical:
`2119d9b953cf2fabde0dcab211004a89e385439108847d2e736a6cdea6e82ce4`.

S0 source, S9 source, and runtime-lock blobs are identical between historical commit and current branch. No mismatched artifact was uploaded. Treat this as runner-level numerical non-bitwise reproducibility.

### V3A same-runtime source-equivalent frontend audit

To avoid cross-runtime confounding, synthetic S9 features were regenerated locally under the same frontend runtime used for V2B real audio.

Source-equivalent synthetic feature SHA:
`48f3a6d44e335a56794fbcde671dd5cd11ca00217eb9bee3854395623f6610c2`

This is not historical-byte-exact.

Observed shift:
- median |SMD| **0.86648**
- p95 |SMD| **1.52489**
- fraction bins |SMD| >=1: **0.390625**
- fraction bins |SMD| >=2: **0**
- median Wasserstein **0.20251**
- p95 Wasserstein **0.30761**
- median robust range overlap **0.88758**
- p05 overlap **0.55983**

V3A therefore found substantial frontend-feature distribution shift.

### V3C frozen affine probes at 0.50 / 0.50

Identity:
- trusted hits **0/56**
- high-confidence **0/49**
- negative FP **0.43945/s**

Global affine:
- trusted hits **1/56**
- high-confidence **1/49**
- negative FP **2.98199/s**
- gain vs identity **+0.01786**

Per-bin affine:
- trusted hits **1/56**
- high-confidence **1/49**
- negative FP **0.34528/s**
- gain vs identity **+0.01786**

Frozen diagnostic gate:
- >= +0.20 absolute trusted admission gain
- >=25% high-confidence admission
- <=0.10 negative FP/s

**No transform was diagnostically interesting.**

### Supported interpretation

There is meaningful synthetic-vs-real frontend-feature distribution shift, but simple first/second-moment affine alignment is insufficient to restore useful real-guitar admission.

This weakens a simple normalization/calibration explanation and points toward deeper synthetic-to-real representation/timbre/task mismatch or other higher-order frontend/model interaction.

Do not claim causal isolation.

### Boundaries

- no training/fine-tuning
- no threshold changes
- no decoder changes
- no arbitrary transform search
- V1.1 not used for tuning
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

Do not run V3D because no transform passed the V3 diagnostic gate.

**Resume instruction:** Stop at the V3 no-transform boundary. Any next experiment aimed at synthetic rendering adequacy, representation learning, or fresh real-domain training is a new project decision and requires explicit authorization.


## V4 synthetic-to-real rendering adequacy design frozen — 2026-09-28

Generic continuation was used only for design/documentation at the V3 no-transform boundary.

New files:
- `docs/astra/SYNTHETIC_REAL_RENDERING_ADEQUACY_V4_DESIGN_V1.md`
- `docs/astra/SYNTHETIC_REAL_RENDERING_ADEQUACY_V4_DESIGN_V1.json`

V4 tests whether missing synthetic acoustic/timbral realism is a major cause of the transfer collapse.

Frozen renderer arms:
- **R0** — original S9 renderer
- **R1** — fixed amplifier/cabinet coloration + soft saturation
- **R2** — R1 + deterministic room/capture variation + low-level recording noise
- **R3** — R2 + mild compression + transient variation + bounded hum/noise + bounded pre-normalization level variation

No pitch/time/label changes are allowed.

### V4A model-free screen

Compare R0/R1/R2/R3 to V2B using:
- median absolute SMD
- fraction of bins with |SMD| >=1
- median Wasserstein distance
- median robust range overlap

A non-baseline renderer advances only if all are true vs R0:
- median |SMD| improves >=15%
- fraction |SMD|>=1 improves >=20% relative
- median Wasserstein improves >=10%
- median range overlap declines by no more than 0.02 absolute

At most the best two non-baseline arms may advance.

If none qualify, V4 stops before training.

### V4B bounded synthetic training

Only if V4A advances renderer(s):
- one R0 baseline reproduction
- each advancing renderer arm
- max 3 models
- 500 optimizer steps/model
- max 1500 optimizer steps total
- S9 architecture/sampler/loss/initialization frozen
- thresholds remain 0.50/0.50
- decoder unchanged
- no retry / no threshold search

### V4C V2B development gate

A renderer-trained model is development-interesting only if vs same-run R0:
- trusted joint-admission gain >= +0.20 absolute
- high-confidence joint admission >=25%
- negative FP <=0.10 events/s

No V1.1 access.

### V4D

Any V4C success requires a fresh holdout. V1.1 remains sealed.

No empirical V4 work has been run.
No new synthetic renderer implemented.
No model trained.
No optimizer steps.
No model inference.
V1.1 remains sealed.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

**Resume instruction:** V4 design is ready. Do not implement/run V4A, generate new renderer arms, train models, or evaluate V2B until the user explicitly authorizes V4 empirical execution. Generic continuation remains documentation/design only.


## V4 empirical execution complete — 2026-09-28

The user explicitly authorized V4 empirical execution.

Frozen implementation/results:
- `astra_backend/synthetic/v4_rendering_adequacy_v1.py`
- `docs/astra/V4A_RENDERER_SCREEN_RESULT_V1.json`
- `docs/astra/V4BC_RENDERER_TRAINING_TRANSFER_RESULT_V1.json`
- `docs/astra/V4_SYNTHETIC_REAL_RENDERING_ADEQUACY_RESULT_V1.md`

### V4A model-free renderer screen

R0:
- median |SMD| **0.86648**
- fraction |SMD|>=1 **0.390625**
- median Wasserstein **0.20251**
- range overlap **0.88758**
- did not advance

R1:
- median |SMD| **0.86695**
- fraction |SMD|>=1 **0.375**
- median Wasserstein **0.19704**
- range overlap **0.90179**
- did not advance

R2:
- median |SMD| **0.79400**
- fraction |SMD|>=1 **0.27604**
- median Wasserstein **0.18162**
- range overlap **0.89874**
- did not advance because median |SMD| improvement was only **8.36%**, below frozen 15% threshold

R3:
- median |SMD| **0.69539**
- fraction |SMD|>=1 **0.171875**
- median Wasserstein **0.15755**
- range overlap **0.90728**
- advanced

R3 relative improvements vs R0:
- median |SMD| **19.75%**
- fraction |SMD|>=1 **56.0%**
- median Wasserstein **22.20%**
- range overlap improved by **0.01970 absolute**

Only R3 met every frozen V4A advancement condition.

### V4B paired bounded training

Exactly two models were trained:
- R0: 500 optimizer steps
- R3: 500 optimizer steps
- total: **1000**, below authorized 1500-step cap

Identity:
- initial model SHA-256 `ff680cadfc2fdcdc33d5375bbd79df45fe175163181057d43b8dfc43edef7ecc`
- batch plan SHA-256 `2883748ca039986f8ccc81e7c2f40580fc17224c7a2d6dcea774938190953afd`
- same initialization: yes
- same targets: yes
- same batch indices: yes

Local paired runtime:
- Python 3.13.5
- torch 2.10.0+cpu
- librosa 0.11.0
- numpy 2.3.5

This is not a historical-runtime reproduction.

### V4C V2B transfer result

R0-trained:
- trusted hits **0/56**
- high-confidence **0/49**
- negative events **13**
- negative FP **0.40806/s**

R3-trained:
- trusted hits **0/56**
- high-confidence **0/49**
- negative events **5**
- negative FP **0.15695/s**

R3 reduced negative false positives by about **61.5%** versus same-run R0, but trusted landmark gain was **0.00**.

Frozen V4C gate required:
- trusted joint-admission gain >= +0.20
- high-confidence admission >=25%
- negative FP <=0.10/s

**R3 is not development-interesting.**

### Supported interpretation

The bounded R3 realism package materially improves synthetic-vs-real frontend statistics and lowers negative false positives after retraining, but it does not restore trusted real-guitar pitch admission.

This weakens the hypothesis that missing simple acoustic/capture realism alone is the dominant transfer cause.

Do not claim causal isolation.

### Guards

- no threshold search
- no decoder change
- no architecture change
- no V1.1 tuning use
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged
- V4D does not run because no V4C model passed the frozen gate

**Resume instruction:** Stop at the V4 no-development-interesting-renderer boundary. Any next experiment on representation/task adequacy, target structure, or fresh real-domain training is a new project decision and requires explicit authorization.


## V5 target-structure adequacy design frozen — 2026-09-28

Generic continuation was used only for design/documentation at the V4 no-development-interesting-renderer boundary.

New files:
- `docs/astra/TARGET_STRUCTURE_ADEQUACY_V5_DESIGN_V1.md`
- `docs/astra/TARGET_STRUCTURE_ADEQUACY_V5_DESIGN_V1.json`

V5 tests whether exact string/fret supervision itself contributes to the transfer collapse while keeping architecture and parameter count fixed.

Frozen arms:
- **T0** — historical exact string/fret state objective
- **T1** — pitch-equivalent state objective: any physically compatible string/fret position for the target MIDI pitch may carry state probability
- **T2** — fixed 50/50 exact + pitch-equivalent state objective

Across T0/T1/T2, freeze:
- identical model architecture and parameter count
- identical R3 renderer
- identical synthetic corpus/splits
- identical batch plan
- identical initialization
- identical optimizer and learning rate
- 500 optimizer steps/arm
- identical onset loss
- 0.50/0.50 thresholds
- ordinary production decoder unchanged

### V5A synthetic sanity

Before V2B:
- parameter/init identity must pass
- all three arms exactly 500 steps
- finite losses
- T1/T2 pitch-onset F1 decline vs T0 <=0.10 absolute
- onset recall decline <=0.10 absolute
- synthetic negative FP <=0.10/s

Only sanity-eligible arms may reach V2B.

### V5B V2B development test

For T1/T2 diagnostic scoring only:
- state admission aggregates probability across physically compatible string/fret positions for the trusted MIDI pitch
- onset admission uses maximum onset probability across compatible strings
- thresholds remain 0.50/0.50
- ordinary decoder still measures negative false positives

Development-interest gate vs same-run T0:
- trusted joint-admission gain >= +0.20
- high-confidence joint admission >=25%
- negative FP <=0.10/s
- onset admission decline <=0.10 absolute

### Compute ceiling

- max 3 models
- 500 steps/model
- max 1500 optimizer steps total
- no retries
- no loss-weight search
- no threshold search

### Boundaries

No empirical V5 work has been run.
No model training or inference.
No renderer/threshold/decoder change.
No real audio training.
V1.1 remains sealed.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

Any V5B success requires a fresh holdout; V1.1 is not the confirmation set.

**Resume instruction:** V5 design is ready. Do not implement the new objective, train T0/T1/T2, or evaluate V2B until the user explicitly authorizes V5 empirical execution. Generic continuation remains design/documentation only.


## V5 empirical execution complete — 2026-09-28

The user explicitly authorized V5 empirical execution.

Frozen source/results:
- `astra_backend/synthetic/v5_target_structure_v1.py`
- `astra_backend/synthetic/test_v5_target_structure_v1.py`
- `docs/astra/V5_TARGET_STRUCTURE_ADEQUACY_RESULT_V1.json`
- `docs/astra/V5_TARGET_STRUCTURE_ADEQUACY_RESULT_V1.md`

Focused model-free helper checks:
- **6 / 6 passed**
- no model inference
- no optimizer work

### Identity / compute

All arms used:
- identical S9/S6-style nonlinear architecture
- identical parameter count
- identical R3 feature array
- identical targets
- identical initialization
- identical batch plan
- identical onset loss
- thresholds 0.50/0.50
- ordinary decoder unchanged

Identity:
- initial model SHA-256 `ff680cadfc2fdcdc33d5375bbd79df45fe175163181057d43b8dfc43edef7ecc`
- R3 feature SHA-256 `622d8c2c95194f9b2e706a4c837941905a7c7d33f8f8ef5daa6abf4297d740e6`
- batch-plan SHA-256 `2883748ca039986f8ccc81e7c2f40580fc17224c7a2d6dcea774938190953afd`

Training:
- T0 exact objective: 500 steps
- T1 pitch-equivalent objective: 500 steps
- T2 fixed 50/50 objective: 500 steps
- total optimizer work: **1500 / 1500 authorized steps**

### V5A synthetic sanity

T0:
- precision **0.76471**
- recall **0.60465**
- F1 **0.67532**
- negative FP **0.0/s**
- eligible

T1:
- precision **0.67213**
- recall **0.31783**
- F1 **0.43158**
- negative FP **0.0/s**
- F1 decline vs T0 **0.24375**
- recall decline vs T0 **0.28682**
- **failed synthetic sanity; not V2B-eligible**

T2:
- precision **0.69811**
- recall **0.57364**
- F1 **0.62979**
- negative FP **0.0/s**
- F1 decline vs T0 **0.04554**
- recall decline vs T0 **0.03101**
- **passed synthetic sanity**

### Protocol note

The first local helper mistakenly evaluated T1 on V2B before applying the already-frozen synthetic-sanity decision.

That readout is quarantined and excluded from V5 conclusions.

No objective, threshold, gate, architecture, renderer parameter, or model choice was changed in response.

The helper was corrected before T2:
- T2 was evaluated on synthetic sanity first;
- only after T2 passed did it reach V2B.

### V5B V2B comparison

Frozen compatible-pitch diagnostic:
- state = noisy-OR over all physical string/fret positions for the trusted MIDI pitch
- onset = maximum compatible-string onset probability
- thresholds unchanged at 0.50/0.50
- ordinary decoder used for negative FP

T0:
- trusted joint **0/56**
- high-confidence joint **0/49**
- state admission **0.03571**
- onset admission **0.01786**
- negative FP **0.15695/s**

T2:
- trusted joint **0/56**
- high-confidence joint **0/49**
- state admission **0.08929**
- onset admission **0.01786**
- negative FP **0.31389/s**
- trusted joint gain **0.00**
- onset admission decline **0.00**
- **not development-interesting**

Frozen gate required:
- trusted joint gain >= +0.20
- high-confidence joint >=25%
- negative FP <=0.10/s
- onset decline <=0.10

T2 fails the complete gate.

### Supported interpretation

Relaxing exact string/fret supervision measurably increases compatible **state** admission, but it does not recover any joint real-guitar landmarks because onset admission remains only **1/56**, and negative selectivity worsens.

Exact string/fret target specificity is therefore not sufficient to explain the transfer collapse.

The evidence now points more strongly toward deeper representation/task/data adequacy, particularly **real-domain onset representation and synthetic-to-real event-statistics mismatch**.

Do not claim causal isolation.

### Guards

- no threshold search
- no decoder change
- no architecture or parameter-count change
- no real audio in training
- V1.1 not used for tuning
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

No fresh V5 holdout is warranted because no alternative objective passed V5B.

**Resume instruction:** Stop at the V5 no-development-interesting-objective boundary. Any next experiment on onset representation, synthetic event statistics, or fresh real-domain training is a new project decision and requires explicit authorization.


## V6 onset-representation / event-statistics adequacy design frozen — 2026-09-29

Generic continuation was used only for design/documentation at the V5 no-development-interesting-objective boundary.

New files:
- `docs/astra/ONSET_EVENT_STATISTICS_ADEQUACY_V6_DESIGN_V1.md`
- `docs/astra/ONSET_EVENT_STATISTICS_ADEQUACY_V6_DESIGN_V1.json`

V6 tests whether onset supervision and synthetic event statistics materially contribute to the real-domain transfer collapse.

Frozen arms:
- **O0** — historical exact-frame BCE onset objective
- **O1** — fixed ±1-frame soft onset targets (center 1.0, adjacent 0.5)
- **O2** — fixed focal onset objective (gamma 2.0, alpha+ 0.75, alpha- 0.25)
- **O3** — fixed soft-window + focal objective

Across all arms:
- identical S9/S6 nonlinear architecture and parameter count
- identical R3 renderer
- exact string/fret state objective frozen
- identical synthetic corpus/splits
- identical initialization and batch plan
- 500 optimizer steps/arm
- thresholds remain 0.50/0.50
- production decoder unchanged
- no onset-window / alpha / gamma / loss-weight search

### V6A synthetic sanity

Alternative arms must satisfy vs O0:
- pitch-onset F1 decline <=0.08 absolute
- onset recall decline <=0.08 absolute
- onset precision >=0.70
- negative-only FP <=0.10/s
- all 500 optimizer steps completed with finite losses

Only sanity-eligible arms may reach V2B.

### V6B V2B development gate

At unchanged 0.50/0.50:
- compatible-string onset admission gain vs O0 >= +0.20
- trusted joint-admission gain vs O0 >= +0.15
- high-confidence joint admission >=20%
- ordinary-decoder negative FP <=0.10/s
- compatible state admission decline <=0.10

No scoring-time temporal tolerance is allowed; O1/O3 must generalize from training.

### V6C model-free event-statistics audit

Regardless of V6B outcome, compare synthetic vs V2B:
- onsets/sec
- IOI p10/p50/p90
- repeated-attack fraction within 250 ms
- event-density distribution
- active-duration distribution where available
- onset-to-sustain ratio

V6C is descriptive only and cannot retroactively alter O1/O2/O3.

### Compute ceiling

- max 4 models
- 500 steps/model
- max 2000 optimizer steps total
- zero retries
- zero threshold search
- zero loss-parameter search

No empirical V6 work has been run.
No model training/inference.
No real audio training.
V1.1 remains sealed.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

Any V6B success requires a fresh holdout; V1.1 is not the confirmation set.

**Resume instruction:** V6 design is ready. Do not implement O1/O2/O3, train O0/O1/O2/O3, evaluate V2B, or run the V6C event-statistics audit until the user explicitly authorizes V6 empirical execution. Generic continuation remains design/documentation only.


## V6 empirical execution complete — 2026-09-29

The user explicitly authorized V6 empirical execution.

Frozen source/results:
- `astra_backend/synthetic/v6_onset_objectives_v1.py`
- `astra_backend/synthetic/test_v6_onset_objectives_v1.py`
- `docs/astra/V6_ONSET_EVENT_STATISTICS_ADEQUACY_RESULT_V1.json`
- `docs/astra/V6_ONSET_EVENT_STATISTICS_ADEQUACY_RESULT_V1.md`

Focused onset-helper tests:
- **7 / 7 passed**

### Identity / compute

All arms used:
- identical S9/S6 nonlinear architecture and parameter count
- identical R3 features
- identical exact-string/fret state objective
- identical initialization
- identical batch plan
- identical optimizer/learning rate
- thresholds 0.50/0.50
- ordinary decoder unchanged

Identity:
- initial model SHA-256 `ff680cadfc2fdcdc33d5375bbd79df45fe175163181057d43b8dfc43edef7ecc`
- R3 feature SHA-256 `622d8c2c95194f9b2e706a4c837941905a7c7d33f8f8ef5daa6abf4297d740e6`
- batch-plan SHA-256 `2883748ca039986f8ccc81e7c2f40580fc17224c7a2d6dcea774938190953afd`

Training:
- O0 exact-frame BCE: 500 steps
- O1 fixed +/-1-frame soft BCE: 500 steps
- O2 fixed focal exact-target: 500 steps
- O3 fixed soft-window + focal: 500 steps
- total optimizer work: **2000 / 2000 authorized steps**

### V6A synthetic sanity

O0:
- precision **0.76471**
- recall **0.60465**
- F1 **0.67532**
- negative FP **0.0/s**
- eligible

O1:
- precision **0.63433**
- recall **0.65891**
- F1 **0.64639**
- negative FP **0.0/s**
- failed frozen precision floor 0.70
- **not V2B-eligible**

O2:
- precision **0.75000**
- recall **0.60465**
- F1 **0.66953**
- negative FP **0.0/s**
- eligible

O3:
- precision **0.72951**
- recall **0.68992**
- F1 **0.70916**
- negative FP **0.0/s**
- eligible

### V6B V2B comparison

O0:
- onset admission **1/56 = 0.01786**
- state admission **2/56 = 0.03571**
- trusted joint **0/56**
- high-confidence joint **0/49**
- negative FP **0.15695/s**

O2:
- onset admission **1/56 = 0.01786**
- state admission **10/56 = 0.17857**
- trusted joint **0/56**
- high-confidence joint **0/49**
- negative FP **0.78473/s**
- onset gain vs O0 **0.00**

O3:
- onset admission **2/56 = 0.03571**
- state admission **9/56 = 0.16071**
- trusted joint **0/56**
- high-confidence joint **0/49**
- negative FP **1.60086/s**
- onset gain vs O0 **+0.01786**

Frozen V6B gate required:
- onset-admission gain >= +0.20
- trusted joint gain >= +0.15
- high-confidence joint >=20%
- negative FP <=0.10/s
- state admission decline <=0.10

**No V6 alternative arm is development-interesting.**

### V6C model-free event-statistics audit

Synthetic:
- 273 positive clips
- 903 onset references
- 546 s
- aggregate **1.65385 onsets/s**
- clip-rate p50 **2.000/s**
- clip-rate p90 **3.000/s**
- IOI p50 **0.3483 s**
- IOI p90 **0.4180 s**
- repeated-attack fraction <=250 ms **26.67%**

V2B:
- 13 positive clips
- 164 frozen onset landmarks
- 110.023 s
- aggregate **1.49059 onsets/s**
- clip-rate p50 **1.177/s**
- clip-rate p90 **3.432/s**
- IOI p50 **0.2560 s**
- IOI p90 **0.8824 s**
- repeated-attack fraction <=250 ms **47.02%**

Synthetic zero IOIs occur from simultaneous multi-string chord attacks counted as separate references.

V2B therefore contains substantially more short-gap repeated attacks and a much longer sparse-event upper tail despite similar aggregate event density.

V2B lacks exhaustive sustain-duration annotations for every clip, so real active-duration/onset-to-sustain metrics were not fabricated.

### Supported interpretation

Fixed onset tolerance and focal loss do not repair real transfer.

O3 improves the synthetic onset task but transfers only one additional real onset landmark and greatly worsens negative false positives.

Combined with V6C, the evidence now points more strongly toward **synthetic event-timing / onset-representation mismatch** rather than threshold, affine normalization, bounded renderer realism, exact string/fret specificity, or simple onset-loss formulation.

Do not claim causal isolation.

### Guards

- no threshold search
- no loss-parameter search
- no decoder change
- no architecture or parameter-count change
- no renderer change
- no real audio in training
- V1.1 not used for tuning
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

No fresh holdout is warranted because no V6B arm passed.

**Resume instruction:** Stop at the V6 no-development-interesting-onset-objective boundary. Any next experiment that redesigns the synthetic event generator/onset curriculum, or any fresh real-domain training study, is a new project decision and requires explicit authorization.


## V7 synthetic event-timing adequacy design frozen — 2026-09-29

Generic continuation was used only for design/documentation at the V6 no-development-interesting-onset-objective boundary.

New files:
- `docs/astra/SYNTHETIC_EVENT_TIMING_ADEQUACY_V7_DESIGN_V1.md`
- `docs/astra/SYNTHETIC_EVENT_TIMING_ADEQUACY_V7_DESIGN_V1.json`

V7 tests whether the synthetic onset-time distribution itself contributes materially to the real-domain transfer failure.

Frozen V2B model-free targets from V6C:
- aggregate onset density **1.49059/s**
- IOI median **0.2560 s**
- IOI p90 **0.882358 s**
- repeated-attack fraction <=250 ms **0.47020**

Frozen timing arms:
- **E0** historical timing
- **E1** repeated-attack enriched: 45% of eligible adjacent pairs at 80–220 ms
- **E2** sparse-tail enriched: 20% at 700–1100 ms
- **E3** combined: 45% short, 20% long, 35% historical

Event count per clip, content templates, labels, splits, R3 renderer, architecture, exact state objective, historical O0 onset loss, thresholds, and decoder remain fixed.

### V7A model-free timing screen

No model training/inference.

Frozen timing distance compares:
- repeated-attack fraction
- IOI median
- IOI p90
- aggregate onset density

A non-baseline arm advances only if all are true vs E0:
- timing distance improves >=30% relative
- repeated-attack absolute error improves >=0.10
- IOI p90 absolute error improves >=0.20 s
- aggregate onset density stays within +/-15% of V2B
- clip bounds/labels remain valid

Advance at most **one** arm, lowest timing distance.

If none qualify, V7 stops before training.

### V7B bounded paired training

Only if V7A advances one arm:
- E0 baseline + one timing arm
- 500 steps/model
- max **1000 optimizer steps total**
- identical initialization and paired batches
- no retries
- no threshold search

### V7C synthetic sanity

Advancing arm must satisfy vs E0:
- F1 decline <=0.08
- recall decline <=0.08
- precision >=0.70
- synthetic negative FP <=0.10/s
- all 500 steps finite

### V7D V2B development gate

At unchanged 0.50/0.50:
- onset-admission gain >= +0.15
- trusted joint-admission gain >= +0.10
- high-confidence joint admission >=15%
- negative FP <=0.10/s
- state admission decline <=0.10

Any success requires a fresh holdout; V1.1 remains sealed.

No empirical V7 work has been run.
No new timing corpus generated.
No model training/inference.
No threshold/loss/renderer/architecture changes.
No real audio training.
P1/P2/P3 remain closed.
A2 remains closed.
Main/Production unchanged.

**Resume instruction:** V7 design is ready. Do not implement E1/E2/E3, generate timing manifests, train models, or evaluate V2B until the user explicitly authorizes V7 empirical execution. Generic continuation remains design/documentation only.


## V7 empirical execution complete at V7A — no arm advances — 2026-09-29

The user explicitly authorized V7 empirical execution.

Frozen results:
- `docs/astra/V7A_EVENT_TIMING_SCREEN_RESULT_V1.json`
- `docs/astra/V7A_TIMING_MANIFEST_IDENTITY_V1.json`
- `docs/astra/V7_SYNTHETIC_EVENT_TIMING_ADEQUACY_RESULT_V1.md`

### Corrected V7A population

The first local V7A summary accidentally included 21 negative-only clips in the onset-density denominator. This bookkeeping error was corrected before freezing the result.

Correct comparison population:
- 273 positive synthetic clips
- 546.0 positive seconds
- 903 positive onset references

No V7 rule, timing parameter, gate, or arm changed.

### V7A timing results

E0:
- rate **1.65385/s**
- IOI p50 **0.3400 s**
- IOI p90 **0.4000 s**
- repeat <=250 ms **26.67%**
- >=700 ms **6.67%**
- timing distance **1.13309**

E1:
- rate **1.65385/s**
- IOI p50 **0.18220 s**
- IOI p90 **0.4000 s**
- repeat <=250 ms **60.48%**
- >=700 ms **4.44%**
- timing distance **1.02428**
- failed all non-rate advancement checks

E2:
- rate **1.65385/s**
- IOI p50 **0.3400 s**
- IOI p90 **0.4000 s**
- repeat <=250 ms **26.67%**
- >=700 ms **6.67%**
- clip-boundary fallbacks **94**
- timing distance **1.13309**
- failed advancement

E3:
- rate **1.65385/s**
- IOI p50 **0.18118 s**
- IOI p90 **0.4000 s**
- repeat <=250 ms **60.48%**
- >=700 ms **8.41%**
- clip-boundary fallbacks **57**
- timing distance **1.02825**
- failed advancement

Frozen V2B targets:
- rate **1.49059/s**
- IOI p50 **0.2560 s**
- IOI p90 **0.88236 s**
- repeat <=250 ms **47.02%**

### V7 decision

**No non-baseline arm advances.**

Therefore:
- V7B training did not run
- V7C synthetic sanity did not run
- V7D V2B evaluation did not run
- optimizer steps: **0**
- model inference: **0**

The short-gap arms overshot repetition and did not create the long sparse tail.
The long-gap arms were constrained by the frozen 2-second clip duration; E2 required 94 deterministic fallbacks and E3 required 57.

### Evidence identity

Local V7A script SHA-256:
`93b2b6008f78bdef2d3cff7fa694a340beeb269eaea505b3fbc8897b899a3df3`

Corrected result SHA-256:
`7b4a52264b43c463740d5bf3abdb2f3edcebe0028904d907e9f01d75ecb6fc45`

Frozen timing-manifest SHA-256:
- E0 `596b6ff5ee935364d5ece217a806f3c9d2dc40189a4a388523dd4b3c96ef71b6`
- E1 `d0e4dbb867c5c228c124eab360b4539ecbd1880593cba8b190b0a486d7126c95`
- E2 `cfc167bea39978685b35a508d78af91c23152d8ea223838de62a6537f1f4b866`
- E3 `dd1bf82b851a8b16c87700479e8ee0cd2a2e26386a2adda0f4f0f264c2e7e243`

### Supported interpretation

The current fixed 2-second synthetic clip structure cannot adequately express the declared V2B-like long-tail timing distribution while preserving the frozen event counts/content.

Do not claim that longer clips will solve transfer; V7 stopped before training.

The next scientifically useful project would require a prospectively redesigned **longer-duration synthetic event curriculum / clip structure**, or a separately authorized fresh real-domain training study.

### Guards

- no optimizer work
- no model inference
- no threshold/loss/renderer/architecture/decoder changes
- no real audio in training
- V1.1 remains sealed
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

**Resume instruction:** Stop at the V7A no-advance boundary. Any experiment that changes synthetic clip duration/curriculum structure, or any fresh real-domain training study, is a new project decision and requires explicit authorization.


## V8 empirical execution complete at V8A — no arm advances — 2026-09-29

The user explicitly authorized the longer-duration synthetic curriculum project.

Frozen design/results:
- `docs/astra/LONG_DURATION_SYNTHETIC_CURRICULUM_V8_DESIGN_V1.md`
- `docs/astra/LONG_DURATION_SYNTHETIC_CURRICULUM_V8_DESIGN_V1.json`
- `astra_backend/synthetic/v8_long_duration_timing_screen_v1.py`
- `docs/astra/V8A_LONG_DURATION_TIMING_SCREEN_RESULT_V1.json`
- `docs/astra/V8_LONG_DURATION_SYNTHETIC_CURRICULUM_RESULT_V1.md`

Accepted V8A workflow:
- run **36523314347**
- job **109260764079**
- head `8e110132c778b7158a431a99e81bf2fe182e27d5`
- artifact **11012914117**
- artifact digest `sha256:56ff7a8c938a4818ab4d4cb4bf17a59a959b57482c0b40a38a301ba9e674e640`
- conclusion **success**

Earlier workflow attempts failed before producing accepted scientific output because the timing-only screen unnecessarily imported the audio frontend. The accepted runner is standalone model-free timing code. A pre-accepted accounting bug that collapsed simultaneous chord onset references was also corrected before the accepted result.

### V8A

L0 2-second baseline:
- onset density **1.65385/s**
- IOI p50 **0.3400 s**
- IOI p90 **0.4000 s**
- repeats <=250 ms **26.67%**
- timing distance **1.13309**

L1 4-second curriculum:
- onset density **1.63462/s**
- IOI p50 **0.3400 s**
- IOI p90 **0.85157 s**
- repeats <=250 ms **38.89%**
- boundary fallbacks **13/273 = 4.76%**
- timing distance **0.49263**
- relative timing-distance improvement **56.52%**
- passes distance/repetition/p90/rate/validity conditions
- **fails frozen <=2% fallback-rate condition**
- does not advance

L2 6-second curriculum:
- onset density **1.64103/s**
- IOI p50 **0.3400 s**
- IOI p90 **0.91007 s**
- repeats <=250 ms **36.52%**
- boundary fallbacks **40/273 = 14.65%**
- timing distance **0.51497**
- relative timing-distance improvement **54.55%**
- fails repeated-error improvement threshold and fallback-rate condition
- does not advance

Frozen V2B timing targets:
- onset density **1.49059/s**
- IOI p50 **0.2560 s**
- IOI p90 **0.88236 s**
- repeats <=250 ms **47.02%**

### V8 decision

**No arm advances.**

Therefore:
- no V8 waveform corpus rendered
- no V8B paired training
- no V8C synthetic sanity
- no V8D V2B inference
- waveform renders: 0
- optimizer steps: **0**
- model inference: **0**

### Supported interpretation

Longer clip duration removes much of the long-tail timing limitation. L1 and L2 both move IOI p90 near the V2B target and more than halve the frozen timing distance.

However, the frozen motif-placement scheme requires too many post-placement boundary corrections, so neither arm passes the prospective integrity gate.

This supports only the narrow conclusion that clip duration was part of the structural timing constraint. It does **not** establish that longer-duration training improves real transfer.

A next project should either:
1. prospectively redesign motif placement so long-duration timing is generated natively with essentially no fallback; or
2. separately design a fresh real-domain training study.

### Guards

- no waveform corpus rendered
- no optimizer work
- no model inference
- no threshold/loss/renderer/architecture/decoder changes
- no real audio training
- V1.1 remains sealed
- P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

**Resume instruction:** Stop at the V8A no-advance boundary. Any fallback-free long-duration curriculum redesign or fresh real-domain training study is a new project decision and requires explicit authorization.


## Explicit next steps with sound files — saved 2026-09-29

The user requested that the next steps be written explicitly into this handoff and that the **sound files** be included in the plan.

### Current scientific boundary

V8A is complete and no long-duration arm advanced to training.

Do **not** train L1/L2 from V8 as currently defined.  
Do **not** reuse V1.1 for tuning or confirmation.  
Do **not** open P1/P2/P3 or A2.  
Do **not** mutate main or Production.

### Preferred next project: fallback-free long-duration curriculum using the collected sound files as real-domain reference evidence

The next project should be **V9: fallback-free long-duration synthetic curriculum with sound-file-grounded timing statistics**.

The sound files already collected for the real-domain development set should be used only as frozen reference evidence unless the user separately authorizes real-audio training.

#### Step 1 — inventory and lock the sound files

Before any new model work:
1. enumerate every sound file currently approved for the development evidence set;
2. record filename / clip ID / duration / SHA-256 where available;
3. confirm which files are positive-guitar clips and which are negative/background-only clips;
4. keep V1.1 files separate and sealed;
5. do not add or remove sound files after the V9 design is frozen unless a new version is declared.

Create a machine-readable manifest for the sound files and freeze its hash.

#### Step 2 — derive model-free timing targets from the sound files

Using only the approved development sound files plus their frozen annotations:
- onset density per second;
- per-clip onset-rate distribution;
- IOI p10 / p50 / p90;
- repeated-attack fraction <=250 ms;
- long-gap fraction >=700 ms;
- simultaneous-onset fraction;
- negative/background duration;
- clip-duration distribution.

Do not infer missing onset labels from model predictions.
Do not fabricate sustain annotations that do not exist.

The existing V6C targets remain the current reference until the sound-file manifest/statistics are regenerated and frozen under V9.

#### Step 3 — design a fallback-free native event generator

The next synthetic generator must create long-duration timing **natively**, rather than placing motifs and correcting them afterward.

Required properties:
- no post-placement boundary shifting;
- no fallback/resample that changes an already generated event sequence;
- event times are sampled conditionally so every event fits inside the clip by construction;
- simultaneous chord attacks are preserved as separate onset references;
- negative-only clips remain negative-only;
- content-family distribution remains prospectively frozen;
- clip duration should be selected prospectively from a small declared set informed by the sound-file duration/timing distribution.

A likely first design should compare a 4-second and/or 6-second native generator, but the exact V9 arms must be frozen before output is viewed.

#### Step 4 — V9A model-free gate before any audio rendering

Generate timing manifests only.

Compare each proposed synthetic timing arm to the frozen sound-file timing targets.

Require, prospectively:
- substantial timing-distance improvement versus the 2-second baseline;
- improved repeated-attack error;
- improved IOI-p90 error;
- aggregate onset density within a declared tolerance;
- **zero boundary fallback by construction**;
- zero invalid clips/labels.

Advance at most one arm.

If no arm passes, stop with:
- 0 waveform renders
- 0 optimizer steps
- 0 model inference

#### Step 5 — render only if V9A passes

If one timing arm passes V9A:
- render exactly one long-duration synthetic arm plus the frozen R3 baseline;
- keep the R3 acoustic renderer fixed;
- freeze feature-array / dataset hashes;
- keep real sound files out of training at this stage.

#### Step 6 — bounded paired synthetic training

Only after V9A passes:
- train baseline + one advancing arm;
- same architecture;
- same initialization policy;
- exact-string/fret state objective;
- O0 exact-frame BCE onset loss;
- paired stratum schedule;
- 500 optimizer steps/model;
- maximum 1000 optimizer steps total;
- no retries;
- no threshold search;
- no decoder changes.

#### Step 7 — synthetic sanity before real sound-file evaluation

The advancing arm must pass a frozen synthetic sanity gate before any real development sound file is scored.

At minimum retain:
- precision floor;
- F1/recall degradation limits;
- negative-only synthetic FP limit;
- finite-loss / exact-step checks.

If it fails, stop before real sound-file inference.

#### Step 8 — evaluate on the approved development sound files only

If synthetic sanity passes:
- evaluate exactly once on the approved development sound files;
- use the existing frozen 0.50 / 0.50 thresholds;
- use the ordinary decoder for negative false-positive rate;
- report onset admission, state admission, trusted joint admission, high-confidence joint admission, and negative FP/s;
- preserve per-clip results so any improvement can be audited.

Do not use V1.1.

#### Step 9 — require a fresh holdout before any broader claim

If the V9 candidate passes its development gate:
- freeze the model and all settings;
- collect a **fresh, prospectively defined set of real sound files** not used in V2B/V9 development;
- annotate those clips before inference;
- run exactly one confirmation evaluation.

No claim of product readiness should be made from development sound files alone.

### Alternative project: fresh real-domain training study

If the user explicitly chooses real-domain training instead of V9 synthetic redesign, treat it as a separate project.

Before training on any sound files:
1. freeze a training/development/holdout split;
2. ensure no V1.1 leakage;
3. define annotation requirements;
4. define whether clips are licensed/authorized for model-training use;
5. freeze preprocessing, augmentations, optimizer budget, and admission criteria;
6. preserve a fresh untouched real-sound holdout.

Do not silently convert the existing development sound files into training data.

### Exact resume instruction

At the next generic “continue”, remain at design/documentation only.

The preferred next action is to prepare the **V9 sound-file manifest + fallback-free curriculum design**.

Do **not**:
- train on the sound files;
- generate new model weights;
- run V9 model inference;
- use V1.1;
- open P1/P2/P3;
- alter thresholds/decoder;
- mutate main/Production;

until the user explicitly authorizes the empirical V9 execution phase.


## Supervisory review after V8 / before V9 — 2026-09-29

**Current resume authority.** This section supersedes conflicting next-step instructions above. V8 remains frozen with no advancing arm. V9 is a proposal, not launch-ready. The next task is a bounded model-free evidence and measurement audit from existing committed records, followed by one concrete design. No new experiment or audio access is authorized by this review.

### Evidence reviewed and limits

Reviewed remote head `c80f1b666122c9b670e50fcd21cace3594bc9e71`, AGENTS.md, both handoffs, V8 design/spec/result, V8 timing runner (blob `3c7efea4ce00d737a9ed1bb2711185b7a5fb1955`) and workflow, V2B collected-audio manifest, duration correction and annotations, and V6 onset-objective helper. Connected GitHub independently reports accepted V8 run 36523314347/job 109260764079 successful. The supplied screenshot points to this same head.

This was source/document review, not independent experimental reproduction. No corpus audio, model weights or result artifact was downloaded; no model, test suite, timing generator, optimizer or workflow was run. V4–V7 empirical claims were not fully reproduced or their complete local execution chains audited. Existing dirty/stale local checkouts were preserved; write from the verified remote tree.

### Assessment and concrete corrections

GPT-5.6 correctly rejected V8 under its frozen gate and avoided unnecessary training. Keep that discipline. L1's reported 56.52% distance improvement is useful development evidence, but its 13 fallbacks fail the declared gate; L2 also fails. Neither establishes improved transcription. The next priority is trustworthy measurement, not another iteration toward the same potentially misleading scalar.

1. **Attack units are inconsistent.** V8 `base_attacks("chords")` emits three identical times for each chord; `summarize` includes zero IOIs in `x <= .25`. L0's repeated fraction and simultaneous fraction are both 0.2666667: from the inspected base templates, all of that “repeat” count is simultaneous chord multiplicity, not successive attacks. V2B's 164 references are spectral-flux timestamps, not per-string chord notes. Comparing those rates/IOIs directly conflates polyphony with temporal density. Preserve V6–V8 results; do not silently recalculate their acceptance. Prospectively report acoustic attack groups separately from note-level targets. Keep all chord notes in training labels, but count a simultaneous group once for attack timing. Define grouping tolerance and positive-gap repeat rules before recomputation. A short gap alone does not establish a repeated pitch or picking technique.

2. **Model-free does not mean verified ground truth.** The V2B annotation file explicitly uses spectral-flux onset detection and YIN stability, with no string/fret annotations and no exhaustive polyphonic truth. “High confidence” is an algorithmic category unless independent QA is documented. Rate 1.49059/s and IOI p90 0.882358 s characterize this detected-landmark sample, not necessarily all audible attacks. V9 must not claim that matching detector output solves a performance-domain mismatch. Pin detector settings/source and document completeness/uncertainty. Independent audio QA, if needed, is a separate concrete scoped step; do not invent it or relabel the existing landmarks as human-verified.

3. **The sound inventory already exists.** Start from `docs/astra/V2B_CALIBRATION_DEVELOPMENT_COLLECTED_AUDIO_V1.json`: exactly C01–C13 positive and D01–D04 negative, with filenames, original-byte hashes, source URLs and crop endpoints. Apply the existing `V2B_CALIBRATION_DEVELOPMENT_COLLECTION_CORRECTION_V2.json` overlay: C04 duration 5.799183673469388 s, D01 8.097959183673469 s; totals 110.023183673 s positive and 31.857959184 s negative. Do not enumerate every uploaded MP3 as eligible: other uploads belong to the excluded V1.1 pool. Reconcile annotations (57/50 raw pitch landmarks) with reported scoring populations (56/49) using recorded exclusions; do not silently change denominators. Preserve both source-byte identity and annotation/crop identity. No re-download or new decoding is needed to copy recorded metadata; mark hash verification as inherited, not newly performed.

4. **V1.1 is closed and already evaluated, not an untouched holdout.** Its prior 1/72 result is exposed evidence. “Sealed” here means no further use for tuning/confirmation. Keep it excluded, along with P1/P2/P3. Any future confirmation set must be genuinely new and grouped by source recording/creator where possible, not another crop or renamed copy of development audio.

5. **V8 did not isolate duration.** L1/L2 also repeat motifs, change repeated-family spacing to 0.18 s and introduce random 0.7–1.1 s inter-motif gaps. Improvements concern this complete construction package, not duration alone. Its `invalidClipCount` checks onset bounds only: it does not validate pitch/string/fret, offsets, sustains, overlap, split identity or negative examples. Negative clips are skipped entirely by the screen. Its fallback numerator counts correction operations, while the spec says fraction of clips with fallback. Those can diverge. Record these limitations without changing V8's frozen result.

6. **Do not infer exhaustive causes from failed small interventions.** V4/V5/V6 failures reject those bounded packages; they do not rule out renderer realism, target design, loss formulation, calibration or representation as interacting contributors. The event-timing hypothesis remains plausible and unproven. V2B has repeatedly informed model/design decisions and is development data, even though its waveforms were not used for gradient training.

7. **Launch and reproducibility safeguards are incomplete.** V8's workflow checks three launch fields but does not pin runner/spec hashes, consume a unique scope, reject reruns or run focused admission tests. Preserve historical infrastructure attempts and corrections honestly; “accepted output” does not erase prior attempts. Future result paths must refuse overwrites, and infrastructure repair must be distinguished from scientific retries. V7 records a local script hash; a hash without the exact retained script is insufficient reproduction evidence.

### Exact next authorized task: model-free evidence audit and one draft design

Do this useful preparation without asking again for permission to edit documentation or inspect committed source. This review does not grant V9 empirical execution.

1. Create `docs/astra/POST_V8_MEASUREMENT_REVIEW_V1.md` and a machine-readable companion. Reconcile the 17-file V2B manifest, corrections, annotation identity, exclusions, durations, prior exposure and source-overlap checks using existing records only. Include a status table distinguishing recorded, independently verified, missing and contradictory evidence. Keep original audio outside Git. Do not access V1.1/P1/P2/P3 bytes or expand the sound pool.

2. Specify a common timing contract before recalculating anything: acoustic-group versus note units; simultaneous tolerance; crop-local origin; exact sample duration versus rounded metadata; endpoint inclusion; quantile convention; pooling versus clip-balanced summaries; empty/single-attack clips; positive-only density denominator; separate negative duration; and repeat fraction over eligible positive IOIs. Report per-clip/per-family counts as well as pooled values. Do not deduce simultaneous note multiplicity or exhaustive attack coverage from the real landmark lists.

3. Implement only a small pure measurement/manifest validator if needed, with hand-authored JSON fixtures and no audio/model dependencies. Test a three-note chord as one acoustic group and three note labels; two distinct short-gap attacks; singleton/empty clips; crop boundaries; duplicate IDs; missing/nonfinite/boolean numeric fields; impossible durations; corrected duration propagation; and count/rate consistency. Fixture checks are authorized. Do not generate V9 empirical timing populations or run historical experiments as a “test.” Record exact focused commands and results.

4. Produce a short reconciliation of historical summaries from committed records. Distinguish V6's synthetic p50/p90 0.3483/0.4180 from V7/V8 template values 0.34/0.40; trace data and transformation provenance rather than assume they are the identical baseline. Locate the full V6/V7 orchestration and measurement source if retained; mark it unavailable if only helper files/hashes survive. Do not reconstruct missing evidence by new model runs.

5. Draft `docs/astra/FALLBACK_FREE_CURRICULUM_V9_DESIGN_V1.md` and matching JSON, explicitly **not launch-ready** until measurement comparability is resolved. Choose one hypothesis and bounded generator package; do not default to trying both 4 and 6 seconds. Explain any chosen duration, content count and gap distribution prospectively. Preserve original note labels and generate feasible onsets AND offsets/sustains by construction. Define conditional sampling, support, infeasibility handling and RNG identity mathematically. Avoid hidden rejection loops, clipping, compression, event deletion or reseeding to force a gate pass. “Zero fallback” is not a substitute for distribution fidelity or full label validity.

6. Before a future empirical phase, freeze all numerical gates and exact comparators. If corrected measurement units require a new distance/target version, document why; historical gates remain unchanged. Freeze weights/scales, all metric definitions, unique seeds, maximum arms, no-advance behavior and tie-breaking. Do not choose gates after viewing candidate timing output. Gate feasibility and sample limitations must be reviewable before generation.

7. Specify the downstream experiment completely on paper: same-runtime baseline and intervention, architecture/source pins, initialization mapping, renderer, frontend, loss reductions, batch and split identities, padding/masks, frame/clip weighting, train duration and number of frames/events seen. Two 500-update models at different sequence lengths do not have equal compute or exposure. Retain the existing maximum two models/1,000 updates unless separately authorized; add explicit render, inference, CPU-time and storage ceilings before launch. Use a common fixed synthetic evaluation population for comparative sanity, plus a separately declared duration stress test if justified. Prevent shared base motifs/recordings crossing train/test.

8. Prospectively encode the full order: timing gate -> render -> train -> synthetic sanity -> permitted V2B evaluation. Failed sanity must technically prevent real inference; the recorded V5 premature T1 evaluation shows why prose alone is insufficient. Freeze eligible clip/landmark populations and scoring functions, including compatibility aggregation and exact timing/frame semantics. Compatible state/onset admission is diagnostic, not exact fingering or ordinary-decoder note accuracy. Keep ordinary-decoder negative FP counts and exact seconds. Any fresh confirmation acquisition/evaluation requires its own reviewable scope; it is not automatic on a development pass.

9. Retain exact source, manifests, settings, model checkpoints and raw result JSON in durable authorized storage for any later execution. Hashes alone and expiring artifacts are insufficient. No original sound files or credentials in Git. Define one consumed launch scope across all invocation paths, source/spec validation, no automatic retry, deadline checks, partial-failure receipts and non-overwriting outputs. Do not modify consumed historical launch markers.

10. Save the audit, any pure validator/tests and the draft design; synchronize both handoff headers and final resume instructions; verify remote ref and content. End with one concrete readiness assessment and an exact proposed empirical scope if all dependencies are satisfied. If reference completeness or timing comparability is unresolved, recommend the smallest annotation/measurement resolution step instead of launching V9. No automatic V10 or indefinite sequence of benchmark-fitting attempts.

### Authorization and stop boundary

The current request authorizes this review and saving instructions. Existing sound-file intake and prior experiment authorizations remain historical scoped grants; do not ask to repeat completed authorized work, and do not treat them as approval for a new empirical project. The latest pre-review handoff explicitly reserves V9 empirical execution for an explicit user decision. Honor any later authorization according to its actual scope, without requiring a magic phrase.

For now: committed-record review, documentation and pure fixture tests only. No new audio decoding/annotation, V9 timing population generation, waveform rendering, weights, inference, optimizer, launch marker, workflow dispatch, A2, main or production changes.

**Resume instruction for GPT-5.6:** Audit V2B identity and timing measurement semantics first, particularly chord multiplicity versus distinct attacks and algorithmic-label uncertainty. Prepare one precise, testable V9 draft only after those issues are documented. Preserve V8's no-advance result and all sound-file identities. Save a concrete readiness checkpoint before requesting any new empirical authorization.


## Post-V8 measurement audit + V9 draft complete — 2026-09-29

**This is the current resume authority and supersedes the earlier instruction to perform the post-V8 audit/design.**

Completed and saved:
- `docs/astra/POST_V8_MEASUREMENT_REVIEW_V1.md`
- `docs/astra/POST_V8_MEASUREMENT_REVIEW_V1.json`
- `astra_backend/synthetic/v9_measurement_contract_v1.py`
- `astra_backend/synthetic/test_v9_measurement_contract_v1.py`
- `docs/astra/FALLBACK_FREE_CURRICULUM_V9_DESIGN_V1.md`
- `docs/astra/FALLBACK_FREE_CURRICULUM_V9_DESIGN_V1.json`

Focused pure-Python fixture validation: 10/10 tests passed. Audio decoding 0; model inference 0; optimizer steps 0; workflow dispatches 0; V1.1/P1/P2/P3/A2 access none; main/Production unchanged.

### Measurement finding that must be preserved

Historical V6/V7/V8 acceptance remains frozen, but the synthetic-to-V2B timing scalar is not prospectively trustworthy as one common physical unit. Retained V8 source counts simultaneous chord-note timestamps as zero IOIs and those zero IOIs also enter the <=250 ms repeat fraction. L0's simultaneous and repeat fractions are both 0.2666667. V2B's 164 references are spectral-flux landmark timestamps, not note-level chord multiplicity.

Future timing work must separate note/string/fret labels from acoustic attack groups used for timing-distribution measurement. Do not retroactively alter V6/V7/V8 decisions.

### Reconciled V2B evidence

Eligible inventory remains exactly C01-C13 positive and D01-D04 negative-only. Frozen corrected durations: C04 5.799183673469388 s; D01 8.097959183673469 s; totals 110.023183673 s positive and 31.857959184 s negative.

Raw annotations contain 164 onset landmarks, 57 trusted-pitch landmarks and 50 high-confidence pitch landmarks, from spectral-flux onset detection plus YIN pitch stability. There is no string/fret truth and no exhaustive polyphonic truth. V6 scoring later uses 56 trusted / 49 high-confidence refs; the exact exclusion provenance remains unresolved in the committed result and must not be guessed.

### V9 design status

One bounded design is drafted: one 4-second intervention arm, native conditional feasible timing generation, separate acoustic-group timing and note labels, onsets and offsets/sustains valid by construction, no post-placement shift, clipping/compression/event deletion, hidden rejection loop or reseed-to-pass. Infeasible instances fail closed. Maximum downstream models remains 2 and maximum downstream optimizer steps remains 1,000 total.

**V9 is not launch-ready.** Numerical gates and common-unit timing targets are intentionally not frozen yet.

### Exact next authorized task: PRE-V9-MEASUREMENT-V1

At a generic continue, perform only this bounded model-free measurement step from committed records:

1. Use the committed V2B manifest, duration-correction and annotation JSON plus retained frozen synthetic baseline records/source.
2. Do not read/decode original audio and do not add/change annotations.
3. Freeze the prospective common timing semantics before calculation: acoustic attack groups separate from note labels; 10 ms simultaneous grouping tolerance; crop-local origin; exact corrected durations; half-open [0,duration) endpoint; positive IOIs only; repeat250 over eligible positive IOIs; positive density excludes negative-only time; empty/singleton clips have zero IOIs and undefined clip repeat; report pooled/per-clip summaries and per-family synthetic summaries.
4. Produce a versioned common-unit target/reference table while preserving historical V6/V7/V8 metrics separately.
5. Reconcile the 57/50 -> 56/49 scoring denominator if a committed exclusion record exists; otherwise mark it unresolved.
6. Run only focused pure measurement/fixture checks. No V9 candidate timing population is part of this step.
7. Save source, machine-readable result, human review and both synchronized handoffs; verify remote branch content.

### Stop boundary

Do not yet generate a V9 candidate timing arm, render waveforms, train models, run V2B model inference, dispatch a workflow/launch marker, access V1.1/P1/P2/P3, open A2, alter thresholds/decoder, or mutate main/Production.

After PRE-V9-MEASUREMENT-V1, stop at the corrected reference table and readiness decision. If comparability is resolved, the next user decision is whether to authorize empirical V9 under a fully frozen numerical contract.


## PRE-V9 common-unit measurement complete — 2026-09-29

**Current resume authority. This section supersedes the earlier PRE-V9-MEASUREMENT-V1 task wording.**

Completed and saved:
- `astra_backend/synthetic/pre_v9_common_unit_measurement_v1.py`
- `astra_backend/synthetic/test_pre_v9_common_unit_measurement_v1.py`
- `docs/astra/PRE_V9_COMMON_UNIT_MEASUREMENT_V1.json`
- `docs/astra/PRE_V9_COMMON_UNIT_MEASUREMENT_V1.md`

The post-V8 review was also amended with the committed V2C scoring-denominator provenance.

### Frozen common-unit reference

Prospective timing semantics are now fixed for V9 preparation:
- acoustic attack groups are separate from note/string/fret labels;
- simultaneous tolerance = 10 ms;
- crop-local time;
- exact corrected duration;
- half-open [0,duration);
- positive within-clip IOIs only;
- repeat250 = fraction of positive IOIs <=250 ms;
- longGap700 = fraction >=700 ms;
- positive density excludes negative-only time;
- linear quantiles at h=(n-1)*p.

V2B:
- 164 raw spectral-flux landmarks -> 164 attack groups (0 merges at 10 ms)
- 110.023183673 s positive; 31.857959184 s negative
- attack-group density 1.490594932/s
- IOI p50 0.256 s
- IOI p90 0.882358 s
- repeat250 0.4701986755
- longGap700 0.1258278146

Retained V8 L0 source remeasured in the same unit:
- 903 note labels -> 735 attack groups
- 546 s positive
- density 1.346153846/s
- IOI p50 0.360 s
- IOI p90 0.400 s
- repeat250 0.0
- longGap700 0.0909090909

The historical 26.67% V8 L0 repeat fraction was simultaneous chord-note multiplicity, not distinct short-gap attacks. Historical V6/V7/V8 results remain frozen and are not rewritten.

### Pitch scoring provenance resolved

Committed V2C evidence records the single unrepresentable landmark excluded from scoring:
- C06
- 0.042667 s
- MIDI 37
- confidence high

Thus raw 57 trusted / 50 high-confidence becomes 56 / 49 scorable references without inference.

### Execution boundary preserved

This measurement step used committed records/source only:
- original audio decoded: 0
- new annotations: 0
- V9 candidate timing populations: 0
- waveform renders: 0
- model inference: 0
- optimizer steps: 0
- workflow dispatches: 0
- V1.1/P1/P2/P3/A2 access: none
- main/Production unchanged

### Readiness decision

Common-unit timing comparability is now sufficiently resolved to prepare a final V9 empirical contract. **V9 empirical execution is still not authorized.**

The draft V9 design remains:
- one 4-second fallback-free native generator only;
- onsets + offsets/sustains feasible by construction;
- no post-placement shift, clipping, compression, event deletion, hidden rejection loop, or reseed-to-pass;
- fail closed on infeasibility;
- maximum 2 models and 1,000 optimizer steps total if later authorized.

### Exact next step requiring a fresh user decision

Do not generate any V9 candidate timing output yet.

The next project step is to finalize and freeze the V9 numerical contract and then, only if the user explicitly authorizes empirical V9, execute it in this order:

1. freeze exact gap supports/weights, content counts, sustain supports, seeds/splits, same-runtime comparator, all numerical gates, distance weights/scales, render/inference/CPU/storage ceilings, and consumed one-shot launch scope;
2. generate timing manifests only;
3. apply the fail-closed timing/full-label gate;
4. render baseline + one intervention only if the timing gate passes;
5. train at most two 500-update models;
6. apply synthetic sanity;
7. allow one V2B development evaluation only if synthetic sanity passes;
8. freeze the result; no automatic V10.

Until that fresh decision: documentation review is allowed, but no V9 candidate generation, workflow dispatch, rendering, model weights, inference, optimizer, new audio/annotation, V1.1/P1/P2/P3/A2, main or Production changes.

**Resume instruction:** Stop at the V9 empirical-decision boundary. If the user explicitly authorizes V9 empirical work, first freeze the complete numerical/spec/launch contract before generating candidate output. Otherwise do not execute V9.


## V9 final empirical contract frozen — 2026-09-29

**Current resume authority. This section supersedes the earlier instruction to prepare the final V9 numerical/spec/launch contract.**

Completed and saved:
- `docs/astra/FALLBACK_FREE_CURRICULUM_V9_FINAL_CONTRACT_V1.md`
- `docs/astra/FALLBACK_FREE_CURRICULUM_V9_FINAL_CONTRACT_V1.json`
- `astra_backend/synthetic/v9_final_contract_validator_v1.py`
- `astra_backend/synthetic/test_v9_final_contract_validator_v1.py`

The earlier V9 draft design is explicitly marked superseded.

### Frozen intervention

Exactly one intervention arm:
- 4.0-second clips
- 294 total slots
- 273 positive / 21 negative-only
- train/validation/test = 210/42/42
- 1,638 acoustic attack groups across 1,092 positive seconds
- attack-group density = 1.500000000/s
- 1,806 attacked note labels
- attacked-note-label density = 1.6538461538461537/s, preserving the historical V8 L0 attacked-label density

Attack groups per positive clip:
- isolated 5
- scales 8
- chords 2
- repeated 8
- legato 4
- palmmute 10
- mixed-positive 4

Chord attacks retain three simultaneous note labels per acoustic group.

### Frozen gap package

Deterministic per-family class multisets, with SHA-256 permutation inside each clip:

- isolated: S,S,S,M
- scales: S,S,S,M,M,M,L
- chords: M
- repeated: S,S,S,M,M,M,L
- legato: S,M,L
- palmmute: S,S,S,S,M,M,M,M,L
- mixed-positive: S,S,L

Aggregate:
- S = 630 / 1,365 = 0.4615384615
- M = 546 / 1,365 = 0.4000000000
- L = 189 / 1,365 = 0.1384615385

Supports:
- S [0.080, 0.250] s
- M [0.251, 0.316] s
- L [0.700, 1.360] s
- first attack [0.050, 0.120] s
- final margin 0.120 s
- sustain [0.120, 0.480] s

Worst-case palmmute support occupies 3.864 s, so the declared 4-second support fits without any planned fallback.

No clipping, shifting, compression, deletion, hidden rejection loop, retry, or reseed-to-pass is allowed. Any infeasible clip fails closed.

### Frozen corrected timing gate

Corrected timing distance V1 now includes common-unit:
- repeat250
- IOI p50
- IOI p90
- attack-group density
- longGap700

Frozen V8 L0 common-unit distance = 1.6103247396.

The one V9 manifest advances only if every condition passes, including:
- relative distance improvement >=60%
- density relative error <=5%
- p50 error <=0.050 s
- p90 error <=0.150 s
- repeat250 error <=0.080
- longGap700 error <=0.050
- exactly 273 positive / 21 negative-only clips
- exactly 1,638 attack groups / 1,806 attacked note labels
- zero infeasible clips
- zero invalid labels/offsets
- zero fallback operations
- exact split/source/spec/reference identity

Failure stops before rendering with 0 optimizer steps and 0 model inference.

### Frozen downstream ceiling if later explicitly authorized

Rendering:
- exactly 2 datasets
- comparator 588 s
- intervention 1,176 s
- R3 fixed
- <=30 CPU minutes render
- <=700 MiB total persisted synthetic datasets
- $0 paid compute

Training:
- exactly 2 S6 nonlinear models
- 500 optimizer updates/model
- <=1,000 total
- active-state weight 9.0
- onset positive weight 8.0
- onset loss multiplier 4.0
- Adam lr 0.003
- batch size 128
- exact-string/fret state objective
- O0 exact-frame BCE onset objective
- thresholds 0.50/0.50
- decoder unchanged
- paired initialization and strata
- report actual frames/events/attack groups/seconds because equal update counts are not equal exposure
- <=60 CPU minutes fit/eval
- zero automatic scientific retries

Synthetic sanity remains a technical gate before any V2B inference. V2B development scoring remains fixed to 56 trusted / 49 high-confidence refs and 31.857959184 negative seconds.

### Launch state

**No launch is armed. No V9 candidate timing population has been generated.**

A future launch must bind:
- final contract blob
- implementation source blobs
- workflow blob
- common-unit reference and V2B record blobs
- unique consumed launch identity
- branch/ref and run-attempt=1
- fail-if-output-exists paths
- deadlines and partial-failure receipt
- durable result/checkpoint retention

### Current authorization boundary

The user’s generic continue allowed final contract preparation only under the existing handoff. It did not authorize empirical V9 execution.

Current counts remain:
- V9 candidate outputs: 0
- waveform renders: 0
- model inference: 0
- optimizer steps: 0
- workflow dispatches: 0
- V1.1/P1/P2/P3/A2 access: none
- main/Production unchanged

**Resume instruction:** Stop here. The next action is empirical V9 execution under the exact frozen contract, and it requires explicit user authorization. If authorization is given, first implement and pin the generator/runner/workflow and validate them model-free without generating candidate timing output; only then consume one launch scope and execute the ordered V9 gate chain. No automatic V10.


## V9 empirical execution complete — synthetic sanity FAIL — 2026-09-29

**Current resume authority. This section supersedes the earlier V9 authorization/execution instruction.**

Explicit user authorization was consumed under launch identity:
- `v9-frozen-v1-20260929-01`

Frozen result:
- `docs/astra/V9_FALLBACK_FREE_CURRICULUM_RESULT_V1.json`
- `docs/astra/V9_FALLBACK_FREE_CURRICULUM_RESULT_V1.md`

Accepted preflight:
- run **36526305988**
- job **109270011760**
- head `a0c09415abba839cf525531141dcfa7822e95f68`
- artifact **11014613083**
- digest `sha256:c764c270d0b280895fb755adcb32032b3d604e66ccef0ae627362d9b26a50b30`
- conclusion **success**

One earlier preflight run failed before candidate generation because the workflow test command omitted the repository root from PYTHONPATH. That was an infrastructure-only failure: 0 candidate timings, 0 renders, 0 optimizer steps, 0 inference. The path was repaired before the consumed empirical launch.

Empirical execution:
- run **36526450793**
- job **109270456836**
- head `f488e857c821fbee2846aa5ae3a511a2e30e8007`
- artifact **11015165684**
- digest `sha256:e5ebb4c1450cbfac7453dc9613c33e0f64a5694044c2195ceeea36651f65af3c`
- workflow conclusion **success**
- models **2**
- optimizer steps **1,000 total**
- automatic scientific retries **0**
- threshold search **false**
- real-audio model inference **0**

### V9A timing gate passed

The single frozen timing arm passed every prospective condition:
- V8 L0 corrected timing distance **1.6103247396**
- V9 timing distance **0.0918590535**
- relative improvement **94.30%**
- density **1.500000/s**
- IOI p50 **0.257750 s**
- IOI p90 **0.902659 s**
- repeat250 **46.1538%**
- longGap700 **13.8462%**
- 1,638 acoustic attack groups
- 1,806 attacked note labels
- 0 infeasible clips
- 0 invalid labels/offsets
- 0 fallback operations

This establishes that the frozen fallback-free construction can closely match the chosen common-unit timing statistics.

### Render/training completed within ceilings

R3 render:
- comparator: 294 clips / 588 s / 87 frames per clip / 735 attack groups / 903 attacked note labels
- V9: 294 clips / 1,176 s / 173 frames per clip / 1,638 attack groups / 1,806 attacked note labels
- render time **64.49 s**
- persisted datasets **41.49 MiB**
- no external audio assets

Training exposure:
- 500 steps/model
- 64,000 sampled frames/model
- 1,486.077 sampled frame-seconds/model
- 16,000 sampled attack frames/model
- comparator sampled attacked note labels **19,702**
- V9 sampled attacked note labels **17,676**

Equal update/frame exposure therefore did not produce equal attacked-note-label exposure. Preserve this as an observed package difference; do not post-hoc resample V9.

### Synthetic sanity failed

Common fixed comparator test population:

Comparator:
- precision **0.826923**
- recall **0.666667**
- F1 **0.738197**
- TP/FP/FN **86 / 18 / 43**
- negative FP/s **0**
- state admission **0.294574**
- onset admission **0.620155**
- joint admission **0.286822**

V9 intervention:
- precision **0.324427**
- recall **0.658915**
- F1 **0.434783**
- TP/FP/FN **85 / 177 / 44**
- negative FP/s **0**
- state admission **0.310078**
- onset admission **0.682171**
- joint admission **0.286822**

Frozen checks:
- onset precision >=0.70: **FAIL**
- pitch-onset F1 decline <=0.08: **FAIL**
- onset recall decline <=0.08: PASS
- negative FP/s <=0.10: PASS
- exactly 500 steps/model: PASS
- finite metrics: PASS

### V9 decision

**V9 stops at synthetic sanity. It does not advance to V2B.**

The technical gate correctly blocked real-development inference:
- V2B model inference **0**
- V1.1/P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

Do not:
- bypass the failed sanity gate;
- run V2B anyway;
- retune thresholds;
- change sampler weights;
- equalize attacked-label exposure post hoc and call it the same V9;
- rerun V9;
- open V10 automatically.

The supported interpretation is narrow: the timing generator solved the common-unit timing-fit problem, but the complete 4-second V9 training package badly degraded synthetic precision/F1. Do not claim duration alone caused the failure because duration, attack allocation, gap distribution, sustain placement, and effective attacked-note-label exposure changed together.

Artifact evidence:
- `timing.json` SHA-256 `ae9384286a40009a328ce98fd90f15f3bbc4e31b9686f48e6f81a5275d41d913`
- render receipt `817a474c5ffabf34a43d5fc19b2e8836982fc86a29bcdc762ada8cfb48aa7f0d`
- train result `7f1b51592fdaf01f77d5d658abe76cc5f22de76ca70cdcf5bcfc9ac6e89dcfc7`
- comparator checkpoint `653587a0ac02b383daca3740d26fe0685bd3fc3c88cfd86335f4a90ad3bfe8a5`
- intervention checkpoint `98668a9e044d1de1823f6e55c982fe0729bb2361264ba9d6264b565b8ef48115`
- execution receipt `62da92fdba5dc195eb378a45daeab1adbbea92d4677b2d72c7e2e083ae4a050d`

The workflow artifact is retained through 2026-10-29. The immutable hashes and scientific result are committed.

### Exact next decision boundary

Stop model execution here.

A future project must be separately and prospectively defined. The smallest scientifically motivated question suggested by V9 is whether **training exposure / attack-label weighting** rather than timing-fit itself explains the precision collapse, but that would be a new controlled study, not a V9 retry.

**Resume instruction:** Preserve V9 as a frozen FAIL at synthetic sanity. Do not perform V2B inference from V9 and do not create V10 automatically. At a generic “continue”, perform documentation/review only unless the user explicitly authorizes a new project question.


## V10 exposure-isolation study prospectively frozen — 2026-09-29

**Current resume authority. This section supersedes the earlier generic “new project question” boundary.**

The user explicitly authorized opening the next project question. That authorization was used only for prospective study definition, static implementation, and model-free preflight. It was not treated as informed authorization for empirical V10 execution because the V10 contract did not yet exist when the authorization was given.

Completed and saved:
- `docs/astra/V10_PROJECT_AUTHORIZATION_V1.json`
- `docs/astra/V10_EXPOSURE_ISOLATION_CONTRACT_V1.md`
- `docs/astra/V10_EXPOSURE_ISOLATION_CONTRACT_V1.json`
- `astra_backend/synthetic/v10_exposure_isolation_v1.py`
- `astra_backend/synthetic/test_v10_exposure_isolation_v1.py`
- `astra_backend/synthetic/v10_contract_validator_v1.py`
- `astra_backend/synthetic/test_v10_contract_validator_v1.py`
- `docs/astra/V10_PREFLIGHT_RESULT_V1.md`
- `docs/astra/V10_PREFLIGHT_RESULT_V1.json`

### Frozen question

Does exact matching of sampled attacked-note-label exposure, while holding the frozen V9 dataset/model/loss/thresholds/update count/non-positive strata/per-step shuffle fixed, materially restore synthetic pitch-onset precision/F1?

This is a new synthetic-only causal diagnostic, not a V9 retry.

### Frozen arms

Both arms train on the exact same regenerated frozen V9 4-second dataset.

Control:
- exact frozen V9 positive-onset sampling

Intervention:
- changes only which positive-onset frames are selected
- total positive-onset frame slots remains 16,000
- attacked-note-label exposure is exactly matched to the old comparator exposure: **19,702**

Exposure arithmetic:
- V9 control expected labels: **17,676**
- target labels: **19,702**
- 1,851 three-label positive frames
- 14,149 one-label positive frames
- 351 updates with 4 multi-label positive frames
- 149 updates with 3 multi-label positive frames

Non-positive stratum selections and per-step shuffle are identical across arms.

Everything else is fixed:
- S6 nonlinear model
- same initialization
- batch size 128
- 500 updates/model
- max 1,000 total
- Adam lr 0.003
- state active weight 9.0
- onset positive weight 8.0
- onset loss multiplier 4.0
- thresholds 0.50/0.50
- no threshold search
- no scientific retry

### Frozen validity and support gates

The V10 control must exactly reproduce the frozen V9 common-population precision/recall/F1 within 1e-12 and attacked-label exposure 17,676. Otherwise the study is invalid.

Exposure support requires all:
- common 2-second comparator-test precision gain >= +0.20
- common F1 gain >= +0.15
- common recall decline <=0.08
- common negative FP/s <=0.10
- V9-test precision decline <=0.05
- V9-test F1 decline <=0.05
- exact 17,676 / 19,702 control/intervention attacked-label exposure
- exactly 500 updates/model
- finite metrics
- no threshold search/retry

There is **no V2B stage in V10** under any outcome.

### Model-free preflight passed

- run **36527632335**
- job **109274053805**
- head `b55f2bebf1df366f08c5262815afe5dbbe82ca95`
- artifact **11014419820**
- digest `sha256:b62962f0715471d0a49e7402fa0cd6baa1383029db7d23db5ff26164c25a2dbd`
- conclusion **success**
- artifact retained through 2026-10-29

Preflight counts:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0

### Current authorization boundary

**Empirical V10 execution is not yet authorized.**

A fresh explicit authorization, now that the exact V10 contract is visible/frozen, is required before:
- rebuilding V9/comparator datasets;
- training the two V10 models;
- any optimizer step;
- any model inference.

Even after a V10 empirical result, V2B remains out of scope and would require a separate project decision.

V1.1/P1/P2/P3/A2 remain untouched. Main/Production unchanged.

**Resume instruction:** Preserve V9 as frozen FAIL. Preserve V10 as frozen/preflight-passed but not empirically executed. At a generic “continue”, documentation review only. If the user explicitly authorizes empirical V10 after this contract freeze, consume one unique V10 launch scope and execute exactly the two-arm synthetic-only study with no retries and no V2B.


## V10 exposure-isolation empirical execution complete — hypothesis NOT SUPPORTED — 2026-09-29

**Current resume authority. This section supersedes the earlier V10 preflight/authorization boundary.**

Explicit user authorization was consumed under launch identity:
- `v10-exposure-v1-20260929-01`

Frozen result:
- `docs/astra/V10_EXPOSURE_ISOLATION_RESULT_V1.json`
- `docs/astra/V10_EXPOSURE_ISOLATION_RESULT_V1.md`

Empirical run:
- run **36528001337**
- job **109275178270**
- head `b5c661b6f383571bf31383e2a1d884089c71311d`
- artifact **11015118480**
- artifact digest `sha256:34bed0c4f07458915196d5fb91cf3ca521ccb5ae8d01233ca0b2de6303e50fee`
- workflow conclusion **success**
- artifact retained through 2026-10-29
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

### Control reproduction passed exactly

The V10 control reproduced frozen V9 common comparator-test metrics exactly:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**
- attacked-note-label exposure **17,676**

This validates the controlled comparison.

### Exposure intervention identity

The intervention changed only positive-onset frame selection:
- positive-onset slots **16,000** in both arms
- control attacked-note labels **17,676**
- intervention attacked-note labels **19,702**
- 1,851 three-label positive frames
- 14,149 one-label positive frames
- non-positive selections identical
- per-step shuffle identical

Control batch-plan SHA-256:
`8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

Exposure-balanced batch-plan SHA-256:
`d439414e7b1dd92a4b505d14752da9bdeee203ee1dc09ff3a3e5c923e22cc837`

### Primary common comparator-test result

Control:
- precision **0.324427**
- recall **0.658915**
- F1 **0.434783**
- state admission **0.310078**
- onset admission **0.682171**
- joint admission **0.286822**
- negative FP/s **0**

Exposure-balanced:
- precision **0.348624**
- recall **0.589147**
- F1 **0.438040**
- state admission **0.271318**
- onset admission **0.666667**
- joint admission **0.255814**
- negative FP/s **0**

Deltas:
- precision **+0.024196**
- recall **-0.069767**
- F1 **+0.003258**
- state admission **-0.038760**
- onset admission **-0.015504**
- joint admission **-0.031008**

Frozen material-recovery gates:
- precision gain >= +0.20: **FAIL**
- F1 gain >= +0.15: **FAIL**
- recall decline <=0.08: PASS
- negative FP/s <=0.10: PASS

### Secondary V9-test result

Control:
- precision **0.486631**
- recall **0.705426**
- F1 **0.575949**

Exposure-balanced:
- precision **0.537994**
- recall **0.686047**
- F1 **0.603066**

Deltas:
- precision **+0.051363**
- recall **-0.019380**
- F1 **+0.027117**

These secondary gains are modest and do not rescue the preregistered primary gate.

### V10 decision

**The attacked-note-label exposure hypothesis is not supported.**

Exact exposure matching did not materially restore the V9 common-population precision/F1 collapse. The roughly 11% attacked-label exposure deficit observed in V9 was therefore not, by itself, a sufficient explanation.

Do not claim the true cause is known. Remaining package differences include longer temporal/context distribution, active/sustain-frame composition, attack-count allocation by family, onset/state coupling, and gap/sustain interactions.

Artifact evidence:
- `result.json` SHA-256 `7d94334506a55799b5d24ca36a490aa96c71047eef0d984e4b4ff8a283aee689`
- execution receipt `acffa9b2491e87ec2f550b6f3433c542ee11ba8c97b8e088a967fbb57253c63f`
- control checkpoint `d1b57eeeb7fbf980fade36e1f2dcd06a5099f32bb63af5acb0d356ee9a6d52d3`
- exposure-balanced checkpoint `f57b034f013ec0a245d83e38654afe2f8aa0d761fbf2fcd711cf5c4ff07b31b6`

### Current stop boundary

Preserve:
- V9 = frozen FAIL at synthetic sanity
- V10 = complete; exposure hypothesis NOT SUPPORTED

Do not:
- rerun V10;
- post-hoc tune exposure, sampler weights, losses, thresholds, or decoder;
- run V2B from V10;
- open V11 automatically;
- access V1.1/P1/P2/P3/A2;
- mutate main or Production.

**Resume instruction:** Stop model execution here. At a generic “continue”, perform documentation/review only. Any next causal study must be prospectively defined as a new project and explicitly authorized after its contract is frozen.


## Post-V10 causal/contract-integrity review complete — 2026-09-29

**Current resume authority. Documentation/review only; no new project opened.**

Completed:
- `docs/astra/POST_V10_CAUSAL_CONTRACT_INTEGRITY_REVIEW_V1.md`
- `docs/astra/POST_V10_CAUSAL_CONTRACT_INTEGRITY_REVIEW_V1.json`

V9 and V10 result files were amended only with interpretive qualifications; their numeric results remain unchanged.

### New source-level finding: V9 legato contract mismatch

The frozen V9 contract said the non-attacked legato continuation should remain a state-label event.

The executed V9 template builder instead filters S0 prototypes to `attack=true` and never re-adds the original non-attacked legato continuation.

Therefore:
- V9 timing measurements remain valid for the generated attack groups;
- V9/V10 empirical metrics remain valid observations of executed code;
- do **not** claim exact V9 conformance to the frozen family-state semantic contract;
- treat state-duration / continuation semantics as unresolved and scientifically relevant.

Historical S0 state durations:
- isolated ~1.03 s
- scales 0.27 s
- chords 0.48 s
- repeated ~0.31 s
- legato attacked 0.50 s + non-attacked continuation 0.74 s
- palmmute 0.16 s
- mixed-positive ~0.86 s

Implemented V9 uses one attacked-note sustain support [0.12, 0.48] s and omits the original non-attacked legato continuation.

### New causal qualification: V10 was not a pure label-mass intervention

V10 raised sampled attacked-note labels from 17,676 to 19,702 by changing positive-onset frame selection:
- 1,851 three-label frames
- 14,149 one-label frames

In this corpus, three-label positive frames are chord attacks. Therefore V10 also changed positive-onset chord/content mixture.

Narrow supported conclusion:
- the **specific chord-enriched label-count matching scheme** did not materially rescue V9.

Do not overstate this as proving that all pure positive-label gradient-mass explanations are false.

### Cross-population evidence

The same V9 control performs substantially better on the V9-domain test than the common old 2-second comparator test:

Common comparator test:
- precision 0.324427
- recall 0.658915
- F1 0.434783

V9 test:
- precision 0.486631
- recall 0.705426
- F1 0.575949

V9-domain minus common:
- precision +0.162204
- recall +0.046512
- F1 +0.141167

This is consistent with a synthetic-domain distribution shift. It does not identify the causal component.

### Preferred next scientific question if a new project is later authorized

Do **not** open V11 automatically.

Preferred next one-variable topic:

> With executed V9 attack timing/counts and all other training/evaluation settings fixed, does restoring historical family-specific state-duration and legato-continuation semantics materially recover common-population precision/F1?

A future contract must preserve the successful V9 attack-timing manifest, explicitly define overlap/next-attack behavior, restore legato continuation by construction, freeze one arm only, and require the same fixed common 2-second population as primary synthetic sanity.

Secondary possible future question:
- keep exact frozen V9 batch indices and change only preregistered positive-onset loss mass, avoiding chord-family resampling.

Neither project is opened or authorized by this review.

### Execution counts for this review

- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0
- workflow dispatches 0

V1.1/P1/P2/P3/A2 untouched. Main/Production unchanged.

**Resume instruction:** Stop here. At a generic “continue”, documentation/review only. If the user explicitly authorizes a new project, prospectively define/freeze its contract first; preferred topic is state-duration / legato-continuation semantics under the already successful V9 attack timing. No V2B and no automatic V11 execution.


## V11 state-semantics study prospectively frozen — preflight PASS — 2026-09-29

**Current resume authority. This section supersedes the prior post-V10 generic-review boundary.**

The user explicitly authorized opening the next project. That authorization was used only for prospective V11 definition, implementation, pure tests, and model-free preflight. It was not treated as empirical-training authorization because the exact V11 contract did not yet exist when authorization was given.

Completed:
- `docs/astra/V11_PROJECT_AUTHORIZATION_V1.json`
- `docs/astra/V11_STATE_SEMANTICS_CONTRACT_V1.md`
- `docs/astra/V11_STATE_SEMANTICS_CONTRACT_V1.json`
- `astra_backend/synthetic/v11_state_semantics_v1.py`
- `astra_backend/synthetic/test_v11_state_semantics_v1.py`
- `astra_backend/synthetic/v11_contract_validator_v1.py`
- `astra_backend/synthetic/test_v11_contract_validator_v1.py`
- `docs/astra/V11_PREFLIGHT_RESULT_V1.md`
- `docs/astra/V11_PREFLIGHT_RESULT_V1.json`

### Frozen V11 question

With successful V9 attack timing/counts fixed, does restoring historical family-specific state/audio durations and the omitted non-attacked legato continuation materially recover common 2-second comparator-test precision/F1?

### Intervention

Control:
- exact executed V9 4-second semantics.

Intervention:
- identical attacked string/fret/onset tuples;
- restore S0 family duration targets:
  - isolated 1.03 s
  - scales 0.27 s
  - chords 0.48 s
  - repeated 0.31 s
  - legato attacked 0.50 s
  - legato non-attacked continuation 0.74 s
  - palmmute 0.16 s
  - mixed-positive 0.86 s
- state ends truncate only at next same-string attack or 4.0 s;
- legato continuation is created when temporal room exists.

Attack timing is never moved, clipped, searched, or regenerated under a different policy.

### Model-free preflight passed

Run:
- **36534288763**
- job **109294696440**
- head `d736257bf2181b1c1a936ac74b825000c15b4588`
- artifact **11017093440**
- digest `sha256:974b0c3a9e86448b0c4b70ec37dada523dfe5a0eb208ac297ce6a0e8e0d56e81`
- conclusion **success**
- retained through 2026-10-29

Static audit:
- clips 294
- positive 273
- negative-only 21
- control/intervention attack groups **1,638 / 1,638**
- control/intervention attacked note labels **1,806 / 1,806**
- exact attacked signature SHA-256 `9129b31cec8c56a8275e269b25fd9ab686b15f91e8b5da711ef6490eddfffe97`
- restored non-attacked legato continuation events **84**
- attacked states truncated at same-string retrigger **789**
- zero waveform renders
- zero models
- zero optimizer steps
- zero inference
- zero V2B inference

Per-family retrigger truncations:
- isolated 168
- scales 37
- chords 126
- repeated 243
- legato 84
- palmmute 82
- mixed-positive 49

These truncations are expected consequences of combining historical duration targets with the denser frozen V9 attack schedule; they are the frozen intervention rule, not fallback corrections.

### Frozen empirical gate if later authorized

V11 control must exactly reproduce frozen V9 common-test precision/recall/F1 within 1e-12:
- precision 0.3244274809160305
- recall 0.6589147286821705
- F1 0.43478260869565216

Support requires all:
- common precision gain >= +0.15
- common F1 gain >= +0.10
- common recall decline <=0.05
- common joint-admission decline <=0.05
- common negative FP <=0.10/s
- frozen-V9 test F1 decline <=0.05
- exact 500 updates/model
- exact 2 models
- finite metrics
- no threshold search
- no scientific retry

There is no V2B stage in V11.

### Current authorization boundary

**Empirical V11 execution is not yet authorized.**

A fresh explicit authorization after this frozen contract/preflight is required before:
- waveform rendering/data generation for V11;
- training the two models;
- any optimizer step;
- any model inference.

Even after an empirical V11 result, V2B remains out of scope.

V1.1/P1/P2/P3/A2 untouched. Main/Production unchanged.

**Resume instruction:** Preserve V9 and V10 as frozen historical results with their post-review qualifications. Preserve V11 as contract-frozen/preflight-passed but not empirically executed. At a generic “continue”, documentation/review only. If the user explicitly authorizes empirical V11 after this point, consume one unique V11 launch scope and execute exactly the frozen two-arm synthetic-only study with no retries and no V2B.


## V11 state-semantics empirical execution complete — hypothesis NOT SUPPORTED — 2026-09-29

**Current resume authority. This section supersedes the earlier V11 preflight/authorization boundary.**

Explicit user authorization was consumed under launch identity:
- `v11-state-semantics-v1-20260929-01`

Frozen result:
- `docs/astra/V11_STATE_SEMANTICS_RESULT_V1.json`
- `docs/astra/V11_STATE_SEMANTICS_RESULT_V1.md`

Empirical run:
- run **36534741201**
- job **109296097761**
- head `0c3a24ab7d49a3b4525a2af372c2fbcf08fbccd6`
- artifact **11018510069**
- artifact digest `sha256:5cb15fcbb40b38bcee93e6bde1b4f4109204c9b979dcfb17910a25d2fe66bb91`
- workflow conclusion **success**
- artifact retained through 2026-10-29
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

### Control reproduction passed exactly

The V11 control exactly reproduced frozen V9 common comparator-test metrics:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

### Identity remained fixed

Both 4-second arms:
- attack groups **1,638**
- attacked note labels **1,806**
- attacked signature SHA-256 `9129b31cec8c56a8275e269b25fd9ab686b15f91e8b5da711ef6490eddfffe97`
- sampled attacked note labels **17,676**
- sampled attack frames **16,000**
- sampled frames **64,000**
- 500 updates/model

The intervention restored **84** non-attacked legato continuation events and applied the frozen historical-duration/retrigger rule with **789** attacked-state truncations at same-string retriggers.

### Primary common comparator-test result

Control:
- precision **0.324427**
- recall **0.658915**
- F1 **0.434783**
- state admission **0.310078**
- onset admission **0.682171**
- joint admission **0.286822**
- negative FP/s **0**

State-semantics restored:
- precision **0.353982**
- recall **0.620155**
- F1 **0.450704**
- state admission **0.263566**
- onset admission **0.689922**
- joint admission **0.255814**
- negative FP/s **0**

Deltas:
- precision **+0.029555**
- recall **-0.038760**
- F1 **+0.015922**
- state admission **-0.046512**
- onset admission **+0.007752**
- joint admission **-0.031008**

Frozen material-recovery gates:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <=0.05: PASS
- joint-admission decline <=0.05: PASS
- negative FP/s <=0.10: PASS

### Secondary frozen-V9 test result

Control:
- precision **0.486631**
- recall **0.705426**
- F1 **0.575949**

State-semantics restored:
- precision **0.438144**
- recall **0.658915**
- F1 **0.526316**

Deltas:
- precision **-0.048487**
- recall **-0.046512**
- F1 **-0.049634**

The frozen V9-test F1 decline limit was 0.05, so the observed 0.049634 decline passed narrowly.

### Sampler strata changed only as a downstream consequence of state targets

Positive-onset stratum:
- control/intervention **1,170 / 1,170**

Non-positive membership:
- active non-onset **10,444 -> 13,872**
- negative-structure inactive **10,868 -> 8,758**
- other inactive **13,848 -> 12,530**

The sampler algorithm was unchanged. Changed state duration changed which frames belonged to the non-positive strata.

### V11 decision

**The state-duration / legato-continuation hypothesis is not supported.**

Restoring historical family-duration targets plus the omitted legato continuation produced only small primary precision/F1 gains and did not meet the prospective material-recovery thresholds.

This weakens the hypothesis that the V9 failure is primarily explained by the state-duration/continuation discrepancy.

Do not claim the true cause is known.

Remaining unresolved package differences include:
- 4-second versus 2-second temporal/context distribution;
- V9 attack-count allocation by family;
- gap distribution / longer-range clip structure;
- interaction between changed occupancy and the fixed four-stratum sampler;
- other correlations introduced by the dense V9 package.

Artifact evidence:
- ZIP `5cb15fcbb40b38bcee93e6bde1b4f4109204c9b979dcfb17910a25d2fe66bb91`
- `result.json` `993e02b43a950072f7e31b4e8075c0a635410747f186f1e963595ca481046a73`
- execution receipt `eaeb365202f0b2b31e6b347a096763da596bff4caf51dcdc51b3c747b0087a55`
- control checkpoint `043d272e22bcb273b3bce6c31c4b561b7e47741cfb242f6b8d419c1c7dc18bb7`
- intervention checkpoint `3a998c7d19e8e3daecca0f624c9f3133824f9f72c30b20c6d1596d2964d91b69`

### Current stop boundary

Preserve:
- V9 = frozen FAIL at synthetic sanity, with post-review contract qualification
- V10 = complete; chord-enriched exposure matching did not materially rescue V9
- V11 = complete; restored state-duration / legato semantics did not materially rescue V9

Do not:
- rerun V11;
- post-hoc alter duration/truncation/sampler/threshold/loss settings and call it V11;
- run V2B;
- open V12 automatically;
- access V1.1/P1/P2/P3/A2;
- mutate main or Production.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. Any next causal study must be prospectively defined as a new project and explicitly authorized after its contract is frozen.


## Post-V11 causal review complete — positive-onset family mixture identified — 2026-09-29

**Current resume authority. Documentation/review only; no V12 opened.**

Completed:
- `docs/astra/POST_V11_CAUSAL_REVIEW_V1.md`
- `docs/astra/POST_V11_CAUSAL_REVIEW_V1.json`

### Main finding

The cleanest unresolved difference after V10/V11 is now the **family composition of the positive-onset stratum**.

Historical 2-second comparator train positive-onset frames:
- isolated 30
- scales 120
- chords 60
- repeated 120
- legato 30
- palmmute 150
- mixed-positive 15
- total **525**

Executed V9 train positive-onset frames:
- isolated 150
- scales 240
- chords 60
- repeated 240
- legato 120
- palmmute 300
- mixed-positive 60
- total **1,170**

Because the sampler uniformly takes exactly 32 positive-onset frames per update, these frame-count differences directly alter positive-onset training-family exposure.

Largest share changes from historical comparator to V9:
- isolated +7.106 percentage points
- chords -6.300 points
- legato +4.542 points
- palmmute -2.930 points
- scales -2.344 points
- repeated -2.344 points
- mixed-positive +2.271 points

Across 16,000 positive-onset slots, the historical comparator proportions correspond to this exact largest-remainder allocation:
- isolated **914**
- scales **3,657**
- chords **1,829**
- repeated **3,657**
- legato **914**
- palmmute **4,572**
- mixed-positive **457**
- total **16,000**

Current V9 uniform positive-onset sampling implies approximately:
- isolated 2,051.3
- scales 3,282.1
- chords 820.5
- repeated 3,282.1
- legato 1,641.0
- palmmute 4,102.6
- mixed-positive 820.5

### Preferred future project question

Do **not** open V12 automatically.

If the user explicitly authorizes opening a new project, the preferred prospective question is:

> With the exact executed V9 dataset arrays, attack timing, state semantics, model, loss, thresholds, optimizer, total positive-onset slots, and all non-positive batch selections fixed, does matching the historical comparator positive-onset family mixture materially recover common-population precision/F1?

Preferred operational design:
- no new rendering;
- no timing generation;
- no state-semantic regeneration;
- control reproduces exact V9 batch plan;
- intervention replaces only positive-onset selections;
- exactly 16,000 positive-onset slots in both arms;
- intervention uses the frozen historical family allocation above;
- active-non-onset, negative-structure-inactive, and other-inactive selections remain identical;
- same per-step shuffle;
- same initialization/model/loss/thresholds/optimizer/500 updates;
- primary eval = frozen 2-second comparator test;
- secondary eval = frozen V9 test;
- no V2B.

Important qualification:
- this is a **family-mixture** intervention, not a pure attacked-label-count intervention;
- chord frames carry three attacked labels, so restoring chord-frame share will also change attacked-note-label exposure;
- any future result must report both frame-family exposure and attacked-note-label exposure.

### What current evidence weakens

Simple single-factor explanations now weakened by direct diagnostics:
- common-unit timing mismatch;
- attacked-note-label exposure deficit alone;
- historical state-duration / legato-continuation omission alone.

These may still participate in interactions, but none materially rescued V9 in the executed studies.

### Current stop boundary

No V12 contract, runner, workflow, launch, or authorization file exists.

This review used:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0
- workflow dispatches 0

V1.1/P1/P2/P3/A2 untouched. Main/Production unchanged.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. If the user explicitly authorizes a new project, prospectively define/freeze the positive-onset family-mixture study first; empirical execution would still require a fresh authorization after that contract/preflight is visible.


## V12 family-mixture study prospectively frozen — preflight PASS — 2026-09-29

**Current resume authority. This section supersedes the prior post-V11 generic-review boundary.**

The user explicitly authorized opening the next project. That authorization was used only for prospective V12 definition, implementation, pure tests, and model-free preflight. It was not treated as empirical-training authorization because the exact V12 contract did not yet exist when authorization was given.

Completed:
- `docs/astra/V12_PROJECT_AUTHORIZATION_V1.json`
- `docs/astra/V12_FAMILY_MIXTURE_CONTRACT_V1.md`
- `docs/astra/V12_FAMILY_MIXTURE_CONTRACT_V1.json`
- `astra_backend/synthetic/v12_family_mixture_v1.py`
- `astra_backend/synthetic/test_v12_family_mixture_v1.py`
- `astra_backend/synthetic/v12_contract_validator_v1.py`
- `astra_backend/synthetic/test_v12_contract_validator_v1.py`
- `.github/workflows/astra-v12-family-mixture-preflight-v1.yml`
- `docs/astra/V12_PREFLIGHT_RESULT_V1.md`
- `docs/astra/V12_PREFLIGHT_RESULT_V1.json`

### Frozen V12 question

With the exact executed V9 dataset semantics and all non-positive batch selections fixed, does matching the historical 2-second comparator positive-onset family mixture materially recover common-population precision/F1?

### Frozen intervention

Control:
- exact executed-V9 training semantics and batch generation.

Intervention:
- same V9 dataset arrays;
- same active-non-onset, negative-structure-inactive, and other-inactive selections;
- same per-step 128-frame shuffle;
- replace only positive-onset selections.

Across exactly 16,000 positive-onset slots, the historical comparator family allocation is frozen to:
- isolated **914**
- scales **3,657**
- chords **1,829**
- repeated **3,657**
- legato **914**
- palmmute **4,572**
- mixed-positive **457**

Family schedule seed: **20281928**  
Family-pool selection seed: **20281929**

Because chord onset frames contain three attacked labels, the intervention will also change attacked-note-label exposure as a downstream consequence. Any empirical result must report that linked quantity and must not call V12 a pure label-count experiment.

### Dataset-regeneration constraint

The original V9 artifact did not retain the V9/comparator dataset arrays.

If empirical V12 is later authorized:
- deterministically regenerate exactly one common 2-second comparator dataset;
- deterministically regenerate exactly one executed-V9 4-second dataset;
- train both V12 arms on that same single V9 dataset;
- no intervention-specific rendering or timing/state generation;
- require exact V9 control reproduction before interpreting V12.

### Model-free preflight passed

Run:
- **36537123050**
- job **109303603997**
- head `250b08ddd7aca913ea0382122a259ca6e7a50f2a`
- artifact **11018394264**
- digest `sha256:b50fe403922d929fb2864b77868f83f57af23b20b240fbfe42f6e8aa8224959e`
- conclusion **success**
- retained through 2026-10-29

Preflight counts:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0

### Frozen empirical gate if later authorized

V12 control must exactly reproduce frozen V9 common-test metrics within 1e-12:
- precision 0.3244274809160305
- recall 0.6589147286821705
- F1 0.43478260869565216

Support requires all:
- common precision gain >= +0.15
- common F1 gain >= +0.10
- common recall decline <=0.05
- common negative FP <=0.10/s
- frozen-V9 test F1 decline <=0.05
- exact historical family-slot totals
- identical non-positive selections
- same per-step shuffle
- exact 500 updates/model
- exact 2 models
- finite metrics
- no threshold search
- no scientific retry

There is no V2B stage in V12.

### Current authorization boundary

**Empirical V12 execution is not yet authorized.**

A fresh explicit authorization after this frozen contract/preflight is required before:
- deterministic dataset regeneration;
- training the two V12 models;
- any optimizer step;
- any model inference.

V1.1/P1/P2/P3/A2 untouched. Main/Production unchanged.

**Resume instruction:** Preserve V9/V10/V11 as frozen historical results. Preserve V12 as contract-frozen/preflight-passed but not empirically executed. At a generic “continue”, documentation/review only. If the user explicitly authorizes empirical V12 after this point, consume one unique V12 launch scope and execute exactly the frozen two-arm synthetic-only family-mixture study with no retries and no V2B.


## V12 family-mixture empirical execution complete — hypothesis NOT SUPPORTED — 2026-09-29

**Current resume authority. This section supersedes the earlier V12 preflight/authorization boundary.**

Explicit user authorization was consumed under launch identity:
- `v12-family-mixture-v1-20260929-01`

Frozen result:
- `docs/astra/V12_FAMILY_MIXTURE_RESULT_V1.json`
- `docs/astra/V12_FAMILY_MIXTURE_RESULT_V1.md`

Empirical run:
- run **36537632082**
- job **109305235382**
- head `d08dd9dc0f8318e094070cc96e30bf8713d581e7`
- artifact **11018959307**
- artifact digest `sha256:1085e801d644b52a48e007f200334ccf4a5fe3c1ed753ae90533a1b58482fa6d`
- workflow conclusion **success**
- artifact retained through 2026-10-29
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

### Control reproduction passed exactly

The V12 control exactly reproduced frozen V9 common comparator-test metrics:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

Control batch plan:
`8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

### Family-mixture intervention identity

Control sampled positive-onset slots:
- isolated 2,013
- scales 3,314
- chords 838
- repeated 3,306
- legato 1,661
- palmmute 4,089
- mixed-positive 779

Historical-mixture intervention:
- isolated 914
- scales 3,657
- chords 1,829
- repeated 3,657
- legato 914
- palmmute 4,572
- mixed-positive 457

Intervention batch plan:
`fa9146d23f67084edb683c889d273a2fc55d2a036c7f858418c92d9329812e0c`

All non-positive selections and per-step shuffle remained identical.

### Linked attacked-note-label exposure

Because the historical mixture increases chord-frame share:
- control attacked labels **17,676**
- intervention attacked labels **19,658**
- increase **1,982** (**11.21%**)

This is a linked downstream consequence and must not be interpreted as a separately isolated factor.

### Primary common comparator-test result

Control:
- precision **0.324427**
- recall **0.658915**
- F1 **0.434783**
- state admission **0.310078**
- onset admission **0.682171**
- joint admission **0.286822**
- negative FP/s **0**

Historical family mixture:
- precision **0.342205**
- recall **0.697674**
- F1 **0.459184**
- state admission **0.333333**
- onset admission **0.751938**
- joint admission **0.333333**
- negative FP/s **0.166667**

Deltas:
- precision **+0.017778**
- recall **+0.038760**
- F1 **+0.024401**
- state admission **+0.023256**
- onset admission **+0.069767**
- joint admission **+0.046512**
- negative FP/s **+0.166667**

Frozen gates:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <=0.05: PASS
- negative FP/s <=0.10: **FAIL**

### Secondary frozen-V9 test

Control:
- precision **0.486631**
- recall **0.705426**
- F1 **0.575949**

Historical family mixture:
- precision **0.470284**
- recall **0.705426**
- F1 **0.564341**

Deltas:
- precision **-0.016347**
- recall **0**
- F1 **-0.011608**

The frozen secondary F1 decline ceiling passed.

### V12 decision

**The positive-onset family-mixture hypothesis is not supported.**

Matching the historical family mixture produced modest common-population recall/F1 gains but did not meet material precision/F1 recovery thresholds and exceeded the negative-only false-positive ceiling.

This further weakens a simple family-mixture explanation for V9.

Do not claim the true cause is known.

Remaining unresolved factors include:
- 4-second versus 2-second inactive/background context distribution;
- longer-range sequence/gap structure beyond marginal timing statistics;
- interactions among duration, family composition, negative/background context and the fixed four-stratum sampler;
- the 2-second versus 4-second corpus construction as a broader composite synthetic-domain shift.

Artifact evidence:
- ZIP `1085e801d644b52a48e007f200334ccf4a5fe3c1ed753ae90533a1b58482fa6d`
- `result.json` `4a5bf0f25b66ff8a842ae1fd8d434859b8769791fe109c51a049f5ff1bb76d91`
- execution receipt `71dca6e919295947173db6af2481a06821ce49c3bef669bd87a3a51bb7e9e94c`
- control checkpoint `da8d334c77790033b35fe6a3df3e70683b3a41b8f9e54b85f022b56f4de4f821`
- intervention checkpoint `4b4aca670d4477fcb4c7d0f0e6fe5724d3ec802043ab04dd85c0513adb5fef3b`

### Current stop boundary

Preserve:
- V9 = frozen FAIL at synthetic sanity
- V10 = frozen; exposure-matching did not materially rescue V9
- V11 = frozen; state-semantics restoration did not materially rescue V9
- V12 = complete; historical positive-onset family-mixture restoration did not materially rescue V9

Do not:
- rerun V12;
- post-hoc tune family proportions, sampler, threshold, loss or decoder and call it V12;
- run V2B;
- open V13 automatically;
- mutate main or Production.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. Any next causal study must be prospectively defined as a new project and explicitly authorized after its contract is frozen.


## Post-V12 causal review complete — active-non-onset family mixture identified — 2026-09-29

**Current resume authority. Documentation/review only; no V13 opened.**

Completed:
- `docs/astra/POST_V12_CAUSAL_REVIEW_V1.md`
- `docs/astra/POST_V12_CAUSAL_REVIEW_V1.json`

### Main finding

The four-stratum sampler always takes exactly 32 frames from each stratum per update, so the absolute stratum-size differences between the historical 2-second comparator and V9 do not change top-level sampler weights.

The important remaining difference is **family composition inside the non-positive strata**, especially active-non-onset.

Historical comparator stratum sizes:
- positive-onset **525**
- active-non-onset **8,220**
- negative-structure inactive **4,635**
- other inactive **4,890**

Executed V9:
- positive-onset **1,170**
- active-non-onset **10,444**
- negative-structure inactive **10,868**
- other inactive **13,848**

### Active-non-onset family redistribution

Historical active-non-onset:
- isolated 1,290 = 15.69%
- scales 1,320 = 16.06%
- chords 1,140 = 13.87%
- repeated 1,470 = 17.88%
- legato 1,560 = 18.98%
- palmmute 900 = 10.95%
- mixed 540 = 6.57%

Executed V9:
- isolated 1,215 = 11.63%
- scales 2,079 = 19.91%
- chords 788 = 7.55%
- repeated 2,140 = 20.49%
- legato 1,163 = 11.14%
- palmmute 2,487 = 23.81%
- mixed 572 = 5.48%

Largest shifts:
- palmmute **+12.86 percentage points**
- legato **-7.84**
- chords **-6.32**
- isolated **-4.06**
- scales **+3.85**
- repeated **+2.61**
- mixed **-1.09**

Across exactly 16,000 active-non-onset training slots, historical comparator proportions map to this deterministic largest-remainder allocation:
- isolated **2,511**
- scales **2,569**
- chords **2,219**
- repeated **2,861**
- legato **3,037**
- palmmute **1,752**
- mixed **1,051**
- total **16,000**

### Why this is the preferred next single-factor question

Unlike V10 and V12, an active-non-onset family-mixture intervention can preserve:
- exact positive-onset selections;
- exact attacked-note-label exposure;
- exact negative-structure-inactive selections;
- exact other-inactive selections;
- exact per-step shuffle;
- exact V9 dataset arrays;
- exact model/loss/threshold/optimizer settings.

This makes it a cleaner state-learning distribution test and directly targets one of the largest remaining within-stratum shifts.

### Secondary unresolved non-positive shift

Negative-structure inactive composition also changed substantially:

Historical:
- legato 22.01%
- palmmute 33.66%
- mixed 44.34%

V9:
- legato 35.95%
- palmmute 22.11%
- mixed 41.94%

If an active-non-onset study later fails, a separate negative-inactive family-mixture study would be the next cleaner one-variable diagnostic. Do not combine both in one project.

### Preferred future project question

Do **not** open V13 automatically.

If the user explicitly authorizes a new project, prospectively freeze:

> With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator active-non-onset family mixture materially recover common-population precision/F1 without increasing negative-only false positives?

No intervention-specific rendering is needed.

### Current stop boundary

No V13 contract, runner, workflow, launch, authorization, model training, or inference exists.

This review used:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0
- workflow dispatches 0

Main/Production unchanged.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. If the user explicitly authorizes a new project, freeze the active-non-onset family-mixture study first. Empirical execution must still wait for a fresh authorization after that contract/preflight is visible.


## V13 active-non-onset family-mixture study prospectively frozen — preflight PASS — 2026-09-29

**Current resume authority. This section supersedes the prior post-V12 generic-review boundary.**

The user explicitly authorized opening the next project. That authorization was used only for prospective V13 definition, implementation, pure tests, and model-free preflight. It was not treated as empirical-training authorization because the exact V13 contract did not yet exist when authorization was given.

Completed:
- `docs/astra/V13_PROJECT_AUTHORIZATION_V1.json`
- `docs/astra/V13_ACTIVE_NONONSET_MIXTURE_CONTRACT_V1.md`
- `docs/astra/V13_ACTIVE_NONONSET_MIXTURE_CONTRACT_V1.json`
- `astra_backend/synthetic/v13_active_nononset_mixture_v1.py`
- `astra_backend/synthetic/test_v13_active_nononset_mixture_v1.py`
- `astra_backend/synthetic/v13_contract_validator_v1.py`
- `astra_backend/synthetic/test_v13_contract_validator_v1.py`
- `.github/workflows/astra-v13-active-nononset-preflight-v1.yml`
- `docs/astra/V13_PREFLIGHT_RESULT_V1.md`
- `docs/astra/V13_PREFLIGHT_RESULT_V1.json`

### Frozen V13 question

With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical 2-second comparator active-non-onset family mixture materially recover common-population precision/F1 without increasing negative-only false positives?

### Frozen intervention

Control:
- exact executed-V9 dataset and four-stratum batch plan.

Intervention:
- same dataset arrays;
- same positive-onset selections;
- same negative-structure-inactive selections;
- same other-inactive selections;
- same per-step 128-frame permutation;
- replace only active-non-onset selections.

Across exactly **16,000 active-non-onset slots**, the historical comparator family allocation is frozen to:
- isolated **2,511**
- scales **2,569**
- chords **2,219**
- repeated **2,861**
- legato **3,037**
- palmmute **1,752**
- mixed-positive **1,051**

Family schedule seed: **20283928**  
Family-pool selection seed: **20283929**

Because positive-onset selections are identical across arms, sampled attacked-note-label exposure must also remain identical.

### Model-free preflight passed

Run:
- **36539873506**
- job **109312472318**
- head `98eaaeb87737582f59fde5755da88cb647af8c27`
- artifact **11019923191**
- digest `sha256:7d46e108c9fcfba1dbc3e1cfd767f62ffe8e3888cdfe3c98ef4da46044d6b96a`
- conclusion **success**
- retained through 2026-10-29

Preflight counts:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0

### Frozen empirical gate if later authorized

V13 control must exactly reproduce frozen V9 common-test metrics within 1e-12:
- precision 0.3244274809160305
- recall 0.6589147286821705
- F1 0.43478260869565216

Support requires all:
- common precision gain >= +0.15
- common F1 gain >= +0.10
- common recall decline <=0.05
- common negative FP <=0.10/s
- frozen-V9 test F1 decline <=0.05
- exact historical active-non-onset family-slot totals
- identical positive-onset selections
- identical negative-structure-inactive selections
- identical other-inactive selections
- identical per-step shuffle
- identical sampled attacked-note-label exposure
- exact 500 updates/model
- exact 2 models
- finite metrics
- no threshold search
- no scientific retry

There is no V2B stage in V13.

### Current authorization boundary

**Empirical V13 execution is not yet authorized.**

A fresh explicit authorization after this frozen contract/preflight is required before:
- deterministic dataset regeneration;
- training the two V13 models;
- any optimizer step;
- any model inference.

Main/Production unchanged.

**Resume instruction:** Preserve V9-V12 as frozen historical results. Preserve V13 as contract-frozen/preflight-passed but not empirically executed. At a generic “continue”, documentation/review only. If the user explicitly authorizes empirical V13 after this point, consume one unique V13 launch scope and execute exactly the frozen two-arm synthetic-only active-non-onset family-mixture study with no retries and no V2B.


## V13 active-non-onset family-mixture empirical execution complete — hypothesis NOT SUPPORTED — 2026-09-29

**Current resume authority. This section supersedes the earlier V13 preflight/authorization boundary.**

Explicit user authorization was consumed under launch identity:
- `v13-active-nononset-v1-20260929-01`

Frozen result:
- `docs/astra/V13_ACTIVE_NONONSET_MIXTURE_RESULT_V1.json`
- `docs/astra/V13_ACTIVE_NONONSET_MIXTURE_RESULT_V1.md`

Empirical run:
- run **36540511146**
- job **109314523890**
- head `fe293c9446e5ed4b5afc632bbf1fdabc0136df3a`
- artifact **11020985149**
- artifact digest `sha256:1610b51364e8589f812b1084a2d090ccf34be062cdfbe2ad6edbda26e8435109`
- conclusion **success**
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

### Control reproduction passed exactly

Frozen V9 common comparator-test metrics were reproduced exactly:
- precision **0.3244274809160305**
- recall **0.6589147286821705**
- F1 **0.43478260869565216**

### V13 intervention identity

Only active-non-onset family selection changed.

Control sampled active-non-onset slots:
- isolated 1,907
- scales 3,193
- chords 1,207
- repeated 3,304
- legato 1,798
- palmmute 3,711
- mixed-positive 880

Historical-mixture intervention:
- isolated 2,511
- scales 2,569
- chords 2,219
- repeated 2,861
- legato 3,037
- palmmute 1,752
- mixed-positive 1,051

Control batch plan:
`8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

Intervention batch plan:
`1627721cd6f541edbf37bd58e4e5f92264d10b39f264855b195dbb6089539de4`

Preserved exactly across arms:
- positive-onset selections;
- negative-structure-inactive selections;
- other-inactive selections;
- per-step shuffle;
- sampled attacked-note-label exposure **17,676 / 17,676**;
- sampled attack frames **16,000 / 16,000**;
- sampled total frames **64,000 / 64,000**.

### Primary common comparator-test result

Control:
- precision **0.324427**
- recall **0.658915**
- F1 **0.434783**
- state admission **0.310078**
- onset admission **0.682171**
- joint admission **0.286822**
- negative FP/s **0**

Historical active-non-onset mixture:
- precision **0.336066**
- recall **0.635659**
- F1 **0.439678**
- state admission **0.263566**
- onset admission **0.674419**
- joint admission **0.240310**
- negative FP/s **0**

Deltas:
- precision **+0.011638**
- recall **-0.023256**
- F1 **+0.004896**
- state admission **-0.046512**
- onset admission **-0.007752**
- joint admission **-0.046512**
- negative FP/s **0**

Frozen gates:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <=0.05: PASS
- negative FP/s <=0.10: PASS

### Secondary frozen-V9 test

Control:
- precision **0.486631**
- recall **0.705426**
- F1 **0.575949**

Historical active-non-onset mixture:
- precision **0.492021**
- recall **0.717054**
- F1 **0.583596**

Deltas:
- precision **+0.005390**
- recall **+0.011628**
- F1 **+0.007647**

### V13 decision

**The active-non-onset family-mixture hypothesis is not supported.**

Matching only this historical within-stratum family mixture produced a negligible common-test precision/F1 improvement and did not meet material-recovery thresholds.

This is a comparatively clean negative result because the other three sampler strata and attacked-note-label exposure were held fixed.

Do not claim the true cause is known.

Remaining unresolved factors include:
- negative-structure-inactive family composition;
- 2-second versus 4-second inactive/background context diversity;
- longer-range sequence/gap structure beyond marginal timing statistics;
- interactions among multiple strata;
- the broader 2-second-to-4-second synthetic-domain construction shift.

Artifact evidence:
- ZIP `1610b51364e8589f812b1084a2d090ccf34be062cdfbe2ad6edbda26e8435109`
- result `f2fa222cacbca5d796767938d093649004dac24425bb826bb4a5e4eb798e2ab1`
- receipt `f65cfbbe10d90053121468d34fa78734bc93efe1cce4b3469a3cae166ad79fae`
- control model `bdba8a2dab99fc61ea057a9511cc2ef7677eb88db889f00a517d546c446fd3d1`
- intervention model `889bab7c5eb1386ab1dd33c20ea99ed3914fecd2beae52e63693aaeece5b0448`

### Current stop boundary

Preserve:
- V9 = frozen FAIL at synthetic sanity
- V10 = frozen negative diagnostic
- V11 = frozen negative diagnostic
- V12 = frozen negative diagnostic
- V13 = complete; active-non-onset family-mixture hypothesis NOT SUPPORTED

Do not:
- rerun V13;
- post-hoc tune the active-non-onset mixture and call it V13;
- run V2B;
- open V14 automatically;
- mutate main or Production.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. Any next causal study must be prospectively defined as a new project and explicitly authorized after its contract is frozen.


## Post-V13 causal review complete — negative-structure-inactive family mixture identified — 2026-09-29

**Current resume authority. Documentation/review only; no V14 opened.**

Completed:
- `docs/astra/POST_V13_CAUSAL_REVIEW_V1.md`
- `docs/astra/POST_V13_CAUSAL_REVIEW_V1.json`

### Main finding

V13 held the other three sampler strata and attacked-note-label exposure fixed, yet common F1 improved only **+0.004896**.

The strongest remaining single within-stratum family-composition difference is now **negative-structure-inactive**.

Historical comparator negative-structure-inactive training frames:
- legato **1,020 = 22.01%**
- palmmute **1,560 = 33.66%**
- mixed **2,055 = 44.34%**
- total **4,635**

Executed V9:
- legato **3,907 = 35.95%**
- palmmute **2,403 = 22.11%**
- mixed **4,558 = 41.94%**
- total **10,868**

Share shifts:
- legato **+13.94 percentage points**
- palmmute **-11.55**
- mixed **-2.40**

Across exactly 16,000 negative-structure-inactive training slots, the historical comparator proportions map to:
- legato **3,521**
- palmmute **5,385**
- mixed **7,094**
- total **16,000**

### Preferred future project question

Do **not** open V14 automatically.

If the user explicitly authorizes a new project, prospectively freeze:

> With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator negative-structure-inactive family mixture materially recover common-population precision/F1 while preserving the negative-only false-positive ceiling?

Preferred design:
- no intervention-specific rendering;
- same regenerated V9 arrays for both arms;
- control = exact V9 batch plan;
- intervention changes only negative-structure-inactive selection;
- positive-onset selection identical;
- active-non-onset selection identical;
- other-inactive selection identical;
- per-step shuffle identical;
- attacked-note-label exposure identical;
- exactly 16,000 negative-inactive slots;
- target 3,521 / 5,385 / 7,094 for legato / palmmute / mixed;
- same model/loss/threshold/optimizer/500 updates;
- primary eval common 2-second comparator;
- secondary eval frozen V9;
- no V2B.

### Broader decision point after that study

If a future negative-structure-inactive isolation also fails, the evidence would increasingly favor a **composite corpus/context domain shift** rather than one isolated sampler statistic.

At that point, stop serial single-factor micro-studies and consider a prospectively frozen matched-context or whole-package 2-second-context design instead.

### Current stop boundary

No V14 contract, authorization, runner, workflow, launch, rendering, model training, inference, or V2B exists.

This review used:
- waveform renders 0
- models trained 0
- optimizer steps 0
- model inference 0
- V2B inference 0
- workflow dispatches 0

Main/Production unchanged.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. If the user explicitly authorizes a new project, freeze the negative-structure-inactive family-mixture study first. Empirical execution must still wait for fresh authorization after that contract/preflight is visible.


## Explicit next steps — saved 2026-09-29

These are the exact next steps to follow from the current frozen state.

1. **Do not execute any model work at a generic “continue”.**
   - No rendering.
   - No dataset regeneration.
   - No optimizer steps.
   - No inference.
   - No V2B.
   - No threshold/sampler/loss retuning.
   - No mutation of main or Production.

2. **Preserve all frozen historical results exactly as they are.**
   - V9 = frozen FAIL at synthetic sanity.
   - V10 = frozen negative diagnostic for attacked-label exposure matching.
   - V11 = frozen negative diagnostic for historical state-duration / legato-continuation restoration.
   - V12 = frozen negative diagnostic for positive-onset family-mixture restoration.
   - V13 = frozen negative diagnostic for active-non-onset family-mixture restoration.

3. **If the user explicitly authorizes a new project, open V14 prospectively.**
   Preferred V14 question:

   > With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator negative-structure-inactive family mixture materially recover common-population precision/F1 while preserving the negative-only false-positive ceiling?

4. **Freeze V14 before any empirical execution.**
   The V14 contract should specify one intervention only:
   - control = exact executed-V9 batch plan;
   - intervention changes only `negativeStructureInactive` selections;
   - exactly 16,000 negative-structure-inactive slots in each arm;
   - historical target allocation:
     - legato **3,521**
     - palmmute **5,385**
     - mixed **7,094**
   - positive-onset selections identical across arms;
   - active-non-onset selections identical across arms;
   - other-inactive selections identical across arms;
   - same per-step 128-frame permutation;
   - sampled attacked-note-label exposure identical;
   - same V9 dataset arrays;
   - same initialization/model/loss/thresholds/optimizer;
   - exactly 500 updates/model, exactly 2 models;
   - no threshold search;
   - no scientific retry;
   - no V2B or real-audio inference.

5. **Run only a model-free preflight after V14 is prospectively frozen.**
   Preflight must verify:
   - contract/source pins;
   - exact 16,000-slot arithmetic;
   - exact 3,521 / 5,385 / 7,094 family allocation;
   - zero waveform renders;
   - zero optimizer steps;
   - zero model inference;
   - zero V2B inference.

6. **Require a fresh explicit user authorization after the V14 contract and preflight are visible before empirical execution.**
   Do not treat the authorization that opens V14 as empirical-training authorization.

7. **If later empirically authorized, V14 control must reproduce frozen V9 exactly before interpreting the intervention.**
   Required common comparator-test reproduction within 1e-12:
   - precision **0.3244274809160305**
   - recall **0.6589147286821705**
   - F1 **0.43478260869565216**

8. **Use the same material-recovery gate unless the future contract prospectively freezes a different justified gate before execution.**
   Current recommended gate:
   - common precision gain >= **+0.15**
   - common F1 gain >= **+0.10**
   - common recall decline <= **0.05**
   - common negative-only FP <= **0.10/s**
   - frozen-V9 test F1 decline <= **0.05**
   - exact 500 updates/model
   - exact 2 models
   - finite metrics
   - identical attacked-note-label exposure
   - no threshold search/retry.

9. **If V14 also fails, stop serial one-factor sampler micro-studies.**
   Do not automatically open V15.

   The preferred next scientific direction after a V14 failure should become a prospectively frozen **composite context/domain-shift study**, such as:
   - a matched 2-second-context control using the successful V9 attack timing principles; or
   - a whole-package matched-context factorial design.

   The purpose would be to test whether the remaining failure is driven by the broader 2-second-to-4-second synthetic corpus/context construction rather than one isolated sampler statistic.

10. **Keep causal wording narrow.**
    Current evidence weakens simple explanations based on:
    - marginal attack timing mismatch;
    - attacked-note-label exposure alone;
    - state-duration / legato-continuation semantics alone;
    - positive-onset family mixture alone;
    - active-non-onset family mixture alone.

    Do not claim the true cause is known.

**Immediate resume rule:** At the next generic “continue”, documentation/review only. At the next explicit authorization to open a project, prospectively define/freeze V14 negative-structure-inactive family-mixture isolation, run model-free preflight only, then stop for fresh empirical authorization.


## Supervisory course correction — stop serial micro-studies; recovery-first context bridge planning — 2026-09-29

**THIS IS THE CURRENT RESUME AUTHORITY. It supersedes the prior instruction proposing V14 as another negative-structure-inactive family-mixture isolation. No V14 is open and no empirical execution is authorized by this review.**

### Why the current path is not progressing

The recent work is careful, reproducible, and honest, but the scientific search strategy has become too local relative to the size of the failure.

Frozen common-comparator reference:
- successful 2-second comparator F1: **0.7381974249**
- executed V9 F1: **0.4347826087**
- V9 gap: **-0.3034148162 F1**
- comparator precision: **0.8269230769**
- V9 precision: **0.3244274809**
- precision gap: **-0.5024955960**

Subsequent bounded interventions on that same common test produced:
- V10 attacked-label/chord-enriched exposure scheme: F1 **+0.0032577371**
- V11 state-semantics restoration package: F1 **+0.0159216167**
- V12 positive-onset historical family mixture: F1 **+0.0244010648**, while violating the frozen negative-only FP ceiling
- V13 active-non-onset historical family mixture: F1 **+0.0048956755**

Those results do not prove that the remaining negative-structure-inactive mixture has zero effect. They do show that serially restoring one marginal sampler statistic at a time has so far recovered only a small fraction of the original V9 deficit. The project should **not** keep spending project versions on increasingly narrow marginal-mixture hypotheses without first testing the larger domain/context construction difference.

### Important correction to the previous V14 recommendation

**Do not open the previously proposed negative-structure-inactive-mixture V14 by default.**

That study may remain a documented optional diagnostic, but it is no longer the preferred next project.

Reason:
- V10-V13 already tested several plausible isolated training-distribution explanations.
- None materially restored the common-test failure.
- The original V9 intervention simultaneously changed a much larger corpus/context package: 2-second versus 4-second construction, amount of rendered temporal context, inactive/background context, sequence/gap structure, family/context interactions, and resulting frame distribution.
- Marginal family-mixture matching does not reconstruct those joint temporal/context distributions.
- A further one-factor mixture test risks producing another precise negative result without materially increasing the probability of a usable system.

### New objective: recovery-first, then causal decomposition

The next phase should answer a more useful question:

> Can the strong V9 attack-timing idea survive when it is placed back into a context/corpus construction that is much closer to the successful 2-second comparator?

This is a **recovery/bridge question**, not a claim that one factor is the true cause.

If recovery occurs, later studies can decompose which context factor mattered. If recovery does not occur, the project has learned much more than another marginal-mixture test would provide.

### Exact next authorized task at a generic “continue” — MODEL-FREE RECOVERY STRATEGY REVIEW

At the next generic “continue”, perform documentation/source analysis only. Do **not** train or infer.

Create:
- docs/astra/POST_V13_RECOVERY_STRATEGY_REVIEW_V1.md
- docs/astra/POST_V13_RECOVERY_STRATEGY_REVIEW_V1.json

The review must do all of the following:

1. **Build one compact result table for V9-V13.**
   Include, for the common comparator test:
   - absolute precision / recall / F1;
   - delta from reproduced V9 control;
   - delta from the successful 2-second comparator where available;
   - state/onset/joint admission;
   - negative-only FP/s;
   - exactly what variable/package each version changed.

2. **Quantify progress against the actual recovery gap.**
   Use the frozen comparator and V9 numbers above.
   For each V10-V13 intervention, report the fraction of the original **0.3034148162 F1 deficit** recovered.
   Do not describe a +0.02 movement as material recovery merely because it is positive.

3. **Inventory the remaining 2-second vs 4-second construction differences from committed source/contracts.**
   At minimum inspect:
   - clip/window duration and boundary handling;
   - renderer context before/after attacks;
   - inactive/background duration and placement;
   - note/state continuation across window boundaries;
   - event density and long-gap structure;
   - family co-occurrence and cross-family sequence structure;
   - sampling pools and eligibility rules;
   - number of unique rendered contexts/examples;
   - normalization/feature framing differences, if any;
   - any source-code divergence between the successful comparator builder and executed V9 builder.

   Distinguish:
   - confirmed difference;
   - likely linked consequence;
   - unknown/unmeasured.

4. **Do not rely only on marginal percentages.**
   Where existing committed arrays/receipts permit model-free analysis, compare joint/context descriptors such as:
   - run-length distributions;
   - attack-to-window-edge distance;
   - silence/inactive run lengths;
   - number of state transitions per window;
   - note overlap/polyphony;
   - family × state-stratum combinations;
   - attack density conditional on family;
   - repeated-note/retrigger spacing;
   - context immediately preceding/following positive onsets.

   No new audio rendering, model loading, optimizer work, or inference is allowed for this review.

5. **Select exactly ONE preferred next empirical project design.**
   The preferred design should be a **matched-context bridge**, not another isolated marginal sampler restoration.

   Default design direction unless source inspection disproves feasibility:
   - retain the successful/frozen V9 attack-timing schedule or its exact deterministic identity;
   - render/train in a **2-second context construction matched as closely as practical to the successful comparator**;
   - keep model architecture, loss, thresholds, optimizer, and evaluation fixed;
   - use the same common 2-second comparator test as primary evaluation;
   - use a separately frozen secondary test only if already available and uncontaminated;
   - no V2B and no real-audio inference at this stage.

   The contract must explicitly list every difference between bridge and V9. Do not call this a single-factor causal isolation if multiple context properties move together.

6. **Define a success gate that measures meaningful recovery, not tiny movement.**
   Before any execution, propose a prospective gate tied to the original comparator gap. A preferred form is:
   - recover at least **50% of the V9 common-test F1 deficit**, which corresponds to F1 >= approximately **0.58649** on the common comparator test;
   - simultaneously obtain a substantial precision recovery;
   - preserve recall within a prospectively frozen tolerance;
   - negative-only FP/s <= **0.10**;
   - exact bounded training budget and no threshold search/retry.

   The final exact numbers must be justified and frozen in the future project contract before execution. Do not tune the gate after observing results.

7. **Add a stop rule.**
   If the matched-context bridge fails to achieve material recovery, stop synthetic micro-optimization and write a decision brief choosing among:
   - redesigning the synthetic generator at a larger level;
   - obtaining a new explicitly authorized independent real-development set;
   - pausing this model line.

   Do not automatically create V15/V16 or continue serial mixture restoration.

### Preferred future V14, only after the recovery review

If the recovery review supports feasibility and the user explicitly authorizes a new project, V14 should be a **2-second matched-context bridge study** (name may be refined in the contract), not the previously proposed negative-structure-inactive-mixture study.

Before any optimizer step:
- freeze the exact V14 question;
- freeze source blobs and dataset/render identities;
- freeze exact differences vs V9 and vs the successful comparator;
- freeze model/loss/threshold/optimizer settings;
- freeze evaluation datasets;
- freeze meaningful recovery gates;
- set hard model/update/time/storage ceilings;
- run a model-free preflight;
- stop and require fresh explicit empirical authorization after the preflight is visible.

### What GPT-5.6 should stop doing

Do not:
- open V14 as negative-structure-inactive family mixture merely because it was the next item in the old handoff;
- keep creating one project per marginal family proportion;
- treat successful workflow execution as scientific progress;
- optimize toward tiny positive deltas while the principal F1/precision gap remains large;
- silently alter multiple properties while describing the experiment as causal isolation;
- retune thresholds/losses/steps to manufacture a pass;
- touch P1/P2/P3, V2B, main, or Production;
- discard frozen negative results.

### What counts as progress now

Progress is:
1. explaining the large V9 regression at the correct scale;
2. testing whether a comparator-like context restores a **material** portion of that regression;
3. preserving deterministic/reproducible controls;
4. stopping quickly if the broader bridge also fails.

The immediate priority is no longer “find the next marginal mismatch.” It is “test the smallest coherent context package capable of plausibly explaining a ~0.30 F1 / ~0.50 precision regression.”

### Immediate resume rule

At the next generic **“continue”**:
1. perform the model-free recovery strategy review above;
2. save its MD + JSON;
3. update both handoffs with one preferred V14 bridge design;
4. do **not** execute training/inference;
5. stop at the explicit project-authorization boundary.

No V14 empirical work is authorized by this supervisory review.


## Post-V13 recovery strategy review complete — recovery-first bridge selected — 2026-09-29

**THIS IS THE CURRENT RESUME AUTHORITY. It supersedes the prior negative-structure-inactive V14 recommendation and the earlier instruction to perform the recovery strategy review.**

Completed:
- `docs/astra/POST_V13_RECOVERY_STRATEGY_REVIEW_V1.md`
- `docs/astra/POST_V13_RECOVERY_STRATEGY_REVIEW_V1.json`

### Decision

Do **not** open V14 as another marginal sampler-mixture study by default.

The frozen common-test gap is:
- successful 2-second comparator F1 **0.7381974249**
- V9 F1 **0.4347826087**
- deficit **0.3034148162**
- comparator precision **0.8269230769**
- V9 precision **0.3244274809**
- precision deficit **0.5024955960**

Recovery achieved by recent separate interventions:
- V10 F1 +0.0032577 = **1.07%** of original F1 deficit
- V11 F1 +0.0159216 = **5.25%**
- V12 F1 +0.0244011 = **8.04%**, but negative FP/s **0.166667** violated the frozen ceiling
- V13 F1 +0.0048957 = **1.61%**

These are useful negative diagnostics, but they do not constitute material recovery.

### Important source-level context finding

The renderer places the synthetic negative-structure burst at about **1.70 s** in both 2-second and 4-second clips.

Therefore:
- 2-second comparator leaves about **0.30 s** after the burst;
- 4-second V9 leaves about **2.30 s** after the burst.

This creates a large temporal-context difference inside negative-structure clips that sampler family-proportion matching does not remove.

Other confirmed V9-vs-comparator package differences include:
- 4.0 s vs 2.0 s clip duration;
- different per-family attack counts;
- V9 first attacks at 0.050–0.120 s vs comparator roughly 0.22–0.36 s;
- deterministic S/M/L gap construction replacing fixed comparator motifs;
- common 0.12–0.48 s V9 sustain support replacing historical family-specific durations;
- executed V9 omission of the historical non-attacked legato continuation;
- different boundary proximity and inactive run geometry;
- materially different training-frame pools.

Within the V9 paired run, R3 renderer, frontend, S6 model, thresholds and common primary evaluation were controlled. The failure is therefore consistent with a larger synthetic context/domain shift rather than merely a different evaluation target or threshold.

### Preferred future V14

No V14 is currently open.

If the user explicitly authorizes opening a new project, prepare exactly one prospective project:

**V14 — 2-second matched-context bridge**

Question:

> Can the successful V9 attack-timing principles retain material benefit when returned to a 2-second comparator-like temporal/context construction?

This is a **package recovery experiment**, not a single-factor causal isolation.

Preferred fixed elements:
- 294 historical family/base/variant identities and split;
- 2.0-second clips;
- R3 renderer;
- frozen RMS normalization + CQT;
- S6 nonlinear five-frame model;
- existing loss/weights;
- thresholds 0.50 / 0.50;
- Adam 0.003;
- four 32-frame sampler strata;
- 500 updates/model;
- exact frozen common 2-second comparator test as primary evaluation;
- no V2B;
- no real audio;
- no threshold/loss/seed search;
- no automatic scientific retry.

Bridge principle:
- retain acoustic-attack-group accounting and deterministic V9-style timing construction;
- use a prospectively frozen feasible 2-second timing/count schedule;
- avoid the 4-second post-1.70-s inactive tail by construction;
- preserve comparator-like family/state semantics unless a difference is explicitly frozen;
- search **zero** alternative empirical schedules;
- document every difference from control.

The exact 2-second per-family attack counts and gap supports are not frozen yet. They may be derived once, model-free, during future contract preparation and must then be frozen before rendering or optimizer work.

### Prospective material-recovery target

Original F1 deficit = **0.3034148162**.

50% recovery corresponds to:

**common-test F1 >= 0.5864900168**

Future V14 contract preparation should also freeze:
- a substantial precision-recovery requirement tied to the original 0.502496 precision deficit;
- recall tolerance;
- negative FP/s <= 0.10;
- exact compute/storage ceilings;
- finite metrics;
- no tuning/retry.

Do not lower these after seeing empirical results.

### Stop rule

If a future authorized V14 matched-context bridge fails material recovery:
- do not auto-open V15/V16;
- stop serial synthetic micro-optimization;
- write one decision brief choosing among larger generator redesign, separately authorized independent real-development evidence, or pausing this model line.

### Current authorization boundary

The recovery review is complete, but **V14 is not opened**.

At a generic “continue”:
- documentation/review only;
- do not generate a V14 timing candidate;
- do not render;
- do not train;
- do not infer;
- do not dispatch an empirical workflow.

A fresh explicit user authorization is required to **open V14 and prepare/freeze its prospective contract and model-free preflight**.

After that contract/preflight is visible, require another fresh explicit authorization before empirical rendering/training.

P1/P2 remain closed. P3 remains sealed. Main/Production unchanged.

**Resume instruction:** Preserve V9-V13 as frozen evidence. Do not revert to the negative-structure-inactive-mixture V14. Await explicit authorization to open the 2-second matched-context bridge project.


## V14 2-second matched-context bridge opened — contract frozen — model-free preflight complete — 2026-09-29

**THIS IS THE CURRENT RESUME AUTHORITY.**

The user's explicit authorization was consumed for **project preparation only**:
- open V14;
- freeze the 2-second matched-context bridge contract;
- derive one deterministic feasible timing schedule;
- implement a pure model-free validator and focused tests;
- complete model-free preflight.

It was **not** consumed as empirical rendering/training authorization.

Created:
- `docs/astra/V14_PROJECT_AUTHORIZATION_V1.json`
- `docs/astra/V14_MATCHED_CONTEXT_BRIDGE_CONTRACT_V1.md`
- `docs/astra/V14_MATCHED_CONTEXT_BRIDGE_CONTRACT_V1.json`
- `astra_backend/synthetic/v14_contract_validator_v1.py`
- `astra_backend/synthetic/test_v14_contract_validator_v1.py`
- `docs/astra/V14_PREFLIGHT_RESULT_V1.md`
- `docs/astra/V14_PREFLIGHT_RESULT_V1.json`

### Frozen V14 question

> Can the successful V9 acoustic-attack timing principles retain material benefit when returned to a 2-second comparator-like temporal/context construction?

V14 is a **package recovery experiment**, not a single-factor causal isolation.

### Frozen bridge timing package

Duration:
- **2.0 s** per clip.

Positive attack groups per clip:
- isolated 1
- scales 4
- chords 2
- repeated 5
- legato 1
- palmmute 6
- mixed-positive 1

Aggregate:
- positive clips **273**
- positive seconds **546**
- attack groups **819**
- density **1.500000/s**
- gaps **546**

Gap classes:
- S **252**
- M **225**
- L **69**

Supports:
- S **0.100–0.130 s**
- M **0.251–0.260 s**
- L **0.850–0.950 s**

Root seed:
- **20260929**

The exact assignment is SHA-256 deterministic by family/base/variant identity. There is no candidate sweep, retry, parameter search, or best-of-N selection.

### Model-free schedule result

Independent preflight recomputation:
- IOI p10 **0.1061617322 s**
- IOI p50 **0.2520127045 s**
- IOI p90 **0.8704418108 s**
- repeat250 **0.4615384615**
- longGap700 **0.1263736264**
- latest attack **1.7920413320 s**
- minimum post-last-attack margin **0.2079586680 s**
- corrected timing-distance V1 **0.0430642112**

All schedule arithmetic passed.

### Preflight correction caught before empirical work

The first frozen draft contained a tiny arithmetic typo in the precision recovery gate.

Correct exact 50%-recovery gates are:
- common F1 >= **0.586490016794178**
- common precision >= **0.5756752789195536**

The contract and validator were corrected before the preflight receipt was frozen.

### Validator/test caveat

Committed:
- `astra_backend/synthetic/v14_contract_validator_v1.py`
- `astra_backend/synthetic/test_v14_contract_validator_v1.py`

The current execution container could not resolve `raw.githubusercontent.com`, and the connected GitHub tooling available in this session did not expose workflow dispatch. Therefore do **not** claim the committed unittest suite was executed remotely.

The exact frozen schedule and gate arithmetic were independently recomputed model-free and passed.

**Future empirical execution must fail closed:** before any render or optimizer step, execute the committed validator/tests against the branch contract. If any test fails, stop with zero renders and zero optimizer steps.

### Frozen empirical settings if later authorized

Both arms:
- same-runtime 2-second datasets;
- control = historical comparator package;
- bridge = frozen V14 timing/context package;
- R3 renderer;
- frozen RMS normalization + CQT;
- S6 nonlinear five-frame model;
- active-state weight 9.0;
- onset positive weight 8.0;
- onset loss multiplier 4.0;
- Adam 0.003;
- four sampler strata × 32 frames/update;
- state/onset thresholds 0.50 / 0.50;
- exactly 500 updates/model;
- exactly 2 models;
- no threshold search;
- no scientific retry;
- primary evaluation = exact frozen common 2-second comparator test;
- no V2B;
- no real-audio inference.

### Current authorization boundary

**Empirical V14 execution is NOT authorized.**

Do not:
- render waveforms;
- generate empirical V14 datasets;
- take optimizer steps;
- run model inference;
- run V2B;
- access P1/P2/P3;
- weaken recovery gates;
- search alternate bridge schedules;
- mutate main or Production.

A fresh explicit user authorization is required before empirical V14 execution.

After that authorization:
1. first run the committed V14 validator/tests;
2. if and only if they pass, consume one unique V14 empirical launch identity;
3. execute exactly the frozen two-arm synthetic-only bridge;
4. no retry;
5. freeze result and stop.

If V14 fails the material-recovery gates, do not auto-open V15/V16. Follow the previously frozen stop rule and choose one larger redesign/independent real-development/pause decision path.

**Resume instruction:** Preserve V9-V13 and the V14 contract/preflight exactly. At a generic “continue”, documentation/review only. Await fresh explicit authorization for empirical V14 execution.


## V14 empirical attempt 1 consumed — INVALID / non-interpretable — corrected package prepared, not executed — 2026-09-29

**THIS IS THE CURRENT RESUME AUTHORITY. It supersedes the earlier “await empirical V14 authorization” boundary.**

The user explicitly authorized empirical V14. That authorization was consumed by exactly one launch:

- launch identity: `v14-matched-context-v1-20260929-01`
- workflow run: **36546933952**
- job: **109335463434**
- head: `8487cc3a433df177285582b966d36ed54bec368f`
- run attempt: **1**
- conclusion: **failure**
- artifact count: **0**

Frozen failure records:
- `docs/astra/V14_EXECUTION_ATTEMPT1_FAILURE_V1.md`
- `docs/astra/V14_EXECUTION_ATTEMPT1_FAILURE_V1.json`

### What passed before execution

Fail-closed V14 validator:
- **7/7 tests passed**
- contract identity valid
- schedule identity valid
- recovery gates valid
- no empirical-authorization mutation inside the frozen contract
- no gate weakening

### What executed

The runner then:
- generated two synthetic 2-second datasets;
- trained exactly **2 models**;
- completed **500 updates/model**;
- completed **1,000 optimizer steps total**;
- performed synthetic evaluation for the control reproduction guard.

No:
- V2B;
- P1;
- P2;
- P3;
- real-audio inference;
- threshold search;
- scientific retry;
- main or Production mutation.

### Failure classification

The runner raised:

`RuntimeError: control reproduction failed`

This happened **after training both models**, but before a valid V14 result/artifact was written.

Therefore attempt 1 is:
- **not a V14 scientific PASS**;
- **not a V14 scientific FAIL**;
- **INVALID / NON-INTERPRETABLE** because the required historical control identity was not reproduced.

Do not infer or reconstruct bridge metrics from this attempt.

### Root cause

The V14 runner incorrectly used the new bridge schedule root **20260929** for paired-batch sampling.

Historical V9 used:
- root **20260927**
- paired-batch RNG seed `20260927 + 17001`

Attempt 1 used:
- root **20260929**
- paired-batch RNG seed `20260929 + 17001`

Thus the control training batch plan was not the frozen historical V9 control plan.

A second prospective parity issue was also found:
- attempt 1 used `ubuntu-latest`, Python 3.11 and freshly resolved packages;
- historical V9 used **ubuntu-22.04**, **Python 3.10.15**, pip 24.0, and exact `astra_backend/tabcnn_runtime/requirements.lock.txt`.

The reproduction guard correctly stopped interpretation.

### Corrections prepared after failure — NOT empirically executed

Corrected package now separates:
- V14 timing/schedule seed = **20260929**
- historical control batch root = **20260927**

The workflow now uses:
- ubuntu-22.04
- Python 3.10.15
- pip 24.0
- exact historical CPU requirements lock

Future reproduction failures also preserve a diagnostic JSON before raising.

A focused guard now asserts:
- `BATCH_ROOT == 20260927`

Corrected blobs:
- runner `68fd78964acc474337988182fc7c619adff691b2`
- workflow `8be667ab11f6e1548c227f2d3b1ddb762ecfa408`
- tests `c0ffdcf95759c0a5e54e95b1f4349f866f704a29`

No corrected empirical execution has occurred.

### Current authorization boundary

**The prior empirical authorization is consumed. No retry is authorized.**

At a generic “continue”:
- documentation/review only;
- no new marker;
- no rerun of run 36546933952;
- no corrected V14 launch;
- no rendering/training/inference.

A fresh explicit user authorization is required before one corrected V14 execution.

If freshly authorized:
1. verify corrected blobs and exact historical runtime pins;
2. run focused validator/tests first;
3. enforce historical control batch identity;
4. consume a new unique corrected launch identity;
5. execute exactly one corrected two-arm V14;
6. if control reproduction fails, preserve the diagnostic artifact and stop;
7. if control reproduces, apply the frozen material-recovery gates;
8. no automatic retry, V2B, P1/P2/P3, or Production mutation.

The scientific V14 question remains **unanswered** after attempt 1.


## V14 empirical execution complete — FAILED material-recovery gate — serial micro-optimization closed — 2026-09-29

**THIS IS THE CURRENT RESUME AUTHORITY.**

Fresh explicit authorization was used for exactly one corrected conforming V14 empirical execution.

### Provenance

- workflow run **36590057639**
- job **109480499261**
- launch identity `v14-matched-context-v1-20260929-02`
- launch commit `e6b3085493b90cecd3ce56d498609ce1afaf54b7`
- artifact **11043457682**
- artifact digest `sha256:bc69dfbc4de527e2cef9c85b7f0cc29bca27aea16f16f799222d7ef6de9f02fb`
- result:
  - `docs/astra/V14_MATCHED_CONTEXT_BRIDGE_RESULT_V1.json`
  - `docs/astra/V14_MATCHED_CONTEXT_BRIDGE_RESULT_V1.md`

The earlier run **36546933952** is a technical invalidation, not an accepted scientific result: it used the wrong historical batch root and a non-parity runtime, then failed the control reproduction guard. Those issues were repaired before the fresh authorized corrected run.

### Validator and control

The fail-closed V14 validator tests passed before empirical execution.

The corrected run exactly reproduced the successful historical 2-second comparator:
- precision **0.8269230769**
- recall **0.6666666667**
- F1 **0.7381974249**
- negative FP/s **0**
- state admission **0.2945736434**
- onset admission **0.6201550388**
- joint admission **0.2868217054**

### V14 bridge primary common-population result

- precision **0.4968944099**
- recall **0.6201550388**
- F1 **0.5517241379**
- negative FP/s **0**
- state admission **0.2868217054**
- onset admission **0.5736434109**
- joint admission **0.2713178295**

Versus reproduced control:
- precision **-0.3300286670**
- recall **-0.0465116279**
- F1 **-0.1864732870**

Recovery relative to frozen V9 failure:
- F1 deficit recovered **38.54%**
- precision deficit recovered **34.32%**

### Frozen gate decision

Required:
- F1 >= **0.5864900168**
- precision >= **0.5756752789**
- recall decline <= **0.05**
- negative FP/s <= **0.10**

Observed:
- F1 -> **FAIL**
- precision -> **FAIL**
- recall decline 0.0465116279 -> **PASS**
- negative FP/s 0 -> **PASS**
- exact two models / 500 updates each -> **PASS**
- finite -> **PASS**
- no threshold search -> **PASS**
- no scientific retry -> **PASS**

**V14 overall: FAIL.**

Do not reinterpret the meaningful V9 improvement as a pass.

### Important generator evidence

Bridge render:
- 294 examples
- 588 s
- 819 attack groups
- 987 attacked labels
- **384 deterministic state truncations**

Control:
- 294 examples
- 588 s
- 735 attack groups
- 903 attacked labels
- 0 truncations

This is strong evidence that the denser V9-style short-gap timing conflicts with historical state-duration semantics in the 2-second bridge. It also changes active/inactive sampler-pool geometry.

The 2-second bridge recovered a substantial minority of the V9 failure, so context duration mattered, but the remaining large precision/F1 gap shows that 4-second context alone was not the full cause.

### Stop rule now active

Do **not**:
- open V15/V16 automatically;
- run another sampler-mixture or timing micro-study;
- retune thresholds;
- change losses;
- increase steps;
- search alternate bridge schedules;
- rerun V14;
- run V2B;
- access P1/P2/P3;
- mutate main or Production.

The serial synthetic micro-optimization path is closed.

### Next authorized task at generic “continue”

Documentation/review only.

Prepare one decision brief comparing exactly these three paths:
1. **larger synthetic-generator redesign** — address timing/state-duration compatibility and joint context generation as a first-class design problem;
2. **separately authorized independent real-development evidence** — only under a new source/acquisition/evaluation plan, with P3 still sealed;
3. **pause this model line**.

The decision brief must:
- summarize V9-V14 evidence at system scale;
- explicitly include the V14 384-truncation finding;
- distinguish what is established from what remains unknown;
- compare information value, risk of overfitting, cost, and what each path could actually resolve;
- recommend exactly one next research direction for user review, but do not execute it;
- preserve all current real-data boundaries.

No new empirical project is currently authorized.

**Resume instruction:** V14 is frozen as a failed result. At generic “continue,” produce the documentation-only post-V14 decision brief and update both handoffs. Do not run any model, render, inference, V2B, or real-data step without a new explicit authorization.


## Post-V14 product-direction review — 2026-10-02

**CURRENT RESUME POINTER.** The requested documentation-only decision brief is complete:
- `astra-work/POST_V14_GPT56_HANDOFF_2026-10-02.md`

Recommendation: **independent real-development evidence**, beginning with a bounded bass-first comparison of original isolated tracks versus separated versions of the same performances, plus a separate verified-note-to-tab evaluation. This is a recommendation for review, not empirical authorization. The brief compares all three required paths and includes V14's 384 truncations, event-level errors, six-second negative denominator, local-model limitations and historical Basic Pitch bass-range mismatch.

Qualify historical causal wording: the V14 package result does not isolate clip duration; deterministic truncation is not automatically incorrect annotation. All original results remain frozen, including V14 FAIL.

**Next task for GPT-5.6:** prepare one concrete, metadata/documentation-only independent bass feasibility execution packet as specified in the brief. Establish sources/rights, annotation and grouped split plan, candidate identities, metrics, budget and prospective decision rules before requesting one bounded execution authorization. Reuse existing infrastructure; do not restart serial synthetic experiments. This review accessed no audio/weights and executed no models/tests/workflows.

P1/P2/V2B remain closed; P3 sealed; no V15/V16, rendering/training/inference or main/Production changes authorized by this review. Earlier conflicting resume sections are historical.


## Independent bass feasibility execution packet prepared — 2026-10-02

**CURRENT RESUME POINTER.** The documentation-only packet requested by the post-V14 review is now prepared:

- `docs/astra/INDEPENDENT_BASS_FEASIBILITY_EXECUTION_PACKET_V1.md`
- `docs/astra/INDEPENDENT_BASS_FEASIBILITY_EXECUTION_PACKET_V1.json`
- fail-closed entry point: `astra_backend/evaluation/independent_bass_feasibility_v1.py`

No audio, corpus, checkpoint or model was opened or downloaded. No separation, transcription, rendering, inference, training, decoder execution or workflow dispatch occurred. P1/P2/V2B remain closed; P3 remains sealed; V15/V16 remain unopened; main/Production unchanged.

The packet freezes the 12-performance / 8-development + 4-confirmation grouped design, annotation rubric, three-arm measurement structure, exact event matching rules, prospective engineering gates and scientific operation-count budget. It explicitly preserves the historical Basic Pitch bass-range mismatch instead of reusing that runner unchanged.

Execution remains **disabled** because the exact 12-source rights-cleared manifest, bass-valid Basic Pitch configuration, one eligible separator, runtime/peak-memory evidence, temporary-storage ceiling and independent annotations are still missing. Current paid-spend ceiling is CAD $0.

**Next task:** metadata/documentation only. Identify and rights-review the 12 candidate performances without opening audio; resolve/freeze the bass-valid T1 configuration; select and rights-review exactly one S1 separator; fill measured runtime/memory/storage ceilings using only permitted non-study smoke material. Then update/freeze the packet and request one bounded authorization for exactly the admitted 12-performance run.

Do not treat this preparation as execution authorization.


## Independent bass metadata review — 2026-10-02

**CURRENT RESUME POINTER.** Continued preparation only.

Added:
- `docs/astra/INDEPENDENT_BASS_FEASIBILITY_METADATA_REVIEW_V1.md`

Progress:
- official Basic Pitch metadata confirms the model note representation begins at MIDI 21 / A0, so standard bass E1 is inside the representation;
- V1 T1 settings are now prospectively defined in the review: Basic Pitch 0.4.0, onset/frame 0.50/0.30, 127.7 ms minimum note length, returned MIDI 28-67 (E1-G4), using the bundled ICASSP-2022 TFLite model with the historical repository-asserted model SHA retained for later environment verification;
- Open-Unmix UMX-HQ is the concrete provisional S1 technical candidate, but remains **not execution-eligible** because the reviewed weight/training-data rights do not establish the required use permission;
- MedleyDB/MUSDB are not admitted under their non-commercial/academic restrictions; Cambridge-MT is not admitted without direct contributor permission;
- a 3-group / 12-slot collaborator-acquisition design is frozen, with C03 held as the confirmation group.

No real source identity, permission, file or hash was invented. No model/checkpoint was downloaded or loaded. No audio was opened. No inference, separation, training, decoder evaluation or workflow dispatch occurred. P1/P2/V2B remain closed; P3 sealed; main/Production unchanged.

**Next task:** populate the 12 acquisition slots with real permissioned sources; resolve UMX-HQ weight-use rights or reject it and review one alternate separator; then benchmark T1/S1 only on a permitted non-study synthetic smoke asset and freeze runtime/memory/storage ceilings before requesting empirical authorization.


## Guitar sample preservation/catalog checkpoint — 2026-10-02

The user re-uploaded the complete previously collected guitar sample set: **15 MP3 files**, reported as individually downloaded from Pixabay in the earlier research workflow.

Preservation:
- all 15 original MP3 files were copied into the persistent ChatGPT Library folder:
  `/Astra Audio/Guitar Samples 2026-10-02/`
- catalog copies were stored there as `GUITAR_SAMPLE_CATALOG_V1.md` and `GUITAR_SAMPLE_CATALOG_V1.json`
- original audio remains outside Git.

Repository catalog:
- `docs/astra/GUITAR_SAMPLE_CATALOG_V1.md`
- each sample has a stable catalog ID `GTR-PXB-01` through `GTR-PXB-15`, exact filename, SHA-256, duration, sample rate, channels, and descriptive filename-derived tags.

Rights/provenance boundary:
- user reports Pixabay as the source;
- exact asset URLs/license snapshots are not yet preserved;
- do not treat filenames as verified lead/rhythm labels or as independently verified licensing evidence.

This guitar set is preserved for the later guitar feasibility stage and does not alter the current bass-first execution boundary.


## Pixabay guitar/control audio cataloged — 2026-10-02

Re-upload batch cataloged in `docs/astra/PIXABAY_GUITAR_AUDIO_CATALOG_V1.md`.

- 30 MP3 files received.
- 24 filename-identified guitar samples.
- 6 non-guitar/control samples (drums, speech, typing, crowd/applause).
- Exact SHA-256, duration, sample rate and channel count recorded for every uploaded file.
- Audio binaries were not committed to Git.
- Musical descriptors are filename-derived only, not reference annotations.
- User reports these were individually downloaded from Pixabay.com in an earlier ChatGPT-guided session; per-asset Pixabay source/license records still need re-verification before empirical benchmark admission.

These files are preserved as a future guitar-feasibility candidate pool plus negative controls. They are separate from the bass-first feasibility study and do not reopen V15/V16/P1/P2/V2B/P3.


## Pixabay bass candidate pool complete — 2026-10-02

Cataloged in `docs/astra/PIXABAY_BASS_AUDIO_CATALOG_V1.md`.

- 30 uploaded bass candidates.
- Total duration: 340.805 s (5 min 40.8 s).
- Exact SHA-256, measured duration, sample rate and channel count recorded for every file.
- Audio binaries were not committed to Git.
- Coverage spans clean/simple phrases, slap/funk, picked bass, rock/death-metal, slow/fast riffs, isolated and sustained notes, low-register diagnostics, fretless/open-string material and distorted bass.
- B30 (`cekketto-riff-dom-cm-603128.mp3`) is cataloged as a bass-heavy electronic-riff candidate and should stay separate until source/type verification.

Important: this 30-file pool is not a substitute for the independent 12-performance paired isolated-bass + matching-mix study. Most candidates lack a matching full mix of the same performance, so they cannot answer the Arm-B separation-penalty question by themselves.

**Next task:** freeze per-asset Pixabay page/license provenance, classify physical-bass vs synthesized/processed/uncertain, select a non-overlapping diagnostic subset for T1 smoke/range testing, and keep the paired 12-source study separate. No empirical model run is authorized by this catalog.


## Pixabay bass provenance/classification review — 2026-10-02

Added `docs/astra/PIXABAY_BASS_PROVENANCE_CLASSIFICATION_V1.md`.

Current Pixabay terms were reviewed as the governing provenance baseline: downloaded non-CC0 content is licensed for commercial or non-commercial use/adaptation subject to prohibited uses, including no standalone redistribution; asset/source records should be retained. This project continues to keep audio binaries out of Git.

The 30 bass candidates are now conservatively classified into strong physical-bass candidates, probable physical-bass candidates, and uncertain assets. B03 (Simple Bass) and B30 (riff dom Cm) remain outside physical-bass evaluation until manually verified.

A proposed 12-file **diagnostic smoke subset** is frozen for later consideration: B05, B19, B20, B12, B15, B21, B23, B22, B01, B06, B08 and B26. This subset is intentionally diverse across low-register notes, raw mono, fretless/open string, picked/slap articulation, long sustain, distortion, regular loop, fast metal, funk/slap and slow phrase material.

This diagnostic subset does **not** replace the independent 12-performance paired isolated-bass + matching-mix study and no model execution is authorized by this review.


## Pixabay bass T1 smoke diagnostic prepared — 2026-10-02

Prepared a fully disabled metadata-only diagnostic package around the frozen 12-file Pixabay bass subset:
- `docs/astra/PIXABAY_BASS_T1_SMOKE_MANIFEST_V1.json`
- `docs/astra/PIXABAY_BASS_T1_SMOKE_EVALUATOR_CONTRACT_V1.md`
- `astra_backend/evaluation/pixabay_bass_t1_smoke_v1.py`

The manifest freezes the exact 12 IDs, filenames, asset IDs, SHA-256 hashes, durations, sample rates, channel counts and diagnostic roles. Scientific budget is fixed at 12 transcriber invocations, 0 separator calls, 0 training runs, 0 scientific retries and CAD $0.

The evaluator contract explicitly forbids precision/recall/F1 because these fixtures do not yet have independent note-event ground truth. Allowed outputs are ingestion/reproducibility, runtime/memory, event-shape sanity, events/sec, pitch span and retrigger/octave-spread diagnostics only.

The Python entry point is intentionally fail-closed and contains no model-execution implementation. No audio/model was opened and no inference occurred.

Execution remains blocked on: frozen per-asset Pixabay provenance for all 12, immutable T1 environment/model/config hashes, measured runtime/peak-RSS ceilings, and one explicit bounded authorization.


## Unified guitar+bass recognition set — 2026-10-02

Merged the preserved guitar, bass and negative-control catalogs into a single recognition-layer design:
- `docs/astra/UNIFIED_GUITAR_BASS_AUDIO_RECOGNITION_SET_V1.md`
- `docs/astra/UNIFIED_GUITAR_BASS_AUDIO_RECOGNITION_SET_V1.json`

Current pool:
- 24 guitar files / 244.110 s
- 30 bass candidates / 340.805 s
- 6 other/negative controls / 41.450 s
- 60 files total / 626.365 s (10 min 26.4 s)

V1 recognition labels are `guitar`, `bass`, and `other`. B03 and B30 remain excluded from scored physical-bass recognition until manually verified.

The recognition layer is deliberately separated from transcription and tablature. Recommended progression is recognition -> instrument-specific transcription -> verified note evaluation -> string/fret mapping -> mixed-song separation pipeline.

Random file-level train/test splitting is forbidden because related files/contributors could leak across the split. Any learned classifier must group by contributor/source family and hold related series together.

This is still a fixture pool, not authorized training/inference. No model execution occurred.


## Clean stem separation / bleed suppression architecture — 2026-10-02

Added `docs/astra/CLEAN_STEM_SEPARATION_BLEED_SUPPRESSION_ARCHITECTURE_V1.md`.

Design direction: replace one-pass separation with a staged pipeline: six-stem RoFormer -> mixture residual -> cross-stem competition -> target-preserving bleed suppressor -> recognition feedback gate -> optional note-aware protection -> optional multi-separator agreement -> mixture-consistency reconstruction -> downstream transcription evaluation.

Primary optimization target is not zero audible bleed. It is preservation of true guitar/bass notes while reducing false transcription events caused by competing stems. A cleaned stem is only better if downstream transcription improves without materially deleting target content.

The design proposes a future S0 synthetic-mixture experiment using the already cataloged rights-cleared guitar/bass/control fixtures, because exact component ground truth would be known. This is not equivalent to real commercial-song separation and remains a separate empirical boundary.

No separator/model/checkpoint was downloaded or run. No audio was processed. No synthetic mixture was created. Next safe preparation step is a disabled synthetic-mixture matrix with frozen component identities, gains and expected stems.


## S0 synthetic mixture fixture generated and frozen — 2026-10-02

Created and verified the first controlled synthetic mixture set for separator/bleed research:
- `docs/astra/S0_SYNTHETIC_MIXTURE_MANIFEST_V1.json`
- `docs/astra/S0_SYNTHETIC_MIXTURE_FIXTURE_V1.md`
- `astra_backend/evaluation/build_s0_synthetic_mixtures_v1.py`

Execution performed in the working container:
- 12 deterministic mixtures generated from cataloged guitar, bass and control uploads;
- 94.602 s total;
- 44.1 kHz stereo PCM float32;
- fixed -6 dB global headroom with prospectively fixed component-relative gains;
- no clipping observed (max absolute sample peak 0.644333);
- rendered component stems numerically reconstruct each generated mixture exactly in the verification pass (maximum absolute reconstruction error 0.0).

Generated WAVs/stems remain outside Git; exact mix hashes and deterministic recipe are committed.

This fixture provides exact component ground truth for future separator/bleed-cleanup evaluation. It does not establish performance on mastered commercial recordings.

No source separator, recognizer, Basic Pitch inference, training, or tab decoder was run. The next empirical step is to select one rights-cleared separator/checkpoint and define a frozen evaluation contract comparing separated stems against these known ground-truth components before any cleanup optimization.


## S0 bleed-cleanup engine built and unit-tested — 2026-10-02

Built:
- `astra_backend/evaluation/stem_bleed_cleanup_v1.py`
- `astra_backend/evaluation/evaluate_s0_bleed_cleanup_v1.py`
- `astra_backend/evaluation/separator_adapter_v1.py`
- `docs/astra/S0_BLEED_CLEANUP_RESULT_V1.json`
- `docs/astra/S0_BLEED_CLEANUP_DEVELOPMENT_V1.md`

The cleanup engine uses soft cross-stem STFT competition with a conservative floor so target energy is never hard-zeroed. Current frozen development settings: FFT 2048, hop 512, magnitude power 2.0, competition weight 0.50, minimum retained gain 0.60. An exact residual is retained so cleaned stems + residual reconstruct the input mixture.

Synthetic unit test: all 12 frozen S0 mixtures were contaminated deterministically with -18 dB of each competing ground-truth stem. The cleanup improved mean SI-SDR on all 12 mixtures. Mean improvement +2.665 dB; worst mixture +1.175 dB; maximum reconstruction absolute error 5.96e-08. An earlier more aggressive cleanup setting that harmed some mixtures was rejected.

This is a cleanup-math validation only, not separator evidence. No learned separator/model/checkpoint was downloaded or run. `separator_adapter_v1.py` remains fail-closed until one rights-cleared separator identity/checkpoint is frozen.

**Next task:** select exactly one rights-cleared separator/checkpoint, implement its adapter without changing the frozen cleanup settings, run S0 separator outputs against exact ground truth, then compare raw separator vs cleaned separator SI-SDR/leakage/reconstruction and downstream transcription only if that first separator test justifies it.


## BS-Roformer-SW 6-stem candidate frozen but rights-blocked — 2026-10-02

Added:
- `astra_backend/evaluation/bs_roformer_sw_6stem_adapter_v1.py`
- `docs/astra/BS_ROFORMER_SW_6STEM_CANDIDATE_REVIEW_V1.md`

Technical contract is now frozen for the exact 6-stem candidate: bass, drums, other, vocals, guitar, piano; 44.1 kHz stereo; STFT 2048 / hop 512; fixed 176400-sample chunks. Exact original checkpoint and ONNX export revisions/SHA-256 values are recorded.

Rights conclusion: the original pretrained checkpoint is published with license **unknown**. Later ONNX rehosts mark their export/code lineage MIT, but explicitly acknowledge that the original pretrained-weight provenance/license is unresolved. Therefore no checkpoint download or separator execution is authorized from this candidate.

The adapter remains fail-closed. The frozen S0 mixture fixture and bleed-cleanup settings remain unchanged.

**Next task:** either obtain explicit enough rights/provenance for these weights, or reject this candidate and select one model whose pretrained-weight license is explicit before any separator run.


## User-authorized BS-Roformer ONNX S0 integration — 2026-10-02

The user explicitly directed the project to use the `elicwhite/bs-roformer-sw-6stem-onnx` package for educational/development evaluation. This direction is recorded as authorization to proceed technically; it is **not** recorded as a legal conclusion that fair use resolves the pretrained-weight license/provenance issue.

Updated/built:
- `astra_backend/evaluation/bs_roformer_sw_6stem_adapter_v1.py`
- `astra_backend/evaluation/run_bs_roformer_s0_v1.py`

Important correction made during integration: the ONNX graph does **not** accept waveform audio directly. It consumes `spec_real` and `spec_imag` tensors with shape [1,2,1025,345] generated using Hann-window STFT (n_fft 2048, hop 512, center=true) for 176400-sample / 4-second chunks, and returns real/imag six-stem spectrograms [1,6,2,1025,345]. The adapter now implements that exact contract, iSTFT reconstruction, stem order bass/drums/other/vocals/guitar/piano, and 25% chunk overlap-add.

The S0 runner verifies the exact FP16 model SHA-256, separates each frozen S0 mixture, scores raw guitar/bass outputs against exact synthetic ground truth, applies the already-frozen bleed cleanup without retuning, scores cleaned outputs, and records runtime/reconstruction metrics.

Current execution blocker is environmental, not architectural: this ChatGPT runtime cannot currently install `onnxruntime` or download the 353 MB model because outbound package/model downloads are unavailable. No separator inference result is claimed. The code path is ready for an environment with the exact model file and ONNX Runtime.

Exact FP16 model SHA-256 remains `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`.


## Private S0 fixture sync packaging — 2026-10-02

Prepared a private-fixture workflow so Codespaces does not require manually re-uploading the 14 S0 source files every session.

Added:
- `scripts/sync_s0_fixtures.sh`
- `scripts/build_s0_fixtures.sh`
- `docs/astra/PRIVATE_S0_FIXTURE_REPO_SETUP_V1.md`

Updated `.gitignore` to exclude `/s0_sources/`, `/s0_generated/`, and `/models/bs-roformer/` from the public repo.

A local bundle `S0_FIXTURE_SOURCES_V1.zip` was created from the 14 exact user-uploaded fixture MP3s. It includes `manifest.json` with SHA-256 hashes and a private-use README. The connected GitHub writer cannot create a new private repository or upload binary MP3s, so the private repo itself still needs to be created/uploaded by the user once.

After that one-time setup, Codespaces can sync fixtures with a single command using `S0_FIXTURE_REPO=owner/private-repo ./scripts/sync_s0_fixtures.sh`, then rebuild S0 with `./scripts/build_s0_fixtures.sh`.


## GitHub Actions runner replaces routine Codespace execution — 2026-10-02

Added:
- `.github/workflows/astra-s0-separator-eval.yml`
- `docs/astra/S0_SEPARATOR_RUN_TRIGGER.txt`
- `docs/astra/GITHUB_ACTIONS_S0_SEPARATOR_RUNNER_V1.md`

The workflow runs only when the trigger file changes on `astra-work`, avoiding normal-commit compute. It checks out the private fixture repo using an Actions secret `S0_FIXTURE_TOKEN`, verifies the expected fixture count, installs dependencies, downloads/verifies the exact FP16 ONNX model SHA, regenerates the 12 S0 mixtures, runs the frozen separator+cleanup evaluator, writes a GitHub summary, uploads only the result JSON, and deletes private audio/model assets from the ephemeral runner.

No private audio is uploaded as an Actions artifact. Codespaces can remain stopped for routine S0 runs once the Actions repository secret exists.

Important: the existing Codespaces secret does not automatically populate GitHub Actions. Add the same fine-grained read-only token as repository Actions secret `S0_FIXTURE_TOKEN` before triggering the workflow.


## Successful GitHub-only BS-Roformer S0 run — 2026-10-02

GitHub Actions run `37078702459` completed successfully using the private fixture repo and exact FP16 ONNX model hash. Artifact `astra-s0-bs-roformer-result` (id `11257653088`, digest `sha256:ff36972b6765f1c5e80b404558ef2417070536d6384b2638a36168bd82f20874`) contains the evaluation JSON.

Result: 12 mixtures, 345.074 s wall time. The frozen cleanup stage **did not improve real BS-Roformer outputs overall**: mean target-present SI-SDR change `-0.632 dB`, worst `-5.161 dB`, best `+0.153 dB`. Therefore freeze the current cleanup as a failed transfer experiment rather than tuning it blindly on the same 12 fixtures.

The separator itself was strong on several fixtures (for example S0M01 guitar 20.052 dB, bass 23.584 dB raw; S0M05 guitar 34.022 dB raw). Absent-target leakage was near-zero in several cases, while S0M10 produced a materially harder false guitar output. Next direction: diagnostic/gated cleanup that only activates when contamination evidence is strong; preserve already-clean raw stems by default.

Detailed records: `docs/astra/BS_ROFORMER_S0_GITHUB_RESULT_V1.md` and `docs/astra/BS_ROFORMER_S0_GITHUB_RESULT_V1.json`.


## S0 separator bleed diagnostics V1 — 2026-10-02

Added `astra_backend/evaluation/stem_bleed_diagnostics_v1.py` and extended `run_bs_roformer_s0_v1.py` to record separator-output diagnostics during the same inference pass, without additional separator calls.

Diagnostics are ground-truth independent and do not alter audio. Per stem they record stem-to-mixture energy, interference pressure (shared time-frequency energy), competitor-dominance fraction, target-dominance fraction, ambiguous fraction, strongest overlap competitor, and per-competitor overlap/energy ratios.

Purpose: design a **gated cleanup** that preserves already-clean BS-Roformer stems and activates only when separator-output evidence indicates likely contamination. No V2 cleanup threshold has been chosen yet; this pass is diagnostic-only to avoid blind retuning on the same 12 S0 mixtures.

GitHub Actions diagnostic run `37079756274` is in progress from trigger commit `57d823069f214825aeb977f6442905f1b777c90f`.


## S0 bleed diagnostics completed — 2026-10-02

GitHub Actions run `37080742780` completed successfully and produced diagnostic artifact `11258307460` (digest `sha256:2901f82fa01d9ed88886e02e23a3e3ef24519dbbc0af6c29ee714bc174b7fb6b`).

Key result: simple spectral overlap/dominance metrics do **not** provide a safe cleanup gate on the current 12-mixture S0 set. Descriptive correlations with cleanup improvement were weak (interference pressure ~0.08, competitor dominance ~-0.01, target dominance ~0.04, stem-to-mixture energy ~-0.11).

Diagnostics correctly identify several already-near-silent absent-target stems, but the hard S0M10 false guitar output looks structurally like a legitimate strong guitar stem, while S0M03 guitar and S0M11 bass are genuine targets that the separator nearly misses and therefore look absent. Conclusion: low energy does not prove target absence and high target dominance does not prove target presence.

**Next direction:** recognizer-gated cleanup. Combine separator diagnostics with an independent guitar/bass/other recognizer; preserve raw stems by default when the recognizer agrees, permit conservative cleanup/reassignment only on strong disagreement + contamination evidence, and preserve/flag uncertain cases rather than destructively suppressing them. S0M10 guitar is the key hard false-positive fixture.

Detailed records: `docs/astra/S0_BLEED_DIAGNOSTICS_RESULT_V1.md` and `docs/astra/S0_BLEED_DIAGNOSTICS_RESULT_V1.json`.


## YAMNet zero-shot recognizer result — 2026-10-02

GitHub Actions run `37081779592` completed successfully. Artifact `11258687346` digest `sha256:b097366a43d0e1ee4d095234065fe0ced4d5c1861666df3d0fcc467a34b8ae33`.

Result: guitar-vs-bass evidence was correct for 6/6 guitar fixtures and 5/6 bass fixtures. B12 picked bass was the one bass miss (guitar 0.1557 vs bass 0.1390). Controls were extremely low-evidence (mean guitar 0.000543, mean bass 0.000286). G13 is an important low-evidence true-guitar fixture despite the correct relative winner.

Decision: YAMNet is useful as independent evidence but not yet as a hard winner-take-all gate. Next direction is a gate with absolute string evidence + guitar/bass margin + explicit uncertain state + separator diagnostics. Recognizer disagreement alone must not delete a stem.

Detailed records: `docs/astra/YAMNET_RECOGNIZER_RESULT_V1.md` and `docs/astra/YAMNET_RECOGNIZER_RESULT_V1.json`.


## Recognizer-gated cleanup V1 result — 2026-10-02

GitHub Actions run `37082340739` completed successfully. Artifact `11259456727` digest `sha256:90ac2d210d8df9a0ee1b9b9d6ae3e09041acedaf477aeaa564d07c2445627b5d`.

Result: cleanup was applied to **0 stems**. Mean/worst/best target SI-SDR change were all `0.000 dB`. This means the preserve-by-default safety principle worked: the gate prevented the destructive blanket-cleanup behavior seen earlier. However, the gate is too conservative to improve hard false-stem cases such as S0M10 guitar.

Decision: keep preserve-by-default. Do not loosen thresholds just to force actions on the same 12 fixtures. Split the next work into (1) target-present bleed cleanup and (2) false-stem suppression/reassignment. S0M10 guitar remains the key false-stem fixture. Next experiment should compare claimed-stem vs competing-stem YAMNet evidence, reassignment consequences, and downstream transcription behavior rather than spectral attenuation alone.

Detailed records: `docs/astra/RECOGNIZER_GATED_CLEANUP_RESULT_V1.md` and `docs/astra/RECOGNIZER_GATED_CLEANUP_RESULT_V1.json`.


## Corrected duplicate-class action result — 2026-10-02

GitHub Actions run `37087791658` completed successfully. Artifact `11260744333` digest `sha256:54c0717f54147c0473f5db2b1bace917aac61c9a0e157e901a6a202922ed02c5`.

Only S0M10 was classified as a duplicate-class candidate. Correct mapping: false guitar stem + true bass companion. Raw bass SI-SDR was `0.0728 dB`. Muting the false guitar left bass unchanged at `0.0728 dB` and increased reconstruction max error from `0.008216` to `0.329865`. Merging the false guitar waveform into bass raised bass SI-SDR to `30.5695 dB` (**+30.4966 dB**) while preserving reconstruction error at `0.008216`.

Interpretation: in S0M10, BS-Roformer split one bass source across the guitar and bass outputs rather than creating an unrelated false guitar source. This strongly supports **duplicate-class consolidation** as a distinct post-separator correction: when both substantial guitar/bass outputs strongly support the same instrument class and satisfy mutual-overlap/energy-consistency checks, consolidate the mislabeled companion into the correct-class stem and zero the false-class stem. Otherwise preserve raw output.

This remains S0-only evidence from one duplicate-class fixture. Next task: expand the controlled duplicate-class fixture set in both directions and across split ratios before any real-audio or production use.

Detailed records: `docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.md` and `docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json`.


## Controlled duplicate-class stress V1 result — 2026-10-02

GitHub Actions run `37088717448` completed successfully. Artifact `11261451719` digest `sha256:c8b6864d90d43391e28a511e6edf2f84edc353d502b33e601394e7f7fb1a625f`.

Frozen PairClassifierConfig V1 generalized perfectly on the controlled detection task: **18/18 intended duplicate positives** (50/50, 40/60, 35/65 splits across 3 bass and 3 guitar sources) and **6/6 prospective hard negatives** (30/70, outside the frozen 6 dB energy-gap gate). This validates the detector on the controlled matrix in both guitar->bass and bass->guitar directions.

Important correction: the stress generator used exact scaled copies of the same source in each pseudo stem, so SI-SDR is scale-invariant and the reported merge-improvement values are not valid action-quality evidence for this experiment. All 24 merges reconstruct exactly (max error 0.0). The prior S0M10 merge result remains meaningful because the separator outputs were imperfect/non-collinear and merging improved bass SI-SDR from 0.0728 dB to 30.5695 dB.

Decision: freeze PairClassifierConfig V1 unchanged. Next task is a **non-collinear duplicate split stress** using complementary frequency partitions, time-varying leakage, phase/filter differences, and/or mild independent contamination while keeping the detector frozen. Do not move to automatic real-audio consolidation yet.

Detailed records: `docs/astra/CONTROLLED_DUPLICATE_STRESS_RESULT_V1.md` and `docs/astra/CONTROLLED_DUPLICATE_STRESS_RESULT_V1.json`.


## EXPLICIT NEXT STEPS — non-collinear duplicate stress follow-up — 2026-10-02

### Evidence just completed

GitHub Actions run `37089070395` (`Astra Non-Collinear Duplicate Stress`) completed successfully.

Artifact:
- id: `11262155308`
- digest: `sha256:17af190d0224c0654052baa02f35e0002c215147cd0432e1f21a3832b6c5b192`

Frozen `PairClassifierConfig V1` result:
- 16 controlled non-collinear cases
- pair accuracy: **15/16 = 93.75%**
- only miss: `G09_delayed_highband_leak`, classified `ambiguous_pair` because the energy gap was ~6.44 dB, just outside the frozen 6 dB gate
- detector thresholds remain **frozen**; do not loosen them from this result alone

Merge action result is **mixed**:
- time-varying split cases improved dramatically after consolidation:
  - B01: +142.32 dB
  - B08: +142.37 dB
  - G09: +140.36 dB
  - G14: +142.06 dB
- some frequency/filter/delay cases improved modestly
- some correctly detected duplicate cases worsened after full merge:
  - B01 frequency partition: -0.47 dB
  - B01 delayed high-band leak: -0.38 dB
  - B01 filtered + contamination: -1.97 dB
  - G14 frequency partition: -2.89 dB
  - G14 delayed high-band leak: -3.06 dB
  - G14 filtered + contamination: -0.25 dB

Therefore **duplicate detection and duplicate consolidation are separate problems**.

### Current conclusion

Keep `PairClassifierConfig V1` frozen.

Do **not** automatically merge every detected duplicate-class pair.

The next stage must answer:

> When a duplicate-class pair is detected, can we decide whether the two stems are complementary fragments of the same source (safe to consolidate) versus differently filtered/phase-shifted/contaminated versions where full summation may reduce source fidelity?

### Exact next implementation task

Build **Duplicate Consolidation Safety Gate V1** as a diagnostic-only layer.

It must use only separator outputs / pair evidence at decision time and must not inspect ground-truth reference audio for the decision.

For each duplicate-class candidate, record at least:

1. **Waveform coherence**
   - zero-lag correlation
   - best-lag normalized cross-correlation over a small bounded lag window
   - best lag in samples/ms

2. **Spectral complementarity**
   - per-bin magnitude overlap
   - fraction of energy unique to each stem
   - fraction of energy shared by both stems
   - low-band vs high-band energy balance between pair members

3. **Phase consistency**
   - phase-consistency / coherence summary over active bins
   - flag strong delayed/phase-shifted duplicate behavior

4. **Temporal complementarity**
   - framewise energy correlation
   - anti-correlation/complementarity score for time-varying splits

5. **Recognizer consistency**
   - retain existing YAMNet guitar/bass evidence for both stems
   - retain pair-classifier state unchanged

6. **Action simulation**
   - raw companion
   - full merge
   - optional bounded weighted merge candidates chosen prospectively, not tuned per fixture
   - reconstruction error for every simulated action

### Prospective evaluation design

Use the same 16 frozen non-collinear cases.

Do not change `PairClassifierConfig V1`.

Before seeing new action results, freeze a small rule set for the consolidation safety gate.

At minimum the gate must produce:
- `merge_safe`
- `preserve_separate`
- `uncertain`

The safety objective is more important than forcing actions.

### Success criteria

The next action gate should:

- keep pair detection at the existing frozen classifier behavior
- avoid full merge on the known harmful merge cases above
- permit merge on the four time-varying split cases that showed very large gains
- make **no harmful automatic action worse than -0.5 dB SI-SDR** on this frozen 16-case development set
- preserve mixture reconstruction to numerical precision whenever a merge is applied

If the gate cannot separate helpful from harmful merge cases without looking at ground truth:
- STOP automatic consolidation work at this stage
- keep duplicate detection as a diagnostic/flagging feature only
- do not retune PairClassifierConfig V1 to compensate

### After this gate

Only if the consolidation safety gate passes the frozen synthetic criteria:

1. add a small **new holdout synthetic set** with new source identities and perturbation seeds;
2. freeze all thresholds before evaluating that holdout;
3. require no destructive false positives before considering any bounded real-recording validation;
4. only then connect the safe duplicate-class consolidation stage into the broader separator -> recognizer -> transcription pipeline.

### Boundaries

Do not:
- deploy to production
- change `main`
- automatically consolidate real recordings
- retune the pair classifier on these same 16 cases
- claim commercial-song or real-world generalization from this synthetic evidence
- reopen archived V15/V16, P1/P2/P3, V2B, or older failed model lines

### Immediate resume instruction

**Next GPT-5.6 task:** implement `Duplicate Consolidation Safety Gate V1` and its diagnostic evaluator/workflow on `astra-work`, using the frozen 16-case non-collinear set and the success/stop rules above. Save results back into this file before moving to holdout or real-audio work.


## Duplicate Consolidation Safety Gate V1 result — 2026-10-02

Implemented and evaluated the exact follow-up requested above.

### Implementation

Added:
- `astra_backend/evaluation/duplicate_consolidation_safety_gate_v1.py`
- `astra_backend/evaluation/evaluate_duplicate_consolidation_safety_gate_v1.py`
- `.github/workflows/astra-duplicate-consolidation-safety-gate-v1.yml`

The decision layer uses separator-output / pair evidence only:
- corrected zero-lag and bounded best-lag waveform correlation
- best lag in samples/ms
- spectral shared and unique energy fractions
- low/high-band balance
- active-bin phase consistency
- framewise energy correlation
- time-varying energy-share swing
- frozen pair-classifier state and existing recognizer evidence

Reference/source audio is not available to the gate decision. It is used only afterward by the evaluator for retrospective SI-SDR scoring.

Important implementation note: the pre-existing `pair_coherence_v1.max_short_lag_corr` initializes its best absolute correlation in a way that can leave a bogus perfect value. Safety Gate V1 therefore computes its own bounded-lag correlation correctly and does not alter the old helper or the frozen pair classifier.

### GitHub Actions evidence

Run: `37089667900` — **success**  
Workflow: `Astra Duplicate Consolidation Safety Gate V1`  
Head commit: `8e44afc86a81caedd9ec4dbf94f9a4a77ebf9a83`

Artifact:
- id: `11262196258`
- digest: `sha256:18ff6d8fae150b179e6fc666e28aff645e3680fe54ca92b83d077e7904b5f67c`

### Prospective result

Frozen 16-case development suite:
- pair-classifier accuracy remained **15/16 = 93.75%**
- `merge_safe`: **0**
- `preserve_separate`: **16**
- `uncertain`: **0**
- automatic merges: **0**
- minimum automatic-action delta: **0.0 dB**
- automatic merge reconstruction error: **0.0**

Success criteria:
- preserve frozen pair-classifier behavior: **PASS**
- permit all four time-varying split merges: **FAIL**
- avoid all negative full-merge cases: **PASS**
- no harmful automatic action worse than -0.5 dB: **PASS**
- numerical reconstruction when merge is applied: **PASS**
- overall gate: **FAIL**

The four time-varying split cases were all conservatively preserved even though retrospective merge gains were extremely large:
- B01: +142.32 dB
- B08: +142.37 dB
- G09: +140.36 dB
- G14: +142.06 dB

Their no-reference diagnostics were internally consistent:
- zero-lag correlation ~0.79–0.83
- spectral shared fraction ~0.27–0.33
- phase consistency ~0.9999
- energy-share swing ~0.73

The frozen V1 rule required much stronger waveform/spectral overlap, so it did not authorize them.

At the same time, every negative full-merge case was correctly blocked, including:
- B01 frequency partition: -0.47 dB
- B01 delayed high-band leak: -0.38 dB
- B01 filtered + contamination: -1.97 dB
- G14 frequency partition: -2.89 dB
- G14 delayed high-band leak: -3.06 dB
- G14 filtered + contamination: -0.25 dB

### Decision required by the prior stop rule

**STOP automatic duplicate consolidation at this stage.**

Do **not** retune Safety Gate V1 thresholds on these same 16 cases. That would be post-hoc fitting after the prospective result.

Keep:
- `PairClassifierConfig V1` frozen
- duplicate-class detection as diagnostic / flagging evidence only
- automatic consolidation disabled
- real recordings untouched
- `main` unchanged

Do **not** move to the synthetic holdout or real-audio consolidation validation, because the prerequisite gate did not pass.

Detailed records:
- `docs/astra/DUPLICATE_CONSOLIDATION_SAFETY_GATE_V1_RESULT.md`
- `docs/astra/DUPLICATE_CONSOLIDATION_SAFETY_GATE_V1_RESULT.json`

### Explicit next resume instruction

The duplicate-consolidation branch of research is now closed at **diagnostic-only** status unless a genuinely new consolidation hypothesis and new development protocol are introduced.

**Next GPT-5.6 task:** do not tune this gate further. Return to the broader separator -> recognizer -> transcription objective and identify the highest-value next diagnostic that can improve final guitar/bass tablature accuracy **without destructive stem mutation**. Prefer measurement of downstream transcription failure modes and confidence/flagging over another separator-action heuristic. Preserve all frozen boundaries above.


## S0 Transcription Failure Attribution V1 — 2026-10-02

Returned from duplicate-consolidation work to the broader separator -> recognizer -> transcription objective without mutating stems.

Implemented:
- `astra_backend/evaluation/evaluate_s0_transcription_failure_attribution_v1.py`
- `.github/workflows/astra-s0-transcription-failure-attribution-v1.yml`

Purpose: run the same frozen Basic Pitch 0.4.0 front end on each exact clean S0 guitar/bass component and on the corresponding untouched raw BS-Roformer stem, then compare exact-MIDI onsets at a fixed 50 ms tolerance. The clean-component transcription is an oracle-audio transcriber baseline, **not** asserted musical ground truth.

First workflow run `37090038784` failed only from a NumPy 2.x / Basic Pitch TFLite binary incompatibility (`_ARRAY_API not found`). Runtime was corrected by pinning NumPy 1.26.4. No scientific parameter changed.

Successful run: `37090246256`  
Head: `57386ca1a0cc98bed124debbd1b2f4c5ed2f3552`  
Artifact: `11262262754`  
Digest: `sha256:e0a1b42c60f2c8aacb10a477b6f70efa8fbfdc418ac049868fcfcebdad4b74ca`

Results:
- 12 mixtures
- 24 role probes
- 20 target-present probes
- 4 target-absent probes
- present-target micro precision **0.789**
- recall **0.632**
- F1 **0.702**
- macro F1 **0.663**
- 5 severe role failures with F1 < 0.5
- all 4 absent-target outputs generated false note events; 53 total

Severe cases:
- S0M03 guitar: SI-SDR -14.84 dB, F1 0.000
- S0M04 guitar: -6.91 dB, F1 0.230
- S0M10 bass: 0.07 dB, F1 0.302
- S0M11 bass: -14.08 dB, F1 0.261
- S0M12 guitar: -5.16 dB, F1 0.071

Descriptive Pearson correlation between raw separator SI-SDR and transcription agreement F1: **0.896**.

For description only:
- SI-SDR >= 15 dB: 12 probes, mean F1 0.864
- SI-SDR < 5 dB: 6 probes, mean F1 0.250

Error morphology across target-present probes:
- 137 unmatched separated events / false positives
- 299 unmatched clean-baseline events / misses
- 38 octave-related FPs
- 31 timing-only FPs
- 30 octave-related misses
- 36 timing-only misses
- only 1 near-semitone miss

Conclusion: source-separation quality can dominate downstream transcription stability. Do not tune Basic Pitch from these S0 outcomes. Instead investigate whether separator/transcriber signals available without ground truth can flag unreliable note output.

Detailed:
- `docs/astra/S0_TRANSCRIPTION_FAILURE_ATTRIBUTION_V1_RESULT.md`
- `docs/astra/S0_TRANSCRIPTION_FAILURE_ATTRIBUTION_V1_RESULT.json`


## S0 Transcription Reliability Observability V1 — 2026-10-02

Implemented:
- `astra_backend/evaluation/evaluate_s0_transcription_reliability_observability_v1.py`
- `.github/workflows/astra-s0-transcription-reliability-observability-v1.yml`

This stage remained descriptive only:
- no separator mutation
- no threshold search
- no fitted confidence gate
- no automatic accept/reject action

GitHub Actions run: `37090800270` — **success**  
Head: `977b1883f96d55ce3c690ed25950c8a832b3bbe3`  
Artifact: `11262263768`  
Digest: `sha256:4fb1caa6253b3cd89a98209b3160901c4aea6b9fbb6ad8d214b79dc887ae6427`

No-reference features were collected from:
- separator-output interference/dominance/energy diagnostics
- Basic Pitch event density/amplitude/duration
- dominant-pitch concentration
- octave-event behavior

Strongest descriptive single-feature associations with transcription-agreement F1:
- stem-to-mixture energy dB: Spearman +0.594
- interference pressure: -0.542
- strongest competitor energy ratio dB: -0.533
- mean note duration: +0.477
- event density: +0.464
- octave-related event fraction: +0.434
- competitor dominance: -0.427
- target dominance: +0.427

These are only moderate associations. Do **not** turn them into an S0-fitted reliability threshold.

Three absent-target cases are trivially recognizable as near-silent/interference-dominated:
- S0M07 bass: ~-92.55 dB stem-to-mixture, competitor dominance 1.0
- S0M08 guitar: ~-93.24 dB, competitor dominance 1.0
- S0M09 bass: ~-92.02 dB, competitor dominance 1.0

But **S0M10 guitar is the hard exception**. Guitar is absent in ground truth, yet its separator output looks internally strong:
- stem-to-mixture -3.03 dB
- interference pressure 0.120
- target dominance 0.776
- 33 Basic Pitch note events
- event density 4.48/s
- dominant MIDI share 0.545
- octave-related event fraction 0.485

The true S0M10 bass output also has 33 note events but poor agreement with the clean bass baseline (F1 0.302). Together with prior duplicate-class evidence, this is consistent with one bass source being represented across both labeled outputs.

### Current decision

Ordinary single-stem no-reference observability is not sufficient for a robust reliability flag on the hard case.

Do not:
- fit an S0 reliability cutoff
- retune Basic Pitch
- reopen automatic consolidation
- merge/mute/reassign audio
- change `main`

Detailed:
- `docs/astra/S0_TRANSCRIPTION_RELIABILITY_OBSERVABILITY_V1_RESULT.md`
- `docs/astra/S0_TRANSCRIPTION_RELIABILITY_OBSERVABILITY_V1_RESULT.json`

### Explicit next resume instruction

**Next GPT-5.6 task:** build **Cross-Stem Transcription Overlap / Role Ambiguity Diagnostic V1** on `astra-work`.

Keep it diagnostic-only. For each S0 mixture:
1. independently transcribe untouched raw guitar and bass separator outputs with the same frozen Basic Pitch settings;
2. compute exact-MIDI onset overlap at 50 ms, pitch-class overlap, octave-related near-onset overlap, and event-density balance between stems;
3. retain the frozen pair-classifier state / duplicate-class evidence as context when available;
4. specifically test whether S0M10 shows unusually high cross-stem musical-event overlap compared with ordinary complementary guitar+bass mixtures;
5. report distributions descriptively only — **do not choose an automatic role-ambiguity threshold on these same S0 fixtures**;
6. no audio mutation, consolidation, reassignment, suppression, production deployment, or `main` change.

If cross-stem transcription overlap meaningfully isolates S0M10-like duplicate-role behavior, use that pattern only to preregister a future holdout flagging test with thresholds frozen before evaluation. If it does not isolate the hard case, keep reliability flagging diagnostic-only and move downstream toward explicit uncertainty presentation rather than automatic correction.


## Cross-Stem Transcription Overlap / Role Ambiguity Diagnostic V1 — 2026-10-02

Implemented:
- `astra_backend/evaluation/evaluate_s0_cross_stem_transcription_overlap_v1.py`
- `.github/workflows/astra-s0-cross-stem-transcription-overlap-v1.yml`

Goal: determine whether the hard S0M10 duplicate-role case can be recognized from musical-event overlap between independently transcribed raw guitar and bass separator outputs.

No audio was modified and no threshold was fitted.

### Runtime boundary correction

Initial run `37091545955` failed because TensorFlow installation for YAMNet caused Basic Pitch to silently choose its TensorFlow SavedModel directory instead of the previously frozen TFLite file. This was rejected as a backend identity change.

Intermediate run `37091775151` still used the older TensorFlow-containing workflow and failed for the same reason.

Final implementation isolates Basic Pitch on its exact frozen TFLite model and imports the already-frozen duplicate-class context from `docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json` rather than re-running YAMNet in the same process.

### Successful evidence

Run: `37091792312` — **success**  
Head: `75b4bfb8b36f56e726aca7b32d05ce047c93f1d1`  
Artifact: `11263730676`  
Digest: `sha256:7cc5b69125dbc042c219a63fa73c4627a359bca7ed9b20591c0f6ecb0a795ed5`

Prior frozen pair context:
- only duplicate candidate: **S0M10**
- state: `duplicate_bass_candidate`

S0M10 vs 8 ordinary both-present guitar+bass mixtures:

- exact-MIDI onset F1: **0.0303**
  - rank 4/9
  - ordinary max 0.0851
  - z +0.34
- pitch-class onset F1: **0.0909**
  - rank 2/9
  - ordinary max 0.1176
  - z +1.12
- octave-related onset F1: **0.0606**
  - rank 2/9
  - ordinary max 0.1176
  - z +0.66
- any-pitch onset coincidence F1: **0.0909**
  - rank 7/9
  - ordinary median 0.1878
  - z -0.86
- event-density balance:
  - guitar events 33
  - bass events 33
  - min/max density ratio **1.000**
  - rank **1/9**
  - ordinary max 0.654
  - z **+3.14**

### Conclusion

The same-note-overlap hypothesis did **not** isolate S0M10.

The hard duplicate-role case has unusually symmetric transcription quantity, but not unusually strong identity overlap. Ordinary complementary mixtures can have equal or greater exact/pitch-class/octave/onset overlap.

Do **not** freeze an automatic cross-stem role-ambiguity gate from this result. Event-count symmetry from a single positive fixture is not specific enough.

Detailed records:
- `docs/astra/S0_CROSS_STEM_TRANSCRIPTION_OVERLAP_V1_RESULT.md`
- `docs/astra/S0_CROSS_STEM_TRANSCRIPTION_OVERLAP_V1_RESULT.json`

Decision required by previous handoff: keep reliability/role ambiguity diagnostic-only and move toward explicit uncertainty presentation rather than automatic correction.


## Transcription Uncertainty Presentation Contract V1 — 2026-10-02

Implemented:
- `astra_backend/transcriptionUncertaintyPresentation.mjs`
- `astra_backend/tests/transcriptionUncertaintyPresentation.test.mjs`
- `.github/workflows/astra-transcription-uncertainty-presentation-v1.yml`

GitHub Actions run: `37092615121` — **success**  
Head: `7b92c09a858a12b72968bfadc530b5e370a04d7d`

The contract:
- preserves exact note pitch/onset identity;
- keeps uncertain evidence visible rather than silently deleting it;
- defines no composite confidence score;
- authorizes no automatic correction;
- authorizes no automatic stem mutation;
- authorizes no automatic role reassignment;
- uses no S0-fitted thresholds.

Presentation states:
- `complete_tab_eligible`
- `evidence_visible_review_required`
- `no_reliable_note_evidence`

Fail-closed reason codes include:
- `PAIR_ROLE_AMBIGUITY_DUPLICATE_CLASS_CANDIDATE`
- `PAIR_MEMBER_MISSING_OR_SILENT`
- `PAIR_ROLE_RELATIONSHIP_AMBIGUOUS`
- all existing note-evidence evaluator failure reasons

Descriptive cross-stem diagnostics can be attached to the presentation packet only when explicitly marked descriptive-only; they cannot own a hidden acceptance rule.

Detailed:
- `docs/astra/TRANSCRIPTION_UNCERTAINTY_PRESENTATION_V1.md`
- `docs/astra/TRANSCRIPTION_UNCERTAINTY_PRESENTATION_V1.json`

### Current project position

The recent separator branch has now established:

1. raw separator quality strongly affects downstream transcription stability;
2. simple single-stem observability is insufficient for the hard duplicate-role case;
3. same-note cross-stem transcription overlap also does not uniquely isolate that case;
4. the frozen pair classifier can identify the known S0M10 duplicate-class condition, but safe automatic consolidation could not be prospectively established;
5. therefore the safest useful behavior is to expose uncertainty explicitly rather than make hidden audio/note corrections.

Keep all prior freezes:
- `PairClassifierConfig V1` unchanged;
- Basic Pitch settings unchanged;
- duplicate consolidation disabled;
- no S0-fitted reliability/overlap threshold;
- no real-recording automatic action;
- `main` unchanged.

### Explicit next resume instruction

**Next GPT-5.6 task:** integrate **Transcription Uncertainty Presentation V1** into a development-only end-to-end evidence packet, without connecting it to production delivery.

Build one deterministic integration test/path that composes:
1. adapted note evidence / evaluator result;
2. `noteEventExposure.mjs`;
3. pair-context diagnostics when present;
4. descriptive cross-stem diagnostics when present;
5. `transcriptionUncertaintyPresentation.mjs`.

Required proof cases:
- clean complementary pair + accepted note evidence -> `complete_tab_eligible`;
- duplicate-class pair + otherwise accepted note evidence -> exact notes remain visible but state becomes `evidence_visible_review_required`;
- unresolved note-evidence failure -> evaluator reason codes remain visible and complete-tab events are empty;
- no component is allowed to change MIDI or onset identity;
- no confidence score or automatic correction may appear.

Do not connect this packet to the user-facing app, production API, commercial recordings, or `main` yet. The next scientific step after the integration proof should be to define what new holdout evidence would be required before any automatic trust/flagging threshold could be considered.


## Development End-to-End Evidence Packet V1 — 2026-10-02

Implemented:
- `astra_backend/developmentEvidencePacket.mjs`
- `astra_backend/tests/developmentEvidencePacket.test.mjs`
- `.github/workflows/astra-development-evidence-packet-v1.yml`

GitHub Actions run: `37093151254` — **success**  
Head: `1652424308d9542f3eb4d8194ba0609f87dde5c8`

The development-only packet now deterministically composes:
1. structure-conditioned note-evidence adaptation;
2. note-evidence evaluation;
3. note-event exposure;
4. optional pair diagnostics;
5. optional descriptive-only cross-stem diagnostics;
6. transcription uncertainty presentation.

Required proof cases all passed:
- clean complementary pair + accepted evidence -> `complete_tab_eligible`;
- duplicate-class pair + otherwise accepted evidence -> notes remain visible, but presentation becomes `evidence_visible_review_required`;
- unresolved evaluator failures remain visible end to end and complete-tab events remain empty;
- exact MIDI/onset identity is invariant through all visible event layers;
- no composite confidence score or automatic correction appears.

The workflow also reran the uncertainty-presentation and note-event-exposure regression suites; both remained green.

Detailed:
- `docs/astra/DEVELOPMENT_EVIDENCE_PACKET_V1_RESULT.md`
- `docs/astra/DEVELOPMENT_EVIDENCE_PACKET_V1_RESULT.json`

Production delivery remains unauthorized. `main` remains unchanged.


## Transcription Trust / Flag Holdout Study Protocol V1 — 2026-10-02

Defined the minimum independent evidence required before any future automatic trust/flagging threshold may even be considered.

Implemented:
- `astra_backend/trustFlagHoldoutProtocol.mjs`
- `astra_backend/tests/trustFlagHoldoutProtocol.test.mjs`
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1.md`
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1.json`
- `.github/workflows/astra-trust-flag-holdout-protocol-v1.yml`

GitHub Actions run: `37093326513` — **success**  
Head: `91f9fdabb10a815f98039523b37d229843fe3f20`

### Required future study shape

Two source-disjoint phases are required.

Calibration minimum: **48 new cases**
- 12 complementary both-present
- 6 target-absent guitar
- 6 target-absent bass
- 6 duplicate-role guitar
- 6 duplicate-role bass
- 12 hard complementary confusers

Holdout minimum: **48 additional new cases** with the same balance.

Total minimum new evidence: **96 cases**.

Admission rules:
- no source asset may overlap S0/prior development;
- no source asset may overlap between calibration and holdout;
- valid SHA-256 source identities required;
- unique case IDs required;
- threshold must still be undefined at admission;
- automatic correction must remain unauthorized;
- production delivery must remain unauthorized.

The validator has green negative tests for:
- threshold leakage;
- calibration/holdout source leakage;
- prior-development source leakage;
- missing hard strata;
- duplicate IDs;
- malformed source hashes.

Detailed:
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1_RESULT.md`
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1_RESULT.json`

### Current scientific boundary

No actual new calibration or holdout cohort has been admitted yet.

Therefore:
- no trust/flag threshold exists;
- no automatic confidence gate may be introduced;
- no further S0 threshold tuning is allowed;
- no production integration is allowed;
- uncertainty presentation remains the correct fail-closed behavior.

### Explicit next resume instruction

**Next GPT-5.6 task:** perform **model-free source inventory / study-manifest preparation only** for the new 96-case trust/flag study.

Do not fabricate source identities.

Required next work:
1. inspect available private fixture/source inventory for genuinely new assets not used by S0 or other prior development;
2. build a candidate manifest only from real accessible source identities/hashes;
3. keep calibration and holdout source sets disjoint;
4. report exactly which required strata can and cannot currently be populated;
5. run `validateTrustFlagHoldoutStudyManifest()` only if a real candidate manifest can satisfy the protocol;
6. if there are insufficient new sources, stop and record the shortfall instead of weakening the protocol or reusing S0.

Do not:
- render new audio yet;
- run BS-Roformer;
- run Basic Pitch;
- define a threshold;
- change any frozen classifier/model setting;
- access commercial recordings;
- connect to production or `main`.

The next authorization boundary is **manifest admission only**.


## Trust / Flag Study Source Inventory — 2026-10-02

Performed the next authorized step: model-free source inventory only.

Inspected private repository:
- `dadrockyt-sys/dadrock-tabs-private-fixtures`
- branch `main`
- head `13e86335bc87740932f49cf2dd5251ba49b8d519`

Inventory contains:
- S0 fixture ZIP
- S0 README
- S0 manifest
- **14 source audio assets**

The S0 manifest provides SHA-256 identities for all 14.

### Eligibility result

New source assets eligible for the new Trust / Flag Holdout Protocol V1: **0**.

Every accessible source audio asset in the private fixture repo is already an S0 development source.

Therefore there is currently no legitimate way to populate:
- 48 new calibration cases
- 48 new sealed holdout cases

without violating source-disjointness.

### Decision

**STOP at manifest-admission boundary due to insufficient new source material.**

Do not:
- reuse S0 assets under newly rendered mixtures;
- transform/copy S0 and call it new source material;
- fabricate source identities/hashes;
- weaken the 96-case study design;
- define a threshold;
- render study audio;
- run BS-Roformer;
- run Basic Pitch;
- connect anything to production or `main`.

Detailed records:
- `docs/astra/TRUST_FLAG_SOURCE_INVENTORY_SHORTFALL_V1.md`
- `docs/astra/TRUST_FLAG_SOURCE_INVENTORY_SHORTFALL_V1.json`

### Explicit next resume instruction

The research code path is now blocked on **genuinely new source-disjoint fixture material**.

**Next GPT-5.6 task, once new fixtures are available:** inventory and SHA-256 hash the new assets first, record provenance, and build a real calibration/holdout candidate manifest satisfying `TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1`.

Before any audio rendering or model run:
1. prove all new source hashes are disjoint from the 14 S0 hashes;
2. prove calibration and holdout source sets are mutually disjoint;
3. satisfy every required stratum in both phases;
4. run `validateTrustFlagHoldoutStudyManifest()`;
5. commit the admitted manifest and its exact hashes.

Only after a real manifest passes admission may a future step design fixture rendering.

Until new source material exists, do not continue tuning S0. The current safe endpoint is:
- evidence packet integrated and green;
- uncertainty presentation integrated and green;
- no automatic threshold;
- no automatic correction;
- no production delivery.


## Go My Way full professional scorer recovery + current-pipeline baseline — 2026-10-03

User directed use of the Go My Way audio/reference assets in `main/public` and clarified that full scorer coverage should exist for bass, lead, and rhythm across measures 1-113.

This was treated as **existing-reference development benchmarking**, not as the new sealed 96-case trust/flag holdout, because Go My Way has extensive prior development exposure.

### Pinned main audio/reference intake

Pinned main commit:
`74dacf322bb979c26a47786e2380c59d2d40e364`

Full-song audio:
- `public/gomywayfullaitest.m4a`
- git blob: `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Full professional PDFs on main:
- bass: `public/Gomywaybassreference.pdf`
  - git blob `9b39fec0e55d60d5ee509863dfc55c1d6bc1f4f4`
  - SHA256 `18e6822394980d22a960a1bd4d923aaddf677f3341b8cc1a2dbb29ea1e8771d0`
- lead: `public/Gomywayleadreference.pdf`
  - git blob `3e5822be398f64b72d806970b27c22503d4e494c`
  - SHA256 `a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56`

The existing professional timing map is explicitly bound to:
`public/gomywayfullaitest.m4a`

### Full scorer history recovery

Initial path-oriented history recovery:
- workflow: `Astra Go My Way Full Scorer Recovery V1`
- run: `37094036423` — success
- artifact: `11263598848`
- digest: `sha256:79e5b9414f4e753dba7eeba8114234728f94618b3f5113d929042fc5c4544b43`

That scan found rhythm-facing full-song references but initially appeared not to find normalized bass/lead scorers.

A deeper provenance scan by frozen PDF/source-set hashes found the older full V154 scorer system under generic research paths:

Bass:
- `research/v154-professional-references/bass-professional-reference-machine-readable.json`
- blob `0773c98556d00837eaea28ee77cfc513498cc21f`
- frozen source-local timing:
  `research/v154-professional-references/bass-source-local-attack-timing.json`
- timing blob `251d4986965c823b288d4a7d0428ec32cc9231cf`

Lead:
- `research/v154-professional-references/lead-professional-reference-machine-readable.json`
- blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`
- frozen source-local timing:
  `research/v154-professional-references/lead-source-local-attack-timing.json`
- timing blob `577a4a07514cdca63d544998f6c5b590ccd2b125`

Shared meter transform:
- `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`
- blob `c7856d2879f4ac1524e68016e979728c92c487fd`
- preserves measure 104 as a real 2/4 bar rather than stretching it.

Provenance recovery workflow:
- run `37094671478` — success
- artifact `11262639696`
- digest `sha256:3f64e1c493788502696d6516b11849290ea2a273531008ea9e1737893f288013`

### Full frozen professional scorer coverage

Rhythm:
- measures 1-16: `analyzer/fixtures/gomyway_professional_intro_reference_v1.json`
- measures 17-113: `public/gomyway-professional-rhythm-reference-17-113.json`
- pitched targets: **971**
- unpitched/dead targets excluded from MIDI score: 71

Bass:
- measures 1-113
- source events: 569
- frozen pitched scorer rows: **547**
- measure 88 timing uncertainty remains excluded through null timing
- event/timing arrays validated with no length mismatches

Lead:
- measures 1-113
- source events: 487
- frozen pitched scorer rows: **447**
- source uncertainty/exclusions preserved, including the measure-39 source-error passage
- event/timing arrays validated with no length mismatches

Total pitched professional targets:
**1,965**

### Current pipeline inference freeze

Implemented:
- `astra_backend/evaluation/evaluate_gomyway_full_song_professional_v1.py`
- `.github/workflows/astra-gomyway-full-song-professional-v1.yml`

Current stack:
- BS-Roformer-SW 6-stem FP16 ONNX, frozen SHA
- Basic Pitch 0.4.0 frozen defaults
- no stem mutation
- no threshold search
- professional references unavailable to inference

Full-song inference run:
- `37094392537` — **success**
- head `b36c99a51fca367d288862dda351515457e6d3af`
- artifact `11262994060`
- digest `sha256:ae73d963ef985beaf26cf9e7c1cbd1780e0bb1e4757e40f6ae3c85c3662045b0`

Frozen prediction counts:
- whole mix: 787
- raw guitar stem: 1065
- raw bass stem: 701

The artifact retains all three prediction streams for scoring-only reuse.

### Full-song rhythm score

971 professional pitched targets.

Whole mix exact MIDI + onset (50 ms):
- TP 18
- precision 2.35%
- recall 1.85%
- F1 **2.07%**

Raw guitar stem:
- TP 36
- precision 3.51%
- recall 3.71%
- F1 **3.61%**

Separator delta:
**+1.53 F1 percentage points**

The separator helps rhythm, but absolute accuracy is poor.

Detailed:
- `docs/astra/GOMYWAY_FULL_SONG_CURRENT_PIPELINE_PROFESSIONAL_V1.md`
- `docs/astra/GOMYWAY_FULL_SONG_CURRENT_PIPELINE_PROFESSIONAL_V1.json`

### Full three-role score

Implemented scoring-only:
- `astra_backend/evaluation/score_gomyway_full_song_three_role_v1.py`
- `.github/workflows/astra-gomyway-three-role-score-v1.yml`

The scoring stage downloads frozen predictions from run `37094392537` and performs no inference.

Two early attempts failed before scoring due accidental inference-module runtime imports. The final scorer was made inference-runtime-free instead of expanding the scoring environment.

Successful run:
- `37095137423`
- head `3b555b10be0b25df207a9178b145d5b9f05efe3b`
- artifact `11264400463`
- digest `sha256:63c86d9ca40af348dd98796c1a08e7946cc473aed7a75793e16abd7cb64a2f75`

Primary metric: one-to-one exact MIDI + onset within fixed 50 ms.

Rhythm / raw generic guitar:
- targets 971
- exact F1 **3.61%**
- pitch-class/onset F1 **7.82%**
- onset-only F1 **25.35%**
- whole-mix exact F1 2.07%
- separator delta +1.53 points

Lead / same raw generic guitar:
- targets 447
- exact F1 **5.98%**
- pitch-class/onset F1 **8.83%**
- onset-only F1 **22.28%**
- whole-mix exact F1 0.99%
- separator delta **+4.99 points**

Bass / raw bass:
- targets 547
- exact F1 **8.21%**
- pitch-class/onset F1 **9.02%**
- onset-only F1 **31.72%**
- whole-mix exact F1 **9.29%**
- separator delta **-1.08 points**

Three-role macro exact MIDI/onset F1:
**5.93%**

Important:
- rhythm and lead share the same generic guitar separator output; this is musical-evidence scoring, not proof of rhythm-vs-lead role separation.
- bass is the only role where the current separator makes exact professional-reference agreement slightly worse than whole-mix Basic Pitch.

Detailed:
- `docs/astra/GOMYWAY_FULL_SONG_THREE_ROLE_SCORE_V1.md`
- `docs/astra/GOMYWAY_FULL_SONG_THREE_ROLE_SCORE_V1.json`

### Three-role professional failure anatomy

Implemented:
- `astra_backend/evaluation/analyze_gomyway_three_role_failure_anatomy_v1.py`
- `.github/workflows/astra-gomyway-three-role-failure-anatomy-v1.yml`

Run:
- `37095293247` — **success**
- head `bedb64979c67a812dfb836d32a592be1ca921080`
- artifact `11264455653`
- digest `sha256:c01753615a1caf6b3294d16321fd1fdbfbde01576fbdd5db114ca1f1de63f1fa`

Across all 1,965 professional targets:
- **60.20%**: no prediction within 50 ms
- **6.67%**: exact MIDI candidate available
- **3.92%**: same pitch class, wrong octave
- **6.11%**: within +/-1-2 semitones
- **11.04%**: fourth/fifth-class relation
- **12.06%**: other wrong pitch only

Rhythm:
- no nearby prediction 58.60%
- exact candidate 3.71%
- professional median MIDI 55
- generic guitar prediction median MIDI 62
- strong high-register/harmonic bias

Lead:
- no nearby prediction 59.06%
- exact candidate 9.84%
- professional median MIDI 64
- generic guitar prediction median MIDI 62
- register is much closer than for rhythm

Bass:
- no nearby prediction 63.99%
- exact candidate 9.32%
- near +/-1-2 semitones 11.15%
- professional median MIDI 38
- bass prediction median MIDI 40
- professional P90 41 vs prediction P90 50

Detailed:
- `docs/astra/GOMYWAY_THREE_ROLE_FAILURE_ANATOMY_V1.md`
- `docs/astra/GOMYWAY_THREE_ROLE_FAILURE_ANATOMY_V1.json`

### Current scientific conclusion

The full real professional scorer changes the priority.

The dominant current end-to-end limitation is **note evidence extraction / transcription**, not duplicate consolidation.

Evidence:
1. most professional attacks have no Basic Pitch event within 50 ms;
2. many nearby events have the wrong pitch/harmonic identity;
3. the generic guitar stream is biased high for rhythm;
4. bass has high-register contamination / near-pitch errors;
5. current separator helps guitar roles but not bass exact score.

Do **not** reopen duplicate consolidation or tune its thresholds from this result.

Also preserve earlier generic front-end decisions:
- Basic Pitch already failed the separately frozen Stage-A advancement gate;
- MR-MT3 failed its frozen program-projection gate;
- prior stop rule says do not simply try a third generic frozen AMT front end on the same development evidence.

### Explicit next resume instruction

**Next GPT-5.6 task:** use the full professional Go My Way scorer as a **development diagnostic**, not a holdout, to design a new reference-blind note-evidence front-end hypothesis that specifically addresses the observed failure modes.

Preferred direction:
1. do not tune Basic Pitch thresholds;
2. do not try another generic off-the-shelf AMT model merely as a third substitution;
3. keep BS-Roformer outputs unchanged;
4. design a candidate-generating note front end that can expose richer pitch evidence at independently detected attacks rather than committing immediately to one pitch;
5. explicitly target:
   - missing attack evidence;
   - rhythm high-register/harmonic bias;
   - fourth/fifth and octave harmonic confusion;
   - bass upper-register contamination / +/-1-2 semitone instability;
6. preserve ambiguity in the evidence packet instead of auto-correcting notes;
7. preregister the extraction algorithm/settings before scoring it on the full professional reference.

A reasonable next experiment is a **reference-blind attack + multi-pitch evidence diagnostic**:
- attack candidates from audio-domain spectral/onset evidence independent of Basic Pitch note acceptance;
- multi-pitch candidates per attack from harmonic-consistency evidence within instrument-specific physical ranges;
- no reference-driven threshold search;
- score candidate availability separately from final one-note decisions.

Go My Way can be used to evaluate this development hypothesis after it is frozen, but any eventual generalization claim still requires genuinely new source-disjoint material under the previously defined holdout protocol.

Keep:
- uncertainty presentation;
- development evidence packet;
- trust/flag holdout protocol;
- no production connection;
- `main` unchanged.


## Go My Way full 113-measure scorer-ready reference correction — 2026-10-03

User clarified that complete scorer references already exist for rhythm, lead, and bass across the full 113-measure song structure.

Confirmed frozen scorer-ready files:
- `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`
  - SHA-256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`
  - 113 measures, 603 events, 946 scored MIDI/step rows
- `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`
  - SHA-256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`
  - 113 measures, 569 source events, 547 scored rows
  - measure 88 explicitly excluded by frozen normalization policy
- `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`
  - SHA-256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`
  - 113 measures, 487 source events, 447 scored rows
  - measures 28 and 39 explicitly excluded by frozen normalization policy

These references were normalized without reading generated candidates; receipts state scoring had not been performed during normalization.

Full-song audio:
- `public/gomywayfullaitest.m4a`
- SHA-256 `60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb`
- timing map: `public/gomyway-professional-timing-map-v2.json`, measures 1..113

### Full-song professional benchmark V2

Added:
- `astra_backend/evaluation/evaluate_gomyway_full_song_professional_v2.py`
- `.github/workflows/astra-gomyway-full-song-professional-v2.yml`

Benchmark contract:
- existing-reference development benchmark, **not** the future sealed 96-case holdout;
- reference-blind inference;
- untouched BS-Roformer guitar/bass outputs;
- frozen Basic Pitch 0.4.0;
- exact MIDI + onset at 50 ms;
- rhythm and lead scored separately against the raw guitar stem;
- combined rhythm+lead reference also scored against the raw guitar stem;
- bass scored against the raw bass stem;
- whole-mix controls and cross-role confusion diagnostics included;
- frozen reference uncertainty exclusions honored;
- no threshold search;
- no audio mutation;
- no automatic correction;
- no `main` modification.

Workflow run started:
- run `37096098308`
- head `627d9ef60ccb4ef455c6be73e3fdb11d85b76c9f`

At this handoff update the run is still in progress.

Do not fall back to the earlier rhythm-only 17..113 benchmark. The scorer-ready 113-measure three-role bundle above is the authoritative scoring target for this development benchmark.


## Go My Way full-song three-role professional benchmark V2 — final result 2026-10-03

User correctly clarified that a complete scorer-ready professional reference already exists for all three roles across the 113-measure song structure.

### Final frozen scorer-ready bundle

Canonical V154 references:
- Rhythm: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`
  - SHA-256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`
  - 113-measure contract, **946** scored note rows
- Lead: `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`
  - SHA-256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`
  - **447** scored rows
  - frozen exclusions: measures 28, 39
- Bass: `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`
  - SHA-256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`
  - **547** scored rows
  - frozen exclusion: measure 88

Combined rhythm+lead reference rows: **1393**.

The rhythm equivalence audit
`research/v154-professional-references/rhythm-scorer-ready-equivalence-audit.json`
is PASS and proves the two final V154 rhythm scorer-ready forms are exact normalized multiset equivalents at 946 rows. The older 971-row intro+17..113 normalization should not be used as the canonical V154 scorer-ready rhythm bundle.

### Fresh current-pipeline run

Implementation:
- `astra_backend/evaluation/evaluate_gomyway_full_song_professional_v2.py`
- `.github/workflows/astra-gomyway-full-song-professional-v2.yml`

Source:
- `public/gomywayfullaitest.m4a`
- repository Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Successful run:
- run `37096244645`
- head `15474cd6cdff2f9792950d72a02508915484e5cc`
- artifact `11264986579`
- digest `sha256:a8997135b0251aa8f4ed8f98b5c91650209f50840b9b6964b73b0e0f85b7e48f`
- runtime **877.64 s**

Inference remained reference-blind:
- raw BS-Roformer guitar/bass stems
- frozen Basic Pitch 0.4.0
- no cleanup
- no threshold search
- no consolidation
- no automatic correction

Fresh exact-MIDI + 50 ms absolute-time scores:

**Rhythm from raw guitar stem**
- 946 targets
- TP 56
- precision 5.47%
- recall 5.92%
- F1 **5.69%**
- whole-mix F1 3.04%

**Lead from raw guitar stem**
- 447 targets
- TP 45
- precision 4.48%
- recall 10.07%
- F1 **6.20%**
- whole-mix F1 1.00%

**Combined rhythm+lead from raw guitar stem**
- 1393 targets
- TP 96
- precision 9.55%
- recall 6.89%
- F1 **8.01%**
- whole-mix F1 2.89%

**Bass from raw bass stem**
- 547 targets
- TP 50
- precision 7.29%
- recall 9.14%
- F1 **8.11%**
- whole-mix F1 9.05%

Role-confusion diagnostics:
- bass stem vs rhythm F1 2.56%
- bass stem vs lead F1 0.18%
- guitar stem vs bass F1 1.66%

### What this establishes

The current separator materially improves the generic guitar transcription compared with whole-mix Basic Pitch, especially for lead-like content.

However, the absolute professional-reference agreement remains very low. Bass separation does not improve the Basic Pitch score on this song.

This confirms that the main downstream bottleneck is still note/structure recognition rather than simply lack of professional reference coverage.

### Canonical V154 scorer boundary

The exact frozen canonical scorer is:
`validation/v154_cpu_multitrack/score_frontend_reference.py`

Git blob:
`9644e65719fbd361a9b39778ae9950c5e983e855`

Its primary metric is exact MIDI within ±0.5 **measure-grid steps**. It assumes the generated candidate already owns an independently generated measure/step grid.

The current BS-Roformer + Basic Pitch benchmark produces absolute-time events only.

Do **not** convert those timestamps to measure/step coordinates using the professional timing map and then claim `referenceRead=false`. That would leak the professional reference timebase into generated-candidate structure.

Historical V154 candidate context only:
- combined-guitar canonical primary F1: 4.92%
- bass canonical primary F1: 11.17%

Those are not directly comparable to the V2 direct-time results because they use a different generated architecture / coordinate contract.

Detailed final records:
- `docs/astra/GOMYWAY_FULL_SONG_PROFESSIONAL_V2_RESULT.md`
- `docs/astra/GOMYWAY_FULL_SONG_PROFESSIONAL_V2_RESULT.json`

### Explicit next resume instruction

**Next GPT-5.6 task:** focus on a **reference-independent full-song musical structure/timebase diagnostic** for `public/gomywayfullaitest.m4a`, before attempting another canonical V154 score.

Goal:
produce measure/beat/step coordinates from audio only, with no professional-reference timing map available to candidate generation.

Requirements:
1. inspect existing reference-blind structure/grid code and any previously generated Go My Way structure evidence;
2. do not read scorer-ready note rows or professional timing values while generating a candidate grid;
3. freeze one candidate structure/grid output first;
4. only after it is frozen, compare its measure/downbeat/tempo alignment diagnostically against the professional timing map;
5. do not tune the same candidate after seeing that comparison;
6. if the reference-independent grid is sufficiently coherent, use that grid in a future candidate payload compatible with the canonical V154 scorer;
7. keep raw Basic Pitch settings, separator model, all uncertainty contracts, and `main` unchanged.

The full three-role scorer coverage problem is solved. The next architecture gap is the candidate's own trustworthy musical timebase plus stronger transcription evidence.


## Go My Way Full-Song Professional Benchmark — 2026-10-03

User explicitly redirected the next development benchmark to the existing Go My Way full-song material and professional references.

### Source/reference inventory now confirmed

Pinned `main` head used for source verification:

`74dacf322bb979c26a47786e2380c59d2d40e364`

Full-song audio selected:

- `main/public/gomywayfullaitest.m4a`
- Git blob: `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Authoritative professional references confirmed on `main/public`:

- bass: `public/Gomywaybassreference.pdf`
  - Git blob: `9b39fec0e55d60d5ee509863dfc55c1d6bc1f4f4`
  - SHA-256 already recorded in Astra intake: `18e6822394980d22a960a1bd4d923aaddf677f3341b8cc1a2dbb29ea1e8771d0`
  - measures 1–113
- lead: `public/Gomywayleadreference.pdf`
  - Git blob: `3e5822be398f64b72d806970b27c22503d4e494c`
  - SHA-256 already recorded in Astra intake: `a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56`
  - measures 1–113

Rhythm full-song scoring source is available on `astra-work` as:
- intro measures 1–16:
  - `analyzer/fixtures/gomyway_professional_intro_reference_v1.json`
- human-approved measures 17–113:
  - `public/gomyway-professional-rhythm-reference-17-113.json`
- timing:
  - `public/gomyway-professional-timing-map-v2.json`

Important distinction:
- rhythm already has machine-readable note-level scoring data across the full song when intro 1–16 and approved 17–113 are joined;
- bass and lead have complete authoritative professional PDFs for 1–113, but equivalent normalized machine-readable note-level scorer JSONs were not found in current/reachable Git history.

### Historical scorer recovery

Implemented:
- `astra_backend/evaluation/recover_gomyway_full_scorer_history_v1.py`
- `.github/workflows/astra-gomyway-full-scorer-recovery-v1.yml`

Successful recovery run:
- run `37094036423`
- artifact `11263598848`
- digest `sha256:79e5b9414f4e753dba7eeba8114234728f94618b3f5113d929042fc5c4544b43`

Scan summary:
- reachable Git objects: 54,116
- relevant historical Go My Way JSON paths: 2,888
- candidate scorer/reference JSONs: 2,861
- full/113-ish candidates: 95

Key result:
- true full-song rhythm reference found;
- no equivalent normalized full-song bass/lead note-label scorer found in reachable history.

Do not treat this as missing source coverage: bass/lead professional source coverage is complete in the PDFs. Only machine normalization is missing.

### Full-song current-pipeline benchmark V1

Implemented:
- `astra_backend/evaluation/evaluate_gomyway_full_song_professional_v1.py`
- `.github/workflows/astra-gomyway-full-song-professional-v1.yml`

Current benchmark definition:

Inference:
1. pinned `main/public/gomywayfullaitest.m4a`
2. decoded to 44.1 kHz stereo float WAV
3. untouched frozen BS-Roformer-SW 6-stem FP16 ONNX
4. frozen Basic Pitch 0.4.0 defaults
5. collect whole-mix, raw-guitar-stem, and raw-bass-stem note streams

Scoring V1:
- rhythm measures 1–113 only
- exact MIDI + onset
- one-to-one matching
- fixed 50 ms onset tolerance
- no alignment search
- no threshold search
- no reference access during inference
- professional timing map used only after inference for scoring

The benchmark also caches:
- whole-mix notes
- raw guitar notes
- raw bass notes

This is deliberate so bass and lead can be scored later against their normalized professional references without rerunning separator or Basic Pitch.

Bass/lead in V1:
- full professional PDFs are hash-locked and bound to the run;
- prediction streams are cached;
- score remains intentionally absent until PDF note labels are machine-normalized.

Current GitHub Actions run:
- workflow: `Astra Go My Way Full Song Professional Benchmark V1`
- run ID: `37094392537`
- status at handoff time: **in progress**
- source/reference identity verification passed
- environment installation had started
- full benchmark result not yet available at the time this handoff was written

### Explicit next resume instruction

**Next GPT-5.6 task: resume from GitHub Actions run `37094392537`.**

1. Check whether run `37094392537` completed.
2. If green:
   - inspect the uploaded benchmark artifact;
   - record:
     - whole-mix event count;
     - raw-guitar event count;
     - raw-bass event count;
     - whole-mix rhythm precision/recall/F1;
     - raw-guitar rhythm precision/recall/F1;
     - separator F1 delta vs whole mix;
     - mean absolute onset error;
     - strongest/weakest measures;
   - preserve the full prediction cache for later bass/lead scoring;
   - commit a result record under `docs/astra/`.
3. If failed:
   - inspect the failed step/log;
   - fix only the runtime/scoring implementation defect;
   - do not alter:
     - audio identity;
     - BS-Roformer model identity;
     - Basic Pitch settings;
     - professional reference identities;
     - 50 ms tolerance;
     - scoring semantics.

4. After the rhythm full-song result is safely recorded, start **Bass/Lead Professional PDF Normalization V1**:
   - source authority must remain the two pinned `main/public` PDFs above;
   - reuse existing PDF raster/localization machinery where practical;
   - do not infer labels from model output;
   - do not copy candidate predictions into the reference;
   - preserve measures 1–113, including printed rests and known annotations;
   - normalize bass and lead into machine-readable measure/event structures;
   - record PDF SHA-256 and provenance in every normalized output.

5. Once bass/lead normalized references exist:
   - score the already-cached raw bass stream against bass 1–113;
   - score the already-cached raw guitar stream against lead 1–113;
   - keep rhythm, lead, and bass as separate role scores;
   - do not collapse them into a single trust threshold.

6. Do not:
   - call this a sealed holdout;
   - use Go My Way to satisfy the 96-case trust/flag holdout protocol;
   - tune thresholds from the professional references;
   - alter note events to improve the score;
   - modify production;
   - modify `main`.

### Current scientific interpretation boundary

Go My Way is an **existing-reference development benchmark**, not a fresh holdout.

Its purpose now is to answer the practical product question:

> How close is the current separator + transcription stack to a full professional tab across rhythm, lead, and bass?

Use the professional references strictly for scoring and error analysis, not for hidden correction of the model output.


## Go My Way reference-independent full-song timebase V1 — launched 2026-10-03

Continued from the full-song three-role professional benchmark V2 resume instruction.

Implemented:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v1.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v1.yml`

Design boundary:
- candidate generation reads decoded `public/gomywayfullaitest.m4a` audio only;
- generation reuses the existing V143 reference-free timing estimator plus reference-free beat-grid repair;
- candidate uses an explicit 4/4 / 16-step measure-grid assumption from the existing adapter;
- no professional timing map or scorer-ready note rows are read by the generation mode;
- candidate JSON is SHA-256 frozen and uploaded in the first Actions job;
- a separate dependent job verifies the frozen bytes before reading `public/gomyway-professional-timing-map-v2.json`;
- professional comparison is diagnostic only and cannot rewrite the candidate;
- integer measure-shift search, if reported, is post-freeze diagnostic alignment only;
- the candidate remains unchanged after the comparison;
- raw Basic Pitch, separator identities and `main` are untouched.

Commits:
- implementation: `250f95224ce52b2c3fe012be6043024cdcd2f790`
- initial workflow: `fabad18170f46697394deffcc7a882cd2f5c55d7`
- runtime-only ffmpeg fix: `0c5b3b7ff4bb73fec62899661fba29f6e98a75a7`

First workflow run:
- run `37121531152`
- result: FAILED before candidate generation because `ffmpeg` was absent on the runner;
- source Git-blob identity check passed before that failure;
- no candidate grid was generated;
- no professional timing comparison was run.

Runtime-only correction:
- workflow now installs `ffmpeg`;
- no audio, estimator, grid or comparison semantics changed.

Corrected workflow run:
- run `37121584921`
- head `0c5b3b7ff4bb73fec62899661fba29f6e98a75a7`
- status at this handoff update: QUEUED.

### Exact next resume instruction

Resume from Actions run `37121584921`.

1. If the blind-grid job succeeds, record the frozen candidate artifact ID/digest and candidate JSON SHA-256.
2. Record candidate tempo, beat count, measure count, first-beat-in-measure, beat/bar confidence and beat-interval summary.
3. Then inspect the dependent post-freeze professional comparison result:
   - same-numbering error;
   - best diagnostic integer measure shift;
   - median/mean absolute downbeat error;
   - signed drift across the song;
   - effect of the professional 2/4 measure 104 against the candidate's intentionally reference-independent 4/4-only assumption.
4. Do not retune or regenerate the same candidate after seeing the professional comparison.
5. If the reference-independent grid is coherent enough for canonical candidate coordinates, freeze that conclusion before integrating note events.
6. If it is not coherent, diagnose the structural failure from the frozen candidate only; do not use the professional timing map to repair it.
7. Keep `main` unchanged and preserve the full three-role professional scorer bundle as scoring-only evidence.


### Provenance hardening update — 2026-10-03

Before accepting the queued run as the frozen candidate source, the workflow checkout was tightened from the moving branch ref to the immutable trigger SHA (`${{ github.sha }}`) in both jobs.

Commit:
- `82ae2166ad2ea02afe725d07cfcf455d30ecf766`

New authoritative run:
- `37121658447`
- head: `82ae2166ad2ea02afe725d07cfcf455d30ecf766`
- status at this update: QUEUED.

Run `37121584921` is superseded for scientific provenance because its workflow checked out the moving branch name. Do not use it as the canonical frozen candidate even if it later turns green.

**Resume from run `37121658447`.**


## Go My Way reference-independent full-song timebase V1 — authoritative green result 2026-10-03

Authoritative workflow run:
- run `37122524144`
- head: `65434c28830f0e23962d30751c95fdd31cc8e142`
- result: GREEN / both jobs successful.

Runtime-only fixes between the first launch and the green result:
- `8fe4307085d7f9447b65bba47b6ce84059757830` — checksum artifact path;
- `4b40cf9ec1161b9b236d111861abbaedea2f6b18` — comparison dependency attempt;
- `c233ea2bbd1d8921b1734542d430c1b4616b1979` — fix exact comparison dependency install;
- `22554b8ecc64449bf6f157f2d670dbb2feed1387` — install full comparison imports;
- `65434c28830f0e23962d30751c95fdd31cc8e142` — verify copied frozen grid from the output directory.

These changes did not alter the audio, estimator, repair logic, meter assumption, subdivision semantics, professional timing map, or comparison metric definitions.

Frozen candidate artifact:
- artifact name: `gomyway-reference-independent-grid-v1`
- artifact id: `11273731974`
- artifact digest: `sha256:863ff326b63dc7323ec51044cceae0406b08c4f191e1bcae756dd40877bdb6ef`
- candidate JSON SHA-256: `18d8105a1325c23f7b36af868c7ac920818f54d577a8ee921cfed3f208a85cb5`

Final result artifact:
- artifact name: `gomyway-reference-independent-timebase-v1-result`
- artifact id: `11274325986`
- artifact digest: `sha256:d11685951a92d8685b6960381b60a421a16ce5f8d567041c6d446dd75a7dc4eb`

Authoritative post-freeze diagnostic comparison:
- candidate tempo: `129.19921875 BPM`;
- best integer measure shift for diagnosis only: `-1`;
- compared pair count: `112`;
- median absolute downbeat error: `1.7427739229025008 s`;
- mean absolute downbeat error: `1.8156368385568522 s`;
- signed drift slope: `0.06570527168881132 s/reference-measure`;
- predicted drift across 113 measures: `7.358990429146868 s`.

Scientific interpretation:
- the reference-independent grid is not coherent enough yet to serve as the canonical measure/step coordinate system for V154 professional-reference scoring;
- the tempo estimate is relatively close in broad terms, but the measure alignment error and accumulated drift are too large for precise tab scoring;
- the diagnostic best shift of -1 indicates an initial measure-phase/anchor mismatch, and the continuing positive drift shows that this is not only a fixed offset problem;
- because the candidate intentionally assumes 4/4 throughout while the professional map contains a 2/4 measure at 104, some late-song divergence is expected, but the observed drift is already too large to attribute the structural failure only to measure 104;
- therefore do NOT map note events into canonical V154 coordinates using this V1 grid.

Critical integrity rule:
- do not tune or regenerate this V1 candidate from the professional timing comparison;
- the frozen V1 remains the evidence for this diagnostic;
- any structural improvement must be a separately versioned V2 candidate generated reference-blind, with its design fixed before comparison.

### Exact next resume instruction

Next task: build a **reference-independent timebase V2** that addresses the structural failure without reading or conditioning on the professional timing map.

Preferred direction:
1. preserve the same full-song audio identity and provenance;
2. keep professional references completely out of candidate generation;
3. improve audio-only tempo/beat/downbeat structure with a stronger long-range method, especially:
   - robust global tempo tracking;
   - downbeat/bar-phase stability;
   - handling of tempo drift or local tempo variation;
   - detection of non-4/4 structural exceptions from audio if possible, without knowing where they occur;
4. freeze the V2 candidate before any professional comparison;
5. compare V2 using the same diagnostic metrics and do not post-hoc repair it;
6. only if V2 becomes sufficiently coherent should its frozen grid be used for V154 note-event coordinate mapping;
7. keep `main` unchanged and do not alter Basic Pitch/separator settings as part of this timebase task.

Do not use the professional timing map as a repair target. It remains scoring/diagnostic evidence only.


## Go My Way reference-independent full-song timebase V2 — launched 2026-10-03

Implemented:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v2.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v2.yml`

Purpose:
- incorporate the existing audio-separation and fixed soft bleed-cleanup work into the timebase experiment without allowing professional-reference conditioning.

Reference-blind V2 candidate inputs frozen before professional comparison:
1. `raw_mix`
2. `raw_guitar`
3. `raw_drums`
4. `raw_guitar_drums_sum`
5. `cleaned_guitar`
6. `cleaned_drums`
7. `cleaned_guitar_drums_sum`

Important cleanup evidence boundary:
- fixed soft cleanup configuration remains `n_fft=2048, hop=512, power=2.0, competition=0.50, floor_gain=0.60`;
- that configuration previously passed only the deterministic synthetic injected-bleed unit test;
- recognizer-gated cleanup V1 applied cleanup to zero stems and therefore did not establish real-separator improvement;
- V2 cleanup variants are experimental timing inputs, not trusted corrections.

V2 primary-selection rule:
- chosen BEFORE reference access;
- maximize `barConfidence`, then `beatConfidence`, then `beatCount`;
- professional timing map cannot select or alter the primary candidate.

Provenance:
- source audio remains `public/gomywayfullaitest.m4a`, expected Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`;
- separator remains BS-Roformer-SW 6-stem FP16 ONNX, SHA-256 `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`;
- both workflow jobs checkout immutable `${{ github.sha }}`;
- professional timing map is opened only in the dependent post-freeze comparison job;
- comparison cannot rewrite the V2 bundle.

Commits:
- V2 script: `5c0c56057da4121ee2a7a0b734d9950609aee884`
- V2 workflow launch: `307715ce9874939bae6a263fe22c5a7969b1cb66`

Authoritative V2 run:
- run `37123049554`
- head `307715ce9874939bae6a263fe22c5a7969b1cb66`
- status at this update: IN PROGRESS
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37123049554

### Exact next resume instruction

Resume from run `37123049554`.

1. If the freeze job succeeds, record:
   - frozen bundle artifact ID/digest;
   - bundle SHA-256;
   - audio-only-selected primary candidate;
   - tempo, beatConfidence, barConfidence, beat count and measure count for all seven candidates.
2. If the comparison job succeeds, record for every candidate:
   - same-numbering error;
   - best diagnostic integer shift;
   - median/mean absolute error;
   - signed drift across 113 measures.
3. Compare raw vs cleaned variants descriptively, but do not retroactively change V2 or its frozen primary candidate.
4. Specifically determine whether cleanup improves timing stability relative to the corresponding raw stem.
5. Do not use the professional timing map to tune cleanup settings, separator output, estimator settings, meter assumptions, or primary selection.
6. If V2 is still structurally incoherent, diagnose the failure and version any future approach separately as V3.
7. Keep `main` unchanged.


## Go My Way reference-independent full-song timebase V2 — authoritative green result 2026-10-03

Authoritative workflow run:
- run `37123049554`
- head `307715ce9874939bae6a263fe22c5a7969b1cb66`
- both jobs: GREEN.

Frozen artifact:
- name: `gomyway-reference-independent-timebase-v2-frozen`
- id: `11273899364`
- digest: `sha256:ae72a72a40c2313694e440c81c50d76cf79643bcf285a8a5d1be0b764bfd8a2b`
- frozen bundle SHA-256: `4961631eaf3e8fdf16d81411bb8c3554d0dcbaf240433cdebf70802a9c57bf36`

Result artifact:
- name: `gomyway-reference-independent-timebase-v2-result`
- id: `11274123598`
- digest: `sha256:6b083dbf96ae96e94823fafa7cf4fdeb4e8a127421a064560b85e6aa87313043`

Frozen primary candidate chosen before reference access:
- `raw_drums`
- tempo: `129.19921875 BPM`
- beat confidence: `0.7315978626924113`
- bar confidence: `0.20601149685263945`
- selection was audio-only by max barConfidence, then beatConfidence, then beatCount.

Audio-side candidate summary:
- raw_mix: tempo 129.19921875, beatConfidence 0.7243903427458401, barConfidence 0.0
- raw_guitar: tempo 215.33203125, beatConfidence 0.45773511983452364, barConfidence 0.0
- raw_drums: tempo 129.19921875, beatConfidence 0.7315978626924113, barConfidence 0.20601149685263945
- raw_guitar_drums_sum: tempo 129.19921875, beatConfidence 0.7338699974395781, barConfidence 0.1384239426979097
- cleaned_guitar: tempo 215.33203125, beatConfidence 0.46439992618328796, barConfidence 0.0
- cleaned_drums: tempo 129.19921875, beatConfidence 0.7293679193170994, barConfidence 0.0
- cleaned_guitar_drums_sum: tempo 129.19921875, beatConfidence 0.7299707827777643, barConfidence 0.0

Post-freeze professional diagnostics:
- raw_mix: best shift -1; median abs error 1.7427739229025008 s; mean abs error 1.8156368385568522 s; predicted drift 7.358990429146868 s.
- raw_guitar: best shift -8; median abs error 34.84675199546484 s; mean abs error 34.76997626263721 s; predicted drift -75.48155181340837 s.
- raw_drums: best shift -2; median abs error 1.678168631519302 s; mean abs error 1.7082971722516207 s; predicted drift 7.163902921890054 s.
- raw_guitar_drums_sum: best shift -1; median abs error 1.7652629580498882 s; mean abs error 1.8510887336005837 s; predicted drift 7.388452725107266 s.
- cleaned_guitar: best shift -8; median abs error 32.65246628117913 s; mean abs error 33.37807611614793 s; predicted drift -72.75623130607177 s.
- cleaned_drums: best shift -1; median abs error 1.5562638696145186 s; mean abs error 1.7029214056857314 s; predicted drift 7.090925984769514 s.
- cleaned_guitar_drums_sum: best shift -1; median abs error 1.7652629580498882 s; mean abs error 1.851905060131196 s; predicted drift 7.3902083836012284 s.

Cleanup interpretation:
- cleanup did NOT solve the timebase problem;
- cleaned drums improved median absolute error vs raw drums by about 0.122 s and mean absolute error by about 0.005 s;
- however cleaned drums lost the only nonzero raw-drum bar confidence (0.206 -> 0.0) and still accumulated ~7.09 s drift;
- raw/cleaned guitar remained grossly octave/tempo-confused at ~215.33 BPM;
- guitar+drums cleanup was effectively neutral/slightly worse.
- Therefore do not promote the cleanup output as a trusted timebase source and do not tune cleanup settings against the professional map.

Scientific conclusion:
- V2 is still structurally incoherent for canonical V154 measure/step coordinates.
- The main unresolved issue is long-range tempo/downbeat structure, not stem cleanliness alone.
- The raw drums candidate remains useful evidence because the audio-only selection rule chose it prospectively and it was slightly better than raw mix, but its ~7.16 s full-song drift is still far too large.

### Exact next resume instruction

Build a separately versioned **reference-independent timebase V3** focused on long-range structure, not cleanup parameter tuning.

Required boundaries:
1. keep the same source audio identity;
2. professional timing map must remain completely absent from candidate generation and model/parameter selection;
3. do not retune the V2 cleanup configuration using these results;
4. use rhythm-bearing audio (raw drums is the strongest prospective V2 source) as one input, but preserve raw mix as a control;
5. replace or augment the V143 local beat repair with a long-range method that can:
   - estimate tempo trajectory across the whole song rather than one static BPM;
   - stabilize downbeat/bar phase over long spans;
   - detect/reset phase around structural transitions;
   - detect meter exceptions from audio where possible rather than assuming 4/4 globally;
6. freeze every V3 candidate before professional comparison;
7. compare with the same diagnostic metrics and never post-hoc repair the frozen candidate;
8. only integrate note events into V154 coordinates if V3 becomes materially coherent;
9. keep `main` unchanged.


## Go My Way reference-independent full-song timebase V3 — launched 2026-10-03

Goal:
- remove the major long-range timing drift before doing more guitar/bass note work;
- test whether accurate beat timing can provide a stable coordinate system for later transcription.

Key V3 change:
- the V143 estimator quantizes tempo to an integer STFT-frame lag, which can create meaningful BPM error and seconds of accumulated drift over a full song;
- V3 replaces that dependency with long-range beat tracking via pinned `librosa==0.10.2.post1`.

Reference-blind V3 candidates:
- `raw_drums_t100`
- `raw_drums_t300`
- `raw_mix_t100`
- `raw_mix_t300`

Generation boundaries:
- source audio unchanged;
- fixed BS-Roformer raw drums used as the primary rhythm-bearing source family;
- raw mix retained as control;
- no professional timing map or scorer rows are read during candidate generation;
- primary candidate is selected before reference access using audio-only beat activity, interval regularity, and bar confidence;
- all candidates remain provisionally 4/4 for measure labeling.

New diagnostic:
- post-freeze comparison now includes beat-level nearest-reference timing errors in addition to measure-start alignment;
- this separates true beat tracking quality from bar-phase/measure-number errors.

Files:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v3.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v3.yml`

Commits:
- V3 implementation: `a36e52767e6deb42a429794d989c129eb0497aaf`
- V3 workflow launch: `cf2fa794a5a8d92dd313c794ee8bf81772898247`

Authoritative V3 run:
- run `37124430872`
- head `cf2fa794a5a8d92dd313c794ee8bf81772898247`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37124430872

### Exact next resume instruction

Resume from run `37124430872`.

1. If freeze succeeds, record:
   - frozen artifact id/digest and JSON SHA-256;
   - prospectively selected primary candidate;
   - tracked median BPM, quality score, bar confidence, beat count for all four candidates.
2. If comparison succeeds, record for each candidate:
   - beat-level median/mean/p95 absolute error;
   - measure best shift and median/mean absolute error;
   - predicted drift across 113 measures.
3. Determine first whether beat tracking itself is materially accurate.
4. If beat-level timing is strong but measure alignment remains weak, focus V4 specifically on downbeat/bar phase and meter exception detection rather than changing beat tracking.
5. If beat-level timing is still drifting, improve long-range beat trajectory in a separately frozen V4.
6. Do not use the professional map to alter V3 candidates.
7. Only after timing is coherent should guitar/bass events be remapped and rescored.
8. Keep `main` unchanged.


## Go My Way reference-independent full-song timebase V3 — authoritative green result 2026-10-03

Authoritative workflow run:
- run `37124430872`
- both jobs GREEN.

Frozen artifact:
- id: `11275385622`
- name: `gomyway-reference-independent-timebase-v3-frozen`
- digest: `sha256:fe96731320da6e2a401cb7022cd3cd622e7b1ac8fee559a35202580d833325bc`
- frozen bundle SHA-256: `a100b26a8cdb23f684973c741e82488262378abee5019122b98f8ca235536d65`

Result artifact:
- id: `11275260248`
- name: `gomyway-reference-independent-timebase-v3-result`
- digest: `sha256:a302b60997cd18fb817567a31532e0195241bb415533d916cf1de0eda1377ca3`

Prospectively selected primary:
- `raw_drums_t300`
- median tracked tempo: `129.19921875 BPM`
- audio-only quality score: `0.7815096352500305`
- bar confidence: `0.06693575596776007`
- beat count: `452`

Beat-level post-freeze diagnostic for primary:
- pair count: 452
- median absolute error: `0.12508844160997512 s`
- mean absolute error: `0.23974702913731824 s`
- p95 absolute error: `0.22184693599774158 s`
- mean signed error: `-0.10191760701242293 s`

Measure-level post-freeze diagnostic for primary:
- best integer shift: -1
- median absolute error: `1.840728310657596 s`
- mean absolute error: `2.013082533001295 s`
- predicted drift across 113 measures: `7.899588849492435 s`

V3 interpretation:
- Beat placement is now materially closer than V1/V2 measure timing, with ~125 ms median nearest-reference beat error.
- However long-range tempo remains too slow and accumulates ~7.9 s of drift.
- This establishes that the next bottleneck is continuous/global tempo accuracy and sub-frame beat placement, not cleanup.
- The measure/bar layer should not yet be repaired while the beat trajectory itself has this systematic drift.

### Exact next resume instruction

Build **reference-independent timebase V4** focused narrowly on continuous tempo and sub-frame beat timing.

Required direction:
1. keep raw drums as the primary rhythm-bearing source family and raw mix as a control;
2. estimate tempo continuously rather than selecting an integer frame-lag/bin;
3. use higher-resolution onset analysis and/or quadratic interpolation around autocorrelation/periodicity peaks;
4. optimize beat phase/period against audio onset evidence only;
5. allow slowly varying beat period if justified by audio;
6. freeze candidate(s) and audio-only selection before reference access;
7. add beat-error drift diagnostics that show early/middle/late behavior;
8. do not change cleanup or note recognition;
9. do not map guitar/bass events until the timebase no longer has material systematic drift;
10. keep `main` unchanged.


## Go My Way reference-independent full-song timebase V4 — launched 2026-10-03

Goal:
- eliminate the systematic long-range beat drift observed in V3 before any further guitar/bass remapping.

V3 diagnosis that motivated V4:
- V3 primary `raw_drums_t300` achieved ~0.125 s median beat error, but still accumulated ~7.90 s drift across the song;
- the remaining issue is therefore continuous tempo accuracy / beat-period quantization rather than stem cleanup.

V4 design:
- high-resolution onset analysis at 22.05 kHz with 64-sample hop (~2.90 ms);
- fractional autocorrelation lag using parabolic interpolation instead of integer frame-lag tempo;
- audio-only beat-phase optimization at 1 ms offset resolution;
- both constant-tempo and slowly varying local-tempo candidates;
- raw drums primary source family, raw mix control;
- no cleanup changes;
- no professional timing/reference access during generation.

Reference-blind V4 candidates:
- `raw_drums_global`
- `raw_drums_local`
- `raw_mix_global`
- `raw_mix_local`

New post-freeze diagnostic:
- sequence-aligned beat-index shift diagnostic, not just nearest-reference beat matching;
- reports median/mean/p95 beat error and predicted full-song beat drift;
- measure alignment remains a separate diagnostic layer.

Files:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v4.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v4.yml`

Commits:
- V4 implementation: `5fab5e045b2f09b5202e997f31ef7afcf20019cf`
- V4 workflow launch: `7b8b4cc545e9d6e7933c3366fda02271c0e40ee8`

Authoritative V4 run:
- run `37125736569`
- head `7b8b4cc545e9d6e7933c3366fda02271c0e40ee8`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37125736569

### Exact next resume instruction

Resume from run `37125736569`.

1. If freeze succeeds, record:
   - frozen artifact id/digest and JSON SHA-256;
   - primary candidate chosen before reference access;
   - global fractional BPM, local BPM summary, quality score, bar confidence, beat count for all candidates.
2. If comparison succeeds, prioritize the sequence-aligned beat diagnostics:
   - best beat-index shift;
   - median/mean/p95 beat error;
   - seconds/reference-beat slope;
   - predicted full-song beat drift.
3. Only after beat drift is materially removed should measure/downbeat/meter labeling become the next target.
4. Do not change cleanup, separator, or note-recognition settings as part of this run.
5. Do not remap guitar/bass events until the beat trajectory itself is coherent.
6. Keep `main` unchanged.


## Go My Way reference-independent full-song timebase V4 — authoritative green result 2026-10-03

Authoritative workflow run:
- run `37125736569`
- both jobs GREEN.

Frozen artifact:
- id: `11275556266`
- name: `gomyway-reference-independent-timebase-v4-frozen`
- digest: `sha256:2143b54495c70f83c8718da97b0b6a4e0bb5f9acb0d7b982ec93ab90b3f472ed`
- frozen bundle SHA-256: `2d395cb0cebfc0235beccdca04021ad12a20c55bc2652889e65af48ecca5a4ca`

Result artifact:
- id: `11275532312`
- name: `gomyway-reference-independent-timebase-v4-result`
- digest: `sha256:32a7b4e0df3c450ed366e1193241192cb35fd1c25be285410447a4230ad60fb1`

Prospectively selected primary:
- `raw_mix_global`
- global fractional tempo: `129.25244238074436 BPM`
- audio-only quality score: `0.4687510768030706`
- bar confidence: `0.23848879557197833`
- beat count: `456`

Post-freeze sequence-aligned beat diagnostic for primary:
- best beat-index shift: `-11`
- pair count: `445`
- median absolute beat error: `1.7574305573885152 s`
- mean absolute beat error: `2.165800078740932 s`
- p95 absolute beat error: `4.850131856087289 s`
- seconds/reference-beat drift slope: `0.0157773696254933`
- predicted full-song beat drift: `7.084038961846491 s`

Measure diagnostic for primary:
- best measure shift: `-3`
- median absolute error: `1.7670655995928612 s`
- mean absolute error: `1.914857025537496 s`
- predicted drift across 113 measures: `7.425204115662205 s`

Other V4 candidates:
- raw_drums_global: 128.7583 BPM; predicted beat drift 7.8840 s
- raw_drums_local: 128.7583 BPM; predicted beat drift 7.3957 s
- raw_mix_local: 129.2524 BPM; predicted beat drift 6.9128 s

Scientific interpretation:
- increasing analysis resolution and using fractional autocorrelation did not remove the systematic drift;
- therefore the dominant error is not merely integer-frame tempo quantization;
- the tracker is consistently selecting a slower periodic interpretation around 129 BPM;
- V4 candidates also contain 454–456 beats, indicating likely beat insertion/count/phase interpretation errors in addition to tempo mismatch;
- do not proceed to guitar/bass remapping yet.

### Exact next resume instruction

Build **reference-independent timebase V5** around cross-source beat-lattice consensus rather than single-envelope autocorrelation.

Required direction:
1. keep professional reference completely absent from generation and candidate selection;
2. use both raw drums and raw mix onset evidence;
3. extract high-confidence transient peaks independently from both sources;
4. construct a continuous candidate beat lattice by jointly optimizing:
   - onset support in drums;
   - onset support in mix;
   - cross-source peak agreement;
   - interval regularity;
   - penalties for inserted/missing beats;
5. search continuous tempo/phase hypotheses broadly and allow slow local tempo evolution;
6. favor hypotheses whose predicted beat positions are independently supported by both sources over hypotheses that merely maximize autocorrelation;
7. freeze all V5 candidates and the primary before any reference read;
8. post-freeze, report beat-count difference, early/middle/late signed error, sequence-aligned drift, and measure diagnostics;
9. do not tune cleanup, separator, or guitar/bass recognizer during this timing phase;
10. keep `main` unchanged.


## Go My Way reference-independent full-song timebase V5 — launched 2026-10-03

Goal:
- reject the recurring ~129 BPM false periodic interpretation that survived V1–V4;
- derive timing from cross-source transient consensus rather than single-envelope autocorrelation.

V5 design:
- high-resolution onset envelopes from raw drums and raw mix;
- continuous global BPM search from 100–160 BPM;
- coarse 0.10 BPM search followed by 0.005 BPM refinement;
- beat phase optimized from joint transient support;
- lattice score rewards:
  - drum onset support;
  - mix onset support;
  - cross-source agreement;
  - lower fraction of weakly supported beat positions;
- separate global and slowly varying local-tempo candidates;
- local tempo profile constrained near the global consensus and smoothed generically;
- professional timing/reference data absent from generation and primary selection.

Reference-blind candidates:
- `consensus_global`
- `consensus_local`

Post-freeze diagnostics:
- candidate vs reference beat-count difference;
- best beat-index shift;
- median/mean/p95 beat error;
- beat-drift slope and predicted full-song drift;
- early/middle/late signed-error summaries;
- separate measure-shift diagnostics.

Files:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v5.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v5.yml`

Commits:
- implementation: `f5ecc12c2d138ecb766bbc078ffff672caa0b19d`
- workflow launch: `afe925cc19ac97de71aae0fd1f238bce84f13bc6`

Authoritative V5 run:
- run `37126810211`
- head `afe925cc19ac97de71aae0fd1f238bce84f13bc6`
- status at this update: IN PROGRESS
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37126810211

### Exact next resume instruction

Resume from run `37126810211`.

1. If freeze succeeds, record:
   - frozen artifact id/digest and bundle SHA-256;
   - primary candidate chosen before reference access;
   - global consensus BPM, quality score, bar confidence, beat count, local tempo summary.
2. If comparison succeeds, prioritize:
   - beat-count difference;
   - best beat-index shift;
   - median/mean/p95 beat error;
   - early/middle/late signed errors;
   - predicted full-song beat drift.
3. If drift collapses materially, proceed next to downbeat/bar/meter labeling while keeping the V5 beat trajectory frozen.
4. If drift does not collapse, diagnose whether inserted/missing beats or tempo trajectory remain the dominant issue; do not tune against the professional reference.
5. Do not change cleanup, separator, or note recognition.
6. Do not remap guitar/bass until beat timing is coherent.
7. Keep `main` unchanged.


## Go My Way reference-independent full-song timebase V5 — authoritative green result 2026-10-03

Authoritative workflow run:
- run `37126810211`
- both jobs GREEN.

Frozen artifact:
- id: `11274669899`
- name: `gomyway-reference-independent-timebase-v5-frozen`
- digest: `sha256:e2bd1b63e8bd467cc3cb8673d28e223988c1236ccb10ee3d1bc19e9b49327566`
- frozen bundle SHA-256: `977287de3fd8985f5e07d0577606e2e4a019d4a947edffe847a56ae218aff9f4`

Result artifact:
- id: `11274979602`
- name: `gomyway-reference-independent-timebase-v5-result`
- digest: `sha256:4c37a0363eda4b677aeee6a8fa1c90e438d6f7677e17c364f9fc64c0087d73e5`

Prospectively selected primary:
- `consensus_global`
- global search tempo: `129.49499999999802 BPM`
- audio-only quality score: `0.321278453093014`
- bar confidence: `0.0`
- candidate beat count: `453`

Post-freeze diagnostic for primary:
- reference beat count: 450
- beat-count difference: +3
- best beat-index shift: -11
- median absolute beat error: `1.6473187379541647 s`
- p95 absolute beat error: `4.283788684243842 s`
- predicted full-song beat drift: `6.69362912534666 s`
- early mean signed error: `-0.8661315901393234 s`
- middle mean signed error: `1.3327776991116633 s`
- late mean signed error: `3.5242330586361246 s`

Measure diagnostic for primary:
- best measure shift: -2
- median absolute error: `1.6696800172021895 s`
- predicted drift across 113 measures: `7.035663786100665 s`

V5 local candidate:
- candidate beat count: 455
- beat-count difference: +5
- median absolute beat error: `1.674832128735595 s`
- predicted full-song beat drift: `7.2643460562685656 s`
- early/middle/late signed errors: -4.0281 / -1.4735 / +0.8198 s.

Scientific interpretation:
- cross-source consensus reduced beat-count mismatch substantially but did not remove systematic tempo drift;
- the primary trajectory changes from early-negative to late-positive signed error, confirming a persistent period mismatch;
- repeated ~129 BPM locking across independent approaches indicates the current onset-periodicity family is consistently selecting the wrong rhythmic mode;
- do not remap guitar/bass yet.

### Exact next resume instruction

Build a separately versioned **reference-independent timebase V6** using an independent multi-feature beat-tracking family rather than another variation of the same onset autocorrelation/lattice objective.

Preferred direction:
1. preserve raw mix and raw drums as independent inputs;
2. use a mature multi-feature rhythm tracker (e.g. Essentia RhythmExtractor2013 if runtime support is viable) as a genuinely independent estimator family;
3. freeze outputs and any audio-only primary selection before professional comparison;
4. retain beat-count, sequence-aligned drift, early/middle/late error, and measure diagnostics;
5. do not use the professional map to select tracker parameters or candidates;
6. do not alter cleanup, separator, or note recognition;
7. keep `main` unchanged.


## Go My Way reference-independent full-song timebase V6 — launched 2026-10-03

Goal:
- test a genuinely independent beat-tracking family after V1–V5 repeatedly converged on the same slower rhythmic mode.

V6 estimator:
- Essentia `RhythmExtractor2013`;
- both `multifeature` and `degara` methods;
- raw full mix and raw BS-Roformer drum stem as independent inputs.

Reference-blind V6 candidates:
- `mix_multifeature`
- `drums_multifeature`
- `mix_degap` (Essentia method `degara`)
- `drums_degap` (Essentia method `degara`)

Primary selection:
- audio-only quality score;
- tie estimator confidence;
- tie bar confidence;
- frozen before professional reference access.

Files:
- `astra_backend/evaluation/gomyway_reference_independent_timebase_v6.py`
- `.github/workflows/astra-gomyway-reference-independent-timebase-v6.yml`

Commits:
- V6 implementation: `ea8fe5db66999c795194cd7b78bd869ee53d37c6`
- V6 workflow launch: `2195a3b096adb37e7144f6d868ea9eeeba164e29`

Authoritative V6 run:
- run `37138941466`
- head `2195a3b096adb37e7144f6d868ea9eeeba164e29`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37138941466

### Exact next resume instruction

Resume from run `37138941466`.

1. If runtime fails because of Essentia packaging/API differences, fix runtime only; do not alter candidate semantics.
2. If freeze succeeds, record artifact identity, bundle SHA, Essentia version, prospectively selected primary, reported BPM/confidence/bar-confidence/beat count for all four candidates.
3. If comparison succeeds, record:
   - beat-count difference;
   - best beat-index shift;
   - median/mean/p95 beat error;
   - early/middle/late signed error;
   - predicted full-song beat drift;
   - measure diagnostics.
4. If an independent estimator collapses beat drift, freeze that beat trajectory and move next to downbeat/meter labeling.
5. If all independent trackers still drift similarly, investigate whether the professional timing map/audio binding itself needs a separate integrity audit before more estimator development; do not assume either side is correct without checking immutable source binding.
6. Do not remap guitar/bass until timing is coherent.
7. Keep `main` unchanged.


## Go My Way professional timing-map integrity audit V1 — launched 2026-10-03

Trigger for audit:
- independent V6 Essentia estimators still converged near 128.9–129.0 BPM;
- the preserved professional timing map itself declares `baseTempoBpm: 129`;
- its current resolved override is `133.8 BPM`, derived from a sparse alignment diagnosis using only 19 matching occurrences;
- the timing map metadata says `performanceDriftCorrection: pending`, has no manual anchor measures, and `productionPromotionAllowed: false`;
- the repeated ~7-second candidate-vs-reference drift is numerically close to the duration difference created by using 133.8 BPM instead of 129 BPM across 450 quarter-note beats.

Critical conclusion:
- do NOT build V7 or force audio-derived beat trackers toward 133.8 until the preserved reference timing map is independently audited.
- The next question is whether the reference map, not the candidate, is the dominant source of the apparent drift.

Audit files:
- `astra_backend/evaluation/gomyway_professional_timing_integrity_audit_v1.py`
- `.github/workflows/astra-gomyway-professional-timing-integrity-audit-v1.yml`

Commits:
- audit script: `bd604572f3da32df27d7dbbed4ee4cd5f1e9d5af`
- audit workflow: `93c5cf2e5f5dede69403a47f049a2b27f01944d0`

Audit checks:
- immutable source audio identity and exact duration;
- timing-map first offset and last mapped end;
- quarter-beat count implied by meter regions;
- expected mapped span at base 129 BPM;
- expected mapped span at resolved 133.8 BPM;
- remaining audio tail under both hypotheses;
- alignment-diagnosis evidence strength and promotion status;
- internal metadata about pending drift correction/manual anchors.

Authoritative audit run:
- run `37140101179`
- head `93c5cf2e5f5dede69403a47f049a2b27f01944d0`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37140101179

### Exact next resume instruction

Resume from audit run `37140101179`.

1. Record exact source audio duration and SHA.
2. Record map span, base-129 expected span/end, resolved-133.8 expected span/end, and remaining audio tail.
3. Determine whether the current 133.8 map is internally well-supported enough to remain the timing gold standard.
4. If the audit shows the map is likely miscalibrated:
   - do not rewrite it from the same sparse alignment evidence;
   - construct a separately versioned reference-timing revalidation using professional notation structure plus audio-only beat evidence and independent anchors;
   - preserve the old map as historical evidence.
5. If the audit unexpectedly supports 133.8 strongly, then resume estimator work.
6. Do not remap guitar/bass until the timing reference itself is trustworthy.
7. Keep `main` unchanged.


## Professional timing integrity audit V1 — authoritative green result 2026-10-03

Audit run:
- `37140101179`
- result: GREEN
- artifact id: `11280530014`
- artifact digest: `sha256:d25f548da6848d18de4ea7b18ea0a2eec78e7beb442a384f0c5c6e3466670c83`

Immutable source:
- `public/gomywayfullaitest.m4a`
- SHA-256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- duration: `211.440907 s`

Existing professional timing map V2:
- base tempo: `129.0 BPM`
- resolved tempo override: `133.8 BPM`
- first measure offset: `7.1 s`
- mapped span: `201.793722 s`
- last measure end: `208.893722 s`
- audio tail after mapped end: `2.547185 s`
- 450 quarter-note beats implied by meter regions.
- span at base 129 BPM would be `209.30232558139534 s`.
- span at resolved 133.8 BPM is `201.79372197309416 s`.
- base-vs-resolved span difference: `7.508603608301172 s`, essentially the same scale as the repeated candidate-vs-map drift.
- map metadata still says `performanceDriftCorrection: pending`, no manual anchors, and `productionPromotionAllowed: false`.

Alignment diagnosis provenance:
- event count: 1629
- best resolved tempo: 133.8 BPM
- best offset: 7.1 s
- correct candidate slots: 8
- total matching occurrences: 19
- diagnosis itself has `productionPromotionAllowed: false`.

Scientific conclusion:
- V2 timing map is internally consistent with its own 133.8-BPM assumption, but that assumption is not strong enough to remain the timing gold standard.
- Multiple independent audio trackers converge near 129 BPM, while the old map's 7.5 s faster-span difference closely matches the apparent full-song drift.
- Preserve V2 unchanged as historical diagnostic evidence, but do not continue forcing candidate timing toward 133.8 BPM.

## Professional timing revalidation V1 — launched 2026-10-03

Purpose:
- construct a separately versioned research-only timing map using:
  1. frozen V6 `mix_multifeature` beat ticks;
  2. frozen V6 `drums_multifeature` beat ticks;
  3. professional notation structure only: 113 measures, meter regions, exactly 450 quarter-note beats.
- old V2 timing coordinates, 133.8 BPM, and 7.1 s offset are explicitly excluded from fitting.

Revalidation method:
- cluster V6 mix+drum ticks within 150 ms;
- derive target interval from the audio clusters themselves;
- dynamic-programming path selects exactly 450 beat starts;
- rewards dual-source support and regular intervals;
- penalizes single-source pulses and skipped cluster events;
- uses professional measure/meter structure only after the 450-beat path is selected;
- old timing map remains untouched.

Offline sanity check of the frozen V6 evidence before workflow launch:
- exact 450-beat consensus path was feasible;
- provisional first beat ~`1.0623 s`;
- provisional average tempo ~`129.16 BPM`;
- provisional final measure endpoint ~`210.1 s`;
- this leaves a short plausible audio tail rather than requiring the old ~7.5 s tempo compression.

Files:
- `astra_backend/evaluation/gomyway_professional_timing_revalidation_v1.py`
- `.github/workflows/astra-gomyway-professional-timing-revalidation-v1.yml`

Commits:
- implementation: `ff4fe8c13349ea5f4e891759dcab6e6a1d24d0e8`
- workflow launch: `a3a51eafbf45422563ccd94eef1b8dcfae86813c`

Authoritative revalidation run:
- run `37141135823`
- head `a3a51eafbf45422563ccd94eef1b8dcfae86813c`
- status at this update: IN PROGRESS
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37141135823

### Exact next resume instruction

Resume from run `37141135823`.

1. If green, record:
   - revalidated timing-map artifact ID/digest;
   - exact map SHA-256 and audit SHA-256;
   - cluster count;
   - selected 450-beat path;
   - first measure start;
   - last measure end;
   - average/median BPM;
   - selected dual-source vs single-source counts;
   - skipped cluster diagnostics.
2. Do not overwrite `public/gomyway-professional-timing-map-v2.json`.
3. Treat new V3 map as research-only until it passes diagnostic rescoring and independent anchor checks.
4. Next, rescore existing raw Basic Pitch guitar/bass events against the revalidated timing map without changing Basic Pitch/separator settings.
5. Compare against the old 133.8-map results to quantify how much of the previous poor guitar/bass score was timing-map error.
6. Keep `main` unchanged.


## Professional timing revalidation V1 — runtime-only failure and relaunch 2026-10-03

Failed run:
- run `37141135823`
- failure occurred after frozen V6 artifact download and checksum verification;
- failure was `ModuleNotFoundError: No module named 'numpy'`;
- the revalidation script did not execute;
- no new timing map or audit artifact was produced;
- this was a runtime packaging failure only, not a scientific failure.

Runtime-only fix:
- added Python 3.10 setup and `numpy==1.26.4` installation to the workflow;
- candidate semantics, frozen V6 artifact, clustering rules, dynamic-programming path, notation structure, and exclusion of old V2 timing coordinates remain unchanged.

Fix commit:
- `0a3c1629c067bea2883ac71815e44e9b7ad09c2b`

Relaunched authoritative run:
- run `37141537153`
- head `0a3c1629c067bea2883ac71815e44e9b7ad09c2b`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37141537153

### Exact next resume instruction

Resume from run `37141537153`.
If green, record exact revalidated map/audit metrics and artifact hashes.
If it fails, inspect only the new runtime/script error and preserve all frozen scientific inputs unchanged.


## Professional timing revalidation V1 — authoritative green result 2026-10-03

Authoritative run:
- run `37141537153`
- result: GREEN
- artifact id: `11280532281`
- artifact name: `gomyway-professional-timing-revalidation-v1`
- artifact digest: `sha256:c7b8dd1f3937628d36cbfa3ab3f790f7faefa60359b041b03fce496987fb3c04`

Generated research timing map:
- file: `gomyway-professional-timing-map-v3-revalidated.json`
- SHA-256: `1aeb65d69c8305f79d8a18995464379a28ed56626c8fc2ba32d036e9a63ab4ac`
- exact selected quarter-beat count: `450`
- clustered V6 beat events before path selection: `460`
- skipped cluster count: `10`
- average tempo: `129.15967204325972 BPM`
- median tempo: `129.19862000985708 BPM`
- first measure start: `1.06231290102005 s`
- last measure end: `209.98965454101562 s`
- audio duration from integrity audit: `211.440907 s`
- remaining audio tail after revalidated map: ~`1.451252459 s`

Consensus support:
- dual-source selected beats (mix + drums): `443 / 450`
- single-source selected beats: `7 / 450`
- therefore 98.44% of selected beat positions have independent support from both frozen V6 source families.

Revalidation audit:
- file: `gomyway-professional-timing-revalidation-v1-audit.json`
- SHA-256: `aa901ca31745c52d41170d37cc6cd069d8063603a69c57f2a21a72b7a4f217da`

Scientific interpretation:
- this new research timing baseline is strongly supported by frozen independent audio evidence and the professional notation structure;
- it resolves the repeated ~7-second mismatch created by the old 133.8-BPM map;
- the old V2 map remains preserved unchanged as historical diagnostic evidence;
- V3 revalidated map is research-only and not production-promoted yet;
- next step is diagnostic rescoring of existing raw guitar/bass note events against this revalidated timing map with separator and Basic Pitch settings unchanged.

### Exact next resume instruction

1. Materialize/use artifact `11280532281` and preserve its map/audit hashes.
2. Build a diagnostic scorer path that uses `gomyway-professional-timing-map-v3-revalidated.json` for timing only.
3. Reuse the already-generated/raw Basic Pitch note events from the full-song benchmark; do NOT regenerate or retune note inference if avoidable.
4. Score rhythm, lead, combined guitar, and bass using the same matching definitions as the previous benchmark.
5. Report side-by-side old-map vs revalidated-map precision/recall/F1 and absolute timing alignment.
6. Quantify how much previous poor guitar/bass performance was due to the bad 133.8-BPM timing map versus note/pitch recognition.
7. If timing-corrected scores improve materially, continue from the revalidated map toward string/fret/pitch refinement.
8. Keep `main` unchanged.


## Timing-map attribution rescore V1 — launched 2026-10-03

Goal:
- quantify how much of the previous low guitar/bass professional-reference agreement was caused by the historical 133.8-BPM timing map versus note/pitch recognition.

Important implementation decision:
- previous full-song benchmark artifact retained scores but not the raw Basic Pitch prediction lists;
- therefore inference must be regenerated;
- separator model, Basic Pitch package/model/default thresholds, source audio, and scorer-ready professional references are all kept frozen;
- inference is run exactly once;
- the same prediction lists are then scored against BOTH timing maps in the same process.

Timing maps:
1. historical V2: `public/gomyway-professional-timing-map-v2.json`
2. revalidated V3 research map downloaded from authoritative revalidation run `37141537153`
   - expected SHA-256 `1aeb65d69c8305f79d8a18995464379a28ed56626c8fc2ba32d036e9a63ab4ac`

Frozen inference:
- source audio Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`
- BS-Roformer-SW 6-stem FP16 ONNX SHA-256 `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`
- Basic Pitch 0.4.0 frozen identity/defaults
- no cleanup
- no threshold search
- no automatic correction

Professional scorer references remain unchanged:
- rhythm `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`
- lead `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`
- bass `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`

Files:
- `astra_backend/evaluation/gomyway_timing_map_attribution_rescore_v1.py`
- `.github/workflows/astra-gomyway-timing-map-attribution-rescore-v1.yml`

Commits:
- implementation: `d96ade0bc6c7d1439f4c574c33c5d21d4e3821da`
- workflow launch: `fc11f06873866419574d2cdc059999375961cfb1`

Authoritative run:
- run `37141748903`
- head `fc11f06873866419574d2cdc059999375961cfb1`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37141748903

### Exact next resume instruction

Resume from run `37141748903`.

If green:
1. record artifact ID/digest and output JSON SHA;
2. record identical prediction counts for whole mix, guitar stem, bass stem;
3. for historical V2 and revalidated V3 timing maps, record separator:
   - rhythm TP/P/R/F1/MAE;
   - lead TP/P/R/F1/MAE;
   - combined guitar TP/P/R/F1/MAE;
   - bass TP/P/R/F1/MAE;
4. record revalidated-minus-historical deltas;
5. interpret how much error was timing-map-induced versus remaining note recognition;
6. if scores improve materially, keep the V3 timing map frozen and move next to pitch/string/fret refinement rather than more timing work;
7. if scores do not improve, diagnose scorer/reference step-coordinate assumptions before changing recognizer thresholds;
8. keep `main` unchanged.


## Timing-map attribution rescore V1 — authoritative green result 2026-10-03

Authoritative run:
- run `37141748903`
- result: GREEN
- artifact id: `11280744097`
- artifact name: `gomyway-timing-map-attribution-rescore-v1`
- artifact digest: `sha256:955fc8d261d6a24c29cbc3093573f81168abca649490b5fdf11e77590434039c`
- result JSON SHA-256: `25d11929d5da30f6a5269219be24d402c6e9437fcd503dc0833311e205389515`

Frozen inference was run once and shared across both timing maps:
- whole mix predictions: 787
- guitar stem predictions: 1065
- bass stem predictions: 701

Historical V2 map (133.8 BPM) separator scores:
- rhythm: TP 56, P 5.4741%, R 5.9197%, F1 5.6882%, onset MAE 24.640 ms
- lead: TP 45, P 4.4776%, R 10.0671%, F1 6.1983%, onset MAE 27.387 ms
- combined guitar: TP 96, P 9.5522%, R 6.8916%, F1 8.0067%, onset MAE 26.096 ms
- bass: TP 50, P 7.2886%, R 9.1408%, F1 8.1103%, onset MAE 22.036 ms

Revalidated V3 map (~129.16 BPM) separator scores:
- rhythm: TP 53, P 4.9906%, R 5.6025%, F1 5.2789%, onset MAE 24.619 ms
- lead: TP 34, P 3.2661%, R 7.6063%, F1 4.5699%, onset MAE 22.414 ms
- combined guitar: TP 76, P 7.3007%, R 5.4559%, F1 6.2449%, onset MAE 24.292 ms
- bass: TP 157, P 22.6551%, R 28.7020%, F1 25.3226%, onset MAE 19.443 ms

Revalidated-minus-historical deltas:
- rhythm: TP -3, F1 -0.409 percentage points
- lead: TP -11, F1 -1.628 percentage points
- combined guitar: TP -20, F1 -1.762 percentage points
- bass: TP +107, F1 +17.212 percentage points

Scientific interpretation:
- bass was strongly timing-map limited; correcting the clock increased bass TP from 50 to 157 and F1 from 8.11% to 25.32% with identical predictions;
- guitar did not improve under the new global clock and actually declined slightly;
- therefore the remaining guitar bottleneck is not the same global tempo error that affected bass;
- before changing Basic Pitch thresholds or separator settings, diagnose guitar beat/bar phase and scorer step-coordinate assumptions against the revalidated map;
- preserve the revalidated timing map frozen while performing this diagnosis.

### Exact next resume instruction

Build a guitar-only timing/coordinate diagnostic using the revalidated V3 map and the same frozen inference stack.
1. Do not tune or mutate the map.
2. For rhythm and lead separately, measure nearest exact-MIDI onset errors without the 50 ms cutoff.
3. Test diagnostic integer beat shifts / bar-phase offsets only after inference.
4. Report early/middle/late error, per-measure concentration, and whether a simple beat/bar phase correction explains the missed matches.
5. If no simple timing-phase explanation exists, move to pitch/voicing/string-fret recognition.
6. Keep bass on the revalidated V3 map.
7. Keep `main` unchanged.


## Guitar timing/coordinate diagnostic V1 — launched 2026-10-03

Purpose:
- explain why bass improved strongly on the revalidated timing map while rhythm/lead guitar did not.

Frozen inputs:
- revalidated V3 timing map SHA-256 `1aeb65d69c8305f79d8a18995464379a28ed56626c8fc2ba32d036e9a63ab4ac`
- source audio unchanged
- BS-Roformer unchanged
- Basic Pitch 0.4.0 unchanged
- rhythm/lead professional scorer references unchanged
- no threshold tuning
- no timing-map mutation

Diagnostics:
1. nearest exact-MIDI onset error without a 50 ms cutoff;
2. early/middle/late signed and absolute error;
3. post-inference integer beat-shift diagnostics from -8 to +8 beats;
4. per-measure TP concentration;
5. rhythm and lead analyzed independently.

Decision rule:
- if a simple beat/bar phase shift explains the guitar misses, fix coordinate interpretation in a new separately versioned layer;
- if not, preserve the clock and move to pitch/voicing/string-fret recognition.

Files:
- `astra_backend/evaluation/gomyway_guitar_timing_coordinate_diagnostic_v1.py`
- `.github/workflows/astra-gomyway-guitar-timing-coordinate-diagnostic-v1.yml`

Commits:
- implementation: `094a99b51f69443e75810b2bfba5b8ccb26810e6`
- workflow launch: `30ccbd22c871b8d08555203e46694720d44e9927`

Authoritative run:
- run `37142945400`
- head `30ccbd22c871b8d08555203e46694720d44e9927`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37142945400

### Exact next resume instruction

Resume from run `37142945400`.
If green:
1. record artifact identity and JSON SHA;
2. record rhythm/lead nearest-exact-MIDI median/mean errors;
3. record early/middle/late timing errors;
4. record best integer beat shift and TP at 50 ms for each role;
5. identify measures with strongest/weakest exact-match concentration;
6. decide whether guitar still has a coordinate-phase problem or should move to pitch/voicing recognition;
7. keep bass on revalidated timing V3 and keep `main` unchanged.


## Guitar timing/coordinate diagnostic V1 — authoritative green result 2026-10-03

Authoritative run:
- run `37142945400`
- result: GREEN
- artifact id: `11281422316`
- artifact name: `gomyway-guitar-timing-coordinate-diagnostic-v1`
- artifact digest: `sha256:993f67c0cb5c9b9da6f2883a07ccfe51a02e38b7bdf7a6735a6231a153a7380a`
- result JSON SHA-256: `9fbc9e5388188def88045ff0a69466e98ec2c87e3ace326f730b7a505e8c9563`

Rhythm guitar:
- nearest exact-MIDI median absolute onset error: `0.4699158430 s`
- mean absolute error: `7.4542163611 s` (heavy outlier effect)
- early/middle/late median absolute errors: 0.4697 / 0.4641 / 0.4855 s
- best integer beat shift: `-1`
- TP at 50 ms under -1 beat diagnostic shift: `326`
- direct unshifted TP on revalidated map was only 53.

Lead guitar:
- nearest exact-MIDI median absolute onset error: `3.0095193133 s`
- mean absolute error: `17.3067080424 s`
- early/middle/late median absolute errors: 3.1814 / 4.4592 / 1.9611 s
- best integer beat shift: `-1`
- TP at 50 ms under -1 beat diagnostic shift: `137`
- direct unshifted TP on revalidated map was only 34.

Critical shared-coordinate finding:
- BOTH rhythm and lead independently prefer the SAME -1 beat shift.
- This is strong evidence of a shared downbeat/measure-origin error rather than separate role-specific timing failures.

Revalidation audit follow-up:
- the exact 450-beat revalidation path began at `1.0623129010 s`;
- it skipped an earlier cluster at `0.5166439712 s`;
- that skipped early cluster has **dual-source support from both drums and mix** with only ~11.6 ms source spread;
- this makes an audio-side one-beat-earlier origin hypothesis plausible and directly explains the guitar -1 beat result.
- do NOT change tempo; tempo remains ~129.16 BPM.
- do NOT silently overwrite the V3 map. Any phase-origin correction must be separately versioned and explicitly marked as a new hypothesis.

### Exact next resume instruction

Build a separately versioned **timing-origin V4 diagnostic candidate** that preserves the frozen ~129.16 BPM beat trajectory but tests the earlier dual-source origin near 0.516644 s.

Requirements:
1. derive it from the same frozen V6 mix+drum evidence;
2. include the early dual-source cluster as the start-origin hypothesis;
3. preserve professional structure of 450 quarter-note beats / 113 measures / 2/4 at m104;
4. do not retune tempo;
5. score identical Basic Pitch predictions against V3 and V4-origin maps in one run;
6. report rhythm, lead, combined guitar, AND bass changes;
7. promotion rule: only consider V4-origin as a research baseline if guitar improves strongly without materially breaking bass and the beat path remains audio-supported;
8. keep old maps preserved and keep `main` unchanged.


## Timing-origin V4 diagnostic — launched 2026-10-03

Motivation:
- guitar timing diagnostic found both rhythm and lead independently prefer an integer beat shift of -1;
- rhythm TP at 50 ms rose from 53 direct matches to 326 under that diagnostic shift;
- lead TP rose from 34 to 137;
- the revalidation audit showed the 450-beat V3 path skipped an earlier dual-source cluster at `0.5166439712 s` and began at `1.0623129010 s`.

V4 origin hypothesis:
- preserve frozen V6 mix+drum evidence;
- preserve ~129 BPM beat trajectory;
- preserve 113 measures / 450 quarter-note beats / 2/4 at measure 104;
- force the earliest dual-source cluster as the origin candidate;
- do not retune tempo;
- mark result as post-hoc diagnostic only, not prospective validation.

Files:
- `astra_backend/evaluation/gomyway_timing_origin_v4_diagnostic.py`
- `.github/workflows/astra-gomyway-timing-origin-v4-diagnostic.yml`

Commits:
- implementation: `6349bdf8c2a4bc42e4c0c9ad6e83db9f2f992c6b`
- workflow launch: `7494655cb6fdc4fac5d069ff2612479558632ab4`

Authoritative run:
- run `37144194576`
- head `7494655cb6fdc4fac5d069ff2612479558632ab4`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37144194576

### Exact next resume instruction

Resume from run `37144194576`.

If green:
1. record V4 origin map SHA and audit SHA;
2. record first measure start, last measure end, average/median BPM, dual-source vs single-source support;
3. compare identical-prediction V3 vs V4-origin scores for rhythm, lead, combined guitar, and bass;
4. V4-origin is only promising if guitar improves strongly while bass does not materially regress;
5. do not call V4-origin validated solely from this post-hoc song-specific test;
6. if promising, preserve it as a research candidate and then validate the origin-selection rule prospectively on independent material;
7. keep all prior maps and `main` unchanged.


## Timing-origin V4 diagnostic — authoritative green result 2026-10-03

Authoritative run:
- run `37144194576`
- result: GREEN
- artifact id: `11281478980`
- artifact name: `gomyway-timing-origin-v4-diagnostic`
- artifact digest: `sha256:b6efd9d9e6b3d9766e90aa97a43da26ba3c95e4bcec76b92172f68b51d27926f`
- V3-vs-V4 attribution JSON SHA-256: `d39a13638b5757fa149131c693ce8220e1eed497bda227d035b00a673b0d14d9`

V4 origin map:
- forced origin: `0.5166439712047577 s`
- source support: dual-source (mix + drums)
- average tempo: `129.13091670756597 BPM`
- median tempo: `129.19862000985708 BPM`
- first measure start: `0.5166439712047577 s`
- last measure end: `209.4904327392578 s`
- dual-source selected beats: `443 / 450`
- single-source selected beats: `7 / 450`
- same professional meter structure: 113 measures, 450 quarter-note beats, 2/4 at measure 104.

Identical-prediction V3 -> V4-origin separator results:

Rhythm:
- V3: TP 53, P 4.99%, R 5.60%, F1 5.28%
- V4-origin: TP 320, P 30.05%, R 33.83%, F1 31.82%
- delta: TP +267, F1 +26.55 percentage points

Lead:
- V3: TP 34, P 3.27%, R 7.61%, F1 4.57%
- V4-origin: TP 133, P 12.74%, R 29.75%, F1 17.84%
- delta: TP +99, F1 +13.27 percentage points

Combined guitar:
- V3: TP 76, P 7.30%, R 5.46%, F1 6.24%
- V4-origin: TP 427, P 40.90%, R 30.65%, F1 35.04%
- delta: TP +351, F1 +28.80 percentage points

Bass:
- V3: TP 157, P 22.66%, R 28.70%, F1 25.32%
- V4-origin: TP 365, P 52.82%, R 66.73%, F1 58.97%
- delta: TP +208, F1 +33.64 percentage points

Scientific interpretation:
- the one-beat-earlier origin dramatically improves every role with identical predictions;
- this strongly supports the hypothesis that V3 was one beat late in measure origin;
- tempo did NOT need retuning;
- the dominant timing problem was coordinate origin, not beat-period estimation;
- however V4-origin is explicitly POST-HOC because the hypothesis was motivated by Go My Way scoring diagnostics;
- do not call V4-origin independently validated or production-ready;
- preserve all older timing maps and artifacts.

### Exact next resume instruction

1. Treat V4-origin as the current strongest RESEARCH timing candidate for Go My Way only.
2. Do not tune further on Go My Way.
3. Extract an audio-only origin-selection rule from the frozen evidence that would have selected the earliest stable dual-source beat without professional scoring.
4. Test that rule prospectively on independent material/reference songs before promoting the rule.
5. For Go My Way downstream diagnostics, V4-origin may be used as the research timing candidate, clearly labeled post-hoc.
6. Next note-recognition work should focus on remaining pitch/voicing/string-fret errors under V4-origin, not tempo.
7. Keep `main` unchanged.


## V4-origin frozen note evidence V1 — launched 2026-10-03

Purpose:
- stop repeatedly regenerating identical Basic Pitch predictions;
- freeze raw whole-mix, guitar-stem, and bass-stem note events once under the V4-origin research timing candidate;
- enable all future pitch/voicing/string-fret diagnostics to reuse byte-identical note evidence.

Inputs remain frozen:
- source audio unchanged;
- BS-Roformer unchanged;
- Basic Pitch 0.4.0 defaults unchanged;
- V4-origin timing map from run `37144194576`;
- no professional note reference is read during generation;
- no threshold search, cleanup, or automatic correction.

Files:
- `astra_backend/evaluation/gomyway_v4_origin_freeze_note_evidence_v1.py`
- `.github/workflows/astra-gomyway-v4-origin-freeze-note-evidence-v1.yml`

Commits:
- implementation: `2ac24fcbb32ae003da271fd514d458afffffc6dd`
- workflow launch: `30c8fcb518ab7c222f5e976ca29310a6ef7ac4f6`

Authoritative run:
- run `37146481347`
- head `30c8fcb518ab7c222f5e976ca29310a6ef7ac4f6`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37146481347

### Exact next resume instruction

Resume from run `37146481347`.

If green:
1. record artifact ID/digest and frozen note-evidence JSON SHA;
2. verify prediction counts remain whole 787 / guitar 1065 / bass 701;
3. use this artifact for the next pitch-error diagnostic instead of rerunning Basic Pitch;
4. analyze, under V4-origin:
   - target notes with correct onset but wrong MIDI;
   - semitone/octave error distribution;
   - chord/voicing collision patterns;
   - rhythm vs lead pitch-confusion separately;
   - bass residual pitch errors separately;
5. do not retune timing further on Go My Way;
6. preserve V4-origin as post-hoc research timing candidate only;
7. keep `main` unchanged.

Independent-origin validation status:
- repo contains Stairway audio and a trusted position/voicing reference, but that fixture lacks absolute beat/onset timing;
- therefore Stairway cannot honestly validate the V4 origin clock yet;
- do not claim prospective origin-rule validation from it.


## V4-origin frozen note evidence V1 — authoritative green result 2026-10-03

Authoritative run:
- run `37146481347`
- result: GREEN
- artifact id: `11282827368`
- artifact name: `gomyway-v4-origin-frozen-note-evidence-v1`
- artifact digest: `sha256:2725447db591a39902baa16f7d33cb985694f01ba382084ab6c8608d0aa3d32b`

Frozen prediction counts:
- whole mix: 787
- guitar stem: 1065
- bass stem: 701

Frozen timing map binding:
- V4-origin timing-map SHA-256: `b87f122a007070d5a2abf0b676693c5ea7872ffcb04a06958ef103269c5f85f3`

Scientific value:
- future pitch/voicing/string-fret diagnostics can reuse exact saved note evidence;
- no need to rerun BS-Roformer or Basic Pitch for each diagnostic;
- removes accidental inference variation and shortens subsequent experiments.

## V4-origin pitch-error diagnostic V1 — launched 2026-10-03

Purpose:
- determine what remains after the major timing-origin correction;
- onset-match frozen predictions to professional targets without requiring MIDI equality first;
- then inspect MIDI error distribution.

Diagnostics by role:
- rhythm from frozen guitar stem;
- lead from frozen guitar stem;
- bass from frozen bass stem.

Reported categories:
- exact MIDI;
- ±1 semitone;
- ±2 semitones;
- ±3–5 semitones;
- ±12 semitone octave errors;
- other pitch/voicing errors;
- median/mean absolute MIDI error among onset-matched pairs;
- onset-matched target recall.

No prediction mutation, no threshold search, no timing tuning.

Files:
- `astra_backend/evaluation/gomyway_v4_origin_pitch_error_diagnostic_v1.py`
- `.github/workflows/astra-gomyway-v4-origin-pitch-error-diagnostic-v1.yml`

Commits:
- implementation: `b102d5a3fa8f447bd940e13a80b93edd3d924bcc`
- workflow launch: `717497b5098de2281df7fc066437b3d115efa338`

Authoritative run:
- run `37147588363`
- head `717497b5098de2281df7fc066437b3d115efa338`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37147588363

### Exact next resume instruction

Resume from run `37147588363`.

If green:
1. record artifact ID/digest and JSON SHA;
2. record onset-matched target recall for rhythm/lead/bass;
3. record exact-MIDI rate among onset-matched pairs;
4. record semitone/octave/error buckets and MIDI delta histogram;
5. determine whether the next bottleneck is:
   - small pitch displacement,
   - octave confusion,
   - chord/voicing confusion,
   - or missing onset evidence;
6. build the next recognizer experiment only around the dominant measured error class;
7. do not retune timing further on Go My Way;
8. keep V4-origin post-hoc/research-only and keep `main` unchanged.


## V4-origin pitch-error diagnostic V1 — runtime-only failure and relaunch 2026-10-03

Failed run:
- run `37147588363`
- frozen note-evidence artifact verified successfully;
- V4-origin timing map verified successfully;
- failure occurred before diagnostic execution;
- error: `ModuleNotFoundError: No module named 'soundfile'`;
- no pitch diagnostic result was produced;
- this was a runtime packaging failure only, not a scientific failure.

Runtime-only fix:
- added `soundfile` to the diagnostic workflow runtime;
- frozen evidence, timing map, professional references, onset tolerance, matching logic, and all diagnostic semantics remain unchanged.

Fix commit:
- `2e79dff796edaf0814c11df260321d9583b99b14`

Relaunched authoritative run:
- run `37148021444`
- head `2e79dff796edaf0814c11df260321d9583b99b14`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37148021444

### Exact next resume instruction

Resume from run `37148021444`.
If green, record the pitch-error buckets and decide the next recognizer experiment from the dominant measured error class.
If it fails again, fix only runtime/import plumbing and preserve all frozen scientific inputs unchanged.


## V4-origin pitch-error diagnostic V1 — second runtime-only failure and clean relaunch 2026-10-03

Second failed run:
- run `37148021444`
- frozen note evidence verified;
- V4-origin map verified;
- failure occurred before diagnostic logic executed;
- error: `ModuleNotFoundError: No module named 'scipy'`;
- root cause was the diagnostic importing helpers from the full benchmark module, which recursively imported inference/cleanup dependencies not needed for a JSON-only analysis.

Clean runtime fix:
- removed the dependency on `evaluate_gomyway_full_song_professional_v2.py`;
- copied only the small deterministic JSON/scoring helpers needed by this diagnostic:
  - SHA verification;
  - scorer reference validation;
  - excluded-measure handling;
  - timing-map target conversion;
  - measure lookup/filtering;
- the diagnostic is now self-contained and requires NumPy only;
- frozen predictions, references, timing map, onset tolerance, and matching semantics are unchanged.

Commits:
- self-contained diagnostic: `6344e6379f0882a4a4c9121f80069236105c9b7d`
- NumPy-only workflow: `6d85e55a78c1378eaa97f6c798db54eb69dfaa99`

Reruns:
- intermediate run `37148106233` was triggered by the script commit;
- latest authoritative run is `37148114794`;
- head `6d85e55a78c1378eaa97f6c798db54eb69dfaa99`;
- status at this update: QUEUED;
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37148114794

### Exact next resume instruction

Resume from latest run `37148114794`, not the intermediate `37148106233`.
If green, record the pitch-error diagnostic artifact and dominant error buckets.
If it fails, inspect the self-contained script directly; do not reinstall inference dependencies.


## V4-origin pitch-error diagnostic V1 — green result

Run `37148114794` succeeded.
- artifact id `11282548854`
- artifact digest `sha256:123c33abf2dee36b93b6f867648f899c4293e6ec9b1ceb1bc9d0e8453cc18337`
- result JSON SHA-256 `80ee32f11b24e77972305ad16d2ae4f6d5ce6ba24329f2aa0ef6972e0d8c716b`

Rhythm guitar:
- onset-matched 444/946 targets = 46.93%
- exact MIDI among onset matches 147/444 = 33.11%
- median absolute MIDI error 5 semitones
- octave errors 102; ±3–5 semitone errors 73; other 110

Lead guitar:
- onset-matched 222/447 targets = 49.66%
- exact MIDI among onset matches 90/222 = 40.54%
- median absolute MIDI error 4 semitones
- octave errors 48; ±3–5 semitone errors 26; other 49

Bass:
- onset-matched 419/547 targets = 76.60%
- exact MIDI among onset matches 318/419 = 75.89%
- median absolute MIDI error 0 semitones
- octave errors 62 are the dominant residual error class

Interpretation:
- V4-origin timing is no longer the main bottleneck.
- Bass is now mostly correct when an onset is found; residual bass error is primarily octave confusion.
- Guitar still has both missing-onset coverage and large pitch/voicing errors.
- Guitar errors are not mainly ±1 semitone tuning mistakes.

### Next resume instruction

Keep V4-origin timing frozen and reuse note-evidence artifact `11282827368`.
Build an octave/voicing attribution diagnostic only:
1. measure wrong guitar pitches recoverable by ±12;
2. measure pitch-class-correct but octave-wrong cases;
3. measure common interval errors separately for rhythm and lead;
4. measure bass +12 recovery upper bound;
5. do not apply corrections yet;
6. choose the next recognizer experiment from the dominant measured error class;
7. keep `main` unchanged.


## V4-origin octave/voicing attribution V1 — launched

Purpose:
- quantify how much remaining pitch error is attributable specifically to octave placement versus broader voicing/chord-tone confusion;
- reuse frozen note evidence from run `37146481347`;
- keep V4-origin timing frozen;
- no prediction mutation or correction.

Measured upper bounds:
- pitch-class-correct but wrong-octave count;
- recoverable-by-±12 count;
- recoverable-by-any-octave-multiple count;
- exact-MIDI upper bound if only ±12 octave mistakes were resolved;
- wrong-pitch interval histograms for rhythm, lead, and bass separately.

Files:
- `astra_backend/evaluation/gomyway_v4_origin_octave_voicing_attribution_v1.py`
- `.github/workflows/astra-gomyway-v4-origin-octave-voicing-attribution-v1.yml`

Commits:
- implementation: `3f9319f9f7853b80e9768a1e0fb776c3d943660b`
- workflow launch: `76b33bf6d24d434eb15348aef253db8f6f5ade10`

Authoritative run:
- run `37148533276`
- head `76b33bf6d24d434eb15348aef253db8f6f5ade10`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37148533276

### Exact next resume instruction

Resume from run `37148533276`.
If green:
1. record artifact ID/digest and JSON SHA;
2. record pitch-class-correct/wrong-octave counts and ±12 recovery upper bounds for rhythm, lead, bass;
3. compare octave-recoverable share of wrong-pitch events with broader interval-class errors;
4. if octave recovery is substantial enough, build a reference-blind octave-resolution heuristic next;
5. otherwise move directly toward harmonic/polyphonic voicing modeling;
6. do not alter V4-origin timing or frozen note evidence;
7. keep `main` unchanged.


## V4-origin octave/voicing attribution V1 — authoritative green result

Run `37148533276` succeeded.
- artifact id `11283248180`
- artifact digest `sha256:26846b3f3aae21356353584c02a7fb72ac0cd2a79c04ba99e55966cfbffea800`
- result JSON SHA-256 `58b500ccb8a438f39c4727166786b07d9dbd9fa161ffd00d959e4418127a6593`

Rhythm:
- onset matched 444
- exact MIDI 202
- wrong MIDI 242
- pitch-class correct but wrong octave 90 = 37.19% of wrong pitches
- single ±12 recoverable 85
- exact-MIDI upper bound under perfect ±12 resolution: 287/444 = 64.64%
- strongest non-octave errors: 4 semitones (44), 3 (19), 5 (19), 2 (13), 19 (13)

Lead:
- onset matched 222
- exact MIDI 100
- wrong MIDI 122
- pitch-class correct but wrong octave 47 = 38.52% of wrong pitches
- single ±12 recoverable 44
- exact-MIDI upper bound under perfect ±12 resolution: 144/222 = 64.86%
- strongest non-octave errors: 3 semitones (13), 19 (10), 2 (9), 4 (9), 5 (7)

Bass:
- onset matched 419
- exact MIDI 318
- wrong MIDI 101
- pitch-class correct but wrong octave 62 = 61.39% of wrong pitches
- all 62 are single +12 octave errors
- exact-MIDI upper bound under perfect ±12 resolution: 380/419 = 90.69%

Interpretation:
- octave resolution has substantial measured upside, especially bass;
- guitar also has meaningful octave error, but broader chord/voicing intervals remain important;
- next candidate should be reference-blind and audio/prediction-only;
- do not blanket-shift notes based on professional reference.

### Next action

Build a reference-blind local octave-consensus resolver:
1. use only frozen prediction timing/MIDI/amplitude;
2. candidate octave shifts limited to ±12 within fixed physical instrument ranges;
3. choose an octave shift only when nearby same-source pitch evidence strongly supports the alternate octave;
4. freeze corrected predictions before reading professional references;
5. score original vs corrected predictions afterward;
6. treat as Go My Way development only, not holdout validation;
7. keep V4-origin timing and `main` unchanged.


## Reference-blind octave consensus V1 — launched

Measured motivation from octave/voicing attribution:
- rhythm wrong-pitch events: 242; pitch-class-correct wrong octave: 90 (37.19%); ±12-only recoverable: 85
- lead wrong-pitch events: 122; pitch-class-correct wrong octave: 47 (38.52%); ±12-only recoverable: 44
- bass wrong-pitch events: 101; pitch-class-correct wrong octave: 62 (61.39%); ±12-only recoverable: 62

Candidate design:
- uses only frozen prediction timing/MIDI/amplitude;
- no professional reference read during candidate construction;
- fixed local window: 2.0 s;
- octave candidates limited to MIDI ±12 within fixed physical ranges:
  - guitar 40..88
  - bass 28..67
- nearby same-pitch-class events provide octave support;
- change requires at least 2 supporting neighbors and a fixed support margin;
- only octave displacement is allowed; no arbitrary pitch correction.

Scientific separation:
- job 1 freezes candidate and uploads SHA;
- job 2 downloads frozen candidate and only then reads professional references for scoring;
- V4-origin timing stays frozen;
- note evidence stays frozen.

Files:
- `astra_backend/evaluation/gomyway_reference_blind_octave_consensus_v1.py`
- `astra_backend/evaluation/score_gomyway_reference_blind_octave_consensus_v1.py`
- `.github/workflows/astra-gomyway-reference-blind-octave-consensus-v1.yml`

Commits:
- candidate implementation: `ccbae6a9bbaa34b70a8cd77d3a99c1d8642cdbcb`
- post-freeze scorer: `254f349a650c41872b8e8dd9aa4114483653919b`
- workflow launch: `9a2ac00b62db15a56913e78f7c2808530465a819`

Authoritative run:
- run `37156148873`
- head `9a2ac00b62db15a56913e78f7c2808530465a819`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37156148873

### Exact next resume instruction

Resume from run `37156148873`.
If green:
1. record frozen candidate artifact ID/digest and candidate SHA;
2. record guitar/bass octave change counts before reference read;
3. record score artifact ID/digest and score JSON SHA;
4. compare original vs corrected TP/P/R/F1 for rhythm, lead, bass;
5. reject the resolver if it harms any role materially;
6. if bass improves strongly and guitar is neutral/positive, consider role-specific octave resolver development;
7. if guitar degrades while bass improves, split guitar and bass octave policies rather than forcing one rule;
8. keep V4-origin timing, frozen note evidence, and `main` unchanged.


## Reference-blind octave consensus V1 — candidate-construction bug and relaunch

Failed run:
- run `37156148873`
- freeze-candidate failed before any candidate artifact was produced;
- score-after-freeze was skipped;
- frozen note evidence verified successfully.

Failure:
- `StopIteration` in `resolve_stream`;
- cause: for a frozen Basic Pitch note already outside the fixed physical instrument MIDI range, the candidate list excluded the original MIDI value, so the resolver could not find its current-state support row.

Conservative fix:
- if an original frozen prediction is outside the fixed instrument range, leave it unchanged;
- do not clamp it into range;
- do not invent an octave correction;
- valid in-range notes still use the exact same ±12 local-consensus rule and thresholds.

Fix commit:
- `8ddc1ab1c2d9465bcf69ce9d814fd632ceb89279`

Relaunched authoritative run:
- run `37156291597`
- head `8ddc1ab1c2d9465bcf69ce9d814fd632ceb89279`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37156291597

### Exact next resume instruction

Resume from run `37156291597`.
If green:
1. record frozen candidate SHA/artifact and guitar/bass change counts;
2. record post-freeze score artifact and original-vs-corrected rhythm/lead/bass metrics;
3. reject or split policies if any role is materially harmed;
4. preserve V4-origin timing, frozen note evidence, and `main`.


## Reference-blind octave consensus V1 — scoring infrastructure retry

Run `37156291597`:
- `freeze-candidate`: SUCCESS
- frozen candidate was produced successfully
- `score-after-freeze`: failed before scoring because GitHub Actions timed out downloading the already-frozen note-evidence artifact
- error was infrastructure/network: "We couldn't respond to your request in time"
- no scorer logic executed and the frozen candidate was not modified

Action taken:
- reran only the failed scoring job
- frozen candidate remains unchanged
- new score-after-freeze job id: `111301566606`
- freeze-candidate remains green

### Exact next resume instruction

Resume run `37156291597`, job `111301566606`.
If green, record frozen candidate identity/change counts and post-freeze original-vs-corrected rhythm/lead/bass metrics.
If it fails again only on artifact download, retry the scoring job without rebuilding the candidate.


## Reference-blind octave consensus V1 — authoritative result

Run `37156291597`:
- freeze-candidate: GREEN
- score-after-freeze rerun: GREEN

Frozen candidate artifact:
- id `11285877585`
- digest `sha256:6202ddacf4e3330b02126407060a826c5c1fa414ac24c55a408850ca26c37808`
- guitar changes: 169
- bass changes: 101

Score artifact:
- id `11286097918`
- digest `sha256:3382a86a6bf3600e883b5bb45a18023097349618a5a933681ef2b14c598dcd60`
- score JSON SHA-256 `303ee5ce922f45585bd932cdd1dc77c806bcb3f8d07695110d49e9c195ce7e83`

Original -> corrected:

Rhythm:
- TP 320 -> 275
- F1 31.82% -> 27.35%
- delta TP -45
- delta F1 -4.48 percentage points

Lead:
- TP 133 -> 129
- F1 17.84% -> 17.30%
- delta TP -4
- delta F1 -0.54 percentage points

Bass:
- TP 365 -> 369
- F1 58.97% -> 59.61%
- delta TP +4
- delta F1 +0.65 percentage points

Conclusion:
- reject the shared guitar+bass octave-consensus V1 policy;
- guitar local pitch-class consensus is too aggressive and destroys correct voicings;
- bass improves slightly and remains the only role with a strong octave-dominant residual error profile;
- next experiment should be bass-only and more conservative;
- preserve V4-origin timing and frozen note evidence;
- no further guitar octave correction until harmonic/voicing context is modeled.

### Next action

Build a bass-only reference-blind octave resolver:
1. never modify guitar;
2. operate only on frozen bass predictions;
3. only consider -12 for high-octave bass predictions because the measured residual bass octave errors were all +12 relative to target;
4. use conservative local register/continuity evidence;
5. freeze candidate before scoring;
6. reject unless bass improves without any guitar change by construction;
7. keep `main` unchanged.


## Bass-only octave resolver V2 — launched

Motivation:
- shared guitar+bass octave consensus V1 failed as a shared policy;
- guitar degraded, while bass improved only slightly;
- bass remains the role with the clearest octave-dominant residual error.

V2 constraints:
- guitar predictions are never modified;
- only frozen bass predictions are considered;
- only -12 semitone correction is allowed;
- correction requires:
  - original MIDI inside fixed bass range 28..67;
  - original MIDI >= 48;
  - lower-octave candidate in range;
  - at least 3 nearby same-pitch-class supporters within 1.5 s;
  - lower-octave support >= 1.5x current support and >= current+0.2;
  - local median-register proximity favoring the lower octave;
- candidate construction is reference-blind;
- scoring occurs only after freeze.

Files:
- `astra_backend/evaluation/gomyway_reference_blind_bass_octave_resolver_v2.py`
- `astra_backend/evaluation/score_gomyway_reference_blind_bass_octave_resolver_v2.py`
- `.github/workflows/astra-gomyway-bass-only-octave-resolver-v2.yml`

Commits:
- candidate: `09ab1000a2e704a9dffe725ddaece6695d20c3df`
- scorer: `cad0b96af9bf4590b13078a6ba3c1a3883548626`
- workflow launch: `e1cb9cd65d11ee3d67c38960d5e8509747703028`

Authoritative run:
- run `37156933423`
- head `e1cb9cd65d11ee3d67c38960d5e8509747703028`
- status at this update: IN PROGRESS
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37156933423

### Exact next resume instruction

Resume from run `37156933423`.
If green:
1. record frozen candidate artifact/digest and bass change count;
2. record score artifact/digest and original-vs-corrected bass TP/P/R/F1;
3. accept only if bass improves materially; guitar is unchanged by construction;
4. if neutral/negative, abandon local octave consensus and move to a different bass octave discriminator;
5. keep V4-origin timing, frozen note evidence, and `main` unchanged.


## Bass-only octave resolver V2 — authoritative green result

Run `37156933423` succeeded.

Frozen candidate:
- artifact id `11286157965`
- digest `sha256:01d6f5878b26c140010a12a227f18dcd0deced6f91316ba4c4a643ac11cc72ce`
- change count: 33 bass notes
- guitar unchanged by construction

Score artifact:
- artifact id `11286038151`
- digest `sha256:d30db42a77b7ae5d635e611c0ff3603c802d9b396903fd66a4b0faedb5bdc71f`
- score JSON SHA-256 `2b77dc5f14b12e183b000be6f263a12e276758b28ba7af715a123bad638e7dfa`

Bass original:
- TP 365
- precision 52.82%
- recall 66.73%
- F1 58.97%

Bass corrected:
- TP 369
- precision 53.40%
- recall 67.46%
- F1 59.61%

Delta:
- TP +4
- F1 +0.65 percentage points

Conclusion:
- V2 is technically positive but only marginally so;
- changing 33 bass notes yielded only 4 additional true positives;
- do not continue tuning local octave-consensus thresholds against Go My Way;
- local pitch-class/register consensus is not strong enough as the main octave discriminator;
- preserve this as a positive-but-weak development result, not a promoted policy.

### Exact next resume instruction

1. Keep V4-origin timing frozen.
2. Keep frozen note evidence unchanged.
3. Stop tuning local octave-consensus heuristics on Go My Way.
4. Next diagnostic should investigate **why** the +12 bass errors occur:
   - harmonic/subharmonic ambiguity,
   - source-separation residuals,
   - Basic Pitch octave bias,
   - local spectral fundamental-vs-second-harmonic evidence.
5. Build a reference-blind spectral octave discriminator using the original bass audio/stem and frozen event times, then freeze before scoring.
6. For guitar, do not apply octave heuristics; remaining problem is broader harmonic/voicing modeling.
7. Keep `main` unchanged.


## Spectral bass octave discriminator V1 — launched

Reason for pivot:
- local octave-consensus V2 was only marginally positive: bass F1 58.97% -> 59.61%, TP +4 after 33 changed notes;
- stop threshold-tuning local-consensus heuristics on Go My Way;
- investigate the physical failure mode directly: Basic Pitch may sometimes lock to the second harmonic rather than the bass fundamental.

Candidate construction:
- regenerate the frozen BS-Roformer bass stem once from immutable source audio;
- reuse frozen Basic Pitch bass event times/MIDI from note-evidence artifact `11282827368`;
- no professional note reference is read during candidate construction;
- for eligible bass events, compare spectral energy around:
  - predicted frequency;
  - one-octave-lower candidate frequency;
  - harmonic-series support for both hypotheses;
- only -12 semitone correction is allowed;
- fixed parameters before scoring:
  - 120 ms event window;
  - FFT size 8192;
  - bass MIDI range 28..67;
  - minimum MIDI for shift 40;
  - lower/current fundamental ratio >= 0.28;
  - lower-hypothesis score >= 1.20x current-hypothesis score;
  - lower-fundamental absolute spectral share >= 0.08.
- candidate is frozen before any professional scoring.

Files:
- `astra_backend/evaluation/gomyway_reference_blind_spectral_bass_octave_v1.py`
- reuses `score_gomyway_reference_blind_bass_octave_resolver_v2.py`
- `.github/workflows/astra-gomyway-spectral-bass-octave-v1.yml`

Commits:
- spectral candidate implementation: `a27768e5719cd25ca08d4254e5396ecd7120673d`
- workflow launch: `79c2853f963e33eb537f79d9e95ea9d6ffbce50e`

Authoritative run:
- run `37157163727`
- head `79c2853f963e33eb537f79d9e95ea9d6ffbce50e`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37157163727

### Exact next resume instruction

Resume from run `37157163727`.
If green:
1. record frozen candidate artifact/digest and candidate SHA;
2. record bass-stem SHA and spectral change count;
3. record post-freeze score artifact/digest and original-vs-corrected bass TP/P/R/F1;
4. compare against local-consensus V2 (TP 369, F1 59.61%);
5. accept spectral direction only if it materially exceeds V2 or gives clearer precision per changed note;
6. if neutral/negative, stop octave correction on Go My Way and move to broader bass onset/pitch modeling;
7. guitar remains untouched; its next work is harmonic/polyphonic voicing modeling;
8. keep V4-origin timing, frozen note evidence, and `main` unchanged.


## Spectral bass octave discriminator V1 — authoritative green result

Run `37157163727` succeeded.

Frozen candidate:
- artifact id `11286259572`
- digest `sha256:28909c85a24f25f6941fe17cd9c71b8673aca76bf1d1e10d319c583c27ff8798`
- spectral octave changes: 68 bass notes
- candidate construction remained reference-blind

Score artifact:
- artifact id `11285384776`
- digest `sha256:dd2e0168fa411a0091b478bf67a2cf88e16f18f2b276bd548dad237bfb17a303`
- score JSON SHA-256 `4d51869936784f9cffa8d7c7619fba73d8124d593c2c6e482f47075fc378c19b`

Bass original:
- TP 365
- precision 52.82%
- recall 66.73%
- F1 58.97%

Spectral corrected:
- TP 372
- precision 53.84%
- recall 68.01%
- F1 60.10%

Delta vs baseline:
- TP +7
- F1 +1.13 percentage points

Comparison to local-consensus V2:
- V2 TP 369, F1 59.61%
- spectral V1 TP 372, F1 60.10%
- spectral V1 is the strongest bass research candidate so far, but improvement remains modest relative to 68 changed notes.

Interpretation:
- direct spectral evidence is more useful than local pitch-class/register consensus for bass octave discrimination;
- keep spectral V1 as the current strongest bass research candidate;
- do not threshold-tune further on Go My Way;
- next major bottleneck is guitar harmonic/polyphonic voicing recognition, not bass octave placement.

### Exact next resume instruction

1. Preserve spectral bass V1 as current strongest bass research candidate.
2. Do not tune its thresholds further on Go My Way.
3. Move to guitar harmonic/voicing analysis using the frozen guitar note evidence and V4-origin timing.
4. Measure chord-onset structure:
   - how many simultaneous/near-simultaneous predicted notes occur per target onset;
   - whether correct target pitch classes are present elsewhere in the local predicted chord even when the one-to-one greedy match chose a wrong MIDI;
   - common missing/additional interval patterns for rhythm vs lead.
5. Use this to decide whether the next recognizer needs:
   - chord-set matching,
   - role assignment,
   - harmonic-context filtering,
   - or a different polyphonic transcription front end.
6. Keep `main` unchanged.


## Guitar chord/voicing diagnostic V1 — launched

Purpose:
- investigate the largest remaining transcription bottleneck after timing and bass-octave improvements;
- reuse frozen V4-origin guitar predictions;
- determine whether correct target pitches are already present inside nearby predicted polyphonic clusters even when one-note matching reports the wrong MIDI.

Method:
- cluster frozen guitar predictions within 60 ms;
- for each rhythm/lead target, find a prediction cluster within ±50 ms;
- report:
  - target-onset cluster coverage;
  - exact target MIDI present anywhere in the cluster;
  - target pitch class present anywhere in the cluster;
  - cluster-size distribution;
  - average extra notes per matched cluster;
  - common interval distances when exact MIDI is missing;
- diagnostic only; no prediction mutation.

Files:
- `astra_backend/evaluation/gomyway_v4_origin_guitar_chord_voicing_diagnostic_v1.py`
- `.github/workflows/astra-gomyway-guitar-chord-voicing-diagnostic-v1.yml`

Commits:
- implementation: `49debb73c7f982ebc43d9648e601a87f212c5c0e`
- workflow launch: `90ddf48b51c67750ccea217eb0caf2fbac65920d`

Authoritative run:
- run `37158245543`
- head `90ddf48b51c67750ccea217eb0caf2fbac65920d`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37158245543

### Exact next resume instruction

Resume from run `37158245543`.
If green:
1. record artifact ID/digest and JSON SHA;
2. record rhythm/lead target cluster coverage;
3. record exact-MIDI-present-anywhere-in-cluster rates;
4. record pitch-class-present-anywhere-in-cluster rates;
5. record cluster multiplicity/extra-note statistics;
6. decide whether next step is chord-set matching/role assignment versus a different polyphonic front end;
7. preserve spectral bass V1 as current strongest bass research candidate;
8. keep V4-origin timing, frozen note evidence, and `main` unchanged.


## Guitar chord/voicing diagnostic V1 — authoritative green result

Run `37158245543` succeeded.
- artifact id `11286531241`
- artifact digest `sha256:269d90fc5501cade98c5d0ccb24d189f2983c40ff88fd5a60640dcb9fd09470a`
- result JSON SHA-256 `97a2f0a9cf0e88cb4b92dc60be019894433bbb750fbf805c287937b28e4df878`

Rhythm:
- targets: 946
- nearby prediction cluster found: 596 = 63.00%
- exact target MIDI present anywhere in cluster: 314 / 596 = 52.68%
- target pitch class present anywhere in cluster: 400 / 596 = 67.11%
- matched-cluster multiplicity:
  - 1 note: 290
  - 2 notes: 246
  - 3 notes: 60
- mean extra predicted notes per found cluster: 0.614
- when exact MIDI missing, strongest intervals include 12, 5, 9, 4, 7, 3 semitones.

Lead:
- targets: 447
- nearby prediction cluster found: 240 = 53.69%
- exact target MIDI present anywhere in cluster: 135 / 240 = 56.25%
- target pitch class present anywhere in cluster: 166 / 240 = 69.17%
- matched-cluster multiplicity:
  - 1 note: 147
  - 2 notes: 79
  - 3 notes: 14
- mean extra predicted notes per found cluster: 0.446
- when exact MIDI missing, strongest intervals include 12, 5, 3, 2, 9, 7, 4 semitones.

Interpretation:
- Basic Pitch is often producing useful polyphonic information near the correct onset;
- a substantial fraction of current guitar misses are likely decoding/assignment/voicing problems rather than complete absence of pitch evidence;
- pitch-class presence is materially higher than exact-MIDI presence, so octave/voicing placement still matters;
- do not replace the transcription front end yet;
- next work should build a reference-blind chord-cluster decoder / role assignment layer that operates on frozen predictions and V4-origin timing;
- candidate must be frozen before professional scoring.

### Exact next resume instruction

1. Preserve spectral bass V1 as current strongest bass research candidate.
2. Keep guitar frozen note evidence and V4-origin timing unchanged.
3. Build a reference-blind guitar chord-cluster decoder:
   - group near-simultaneous notes;
   - use local continuity and register to assign likely rhythm vs lead roles;
   - preserve multiple notes when evidence supports a chord;
   - do not read professional references during candidate construction;
   - freeze candidate before scoring.
4. First version should avoid arbitrary pitch invention; only select/reassign among already-predicted notes, with optional octave normalization only if independently justified.
5. Score rhythm, lead, and combined guitar after freeze.
6. If this materially improves guitar, continue toward string/fret mapping.
7. Keep `main` unchanged.


## Reference-blind guitar chord-role decoder V1 — launched

Motivation from chord/voicing diagnostic:
- rhythm cluster coverage 63.00%; exact MIDI present somewhere in cluster 52.68%; target pitch class present 67.11%;
- lead cluster coverage 53.69%; exact MIDI present somewhere in cluster 56.25%; target pitch class present 69.17%;
- this suggests useful polyphonic evidence is already present and current misses may partly be decoding/role-assignment errors.

V1 decoder:
- uses frozen guitar predictions only;
- groups notes within 60 ms;
- no pitch invention;
- rhythm candidate keeps up to 3 notes/cluster using local register + continuity preference;
- lead candidate keeps up to 1 note/cluster using continuity + upper-register preference;
- singleton clusters are assigned rhythm-only;
- professional references are not read during candidate construction;
- candidate is frozen before scoring.

Files:
- `astra_backend/evaluation/gomyway_reference_blind_guitar_chord_role_decoder_v1.py`
- `astra_backend/evaluation/score_gomyway_reference_blind_guitar_chord_role_decoder_v1.py`
- `.github/workflows/astra-gomyway-guitar-chord-role-decoder-v1.yml`

Commits:
- decoder: `d6dcc4331a6b1520012e0f09bfefd6c23ca1e1fd`
- scorer: `5fdac662329fc436bd489f23dd71865bb4e844b9`
- workflow: `94d4999df709b6f2850e911dc4a7c7bf4d7556ac`

Authoritative run:
- run `37158385869`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37158385869

### Exact next resume instruction

Resume from run `37158385869`.
If green:
1. record frozen candidate artifact/digest and rhythm/lead candidate counts;
2. record post-freeze rhythm/lead/combined-guitar TP/P/R/F1;
3. compare against V4-origin baseline rhythm 31.82%, lead 17.84%, combined 35.04%;
4. if role-aware decoding improves precision without catastrophic recall loss, iterate structurally—not by tuning against reference;
5. if it fails, conclude Basic Pitch chord evidence is insufficiently separable by simple register/continuity and consider a different polyphonic front end;
6. preserve spectral bass V1 as current strongest bass candidate;
7. keep V4-origin timing, frozen note evidence, and `main` unchanged.


## Reference-blind guitar chord-role decoder V1 — authoritative green result

Run `37158385869` succeeded.

Frozen candidate:
- artifact id `11285559715`
- digest `sha256:795ebbdd20ec1723ef8a45d54d0caee88c30a70f47bfec7aba5f51406e6ab31f`
- input guitar predictions: 1065
- rhythm candidate: 1062
- lead candidate: 263

Score artifact:
- artifact id `11286890764`
- digest `sha256:fa150224cd992f11c6b4ae58cf95bfa05553b8b5a13a1ad5e30b74c68a0bb928`
- score JSON SHA-256 `41c2aaa360aec1a843487fffe19be6d7d448ee18cebce58ce8bd332b0d21f415`

Rhythm:
- baseline TP 320, F1 31.82%
- decoded TP 320, F1 31.87%
- effectively neutral

Lead:
- baseline TP 133, F1 17.84%
- decoded TP 40, F1 11.36%
- severe recall collapse

Combined guitar:
- baseline TP 427, F1 35.04%
- decoded TP 436, F1 32.40%
- TP +9 but precision loss causes F1 -2.64 percentage points

Conclusion:
- reject simple register/continuity role assignment V1;
- preserving many rhythm notes while choosing one upper lead voice is too aggressive for lead;
- Basic Pitch contains useful polyphonic evidence, but simple local role splitting cannot reliably map it into rhythm vs lead;
- do not tune this heuristic against Go My Way.

### Exact next resume instruction

1. Keep spectral bass V1 as current strongest bass research candidate.
2. Keep V4-origin timing and frozen guitar note evidence unchanged.
3. Stop simple guitar role-assignment heuristics.
4. Next direction: richer polyphonic/chord-set modeling or an alternate polyphonic transcription front end.
5. Before introducing a new model, audit available repo/dependency options for guitar-capable polyphonic transcription and/or harmonic salience representations.
6. Prefer a reference-blind candidate generation path with post-freeze professional scoring.
7. Keep `main` unchanged.


## Specialized guitar AMT V1 — launched

Reason for pivot:
- simple guitar chord-role decoder V1 failed to improve combined guitar and severely hurt lead recall;
- repo audit found two alternate front-end paths:
  - MR-MT3: previously failed its frozen Stage-A gate because zero predictions survived the predeclared guitar-program projection;
  - specialized HCQT+Mel cascaded guitar transcription model: purpose-built six-string/fret-state network with MIT-labeled code and weights.
- the older public GuitarProFX TabCNN checkpoint remains execution-blocked for commercial-use provenance and is not used here.

Pinned specialized-guitar upstream:
- code repo: `ErenReyhanlioglu/Guitar-Transcription`
- code commit: `9f8e31d2ed42c2f8d155d6164ea2fdb43e285482`
- code license: MIT
- model source blob `src/models/cnn_mtl.py`: `cfe5a8e91d7315ad43f976bc114fdaba82838fbd`
- weights repo: `ErenReyhanlioglu/Guitar-Transcription-Weights`
- weights commit: `e2be2c66a71b76ced009afcd0f6bf837c0b9b8a3`
- weights repo license: MIT
- config path: `cnn_mtl_20251210_113013/config.yaml`
- config git blob: `8fb170c504a7a43e49d65d14ae47944cee77d52e`
- fold-1 checkpoint path: `cnn_mtl_20251210_113013/fold_1/model_best.pt`
- checkpoint git blob: `82094eecad83603b331b1bfbce0f0310f8942df8`

Model contract:
- HCQT + Mel active features;
- 6 strings;
- 19 frets + silence;
- standard tuning [40,45,50,55,59,64];
- sample rate 22050;
- hop 512;
- 19-frame context;
- cascaded auxiliary heads include multipitch, hand position, string activity, pitch class;
- generic guitar output; no rhythm/lead identity during candidate construction.

Experiment:
- generate two reference-blind frozen candidates:
  1. full decoded mix;
  2. BS-Roformer guitar stem;
- convert per-string frame-state transitions to note-onset events;
- do not read professional references during candidate generation;
- freeze both candidate JSON files + hashes first;
- post-freeze score rhythm, lead, and combined guitar against V4-origin timing;
- no threshold search or model mutation.

Files:
- `analyzer/gomyway_specialized_guitar_amt_freeze_v1.py`
- `analyzer/score_gomyway_specialized_guitar_amt_v1.py`
- `.github/workflows/astra-gomyway-specialized-guitar-amt-v1.yml`

Commits:
- freezer: `a8e9f694c8fe108fef02893d11be64cc37f7c2f4`
- scorer: `2f3b0d9d44bfe86116bdd43e0274cb0b7a1a08b2`
- workflow launch: `1f83cd483bb7a8e3efa65ce3cf82c36c1e6f5bee`

Authoritative run:
- run `37158683727`
- head `1f83cd483bb7a8e3efa65ce3cf82c36c1e6f5bee`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37158683727

### Exact next resume instruction

Resume from run `37158683727`.
If green:
1. record frozen candidate artifact ID/digest;
2. record exact config/checkpoint SHA-256 values emitted by workflow;
3. record full-mix vs guitar-stem prediction counts;
4. record score artifact ID/digest and per-input rhythm/lead/combined TP/P/R/F1;
5. compare both candidates against Basic Pitch V4 baseline:
   - rhythm F1 31.82%;
   - lead F1 17.84%;
   - combined guitar F1 35.04%;
6. if specialized model materially improves combined guitar or lead, continue with its direct string/fret outputs;
7. if both candidates underperform, stop generic front-end swapping and revisit training a clean Guitar-TECHS-derived model;
8. preserve spectral bass V1 as strongest bass research candidate;
9. keep `main` unchanged.


## Guitar chord-role decoder V1 — authoritative result

Run `37158385869` is actually GREEN at the workflow level:
- freeze-candidate: SUCCESS
- score-after-freeze: SUCCESS
- run conclusion: SUCCESS

Artifacts:
- frozen candidate id `11285559715`
- frozen candidate digest `sha256:795ebbdd20ec1723ef8a45d54d0caee88c30a70f47bfec7aba5f51406e6ab31f`
- score artifact id `11286890764`
- score digest `sha256:fa150224cd992f11c6b4ae58cf95bfa05553b8b5a13a1ad5e30b74c68a0bb928`
- score JSON SHA-256 `41c2aaa360aec1a843487fffe19be6d7d448ee18cebce58ce8bd332b0d21f415`

Scientific result:

Rhythm:
- original TP 320, F1 31.82%
- decoded TP 320, F1 31.87%
- essentially neutral (+0 TP, +0.05 percentage points F1)

Lead:
- original TP 133, F1 17.84%
- decoded TP 40, F1 11.36%
- delta TP -93
- delta F1 -6.48 percentage points

Combined guitar:
- original TP 427, F1 35.04%
- decoded TP 436, F1 32.40%
- TP +9 but precision loss causes F1 -2.64 percentage points

Conclusion:
- reject simple register/continuity role assignment as a general guitar decoder;
- Basic Pitch contains useful polyphonic evidence, but a hand-written role splitter cannot reliably separate lead from rhythm;
- do not tune these role-selection weights against Go My Way;
- next direction should inspect richer front-end evidence or a different polyphonic transcription model rather than further heuristic role assignment;
- preserve spectral bass V1 as strongest bass research candidate;
- keep V4-origin timing and frozen note evidence unchanged;
- keep `main` unchanged.


## Guitar chord-role decoder V1 — workflow green, scientific failure

Run `37158385869` completed successfully at the workflow level.
Artifacts:
- frozen candidate id `11285559715`, digest `sha256:795ebbdd20ec1723ef8a45d54d0caee88c30a70f47bfec7aba5f51406e6ab31f`
- score artifact id `11286890764`, digest `sha256:fa150224cd992f11c6b4ae58cf95bfa05553b8b5a13a1ad5e30b74c68a0bb928`
- score JSON SHA-256 `41c2aaa360aec1a843487fffe19be6d7d448ee18cebce58ce8bd332b0d21f415`

Scientific result:
- rhythm: TP 320 -> 320, F1 31.82% -> 31.87% (essentially neutral)
- lead: TP 133 -> 40, F1 17.84% -> 11.36% (large failure)
- combined guitar: TP 427 -> 436, F1 35.04% -> 32.40% (precision loss)
- reject simple register/continuity role assignment;
- do not tune this heuristic against Go My Way.

## Raw Basic Pitch guitar activation freeze V1 — launched

Purpose:
- inspect richer pre-threshold Basic Pitch evidence from the separated guitar stem;
- determine whether useful chord tones exist below current note-event thresholds before replacing the front end.

Reference-blind construction:
- immutable source audio;
- frozen BS-Roformer guitar stem;
- Basic Pitch 0.4.0 exact model SHA `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`;
- save raw `model_output` arrays from Basic Pitch `predict()` to compressed NPZ;
- no professional references, no threshold search, no candidate correction.

Files:
- `astra_backend/evaluation/gomyway_freeze_basic_pitch_guitar_activations_v1.py`
- `.github/workflows/astra-gomyway-freeze-basic-pitch-guitar-activations-v1.yml`

Commits:
- initial implementation `dbac6746d574a67832bc74b3958fc5380477e091`
- corrected model identity `d28e223c391a53b8ee38534d698e6da074f9b45c`
- workflow launch `53486477f9df3ff70abd88c8461c98a9a4a74fcd`

Authoritative run:
- run `37159748378`
- status at this update: QUEUED
- monitor: https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37159748378

### Exact next resume instruction

Resume from run `37159748378`.
If green:
1. record artifact ID/digest and NPZ/metadata JSON hashes;
2. record Basic Pitch model-output keys, array shapes, ranges, and thresholded note-event count;
3. build a diagnostic that samples raw activation energy at professional target onset/pitch positions only AFTER the raw activation artifact is frozen;
4. compare activation strength for:
   - exact target pitch;
   - octave aliases;
   - nearby chord tones;
   - targets absent from thresholded note events;
5. decide whether sub-threshold evidence is recoverable by a better decoder or whether the polyphonic guitar front end itself should be replaced;
6. preserve spectral bass V1, V4-origin timing, frozen note evidence, and `main`.


## Explicit handoff — raw Basic Pitch guitar activation phase

Current scientific state:
- V4-origin timing remains the strongest Go My Way research timing candidate.
- Spectral bass octave V1 remains the strongest bass research candidate:
  - TP 372
  - F1 60.10%
- Simple guitar chord-role decoder V1 is rejected:
  - rhythm essentially neutral;
  - lead degraded strongly;
  - combined-guitar F1 degraded.
- Therefore do NOT continue tuning hand-written rhythm/lead register/continuity rules on Go My Way.

Latest guitar interpretation:
- Basic Pitch thresholded note events contain useful polyphonic evidence, but the thresholded event list is likely discarding sub-threshold chord tones and harmonic evidence.
- Next phase should inspect/freeze raw Basic Pitch activation tensors from the separated guitar stem before any note-event thresholding.
- Do not change V4-origin timing.
- Do not tune thresholds against the professional reference.

Work already started:
- added `astra_backend/evaluation/gomyway_freeze_basic_pitch_guitar_activations_v1.py`
- implementation commit: `dbac6746d574a67832bc74b3958fc5380477e091`
- purpose: save raw Basic Pitch model-output arrays to compressed NPZ plus metadata JSON from the frozen separated guitar stem.
- no workflow has been launched yet for this activation freeze.

Important correction discovered before launch:
- the new activation-freeze script currently contains the WRONG hard-coded Basic Pitch model SHA:
  - currently in script: `206bc0de22c9c9e4d5710ee9f32ca7316ad70d8e5d6f0838887e772aa143866d`
- the authoritative frozen Basic Pitch SHA already used by the existing full-song benchmark is:
  - `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`
- fix this hash BEFORE creating or launching the workflow.
- do not weaken or remove the hash check.

### Exact next resume steps

1. Edit `astra_backend/evaluation/gomyway_freeze_basic_pitch_guitar_activations_v1.py`:
   - replace the incorrect expected Basic Pitch SHA with:
     `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`
   - leave Basic Pitch version and frozen inference settings unchanged.

2. Create a new workflow for raw guitar activation freeze:
   - immutable source: `public/gomywayfullaitest.m4a`
   - verify git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`
   - BS-Roformer FP16 SHA `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`
   - Basic Pitch 0.4.0 model SHA `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`
   - separate guitar stem once;
   - run Basic Pitch `predict()` with the frozen defaults;
   - save raw model-output tensors to NPZ;
   - save metadata JSON containing tensor keys/shapes/statistics, guitar-stem SHA, model SHA, thresholded note count, and NPZ SHA.
   - do NOT read professional rhythm/lead references in this freeze job.

3. Freeze and upload the activation artifact before any reference analysis.

4. After freeze, build a separate diagnostic job that reads the frozen activation tensors plus V4-origin timing and professional references only for analysis.
   Measure:
   - activation strength at target MIDI/time for rhythm and lead;
   - activation strength at target pitch class in neighboring octaves;
   - how often a target absent from thresholded notes still has substantial sub-threshold activation;
   - onset-vs-frame activation separately if both arrays are available;
   - activation rank of the target pitch within the local chord/onset frame;
   - difference between rhythm and lead recovery potential.

5. Do NOT threshold-search against Go My Way in the same diagnostic.
   The first activation diagnostic is descriptive/attribution only.

6. Decision after diagnostic:
   - if many missing guitar targets have strong sub-threshold activation, build a separately versioned reference-blind decoder using frozen activation evidence;
   - if target activation itself is weak/absent, Basic Pitch has reached its front-end limit for this material and evaluate a different polyphonic transcription front end.

7. Preserve:
   - V4-origin timing candidate;
   - frozen note-evidence artifact `11282827368`;
   - spectral bass V1 as current strongest bass candidate;
   - all old timing maps/results;
   - `main` unchanged.

8. Do not resume:
   - timing tuning;
   - local guitar octave heuristics;
   - register/continuity role splitting;
   - threshold optimization against the Go My Way professional reference.

This section is the authoritative resume point for the next model.


## Raw Basic Pitch guitar activation diagnostic V1 — prepared, not launched

Freeze run:
- authoritative freeze run: `37159748378`
- head: `53486477f9df3ff70abd88c8461c98a9a4a74fcd`
- current observed state at this checkpoint: IN PROGRESS
- completed successfully through immutable-source verification, source decode, and BS-Roformer download/SHA verification
- current active step: `Separate guitar stem`
- no activation artifact exists yet, so no professional-reference activation analysis has been launched

Post-freeze diagnostic prepared:
- `astra_backend/evaluation/gomyway_basic_pitch_guitar_activation_diagnostic_v1.py`
- commit `c261c3caef82daa6058ae8127622e13a7b1fadc6`
- `.github/workflows/astra-gomyway-basic-pitch-guitar-activation-diagnostic-v1.yml`
- commit `908720e3be36322950ab806346d4cfe9d81b8e83`
- workflow trigger is MANUAL ONLY (`workflow_dispatch`) so preparation cannot accidentally read professional references before freeze completion

Frozen diagnostic contract:
- download raw activation artifact only from run `37159748378`;
- verify NPZ SHA against frozen metadata;
- verify V4-origin timing SHA remains `b87f122a007070d5a2abf0b676693c5ea7872ffcb04a06958ef103269c5f85f3`;
- use existing frozen thresholded note evidence from run `37146481347`;
- read rhythm/lead professional references only in the diagnostic job after activation freeze;
- descriptive only: no threshold search, no pitch correction, no candidate mutation;
- measure exact target frame/onset activation, octave-alias activation, nearby semitone activation, target pitch rank, and missing-thresholded-event activation;
- fixed descriptive bins and the existing Basic Pitch 0.5 onset / 0.3 frame thresholds are attribution markers only, not tuned decoder thresholds.

### Exact next resume instruction

1. Resume from freeze run `37159748378`.
2. If the freeze run fails, inspect the failed job/log and repair only the failure; do not launch the diagnostic.
3. If the freeze run is green:
   - record artifact ID/digest;
   - record NPZ SHA and metadata JSON SHA;
   - record model-output keys/shapes/ranges and thresholded note-event count;
   - verify the frozen artifact before any reference analysis.
4. Only after that verification, manually dispatch `Astra Go My Way Basic Pitch Guitar Activation Diagnostic V1`.
5. When diagnostic is green, record its artifact ID/digest and JSON SHA, then summarize rhythm vs lead:
   - exact target activation distributions;
   - octave-alias strength;
   - nearby semitone/chord-neighbor strength;
   - pitch-rank distributions;
   - missing-thresholded-event counts with activation at/above the already-frozen Basic Pitch defaults.
6. Decide from that descriptive evidence whether a new reference-blind activation decoder is justified or whether Basic Pitch's guitar front end should be retired for this material.
7. Preserve spectral bass V1, V4-origin timing, frozen note evidence, and `main` unchanged.
