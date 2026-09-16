# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — candidate-population breadth result is frozen; a new gate-free competition-only diagnostic PRE and module/test pair are prospectively frozen but have not executed. Temporal/support attempt-1 measurement access remains blocked/no-decision.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic diagnostics are never authoritative real/model correctness validation.
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

Consumed real-run authorizations remain consumed. There is currently **no authorization** for another EGFxSet run, Basic Pitch rerun, V6/V7 real correctness run, modified-real-rule execution, AG-PT/rejected-holdout access, physical capture/calibration, protected-song execution or any real/model successor evaluation.

## FROZEN STATUS LEDGER

### V3 physical-template synthetic line

- Iteration 1: `FAIL_SYNTHETIC_ALIAS_PROTECTION`.
- Iteration 2: `FAIL_SYNTHETIC_SPURIOUS_SUPPORT`.
- Iteration 3: permanently `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`.
- Iteration-3 PRE commit `26ac58fe54c179744ef036a9dc4f4a7d69598038`; result commit `e97ab67c9c2794f4a50c5170102d1380484f5fb1`.
- Frozen 34 fixtures ×3, deterministic, mismatch `0`.
- Frozen `MIN_CANDIDATE_EVIDENCE_FRACTION = 0.10`; NNLS necessity minimum `0.01`.

### V7 successor mechanical integration

- PRE `638b045aea5a9fc66cee30c78772e792b38b8c79`; module `a2d312aa1dfd86be617fba35724de8aa1fba40d6`; result `9f6345e971f36a0def367a70564ba9b86c948e23`.
- Frozen result `PASS_SYNTHETIC_MECHANICAL_INTEGRATION`, 34 fixtures ×3, deterministic, mismatch `0`.

### V7 first real-evaluation attempt

- PRE `b7f5f681d6ef39669bcec44ba8116a4ae177e680`.
- Run `35051186125`, attempt 1.
- Result remains `FAIL_V7_BOUNDARY_SYNTHETIC_PREREQUISITE / REAL_EVALUATION_NOT_EXECUTED`.
- Prior Basic Pitch artifact, EGFxSet media and real qualifier were skipped; authorization is consumed.

### Representation bridge / dual-view / semantic-delta line

- Bridge iteration 1 run `35051843902`: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`, 18/23 matched, untouched V3 PASS.
- Bridge iteration 2 run `35052132987`: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`, 20/23 matched, untouched V3 PASS.
- Persistent bridge-V2 cases: `selected64_enters_over_existing60`, `simultaneous_dyad_sel60`, `reattack_m64`.
- Dual-view PRE `6402e3a6f77268ccc090232b340ac3719577ba76`, run `35052606540`: `COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`.
- Frozen-V6 semantic-delta PRE `bbc93f68b995598187ec140accf713a604650c60`, run `35052971870`, result commit `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`: `COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`.
- Frozen semantic separation: support/local-background eligibility, raw observed fit evidence, candidate competition population, and reattack temporal/support representation are distinct roles.
- Historical V6 fundamental-ratio threshold `0.20` remains historical/reference-only.

### V7 reattack temporal/support diagnostic — BLOCKED MEASUREMENT ACCESS

- PRE `77db77632d68f02d52f5d26df87f6fe562cba9e3`.
- Module blob `3877ddc9fabd92e9ba1d2db891c9e34a6a6c9e0f`; test blob `95ffe764bacb449143c0b5d4f06638a46390f8bf`.
- Workflow/head `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`.
- Run `35053450282`, job `104658560061`, attempt 1: `completed/success`.
- Result file `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md`, commit `86549fcf3f15898aa551064b522ce42ca32b1b86`.
- Frozen status `COMPLETE_MECHANICAL_EXECUTION / BLOCKED_STORED_LOG_ACCESS / NO_MEASUREMENT_DECISION`.
- Job-log endpoint now returns `404`; run-level console text is unavailable; there were zero artifacts; public UI requires sign-in.
- **Do not rerun or locally reproduce this diagnostic.** No exact reattack support-loss stage is frozen and no temporal/support repair is authorized from this blocked result.

### V7 candidate-population / competition diagnostic — COMPLETE

- PRE `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_PRE.md`, commit `ea17df201a58d0c6ba841350f2646826da6fe945`, blob `0e966271403ee9eaaea6b52f5e3739b77d02c5c6`.
- Module commit `b7abd17a37680a720b0e0fa6c7831fa0e0c94402`, blob `194507cbd23b4f67be20c2d7a6a28b454bb146ca`.
- Test/pair head `da4a3624d66c4138390969cb986317b0cd791c05`, blob `080040b9269fa80b14508f5c654d4b5054afab3d`.
- PRE-to-pair diff exactly two allowed Python files.
- Workflow/head `3ae25dbb0cb4cb0e2e65cbc2a8aa6184c0d9026b`, blob `b4696d10d347c21b7414bddfc228129a32a89bff`.
- Run `35057264267`, job `104669939122`, attempt 1: success.
- Artifact `10430643432`, digest `sha256:199af452612c0a224b6bb2b214148026e2501e378d2bed1f510d767380722c9a`.
- Result file `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`, commit `4750332a347b03795d089690e8f7c4249319cd71`.
- Result label `COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`.
- 23 fixtures ×3 deterministic; onset available 19; selected in raw/support intersection 14; full broad-vs-restricted attribution available 13; frozen-V6 reproduction passed at `1e-12`; untouched V3 34×3 PASS.

Key frozen measurements:

- All 13 numerically comparable fixtures show higher selected necessity under the narrow raw/support intersection than under broad raw-valid competition.
- `simultaneous_dyad_sel60`: 49-candidate necessity `0.0041216775902363015`; seven-candidate necessity `0.17554666733325255`; raw-only MIDI59 is strongest prospectively measured add-one competitor but does not alone reproduce the full broad result.
- Same-audio `simultaneous_dyad_sel64`: 49-candidate necessity `0.05178270149633484`; seven-candidate necessity `0.16256312708394405`.
- `selected64_enters_over_existing60`: 40-candidate necessity `0.019916868330096094`; five-candidate raw/support-intersection necessity `0.30343914432503055`; MIDI63 is strongest prospectively measured add-one/leave-one-out contributor but does not alone reproduce the broad result.
- Attribution varies by fixture and can be non-monotonic. Do not convert MIDI59, MIDI63 or any other observed contributor into a rule.
- `reattack_m64` remains upstream/support-ineligible and outside the restricted comparison.
- Historical V6 raw-valid breadth is informative but its `0.20` ratio gate is **not adopted**.

### V7 gate-free competition dictionary diagnostic — PRE + PAIR FROZEN, NOT EXECUTED

This line is prospectively motivated by the candidate-breadth result and does not depend on the inaccessible temporal payload.

PRE:

- file: `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_PRE.md`;
- commit: `195d219c0d9a031f2d99b1822176377bac9fbb8c`.

Frozen pair:

- module: `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`;
- module commit: `3eb799075c9cc8720ed9d827f5b7aecff126d42e`;
- module blob: `08eb9e945bf2cdf33e640cf7b3349ae075002846`;
- test: `scripts/songsterr-fresh/test_v7_gate_free_competition_diagnostics_v1.py`;
- pair head/test commit: `539c4b917a8d2b5bb97b5e1a929a8e506482a191`;
- test blob: `f92df723af79a37f12996e896b881593d70d7bc6`.

PRE-to-pair compare is exactly those two added Python files.

Prospectively frozen semantics:

- untouched raw V6 onset innovation;
- exact frozen V6 harmonic-template geometry for historically valid candidates;
- one competition-only template for every structurally constructible playable MIDI 40..88;
- the historical V6 fundamental-to-max-harmonic ratio `0.20` is recorded only as metadata and **does not gate competition admission**;
- all structurally constructible candidates enter the gate-free competition dictionary;
- NNLS selected necessity is diagnostic only and never changes selected-note eligibility;
- every newly admitted candidate is prospectively enumerated with add-one and gate-free leave-one-out attribution when available;
- selected historical-gate failures such as `already_sounding_m64` may be measured but cannot be promoted or accepted from this diagnostic;
- no classifier, threshold, support gate, per-MIDI rule, candidate search, real/model inference or reattack repair is defined.

Immediate next step for this line:

1. add only `.github/workflows/songsterr-v7-gate-free-competition-diagnostic-one-shot.yml` under the PRE write boundary;
2. self-scope it to a push of its own YAML path;
3. pin/verify PRE, frozen dependencies, module blob `08eb9e...` and test blob `f92df7...` before execution;
4. compile/static-guard the packet;
5. execute diagnostic and untouched V3 regression exactly once;
6. persist `gate-free-competition-diagnostic.json` and `v3-regression.txt` as artifact `songsterr-fresh-v7-gate-free-competition-diagnostic` with `actions/upload-artifact@v4`, `if: always()`;
7. freeze attempt 1 from that artifact before any successor composition PRE.

No gate-free run has occurred yet.

## CURRENT TECHNICAL CONCLUSION

The seam has four empirically separated roles/problems:

1. support/local-background eligibility;
2. raw observed NNLS fit evidence;
3. candidate/template competition breadth;
4. reattack temporal/support representation.

Candidate breadth must preserve broad alternative explanations, but the successor population must not simply inherit the historical V6 `0.20` candidate-validity gate. The gate-free diagnostic above is the current prospective test of a threshold-free competition-only population.

Do not convert frozen findings into a V6-threshold transplant, MIDI exception, fixture branch, threshold search, candidate-subset search, monotonic-candidate assumption or temporal fallback.

## FRESH CHAT RESUME POINT

1. Read this checkpoint first from `songsterr-fresh-pipeline-v1`; reconcile any newer branch commits.
2. Treat candidate-breadth result commit `4750332a347b03795d089690e8f7c4249319cd71` and artifact `10430643432` as frozen; do not rerun run `35057264267`.
3. Keep temporal/support run `35053450282` blocked; do not rerun/reconstruct it.
4. For the current gate-free line, confirm PRE `195d219c0d9a031f2d99b1822176377bac9fbb8c`, pair head `539c4b917a8d2b5bb97b5e1a929a8e506482a191`, module blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`, and test blob `f92df723af79a37f12996e896b881593d70d7bc6`.
5. The next permitted executable addition is only the prospectively allowed self-scoped gate-free one-shot workflow with artifact preservation.
6. Freeze its attempt-1 artifact result before opening any composition-rule PRE.
7. Any future real/media/model V7 evaluation requires a new real-evaluation PRE plus fresh explicit user authorization.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not rerun temporal/support run `35053450282`.
- Do not rerun candidate-breadth run `35057264267`.
- Do not execute the gate-free diagnostic except through its prospectively allowed first one-shot workflow.
- Do not tune from frozen post-result attribution.
- Do not change/adopt V3 thresholds or historical V6 thresholds.
- Do not add per-MIDI exceptions, fixture branches, confidence promotion, learned parameters, candidate subset searches or real-corpus rules.
- Do not edit frozen V6/V3 implementations or frozen result checkpoints.
- Do not switch Production or `main`.
- Do not use real media/model access without a new prospective real-evaluation PRE and explicit user authorization.

Archived V143/Gomyway remains untouched.
