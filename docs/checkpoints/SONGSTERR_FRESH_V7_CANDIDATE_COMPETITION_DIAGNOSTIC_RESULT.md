# RESULT — Songsterr Fresh V7 Candidate-Population / Competition Diagnostic V1

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION**

## 1. Scope and authority

This freezes the first and only execution of the prospective synthetic-only, measurement-only diagnostic defined by:

- PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_PRE.md`
- PRE commit: `ea17df201a58d0c6ba841350f2646826da6fe945`
- PRE blob: `0e966271403ee9eaaea6b52f5e3739b77d02c5c6`

This result defines **no successor classifier, threshold, candidate-admission rule, playable-MIDI rule, fallback, real/model implication, or delivery advancement**.

The blocked temporal/support diagnostic remains separate. Nothing in this result repairs or reinterprets `reattack_m64`, and nothing here resumes archived V143/Gomyway.

## 2. Frozen implementation and execution identity

Diagnostic pair:

- module: `scripts/songsterr-fresh/v7_candidate_competition_diagnostics_v1.py`
- module commit: `b7abd17a37680a720b0e0fa6c7831fa0e0c94402`
- module blob: `194507cbd23b4f67be20c2d7a6a28b454bb146ca`
- test: `scripts/songsterr-fresh/test_v7_candidate_competition_diagnostics_v1.py`
- pair head / test commit: `da4a3624d66c4138390969cb986317b0cd791c05`
- test blob: `080040b9269fa80b14508f5c654d4b5054afab3d`

One-shot runner:

- workflow: `.github/workflows/songsterr-v7-candidate-competition-diagnostic-one-shot.yml`
- workflow/head commit: `3ae25dbb0cb4cb0e2e65cbc2a8aa6184c0d9026b`
- workflow blob: `b4696d10d347c21b7414bddfc228129a32a89bff`
- run: `35057264267`
- job: `104669939122`
- attempt: `1`
- run number: `1`
- trigger: self-scoped `push` of the workflow file
- conclusion: `success`

The workflow successfully completed, in order:

1. frozen Python/dependency setup;
2. exact frozen Git-blob verification;
3. compile/static no-network/no-model/no-repository-mutation guard;
4. the frozen 23-fixture candidate-competition diagnostic exactly once;
5. the untouched V3 iteration-3 regression in the same attempt;
6. authoritative evidence preservation.

No rescue rerun occurred.

## 3. Authoritative preserved artifact

Artifact:

- name: `songsterr-fresh-v7-candidate-competition-diagnostic`
- artifact id: `10430643432`
- size: `44116` bytes
- digest: `sha256:199af452612c0a224b6bb2b214148026e2501e378d2bed1f510d767380722c9a`
- expired at freeze time: `false`

Preserved files:

- `candidate-competition-diagnostic.json`
- `v3-regression.txt`

This result was extracted from that attempt-1 artifact, not from a rerun or reconstructed execution.

## 4. Mechanical result

The authoritative JSON records:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- onset-available fixtures: `19`
- selected MIDI present in raw/support-valid intersection: `14`
- full restricted-vs-broad attribution available: `13`
- frozen-V6 reproduction tolerance: `1e-12`
- `finalDecisionDefined:false`
- `referenceExpectedUsedForComputation:false`
- `historicalV6ThresholdAdoptedAsSuccessorRule:false`
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked: `false`
- customer eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

The gate also verified that every comparable `rawFullFit` reproduced the frozen V6 fit fields to the prospectively fixed `1e-12` absolute/relative tolerance.

## 5. Untouched V3 regression

The preserved `v3-regression.txt` is:

- contract: `songsterr-fresh-v3-physical-template-evidence-significance-synthetic-test-v3`
- fixture count: `34`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `0`
- result: `PASS`.

No frozen V3 implementation or behavior changed.

## 6. Population-breadth measurement across all available comparisons

The controlled comparison holds raw V6 observation and raw V6 template semantics fixed. Only the candidate MIDI population changes from the full raw-valid set to the raw/support-valid intersection.

For all **13** fixtures where both fits are numerically available, the restricted intersection produces a larger selected-MIDI necessity than the broad raw-valid population. This is a descriptive property of attempt 1, not a threshold or classifier.

| Fixture | Raw-full candidates | Intersection candidates | Raw-full necessity | Restricted necessity | Restricted − full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clean_low_m40` | 49 | 2 | 0.21180289618799777 | 0.6718242072095567 | 0.46002131102155897 |
| `clean_mid_m64` | 45 | 3 | 0.07186051708314076 | 0.37871969306713094 | 0.30685917598399015 |
| `detune_plus25_m64` | 45 | 3 | 0.07375627220030836 | 0.3186554828277365 | 0.24489921062742812 |
| `detune_minus25_m64` | 45 | 3 | 0.011357415735861676 | 0.5283131335104645 | 0.5169557177746028 |
| `attack_noise_true_m64` | 45 | 3 | 0.07298349242692048 | 0.3761254649849046 | 0.30314197255798414 |
| `octave_alias_sel72_actual60` | 46 | 3 | 0.0010925183441363568 | 0.008921043317398085 | 0.007828524973261728 |
| `octave_alias_sel79_actual67` | 40 | 2 | 0.0 | 0.00042127371028098784 | 0.00042127371028098784 |
| `selected64_enters_over_existing60` | 40 | 5 | 0.019916868330096094 | 0.30343914432503055 | 0.28352227599493446 |
| `simultaneous_dyad_sel60` | 49 | 7 | 0.0041216775902363015 | 0.17554666733325255 | 0.17142498974301626 |
| `simultaneous_dyad_sel64` | 49 | 7 | 0.05178270149633484 | 0.16256312708394405 | 0.1107804255876092 |
| `simultaneous_triad_sel60` | 49 | 9 | 0.03996589910876862 | 0.1805857315930824 | 0.14061983248431376 |
| `simultaneous_triad_sel64` | 49 | 9 | 0.011551106328093808 | 0.05166809445543304 | 0.040116988127339236 |
| `simultaneous_triad_sel67` | 49 | 9 | 0.02679868547802654 | 0.045725110105117935 | 0.018926424627091393 |

`clean_high_m88` is the fourteenth fixture whose selected MIDI is in the raw/support intersection, but its intersection contains only the selected MIDI. The prospectively frozen reduced-dictionary fit is therefore unavailable rather than fabricating a necessity value.

## 7. Primary dyad finding — selected MIDI60

Fixture: `simultaneous_dyad_sel60`.
Reference-only expected class: `not-onset-birth-corroborated`.

Candidate sets:

- raw-valid: all 49 playable MIDIs `40..88`;
- support-valid / raw-support intersection: `[48,52,60,64,67,72,76]`;
- raw-only candidates excluded by support eligibility: `42`.

Broad raw-template fit:

- candidate count: `49`
- feature-bin count: `199`
- feature energy: `160.62510890053264`
- selected coefficient: `19.79690947013013`
- full residual: `81.86255902518059`
- residual without selected: `82.52460393696518`
- selected necessity: `0.0041216775902363015`.

Same raw observation and same raw-template semantics, restricted only to the seven raw/support-valid MIDIs:

- candidate count: `7`
- feature-bin count: `39`
- feature energy: `93.15263866818366`
- selected coefficient: `42.60484126765841`
- full residual: `41.08641259675067`
- residual without selected: `57.439047868248984`
- selected necessity: `0.17554666733325255`.

The population restriction therefore raises selected-MIDI60 necessity by `0.17142498974301626` while holding raw observation and raw V6 template semantics fixed.

### Prospectively frozen excluded-candidate attribution

Among the 42 raw-only candidates, MIDI59 has the largest absolute add-one effect:

- restricted necessity before adding MIDI59: `0.17554666733325255`
- add MIDI59 alone: `0.028050296057115214`
- delta from restricted: `-0.14749637127613735`.

MIDI59 also has the largest absolute full leave-one-out effect:

- full necessity with all 49 candidates: `0.0041216775902363015`
- full population without MIDI59: `0.01702814282853363`
- delta from full: `+0.012906465238297329`.

MIDI59 is therefore a strong measured competitor for this fixture under both prospectively frozen attribution views. It is **not** sufficient to explain the entire broad-population result by itself: the add-one value `0.028050296057115214` remains different from the 49-candidate value `0.0041216775902363015`. The remaining candidates collectively alter the fit as well.

No MIDI59-specific rule is authorized.

## 8. Same-audio selected MIDI64 control

Fixture: `simultaneous_dyad_sel64` uses the same raw/support candidate sets as selected MIDI60.

Broad raw-template fit:

- candidate count: `49`
- necessity: `0.05178270149633484`.

Restricted seven-candidate raw-template fit:

- necessity: `0.16256312708394405`.

Thus broader competition also suppresses selected MIDI64 necessity, but its broad-population measured necessity remains materially different from selected MIDI60 in the same audio (`0.05178270149633484` versus `0.0041216775902363015`).

Its strongest absolute add-one reduction from the restricted population is MIDI45:

- add-one necessity: `0.0905160988446734`
- delta: `-0.07204702823927064`.

Its largest absolute full leave-one-out effect is MIDI57, and the sign is opposite to a simple monotonic “more competitors always reduce necessity” story:

- full necessity: `0.05178270149633484`
- without MIDI57: `0.03536590529485699`
- delta: `-0.016416796201477853`.

This non-monotonic attribution is expected for an interacting NNLS dictionary whose feature-bin union can also change with population membership. It is evidence against turning a single post-result candidate into a generic admission/exclusion rule.

## 9. Entering selected MIDI64 over existing MIDI60

Fixture: `selected64_enters_over_existing60`.
Reference-only expected class: `onset-birth-corroborated-candidate`.

Candidate sets:

- raw-valid count: `40`
- support-valid MIDIs: `[45,57,61,64,73,76]`
- raw/support intersection: `[57,61,64,73,76]`
- support-only MIDI: `[45]`
- raw-only count: `35`.

Broad raw-template necessity: `0.019916868330096094`.

Five-candidate raw/support-intersection necessity: `0.30343914432503055`.

Largest absolute add-one and full leave-one-out attribution is MIDI63:

- restricted + MIDI63 necessity: `0.09239416376011964`
- add-one delta: `-0.21104498056491092`
- full population without MIDI63 necessity: `0.07510570683801254`
- leave-one-out delta from full: `+0.05518883850791645`.

Again, the broad result is not reducible to that one candidate: `0.09239416376011964` after adding only MIDI63 remains different from the full-population `0.019916868330096094`.

## 10. Protection/control observations

### Octave alias selected MIDI72 over actual MIDI60

- raw-full candidates: `46`
- restricted candidates: `3` (`[48,60,72]`)
- raw-full necessity: `0.0010925183441363568`
- restricted necessity: `0.008921043317398085`.

The broad raw-valid population further suppresses the alias relative to the restricted population.

### Octave alias selected MIDI79 over actual MIDI67

- raw-full candidates: `40`
- raw/support intersection: `[67,79]`
- support-only MIDI: `[55]`
- raw-full necessity: `0.0`
- restricted necessity: `0.00042127371028098784`.

Again the broader raw-valid population does not inflate selected-alias necessity in this frozen fixture.

### Selected MIDI not support-eligible

The following onset-available fixtures have a frozen raw V6 full fit but no restricted competition comparison because the selected MIDI is not support-valid:

- `neighbor_sel60_actual61`: raw-full necessity `0.004104369410450875`;
- `reattack_m64`: raw-full necessity `0.14453142873815786`;
- `unrelated_transient_only_sel64`: raw-full necessity `0.0023185831926859383`;
- `weak_selected64_under60`: raw-full necessity `0.0008448320887965837`.

`already_sounding_m64` is not raw-template eligible and is also not support-template eligible, so no controlled raw-full/restricted selected fit exists.

`reattack_m64` therefore remains exactly where the earlier frozen work placed it: the candidate-competition diagnostic cannot be applied because selected support eligibility fails upstream. No temporal/support inference is made from this result.

## 11. Frozen interpretation

The attempt-1 measurements establish the following descriptive facts:

1. **Candidate-population breadth is a material, independent NNLS semantic dimension.** Across every one of the 13 numerically comparable fixtures, restricting raw-template competition to the support-valid intersection increases selected necessity relative to the broad raw-valid population.
2. **The simultaneous-dyad MIDI60 false-positive mechanism is not an observed-vector-only issue.** With raw observation and raw template semantics held fixed, narrowing the candidate population from 49 to seven raises MIDI60 necessity from `0.0041216775902363015` to `0.17554666733325255`.
3. **A small number of raw-only candidates can have large effects, but the broad result is collective and interacting.** MIDI59 is the strongest prospectively measured contributor for dyad MIDI60; MIDI63 is strongest for `selected64_enters_over_existing60`; other fixtures have different strongest candidates and can show non-monotonic leave-one-out effects.
4. **Simply restricting competition to support-valid MIDIs is not justified as a successor mechanism.** The restriction inflates selected necessity for positive controls and negative controls alike, and it removes competition that is materially active in the broad raw fit.
5. **The historical V6 raw-valid population is informative evidence, not an adopted successor rule.** Its candidate validity includes the historical V6 fundamental-ratio threshold `0.20`, which remains reference-only. This result does not authorize transplanting that threshold into V7.
6. **Reattack remains a separate blocked upstream dimension.** No result here supplies the missing support/temporal measurement or a reattack fallback.

## 12. Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`

The measurement supports preserving **broad competing explanations** as a distinct design requirement for later successor composition, but it does not specify how a successor should prospectively construct that broad candidate population without importing historical V6 eligibility semantics.

The next synthetic question, if continued, is therefore narrower than “which threshold should we use?”: prospectively define and measure a **competition-only candidate construction** that can expose broad alternative explanations without using post-result MIDI exceptions, fixture branches, candidate-subset search, or automatically adopting the historical V6 `0.20` template-validity gate.

Any such executable experiment requires a new prospective PRE before implementation.

## 13. Authority / prohibited work remains unchanged

No EGFxSet or other real media, prior Basic Pitch artifact, Basic Pitch/Demucs/model inference, real correctness run, AG-PT-set, rejected holdout, protected song, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN, or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.
