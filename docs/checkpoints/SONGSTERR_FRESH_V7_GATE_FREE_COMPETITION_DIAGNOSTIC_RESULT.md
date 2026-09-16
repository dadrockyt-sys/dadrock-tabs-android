# RESULT — Songsterr Fresh V7 Gate-Free Competition Dictionary Diagnostic V1

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **COMPLETE_SYNTHETIC_GATE_FREE_COMPETITION_DIAGNOSTIC_NO_DECISION**

## 1. Scope and authority

This freezes the first and only execution of the prospective diagnostic defined by:

- PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_PRE.md`
- PRE commit: `195d219c0d9a031f2d99b1822176377bac9fbb8c`
- PRE blob: `316224fce582cf86135613db08b548fb849b4716`

It measures competition-only admission when the historical V6 fundamental-ratio `0.20` gate is removed from candidate-column admission. It does **not** change selected-note eligibility, define a successor classifier, adopt a threshold, repair reattack behavior, authorize real/model work, or advance delivery.

Archived V143/Gomyway remains untouched.

## 2. Frozen implementation and execution identity

Diagnostic pair:

- module: `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`
- module commit: `3eb799075c9cc8720ed9d827f5b7aecff126d42e`
- module blob: `08eb9e945bf2cdf33e640cf7b3349ae075002846`
- test: `scripts/songsterr-fresh/test_v7_gate_free_competition_diagnostics_v1.py`
- pair head / test commit: `539c4b917a8d2b5bb97b5e1a929a8e506482a191`
- test blob: `f92df723af79a37f12996e896b881593d70d7bc6`

PRE-to-pair compare contained exactly those two added Python files.

One-shot runner:

- workflow: `.github/workflows/songsterr-v7-gate-free-competition-diagnostic-one-shot.yml`
- workflow/head commit: `b518b0e9b344eb0f6d4b2d42cc4a0fa5bfa40323`
- workflow blob: `c6403609d9441d3f32157f125ae1df583abeb9c3`
- run: `35057812575`
- job: `104671550898`
- attempt: `1`
- run number: `1`
- trigger: self-scoped workflow-file push
- conclusion: `success`

No rescue rerun occurred.

## 3. Authoritative artifact

- artifact name: `songsterr-fresh-v7-gate-free-competition-diagnostic`
- artifact id: `10431411768`
- size: `112879` bytes
- digest: `sha256:d076d15560677a8f55b5a70787101b9c592bf54c3774f8d304222c79781b45a8`
- expired at freeze time: `false`

Preserved files:

- `gate-free-competition-diagnostic.json`
- `v3-regression.txt`

This result is frozen from that attempt-1 artifact.

## 4. Mechanical result

The authoritative diagnostic reports:

- fixtures: `23`
- repetitions: `3`
- deterministic: `true`
- onset available: `19`
- all 49 playable MIDI templates structurally constructible: `19/19` onset-available fixtures
- historical V6 already had all 49 candidates: `8` fixtures
- selected MIDI historically invalid but gate-free constructible: `1` fixture
- attribution available: `18` fixtures
- geometry / reproduction tolerance: `1e-12`
- `finalDecisionDefined:false`
- `referenceExpectedUsedForComputation:false`
- `historicalV6RatioGateAdoptedAsCompetitionGate:false`
- `historicalV6NecessityThresholdAdoptedAsDecisionRule:false`
- real corpus evaluated: `false`
- model inference: `false`
- Basic Pitch: `false`
- network: `false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- mechanical status: `COMPLETE`.

For every historically V6-valid candidate, the gate-free builder reproduced the frozen V6 template geometry to the frozen `1e-12` tolerance. For all eight fixtures where historical V6 already admitted all 49 MIDIs, the gate-free all-49 fit reproduced frozen V6 fit fields exactly within that tolerance.

## 5. Untouched V3 regression

`v3-regression.txt` reports:

- fixture count: `34`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `0`
- result: `PASS`.

No frozen V3 implementation changed.

## 6. Primary breadth result

Every onset-available fixture admitted all 49 playable MIDIs under the gate-free competition-only construction. Therefore the historical `0.20` fundamental-ratio gate is **not mechanically required to obtain a structurally complete 49-MIDI competition dictionary** on this frozen synthetic population.

This says nothing about selected-note eligibility. The removed gate remains historical/reference-only and is not declared wrong, unnecessary for other roles, or replaced by a new threshold.

## 7. Eight full-49 historical controls — exact reproduction

The eight fixtures that already had 49 historical V6-valid candidates are unchanged by the gate-free competition dictionary because no new columns are admitted:

- `clean_low_m40`: necessity `0.21180289618799777`
- `simultaneous_dyad_sel60`: `0.0041216775902363015`
- `simultaneous_dyad_sel64`: `0.05178270149633484`
- `simultaneous_triad_sel60`: `0.03996589910876862`
- `simultaneous_triad_sel64`: `0.011551106328093808`
- `simultaneous_triad_sel67`: `0.02679868547802654`
- `unrelated_transient_only_sel64`: `0.0023185831926859383`
- `weak_selected64_under60`: `0.0008448320887965837`.

This is especially important for the frozen dyad result: removing the historical ratio gate from competition admission does **not** re-inflate selected MIDI60. The broad 49-column value remains exactly `0.0041216775902363015`, while same-audio selected MIDI64 remains exactly `0.05178270149633484`.

## 8. Fixtures where removing the competition gate changes the population

For historically selected-valid onset rows with fewer than 49 historical candidates, the gate-free all-49 fit changes selected necessity as follows:

| Fixture | Historical candidates | Newly admitted | Historical necessity | Gate-free necessity | Gate-free − historical |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clean_mid_m64` | 45 | 4 | 0.07186051708314076 | 0.05820153811877132 | -0.013658978964369434 |
| `clean_high_m88` | 35 | 14 | 0.5125878896768 | 0.1751822283493485 | -0.33740566132745153 |
| `detune_plus25_m64` | 45 | 4 | 0.07375627220030836 | 0.06557124232685847 | -0.008185029873449892 |
| `detune_minus25_m64` | 45 | 4 | 0.011357415735861676 | 0.009315541348354626 | -0.00204187438750705 |
| `attack_noise_true_m64` | 45 | 4 | 0.07298349242692048 | 0.05872309311957527 | -0.014260399307345212 |
| `octave_alias_sel72_actual60` | 46 | 3 | 0.0010925183441363568 | 0.0006851135019640799 | -0.0004074048421722769 |
| `octave_alias_sel79_actual67` | 40 | 9 | 0.0 | 0.0 | 0.0 |
| `selected64_enters_over_existing60` | 40 | 9 | 0.019916868330096094 | 0.014558336594470958 | -0.005358531735625135 |
| `neighbor_sel60_actual61` | 47 | 2 | 0.004104369410450875 | 0.0041471827861076635 | +0.000042813375656788714 |
| `reattack_m64` | 34 | 15 | 0.14453142873815786 | 0.05310246072441282 | -0.09142896801374503 |

Across these ten selected-historically-valid rows:

- eight show lower selected necessity after adding the previously ratio-gated candidates;
- one is unchanged (`octave_alias_sel79_actual67`);
- one rises slightly (`neighbor_sel60_actual61`).

Therefore the effect of adding low-ratio competition columns is predominantly suppressive in this frozen population, but it is **not monotonic by construction** and cannot be reduced to “more candidates always lower necessity.”

## 9. Positive-control sensitivity

The threshold-free competition dictionary preserves broad competition but can materially reduce selected necessity for positive synthetic controls.

### `clean_high_m88`

- historical candidates: `35`
- gate-free candidates: `49`
- historical feature bins: `152`
- gate-free feature bins: `192`
- historical feature energy: `106.20527060463667`
- gate-free feature energy: `152.55983091530476`
- historical necessity: `0.5125878896768`
- gate-free necessity: `0.1751822283493485`.

Strongest prospectively enumerated newly admitted candidate: MIDI64.

- its historical ratio metadata: `0.04947909114836207`
- add-one delta from the historical gated population: `-0.19530517131923286`
- gate-free leave-one-out delta: `+0.04899926279099878`
- its coefficient in the full gate-free fit: `18.3586724724862`.

This is a large population/feature-union effect, but it does not define an exclusion rule for MIDI64.

### `detune_minus25_m64`

- historical necessity: `0.011357415735861676`
- gate-free necessity: `0.009315541348354626`.

The historical V6 necessity threshold `0.01` is reference-only, but this measurement sits on the opposite side of that historical reference value after gate removal. That is a concrete warning that the gate-free competition dictionary must **not** simply be plugged into the historical V6 decision rule without a new prospective composition design.

Strongest newly admitted candidate: MIDI44, historical ratio `0.19825547901015486`.

- add-one delta: `-0.0015593473954523176`
- leave-one-out delta: `+0.0014485413701403396`.

### `selected64_enters_over_existing60`

- historical necessity: `0.019916868330096094`
- gate-free necessity: `0.014558336594470958`.

Strongest newly admitted candidate: MIDI42, ratio `0.16355310375721285`.

- add-one delta: `-0.0023191301011505454`
- leave-one-out delta: `+0.0015094598834412328`.

Again, no MIDI42 rule is authorized.

## 10. Negative/protection controls

The gate-free competition dictionary does not show a broad inflation of the frozen negative controls:

- `already_sounding_m64`: the selected MIDI is one of the historically ratio-invalid candidates, but when admitted as a competition-only column its selected coefficient is `0.0` and selected necessity is `0.0`;
- `octave_alias_sel72_actual60`: necessity decreases from `0.0010925183441363568` to `0.0006851135019640799`;
- `octave_alias_sel79_actual67`: remains `0.0`;
- `unrelated_transient_only_sel64`: unchanged at `0.0023185831926859383`;
- `weak_selected64_under60`: unchanged at `0.0008448320887965837`;
- `neighbor_sel60_actual61`: rises only from `0.004104369410450875` to `0.0041471827861076635`.

These are descriptive synthetic controls only. They do not validate a production classifier.

## 11. Reattack remains separate

`reattack_m64` is competition-measurable under raw V6 geometry:

- historical candidates: `34`
- gate-free candidates: `49`
- historical necessity: `0.14453142873815786`
- gate-free necessity: `0.05310246072441282`.

Strongest newly admitted candidate is MIDI51:

- historical ratio metadata: `0.10740889816393139`
- add-one delta from historical population: `-0.05197704791893523`
- gate-free leave-one-out delta: `-0.006661935950546989`.

This does **not** repair or reinterpret the frozen support/temporal failure. `reattack_m64` still lacks the separately required support eligibility in the V7 representation line, and the attempt-1 temporal/support measurement payload remains inaccessible. No reattack acceptance/fallback is authorized.

## 12. Important semantic limitation — population changes also change the feature-bin union

Under frozen V6 NNLS semantics, the observed fit vector is sampled on the union of bins used by the admitted candidate templates. Therefore admitting additional competition templates changes both:

1. the set of dictionary columns; and
2. the feature-bin union / feature energy on which the raw observation is fitted.

Examples:

- `clean_mid_m64`: feature bins `179 -> 190`, energy `224.7735611917374 -> 238.75726938202047`;
- `clean_high_m88`: `152 -> 192`, energy `106.20527060463667 -> 152.55983091530476`;
- `selected64_enters_over_existing60`: `181 -> 197`, energy `168.61487022311414 -> 186.1652712750706`;
- `reattack_m64`: `151 -> 183`, energy `149.28292791314593 -> 199.2417662109049`.

Accordingly, this result establishes a **gate-free dictionary/population effect**, not a pure causal estimate of extra NNLS columns at a fixed feature universe. The prospectively enumerated add-one/leave-one-out rows inherit the same frozen feature-union semantics.

This distinction must be resolved before a final successor competition composition can be justified.

## 13. Frozen interpretation

Attempt 1 supports these descriptive conclusions:

1. A structurally complete 49-MIDI competition dictionary can be built on all 19 onset-available frozen fixtures **without using the historical V6 `0.20` ratio as a competition-admission gate**.
2. For fixtures where V6 already admitted all 49 MIDIs, gate-free construction exactly reproduces frozen V6 competition behavior, including the dyad MIDI60/MIDI64 separation.
3. Newly admitted low-ratio alternatives generally suppress selected necessity on the frozen rows where they exist, sometimes materially.
4. The frozen negative controls do not show broad selected-necessity inflation under the gate-free all-49 dictionary, and `already_sounding_m64` remains zero even though its selected column becomes constructible.
5. Positive-control margins can contract substantially; `clean_high_m88` and `detune_minus25_m64` show why a gate-free competition dictionary cannot simply be paired with historical V6 decision semantics.
6. Population-induced feature-bin expansion is still entangled with column competition under frozen V6 fit construction. A final composition should not attribute all measured change solely to additional competitor columns.
7. No historical threshold, post-result MIDI contributor, or fixture-specific subset is adopted.

## 14. Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_GATE_FREE_COMPETITION_DIAGNOSTIC_NO_DECISION`

The gate-free all-playable dictionary is a viable **measurement representation for broad competition** on the frozen synthetic population in the narrow sense that it is structurally complete and preserves exact V6 behavior where V6 was already full-49. It is **not yet justified as a successor fit composition**, because candidate admission also expands the feature-bin universe and can materially compress positive-control necessity.

The next prospective synthetic question, if continued, should isolate these two effects by comparing candidate-column breadth under a **fixed prospectively defined feature universe**, without threshold search, MIDI exceptions, or reference-label branching.

Any executable fixed-feature diagnostic requires a new prospective PRE.

## 15. Authority remains unchanged

No real media/model evaluation, Basic Pitch/Demucs, AG-PT/rejected holdout, protected song, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN, or archived V143/Gomyway was accessed or changed.

Global authorization remains unchanged and `mayAdvanceDelivery:false`.
