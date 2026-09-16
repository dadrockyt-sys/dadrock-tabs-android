# PRE — Songsterr Fresh V7 Gate-Free Competition Dictionary Diagnostic V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / DIAGNOSTIC-ONLY / NO CLASSIFIER**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. Frozen motivation

The frozen candidate-population result is:

`COMPLETE_SYNTHETIC_CANDIDATE_COMPETITION_BREADTH_DIAGNOSTIC_NO_DECISION`

Authority:

- result: `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`
- result commit: `4750332a347b03795d089690e8f7c4249319cd71`
- run: `35057264267`, attempt 1
- artifact id: `10430643432`

That result established prospectively that narrowing raw-template competition to the raw/support-valid MIDI intersection raises selected necessity in all 13 numerically comparable fixtures. In `simultaneous_dyad_sel60`, the same raw observation and raw-template semantics changed from 49-candidate necessity `0.0041216775902363015` to seven-candidate necessity `0.17554666733325255`.

It also established that the historical V6 raw-valid population is informative but cannot simply be adopted as the successor population because V6 candidate validity includes the historical/reference-only fundamental-to-max-harmonic ratio gate `0.20`.

This PRE asks whether broad competition can be represented **without any per-candidate evidence-validity threshold at all**.

The blocked temporal/support line remains separate and untouched.

## 2. Diagnostic question — no classifier

For each onset-available frozen V6 synthetic fixture, construct one competition-only harmonic template for **every playable MIDI 40..88** using frozen V6 geometric/template mechanics but **without applying the historical `0.20` fundamental-ratio validity gate**.

Then measure the selected-MIDI NNLS necessity under that 49-MIDI gate-free competition dictionary and compare it mechanically with the frozen V6 gated fit where available.

This is a competition-population measurement only. It does not decide whether the selected note is valid, supported, corroborated, accepted, rejected, or customer eligible.

## 3. Frozen population

Use all 23 fixtures from:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for exactly three in-process repetitions.

Reference expected classifications may be copied only as metadata. They may not affect template construction, branching, fit availability, process status, attribution, or any result field other than reference metadata.

No fixture-ID computation branch is allowed.

## 4. Frozen dependencies / read-only semantics

Read-only:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- frozen V3 base / iteration-2 / iteration-3 modules and untouched iteration-3 regression test;
- all prior fresh-pipeline PRE/result checkpoints and runs;
- `songsterr_pipeline/**`;
- `main`, Production, closed research lines and archived V143/Gomyway.

No frozen constant may be changed.

Historical V6 `TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN = 0.20` and `NECESSITY_FRACTION_MIN = 0.01` remain reference-only. Neither is a decision boundary in this diagnostic.

## 5. Gate-free competition template construction

For each onset-available fixture, use the untouched raw V6 onset innovation and frozen V6 frequency grid.

For every MIDI `40..88`, construct a competition-only template using the exact frozen V6 geometry **up to but not including the historical fundamental-ratio rejection**:

1. define the MIDI fundamental semitone cell using `midi - 0.5` to `midi + 0.5` through frozen V6 `midi_to_hz()`;
2. within that cell, choose the raw-innovation maximum as the fundamental bin, exactly as frozen V6 does;
3. use that chosen fundamental frequency to generate harmonics in ascending order up to frozen `HARMONIC_COUNT_MAX = 6` and Nyquist;
4. for each harmonic, use the frozen V6 nearest-bin geometry and `nearest ±1` raw-innovation local maximum;
5. use frozen V6 harmonic weights `1/harmonic`, normalized by their L2 norm;
6. record the observed harmonic innovation and fundamental-to-max-harmonic ratio;
7. record `historicalV6RatioGateWouldPass = (ratio >= 0.20)` as reference metadata only;
8. **do not reject the candidate because of that ratio**.

Structural failures unrelated to the historical ratio gate must remain explicit and must not fabricate a template. Given the frozen playable range/grid, the first execution is expected to verify whether all 49 candidates are structurally constructible rather than assume silently.

No support-validity, V3 eligibility, owner veto, candidate-evidence threshold, fixture label or post-result measurement may gate competition-template admission.

## 6. Required geometry equivalence check

For every MIDI whose frozen V6 `_candidate_template()` is valid, the gate-free builder must reproduce the frozen V6 template geometry exactly:

- fundamental bin;
- fundamental Hz to `1e-12` absolute/relative;
- harmonic bins;
- normalized harmonic weights to `1e-12` absolute/relative;
- observed harmonic innovation to `1e-12` absolute/relative;
- fundamental-to-max-harmonic ratio to `1e-12` absolute/relative.

Any mismatch is a mechanical failure.

This ensures the only intended semantic difference is candidate admission when the historical ratio gate would have rejected a structurally constructible template.

## 7. Gate-free all-MIDI NNLS fit

For each onset-available fixture where the selected MIDI has a structurally constructible gate-free template:

- candidate list: every structurally constructible playable MIDI, ascending;
- observed vector: untouched raw V6 innovation sampled at the union of all included gate-free template bins;
- dictionary: gate-free template weights at those bins;
- solver: `scipy.optimize.nnls`;
- selected coefficient: coefficient of the selected MIDI column;
- selected necessity: `(withoutSelectedResidual - fullResidual) / max(featureEnergy, 1e-15)` after removing the selected MIDI column;
- no threshold comparison.

Record:

- exact candidate list/count;
- feature bins/count;
- feature energy;
- selected coefficient;
- full residual;
- residual without selected;
- selected necessity fraction;
- all candidate coefficients in ascending MIDI order.

## 8. Frozen-V6 gated reference

Carry the exact frozen `v6.classify_audio_event()` / fit payload as a namespaced reference.

For onset-available fixtures where frozen V6 has a selected-template `status: OK` fit, record:

- frozen raw-valid candidate count;
- frozen feature energy;
- selected coefficient;
- residuals;
- necessity fraction.

When frozen V6 raw-valid candidate count is already `49`, the gate-free 49-MIDI fit must mechanically reproduce the frozen V6 fit to `1e-12` because the candidate population and valid-template geometry are identical. A mismatch is a mechanical failure.

Where frozen V6 candidate count is less than 49, the difference is a measurement of removing the historical ratio gate from competition admission only.

## 9. Prospectively frozen newly-admitted-candidate attribution

For each onset-available fixture define generically:

- `historicalRawValidMidis`: frozen V6-valid candidate MIDIs;
- `gateFreeMidis`: structurally constructible gate-free MIDIs;
- `newlyAdmittedMidis = gateFreeMidis - historicalRawValidMidis`.

When the selected MIDI is frozen-V6-valid and both the frozen gated fit and gate-free fit are available, enumerate **every** `newlyAdmittedMidi` in ascending order.

For each newly admitted candidate:

### Add-one attribution

Fit `historicalRawValidMidis ∪ {midi}` using the same gate-free template geometry and raw observation. Record:

- selected necessity;
- `necessityDeltaFromFrozenGatedPopulation`.

### Gate-free leave-one-out attribution

Fit `gateFreeMidis - {midi}` while retaining the selected MIDI. Record:

- selected necessity;
- `necessityDeltaFromGateFreePopulation`.

These rows are descriptive only. No candidate may be selected for a rule after output is observed.

The result may identify the largest absolute add-one and leave-one-out deltas with deterministic lower-MIDI tie-break for readability only.

## 10. Selected-MIDI historical-gate failures

If the selected MIDI itself is structurally constructible but fails the historical V6 ratio gate, the gate-free diagnostic may report its gate-free coefficient/necessity as a measurement.

It may **not** interpret that measurement as acceptance, promotion, corroboration, or evidence that the historical gate should be removed from selected-note eligibility. Competition-template admission and selected-note eligibility are separate semantic roles.

`already_sounding_m64` is an important generic negative control for this separation, but no fixture-specific computation branch is allowed.

## 11. Key result-summary classes

The result checkpoint must summarize, without special-case computation:

- clean onset controls: `clean_low_m40`, `clean_mid_m64`, `clean_high_m88`;
- detune controls: `detune_plus25_m64`, `detune_minus25_m64`;
- `attack_noise_true_m64`;
- `already_sounding_m64`;
- both octave aliases;
- `selected64_enters_over_existing60`;
- both simultaneous-dyad selected notes;
- all three simultaneous-triad selected notes;
- `neighbor_sel60_actual61`;
- `reattack_m64` only as a competition-population measurement, with no support/temporal conclusion;
- `unrelated_transient_only_sel64`;
- `weak_selected64_under60`;
- all four insufficient/context rows.

## 12. Mechanical invariants

The first execution must establish all of the following or fail:

- exact frozen dependency blobs/contracts;
- exactly 23 fixture rows in manifest order;
- exactly 3 in-process repetitions;
- canonical-JSON deterministic output across repetitions;
- `finalDecisionDefined:false` globally and per row;
- reference expected classification not used for computation;
- finite diagnostics where available;
- gate-free competition admission never consults the historical ratio as a gate;
- gate-free geometry reproduces every frozen-V6-valid template to `1e-12`;
- when frozen V6 has 49 valid candidates, gate-free fit reproduces frozen V6 fit fields to `1e-12`;
- newly admitted attribution enumerates every and only `gateFreeMidis - historicalRawValidMidis` when available;
- no support/V3 eligibility field gates the competition dictionary;
- no classifier, threshold comparison or successor verdict is emitted;
- diagnostic code contains no network/model/GPU/subprocess/repository mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

Process status depends only on these mechanical invariants, not on reference expected classifications or whether a measured necessity appears desirable.

## 13. First-run evidence preservation

The one-shot runner must persist attempt-1 output as a GitHub Actions artifact in addition to console output.

Required artifact name:

`songsterr-fresh-v7-gate-free-competition-diagnostic`

Required files:

- `gate-free-competition-diagnostic.json` — exact diagnostic-test stdout JSON;
- `v3-regression.txt` — untouched V3 regression stdout.

Use `actions/upload-artifact@v4` with `if: always()`.

## 14. Prospective write boundary

May create/change only:

- `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_PRE.md`;
- `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_gate_free_competition_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-gate-free-competition-diagnostic-one-shot.yml`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires another prospective PRE.

## 15. First-run policy

- Commit this PRE before executable diagnostic code.
- Commit the module/test pair before observing any diagnostic output.
- Verify PRE-to-pair diff contains only the two allowed new Python files plus any state-only checkpoint update.
- Perform compile/static import/I/O guard before execution.
- Add a self-scoped workflow only after the pair is frozen; its own push is the sole first execution trigger.
- Pin/verify every frozen dependency plus PRE/module/test blobs.
- Execute exactly once with untouched V3 regression in the same attempt.
- Freeze attempt 1 from the persisted artifact.
- No rescue rerun, threshold search, MIDI-range search, candidate-subset search, metric selection or post-result fixture addition.

## 16. Explicit prohibitions

No successor classifier; no selected-note eligibility change; no reattack repair; no V6 `0.20` adoption/change/search; no necessity-threshold adoption/change/search; no V3 threshold/radius change; no support-validity competition gate; no per-MIDI exception; no fixture branch; no playable-range search; no learned parameter; no EGFxSet/real media; no prior Basic Pitch artifact; no Basic Pitch/Demucs/model inference; no real correctness; no AG-PT/rejected holdout; no protected song; no physical capture/calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 17. Authority after result

Measurement only. The result will not itself authorize a final composition rule, selected-note gate change, real/model evaluation or delivery advancement.

Any successor composition after this diagnostic requires another prospective PRE.
