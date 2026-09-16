# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — fresh-chat handoff after the first V7 reattack temporal/support diagnostic execution.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains deterministic/model-free/process-free/network-free and read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.
- Never rewrite, soften or reinterpret any frozen historical FAIL/C/PASS result.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Consumed real-run authorizations:

- `Please try the run again` -> hardened-V1 EGFxSet run `34938917218`, attempt 1.
- `Lets take what was learned, repair and run again` -> boundary-aware V2 repair plus EGFxSet V2 run `34940292514`, attempt 1.
- `I authorize please continue` -> V7 real-evaluation attempt run `35051186125`, attempt 1; synthetic prerequisite failed and prior Basic Pitch artifact, EGFxSet media and V7 real qualifier were skipped. That authorization is consumed; there is no retry under it.

There is currently **no authorization** for another EGFxSet run, Basic Pitch rerun, V6/V7 real correctness run, threshold variation, modified-real-rule execution, AG-PT-set structural re-audit, rejected-candidate payload access, physical capture/calibration, protected-song execution or any real/model successor evaluation.

## FROZEN STATUS LEDGER

### V3 physical-template synthetic line

- Iteration 1 remains `FAIL_SYNTHETIC_ALIAS_PROTECTION`.
- Iteration 2 remains `FAIL_SYNTHETIC_SPURIOUS_SUPPORT`.
- Iteration 3 remains permanently `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`.
- Iteration-3 PRE commit: `26ac58fe54c179744ef036a9dc4f4a7d69598038`.
- Iteration-3 result commit: `e97ab67c9c2794f4a50c5170102d1380484f5fb1`.
- Frozen 34 fixtures ×3 repetitions, deterministic, mismatch count `0`.
- Frozen `MIN_CANDIDATE_EVIDENCE_FRACTION = 0.10`; NNLS necessity minimum remains `0.01`.
- Frozen V3 geometry/threshold semantics remain read-only.

### V7 successor mechanical integration

- PRE commit: `638b045aea5a9fc66cee30c78772e792b38b8c79`.
- V7 module commit: `a2d312aa1dfd86be617fba35724de8aa1fba40d6`.
- Result commit: `9f6345e971f36a0def367a70564ba9b86c948e23`.
- Frozen result: `PASS_SYNTHETIC_MECHANICAL_INTEGRATION`.
- 34 fixtures, 3 repetitions, deterministic, mismatch count `0`.
- This is mechanical/synthetic only; it is not real/model correctness evidence.

### V7 first real-evaluation attempt

- PRE commit: `b7f5f681d6ef39669bcec44ba8116a4ae177e680`.
- Run `35051186125`, attempt 1.
- Frozen result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_RESULT.md`.
- Result remains `FAIL_V7_BOUNDARY_SYNTHETIC_PREREQUISITE / REAL_EVALUATION_NOT_EXECUTED`.
- Prior Basic Pitch artifact fetch, EGFxSet media fetch and V7 real qualifier were all skipped.
- No EGFxSet conclusion may be inferred and there is no same-authorization retry.

### Representation bridge iteration 1

- PRE commit: `6502f00670efe9987ff5a76707d9cf32476ac4fe`.
- Run `35051843902`, attempt 1.
- 23 frozen V6 audio fixtures ×3, deterministic.
- 18/23 matched; untouched V3 direct-spectrum regression 34/34 PASS.
- Frozen result: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`.
- No iteration-1 rerun or repair.

### Representation bridge iteration 2

- PRE commit: `7cc8fc88a9b3d12596dfdce553bb717bc77fb05b`.
- Run `35052132987`, attempt 1.
- 23 fixtures ×3, deterministic.
- 20/23 matched; untouched V3 suite 34/34 PASS.
- Frozen result: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`.
- Persistent cases:
  - `selected64_enters_over_existing60`: expected PASS, support-view `FAIL_NECESSITY`.
  - `simultaneous_dyad_sel60`: expected reject, support-view PASS.
  - `reattack_m64`: expected PASS, `SELECTED_TEMPLATE_INELIGIBLE`.
- No iteration-2 rerun or repair.

### Dual-view diagnostic

- PRE commit: `6402e3a6f77268ccc090232b340ac3719577ba76`.
- Run `35052606540`, attempt 1.
- Frozen result: `COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`.
- Key separation: support/local-background eligibility and raw observed NNLS fit evidence are distinct roles.
- `selected64_enters_over_existing60` shows weak support necessity but strong raw observed-fit necessity.
- `simultaneous_dyad_sel60` remains a false positive even with raw observed fit against the same narrow support-derived candidate set.
- `reattack_m64` fails upstream because no eligible selected support template exists.
- No classifier or new threshold was defined.

### Frozen-V6 semantic-delta diagnostic

- PRE commit: `bbc93f68b995598187ec140accf713a604650c60`.
- Module commit: `8daaca217ca38f51a3b6e6dbad6b9c2c7a1ac348`.
- Run `35052971870`, attempt 1.
- Result commit: `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`.
- Frozen result: `COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`.
- Candidate-competition breadth explains the simultaneous-dyad MIDI60 false positive.
- Reattack MIDI64 remains a separate support/temporal representation defect upstream of candidate competition.
- Historical V6 fundamental-ratio threshold `0.20` remains historical/reference-only and is not adopted as a successor rule.

## CURRENT TECHNICAL CONCLUSION

The representation seam is separated into distinct roles:

1. **support / local-background eligibility** — benefits from leakage-cleaned representation;
2. **observed NNLS fit evidence** — should retain richer raw V6 innovation rather than reuse sparse support evidence;
3. **candidate/template competition population** — must be broad enough to preserve competing explanations;
4. **reattack temporal/support representation** — can fail before any fit or competition rule is reached.

Do not combine these observations into a post-result threshold, V6-0.20 transplant, MIDI exception, fixture branch, peak-width search or one-off fallback.

## REATTACK TEMPORAL/SUPPORT DIAGNOSTIC — FIRST RUN COMPLETE, RESULT NOT YET FROZEN

This is the newest authoritative working boundary for a fresh chat.

Prospective PRE:

- file: `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_PRE.md`
- commit: `77db77632d68f02d52f5d26df87f6fe562cba9e3`.

Committed diagnostic pair:

- module: `scripts/songsterr-fresh/v7_reattack_temporal_support_diagnostics_v1.py`
- module commit: `a7a7acf4c51c6bc6b6609efbcc2dde3b34bcc850`
- module blob: `3877ddc9fabd92e9ba1d2db891c9e34a6a6c9e0f`
- test: `scripts/songsterr-fresh/test_v7_reattack_temporal_support_diagnostics_v1.py`
- test commit / pair head: `d80a162c22b00cc2ed32ec518c3fa7c24c8534e6`
- test blob: `95ffe764bacb449143c0b5d4f06638a46390f8bf`.

One-shot runner:

- workflow: `.github/workflows/songsterr-v7-reattack-temporal-support-diagnostic-one-shot.yml`
- workflow/head commit: `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`
- run: `35053450282`
- job: `104658560061`
- attempt: `1`
- status: `completed`
- conclusion: `success`.

The job's dependency/blob verification completed successfully and the step `Run frozen temporal-support diagnostic and untouched V3 regression exactly once` completed successfully.

**Do not rerun this diagnostic.** Attempt 1 is the only authoritative execution. Workflow success means the frozen measurement/test invariants completed; it does not by itself define a classifier or a repair.

No result checkpoint for this temporal/support diagnostic has been frozen yet. The stored attempt-1 log must be treated as the only source for the measured trace values.

## FRESH-CHAT NEXT STEPS — DO THESE IN ORDER

1. **Re-fetch this branch and this checkpoint first.** Confirm the live branch still descends from `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`; if it has advanced, reconcile the newer commits before writing anything.
2. **Do not rerun run `35053450282`.** Read only the stored attempt-1 job log for job `104658560061` and extract the prospectively named comparison rows from the PRE/test. In particular compare the clean onset, already-sounding/continuing note, `reattack_m64`, transient-only, weak-owner and context-edge controls.
3. **Identify the exact reattack support-loss mechanism from those stored rows only.** Distinguish whether the genuine reattack is lost at raw harmonic innovation, retained-center placement/suppression, bridged peak survival, local-background contamination, weighted support coverage, or another already-instrumented measurement. Do not invent a repair while extracting the result.
4. **Freeze a result checkpoint before any new executable repair work.** Create `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md` containing the exact run/head/blob identities, first-run-only policy, measured comparison rows, deterministic/mechanical status, untouched V3 regression status, and a neutral measurement-only conclusion. No classifier, threshold, production rule or real-data implication may be claimed.
5. **Update this current-state checkpoint immediately after freezing that result.** Record the result commit and the exact measured reattack mechanism.
6. **Only after the temporal result is frozen, open a new prospective PRE for the next experiment.** Keep reattack support/temporal repair separate from candidate-population/competition composition unless the frozen measurement itself prospectively justifies a shared mechanism.
7. The other still-open synthetic dimension is **candidate-population/competition composition** for `simultaneous_dyad_sel60`. A later prospective PRE may evaluate broader candidate competition with raw observed fit while preserving frozen V3 support/owner/evidence protections. It must not simply transplant the historical V6 `0.20` gate.
8. **Only after both unresolved synthetic dimensions are prospectively resolved** should a complete successor composition rule be frozen and tested against all 23 frozen V6 audio expectations plus the untouched 34-fixture V3 regression.
9. **Any future real/media/model V7 evaluation requires a new real-evaluation PRE plus fresh explicit user authorization.** The prior authorization is consumed. Do not fetch EGFxSet media, run Basic Pitch, run a V6/V7 real qualifier, or infer real correctness from synthetic diagnostics without that authorization.

## FRESH CHAT RESUME POINT — IMMEDIATE TASK

The previous chat stopped at the measurement-extraction gate. No detector code was changed, no temporal diagnostic rerun was performed, and no temporal result checkpoint was created.

A new chat should begin with this exact sequence:

1. Read this checkpoint and `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_PRE.md` from branch `songsterr-fresh-pipeline-v1`.
2. Fetch the **stored** GitHub Actions log for run `35053450282`, job `104658560061`, attempt 1. Do not dispatch or rerun the workflow.
3. Use the PRE and the frozen diagnostic test/module to identify the exact emitted markers/row names, then extract all prospectively declared comparison rows and the untouched V3 regression result from the stored log. The diagnostic covers 23 frozen fixtures with three deterministic repetitions; the V3 regression remains 34 fixtures ×3.
4. Record the factual values for all named comparison classes, including `reattack_m64`, and locate the first instrumented stage where its temporal/support evidence diverges from the valid-onset controls. Do not infer values that are absent from the stored log and do not invent a threshold.
5. Compare the measurements only against criteria prospectively frozen in the PRE. If the PRE does not authorize a numeric decision boundary, freeze a neutral/no-decision measurement result rather than creating one after seeing the data.
6. Before touching detector implementation, create and commit `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md`; then update this current-state checkpoint with the result commit, exact support-loss stage, regression status and authorized next experiment.
7. Only if that frozen result prospectively justifies a narrow next experiment should a new PRE be written. No detector change comes first.

Current branch head before this handoff update was `1ed5c507dad1b3311e9da6d2625b5c6a9fa74f47`, whose parent is the one-shot workflow/head commit `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`.

## DO NOT DO IN A FRESH CHAT

- Do not resume V143/Gomyway.
- Do not rerun temporal/support run `35053450282` or any frozen bridge/diagnostic run.
- Do not tune from frozen post-result mismatches.
- Do not lower V3 thresholds or historical V6 thresholds.
- Do not add per-MIDI exceptions, EGFxSet-specific rules, fixture branches, confidence-based promotion, learned parameters, or post-result threshold searches.
- Do not edit frozen V6/V3 implementations or closed checkpoint results.
- Do not switch Production or `main`.
- Do not use real media/model access without a new prospective real-evaluation PRE and explicit user authorization.

Archived V143/Gomyway remains untouched.
