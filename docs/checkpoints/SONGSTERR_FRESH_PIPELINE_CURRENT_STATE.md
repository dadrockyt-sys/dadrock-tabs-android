# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-16 America/Toronto — candidate-breadth and gate-free all-playable competition diagnostics are both frozen from attempt-1 artifacts. The next unresolved synthetic dimension is candidate-column breadth versus feature-bin-union expansion. Temporal/support attempt-1 measurement access remains blocked/no-decision.

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
- Result `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md`, commit `86549fcf3f15898aa551064b522ce42ca32b1b86`.
- Status `COMPLETE_MECHANICAL_EXECUTION / BLOCKED_STORED_LOG_ACCESS / NO_MEASUREMENT_DECISION`.
- Original console payload is inaccessible through current read-only paths; run had no artifact.
- **Do not rerun or locally reproduce.** No exact reattack support-loss stage is frozen and no temporal repair is authorized.

### Candidate-population breadth diagnostic — COMPLETE

- PRE `ea17df201a58d0c6ba841350f2646826da6fe945`.
- Pair head `da4a3624d66c4138390969cb986317b0cd791c05`.
- Workflow/head `3ae25dbb0cb4cb0e2e65cbc2a8aa6184c0d9026b`.
- Run `35057264267`, job `104669939122`, attempt 1: success.
- Artifact `10430643432`, digest `sha256:199af452612c0a224b6bb2b214148026e2501e378d2bed1f510d767380722c9a`.
- Result `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`, commit `4750332a347b03795d089690e8f7c4249319cd71`.
- Label `COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`.
- 23 fixtures ×3 deterministic; untouched V3 34×3 PASS.
- All 13 numerically comparable fixtures have larger selected necessity under narrow raw/support-intersection competition than broad raw-valid competition.
- `simultaneous_dyad_sel60`: full 49 necessity `0.0041216775902363015`; restricted 7 necessity `0.17554666733325255`.
- Same-audio `simultaneous_dyad_sel64`: full `0.05178270149633484`; restricted `0.16256312708394405`.
- `selected64_enters_over_existing60`: full 40 `0.019916868330096094`; restricted 5 `0.30343914432503055`.
- Prospectively enumerated attribution is interacting/non-monotonic; no MIDI59/MIDI63/other post-result candidate rule is authorized.
- Result supports broad competing explanations but does not define a successor population.

### Gate-free all-playable competition dictionary diagnostic — COMPLETE

Prospective identity:

- PRE `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_PRE.md`, commit `195d219c0d9a031f2d99b1822176377bac9fbb8c`, blob `316224fce582cf86135613db08b548fb849b4716`.
- module commit `3eb799075c9cc8720ed9d827f5b7aecff126d42e`, blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`.
- test/pair head `539c4b917a8d2b5bb97b5e1a929a8e506482a191`, blob `f92df723af79a37f12996e896b881593d70d7bc6`.
- PRE-to-pair diff exactly two allowed Python files.
- workflow/head `b518b0e9b344eb0f6d4b2d42cc4a0fa5bfa40323`, workflow blob `c6403609d9441d3f32157f125ae1df583abeb9c3`.
- run `35057812575`, job `104671550898`, attempt 1: success.
- artifact `10431411768`, digest `sha256:d076d15560677a8f55b5a70787101b9c592bf54c3774f8d304222c79781b45a8`.
- result `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_RESULT.md`, commit `2b115a380cc49a34fc9d42fe0590073e1d1c6d46`.
- label `COMPLETE_SYNTHETIC_GATE_FREE_COMPETITION_DIAGNOSTIC_NO_DECISION`.

Mechanical facts:

- 23 fixtures ×3 deterministic; onset available 19.
- all 19 onset-available fixtures structurally construct all 49 playable MIDI competition templates without using historical V6 `0.20` as an admission gate.
- every historically V6-valid template reproduces frozen V6 geometry to `1e-12`.
- eight fixtures already had 49 historical V6-valid candidates and reproduce frozen V6 fit exactly.
- untouched V3 regression: 34 fixtures ×3, deterministic, mismatch `0`, PASS.
- selected historical-gate-invalid but gate-free-constructible count: 1 (`already_sounding_m64`); its gate-free selected coefficient and necessity are both `0.0`.

Key measurements:

- `simultaneous_dyad_sel60` remains exactly `0.0041216775902363015`; `simultaneous_dyad_sel64` remains exactly `0.05178270149633484` because both historical populations were already all 49 MIDIs.
- `clean_mid_m64`: `0.07186051708314076 -> 0.05820153811877132`.
- `clean_high_m88`: `0.5125878896768 -> 0.1751822283493485` when candidate count grows 35→49.
- `detune_plus25_m64`: `0.07375627220030836 -> 0.06557124232685847`.
- `detune_minus25_m64`: `0.011357415735861676 -> 0.009315541348354626`; the historical `0.01` necessity threshold remains reference-only, but this crossing warns against plugging gate-free competition directly into historical V6 decision semantics.
- `attack_noise_true_m64`: `0.07298349242692048 -> 0.05872309311957527`.
- `selected64_enters_over_existing60`: `0.019916868330096094 -> 0.014558336594470958`.
- `octave_alias_sel72_actual60`: `0.0010925183441363568 -> 0.0006851135019640799`; alias79 stays `0.0`.
- `neighbor_sel60_actual61`: small increase `0.004104369410450875 -> 0.0041471827861076635`.
- `unrelated_transient_only_sel64` and `weak_selected64_under60` are unchanged because both historical populations were already 49.
- `reattack_m64`: raw competition necessity `0.14453142873815786 -> 0.05310246072441282`, but support eligibility remains separately blocked and no temporal conclusion is authorized.

Critical semantic limitation:

Under frozen V6 NNLS construction, candidate population defines the union of feature bins used for the raw observed fit. Adding low-ratio candidates therefore changes **both** dictionary columns and the feature-bin universe/feature energy. Examples:

- `clean_high_m88`: feature bins 152→192, energy `106.20527060463667 -> 152.55983091530476`;
- `selected64_enters_over_existing60`: 181→197, energy `168.61487022311414 -> 186.1652712750706`;
- `reattack_m64`: 151→183, energy `149.28292791314593 -> 199.2417662109049`.

Therefore the gate-free result establishes a **dictionary/population effect**, not a pure causal estimate of additional competitor columns at fixed observation support.

## CURRENT TECHNICAL CONCLUSION

The successor seam now has five separated questions:

1. support/local-background eligibility;
2. raw observed NNLS fit evidence;
3. broad candidate/template competition population;
4. feature-bin universe used by the competition fit;
5. reattack temporal/support representation.

Broad competition is necessary to avoid the narrow-dictionary dyad failure, and an all-49 competition dictionary can be constructed without adopting historical V6 `0.20`. However, gate-free population expansion also expands the fit feature universe and can materially compress positive-control necessity. A final successor competition composition is therefore not yet justified.

Do not convert these results into a V6-threshold transplant, all-49 production rule, MIDI exception, fixture branch, threshold search, candidate-subset search, or reattack fallback.

## NEXT PROSPECTIVE SYNTHETIC QUESTION

If continuing this line, the next safe measurement is a **fixed-feature competition diagnostic**, prospectively defined before execution, that separates:

- candidate-column breadth; from
- population-induced feature-bin-union expansion.

The PRE must define one fixed feature universe generically for each onset-available fixture before comparing candidate populations. It must not use reference labels, post-result MIDI selection, threshold search, support-validity as a final classifier, or historical V6 decision thresholds.

The purpose is measurement only: determine whether broad columns still produce the key dyad/positive-control separation when the observed raw feature vector is held on the same prospectively defined bins across compared candidate populations.

Any executable fixed-feature diagnostic requires a new PRE, frozen pair, one-shot attempt with artifact preservation, untouched V3 regression, and a frozen result before any composition rule.

## FRESH CHAT RESUME POINT

1. Read this checkpoint first and reconcile newer branch commits.
2. Do not rerun temporal run `35053450282`, candidate-breadth run `35057264267`, or gate-free run `35057812575`.
3. Candidate-breadth authority: result commit `4750332a347b03795d089690e8f7c4249319cd71`, artifact `10430643432`.
4. Gate-free authority: result commit `2b115a380cc49a34fc9d42fe0590073e1d1c6d46`, artifact `10431411768`.
5. Temporal line remains blocked/no-decision at result commit `86549fcf3f15898aa551064b522ce42ca32b1b86`.
6. If continuing synthetic competition research, write a new fixed-feature diagnostic PRE **before executable code**.
7. Any future real/media/model evaluation requires a new real-evaluation PRE plus fresh explicit user authorization.

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
