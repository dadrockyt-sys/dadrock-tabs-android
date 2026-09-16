# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — candidate-breadth and gate-free all-playable competition diagnostics are frozen. The fixed-feature competition PRE/module/test pair is now frozen and has not executed; the next permitted write is its self-scoped one-shot workflow. Temporal/support attempt-1 measurement access remains blocked/no-decision.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## LATEST CONTINUATION OVERRIDE — AUTHORITATIVE WHERE OLDER TEXT CONFLICTS

Live branch reconciliation at continuation start found head `949523ca753c2f7f0a5b87af195770210143d8cb`, directly descending from fixed-feature PRE `89f7f0d7b24b30fe2296fd9f76bb44ab50751e0c`, with no intervening/concurrent work.

### Fixed-feature competition diagnostic — PRE + PAIR FROZEN, NOT EXECUTED

Prospective PRE:

- file: `docs/checkpoints/SONGSTERR_FRESH_V7_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_PRE.md`;
- PRE commit: `89f7f0d7b24b30fe2296fd9f76bb44ab50751e0c`;
- PRE blob: `29e0b297d7b780c8cabc121d6c561cdfa806471f`.

Frozen diagnostic pair:

- module: `scripts/songsterr-fresh/v7_fixed_feature_competition_diagnostics_v1.py`;
- module commit: `949523ca753c2f7f0a5b87af195770210143d8cb`;
- module blob: `d69382ae14b1fb8f7f570919240dce372db1e424`;
- test: `scripts/songsterr-fresh/test_v7_fixed_feature_competition_diagnostics_v1.py`;
- test/pair head: `ab8b0d2501aab46a313e1dfb1adfad6a3405bd5c`;
- test blob: `d658a9f7baee2f13df35956daa7a3c77d24e9eec`.

PRE-to-pair compare (`89f7f0d7...ab8b0d25`) contains exactly:

- the new fixed-feature diagnostic module;
- the new fixed-feature test gate;
- state-only edits to this checkpoint.

No other path changed.

The prospectively frozen decomposition is measurement-only:

1. all gate-free competition templates for playable MIDI `40..88` define one fixed feature-bin universe;
2. untouched raw V6 innovation is sampled once on those fixed rows;
3. three column populations are fitted against the identical observation rows: gate-free all-playable, historical raw-valid, and raw/support intersection;
4. variable-feature fits are carried separately as reference measurements;
5. descriptive deltas separate column-breadth effects from feature-universe effects;
6. no classifier, threshold decision, candidate search, selected-note eligibility change, reattack repair or production rule exists.

The frozen test gate additionally enforces:

- exactly 23 fixtures ×3 deterministic repetitions;
- reference expected labels unused for computation;
- all onset-available rows mechanically reconstruct all 49 gate-free candidate columns;
- sorted/unique/in-range candidate sets and fixed feature bins;
- identical fixed feature bins/energy across all compared fixed-feature fits;
- gate-free/V6 historical-valid template geometry equivalence to `1e-12`;
- gate-free fixed fit reproduces the corresponding all-gate-free variable-feature fit to `1e-12`;
- historical variable-feature fit reproduces frozen V6 fit where mechanically available;
- no verdict fields or threshold adoption.

**No fixed-feature diagnostic execution has occurred yet.**

Next permitted action:

1. create only `.github/workflows/songsterr-v7-fixed-feature-competition-diagnostic-one-shot.yml` under the PRE write boundary;
2. self-scope it to its own YAML path;
3. pin/verify PRE, frozen dependencies, module and test blobs;
4. compile/static-guard the packet;
5. execute the diagnostic and untouched V3 iteration-3 regression exactly once;
6. persist `fixed-feature-competition-diagnostic.json` and `v3-regression.txt` as artifact `songsterr-fresh-v7-fixed-feature-competition-diagnostic` using `actions/upload-artifact@v4` and `if: always()`;
7. freeze attempt 1 from that artifact before any successor composition PRE.

Do not rerun any prior one-shot. Archived V143/Gomyway remains untouched.

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic diagnostics are never authoritative real/model correctness validation.
- Never rewrite, soften or reinterpret frozen historical FAIL/C/PASS results.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

All prior real-run authorizations remain consumed. There is no authorization for another EGFxSet run, Basic Pitch rerun, real V6/V7 qualifier, modified-real-rule execution, AG-PT/rejected holdout access, physical capture/calibration, protected-song execution or other real/model successor evaluation.

## FROZEN STATUS LEDGER

### V3 / V7 historical synthetic state

- V3 iteration 1: `FAIL_SYNTHETIC_ALIAS_PROTECTION`.
- V3 iteration 2: `FAIL_SYNTHETIC_SPURIOUS_SUPPORT`.
- V3 iteration 3: permanent `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`; PRE `26ac58fe54c179744ef036a9dc4f4a7d69598038`, result `e97ab67c9c2794f4a50c5170102d1380484f5fb1`, 34 fixtures ×3 deterministic, mismatch `0`.
- V7 mechanical integration: `PASS_SYNTHETIC_MECHANICAL_INTEGRATION`; PRE `638b045aea5a9fc66cee30c78772e792b38b8c79`, result `9f6345e971f36a0def367a70564ba9b86c948e23`.
- V7 first real-evaluation attempt run `35051186125`: `FAIL_V7_BOUNDARY_SYNTHETIC_PREREQUISITE / REAL_EVALUATION_NOT_EXECUTED`; no EGFxSet conclusion; authorization consumed.

### Representation seam historical state

- Bridge iteration 1 run `35051843902`: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`.
- Bridge iteration 2 run `35052132987`: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`; persistent cases `selected64_enters_over_existing60`, `simultaneous_dyad_sel60`, `reattack_m64`.
- Dual-view run `35052606540`: `COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`.
- Frozen-V6 semantic-delta run `35052971870`, result commit `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`: `COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`.
- Frozen semantic roles remain separate: support/local-background eligibility; raw observed fit evidence; candidate competition population; reattack temporal/support representation.
- Historical V6 ratio threshold `0.20` and necessity threshold `0.01` remain reference-only for successor research.

### Reattack temporal/support diagnostic — BLOCKED STORED MEASUREMENT ACCESS

- PRE `77db77632d68f02d52f5d26df87f6fe562cba9e3`.
- Run `35053450282`, job `104658560061`, attempt 1, head `58018849dc5d2c8ebda4378a6b72b6a1f5ef116d`: success.
- Result commit `86549fcf3f15898aa551064b522ce42ca32b1b86`.
- Status `COMPLETE_MECHANICAL_EXECUTION / BLOCKED_STORED_LOG_ACCESS / NO_MEASUREMENT_DECISION`.
- **Do not rerun or locally reproduce.** No exact reattack support-loss stage is frozen and no temporal repair is authorized.

### Candidate-population breadth diagnostic — COMPLETE

- PRE `ea17df201a58d0c6ba841350f2646826da6fe945`; pair head `da4a3624d66c4138390969cb986317b0cd791c05`.
- Run `35057264267`, job `104669939122`, attempt 1: success.
- Artifact `10430643432`, digest `sha256:199af452612c0a224b6bb2b214148026e2501e378d2bed1f510d767380722c9a`.
- Result commit `4750332a347b03795d089690e8f7c4249319cd71`.
- Label `COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`.
- `simultaneous_dyad_sel60`: broad 49 necessity `0.0041216775902363015`; restricted 7 necessity `0.17554666733325255`.
- Same-audio MIDI64: broad `0.05178270149633484`; restricted `0.16256312708394405`.
- Broad competing explanations are required for this synthetic seam, but no successor population is defined.

### Gate-free all-playable competition dictionary diagnostic — COMPLETE

- PRE commit `195d219c0d9a031f2d99b1822176377bac9fbb8c`; pair head `539c4b917a8d2b5bb97b5e1a929a8e506482a191`.
- Run `35057812575`, job `104671550898`, attempt 1: success.
- Artifact `10431411768`, digest `sha256:d076d15560677a8f55b5a70787101b9c592bf54c3774f8d304222c79781b45a8`.
- Result commit `2b115a380cc49a34fc9d42fe0590073e1d1c6d46`.
- Label `COMPLETE_SYNTHETIC_GATE_FREE_COMPETITION_DIAGNOSTIC_NO_DECISION`.
- 19 onset-available fixtures all construct 49 playable competition templates; untouched V3 34×3 PASS.
- `simultaneous_dyad_sel60` remains `0.0041216775902363015`; MIDI64 remains `0.05178270149633484`.
- Gate-free expansion can compress positive-control necessity materially, e.g. `clean_high_m88` `0.5125878896768 -> 0.1751822283493485`.
- This result confounds added columns with feature-bin-union expansion, motivating the now-frozen fixed-feature diagnostic.

## CURRENT TECHNICAL CONCLUSION

The successor seam has five separated questions:

1. support/local-background eligibility;
2. raw observed NNLS fit evidence;
3. broad candidate/template competition population;
4. feature-bin universe used by the competition fit;
5. reattack temporal/support representation.

Broad competition is necessary to avoid the narrow-dictionary dyad failure, and all-playable competition can be constructed without adopting historical V6 `0.20`; however prior gate-free measurement changed both columns and feature rows. The fixed-feature pair is now prospectively frozen to isolate those effects and has not executed.

Do not convert these results into a V6-threshold transplant, all-49 production rule, MIDI exception, fixture branch, threshold search, candidate-subset search, or reattack fallback.

## FRESH CHAT RESUME POINT

1. Read this checkpoint first and reconcile newer branch commits.
2. Do not rerun temporal `35053450282`, candidate-breadth `35057264267`, or gate-free `35057812575`.
3. Fixed-feature PRE: `89f7f0d7b24b30fe2296fd9f76bb44ab50751e0c`; module `949523ca753c2f7f0a5b87af195770210143d8cb` / blob `d69382ae14b1fb8f7f570919240dce372db1e424`; test/pair `ab8b0d2501aab46a313e1dfb1adfad6a3405bd5c` / blob `d658a9f7baee2f13df35956daa7a3c77d24e9eec`.
4. No fixed-feature execution has occurred. Next permitted write is the self-scoped workflow only.
5. Freeze attempt 1 from its artifact before any successor composition PRE.
6. Any future real/media/model evaluation requires a new real-evaluation PRE plus fresh explicit user authorization.

## DO NOT DO

- Do not resume V143/Gomyway.
- Do not rerun any frozen one-shot above.
- Do not tune from post-result attribution.
- Do not adopt/change V3 or historical V6 thresholds.
- Do not add per-MIDI exceptions, fixture branches, learned parameters, candidate subset searches or real-corpus rules.
- Do not edit frozen V6/V3 implementations or frozen result checkpoints.
- Do not switch Production or `main`.
- Do not use real media/model access without a new prospective real-evaluation PRE and explicit user authorization.

Archived V143/Gomyway remains untouched.
