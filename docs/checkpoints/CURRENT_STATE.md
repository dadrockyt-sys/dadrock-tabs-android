# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **LOCALIZATION RESULTS FROZEN — CANDIDATE TRANSFER FAILURE OBSERVED; P2 CAUSE UNRESOLVED; PREPARE MODEL-FREE INTEGRITY AUDIT OFFLINE; P3 SEALED**

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
