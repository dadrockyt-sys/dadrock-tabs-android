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
