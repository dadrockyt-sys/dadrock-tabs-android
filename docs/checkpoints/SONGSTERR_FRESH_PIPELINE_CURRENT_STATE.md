# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — candidate-population / competition diagnostic attempt 1 is frozen from a preserved Actions artifact; temporal/support attempt-1 measurement access remains blocked/no-decision.

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
  - `selected64_enters_over_existing60`: expected PASS, support-view `FAIL_NECESSITY`;
  - `simultaneous_dyad_sel60`: expected reject, support-view PASS;
  - `reattack_m64`: expected PASS, `SELECTED_TEMPLATE_INELIGIBLE`.
- No iteration-2 rerun or repair.

### Dual-view diagnostic

- PRE commit: `6402e3a6f77268ccc090232b340ac3719577ba76`.
- Run `35052606540`, attempt 1.
- Frozen result: `COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`.
- Support/local-background eligibility and raw observed NNLS fit evidence are distinct roles.
- `selected64_enters_over_existing60` shows weak support necessity but strong raw observed-fit necessity.
- `simultaneous_dyad_sel60` remains a false positive with raw observed fit against the same narrow support-derived candidate set.
- `reattack_m64` fails upstream because no eligible selected support template exists.
- No classifier or new threshold was defined.

### Frozen-V6 semantic-delta diagnostic

- PRE commit: `bbc93f68b995598187ec140accf713a604650c60`.
- Module commit: `8daaca217ca38f51a3b6e6dbad6b9c2c7a1ac348`.
- Run `35052971870`, attempt 1.
- Result commit: `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`.
- Frozen result: `COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`.
- Candidate-competition breadth is the material semantic delta for the simultaneous-dyad MIDI60 false positive.
- Reattack MIDI64 is a separate support/temporal representation defect upstream of competition.
- Historical V6 fundamental-ratio threshold `0.20` remains historical/reference-only and is not adopted as a successor rule.

### V7 reattack temporal/support diagnostic — mechanically complete, stored measurement unavailable

- PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_PRE.md`.
- PRE commit: `77db77632d68f02d52f5d26df87f6fe562cba9e3`.
- Module blob: `3877ddc9fabd92e9ba1d2db891c9e34a6a6c9e0f`.
- Test blob: `95ffe764bacb449143c0b5d4f06638a46390f8bf`.
- Workflow/head: `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`.
- Run `35053450282`, job `104658560061`, attempt 1: `completed/success`.
- Result: `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md`.
- Result commit: `86549fcf3f15898aa551064b522ce42ca32b1b86`.
- Frozen status: `COMPLETE_MECHANICAL_EXECUTION / BLOCKED_STORED_LOG_ACCESS / NO_MEASUREMENT_DECISION`.
- Connected GitHub run/job metadata confirms success, but the job-log endpoint returns `404`, run-level log text is unavailable, there were zero artifacts, and the public job page requires sign-in to view the console payload.
- **Do not rerun or locally reproduce this diagnostic to replace attempt 1.**
- No exact reattack support-loss stage is frozen; no temporal/support repair PRE is authorized from this blocked result.

### V7 candidate-population / competition diagnostic — COMPLETE

Prospective PRE and pair:

- PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_PRE.md`.
- PRE commit: `ea17df201a58d0c6ba841350f2646826da6fe945`.
- PRE blob: `0e966271403ee9eaaea6b52f5e3739b77d02c5c6`.
- module: `scripts/songsterr-fresh/v7_candidate_competition_diagnostics_v1.py`.
- module commit: `b7abd17a37680a720b0e0fa6c7831fa0e0c94402`.
- module blob: `194507cbd23b4f67be20c2d7a6a28b454bb146ca`.
- test: `scripts/songsterr-fresh/test_v7_candidate_competition_diagnostics_v1.py`.
- pair head / test commit: `da4a3624d66c4138390969cb986317b0cd791c05`.
- test blob: `080040b9269fa80b14508f5c654d4b5054afab3d`.
- PRE-to-pair diff was exactly the two prospectively allowed Python files.

One-shot execution:

- workflow: `.github/workflows/songsterr-v7-candidate-competition-diagnostic-one-shot.yml`.
- workflow/head commit: `3ae25dbb0cb4cb0e2e65cbc2a8aa6184c0d9026b`.
- workflow blob: `b4696d10d347c21b7414bddfc228129a32a89bff`.
- run: `35057264267`.
- job: `104669939122`.
- attempt: `1`.
- conclusion: `success`.
- artifact: `songsterr-fresh-v7-candidate-competition-diagnostic`.
- artifact id: `10430643432`.
- artifact digest: `sha256:199af452612c0a224b6bb2b214148026e2501e378d2bed1f510d767380722c9a`.
- no rerun occurred.

Frozen result:

- file: `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`.
- result commit: `4750332a347b03795d089690e8f7c4249319cd71`.
- result label: `COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`.
- 23 fixtures ×3, deterministic.
- onset available: `19`.
- selected MIDI in raw/support intersection: `14`.
- complete broad-vs-restricted attribution available: `13`.
- frozen-V6 full-fit reproduction tolerance: `1e-12`, passed.
- untouched V3 iteration-3 regression: 34 fixtures ×3, deterministic, mismatch `0`, PASS.
- no real/model/network execution; `finalDecisionDefined:false`; `mayAdvanceDelivery:false`.

Key frozen measurements:

1. Across **all 13** numerically comparable fixtures, restricting raw-template competition to the raw/support-valid MIDI intersection increased selected-MIDI necessity relative to the broad raw-valid population.
2. `simultaneous_dyad_sel60`:
   - raw-full candidates `49`, necessity `0.0041216775902363015`;
   - raw/support intersection candidates `7`, necessity `0.17554666733325255`;
   - restricted-minus-full delta `0.17142498974301626`;
   - raw-only MIDI59 is the strongest prospectively measured add-one competitor: adding it alone changes necessity to `0.028050296057115214` (`-0.14749637127613735` from restricted);
   - removing MIDI59 from the full population changes necessity to `0.01702814282853363` (`+0.012906465238297329` from full).
3. Same-audio `simultaneous_dyad_sel64`:
   - full necessity `0.05178270149633484`;
   - restricted necessity `0.16256312708394405`;
   - broad competition suppresses both selected notes, but the full broad fit keeps MIDI60 and MIDI64 materially separated in the same audio.
4. `selected64_enters_over_existing60`:
   - full candidates `40`, necessity `0.019916868330096094`;
   - raw/support intersection candidates `5`, necessity `0.30343914432503055`;
   - MIDI63 is the strongest prospectively measured add-one / leave-one-out contributor, but a single candidate does not reproduce the full broad result.
5. Attribution is interacting/non-monotonic across fixtures. Example: for dyad selected MIDI64, removing raw-only MIDI57 from the full fit lowers rather than raises necessity. Do not turn a single omitted MIDI into a generic candidate rule.
6. `reattack_m64` remains outside this comparison because selected support eligibility fails upstream; raw-full necessity remains the previously frozen `0.14453142873815786`, but there is no restricted competition fit.
7. Historical V6 raw-valid candidate breadth is informative evidence only. It relies on historical V6 raw-template validity, including the `0.20` fundamental-ratio rule, which remains **reference-only and not adopted**.

## CURRENT TECHNICAL CONCLUSION

The seam now has four empirically separated roles/problems:

1. **support / local-background eligibility** — leakage-cleaned support evidence is useful for physical support but can reject reattacks upstream;
2. **observed NNLS fit evidence** — richer raw innovation should remain distinct from sparse support evidence;
3. **candidate/template competition population** — narrow support-derived competition systematically inflates selected necessity in the frozen comparable population; broad alternative explanations materially change NNLS necessity;
4. **reattack temporal/support representation** — still unresolved because its first-run measurement payload is inaccessible, and it cannot be repaired from candidate-competition evidence.

The candidate diagnostic supports preserving **broad competing explanations** as a design requirement. It does **not** define how a successor should construct that broad population without importing historical V6 eligibility semantics.

Do not convert the frozen result into:

- a V6 `0.20` transplant;
- a MIDI59, MIDI63 or other per-MIDI exception;
- a fixture-specific rule;
- a threshold search;
- a candidate-subset search;
- a rule that every extra candidate monotonically lowers necessity;
- a temporal/reattack fallback.

## NEXT PROSPECTIVE SYNTHETIC QUESTION

If continuing candidate-population research, the next permissible engineering step is a **new prospective PRE before any executable implementation** for a competition-only candidate-construction diagnostic.

That PRE must answer this narrower question:

> Can a broad competition dictionary expose alternative harmonic explanations without using support-validity as the competition gate and without automatically adopting the historical V6 `0.20` fundamental-ratio validity rule?

A safe next diagnostic should remain measurement-only and should prospectively define candidate construction before output is observed. It must use all 23 frozen V6 fixtures generically, preserve the untouched V3 34-fixture regression, persist attempt-1 evidence as an artifact, and prohibit post-result MIDI/candidate search.

Do **not** define a final successor classifier before that construction problem is prospectively resolved. The temporal/support line remains independently blocked.

## FRESH CHAT RESUME POINT

A new chat should begin in this order:

1. Read this checkpoint first from `songsterr-fresh-pipeline-v1` and reconcile any newer branch commits.
2. Read `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md` and treat commit `4750332a347b03795d089690e8f7c4249319cd71` as frozen measurement authority for candidate breadth.
3. Do not rerun candidate run `35057264267`; its attempt-1 artifact `10430643432` is authoritative.
4. Keep temporal/support run `35053450282` blocked; do not rerun/reconstruct it.
5. If continuing candidate research, write a new prospective PRE for competition-only candidate construction **before** adding executable code. Do not adopt V6 `0.20`, a measured MIDI exception, or a post-result candidate subset.
6. Freeze any new first-run result from a persisted artifact before opening a composition-rule PRE.
7. Any future real/media/model V7 evaluation requires a new real-evaluation PRE plus fresh explicit user authorization.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not rerun temporal/support run `35053450282`.
- Do not rerun candidate-competition run `35057264267`.
- Do not tune from frozen post-result mismatches or attribution rows.
- Do not lower/change V3 thresholds or transplant historical V6 thresholds.
- Do not add per-MIDI exceptions, EGFxSet-specific rules, fixture branches, confidence-based promotion, learned parameters, or post-result candidate searches.
- Do not edit frozen V6/V3 implementations or frozen result checkpoints.
- Do not switch Production or `main`.
- Do not use real media/model access without a new prospective real-evaluation PRE and explicit user authorization.

Archived V143/Gomyway remains untouched.
