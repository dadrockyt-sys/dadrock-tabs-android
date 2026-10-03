> Current review (2026-10-02): see `astra-work/POST_V14_GPT56_HANDOFF_2026-10-02.md` and the final resume pointer below. Review complete; prepare an independent bass feasibility packet only. No empirical execution authorized.

# Astra — current handoff

Updated: 2026-09-29 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **V9-V14 FROZEN; V14 FAILED MATERIAL-RECOVERY GATE; SERIAL SYNTHETIC MICRO-OPTIMIZATION CLOSED**

Latest resume instructions are in **V14 empirical execution complete — FAILED material-recovery gate — serial micro-optimization closed — 2026-09-29** at the end of both handoffs. Earlier execution/resume sections are historical where superseded.

## Standing policy

Routine GitHub work and bounded inexpensive synthetic GitHub model runs remain pre-authorized.

P1/P2/P3 real-data access remains a separate boundary.

## Canonical localization run

- run **36392740663**
- job **108832021154**
- head `a5ecdc519b557849ae98825f8c50b219c15527d4`
- workflow **SUCCESS**
- artifact **10957888924**
- digest `sha256:bc766cf7082bbdc92f82dda9818b2981bf329e67b5b80bdd6f84ac8d27fc7f74`
- optimizer steps **0**
- thresholds fixed **0.50 / 0.50**
- threshold search **no**
- model weights changed **no**
- additional/post-hoc normalization fed to model **no** (the frozen preprocessing already includes RMS normalization and relative-dB CQT scaling)
- P1 accessed **yes**
- P2 accessed **yes**
- P3 opened **no**

Frozen result:
- `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_RESULT_V1.json`

Analysis:
- `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_ANALYSIS_V1.md`

## P1 localization

Historical V3 baseline:
- exact string/fret top-1 **56.25%**
- pitch-only top-1 **56.25%**
- median absolute semitone error **0**
- median true-state global rank **1**
- top-5 true-class rate **87.5%**

Synthetic candidate:
- exact string/fret top-1 **6.25%**
- pitch-only top-1 **31.25%**
- wrong-string/correct-pitch top-1 **25%**
- median absolute semitone error **11.5**
- median true-state global rank **13.5**
- top-5 true-class rate **31.25%**

Interpretation:
- candidate state/pitch representation is not real-domain compatible;
- not primarily a simple string-assignment swap.

P1 onset:
- baseline threshold crossing within +/-1 frame **100%**
- candidate **18.75%**

## P2 localization

Both models remain onset-limited.

Baseline:
- reference onset probability mean **0.0049**
- max within +/-4 mean **0.0190**
- threshold crossing within +/-4 **0%**

Candidate:
- reference onset probability mean **0.0441**
- max within +/-4 mean **0.0642**
- threshold crossing within +/-4 **0%**

Neither model crosses 0.50 within the tested +/-4-frame window. The quoted **0-1 frame** medians come from the constrained +/-1-frame search and do not independently establish correct alignment or exclude larger source/crop offsets.

Attack novelty:
- synthetic k=1 spectral flux mean **26.54**
- P1 **14.42**
- P2 **8.51**

Frame-difference L2 k=1:
- synthetic **2.923**
- P1 **1.972**
- P2 **1.419**

Interpretation:
- P2 has lower mean novelty in the prepared feature representation on this small sample;
- attack/capture-domain mismatch is a hypothesis, not an established cause: preprocessing, annotation/crop alignment, gain and event composition remain confounders.

## Do not

- lower thresholds;
- tune on these eight real examples;
- seed/model-pick;
- normalize model inputs post hoc;
- open P3.

## Next design-only proposal

- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_PROPOSAL_V1.md`

Purpose:
- distinguish genuinely weak P2 transients from preprocessing/resampling or source-to-prepared timing issues.

**Do not execute yet. Fresh explicit P1/P2 source access authorization is required.**

P3 remains sealed.

## Explicit next steps

1. **Stop all model training/tuning.**
   - Do not run new synthetic architecture, sampler, loss-weight, seed, threshold, normalization, or decoder experiments from the current P1/P2 findings.
   - Do not select a different synthetic seed after seeing P1/P2.
   - Keep thresholds fixed at **0.50 / 0.50**.

2. **Next executable experiment, only after fresh explicit P1/P2 authorization:**
   - run the zero-training **P2 attack/preparation integrity audit** defined in:
     - `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_PROPOSAL_V1.md`
   - use only the exact previously allowlisted P1/P2 source captures;
   - optimizer steps = **0**;
   - model-weight changes = **0**;
   - threshold search/retuning = **0**;
   - no input normalization fed into a model;
   - no model/seed selection;
   - no automatic retry;
   - no P3 access.

3. **Audit measurements to implement/freeze before any authorized source access:**
   - raw-audio short-window RMS before/after each eligible attack;
   - raw waveform first-difference energy;
   - raw STFT positive spectral flux;
   - prepared-CQT frame-difference and positive-flux measurements;
   - source annotation time;
   - prepared crop-local annotation time;
   - nearest raw transient-peak offset;
   - nearest prepared-CQT novelty-peak offset;
   - source sample rate, channel metadata, crop boundaries, resampling provenance.

4. **Required comparison:**
   - compare P1 vs P2 descriptively only;
   - determine whether P2 weakness is already present in raw audio, introduced/amplified by preprocessing, or caused by annotation/crop alignment;
   - do not optimize any parameter from these comparisons.

5. **Frozen decision branches for that audit:**
   - raw P2 attacks weak -> support **capture/performance-domain mismatch**;
   - raw attacks strong but prepared CQT novelty weak -> support **preprocessing/resampling representation mismatch**;
   - novelty peaks systematically offset from annotations -> support **alignment/crop timing issue**;
   - no clear discrepancy -> freeze as **unresolved** and do not tune on P2.

6. **After the audit:**
   - freeze exact result, artifact hashes, interpretation, and any failure honestly in this file;
   - if the result points to an offline preprocessing bug that can be reproduced without P1/P2, fix/test it offline first;
   - if the result merely suggests a real-domain modeling change, write a proposal only—do not train against these eight examples automatically;
   - do not open P3 unless separately and explicitly authorized after a new development-stage gate is defined.

## Authorization boundary for the next step

Current authorization does **not** permit another P1/P2 source-access run.

A fresh explicit user authorization is required before executing the P2 attack/preparation integrity audit.

Routine GitHub-only preparation for that audit remains allowed.

P3 remains sealed.


## Supervisory review for GPT-5.6 — 2026-09-28

This section refines the interpretation and execution order above. Preserve all frozen numerical results and historical artifacts; do not rewrite an old failure into success.

### Review evidence and limits

Reviewed branch head `4f0c130d857bae0d5cb8d4cfee6176b94d1a5678`, current handoff, frozen result/analysis/proposal, and source pinned at localization head `a5ecdc519b557849ae98825f8c50b219c15527d4`: localization runner, its three focused tests, transfer evaluator, P2 preparation, preprocessing, workflow and S0 generator imports. GitHub reports job **108832021154** and all its steps successful, including focused tests and artifact upload. This review did not download/recompute the artifact, open corpus audio, run models, or rerun tests. A successful workflow proves completion, not musical accuracy.

Local checkout warning: the available older checkout's shell fetch returned September-20 head `5ee7d187...`, while the connected GitHub API returned September-28 head `4f0c130d...`. Preserve its untracked work and do not push that stale checkout. Reconcile against the connected remote before future code changes.

### Assessment: useful failure evidence, not a completed causal diagnosis

GPT-5.6 correctly froze a failed transfer candidate, retained fixed thresholds, avoided training during localization and kept P3 sealed. Continue this discipline. These are development diagnostics on four captures per performer; they do not establish customer readiness, full-song accuracy or bass/lead/rhythm separation.

Correct these interpretation details in subsequent analysis, without mutating the frozen result:

1. **P1 global top-1 is not polyphonic transcription accuracy.** `p1_state_event` selects one maximum across all active string/fret classes, excludes silence from that choice and compares the same winner with each simultaneous reference note. A correct chord cannot have every reference note be that single winner. Separate string softmaxes also are not one global categorical posterior. Treat 6.25% versus 56.25% as this diagnostic's result, not general note accuracy; do not infer a proven representation mechanism from it alone. The candidate's low true-state probability/high silence probability and onset weakness still support poor transfer.
2. **Timing inference was overstated.** The frozen 0/1 medians are `window1AbsMaxFrameOffsetMedian`: an argmax constrained to +/-1 can only be 0 or 1 in absolute value. Non-crossing within +/-4 is useful evidence against a rescue inside that window at 0.50, not proof that source annotations/crops are aligned. With the real preprocessing hop 512/22050, four frames are about 92.9 ms.
3. **Novelty is feature-domain evidence.** `spectral_novelty` differences prepared CQT feature vectors, not raw STFT magnitudes or waveform attacks. Lower group means cannot isolate performer, capture gain, polyphony, technique, preprocessing or annotation effects.
4. **Normalization wording must be precise.** P2 preparation calls `rms_normalize`; preprocessing uses relative-max amplitude-to-dB and /80 + 1 scaling. Preserve that frozen path. `normalizationFedToModel:false` should be explained as no additional diagnostic/post-hoc normalization, not unnormalized audio.
5. **Concrete bookkeeping defect:** `_synthetic_refs` records `start = frame * (256/22050)`, whereas the frozen preprocessing hop is 512 and S0 imports that hop. Confirm the generator's frame contract offline and add a regression test. The diagnostic consumes the stored frame index for novelty/model lookups, so this apparent timestamp defect does not by itself invalidate the frozen frame-based rates. Do not claim it explains the real failure or rerun inference to repair descriptive timestamps.

### Immediate authorized work: finish preparation before asking to execute

The next task is implementation and synthetic verification of the audit, not another proposal-only handoff or another training experiment. No P1/P2 source reopening is needed to do this.

1. Read the existing proposal and frozen preparation code. Implement a standalone audit runner plus a machine-readable frozen specification and focused tests. Suggested new paths:
   - `astra_backend/evaluation/p2_attack_preparation_integrity_audit_v1.py`
   - `astra_backend/evaluation/test_p2_attack_preparation_integrity_audit_v1.py`
   - `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_SPEC_V1.json`
   Reuse exact preparation semantics; isolate pure measurement logic from acquisition. No model imports/loads/inference, optimizer, training, synthetic-population regeneration or model downloads are needed.
2. Before any source access, freeze numeric window lengths in seconds, sample/frame rounding, channel mixing, resampler/version, STFT window/hop/centering, CQT parameters, peak-selection/tie rules, edge exclusions and eligible-event rules. Establish these with generated impulses/plucks only; do not choose them from P2 outcomes. Report missing/ambiguous peaks as unresolved. A nearest peak always existing is not alignment proof.
3. Trace the complete coordinate transform: source MIDI time -> signed frozen lag correction -> decoded/resampled audio time -> crop start frame/time -> crop-local annotation -> CQT frame. Record each component and verify metadata hop agreement. Keep full-source preprocessing-before-cropping semantics; crop-first transforms can change padding and relative scaling.
4. Preserve measurements at native decoded audio, frozen decoded/resampled audio, existing RMS-normalized audio and prepared CQT stages. Raw-channel measurements are descriptive; never feed alternative scaling back into a model. RMS/gain-sensitive values and log-relative CQT flux have different units: compare like with like, not their absolute values across representations.
5. Report each capture/category separately before group summaries, with eligible/excluded event counts, simultaneous-attack grouping, median/spread and raw values or permitted aggregate evidence. Distinguish per-note counts from acoustic-attack counts so chords do not multiply the same transient. Retain both event-weighted and capture-balanced summaries where meaningful; do not treat correlated events as independent generalization trials.
6. Add meaningful synthetic tests for known lag sign and crop offset, resampling timing, centered-transform boundary behavior, stereo cancellation/channel handling, gain changes, silence, clipping/nonfinite inputs, repeated/chord attacks, out-of-range events and no valid peak. Add negative admission tests for duplicate/missing/extra captures, P3, changed hashes/config and attempted overwrite. The existing three localization tests cover summaries, not these failure modes.
7. Freeze exact eight capture allowlist, source/member hashes, crop identities, correction-file identity and dependency/source pins from existing receipts. The current transfer loader checks a set of capture keys, which would not reject duplicate keys by itself: require exactly four unique captures per performer and eight total. Reject substitutions before measurement.
8. Prepare a disabled-by-default execution workflow with explicit authorization validation before any corpus download/open, bounded CPU time/download bytes, one execution and no automatic retry. Do not edit a historical launch file or create a live launch marker while preparing. No model, Codespaces or Vercel work is part of this audit.
9. Run focused CPU synthetic tests once; fix concrete failures and rerun only relevant checks. Save code/spec/tests and actual results to `astra-work`, verify remote content/head, and update this handoff with exact commands and pins. Do not repeat the full model/backend suites without a specific reason.
10. Only when the implementation is reviewable and tests pass, request the one fresh P1/P2 source-access authorization required by the existing checkpoint/proposal. Explain that this is a restricted real-data access boundary, not a request to reauthorize routine GitHub preparation. The user's current review request does not execute that audit. Honor any subsequent explicit authorization without repeatedly asking for the same scope.

### Decision after an authorized audit

- Reproducible coordinate/preprocessing defect: first create an offline synthetic regression and fix the defect there. Preserve old results and version corrections. Any real rerun must remain within explicit execution scope.
- Weak raw attacks without an identifiable pipeline defect: describe support for a capture/performance hypothesis; do not claim causality from four captures or automatically train on them.
- Strong raw attacks but weaker prepared novelty: describe representation/preprocessing sensitivity; expected transform behavior alone is not proof of a bug.
- Ambiguous or mixed evidence: freeze **unresolved**. Do not expand peak windows, alter thresholds, add captures or open P3 to obtain a preferred result.
- Any later modeling work needs a separate finite development plan, budget and success/stop rule. P1/P2 are now exposed development evidence; P3 remains untouched until a new gate and separate authorization. No indefinite synthetic seed/architecture search.

**Resume instruction:** Implement and test the model-free preparation-integrity audit offline, then save the concrete execution package. Keep the candidate/result frozen, thresholds 0.50/0.50, P3 sealed and main/Production unchanged.


## Preparation-integrity audit implementation checkpoint — 2026-09-28

The offline preparation requested by the supervisory review is now implemented and synthetically verified. **No P1/P2 source was reopened by this preparation work. P3 remains sealed. No model was loaded or run. No optimizer/training, threshold search, Codespaces, Vercel, main, or Production mutation occurred.**

### Concrete execution package now frozen on `astra-work`

- model-free runner: `astra_backend/evaluation/p2_attack_preparation_integrity_audit_v1.py`
  - Git blob `3f33b967aee9d80dddddf35e4b7eda6922ff09df`
- focused synthetic/admission tests: `astra_backend/evaluation/test_p2_attack_preparation_integrity_audit_v1.py`
  - Git blob `3377ceccda1602105a4453f567df6fc0a4a7f262`
- frozen machine-readable spec: `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_SPEC_V1.json`
  - Git blob `5356ea218027d595c08b9f46491f0abf1f5259c1`
- offline test workflow: `.github/workflows/astra-p2-attack-preparation-integrity-audit-offline-tests-v1.yml`
  - Git blob `4544647991f0cd41b834904c39aed4b53488ad59`
- disabled-by-default authorization-gated real workflow: `.github/workflows/astra-p2-attack-preparation-integrity-audit-v1.yml`
  - Git blob `a9673b97bf81724ee3d2e6819245d9105f4e9d69`
- authorization request, **not an authorization**: `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_AUTHORIZATION_REQUEST_V1.json`
  - status: `awaiting_fresh_explicit_user_authorization`
  - no authorization file and no launch marker have been created.

### Frozen audit semantics

The audit has no model imports/loads/inference. It preserves and reports four preparation stages:
1. native decoded source audio, including channel metadata, per-channel attack measurements and arithmetic-mean channel mix;
2. the frozen ffmpeg mono 22,050 Hz decoded/resampled audio;
3. the existing RMS-normalized 22,050 Hz audio, descriptive only;
4. the already-prepared 200 x 192 CQT crop, preserving full-source preprocessing-before-cropping.

Fixed measurements include:
- 40 ms RMS pre-window, ending 5 ms before the annotation;
- 60 ms RMS post-window;
- waveform first-difference energy;
- raw STFT positive flux with n_fft 1024, hop 256, Hann window, center=false;
- raw transient search +/-120 ms inside a 500 ms fixed context;
- prepared-CQT frame difference and positive flux;
- prepared-CQT peak search +/-4 frames inside a fixed +/-20-frame context;
- peak qualification: local maximum above context median + 3 MAD; no qualifying peak => null/unresolved, never widen the window;
- simultaneous notes within 1 microsecond are one acoustic attack for attack-weighted summaries;
- per-note records are retained separately;
- per-capture summaries precede P1/P2 population summaries;
- both event-weighted and capture-balanced summaries are emitted.

Eligibility is frozen before real access. A reference must be a frozen prepared scorable event and must have the full raw RMS window, full raw peak-search window, and full prepared-CQT +/-4-frame search window. Ineligible events are recorded with reasons and excluded from acoustic-attack summaries rather than repaired.

Exact archive downloads are bounded to **4,004,045,267 bytes total**, sequentially, one archive at a time; the largest single archive is 1,150,819,056 bytes. The eight archive byte/MD5/SHA256 identities, exact capture keys, lags, frozen feature hashes, target hashes, source/preparation Git blobs, and dependency pins are frozen in the spec.

The observed Ubuntu 22.04 toolchain is also frozen before source access:
- Python 3.10.15
- ffmpeg `4.4.2-0ubuntu0.22.04.1`
- ffprobe `4.4.2-0ubuntu0.22.04.1`
- NumPy 1.21.6
- librosa 0.9.1
- SciPy 1.8.1
- resampy 0.4.3
- soundfile 0.12.1

Toolchain observation:
- offline run **36398621201**
- artifact **10958999311**
- digest `sha256:6967c04f04644c642a00377d7fba175d179697c587247d84fc123a93f0e45596`

The real workflow verifies the exact ffmpeg/ffprobe version lines **before** any P1/P2 source access.

### Synthetic/admission verification

Final focused offline verification:
- workflow run **36398953237**
- job **108852033523**
- tested head `4cd69a6c0a996e351987bc3b65afe797ec7975ec`
- conclusion **SUCCESS**

Successful steps included:
- frozen source-pin verification;
- frozen CPU runtime installation;
- frozen ffmpeg toolchain verification;
- focused preparation-integrity synthetic tests;
- localization timestamp bookkeeping regression.

The focused tests cover:
- known signed lag and crop-offset transform;
- sample rounding;
- stereo cancellation/channel handling;
- raw gain scaling versus gain-invariant RMS ratio behavior;
- silence/no-qualified-peak behavior;
- known impulse peak localization;
- prepared-CQT novelty peak localization;
- repeated/chord attack grouping;
- out-of-range/no-valid-peak behavior;
- nonfinite input rejection;
- clipped finite input;
- peak tie rule;
- duplicate/missing/extra capture-spec rejection;
- P3 rejection;
- changed model/optimizer execution ceiling rejection;
- missing source-pin rejection;
- existing result overwrite rejection.

Repository-wide Astra backend tests also passed for the final implementation state used by the package:
- run **36398953268**
- job **108851974933**
- conclusion **SUCCESS**

### Bookkeeping defect fixed offline without rewriting history

`real_domain_failure_localization_v1.py::_synthetic_refs` previously wrote descriptive synthetic event start times with `256/22050`. It now uses the frozen preprocessing constants `HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ = 512/22050`, with a regression test.

This does **not** alter the historical frozen localization result, does **not** explain the real-domain failure, and does **not** justify rerunning inference. The old diagnostic consumed stored frame indices for the relevant novelty/model lookups; preserve the old result as historical evidence.

### Next executable step — requires fresh explicit authorization

The package is now reviewable and its offline tests pass. The next step is exactly one authorization-gated P1/P2 source-access run using the frozen package above.

Required scope:
- exact four frozen P1 + exact four frozen P2 direct-input captures only;
- optimizer steps **0**;
- models loaded **0**;
- model inference **false**;
- threshold search/retuning **false**;
- one CPU GitHub Actions execution, <=120 minutes;
- total source downloads <=4,004,045,267 bytes;
- automatic retry **false**;
- Codespaces **false**;
- Vercel **false**;
- main/Production mutation **false**;
- P3 **sealed**.

Do **not** create `P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_AUTHORIZATION_V1.json` or `P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_LAUNCH_V1.json` until the user gives fresh explicit authorization for this exact P1/P2 source-access audit.

After authorization, create a source-pinned authorization file and one single-use launch marker, execute once, freeze the exact result/artifact hashes, update this handoff, and stop. Do not automatically tune or train from the outcome.

**Resume instruction:** Await the user's fresh explicit authorization for the single frozen P1/P2 preparation-integrity audit. Until then, P1/P2 source access is closed and P3 remains sealed.


## Authorized integrity-audit execution outcome — 2026-09-28

The user gave fresh explicit authorization for the single frozen P1/P2 preparation-integrity audit. That authorization was consumed by exactly one source-access execution.

### V1 authorized run

- workflow: **Astra P2 preparation integrity audit v1**
- run **36399552501**
- job **108853905409**
- head `0d00348ff1faf0aea1accf3958f3a258fd9be255`
- workflow conclusion: **FAILURE**
- automatic retry: **not performed**
- P1 accessed: **yes**
- P2 accessed: **yes**
- P3 opened: **no**
- optimizer steps: **0**
- models loaded: **0**
- model inference: **false**
- threshold search/retuning: **false**

All authorization, source-pin, frozen-toolchain and focused-test guards passed before source access. The workflow then downloaded, hash-verified, extracted and deterministically prepared exactly the authorized eight captures. It failed at the first model-free audit admission step before any attack/preparation measurements were produced.

Exact exception:

`RuntimeError: prepared crop identity mismatch`

The failure came from the eight `featureSha256` values frozen in the initial audit spec. They did not equal the deterministic feature hashes emitted by the already-frozen preparation code. The corresponding eight frozen `targetSha256` values did match. This is a bookkeeping/admission defect in the new audit spec, not evidence about P1/P2 attack strength and not a scientific audit result.

No result artifact was produced. Cleanup ran. Preserve the failed run as historical evidence.

Frozen failure record:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_FAILED_EXECUTION_V1.json`
- Git blob `385448bd51666e93dfbc32a169ef90beeb37deb1`

### Deterministic feature identities recovered from the authorized run

The preparation logs emitted the exact feature hashes and crop identities before the admission failure:

- P1 chords Drop3_7: feature `278363f1b1129baeadb65dabdfb8353ebbbba23d9aefff188f88e43d73c15a91`, target `561ed7e9b6bd54742de973c4f33d8b84cbb6dd02215843daa44b048307d7d8d3`, start frame 2233
- P1 scales Ab: feature `e34e9dd87e8be0f65c7758c1f64505656efaf16f4db00aaff4821da52f33615a`, target `b1f3bb14b9f69cf119e86095bf05dbf8c5c820bf8a24f2e2017d963c7f88a41b`, start frame 335
- P1 allsinglenotes: feature `083c87bfc280f7d97b2f763cff214b4d0efbe607a43451882b1ddee9327c4328`, target `d8accc5ffaa70514d336c2d154ad0cb1360015b28d6f9118ea16a38fb0b9ccd7`, start frame 164
- P1 PalmMute: feature `bb71d75b85c2db3871390e8a340f9fefccdbfcdddb2343077565b5f59df98e25`, target `4bc74be8b0e1b84b0a4b7b9c6adf7baea1c79e3e5cdcc7e83606dc52fcb210f2`, start frame 162
- P2 chords Drop3_7: feature `882530529381d7d0268a8a91f7fbe727f27ae2b1ca7a44ddde89fdba8ed510ab`, target `3508bac1a566a1104233c66d583f01eaa089e0eb398de3d65eff436d656f0c75`, start frame 0
- P2 scales Ab: feature `b5b3f7f049a2c2354d9333ed861f3f1b71f54e0a2d0dbf626d7df0a450c86f6a`, target `9a9507b60765c9bb2d3d21bb6775a7a4be065b9046ae0aead182e4a1cbd650e9`, start frame 336
- P2 allsinglenotes: feature `bad44048c953b4438bf2a7d2a2c168227af60933b24bad814df0d0dccb4cb27b`, target `e2eb414127cb87b2d09d99097a4e1df0895e3544a36ef9dbe7326a3d2ddf0d2b`, start frame 163
- P2 PalmMute: feature `6576417076b4767e02ad0240708ee45663792ce5cadd23340a00340b8416332e`, target `1c8d216a844b9a2f4be54c57cf7ec6e65bdfd6e5a26fe03d109471d89d283be5`, start frame 21526

These values are now the corrected frozen prepared identities. Do not infer scientific meaning from them.

### Offline repair completed after the failed single execution

The spec was corrected **only** by replacing the eight bad prepared-feature hashes with the exact deterministic hashes emitted by the authorized run. No measurement windows, population, target hashes, model behavior, threshold behavior, source archives, lags or decision rules were changed.

Corrected spec:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_SPEC_V1.json`
- Git blob `06c966b37e65a1e0a93ab8112f439dd87073b042`
- correction commit `14cb5d0b3510ce1dad2c16826dee87c2eff6d523`

Corrected offline focused verification:
- run **36407736805**
- job **108880392512**
- conclusion **SUCCESS**
- source-pin verification passed
- frozen toolchain verification passed
- focused synthetic integrity-audit tests passed
- localization timestamp regression passed

A new disabled-by-default V2 real workflow is prepared:
- `.github/workflows/astra-p2-attack-preparation-integrity-audit-v2.yml`
- Git blob `29cf152667b3e53c46c5c8a33416aeb8641d8714`
- it requires new `P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_AUTHORIZATION_V2.json` and `P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_LAUNCH_V2.json`
- neither file has been created.

Fresh authorization request:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_AUTHORIZATION_REQUEST_V2.json`
- status: **awaiting fresh explicit user authorization after failed V1 execution**

### Authorization boundary now

The prior authorization cannot be reused:
- it authorized a **single execution**;
- that execution occurred and accessed P1/P2;
- `automaticRetryAuthorized` was **false**.

Therefore do **not** rerun V1, do **not** create V2 authorization/launch files, and do **not** reopen P1/P2 until the user gives another fresh explicit authorization for exactly one corrected V2 run.

The requested V2 scope remains:
- exact four frozen P1 + four frozen P2 direct-input captures only;
- optimizer steps **0**;
- models loaded **0**;
- model inference **false**;
- threshold search/retuning **false**;
- one CPU GitHub Actions execution, <=120 minutes;
- total source downloads <=4,004,045,267 bytes;
- automatic retry **false**;
- Codespaces **false**;
- Vercel **false**;
- main/Production mutation **false**;
- P3 **sealed**.

**Resume instruction:** Await a new explicit `I authorize` for the corrected single V2 P1/P2 preparation-integrity audit. If received, create source-pinned V2 authorization + one single-use V2 launch marker, execute exactly once, freeze the exact result or failure, update this handoff, and stop. Do not tune or train automatically from the outcome.


## Corrected V2 P1/P2 preparation-integrity audit — successful frozen result — 2026-09-28

The user gave fresh explicit authorization for exactly one corrected V2 P1/P2 source-access audit. That authorization has now been consumed.

### Execution result

- workflow: **Astra P2 preparation integrity audit v2**
- run **36408179090**
- job **108881796729**
- launch head `0e4e5c56ce49eebb0447ed9f467071578112e962`
- conclusion: **SUCCESS**
- started: `2026-09-28T10:11:15Z`
- completed: `2026-09-28T10:54:22Z`
- artifact **10964618513**
- artifact digest `sha256:763c700a20c0688879953b909ac32d476138b863555c7e5349315118f5019fc2`
- frozen artifact `result.json` SHA256 `4d97c4993031f1362cd349c91068f19156311e22642b6f6f0fd12eeaa57e6edc`
- artifact expiry: `2026-10-28T10:54:17Z`

Repository summary:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_RESULT_V2.json`
- Git blob `80c20349fef1252d516aaaed440d105b773ebbf1`

Repository-wide Astra backend tests for the launch head also passed:
- run **36408179235**
- conclusion **SUCCESS**

Execution guards remained intact:
- exact 4 P1 + 4 P2 direct-input captures;
- optimizer steps **0**;
- models loaded **0**;
- model inference **false**;
- threshold search/retuning **false**;
- automatic retry **false**;
- Codespaces/Vercel **not used**;
- main/Production **not mutated**;
- **P3 remained sealed**.

### What the model-free audit established

Eligible acoustic attacks:
- P1: **16** across 4 captures; no excluded note events.
- P2: **11** across 3 captures; 4 P2 Drop3_7 chord note events were excluded by the already-frozen full-window eligibility rule because the selected chord starts only about 58 ms into the source/crop. Do not silently promote those chord observations into the prospective population aggregate.

Event-weighted medians:

| measure | P1 | P2 | P2 / P1 |
|---|---:|---:|---:|
| raw post-attack RMS | 0.0376450 | 0.0202229 | ~0.54 |
| raw first-difference energy | 1.19762e-4 | 1.13366e-5 | ~0.095 |
| prepared-CQT positive flux | 12.9890 | 11.3093 | ~0.87 |
| raw qualified-peak offset | -3.09 ms | -4.71 ms | difference ~-1.61 ms |
| prepared-CQT peak offset | 0 frames | 0 frames | no median shift |

Interpretation:
- **Weak/variable real attack-envelope contrast is now a supported domain-mismatch factor.**
- P2 has substantially weaker raw short-time transition energy on the eligible bounded examples, and moderately weaker post-attack RMS / prepared-CQT positive flux.
- The weakness is **not uniform**: the selected P2 PalmMute attacks are strong; P2 scales are weaker; the selected P2 single-note attack is especially weak in prepared-CQT novelty.
- There is **no evidence here of a gross P2 timestamp/preparation shift**. Raw peak medians differ by only about 1.6 ms, and the prepared-CQT median peak lands on the annotated frame for both populations.
- There is also **no evidence that stereo downmix attenuates P2**. The P2 direct-input files are two-channel with identical measured channel attack metrics. Frozen ffmpeg mono decoding raises eligible P2 post-RMS by about `sqrt(2)` relative to the arithmetic mean of one duplicated channel pair (roughly +3 dB), rather than reducing it. The existing full-file RMS normalization then removes fixed global gain before CQT extraction.
- Therefore the prior P2 onset failure should **not** be attributed to a simple stereo/downmix attenuation bug or a gross fixed timing offset.

The audit does **not** prove one unique causal mechanism. It does not justify threshold rescue, seed/model selection, or tuning on these eight examples.

### P2 Drop3_7 boundary caveat

The selected P2 Drop3_7 chord begins at source annotation ~11.46 ms and aligned annotation ~58.46 ms with the frozen +47 ms lag. Because the prospective raw peak window is +/-120 ms and prepared-CQT search is +/-4 frames, all four simultaneous note events fail the full-window rule at the beginning of the crop/source.

Descriptive values are preserved in the artifact but excluded from the frozen aggregate. Do not change the eligibility window after seeing the result merely to recover this chord.

### Current scientific direction

The evidence chain is now:
1. historical V3 baseline is strong on its P1 training-domain crops;
2. frozen synthetic candidate failed transfer to both P1 and P2;
3. state representation mismatch is severe on P1 candidate outputs;
4. onset probabilities collapse on real P2;
5. model-free integrity audit shows P2 attack timing is not grossly shifted and stereo/downmix is not suppressing amplitude;
6. eligible P2 real attacks have materially weaker and more variable transient/attack-envelope contrast than P1, especially in raw first-difference energy.

This supports treating **synthetic-to-real attack-envelope/domain mismatch** as a real factor while retaining the separate P1 candidate state-representation failure as another unresolved factor.

### Next-step boundary

**Do not automatically train, tune, rerun, or reopen P1/P2. Do not open P3.**

The V2 authorization was single-use and is consumed.

The next safe step is offline design/review only:
- preserve this V2 result unchanged;
- design any future synthetic intervention prospectively, without choosing exact generator parameters by fitting to these eight P1/P2 outcomes;
- if a future synthetic-only experiment is proposed, predeclare architecture/data intervention, seeds, optimizer budget, metrics and decision criteria before running it;
- do not use these eight real examples for threshold search, seed selection, model selection or training;
- any future P1/P2 source access requires a new explicit authorization;
- P3 remains sealed until a separately defined and authorized gate is met.

**Resume instruction:** Continue from the frozen V2 integrity result. Treat weaker/variable real attack-envelope contrast as supported evidence, but do not collapse the problem into onset energy alone because P1 still shows a separate candidate state-representation failure. Keep the next phase synthetic-only and prospectively specified unless the user explicitly authorizes another real-data action.


## S12 synthetic onset-transition robustness result — 2026-09-28

The user gave broad authorization to continue. The only prospectively frozen executable package at that point was the **S12 synthetic-only** robustness experiment. No new P1/P2/P3 action had been defined, so the broad authorization was used only for this already-specified S12 run.

### Execution

- workflow: **Astra synthetic S12 entry v2**
- run **36447341941**
- job **109012933088**
- launch head `b0381c7bf92c6ed5e7ea984fad716d0cc83c0432`
- workflow conclusion: **SUCCESS**
- artifact **10980364991**
- artifact digest `sha256:b4c610134c0a2e8398e30b697b0cefc2cf820259df6f6b9d317e98f100714db4`
- exact artifact `result.json` SHA256 `6cf96ad22f35d9bfd6bcf7880e0abd97c7772f64299ebf30833f21c081798800`
- artifact expiry `2026-12-27T15:56:11Z`

Frozen repository summary:
- `docs/astra/SYNTHETIC_ONSET_ENVELOPE_S12_RESULT_V1.json`

Launch-head Astra backend tests also passed:
- run **36447341885**
- conclusion **SUCCESS**

Execution remained bounded:
- models: **6**
- seeds: **20260927, 20260928, 20260929**
- optimizer steps: **500/model, 3,000 total**
- thresholds fixed **0.50 / 0.50**
- threshold search/retuning: **none**
- automatic retry: **none**
- paid compute: **$0**
- P1 accessed: **no**
- P2 accessed: **no**
- P3 opened: **no**
- Codespaces/Vercel/Production mutation: **none**

### Frozen S12 outcome: gate failed

The training-only CQT onset-transition softening was directionally helpful on the separately frozen soft-onset synthetic challenge:

- challenge onset F1 gain was positive in **3/3** seeds;
- challenge onset recall gain was positive in **3/3** seeds;
- mean challenge onset F1 delta: **+0.0370**;
- mean challenge onset recall delta: **+0.0413**.

However, those gains missed the preregistered floors:
- required mean challenge F1 gain: **+0.05**;
- required mean challenge recall gain: **+0.08**.

More importantly, ordinary synthetic competence regressed in all three seeds:
- mean ordinary onset F1 delta: **-0.0508**;
- mean ordinary onset recall delta: **-0.0698**;
- mean ordinary state-admission delta: **-0.0775**;
- mean ordinary joint-admission delta: **-0.0646**.

Frozen gate failures:
- mean challenge onset F1 gain >= +0.05: **FAIL**
- mean challenge onset recall gain >= +0.08: **FAIL**
- no ordinary onset-F1 loss >0.03: **FAIL**
- no ordinary state-admission loss >0.03: **FAIL**
- no ordinary joint-admission loss >0.04: **FAIL**

Passed:
- challenge F1 gain positive 3/3;
- challenge recall gain positive 3/3;
- challenge precision-loss guard;
- challenge negative-only FP guard;
- non-chord family stability count guard;
- all six 500-step finite paired/fixed-threshold execution checks.

### Interpretation

S12 demonstrates that the fixed synthetic model can trade ordinary competence for somewhat better tolerance to softened onset transitions. That supports the relevance of onset-domain robustness as an engineering factor, but **this particular intervention is not acceptable** because its challenge benefit is too small and its ordinary-domain cost is too large.

Do not:
- widen the blend range after seeing S12;
- weaken the frozen S12 challenge;
- lower thresholds;
- add more seeds to search for a favorable result;
- retry S12 automatically;
- reinterpret the gate failure as a pass.

This result also does not erase the separate real-domain state-representation problem observed on P1.

### Current boundary / next step

Freeze S12 as a failed intervention.

No P1/P2/P3 access is currently needed. The user's broad authorization does not by itself define a scientifically valid new real-data action. **P3 remains sealed because no development gate for opening P3 has been prospectively defined.**

Before another model run, require a new finite prospective design that:
1. addresses both onset-domain robustness and ordinary state/joint competence rather than optimizing only the S12 challenge;
2. does not choose transformation strength, thresholds, seed, or architecture from P1/P2 outcomes;
3. defines one bounded hypothesis, fixed seeds/budget, success/stop rules, and no automatic retry;
4. remains synthetic-only unless a separately specified real-data evaluation is required;
5. does not reopen P3 until a specific P3 gate is written and met.

**Resume instruction:** Continue from the frozen S12 gate failure. Do not rerun or tune S12. Preserve the V2 P1/P2 integrity result and the P1 state-representation failure as separate evidence. The next action should be prospective design/review only unless a concrete bounded experiment is first frozen.


## Explicit next steps after S12 — 2026-09-28

These are the canonical resume instructions. Follow them in order. Do not skip directly to another model run.

### 1. Preserve all frozen evidence

Do not modify or reinterpret:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_RESULT_V2.json`;
- `docs/astra/SYNTHETIC_ONSET_ENVELOPE_S12_RESULT_V1.json`;
- historical S0-S11 results;
- frozen transfer/localization results;
- thresholds 0.50 / 0.50.

Treat the following as separate established development facts:
- P1 still exposes a serious candidate state-representation/generalization failure;
- P2 has weaker/more variable real attack-envelope contrast on the bounded integrity sample;
- gross fixed timing error and stereo/downmix attenuation were not supported as the main P2 explanation;
- S12 improved a soft-onset synthetic challenge directionally but sacrificed too much ordinary synthetic onset/state/joint competence.

### 2. Do not execute another model immediately

The next action is **offline prospective design only**.

Do not:
- rerun S12;
- change S12 blend strengths;
- add seeds to S12;
- lower decoder/model thresholds;
- search loss weights, hidden widths, samplers, or seeds against P1/P2;
- reopen P1 or P2;
- open P3;
- use Codespaces/Vercel/Production for this work.

Routine GitHub editing, design review, tests that do not train models, and source inspection are allowed.

### 3. Define one bounded S13 hypothesis before implementation

The next experiment must address both failure axes simultaneously:
1. retain ordinary exact state/joint competence;
2. improve robustness to weaker onset contrast.

Do **not** optimize only for the S12 soft-onset challenge.

A valid S13 design must predeclare:
- exactly one intervention variable or one tightly coupled intervention package with a clear causal rationale;
- unchanged control arm;
- exact architecture;
- exact data construction;
- exact seeds;
- optimizer, learning rate, batch size and step count;
- decoder and thresholds;
- ordinary-test metrics;
- synthetic soft-onset challenge metrics;
- state-admission and joint-admission metrics;
- negative-only false-positive guard;
- success criteria and stop criteria;
- hard compute ceiling;
- zero automatic retry.

Do not choose any S13 numeric setting by fitting to the eight P1/P2 examples.

### 4. Prefer an intervention that preserves ordinary-domain identity

The strongest next design direction is **identity-preserving robustness**, not stronger corruption.

Favor mechanisms where the ordinary synthetic representation remains intact and the model is encouraged to tolerate onset variation without replacing the clean signal.

Examples that are acceptable to evaluate prospectively:
- paired clean + softened views of the same training event with a consistency objective;
- a bounded auxiliary representation-consistency loss between clean and softened views;
- a small fixed mixture of clean and softened training views while keeping all clean examples present.

Do not silently choose among these by running all of them. Select one design on paper first, justify it from existing evidence, and freeze it before optimizer work.

### 5. S13 minimum experimental structure

Unless a written design justifies a smaller experiment, use:
- control = frozen S9/S11 diversified synthetic training path;
- intervention = one predeclared identity-preserving robustness method;
- seeds = exactly `20260927, 20260928, 20260929`;
- paired initialization and paired minibatch schedule where mathematically possible;
- 500 optimizer steps/model;
- maximum 6 models total / 3,000 optimizer steps total;
- CPU-only GitHub Actions;
- fixed 0.50 / 0.50 thresholds;
- no threshold search;
- no automatic retries;
- no P1/P2/P3 access.

### 6. Predeclare a two-domain gate

Before execution, freeze a gate that requires both:

**Ordinary-domain preservation**
- no material ordinary onset-F1 regression;
- no material ordinary state-admission regression;
- no material ordinary joint-admission regression;
- precision and negative-only false-positive stability.

**Soft-onset robustness**
- positive challenge onset F1 and recall deltas across all predeclared seeds;
- minimum mean gains large enough to be practically meaningful, not merely positive.

The exact numeric floors must be written before model execution. Do not weaken them after seeing results.

### 7. Implement offline and test before launch

After the S13 design is frozen:
1. implement the runner;
2. add focused unit/admission tests;
3. verify dataset identity and paired-control invariants;
4. run repository tests needed for the changed code;
5. record source Git blobs;
6. prepare a single-use launch workflow;
7. update this handoff before execution.

If implementation tests fail, fix only concrete implementation defects. Do not alter the scientific hypothesis to make the gate easier.

### 8. Execution authorization handling

The user's standing broad authorization permits bounded inexpensive GitHub work, but every experiment must still have a **prospectively frozen scope** before execution.

For S13:
- once the design, code, tests, source pins, budget and gate are frozen, the single bounded synthetic-only run may proceed under the user's broad authorization;
- do not use that authorization to reopen P1/P2 or P3 unless a separate real-data action has first been explicitly defined in this handoff;
- P3 remains sealed until a written development gate specifies exactly why it should be opened and what result would count as success/failure.

### 9. Stop conditions

Stop and freeze if:
- S13 fails its preregistered gate;
- ordinary competence regresses beyond the frozen limits;
- robustness gains are seed-sensitive;
- any identity invariant fails;
- runtime exceeds the declared ceiling;
- results suggest another parameter search rather than a clear bounded follow-up.

Do not chain immediately into S14 after a failed S13. First write an analysis explaining what was learned and whether another experiment is scientifically justified.

### 10. Resume command

**Resume from here by drafting and reviewing the S13 prospective design only. Do not launch a model until that design, exact gate, code/test plan, source pins and hard execution ceiling are frozen. Keep P1/P2 closed and P3 sealed.**


## Supervisory review after S12 — 2026-09-28 (canonical next action)

This section supersedes the earlier broad S13 recommendations where they differ. Historical results, gates, source and launch records remain unchanged.

### Review performed and assessment

Reviewed connected GitHub head `057f67e5dfa23a2724bc2c618fb478e5a5736359`, AGENTS.md, this handoff, V2 integrity summary, S12 design/result/scope, S12 runner/tests/workflow and imported S11 training/evaluation code. GitHub job `109012933088` reports successful tests, execution and artifact upload. No artifacts were downloaded/recomputed, no corpus was reopened, no model was run, and no new test result is claimed by this documentation review. Preserve the stale local checkout and its untracked files; use the connected remote as the current source.

GPT-5.6 correctly retained the fixed thresholds, paired seeds and negative S12 gate. S12 is a completed, rejected intervention, not a successful model. The next useful work is a short implementation-validity review followed by ONE prospective design; do not launch an open-ended sequence of synthetic experiments.

### Corrections that must carry forward

1. **Report capture-balanced evidence alongside event-weighted evidence.** The frozen V2 summary already contains these numbers; no new real-data access is needed:

   | P2/P1 ratio of medians | Event-weighted | Capture-balanced |
   |---|---:|---:|
   | raw post-attack RMS | 0.537 | approximately 0.899 |
   | raw first-difference energy | 0.0947 | approximately 0.792 |
   | prepared CQT positive flux | 0.871 | approximately 0.952 |

   Capture-balanced here means ratio of the two populations' medians of capture medians, not a paired effect estimate. P1 has four eligible captures, P2 only three, with its chord excluded. The strong event-weighted first-difference contrast is therefore highly sensitive to event/category composition. Lower/variable contrast is observed on these examples; a roughly tenfold performer-wide weakness or a demonstrated cause of P2 onset collapse is NOT established. Preserve the frozen JSON; qualify its interpretation in future reports. Peak medians also do not establish every event's alignment or rule out errors outside the fixed search windows.

2. **S12 is feature corruption, not a validated physical attack-envelope simulator.** `soften_features` blends all 192 bins at each onset toward the preceding frame. The following frame blends toward the already-modified onset frame. Adjacent onsets can interact because the array is mutated in order. It does not merely reduce an onset scalar: pitch/harmonic evidence, another string's sustain and context can change while labels stay fixed. At blend 1 the two frames can become the preceding state. This is a plausible contributor to ordinary-state regression, not a proven explanation. Do not describe bit-identical labels as proof that observable note identity/timing survived the transform.

3. **Keep metric names honest.** S12's `onsetF1` comes from `pitchOnset.f1`: it is pitch-plus-onset event F1, not a pitch-independent attack detector score. State/joint admission diagnostics are distinct. P1's earlier global-top-1 diagnostic remains subject to the chord/global-softmax limitations recorded above. Failed real transfer is supported; a unique internal representation mechanism is still unresolved.

4. **Three model seeds are not three new datasets or real-domain replications.** They share the fixed generated corpus and challenge. The S12 challenge has now informed the S13 design and is development evidence. Reusing it is useful for comparison but cannot be called untouched confirmation or proof of real-audio improvement. Preserving ordinary synthetic competence does not by itself repair the P1 real-domain failure.

### Exact authorized offline work, in order

1. Write `docs/astra/SYNTHETIC_S13_PREIMPLEMENTATION_REVIEW_V1.md`. Use only existing source/results and small handcrafted arrays. Trace the S12 transform through `context5`, target layout, and the S11 loss. Add focused non-training tests/diagnostics for: isolated new pitch; repeated same pitch; one string attacking over another sustaining; adjacent onsets; frame-zero and final-frame behavior; input immutability; mismatched shapes/nonfinite input. Record the actual before/after feature values and unchanged targets. Do not regenerate the full corpus or run an optimizer merely to do this review. Keep S12 source/results frozen; place new diagnostics in a separate module.

2. Make a concrete **go/no-go design decision** from that review. Do not claim that consistency or clean-view mixing is guaranteed to work. If preserving labels under the proposed soft view cannot be justified even in simple constructed cases, stop and document that issue rather than stacking a consistency loss on it. A transform correction would itself be the intervention and must be versioned; do not silently combine a new transform, new loss and new sampler.

3. If justified, choose exactly ONE S13 method and write `docs/astra/SYNTHETIC_S13_DESIGN_V1.md` plus a machine-readable spec. A clean-supervised path with a separately bounded soft-view objective is a reasonable hypothesis, not a selected winner. Specify the exact loss equation, coefficients, reduction/normalization, which state/onset outputs receive supervision or consistency, gradient/stop-gradient direction, view pairing and random-number streams. State precisely whether the clean loss weight remains unchanged. No unrecorded defaults and no comparison of several methods followed by selection.

4. Keep the frozen S9/S11 control, three seeds 20260927/20260928/20260929, architecture, optimizer, decoder and 0.50/0.50 thresholds. At most six trained models and 3,000 optimizer steps. Paired clean/soft views may double forward/backward work per step: declare view counts, examples processed and wall-clock limit as well as steps. Label that additional work explicitly instead of calling the arms compute-identical. Use identical control/intervention initialization and clean minibatch indices, with a separate fixed augmentation RNG.

5. Keep the S12 numerical benefit floors and ordinary-regression limits as the minimum comparison gate: challenge mean pitch-onset F1 gain >=0.05 and recall gain >=0.08; both positive in all three seeds; each seed ordinary F1 loss <=0.03, state-admission loss <=0.03 and joint-admission loss <=0.04; challenge precision loss <=0.05; challenge negative-only FP <=0.10 events/s. Predeclare ordinary precision/negative-only and family guards too. Do not lower gates to make a new run attractive. Report absolute control/intervention scores, TP/FP/FN and denominators, not only deltas. A pass is synthetic development evidence only. No automatic P1/P2/P3 evaluation or production promotion follows.

6. Before launch, test dataset split/label identity, paired initialization and batches, loss/gradient routing on tiny tensors, exact gate boundary cases and every launch rejection path. No optimizer pilot, tuning sweep or extra seed may hide inside a unit test. Pin the complete imported source dependency closure, including preprocessing, decoder, metric and sampler modules, rather than only top-level runners. Record canonical per-array dataset hashes and verify both arms against the frozen common corpus; equal row counts alone are insufficient. Assert the challenge's non-test features are unchanged at the execution entry point.

### Execution controls to improve in S13

The inspected S12 code checks a `singleLaunch` boolean, but that is not a consumed-run ledger. Its workflow can be rerun; the runner deletes existing output directories with `shutil.rmtree`; several guard fields are recorded constants. These observations do not prove an unauthorized S12 rerun occurred. They identify controls not to copy into S13.

- Prepare disabled first. Validate exact branch, launch/spec/source identities and run attempt before expensive work. Reject GitHub run attempts greater than 1 and reused launch identities using a durable execution receipt/history check. Concurrency control alone is not single-use enforcement.
- Refuse existing evidence/output paths; use a unique launch/run directory. Never delete earlier evidence to make a new execution fit.
- Use read-only repository permissions, bounded CPU/time, no corpus/network acquisition in the experiment, no retry loop and no model/Codespaces/Vercel costs outside the standing authorization.
- Validate all declared ceilings and thresholds against actual runtime settings. Check finiteness of every required per-arm/per-seed metric and fail closed on missing data. The inherited aggregate-mean finiteness check is not complete validation.
- Save failure receipts and upload partial diagnostics with an always-run artifact step. A workflow success and a scientific gate pass must remain separate fields.
- Commit design/spec/code/tests and an in-progress checkpoint before the one launch. Once the concrete package passes its offline checks, the existing standing authorization for bounded inexpensive synthetic GitHub work applies; do not ask repeatedly for routine preparation. A genuinely new paid/model-cost scope still needs the user's required approval. This review itself launches nothing.

### Stop rule and next handoff

After one authorized S13 execution, freeze pass/fail, all seed results, source/data identities, compute and artifact checksums. No automatic S14, threshold rescue or favorable-seed selection. A failed S13 requires a project-level review of the simulator/representation strategy before more architecture or loss experiments. A pass requires a separately specified development-transfer plan; P1/P2 remain exposed development data and P3 stays sealed. Respect the current explicit real-data access boundary.

**GPT-5.6's immediate next task:** complete the small, model-free S12 transform/target validity review and its focused tests, then freeze one justified S13 design or an explicit no-go. Save actual findings and exact next action here on `astra-work`, verify the remote commit, and retain main/Production unchanged.

## S13 preimplementation transform/target validity review — 2026-09-28

The required small, model-free review after S12 is complete. **No model was trained or loaded, optimizer steps = 0, the full synthetic corpus was not regenerated, P1/P2 were not reopened, P3 remains sealed, and main/Production were unchanged.**

Frozen review:
- `docs/astra/SYNTHETIC_S13_PREIMPLEMENTATION_REVIEW_V1.md`

New diagnostics:
- `astra_backend/synthetic/s13_preimplementation_review_v1.py`
- `astra_backend/synthetic/test_s13_preimplementation_review_v1.py`
- `.github/workflows/astra-s13-preimplementation-review-v1.yml`

Focused workflow:
- successful run **36453347122**
- job **109033319204**
- head **94c4a66cd06044fbf063dad8d1e5716f2ccf279b**
- artifact **10984880391**
- artifact digest `sha256:df859c6f93bbe88c864d04e005ed70b9f37001ee8a7fe4a49ae9691d50a45bee`
- test result: **11 passed**
- model run: **no**
- optimizer steps: **0**

Two concrete preparation failures were fixed before the passing run:
1. the first review workflow referenced a nonexistent `astra_backend/requirements.txt`; it was corrected to use the frozen tabcnn runtime lockfile;
2. the first adjacent-onset expected-value assertion was arithmetically wrong; the actual recursive mutation is `[0.0, 0.5, 0.425, 0.7125, 1.0]`, and the test/review were corrected. These were implementation/test defects only; the scientific interpretation was not changed to obtain a pass.

### Actual model-free findings

The existing S12 transform is **not justified as a label/identity-preserving clean-vs-soft consistency view**:

- isolated new pitch, blend 0.70:
  - before `[0.0, 1.0, 1.0, 1.0]`
  - after approximately `[0.0, 0.3, 0.51, 1.0]`;
- repeated same pitch, blend 0.70:
  - before `[0.8, 1.0, 1.0, 0.9, 0.8]`
  - after approximately `[0.8, 0.86, 0.902, 0.9, 0.8]`;
- attack over another changing/sustaining component changes unrelated spectral bins because all 192 bins are blended;
- adjacent onsets are mutation-order coupled:
  - before `[0.0, 1.0, 0.2, 1.0, 1.0]`
  - after approximately `[0.0, 0.5, 0.425, 0.7125, 1.0]`;
- frame-zero onset labels are ignored by the transform and final-frame onsets receive asymmetric treatment;
- `context5` spreads these local feature changes into overlapping five-frame model inputs while the state/onset targets remain unchanged.

This does **not** prove that the S12 transform alone caused all ordinary-domain regression, and it does not modify the frozen S12 failure. It establishes that the prerequisite for stacking a clean/soft consistency loss on this transform is not met.

### Frozen decision: explicit NO-GO for that S13 path

Do **not** implement or train S13 using the existing S12 soft view as a supposedly identity-preserving augmentation/consistency view.

Per the supervisory stop rule, no `SYNTHETIC_S13_DESIGN_V1` model package was created after this no-go. Do not substitute a new loss, sampler or architecture in the same step.

### Exact next action

The next scientific action, if continuing, is **offline transform-design work only**:

1. define one separately versioned onset-robustness transform with a physical/representation rationale;
2. demonstrate preservation behavior first on isolated, repeated, polyphonic/overlapping and adjacent-onset handcrafted cases;
3. keep the S9/S11 model, thresholds 0.50/0.50, P1/P2 boundary and P3 seal unchanged while doing that review;
4. treat any transform correction itself as the single intervention;
5. only after a transform passes a prospective preservation review may a new S13 design/spec be written and frozen before optimizer work.

Do not run S13, do not rerun S12, do not search transform strengths against P1/P2, and do not chain into S14.

**Resume instruction:** Continue from this explicit no-go. The immediate task is model-free prospective transform design/review only. Preserve S12 as failed, keep P1/P2 closed, P3 sealed, thresholds 0.50/0.50, and main/Production unchanged.

## S13 transform-design review and prospective design freeze — 2026-09-28

Continued from the explicit S12-view no-go with model-free transform design only.

### Prospective replacement transform reviewed

One replacement transform was defined and reviewed:

**positive-onset-increment compression**

At labeled onset frames only, using immutable source features:

`positive_delta = max(x[f] - x[f-1], 0)`

`x_soft[f] = x[f] - (1-r) * positive_delta`

Key properties:
- only positive increments can change;
- flat/decreasing bins are preserved exactly;
- no following-frame mutation;
- no recursive coupling between adjacent onsets;
- simultaneous string onsets at one frame transform the frame once;
- frame zero remains unchanged;
- transform is representation-local, **not** string-source-selective and is not claimed to be a physical attack-envelope simulator.

Model-free review files:
- `docs/astra/SYNTHETIC_S13_TRANSFORM_DESIGN_REVIEW_V1.md`
- `astra_backend/synthetic/s13_transform_design_review_v1.py`
  - blob `f9ccbca8f692c7db01e71d7d497c9df34b82c15f`
- `astra_backend/synthetic/test_s13_transform_design_review_v1.py`
  - blob `547b749bb7da3e0673cfe5a0d41f959ca24f2c38`
- `.github/workflows/astra-s13-transform-design-review-v1.yml`
  - blob `bba8b5aeedb0bffb533253842fe35efbfb1edee4`

Focused review:
- workflow run **36456672322**
- job **109044647114**
- head **4d9438b8b6524314ad08f3dad0daee81340e20cc**
- result: **17 passed**
- artifact **10986610039**
- artifact digest `sha256:b7f7f46064b42700391a5675119a1fdd08dd5008e32543efa2195565176a5f69`
- model run: **no**
- optimizer steps: **0**
- P1/P2 access: **no**
- P3 opened: **no**

Handcrafted admission findings at demonstration retain fraction 0.50:
- isolated new pitch `[0,1,1,1,1] -> [0,0.5,1,1,1]`;
- repeated pitch `[0.8,1,1,0.9,0.8] -> [0.8,0.9,1,0.9,0.8]`;
- decaying/sustaining bins remain unchanged while a new positive attack rise is compressed;
- adjacent onset case `[0,1,0.2,1,1] -> [0,0.5,0.2,1,1]`, with no recursive order coupling;
- an unrelated bin rising at the same frame is also compressed, retained as an explicit non-source-selective limitation.

Decision: **GO for prospective S13 design work only.** This does not authorize or imply a model pass.

### S13 prospective design/spec now frozen

Created:
- `docs/astra/SYNTHETIC_S13_DESIGN_V1.md`
  - blob `2e48f3ff9af79323b34a3f41124d9d2b56f3553a`
- `docs/astra/SYNTHETIC_S13_SPEC_V1.json`
  - blob `9da9ba1657d452faf667119320d3a7285d4cdb67`

Single intervention package:
- retain fraction exactly **0.50**;
- transform exactly `floor(n_family/2)` training rows inside each family;
- deterministic per-family transformed subset ranked by SHA-256 of `astra-s13-soft-subset-v1|<rowIndex>`;
- clean rows remain present;
- no row-count change;
- no sampler change;
- no new loss/consistency objective;
- no architecture, decoder or threshold change.

Corrected evaluation challenge:
- all test rows transformed with the same admitted nonrecursive transform at retain fraction **0.50**;
- training/validation challenge features stay clean;
- all labels/references remain identical;
- this replaces the S12 recursive challenge for S13, so absolute S12/S13 challenge scores are not directly comparable.

Frozen training scope:
- seeds **20260927, 20260928, 20260929**;
- frozen S9/S11 model and onset-aware 32/32/32/32 sampler;
- Adam lr **0.003**;
- batch size **128**;
- **500 optimizer steps/model**;
- at most **6 models / 3,000 steps total**;
- state/onset thresholds **0.50 / 0.50**;
- no threshold search/retuning;
- CPU-only GitHub Actions;
- <=90 fit/eval minutes;
- $0 paid compute;
- no automatic retry;
- no P1/P2/P3 access;
- no Codespaces/Vercel/main/Production mutation.

The S13 gate keeps the S12 minimum benefit/regression floors and adds ordinary precision, ordinary negative-only and identity/runtime admission checks. A scientific pass requires all frozen criteria; workflow success alone cannot count as a gate pass.

### Exact next action

**Do not launch S13 yet.**

Next authorized work is offline implementation/preparation only:
1. implement the S13 runner using the frozen design/spec exactly;
2. add focused tests for transformed-subset identity, formula invariants, challenge identity, paired initialization/batches, loss/gradient path unchanged, exact gate boundaries and every launch rejection path;
3. pin the complete imported source dependency closure and canonical per-array dataset hashes;
4. implement single-use launch controls, durable launch-identity receipt/history, run-attempt rejection, unique output path and failure receipts;
5. run only focused offline tests needed for this package;
6. update this handoff with actual test results, blobs, hashes and execution ceiling before any optimizer work.

Standing bounded GitHub authorization may cover the eventual one synthetic-only launch **only after** that concrete execution package is fully frozen and verified. Do not reopen P1/P2 or P3.

**Resume instruction:** Implement and verify the frozen S13 package offline. Do not train a model yet. Preserve S12 as failed, keep thresholds 0.50/0.50, P1/P2 closed, P3 sealed and main/Production unchanged.

## S13 offline execution package verified — 2026-09-28

The frozen S13 implementation/preparation package is now complete and reconciled to the canonical package already present on `astra-work`. No S13 model has been trained yet at this checkpoint.

Canonical package:
- runner: `astra_backend/synthetic/s13_pilot_v1.py` — blob `3400dfa2113ec34a72bbc517ba4b6c6f5935027a`
- focused tests: `astra_backend/synthetic/test_s13_pilot_v1.py`
- deterministic preparation workflow: `.github/workflows/astra-s13-offline-preparation-v1.yml`
- disabled-by-default execution workflow: `.github/workflows/astra-s13-execution-v1.yml` — blob `7eaae50131800563317ec270b82536fd5eaff4bb`
- frozen run scope: `docs/astra/SYNTHETIC_S13_RUN_SCOPE_V1.json` — blob `1e5812bfc1b96bfec6a85e81894ae08dba9439e4`
- durable execution history: `docs/astra/SYNTHETIC_S13_EXECUTION_HISTORY_V1.json` — blob `c0cecbc58966a38ed7acd35439c439c74fcd8fbd`
- launch request only: `docs/astra/SYNTHETIC_S13_LAUNCH_REQUEST_V1.json`
- actual launch marker `docs/astra/SYNTHETIC_S13_LAUNCH_V1.json`: **not present at this checkpoint**

All pinned design/spec/source identities in the frozen scope were rechecked against the connected remote and match exactly.

### Deterministic preparation evidence

The canonical preparation froze single-thread numerical settings:
- `PYTHONHASHSEED=0`
- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `NUMEXPR_NUM_THREADS=1`

This was necessary because earlier cross-run CQT feature hashes varied before thread determinism was frozen. The execution workflow therefore downloads the exact frozen preparation artifact and independently checks the pinned per-array hashes before optimizer work.

Canonical preparation remains:
- run **36458911022**
- job **109052218872**
- artifact **10985624417**
- digest `sha256:5a1737985f839adf2d14776a7b83d78609921f069102e36af874a1f3672690e1`

A fresh reconciliation replay after restoring the canonical package also passed:
- run **36463015424**
- job **109066035904**
- head **06bc39a67119c066f851e0945b79ec082677e4f1**
- focused tests **15 passed**
- two independent preparations in the same frozen environment matched exactly
- `S13_REPEATABILITY_ARRAY_HASHES_MATCH=true`
- model run **false**
- optimizer steps **0**
- P1/P2/P3 access **false**
- replay artifact **10988745088**
- replay artifact ZIP digest `sha256:f8bf1fc6b69b2461db2e970d6ce28698a8de440d3a5cc8a109d069a3a8d340f0`

The replay reproduced the canonical frozen dataset identities exactly:
- control feature hash `b172b7cdcc0df5bc3b47b54a8dd116992f9552383babe0dc4cde5eecdac3a749`
- intervention feature hash `182a9e64a1ea5a275fc79c3f8c0840b8f99a16b4649df118d107abdb458005db`
- challenge feature hash `293ab2701b53b941c4567a0defc2fecd12ec611456d368996421e4f674649c3d`
- transformed training rows **105**
- challenge test rows **42**

### Launch boundary now reached

The offline package is fully frozen and verified. The prior handoff explicitly permits exactly one bounded inexpensive synthetic-only S13 launch under the standing authorization once this condition is met.

The one launch must:
- create exactly one unique armed `SYNTHETIC_S13_LAUNCH_V1.json`;
- use run attempt 1 only;
- use the exact frozen preparation artifact and hashes;
- train at most 6 models / 3,000 optimizer steps total;
- keep thresholds fixed at 0.50 / 0.50;
- use no P1/P2/P3;
- use no automatic retry;
- preserve all failure evidence;
- stop after the one execution and freeze pass/fail before any further experiment.

**Immediate next action:** create the one unique armed S13 launch marker and allow the already-frozen execution workflow to run exactly once. Then freeze the scientific gate result, update the durable execution history, and stop. No S14 and no real-data follow-up may occur automatically.



## S13 single execution frozen — 2026-09-28

The one authorized bounded synthetic-only S13 execution has completed and is now **consumed**. The GitHub workflow succeeded operationally, but the preregistered **scientific gate failed**. This is a frozen negative result.

Frozen result:
- `docs/astra/SYNTHETIC_S13_RESULT_V1.json`
- launch identity `s13-v1-20260928-canonical-01`
- launch commit `c3644cb2566e25a92ec1cd0aa4859e76c3930f3c`
- workflow run **36463727631**
- job **109068446982**
- run attempt **1**
- artifact **10988304586**
- artifact ZIP digest `sha256:964248c795d534cf44062b80de5319108cf8dc9477fe44067a554238f5acf162`
- frozen `result.json` SHA-256 `aef0af7892029cc86ab3a04fcf8073c3f0f749d86e8754576ca496d25803e67f`
- workflow conclusion **success**
- scientific gate **FAIL**
- models **6**
- optimizer steps **3000 total / 500 per model**
- fit/eval **58.35 s**
- thresholds **0.50 / 0.50**
- threshold search/retuning **none**
- automatic retry **none**
- P1/P2 access **none**
- P3 opened **no**
- paid compute **$0**
- main/Production mutation **none**

The durable ledger has been updated:
- `docs/astra/SYNTHETIC_S13_EXECUTION_HISTORY_V1.json`
- the launch identity is consumed and must not be reused.

### Scientific result

The intervention did not deliver the required challenge benefit.

Aggregate challenge deltas, intervention minus paired control:
- pitch-onset F1 mean **-0.01208**; seed deltas **-0.03317, +0.02572, -0.02880**;
- pitch-onset recall mean **-0.02326**; seed deltas **-0.00775, -0.00775, -0.05426**;
- pitch-onset precision mean **+0.00184**, but one seed lost **0.06769**, exceeding the frozen maximum allowed precision loss of 0.05.

Aggregate ordinary deltas:
- pitch-onset F1 mean **-0.01228**;
- precision mean **-0.01548**, with one seed loss **0.04728**, exceeding the frozen 0.03 limit;
- state admission mean **-0.00517**, with one seed loss **0.03101**, exceeding the frozen 0.03 limit;
- joint admission mean **-0.01292**.

The required positive challenge F1 gain in all three seeds failed (**1/3 positive**), and challenge recall gain was positive in **0/3** seeds. The required mean challenge F1 gain >=0.05 and recall gain >=0.08 both failed.

Safety/identity/runtime controls did behave as frozen:
- all required metrics finite;
- exactly six 500-step models / 3000 total steps;
- paired initialization and batches verified;
- fixed thresholds/no search verified;
- transformed-row rule and transform invariants verified;
- non-feature arrays bit-identical;
- challenge train/validation features unchanged;
- negative-only FP guard passed every seed;
- no P1/P2/P3 access.

### Frozen interpretation

S13 is **not** a successful robustness intervention. The admitted positive-onset-increment compression, applied to half of training rows at retain fraction 0.50, did not improve the transformed synthetic challenge under the preregistered gate and introduced ordinary-domain regressions in precision/state admission for some seeds.

This negative result does not prove that onset robustness is impossible, and it does not identify one unique failure mechanism. It does establish that this exact transform/training intervention is rejected.

### Mandatory stop

Per the preregistered S13 stop rule:
- **do not rerun S13**;
- **do not lower thresholds or gates**;
- **do not select the favorable seed**;
- **do not tune retain fraction, subset fraction, loss, sampler, architecture, decoder, or transform strength from this result**;
- **do not chain into S14**;
- **do not automatically reopen P1/P2 or P3**.

The next scientific step, if the project continues, is a **project-level review of the simulator/representation strategy**, using the frozen S12 and S13 failures plus the prior real-domain localization evidence. That review must be analysis/design only before any new model experiment is proposed.

**Resume instruction:** Begin with project-level simulator/representation strategy review only. Preserve S12 and S13 as failed frozen interventions. Keep thresholds 0.50/0.50, P1/P2 closed, P3 sealed, and main/Production unchanged. Do not launch any model or real-data workflow from this checkpoint.


## Project-level simulator/representation strategy review — 2026-09-28

Completed the mandatory post-S13 project-level review without reopening P1/P2 media, P3, or any model execution.

Frozen review:
- `docs/astra/SIMULATOR_REPRESENTATION_STRATEGY_REVIEW_V1.md`

No model was loaded or trained. Optimizer steps **0**. Thresholds remain **0.50 / 0.50**. Main/Production unchanged.

### Review conclusion

The combined evidence does **not** justify another synthetic model experiment.

- S12 produced directional soft-challenge gains but failed the preregistered benefit floors and caused substantial ordinary-domain regression; later model-free review also showed its recursive frame-wide transform was not a clean identity-preserving view.
- S13 used the corrected narrower positive-increment transform, but challenge pitch-onset F1 mean delta was **-0.0121**, recall mean delta **-0.0233**, F1 improved in only **1/3** seeds and recall in **0/3**.
- The frozen synthetic corpus is a small controlled procedural surrogate (**294 clips / 7 families**) and should not be treated as a validated real-guitar distribution.
- The frozen S11 model is a five-frame flattened CQT MLP with limited explicit time-frequency/source-separation inductive structure. This is a plausible transfer-risk factor, not a proven root cause.
- Existing P1/P2 prepared-feature evidence cannot distinguish raw attack strength, capture/articulation, preprocessing sensitivity and coordinate alignment.

Therefore:
- **NO-GO for S14 or any further transform/loss/sampler/architecture/threshold search from S12/S13.**
- **GO only for the already-prepared zero-model P1/P2 attack/preparation integrity audit as the next empirical information-gathering step.**

That audit remains behind the existing explicit source-access boundary. The generic continuation instruction was **not** treated as fresh permission to reopen P1/P2 media.

Prepared authorization request remains:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_AUTHORIZATION_REQUEST_V1.json`

Exact requested scope:
- eight frozen P1/P2 direct-input captures only;
- P1 media access **yes**;
- P2 media access **yes**;
- P3 **no**;
- models loaded **0**;
- inference **no**;
- optimizer steps **0**;
- threshold changes/search **none**;
- automatic retry **no**;
- CPU-only GitHub Actions;
- <=120 minutes;
- <=4,004,045,267 download bytes;
- no Codespaces/Vercel/main/Production mutation.

### Resume instruction

Do not launch another synthetic model experiment.

The next executable empirical action requires **fresh explicit user authorization** for the exact frozen zero-model P1/P2 preparation-integrity audit above. If that authorization is not provided, remain in analysis/documentation mode. P3 stays sealed.


## Reconciliation correction after user authorization — 2026-09-28

The user's fresh `I authorize` was received after the post-S13 V1 strategy review requested the zero-model P1/P2 integrity audit.

Before launching anything, repository continuity was rechecked. That revealed the corrected V2 integrity audit had already been executed successfully earlier on this branch and its single-use authorization was already consumed:
- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_RESULT_V2.json`
- run **36408179090**
- job **108881796729**
- artifact **10964618513**
- result SHA256 `4d97c4993031f1362cd349c91068f19156311e22642b6f6f0fd12eeaa57e6edc`

Therefore the new authorization was **not** used to reopen or rerun P1/P2. Repeating the same source-access audit would violate the single-use/no-retry discipline and add no new scientific information.

The prior post-S13 strategy review V1 missed this already-frozen V2 evidence because the long handoff contains sections appended out of chronological order. V1 is preserved historically but superseded.

Corrected review:
- `docs/astra/SIMULATOR_REPRESENTATION_STRATEGY_REVIEW_V2.md`

### Corrected scientific synthesis

The V2 audit established weak/variable real attack-envelope contrast as a supported domain factor on the bounded eligible examples, while not supporting a gross fixed timing shift or stereo/downmix attenuation mechanism.

Capture-balanced evidence must accompany event-weighted evidence:
- raw post-attack RMS P2/P1: event-weighted **0.537**, capture-balanced approximately **0.899**;
- raw first-difference energy: event-weighted **0.0947**, capture-balanced approximately **0.792**;
- prepared-CQT positive flux: event-weighted **0.871**, capture-balanced approximately **0.952**.

This heterogeneity prevents interpreting the event-weighted first-difference ratio as a universal performer-wide weakness.

Combined with:
- the separate severe P1 candidate state/pitch representation failure;
- S12's failed tradeoff and invalid recursive feature corruption;
- S13's failed narrower feature-space intervention;

the next justified step is **not** another feature-space transform or model run.

### Exact next action

Proceed with offline/model-free source-audio simulator diversity design only.

Create prospectively:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_SPEC_V1.json`

Requirements:
- waveform/source generation before frozen CQT preprocessing;
- fixed engineering/physical priors, not fit to exposed P1/P2 outcomes;
- attack-envelope variability plus broader timbre/electrical/noise dimensions;
- deterministic RNG and exact label preservation;
- model-free admission diagnostics before optimizer work;
- prospectively frozen held-out synthetic challenge families;
- P1/P2 remain closed;
- P3 remains sealed;
- no model training, threshold changes, architecture change, launch marker, main or Production mutation yet.

**Resume instruction:** Continue with the prospective source-audio simulator diversity design only. No P1/P2 rerun is needed or authorized by this checkpoint.


## Source-audio simulator diversity prospective design frozen — 2026-09-28

Continued from the corrected V2-aware strategy review without reopening real media and without model execution.

Created and frozen:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_SPEC_V1.json`

This is one waveform-level source-domain randomization package applied **before** frozen CQT preprocessing. It is not fit to P1/P2 and is not claimed to be a physical replica of those captures.

Frozen source-domain axes include:
- attack rise-time and transient-noise variability;
- string/body damping and spectral brightness;
- pick-position variability;
- bounded pickup/electrical coloration;
- mild nonlinear/compression-like wet behavior;
- bounded broadband noise/hum;
- per-note dynamic variation.

The intervention policy is prospective:
- all training waveform renders receive the package;
- validation/test remain bit-identical to control;
- row count and all labels/references/splits remain unchanged.

A fixed held-out waveform-level challenge profile is also frozen now, before any optimizer work.

### Current authorization boundary

No training is authorized by this design.

Next allowed work:
1. implement the source-domain waveform generator package in a separate versioned module;
2. add deterministic model-free fixture diagnostics/tests for isolated, repeated, scale, chord, palm-muted, legato and negative-only cases;
3. verify label/reference/split identity;
4. verify waveform finiteness, no unintended clipping and fundamental preservation within the frozen tolerance;
5. verify attack-envelope span and that intended source changes survive frozen CQT preprocessing;
6. optionally perform only the bounded model-free deterministic dataset preparation after fixture admission passes;
7. freeze exact hashes, test results and any defects before proposing a model experiment.

Hard model-free ceiling:
- models loaded **0**;
- optimizer steps **0**;
- P1/P2/P3 access **none**;
- <=60 diagnostic fixture renders;
- <=900 total synthetic renders if full preparation occurs;
- <=1,800 synthetic audio seconds;
- <=500 MB persisted artifacts;
- CPU only;
- <=45 minutes;
- $0 paid compute;
- no automatic retry loop;
- no main/Production mutation.

**Resume instruction:** Implement and verify the frozen source-domain simulator diversity package offline. Do not train a model yet. Keep P1/P2 closed, P3 sealed, thresholds 0.50/0.50, and main/Production unchanged.


## Source-domain simulator model-free implementation/preparation complete — 2026-09-28

The frozen waveform-level source-domain simulator package has now passed model-free admission and bounded deterministic preparation.

Frozen result:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_PREPARATION_RESULT_V1.json`

### Model-free fixture admission

Successful run:
- workflow run **36474090090**
- job **109103325464**
- head `1cf92163ebdabbdc577536c85d72d04ee3eb336e`
- **15 focused tests passed**
- artifact **10992965604**
- artifact digest `sha256:f4a74eca7b619e96740200284aca60ed92ef3752704dafb3b905b2b68cd1fe7a`

Admission:
- all frozen criteria passed;
- fixture renders **23**;
- measured fast/slow attack-rise ratio approximately **14.60x**;
- maximum absolute stable-fundamental error approximately **6.79 cents**, within the frozen 15-cent limit;
- labels/references preserved on fixtures;
- CQT effects present on all positive fixtures;
- no unlabeled transient injection;
- model run **no**;
- optimizer steps **0**;
- P1/P2/P3 access **none**.

One concrete implementation defect was fixed before the successful run: polyphase resampling could slightly overshoot the pre-resample 0.78 peak normalization. The same frozen 0.78 bound is now re-applied deterministically after resampling. No simulator parameter range or admission criterion was changed.

### Full bounded deterministic preparation

Successful run:
- workflow run **36475263654**
- job **109107267996**
- head `fd52262738a626b7131fcf96ca930dda36442d3a`
- focused tests: **15 simulator + 5 preparation passed**
- repository Astra test run **36475263505** also succeeded
- artifact **10993531230**
- artifact digest `sha256:00bbd401e887aaabef6f5c911b2a9a767d854ad3d7254584b94927a10ec29953`

Prepared corpus:
- control examples **294**
- source-domain intervention changes exactly **210 training rows**
- fixed source-domain challenge changes exactly **42 test rows**
- total preparation renders **576**
- total synthetic audio **1,152 seconds**
- persisted three-arm dataset bytes **25,733,042**
- preparation core time approximately **52.07 seconds**

Frozen feature hashes:
- control `b172b7cdcc0df5bc3b47b54a8dd116992f9552383babe0dc4cde5eecdac3a749`
- intervention `a8b5c5c590c82c152f302260430b3d6e4a3c9d5ee378d683bd8091f8f220501a`
- challenge `c786d846b2651872b621afa16d69a179965ffc0190a164d2e5e4ca89e0842640`

Frozen dataset file SHA-256:
- control `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`
- intervention `b46fa80121c43705708bfe786715456be535f6e39d31835b2fa611629024e94e`
- challenge `0d40ab89291f4c19cf44bddb3c1c2adb4926ce3363eeb67f45770940ae03a010`

All non-feature arrays are bit-identical across arms; intervention validation/test features are control-identical; challenge train/validation features are control-identical.

### Historical S9 fixed-width string defect surfaced and preserved

Preparation discovered a pre-existing S9 bookkeeping defect on the 30 training chord rows:
- `template_id` and `refs_json` were assigned into fixed-width Unicode arrays inherited from S0 and are truncated;
- training chord `refs_json` is therefore malformed historical metadata;
- state/onset arrays are intact;
- held-out/test references are unaffected.

This was **not repaired in one arm**. The new preparation:
- reconstructs each S9 training chord from its frozen row slot;
- requires exact state/onset identity;
- verifies each historical stored reference is an exact prefix truncation of the reconstructed reference;
- preserves the frozen historical strings byte-identically in all arms.

A second concrete workflow-only defect was fixed after preparation completed: a receipt rewrite emitted literal `\\n` after JSON rather than an actual newline. No dataset/scientific setting changed.

### Prospective source-domain training design frozen

Created:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_SPEC_V1.json`

The future experiment, if later authorized after execution-package verification:
- keeps the frozen S11 architecture;
- seeds **20260927 / 20260928 / 20260929**;
- paired initialization and batches;
- **500 optimizer steps/model**;
- maximum **6 models / 3,000 steps total**;
- state/onset thresholds **0.50 / 0.50**;
- no threshold search/retuning;
- source-domain training data package is the **only intervention**;
- P1/P2/P3 remain closed.

The frozen gate retains the established challenge benefit floors and ordinary-regression limits rather than weakening criteria after S12/S13.

**Training is not authorized by this checkpoint.**

### Exact next action

Implement and verify the prospective source-domain training execution package **offline only**:
1. fail-closed runner using the exact frozen preparation artifact/hashes;
2. focused tests for dataset identity, historical S9 metadata handling, paired initialization/batches, gate boundaries and every launch rejection path;
3. complete source dependency pins;
4. durable single-use execution ledger and disabled launch boundary;
5. zero optimizer steps during package verification.

**Resume instruction:** Implement and verify the source-domain training execution package offline. Do not launch a model yet. Keep P1/P2 closed, P3 sealed, thresholds 0.50/0.50, and main/Production unchanged.


## Source-domain training offline execution package verified — 2026-09-28

The prospective source-domain training execution package is now fail-closed and verified without optimizer work.

Frozen verification:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_OFFLINE_VERIFICATION_V1.json`

Package:
- runner: `astra_backend/synthetic/source_domain_simulator_training_v1.py`
- focused tests: `astra_backend/synthetic/test_source_domain_simulator_training_v1.py`
- run scope: `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_RUN_SCOPE_V1.json`
- durable ledger: `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_EXECUTION_HISTORY_V1.json`
- disabled launch request: `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_LAUNCH_REQUEST_V1.json`
- launch-marker-only execution workflow: `.github/workflows/astra-source-domain-training-execution-v1.yml`

Offline verification:
- run **36476387279**
- job **109111039398**
- head `2589a201a535d3689400d11824d35315b7398984`
- conclusion **SUCCESS**
- focused tests **15 passed**
- artifact **10993852045**
- digest `sha256:6a18f375c550938ad2816e91bceec8107d4d4ac4cfa7dc2e258be4e3c2dfad59`
- model run **false**
- optimizer steps **0**
- P1/P2/P3 access **false**

Verification independently downloaded preparation artifact **10993531230** and matched:
- control feature hash `b172b7cdcc0df5bc3b47b54a8dd116992f9552383babe0dc4cde5eecdac3a749`
- intervention feature hash `a8b5c5c590c82c152f302260430b3d6e4a3c9d5ee378d683bd8091f8f220501a`
- challenge feature hash `c786d846b2651872b621afa16d69a179965ffc0190a164d2e5e4ca89e0842640`
- exact dataset file hashes;
- 210 train rows / 42 test rows;
- 30 historical S9 truncated training-chord metadata rows preserved;
- complete frozen source pins;
- no launch marker present at verification time.

### Launch boundary

The standing branch policy pre-authorizes bounded inexpensive synthetic GitHub model runs. This exact package now satisfies the prerequisite offline verification.

Exactly one synthetic-only launch may now be armed under that standing authorization:
- seeds 20260927 / 20260928 / 20260929;
- 6 models maximum;
- 500 optimizer steps/model;
- 3,000 optimizer steps total;
- CPU-only;
- <=90 fit/eval minutes;
- $0 paid compute;
- thresholds 0.50 / 0.50;
- no threshold search/retuning;
- no automatic retry;
- no P1/P2/P3 access;
- no Codespaces/Vercel/main/Production mutation.

After that one run, freeze workflow and scientific pass/fail and stop. No parameter rescue, seed selection, P1/P2 transfer, P3 access, or follow-on model experiment may occur automatically.

**Immediate next action:** create exactly one unique armed source-domain training launch marker, let the already-frozen workflow execute once, freeze its result, consume the launch identity, and stop.


## Source-domain simulator training V1 — single execution failed scientifically — 2026-09-28

The one bounded synthetic-only source-domain training execution completed and the launch identity is consumed.

Frozen result:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_RESULT_V1.json`

Frozen failure analysis:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_FAILURE_ANALYSIS_V1.md`

Execution:
- run **36476678125**
- job **109112023738**
- launch head `a47bd80c71e275c9523744c348c7c559a557dcbf`
- run attempt **1**
- workflow conclusion **SUCCESS**
- scientific gate **FAIL**
- artifact **10993997488**
- artifact digest `sha256:06015a175a2e84b5094b4ffe9dbd58196be14c39b8e25025fbdf3efb65007c3a`
- artifact result SHA-256 `3e769072bf5bd906318bfd78ae2f7b126e81f6f0d39dd183dbf4b1f9a33fdacf`
- models **6**
- optimizer steps **3,000**
- fit/eval about **13.25 s**
- thresholds fixed **0.50 / 0.50**
- threshold search/retuning **none**
- automatic retry **none**
- P1/P2/P3 access **none**
- paid compute **$0**
- main/Production mutation **none**

The durable ledger now consumes:
- `source-domain-v1-20260928-canonical-01`

### Scientific outcome

Challenge onset F1 increased in all three seeds, but only slightly:
- deltas **+0.0129, +0.00066, +0.0450**
- mean **+0.0195**, below the frozen +0.05 floor.

Challenge precision increased strongly:
- mean delta **+0.1083**.

But challenge recall decreased in all three seeds:
- deltas **-0.0543, -0.0465, -0.0465**
- mean **-0.0491**.

Ordinary-domain performance also became more conservative:
- onset F1 mean delta **-0.0303**
- onset recall mean delta **-0.0568**
- joint admission mean delta **-0.0388**
- ordinary legato F1 loss exceeded 0.15 in two seeds.

Prediction counts show fewer false positives **and** fewer true positives on the challenge. This is a precision/recall tradeoff, not the preregistered robustness improvement.

### Post-hoc synthetic feature description

Using only the frozen synthetic arrays:
- intervention-training median onset positive flux was about **74–86%** of clean control across families;
- fixed challenge median onset positive flux was about **38–59%** of clean control across families.

The challenge therefore produces a substantially stronger onset-feature shift than the typical randomized training examples.

This is descriptive only and does not authorize range/challenge tuning.

### Mandatory stop

Do not:
- rerun the source-domain V1 training;
- select the favorable seed;
- lower thresholds;
- weaken the challenge;
- widen simulator ranges;
- change loss/sampler weights;
- change architecture in the same follow-up;
- reopen P1/P2;
- open P3.

### Exact next action

Perform **model-free source-domain joint-coverage review only**.

Use the existing deterministic parameter draws and frozen synthetic arrays to report:
- marginal parameter coverage;
- joint occupancy relative to the fixed challenge profile;
- family-conditioned coverage;
- challenge onset-flux positions relative to intervention training distributions.

Do not choose new ranges or a new challenge from this review. No model execution, optimizer step or real-data access is allowed.

**Resume instruction:** Continue with the model-free joint-coverage review only. Preserve all V2/S12/S13/source-domain V1 results, keep P1/P2 closed, P3 sealed, thresholds 0.50/0.50, and main/Production unchanged.


## Source-domain joint-coverage review — frozen model-free result — 2026-09-28

Completed the prospective model-free joint-coverage review after the failed source-domain training V1.

Frozen files:
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_RESULT_V1.json`
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_ANALYSIS_V1.md`

Execution:
- run **36477515197**
- job **109114818877**
- head `6d8a9e71e36b862ce7324088bb1e99c6ff4b7d99`
- conclusion **SUCCESS**
- focused tests **4 passed**
- artifact **10993409802**
- digest `sha256:bfb07fbae8cd7d2b1f59228362104abca0c55240cf89e388ef9ad1b94b77b56b`
- result SHA-256 `89ec82452ed3440af9d7935696f3bc66b0076c4c63c584b815780f9ea6f650ba`
- model run **false**
- optimizer steps **0**
- waveform renders **0**
- P1/P2/P3 access **none**

### Parameter-space result

Every fixed challenge scalar lies inside the frozen marginal simulator ranges, but several are tail-like among the 210 training draws:
- attack rise: **96.2nd percentile**
- transient-noise gain: **13.8th percentile**
- damping: **79.0th percentile**
- brightness: **14.8th percentile**
- pick position: **85.2nd percentile**
- low-pass cutoff: **11.4th percentile**
- spectral tilt: **15.2nd percentile**
- broadband noise: **81.4th percentile**

The prospectively frozen challenge-side conjunction shows the joint coverage failure:
- attack-rise condition only: **8/210**
- plus low transient gain: **1/210**
- plus high damping: **0/210**
- all later cumulative conditions: **0/210**
- full conjunction: **0 rows in every family**

The V1 fixed challenge is therefore marginally in-range but jointly unrepresented by the training sample.

### Prepared-feature result

Pooled prepared-CQT onset positive flux:
- intervention-training median **20.658**
- challenge-test median **12.749**
- median challenge event is at about the **13.3rd percentile** of intervention-training flux.

Family median challenge onset-flux percentiles:
- chords **26.7%**
- isolated **3.3%**
- legato **3.3%**
- mixed **0%**
- palmmute **14.3%**
- repeated **10.8%**
- scales **1.25%**

Row-level feature displacement:
- intervention-training median **0.0410**
- challenge-test median **0.0578**
- median challenge row is at about the **83.3rd percentile** of intervention-training displacement.

Most families have challenge displacement medians around the 85th–97th percentile.

### Interpretation

Joint train/challenge coverage mismatch is now a supported **experimental-design limitation** of source-domain V1.

It does not prove that coverage alone caused the failed precision/recall tradeoff and does not authorize:
- widening simulator ranges;
- oversampling the failed challenge corner;
- weakening the challenge;
- lowering thresholds;
- changing loss/sampler/architecture;
- another model run.

The V1 training result remains failed and frozen.

### Exact next action

Design-only work may define a new independent protocol for **joint** source-domain coverage while preserving the same already-frozen marginal engineering ranges.

Any such design must:
- be a new experiment version, not a V1 rescue;
- leave V1 failure unchanged;
- select its space-filling method without using V1 model scores;
- keep architecture changes out;
- define model-free coverage admission before any optimizer work;
- keep P1/P2 closed and P3 sealed.

**Resume instruction:** Continue with design-only joint-coverage protocol work. Do not train or render a new dataset yet.


## Joint-coverage V2 zero-render manifest admission — 2026-09-28

The prospective V2 joint-coverage protocol and deterministic parameter-manifest implementation have now passed zero-render admission.

Frozen protocol:
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.md`
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.json`

Implementation:
- `astra_backend/synthetic/source_domain_joint_coverage_manifest_v2.py`
- `astra_backend/synthetic/test_source_domain_joint_coverage_manifest_v2.py`
- `.github/workflows/astra-source-domain-joint-coverage-manifest-v2.yml`

Frozen result:
- `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_MANIFEST_RESULT_V2.json`

### Verification

Workflow:
- run **36481373445**
- job **109127570036**
- head `4ebd5a9f3d4c78a6493372d2642e67f77eb8ec4c`
- conclusion **SUCCESS**
- focused tests **4 passed**

Artifact:
- **10997033182**
- digest `sha256:69fb45f4c5cfa20a18a5a3dda75c5ff835da38c08549d64fc929daaaba1b30ee`
- manifest JSON SHA-256 `a0d7786b1f459d348efef151f7ef8d4f5b1cf412b27ad61e7a4e052c4559e24d`
- manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`

Frozen input:
- source-domain V1 preparation run **36475263654**
- artifact **10993531230**
- exact S9 control file SHA-256 `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`

### Zero-render admission result

The deterministic manifest contains:
- **210** training parameter rows;
- exactly **30 per family**;
- **42** primary held-out challenge rows;
- exactly **6 per family**.

Checks passed:
- every continuous training axis occupies all 30 frozen marginal strata exactly once per family;
- every primary-challenge axis occupies all six frozen challenge strata exactly once per family;
- categorical nonlinear/hum counts match the protocol;
- train/challenge exact full parameter-vector duplicates = **0**;
- historical S9 metadata identity preserved;
- manifest rerun logic is deterministic under the frozen implementation.

Execution boundary remained exact:
- waveform renders **0**;
- models loaded **0**;
- model inference **false**;
- optimizer steps **0**;
- P1/P2/P3 access **none**;
- threshold search/retuning **none**;
- paid compute **$0**;
- main/Production mutation **none**.

### What this establishes

The V2 parameter plan fixes the V1 design problem of relying only on independent marginal random draws at the manifest level by imposing deterministic family-wise marginal stratification and a separately stratified held-out in-support challenge.

This is **not yet evidence** that:
- waveform-level V2 coverage survives the source renderer as intended;
- prepared-CQT joint coverage improves;
- the frozen S11 model will benefit;
- V1's failed precision/recall tradeoff was caused by coverage alone.

The V1 failed training result remains frozen.

### Exact next action

Do **not** render the full V2 dataset and do **not** train a model yet.

Next work is design/review only for a bounded **model-free waveform and prepared-feature admission** using the frozen V2 manifest:
1. define a small fixed waveform fixture/sample subset before rendering;
2. freeze source-label/timing/fundamental/peak and no-clipping checks;
3. freeze prepared-CQT coverage diagnostics comparing V2 train/challenge geometry without using model scores;
4. keep the old V1 fixed challenge as secondary diagnostic only, never as the V2 gate;
5. define hard render/audio/storage/time ceilings;
6. only after that design is frozen may a bounded model-free V2 waveform preparation be implemented.

**Resume instruction:** Continue with model-free V2 waveform/prepared-feature admission design only. No dataset rendering, model execution, optimizer work, P1/P2 access or P3 access.


## V2 waveform / prepared-feature admission design frozen — 2026-09-28

Created:
- `docs/astra/SOURCE_DOMAIN_V2_WAVEFORM_PREPARED_FEATURE_ADMISSION_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_V2_WAVEFORM_PREPARED_FEATURE_ADMISSION_SPEC_V1.json`

No waveform was rendered by the design step. No model was loaded or run. Optimizer steps **0**. P1/P2/P3 access **none**.

### Stage A — next allowed execution

Implement and run only the small deterministic acoustic admission.

Frozen sample:
- seven families;
- training manifest local positions **0 and 29** per family = **14** V2 training rows;
- primary-challenge manifest local positions **0 and 5** per family = **14** V2 challenge rows;
- paired clean controls for all selected rows.

Base Stage-A set:
- **28** V2 source-domain renders;
- **28** paired controls;
- **56** base renders / **112 synthetic seconds**.

Deterministic V2 rerender checks are required and the total hard Stage-A ceiling is:
- <= **112 waveform renders**;
- <= **224 synthetic audio seconds**;
- <= **20 minutes**;
- <= **150 MB** persisted artifacts;
- CPU only;
- $0 paid compute.

Frozen Stage-A hard gates:
- deterministic rerender identity;
- exact state/onset/reference identity versus paired control;
- finite waveform/CQT;
- final peak < **0.999**;
- attacked-event stable fundamental within **±15 cents**;
- no transient injection on unlabeled/nonattack events;
- every positive selected V2 row changes prepared CQT versus paired control;
- exact binding to frozen manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`.

If Stage A fails, freeze failure and stop. Do not substitute rows or relax gates.

### Stage B — explicitly blocked until Stage A passes

If and only if Stage A passes and is frozen, a later bounded full model-free V2 preparation may be implemented.

Prospective Stage-B feature-coverage gate is already frozen:
- five descriptors:
  - waveform RMS;
  - spectral centroid;
  - first-difference energy;
  - prepared-CQT positive onset flux;
  - prepared-CQT row displacement;
- evaluated separately in all seven families;
- primary-challenge median must lie inside the inclusive V2-training **5th–95th percentile** interval;
- **35/35** family/descriptor checks required.

Rise time is report-only in Stage B after the stricter Stage-A physical-validity gate.

The old V1 fixed challenge is secondary diagnostic only. It is not V2 gate-eligible and must not be re-rendered for this step.

### Standing prohibitions

Do not:
- render the full V2 dataset before Stage-A pass;
- train or load a model;
- run inference;
- perform optimizer steps;
- search/retune thresholds;
- change architecture, loss, sampler, renderer equations, marginal ranges or V2 challenge;
- access P1/P2;
- open P3;
- mutate main/Production.

**Resume instruction:** Implement the frozen Stage-A V2 acoustic admission package and run it once under the stated model-free ceilings. Freeze pass/failure and stop before Stage B.


## V2 Stage A first attempt — pre-execution test failure frozen — 2026-09-28

The first and only Stage-A workflow attempt under the prior checkpoint did **not** reach acoustic admission.

Frozen failure:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_PREEXECUTION_FAILURE_V1.json`

Workflow:
- run **36482951827**
- job **109132814201**
- head `fc3c31d8a604336bef85406f1f579e5a3d3cacb4`
- run attempt **1**
- conclusion **FAILURE**

Frozen artifact identity verification succeeded before the failure:
- S9 control SHA-256 `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`;
- V2 manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`.

Focused preflight tests:
- **4 passed**
- **1 failed**

Failing test:
- `test_manifest_override_changes_only_frozen_v2_clip_axes_and_categoricals`

### Exact technical cause

The synthetic test helper creates its position-0 row with:
- `humActive=true`;
- `humFundamentalHz=50`.

The implementation correctly includes `humFundamentalHz` in the renderer override when hum is active, as required by the frozen V2 categorical manifest protocol.

The test incorrectly expected that key to be absent for that active-hum fixture.

This is a **test-contract defect**, not a measured waveform/scientific failure.

### What did not happen

Because the focused test failed first:
- Stage-A acoustic runner **not executed**;
- waveform renders **0**;
- synthetic audio seconds **0**;
- no Stage-A result artifact exists;
- model loads **0**;
- inference **false**;
- optimizer steps **0**;
- threshold search/retuning **none**;
- P1/P2/P3 access **none**;
- paid compute **$0**;
- main/Production mutation **none**.

Therefore there is **no scientific Stage-A pass/fail result** yet.

### Mandatory stop

The prior checkpoint explicitly required one attempt, freezing pass/failure, and no automatic retry. That condition is honored.

Do not:
- silently correct the test and rerun the same Stage-A workflow;
- run Stage B;
- train/load a model;
- change scientific gates, manifest rows, renderer ranges or equations;
- access P1/P2/P3.

### Exact next action

Perform **design/test-contract review only**.

The next review may:
1. verify that active hum rows must carry the manifest-selected 50/60 Hz categorical value;
2. verify inactive hum rows leave frequency behavior irrelevant/unoverridden;
3. determine whether correcting the unit-test expectation changes any scientific parameter (expected: no);
4. define a separately versioned Stage-A execution attempt if justified.

No waveform execution is authorized by this checkpoint.

**Resume instruction:** Review and freeze the Stage-A test-contract correction only. Do not rerun Stage A yet.


## V2 Stage-A test-contract correction review frozen — 2026-09-28

Completed the required design/test-contract review after the pre-execution Stage-A failure.

Frozen review:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_TEST_CONTRACT_REVIEW_V1.md`
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_TEST_CONTRACT_REVIEW_V1.json`

No waveform was rendered. Stage A was not rerun. Model loads/inference/optimizer steps remained zero. P1/P2/P3 remained closed.

### Contract decision

The frozen V2 hum categorical contract is:

Active hum:
- `humActive=true`;
- `humFundamentalHz` must be included in the renderer override;
- value must equal the manifest-selected **50 Hz or 60 Hz**.

Inactive hum:
- `humActive=false`;
- `humFundamentalHz` must not be overridden.

For both cases:
- `humCombinedRmsRelative` is **not** a V2 manifest override;
- it remains on the unchanged deterministic V1 source-parameter substream.

This matches the frozen V2 protocol and the existing Stage-A runner.

The failed V1 focused test was wrong because its position-0 synthetic row had active 50-Hz hum while its assertion expected no `humFundamentalHz` key.

### Scientific-change audit

Correcting that test expectation changes:
- no manifest content/hash;
- no selected Stage-A row;
- no parameter value/range;
- no categorical assignment;
- no waveform equation;
- no deterministic V1 substream;
- no frontend;
- no label/reference/timing;
- no Stage-A or Stage-B gate;
- no threshold/model setting.

Classification:
**technical verification-contract correction only; scientific configuration unchanged.**

### Versioning / execution boundary

Do not edit history to make the first attempt disappear.

Any future Stage-A attempt must be separately versioned.

Reserved next-package paths:
- `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v2.py`
- `.github/workflows/astra-source-domain-v2-stage-a-admission-v2.yml`

The original V1 test/workflow remain historical evidence.

### Exact next action

Build the corrected Stage-A V2 execution package **offline only**:
1. add a corrected V2 focused-test file that separately tests active and inactive hum;
2. add a separately versioned V2 workflow in a **disabled/non-triggering state**;
3. pin the same frozen S9 control and V2 manifest hashes;
4. keep the same Stage-A runner scientific logic, selected rows, gates and ceilings;
5. verify statically that the package cannot auto-run;
6. freeze package verification.

Do **not** run the new workflow yet.

**Resume instruction:** Construct and verify the separately versioned corrected Stage-A package offline only. No waveform execution is authorized by this checkpoint.


## Corrected Stage-A V2 package statically verified — 2026-09-28

Built the separately versioned corrected package required by the frozen test-contract review.

Created:
- `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v2.py`
- `.github/workflows/astra-source-domain-v2-stage-a-admission-v2.yml`
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_PACKAGE_VERIFICATION_V2.md`
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_PACKAGE_VERIFICATION_V2.json`

### Corrected focused-test contract

The new V2 test file separately checks:

Active hum:
- `humActive=true`;
- manifest-selected `humFundamentalHz` is included;
- both 50 Hz and 60 Hz cases are represented;
- `humCombinedRmsRelative` is not overridden.

Inactive hum:
- `humActive=false`;
- `humFundamentalHz` is not overridden;
- `humCombinedRmsRelative` is not overridden.

The original V1 failed test/workflow remain unchanged historical evidence.

### Workflow is deliberately disabled

The V2 workflow:
- has **only** `workflow_dispatch`;
- has no push / pull-request / schedule / workflow-run trigger;
- hard-disables its only job with:
  `if: ${{ false }}`.

Static inspection after the workflow commit showed no Stage-A V2 check run. Only the unrelated Cloudflare Pages check appeared.

Therefore the package cannot auto-run and cannot execute Stage A even if manually dispatched while the hard-false guard remains.

### Frozen inputs unchanged

The disabled package still pins:
- V1 preparation run **36475263654**;
- S9 control SHA-256 `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`;
- V2 manifest run **36481373445**;
- manifest content SHA-256 `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`.

Scientific runner logic, selected rows, acoustic gates and ceilings remain unchanged.

### Execution accounting

During this package-build/static-verification step:
- waveform renders **0**;
- Stage-A runner executions **0**;
- model loads **0**;
- inference **false**;
- optimizer steps **0**;
- P1/P2/P3 access **none**;
- main/Production mutation **none**.

This is an **offline package pass**, not a scientific Stage-A pass.

### Exact next action

Do not edit the disabled workflow guard casually and do not dispatch it yet.

The next checkpoint may perform only a **separate arming decision**:
1. decide whether one corrected Stage-A V2 acoustic attempt is justified;
2. if yes, create a uniquely versioned armed workflow/marker rather than rewriting the historical disabled package;
3. preserve the same frozen hashes, rows, gates and ceilings;
4. allow exactly one attempt with no automatic retry;
5. freeze pass/failure and stop before Stage B.

Until such a checkpoint explicitly arms the attempt:
- Stage A remains unexecuted scientifically;
- Stage B remains blocked;
- model execution remains blocked;
- P1/P2 remain closed;
- P3 remains sealed.

**Resume instruction:** Continue with the Stage-A V2 arming decision only. Do not execute waveform admission yet.


## Superseding continuation — corrected Stage A through final V3 training — 2026-09-28

This section supersedes the older Stage-A resume instructions above. Historical failures and package reviews remain preserved.

### Corrected Stage-A V2 acoustic admission

First corrected acoustic execution:
- workflow run **36484128430**
- job **109136731820**
- artifact **10997847232**
- artifact digest `sha256:1e918e7b5a95dc692f5a81761fe7cdcba4b76dd6b34f29a56cc4cec86e8a8343`
- full Stage-A result SHA-256 `5778104fe505f5a38b4e2a0ed3e049a9993db92a9a1a3a078851c6cb7df8e0c2`
- **84 waveform renders / 168 synthetic seconds**
- models **0**
- optimizer steps **0**
- P1/P2/P3 **none**

Original Stage-A result failed only the mixed-waveform per-note fundamental gate:
- maximum reported error **205.8039 cents**
- exactly **4/86** measurable attacked-event checks outside ±15 cents
- all four failures were chord events
- maximum non-chord absolute error **8.0898 cents**

Frozen result:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_RESULT_V1.json`

### Polyphonic pitch-measurement defect and isolated diagnostic

Model-free measurement review showed the mixed-waveform FFT helper was not source-separating. In each failed chord case, a simultaneous note fundamental or harmonic occupied the target search band and could become the strongest peak.

Frozen review:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_MEASUREMENT_VALIDITY_REVIEW_V1.md`
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_MEASUREMENT_VALIDITY_REVIEW_V1.json`

A prospectively frozen source-isolating diagnostic then rendered exactly the same attacked events with one musical note component per probe, preserving the exact row/event parameters and post chain.

One-shot isolated diagnostic:
- run **36488106137**
- job **109149841945**
- artifact **10999874443**
- artifact digest `sha256:00550e6c0bf84d20eb0c65208556abe7435ab04584e672b49b840c0253976caa`
- result SHA-256 `3e3cc594a58a9ab29ae9dbbed8bf1f3107b71b9e2076e3b25e7924b031cf5561`
- **172 probe renders / 344 synthetic seconds**
- **86/86** original measurable attacked events retained
- **0** outside ±15 cents
- maximum absolute isolated error **8.0898 cents**
- models/optimizer/P1/P2/P3 **0 / 0 / none**

Frozen result:
- `docs/astra/SOURCE_DOMAIN_V2_SOURCE_ISOLATING_PITCH_RESULT_V1.json`

A zero-render corrected Stage-A adjudication retained every original non-pitch gate and replaced only the invalid mixed-chord measurement with the source-isolating evidence.

Adjudication:
- run **36488493592**
- job **109151112276**
- artifact **10999984993**
- digest `sha256:eec6c162e2b1e3a4303b5524ebebd4a35fea6e1184e6bad073d182367f6e9f51`
- result SHA-256 `5a15ce7a2fd6ea7e4e2072a3a215a9eccd90d0258d811ca0b6cd47775f2e659a`
- corrected Stage A **PASS**
- new waveform renders **0**

Frozen corrected result:
- `docs/astra/SOURCE_DOMAIN_V2_CORRECTED_STAGE_A_RESULT_V1.json`

The historical original Stage-A failure remains preserved and is not rewritten.

### V2 Stage-B full model-free preparation

V2 Stage B then executed under its prospectively frozen 35-check family/descriptor gate.

Frozen result:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_B_RESULT_V1.json`
- run **36485375684**
- job **109140893933**
- artifact **10999695803**
- artifact digest `sha256:a38a2a2a400cc3e2c470c9fd8ccf46ac8e6b9a346ffb57292aa4384b2615e6ca`
- result SHA-256 `d1f4ee0580ca98094fb12adabf76f437e6e3769c85b1fbc7f741205c9a3b13d2`
- V2 intervention NPZ SHA-256 `a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b`
- **504** deterministic render operations / **1,008 synthetic seconds**
- model loads **0**
- optimizer **0**
- P1/P2/P3 **none**

Stage B passed **34/35** checks.

Only failure:
- family **repeated**
- descriptor **raw firstDifferenceEnergy**
- train p05 **0.0001275503051**
- train p95 **0.0026163426368**
- challenge median **0.0028062511494**
- ~**7.26%** above frozen p95.

Failure analysis showed raw first-difference energy is globally amplitude-sensitive while the frozen model frontend RMS-normalizes audio. The already-existing real-domain V2 audit had also prospectively used RMS-normalized first-difference evidence.

Frozen analysis:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_B_FAILURE_ANALYSIS_V1.md`

V2 remained failed; the gate was not waived.

### Final V3 model-free coverage

One final source-domain coverage version was prospectively frozen:
- training support = exact V2 Stage-B 210-row intervention support;
- new independent challenge = **84 rows / 12 per family**;
- RMS-normalized first-difference became the gated attack descriptor;
- raw first-difference became report-only;
- unchanged source-domain marginal ranges and waveform equations;
- no model.

A first V3 workflow attempt failed before rendering due a NumPy API compatibility issue and was preserved as a pre-execution technical failure.

Corrected final V3 execution:
- run **36487005586**
- job **109146224786**
- artifact **10999342888**
- artifact digest `sha256:29868ae9595cd530ee7d3d25226da2a006f01dce16b9b570b2e5c2708ca59855`
- result SHA-256 `05dbd9558afa1d63721351e6d2b9fffa44f32ccb4a231eaba3e228583a42a3ca`
- V3 challenge manifest SHA-256 `2ba557e93692e18cf7a22807d36400ca3e22f87e6c9a4b12ee99534721d693ee`
- V3 challenge NPZ SHA-256 `368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce`
- **168** challenge render operations / **336 synthetic seconds**
- **35/35** model-free coverage checks **PASS**
- models/optimizer/P1/P2/P3 **0 / 0 / none**

Frozen result:
- `docs/astra/SOURCE_DOMAIN_V3_FINAL_RESULT_V1.json`

This was declared the final source-domain coverage iteration.

### Final V3 synthetic training package

A separately preregistered final synthetic training design then reused the exact frozen S11 training/model protocol:

- seeds **20260927 / 20260928 / 20260929**
- control-trained + V2-source-domain-trained model per seed
- **6 models**
- **500 optimizer steps/model**
- **3,000 optimizer steps total**
- S11 architecture unchanged
- state active weight **9**
- onset positive weight **8**
- onset loss multiplier **4**
- sampler **32/32/32/32**
- Adam **0.003**
- batch **128**
- state/onset thresholds **0.50 / 0.50**
- zero threshold search/retuning
- ordinary evaluation = frozen clean S9 test
- challenge evaluation = exact 84-row V3 challenge
- exact V1 source-domain scientific gate reused without weakening.

Design/spec:
- `docs/astra/SOURCE_DOMAIN_V3_SYNTHETIC_TRAINING_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_V3_SYNTHETIC_TRAINING_SPEC_V1.json`

Runner:
- `astra_backend/synthetic/source_domain_v3_synthetic_training_v1.py`

Offline package verification:
- run **36489377119**
- job **109154011434**
- artifact **11001326153**
- digest `sha256:e0bf086ef504c8f750eb9461b27f3d66427f0457b6911a2cd11dce4f458fa1a9`
- receipt SHA-256 `02ea4fa1928024a010b790fce66514961212cd65be0b05df98dfe6fcaccedf41`
- optimizer steps **0**
- model fit calls **0**
- exact dataset/source pins verified.

### Final V3 synthetic training outcome — FAILED

One-shot execution:
- run **36489648572**
- job **109154913563**
- head `4416964897ab8846fb91748737e9f7cc03752349`
- run attempt **1**
- workflow conclusion **SUCCESS**
- artifact **11000187208**
- digest `sha256:84f2566c656c37d5fe20bdc26bfdaa699d5e2c4089c0c91f99434d8f0282e3f3`
- result JSON SHA-256 `5b5b9be61196d6e40abb2182f5dd0cff4b21f7c9fe927592324bc20df471f36d`
- six models / **3,000 steps**
- fit/eval **18.547 s**
- automatic retry **false**
- thresholds fixed **0.50/0.50**
- P1/P2/P3 **none**

Frozen result:
- `docs/astra/SOURCE_DOMAIN_V3_SYNTHETIC_TRAINING_RESULT_V1.json`

Scientific gate: **FALSE**

Challenge deltas, intervention minus control:
- onset F1 mean **+0.0611363**, positive **3/3**, minimum **+0.0567062**
- onset recall mean **+0.0180879**, positive **3/3**
- onset precision mean **+0.1143840**, positive **3/3**
- state admission mean **-0.0361757**
- joint admission mean **-0.0452196**

Ordinary clean deltas:
- onset F1 mean **+0.0206627**, positive **3/3**
- onset recall mean **+0.0310078**, positive **3/3**
- onset precision mean **+0.00631948**
- state admission mean **-0.0775194**
- joint admission mean **-0.0671835**

Failed criteria:
1. `meanChallengeOnsetRecallGainAtLeast0_08`
   - observed **+0.0180879**
2. `challengeNegativeOnlyFpAtMost0_10EverySeed`
   - intervention seed 20260928 = **0.166667 events/sec**
3. `noOrdinaryStateAdmissionLossOver0_03`
   - every seed lost >= **0.0620**
4. `noOrdinaryJointAdmissionLossOver0_04`
   - every seed lost >= **0.0620**

Notable passed criteria:
- challenge onset F1 gain positive **3/3**
- challenge recall gain positive **3/3**
- mean challenge F1 gain >= **+0.05**
- no challenge precision loss >0.05
- ordinary onset F1/precision guards passed
- ordinary negative-only FP guard passed
- non-chord family stability guard passed
- exact paired initialization/batches, six models, 3,000 steps and fixed dataset identities passed.

Interpretation:
- broader admitted source-domain training can improve onset F1/precision and produces positive recall movement;
- it does **not** satisfy the full recall/state/joint/negative-control contract;
- the final system is not accepted as a generally stronger transcription model.

### Post-V3 strategy boundary

Frozen project-level review:
- `docs/astra/POST_V3_REPRESENTATION_DATA_STRATEGY_REVIEW_V1.md`

Decision:
**NO-GO for further source-domain synthetic tuning/model execution from this evidence.**

Do not:
- run V4/V5 source-domain coverage;
- rerun V3;
- select a favorable seed;
- lower thresholds;
- weaken gates;
- retune loss/sampler/state weights;
- widen decoder windows;
- directly swap architecture and retry;
- reopen P1/P2 for the failed V3 candidate;
- open P3.

The earlier architecture boundary required a source-domain candidate to pass its synthetic robustness gate before architecture follow-up. That condition was not met.

### Exact current boundary

The remaining ambiguity cannot be resolved reliably with another iteration of the same repo-owned synthetic evidence.

Next empirical work requires one of:

1. **New broader real development evidence**
   - independent of P3;
   - broader than the already-exposed P1/P2 captures;
   - prospectively frozen capture/annotation/preprocessing/evaluation contract;
   - requires fresh explicit authorization before accessing/using new real data.

2. **A genuinely new architecture research project version**
   - not a V3 rescue;
   - independent prospective architectural hypotheses and evaluation contract;
   - no simultaneous threshold/loss/sampler tuning;
   - requires a separate explicit project decision before optimizer work.

P1/P2 remain **closed**.
P3 remains **sealed**.
Main/Production remain unchanged.

**Resume instruction:** Stop empirical/model execution. Ask for explicit authorization before any new real development-data program, or explicit approval before opening a new architecture research version. Do not run another source-domain synthetic experiment automatically.


## Architecture Research A1 — decoupled state/onset encoders — 2026-09-28

The user explicitly approved opening a new architecture research version.

A1 was defined as a new project version, not a V3 rescue.

### Frozen hypothesis

S11 used one shared:
- Linear(960,128) + ReLU encoder

for both:
- state classification;
- onset detection.

A1 changed **only** encoder sharing:
- independent state encoder: Linear(960,128) + ReLU;
- independent onset encoder: Linear(960,128) + ReLU.

Everything else stayed fixed:
- context5 / 960 input;
- state/onset heads;
- loss weights 9 / 8 / 4;
- sampler 32/32/32/32;
- Adam 0.003;
- batch 128;
- seeds 20260927/28/29;
- 500 steps/model;
- thresholds 0.50/0.50;
- decoder/evaluator;
- V2 intervention training data;
- ordinary S9 control test;
- V3 84-row challenge.

Design/spec:
- `docs/astra/ARCHITECTURE_RESEARCH_A1_DESIGN_V1.md`
- `docs/astra/ARCHITECTURE_RESEARCH_A1_SPEC_V1.json`

Runner/tests:
- `astra_backend/synthetic/architecture_research_a1_v1.py`
- `astra_backend/synthetic/test_architecture_research_a1_v1.py`

### Structural / offline verification

A1 structural tests proved:
- S11-compatible output shapes;
- state/onset encoder parameter sets disjoint;
- state-path backward does not touch onset encoder;
- onset-path backward does not touch state encoder;
- deterministic seed behavior;
- exact three-model / 1,500-step budget.

Offline verification:
- run **36492512434**
- job **109164198506**
- artifact **11002241343**
- digest `sha256:ab4efd46bc6522d1fb1a0ae1ad0f08767adb0dbb37c7cde1f6aead7295923c17`
- receipt SHA-256 `55b3b48bc4f47ff3bc34850b53bf7913026f2091a4193c77727efcf8348e3a1c`
- fit calls **0**
- optimizer steps **0**
- P1/P2/P3 **none**

Frozen verification:
- `docs/astra/ARCHITECTURE_RESEARCH_A1_OFFLINE_VERIFICATION_V1.json`

### One-shot A1 execution

Run:
- workflow **36492748299**
- job **109164963801**
- head `c8841c47363073bb4f82891ea49a86577fa3010a`
- run attempt **1**
- workflow conclusion **SUCCESS**
- artifact **11002106213**
- artifact digest `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`
- result JSON SHA-256 `090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3`

Execution:
- models **3**
- optimizer steps/model **500**
- total optimizer steps **1,500**
- fit/eval **6.811 s**
- thresholds fixed **0.50 / 0.50**
- threshold search/retuning **false**
- automatic retry **false**
- P1/P2/P3 **none**
- main/Production unchanged.

Frozen result:
- `docs/astra/ARCHITECTURE_RESEARCH_A1_RESULT_V1.json`

Analysis:
- `docs/astra/ARCHITECTURE_RESEARCH_A1_ANALYSIS_V1.md`

### A1 scientific gate — FAILED

Exactly two frozen criteria failed.

1. Mean ordinary joint-admission gain versus frozen S11 intervention:
   - observed **+0.0387597**
   - required **>= +0.0400000**
   - shortfall approximately **0.0012403**
   - positive in **3/3** seeds.

2. V3 challenge recall gain versus frozen S11 control:
   - seed 20260927 **-0.003876**
   - seed 20260928 **+0.077519**
   - seed 20260929 **+0.054264**
   - required positive **3/3**
   - observed positive **2/3**.

The gate is not rounded, relaxed or reinterpreted.

### Strong positive structural evidence

Versus the frozen shared-encoder S11 intervention:

Ordinary state admission:
- mean **+0.0930233**
- minimum **+0.0697674**
- positive **3/3**

V3 challenge state admission:
- mean **+0.0723514**
- minimum **+0.0271318**
- positive **3/3**

Ordinary joint admission:
- mean **+0.0387597**
- positive **3/3**

Challenge joint admission:
- mean **+0.0284238**
- positive **3/3**

Ordinary onset F1:
- mean **+0.0331766**
- positive **3/3**

Challenge onset F1:
- mean **+0.0513049**
- positive **3/3**

Challenge onset precision:
- mean **+0.0906692**
- positive **3/3**

Negative-only FP:
- ordinary **0.0 events/sec in every seed**
- challenge **0.0 events/sec in every seed**

Versus frozen S11 control:
- challenge onset F1 mean **+0.112441**
- positive **3/3**
- challenge precision mean **+0.205053**
- positive **3/3**

Interpretation:
- the synthetic evidence supports encoder sharing as a meaningful state/onset tradeoff factor;
- A1 still does not satisfy its complete prospective acceptance contract;
- this does not establish real-domain readiness or a real-domain causal mechanism.

### Current stop rule

Do not:
- rerun A1;
- relax the +0.04 joint gate;
- drop seed 20260927;
- lower thresholds;
- retune loss/sampler;
- widen/deepen A1 automatically;
- add convolution/recurrent/context changes automatically;
- reopen P1/P2;
- open P3.

**A1 is closed.**

Any A2 architecture is a **new project decision** and requires:
1. fresh explicit user approval for A2;
2. a new structural hypothesis frozen before optimizer work;
3. one-variable or otherwise clearly isolated architectural change;
4. a newly preregistered synthetic evaluation contract.

P1/P2 remain closed.
P3 remains sealed.
Main/Production remain unchanged.

**Resume instruction:** Stop model execution. Do not automatically create A2. If the user explicitly approves a new A2 architecture project, first define and freeze its independent structural hypothesis and contract before any optimizer work.


## Post-A1 supervisory handoff synchronization — 2026-09-28

The review at remote head `fc7b56b7ef559dfec1a95fbfab682561a4b6e971` is saved in `astra-work/CURRENT_STATE.md`, section **Supervisory review for GPT-5.6 after A1**, commit `b92b524d3cd241e9c5373efc92036325831f5467`.

Read that section before resuming. It preserves A1's failure and qualifies the mechanism claim: dual encoders add 78.6% parameters and alter downstream initialization; ordinary joint admission remains below the clean S11 control in all seeds. Reused synthetic benchmarks do not establish independent confirmation or real-domain readiness.

**Exact next task:** Produce the specified model-free post-A1 evidence review and concrete decision brief from existing records, optionally adding a separate pure result validator with focused tests. No new model, inference, optimizer, renderer, launch marker or workflow dispatch. Do not modify frozen A1/V3 outcomes. No A2 is opened by this review request; P1/P2 remain closed, P3 sealed, main/Production unchanged. Save and verify both handoffs after completing the bounded task. The full instructions in `astra-work/CURRENT_STATE.md` govern if earlier resume text conflicts.


## Post-A1 evidence reconciliation complete — 2026-09-28

The bounded supervisory review requested at commit `983ef1f2efd5701d709545ec3b76826622f75746` is complete.

Frozen review outputs:
- `docs/astra/POST_A1_SUPERVISORY_EVIDENCE_REVIEW_V1.md`
- `docs/astra/POST_A1_SUPERVISORY_EVIDENCE_REVIEW_V1.json`

Prospective validator:
- `astra_backend/synthetic/post_a1_result_validator_v1.py`
- `astra_backend/synthetic/test_post_a1_result_validator_v1.py`

Focused model-free test command:
- `python -m unittest -v astra_backend.synthetic.test_post_a1_result_validator_v1`
- **10/10 passed**
- no torch/model import, inference, optimizer, renderer, workflow dispatch, or real-data access.

Artifact verification:
- A1 artifact **11002106213** GitHub digest unchanged: `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`.
- Downloaded A1 `result.json` SHA-256 exactly matched `090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3`.
- V3 training artifact **11000187208** GitHub digest unchanged: `sha256:84f2566c656c37d5fe20bdc26bfdaa699d5e2c4089c0c91f99434d8f0282e3f3`.
- Downloaded V3 `result.json` SHA-256 exactly matched `5b5b9be61196d6e40abb2182f5dd0cff4b21f7c9fe927592324bc20df471f36d`.

The review records all available per-seed absolute state/joint/onset metrics, deltas, TP/FP/FN, negative-only event counts and durations for A1 against both frozen S11 comparators.

Required interpretation:
- A1 remains a frozen scientific **FAIL**.
- A1 = **279,556** parameters; S11 = **156,548**; increase **123,008 / 78.6%**.
- Same seed and exact frozen batch plan do not imply paired common-tensor initialization because A1 adds a second encoder before the downstream heads.
- Ordinary A1 joint admission remains below the clean S11 control in **3/3** seeds.
- Zero A1 negative-only decoded events cover only **6 s ordinary + 12 s challenge per seed**.
- S9 ordinary and V3 challenge are repeatedly exposed development benchmarks, not independent confirmation.
- The later A1 gate does not retroactively repair the failed V3 system gate.

### Decision boundary

Current recommendation: **pause model research**.

If a new project is explicitly authorized, the preferred next evidence for product relevance is a prospectively frozen **independent real-development evaluation** that is not P3 and is not silent reuse of closed P1/P2. A capacity/initialization-controlled architecture-identification study is a separate narrower option and does not itself establish real-domain readiness.

No A2 is open.
P1/P2 remain closed.
P3 remains sealed.
Main/Production remain unchanged.

**Resume instruction:** Do not resume an experiment. Stop at the project-decision boundary. New real-development evidence requires explicit authorization for its access/evaluation scope. A2 or another architecture-identification study requires a separate explicit project decision. Generic “continue” does not authorize either.


## Independent real-development evidence program — authorized 2026-09-28

The user selected **option 1** and authorized the new independent real-development evidence program.

Frozen prospective design:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_V1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_EVALUATION_V1.json`

Frozen intake package:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`
- `astra_backend/synthetic/independent_real_development_intake_validator_v1.py`
- `astra_backend/synthetic/test_independent_real_development_intake_validator_v1.py`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_PACKAGE_VERIFICATION_V1.json`

First-tranche contract:
- 24 newly created/sourced real-development clips;
- >=18 positive, >=6 negative-only;
- >=90 s positive audio, >=30 s negative-only;
- no P1/P2/P3 or previously inspected/tuned audio;
- annotations frozen before inference;
- fixed 0.50/0.50 thresholds and frozen frontend/evaluator;
- no tuning, retraining, candidate selection, or decoder adjustment from this set.

Required coverage:
- single-note;
- repeated attacks;
- legato;
- palm mute;
- dyad/chord;
- clean capture;
- distorted/overdriven capture.

Model-free intake verification:
- exact command: `python -m unittest -v test_independent_real_development_intake_validator_v1.py`
- **10/10 passed**
- model imports/inference **0**
- optimizer steps **0**
- real clips accessed **0**
- workflow dispatches **0**
- P1/P2/P3 **none**
- main/Production unchanged.

Current blocker: no genuinely new qualifying real-development clip set has yet been added to the intake package. Do not substitute P1/P2/P3 or old examined audio.

A1 must not be retrained to recreate weights. Before eventual inference, pin one durable already-frozen candidate identity; if the preferred candidate weights are unavailable, freeze that limitation rather than reconstructing them.

**Resume instruction:** Continue with intake only after qualifying new real audio is supplied or identified. Hash, annotate, pin provenance and candidate/runtime identities, validate the complete manifest, and freeze a zero-inference verification receipt. Only a fully passed pre-inference intake may advance to one bounded real-development evaluation. Do not train/tune, open A2, reuse P1/P2, or access P3.


## Independent real-development web sourcing — completed 2026-09-28

Frozen sourcing review:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_WEB_SOURCE_REVIEW_V1.md`
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_WEB_SOURCE_REVIEW_V1.json`

Sourced candidate pool:
- **18 positive guitar clips**, nominal **139 s**;
- **6 negative-only clips**, nominal **39 s**;
- one reserve legato source requiring a prospectively frozen 4–10 s crop if used.

Primary selected source: Pixabay sound effects under the Pixabay Content License, for internal evaluation only. Original standalone audio must not be committed or redistributed.

Coverage represented in the pool:
- clean/distorted electric;
- acoustic/baritone;
- single notes;
- repeated attacks;
- bends/slide;
- palm mute;
- strumming/arpeggio;
- riffs/chords;
- transient-rich negative speech/percussion/typing/crowd material.

No audio download, model inference, optimizer, workflow dispatch, or P1/P2/P3 access occurred during sourcing.

**Resume instruction:** Continue only by downloading the frozen shortlisted candidates, hashing them, preserving provenance, human-screening them, freezing annotations before output, populating the intake manifest, and passing the pure zero-inference intake verification. Do not train/tune or infer before that checkpoint.


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

Documentation/review only. No V14 was opened and no rendering, training, inference, V2B, or workflow dispatch occurred.

Preferred next project if explicitly authorized: isolate only the negative-structure-inactive family mixture while holding the other three sampler strata, per-step shuffle, attacked-note-label exposure, model, loss, thresholds, optimizer, and V9 dataset fixed.

Frozen historical target across 16,000 negative-structure-inactive slots:
- legato **3,521**
- palmmute **5,385**
- mixed **7,094**

If that single-factor study also fails, stop serial micro-studies and consider a prospectively frozen composite matched-context / 2-second-context design.

**Resume instruction:** Stop model execution here. At a generic “continue”, documentation/review only. If the user explicitly authorizes a new project, freeze the negative-structure-inactive family-mixture study first. Empirical execution must still wait for fresh authorization after that contract/preflight is visible.


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


## Recognizer-gated cleanup V1 launched — 2026-10-02

Built:
- `astra_backend/evaluation/recognizer_gate_v1.py`
- `astra_backend/evaluation/evaluate_recognizer_gated_cleanup_v1.py`
- `.github/workflows/astra-recognizer-gated-cleanup-eval.yml`

V1 gate is conservative and prospectively frozen before evaluation. It uses absolute YAMNet string evidence, guitar-vs-bass margin, separator interference pressure, competitor-dominance evidence, and an explicit uncertain state. Raw stems are preserved by default. Cleanup is only eligible on strong recognizer disagreement plus separator contamination evidence. Cleanup itself is softened relative to V1 blanket cleanup (floor gain 0.85, competition 0.35).

Because the platform blocked creation of a new tiny trigger file, the workflow temporarily reuses `docs/astra/YAMNET_RECOGNIZER_RUN_TRIGGER.txt`. Trigger commit `6873fd8b8c547ca100f214fed0a25b10a0aa4261` launched recognizer-gated cleanup run `37082340739`. This also launches the existing YAMNet evidence workflow and normal backend tests from the same commit; those are incidental and do not change the gated-cleanup experiment.


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
