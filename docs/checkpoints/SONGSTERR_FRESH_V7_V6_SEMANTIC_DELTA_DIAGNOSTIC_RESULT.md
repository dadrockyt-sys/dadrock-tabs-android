# RESULT — Songsterr Fresh V7 / Frozen V6 Semantic-Delta Diagnostic V1

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_V6_SEMANTIC_DELTA_DIAGNOSTIC_PRE.md`
PRE commit: `bbc93f68b995598187ec140accf713a604650c60`

## Scope

This is a frozen **measurement-only** result. It defines no successor classifier, combined verdict, threshold, fallback route, promotion rule, production route or real-evaluation authorization.

The diagnostic compared, for all 23 frozen V6 synthetic audio fixtures:

1. frozen V6 raw onset innovation and selected raw-template semantics;
2. frozen V6 full candidate population / NNLS fit behavior;
3. frozen bridge-V2 / V3 support-template behavior;
4. frozen dual-view raw-fit behavior using the support-derived dictionary.

Frozen expected fixture classifications were carried only as reference metadata and did not affect computation, branching or process status.

## Frozen implementation / execution identity

- semantic-delta PRE commit: `bbc93f68b995598187ec140accf713a604650c60`
- diagnostic module commit: `8daaca217ca38f51a3b6e6dbad6b9c2c7a1ac348`
- diagnostic module Git blob: `f3e63be1dba7c862c5ec654750cc5ec2e27e19b8`
- complete module/test pair head: `c11f6c62050a4b4a17518c04a5b01fae701e6b50`
- test Git blob: `a76e1e7264366ffdb846d6e9340a4984853450aa`
- workflow head: `3102611820182c1ffb97b013693d98740e7091e7`
- workflow: `.github/workflows/songsterr-v7-v6-semantic-delta-diagnostic-one-shot.yml`
- workflow Git blob: `c616077c7f6b0bdc899c3db5f665398aeb332850`
- run: `35052971870`
- job: `104657128437`
- attempt: `1`
- workflow conclusion: `success` because the prospectively frozen diagnostic/mechanical invariants completed; this is **not** a classifier PASS.

The PRE-to-pair compare contained exactly the two prospectively allowed new semantic-delta Python files. The one-shot workflow was self-scoped to its own YAML path and verified the frozen V6, fixture-manifest, V3, bridge-V2, dual-view and semantic-delta blobs before execution.

No rescue rerun or post-result metric selection occurred.

## Mechanical result

The first and only semantic-delta execution completed with:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- onset-available rows: `19`
- frozen-V6 selected raw-template valid rows: `18`
- V3 support selected-template valid rows: `14`
- dual-view raw-fit available rows: `14`
- `finalDecisionDefined:false`
- `referenceExpectedUsedForComputation:false`
- `historicalV6ThresholdAdoptedAsSuccessorRule:false`
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked by diagnostic execution: `false`
- customer eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

The four unavailable onset rows were the frozen low-support/context cases: silence, low noise, truncated pre-context and truncated post-context. No evidence or context was fabricated.

## Untouched V3 direct-spectrum regression

The same first workflow attempt executed the untouched frozen iteration-3 suite:

- fixture count `34`
- repetitions `3`
- deterministic `true`
- mismatch count `0`
- result `PASS`
- process status `0`.

The diagnostic did not alter any frozen V3 behavior.

## Semantic finding 1 — entering MIDI64 over an existing MIDI60

Fixture: `selected64_enters_over_existing60`
Reference-only expected class: `onset-birth-corroborated-candidate`.

Frozen V6:

- historical classification: corroborated
- fit passed: `true`
- valid candidate count: `40`
- feature energy: `168.61487022311414`
- selected coefficient: `37.9827614783114`
- necessity fraction: `0.019916868330096094`
- selected raw template valid: `true`
- selected raw-template fundamental ratio: `1.0`.

Frozen V3 support view:

- selected template valid: `true`
- selected cents: `0.0`
- supported harmonic count: `4`
- weighted harmonic coverage: `0.45578231292517013`
- valid candidate count: `6`
- composite: `FAIL_NECESSITY`
- support-view necessity: `0.0017494445720472739`
- candidate-evidence fraction: `0.2077502515962489`
- credible lower-owner MIDIs: `[45,57,61]`
- veto lower owners: `[]`.

Dual-view raw fit using the same support-derived candidate dictionary:

- available: `true`
- raw feature energy: `86.56381529788543`
- selected coefficient: `54.81893579964519`
- raw-view necessity: `0.22933221700533318`.

**Frozen interpretation:** the selected note has plausible support and is independently necessary in frozen V6 and in the raw-observed dual-view fit. Its failure in the support-only composite is caused by using the sparsified support representation as NNLS observed evidence. This confirms that support/local-background evidence and fit/competition evidence must remain separate semantic roles in any successor design.

## Semantic finding 2 — simultaneous dyad selected MIDI60 false positive

Fixture: `simultaneous_dyad_sel60`
Reference-only expected class: `not-onset-birth-corroborated`.

Frozen V6:

- historical classification: not corroborated
- fit passed: `false`
- valid candidate count: `49`
- feature energy: `160.62510890053264`
- selected coefficient: `19.79690947013013`
- necessity fraction: `0.0041216775902363015`
- selected raw template valid: `true`
- selected raw-template fundamental ratio: `1.0`.

Frozen V3 support view:

- selected template valid: `true`
- selected cents: `5.0`
- supported harmonic count: `6`
- weighted harmonic coverage: `1.0`
- valid candidate count: `7`
- composite: `PASS`
- support-view necessity: `0.1840904226252075`
- candidate-evidence fraction: `0.34678943650665484`
- credible lower-owner MIDIs: `[52]`
- veto lower owners: `[]`.

Dual-view raw fit using that same seven-candidate support dictionary:

- available: `true`
- raw feature energy: `78.38698002009778`
- selected coefficient: `35.26484965561954`
- raw-view necessity: `0.14893565820377008`.

Same-audio positive control, selected MIDI64:

- frozen V6 valid candidate count: `49`
- frozen V6 necessity: `0.05178270149633484`
- V3 support valid candidate count: `7`
- support-view necessity: `0.2231743576286899`
- dual raw-view necessity: `0.24578762252117828`
- credible lower owners: `[48,60]`
- veto lower owners: `[]`.

**Frozen interpretation:** changing sparse observed evidence to raw observed evidence does not repair the MIDI60 false positive. The material semantic delta is the competition/template dictionary: frozen V6 evaluates a much broader 49-candidate population and reduces MIDI60 necessity below its historical necessity minimum while preserving MIDI64 in the same audio. The support-derived seven-candidate dictionary leaves MIDI60 strongly necessary under both sparse and raw observations. A successor must investigate candidate-population/competition semantics prospectively rather than tune a necessity threshold or peak width from this result.

## Semantic finding 3 — genuine reattack MIDI64

Fixture: `reattack_m64`
Reference-only expected class: `onset-birth-corroborated-candidate`.

Frozen V6:

- historical classification: corroborated
- fit passed: `true`
- valid candidate count: `34`
- feature energy: `149.28292791314593`
- selected coefficient: `54.96054277761474`
- necessity fraction: `0.14453142873815786`
- selected raw template valid: `true`
- selected raw-template fundamental ratio: `1.0`
- observed harmonic innovation: `[50.902462979354425,18.39929669286834,16.311418147811047,5.608287303513769,5.461352299669706,4.151041656270273]`.

Frozen V3 support view:

- selected template valid: `false`
- status: `NO_ELIGIBLE_DETUNING_ANCHOR`
- valid candidate count: `0`
- dual-view fit: unavailable because no support-derived selected template/dictionary exists.

**Frozen interpretation:** this failure is upstream of competition/NNLS. Frozen V6 sees coherent raw harmonic evidence and strongly corroborates the reattack, while the leakage-cleaned V3 support representation rejects every candidate anchor. This is a separate representation/temporal-support problem and must not be repaired by changing the dyad competition rule or by fixture-specific fallback.

## Protection controls

The semantic comparison preserved the important negative controls:

- `octave_alias_sel72_actual60`: frozen V6 necessity `0.0010925183441363568`; support necessity `0.0`; lower-owner veto `[60]`; dual raw necessity `0.0015097254732536797`.
- `octave_alias_sel79_actual67`: frozen V6 necessity `0.0`; support necessity `0.0`; lower-owner veto `[67]`; dual raw necessity `0.000928071601282142`.
- `neighbor_sel60_actual61`: frozen V6 necessity `0.004104369410450875`; support selected template ineligible.
- `weak_selected64_under60`: frozen V6 necessity `0.0008448320887965837`; support selected template ineligible.
- `unrelated_transient_only_sel64`: frozen V6 raw template is valid, but frozen V6 necessity is only `0.0023185831926859383` and the event is rejected; support selected template is ineligible.
- `already_sounding_m64`: frozen V6 raw template is invalid through `FUNDAMENTAL_ONSET_INNOVATION_TOO_WEAK`; V3 support is likewise ineligible.

The transient-only control is especially important: **raw V6 template validity alone is not a safe promotion rule.** Frozen V6 requires the independent competition/necessity stage to reject it.

## Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`

The diagnostic establishes three distinct wiring requirements:

1. **Support evidence and fit evidence must be separated.** The entering-MIDI64 case is repaired mechanically when raw observed innovation is used for fit while support-derived template eligibility is held fixed.
2. **Candidate competition breadth is a separate semantic dimension.** The MIDI60 dyad false positive is not repaired by raw observed fit against the narrow support-derived dictionary; frozen V6's much broader candidate competition distinguishes MIDI60 from MIDI64 in the same audio.
3. **Reattack support is a separate upstream problem.** The reattack cannot reach a dual-view fit because the current support representation produces no eligible selected template, despite strong frozen-V6 raw harmonic evidence.

Do not collapse these into one post-result threshold or fixture-specific rule. Do not adopt the historical V6 `0.20` fundamental-ratio threshold as a new successor rule merely because frozen V6 is informative here.

The next engineering work, if continued, requires a new prospective synthetic PRE. The safest decomposition is to investigate candidate-population/competition composition and reattack temporal/support representation as separately frozen problems before defining a final successor classifier.

## Authority / prohibited work

No EGFxSet or other real media, prior Basic Pitch artifact, Basic Pitch/Demucs/model inference, real correctness run, AG-PT-set, rejected holdout, protected song, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.
