# RESULT — Songsterr Fresh V7 Fixed-Feature Competition Diagnostic V1

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_PRE.md`
PRE commit: `89f7f0d7b24b30fe2296fd9f76bb44ab50751e0c`

## Scope

This is a frozen **synthetic measurement-only** result. It defines no successor classifier, threshold, selected-note eligibility change, candidate-search rule, production rule, temporal/reattack repair, real-data implication or delivery authorization.

The diagnostic prospectively separated two NNLS semantics that were coupled in the prior gate-free result:

1. candidate-column population; and
2. the feature-bin universe / observed raw vector used by the fit.

Every compared fixed-feature population used the same all-gate-free feature rows and the same untouched raw V6 observed vector for that fixture.

## Frozen implementation / execution identity

- PRE commit: `89f7f0d7b24b30fe2296fd9f76bb44ab50751e0c`
- PRE Git blob: `29e0b297d7b780c8cabc121d6c561cdfa806471f`
- diagnostic module commit: `949523ca753c2f7f0a5b87af195770210143d8cb`
- diagnostic module Git blob: `d69382ae14b1fb8f7f570919240dce372db1e424`
- test / frozen pair head: `ab8b0d2501aab46a313e1dfb1adfad6a3405bd5c`
- test Git blob: `d658a9f7baee2f13df35956daa7a3c77d24e9eec`
- workflow/head commit: `7b0e8512ad7476c500af2f3b9c721c408a6bbd63`
- workflow: `.github/workflows/songsterr-v7-fixed-feature-competition-diagnostic-one-shot.yml`
- workflow Git blob: `937b465d26b70f8c0a7b7f89a543d10b2443b076`
- run: `35058404820`
- job: `104673320912`
- attempt: `1`
- workflow conclusion: `success`
- artifact name: `songsterr-fresh-v7-fixed-feature-competition-diagnostic`
- artifact ID: `10431099242`
- artifact digest: `sha256:9b3fb42d77b8774b60d12de56d20cd4f98e9d62c6139df22396bfb739a1604a8`
- persisted files: `fixed-feature-competition-diagnostic.json`, `v3-regression.txt`

The workflow-file push was the sole first execution trigger. There was no rescue rerun, threshold search, MIDI-range search, candidate-subset search, metric selection or fixture addition after observing output.

## Prospective packet boundary

The PRE-to-pair compare contained only:

- `scripts/songsterr-fresh/v7_fixed_feature_competition_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_fixed_feature_competition_diagnostics_v1.py`;
- state-only edits to `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.

The one-shot workflow verified the prospectively frozen PRE, V6, fixture manifest, bridge-V2, V3/V3 iteration dependencies, gate-free module and new module/test Git blobs before execution. Compilation and static no-network/no-model/no-subprocess/no-repository-mutation guards completed successfully.

## Mechanical result

Attempt 1 completed with:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- onset-available rows: `19`
- all-49 gate-free population rows: `19`
- gate-free fixed-fit available rows: `19`
- historical-raw-valid fixed-fit available rows: `18`
- raw/support-intersection fixed-fit available rows: `13`
- geometry / reproduction tolerance: `1e-12`
- `finalDecisionDefined:false`
- `referenceExpectedUsedForComputation:false`
- `historicalV6RatioGateAdoptedAsCompetitionGate:false`
- `historicalV6NecessityThresholdAdoptedAsDecisionRule:false`
- `candidateSubsetSearchPerformed:false`
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked: `false`
- customer eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

All 19 onset-available rows mechanically reconstructed all 49 gate-free competition templates. Historically V6-valid templates remained geometry-equivalent to the frozen V6 templates to `1e-12`.

For every onset-available row, the all-49 fixed-feature fit reproduced the all-49 variable-feature gate-free fit to `1e-12`, as required because both use the same all-49 feature-bin union.

Where the selected MIDI was historically raw-valid and the frozen V6 fit was mechanically available, the historical variable-feature reference reproduced the frozen V6 fit.

## Untouched V3 direct-spectrum regression

The same first workflow attempt executed the untouched frozen V3 iteration-3 regression:

- fixture count: `34`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `0`
- result: `PASS`.

No frozen V3 implementation or historical result was changed.

## Finding 1 — narrow variable-feature fits substantially inflate necessity

For all `13` rows where the selected MIDI was present in the raw/support-intersection population, moving that same narrow candidate population from its own subset-specific feature union onto the fixed all-49 feature universe **reduced** selected necessity. The `intersectionFeatureUniverseDelta` was negative in all 13 comparable rows.

Representative measurements (`variable-feature intersection -> fixed-feature intersection`):

- `clean_low_m40`: `0.6718242072095567 -> 0.1336742156798457`
- `clean_mid_m64`: `0.37871969306713094 -> 0.0348436350186825`
- `detune_plus25_m64`: `0.3186554828277365 -> 0.055617826773886936`
- `detune_minus25_m64`: `0.5283131335104645 -> 0.04128459632656424`
- `attack_noise_true_m64`: `0.3761254649849046 -> 0.034554805511817326`
- `selected64_enters_over_existing60`: `0.30343914432503055 -> 0.042681875818114806`
- `simultaneous_dyad_sel60`: `0.17554666733325255 -> 0.03581555153043586`
- `simultaneous_dyad_sel64`: `0.16256312708394405 -> 0.03281593026578595`
- `simultaneous_triad_sel60`: `0.1805857315930824 -> 0.03477024848153128`
- `simultaneous_triad_sel64`: `0.05166809445543304 -> 0.008627181637841005`
- `simultaneous_triad_sel67`: `0.045725110105117935 -> 0.0075793556687056415`.

The alias controls likewise decreased:

- `octave_alias_sel72_actual60`: `0.008921043317398085 -> 0.0012940960811666244`
- `octave_alias_sel79_actual67`: `0.00042127371028098784 -> 0.0000010190400936669332`.

**Frozen interpretation:** the very large necessity values previously seen with narrow support-derived/raw-support-intersection dictionaries were materially amplified by contracting the observed feature universe to bins owned by that same narrow dictionary. That inflation is not a pure candidate-column effect.

## Finding 2 — broad candidate columns remain independently material at fixed observation support

Holding the feature universe fixed does **not** make candidate population irrelevant.

The same-audio simultaneous-dyad comparison is the clearest separation:

### Selected MIDI60

- fixed feature bins: `199`
- fixed feature energy: `160.62510890053264`
- broad historical/gate-free 49-candidate necessity: `0.0041216775902363015`
- narrow 7-candidate raw/support-intersection necessity on the same 199 bins: `0.03581555153043586`
- historical-vs-intersection fixed-column delta: `-0.03169387394019956`.

### Selected MIDI64

- same fixed feature bins: `199`
- same fixed feature energy: `160.62510890053264`
- broad historical/gate-free 49-candidate necessity: `0.05178270149633484`
- narrow 7-candidate raw/support-intersection necessity on the same 199 bins: `0.03281593026578595`
- historical-vs-intersection fixed-column delta: `+0.018966771230548893`.

Thus, on an identical observed vector, narrowing from 49 candidates to the same seven-candidate support intersection moves the two selected notes in **opposite directions**: MIDI60 necessity rises while MIDI64 necessity falls.

**Frozen interpretation:** broad competing columns themselves carry independent explanatory information. The prior dyad failure was caused by both a narrow candidate population and its narrow feature universe, not by either semantic dimension alone.

## Finding 3 — fixed-feature candidate-column effects are non-monotonic across fixtures

Among the 13 rows with both historical-raw-valid and raw/support-intersection fixed fits:

- `historicalVsIntersectionColumnDelta > 0` on `8` rows;
- `historicalVsIntersectionColumnDelta < 0` on `5` rows;
- zero on `0` rows.

Examples where narrowing the columns **raises** selected necessity (`historical fixed -> intersection fixed`):

- `detune_minus25_m64`: `0.009232826936120875 -> 0.04128459632656424`
- `selected64_enters_over_existing60`: `0.013982688788731774 -> 0.042681875818114806`
- `simultaneous_dyad_sel60`: `0.0041216775902363015 -> 0.03581555153043586`
- `octave_alias_sel72_actual60`: `0.0010585608366633294 -> 0.0012940960811666244`.

Examples where narrowing the columns **lowers** selected necessity:

- `clean_low_m40`: `0.21180289618799777 -> 0.1336742156798457`
- `clean_mid_m64`: `0.05884670489390565 -> 0.0348436350186825`
- `attack_noise_true_m64`: `0.05942423654588064 -> 0.034554805511817326`
- `simultaneous_dyad_sel64`: `0.05178270149633484 -> 0.03281593026578595`
- all three simultaneous-triad selected notes also decrease under the narrow fixed-feature population.

**Frozen interpretation:** candidate count alone is not a monotonic control variable and cannot justify a post-result population-size threshold or MIDI-specific admission rule.

## Finding 4 — feature-universe expansion explains much of the gate-free compression seen previously

For the historical raw-valid population, holding its columns constant but expanding observation rows to the all-49 feature universe produced `historicalFeatureUniverseDelta <= 0` on every comparable row:

- negative on `9` rows;
- zero on `9` rows.

Representative (`historical variable-feature -> historical fixed-feature`) measurements:

- `clean_high_m88`: `0.5125878896768 -> 0.18512862446868777` (`-0.32745926520811225`)
- `reattack_m64`: `0.14453142873815786 -> 0.048459191605388106` (`-0.09607223713276974`)
- `clean_mid_m64`: `0.07186051708314076 -> 0.05884670489390565` (`-0.013013812189235106`)
- `attack_noise_true_m64`: `0.07298349242692048 -> 0.05942423654588064` (`-0.013559255881039844`)
- `selected64_enters_over_existing60`: `0.019916868330096094 -> 0.013982688788731774` (`-0.005934179541364319`).

Rows whose historical population was already all 49 candidates have zero feature-universe delta by construction, including both simultaneous-dyad rows, all simultaneous-triad rows, unrelated transient and weak-owner control.

**Frozen interpretation:** much of the positive-control necessity compression observed in the prior all-49 gate-free diagnostic came from expanding the observed feature-bin universe, not simply from adding gate-free columns.

## Finding 5 — adding gate-free columns on already-fixed all-49 rows is a smaller, mixed effect

Comparing all-49 gate-free columns with historical raw-valid columns on the **same** all-49 fixed feature universe produced, among 18 available historical fixed fits:

- zero delta on `9` rows;
- negative gate-free-vs-historical delta on `5` rows;
- positive delta on `4` rows.

Representative values (`historical fixed -> gate-free49 fixed`):

- `clean_high_m88`: `0.18512862446868777 -> 0.1751822283493485`
- `clean_mid_m64`: `0.05884670489390565 -> 0.05820153811877132`
- `attack_noise_true_m64`: `0.05942423654588064 -> 0.05872309311957527`
- `selected64_enters_over_existing60`: `0.013982688788731774 -> 0.014558336594470958`
- `neighbor_sel60_actual61`: `0.004045354845430571 -> 0.0041471827861076635`
- `reattack_m64`: `0.048459191605388106 -> 0.05310246072441282`.

The simultaneous-dyad and triad rows are exactly unchanged because their historical raw-valid population already contains all 49 playable MIDIs.

**Frozen interpretation:** once observation support is held fixed, admitting the remaining low-ratio gate-free competitor columns has a smaller and mixed effect than the previously conflated all-49 change. This does not establish that all-49 is a final successor population; it only separates the two measured mechanisms.

## Reattack boundary remains unchanged

For `reattack_m64`, the fixed-feature competition measurements are:

- historical raw-valid candidates: `34`
- raw/support intersection candidates: `0`
- fixed all-49 feature bins: `183`
- historical variable-feature necessity: `0.14453142873815786`
- historical fixed-feature necessity: `0.048459191605388106`
- gate-free49 fixed necessity: `0.05310246072441282`.

These are competition/feature measurements only. The selected support template remains unavailable in the frozen support path, and the exact temporal/support loss stage is still unavailable because the original temporal attempt-1 payload cannot currently be recovered.

No temporal/reattack repair or implication is authorized from this result.

## Insufficient/context controls

The four frozen unavailable rows remained unavailable without fabricated evidence:

- `silence`: `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `low_noise`: `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `truncated_pre_context`: `REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO`
- `truncated_post_context`: `REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO`.

## Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_NO_DECISION`

The fixed-feature diagnostic resolves the prior semantic confound at measurement level:

1. **Feature-universe contraction materially inflates selected necessity in narrow support-derived/intersection fits.** All 13 comparable intersection rows decreased when placed on the fixed all-49 observation support.
2. **Broad candidate columns remain independently material.** On identical feature rows, broad competition preserves a strong same-audio difference between dyad MIDI60 and MIDI64 that the narrow intersection population does not preserve.
3. **Column effects are non-monotonic across fixtures.** Candidate count or individual post-result MIDI attribution cannot be converted into a generic rule from these measurements.
4. **The prior all-49 gate-free compression was substantially a feature-universe effect.** Additional gate-free columns on a fixed all-49 observation vector have a smaller mixed effect.
5. **No final successor classifier is defined.** These measurements do not authorize a necessity threshold, all-49 production rule, selected-note eligibility change, V6 `0.20` transplant, candidate-subset search, reattack fallback, or real/model evaluation.

Any executable successor composition using these measurements requires a new prospective PRE and must preserve the still-separate support, raw-fit, competition, feature-universe and temporal/support roles.

## Authority / prohibited work

No EGFxSet or other real media, Basic Pitch/Demucs/model inference, real correctness run, AG-PT/rejected holdout, protected song, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.
