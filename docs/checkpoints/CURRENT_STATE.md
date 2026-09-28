# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **V2 STAGE A TEST-CONTRACT CORRECTION REVIEW FROZEN — SCIENTIFIC CONFIG UNCHANGED; NEXT: BUILD SEPARATELY VERSIONED CORRECTED STAGE-A PACKAGE OFFLINE ONLY, DO NOT RUN; STAGE B/MODELS BLOCKED; P1/P2 CLOSED; P3 SEALED**

Latest supervisory instructions are in **Supervisory review after S12** at the end of this file. Earlier execution/resume sections are historical where superseded.

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
