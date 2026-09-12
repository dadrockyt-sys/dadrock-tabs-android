# Songsterr Fresh Polyphonic Harmonic Necessity V5

Status: **SYNTHETIC CONTRACT GREEN / RESEARCH ONLY / NO REAL CORPUS EVALUATED**

Branch: `songsterr-fresh-pipeline-v1`

## Frozen preregistration

`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`

Preregistration commit:
`beb80f32311bd0b713b78d81049d68dbeec7afe3`

## Implementation

`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`

Implementation commit:
`0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`

Contract:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`

V5 uses a full playable-guitar harmonic dictionary and deterministic nonnegative least squares to test whether the existing selected MIDI is necessary to explain the observed spectrum when simultaneous pitches are allowed. It does not rewrite event identity or MIDI.

Frozen core constants:
- sample rate `44100`
- window samples `8192`
- window offsets `(2048, 8192, 14336)`
- FFT size `32768`
- playable MIDI `40..88`
- harmonics `1..8`
- demeaned RMS minimum `1e-4`
- leave-one-selected-pitch-out necessity fraction minimum `0.01`
- selected fundamental / own maximum harmonic magnitude minimum `0.05`
- NumPy `1.26.4`
- SciPy `1.15.3`
- all three temporal views required; no voting/fallback.

## Synthetic fixture manifest

`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`

Manifest commit:
`efca2994efdce2c5a3b35d6e12fb9dc82096a268`

Frozen fixture count: `20`

Expected class counts:
- independently corroborated: `13`
- not independently corroborated: `4`
- insufficient evidence: `3`.

The fixture population includes monophonic range, ±25-cent detuning, attack noise, dominant second harmonic, perfect-fifth dyad, triads with different selected chord tones, a dense six-note mixture, close dyad, wrong-octave traps, neighboring-semitone trap, temporal pitch change, silence, low noise and truncation.

## Controlled CI

Workflow:
`.github/workflows/songsterr-fresh-v5-polyphonic-necessity-ci.yml`

Workflow commit:
`7f07aa34ffb45860d55bcd755372abca98019717`

Run:
`34718020842`

Job:
`103618636972`

Conclusion: **SUCCESS**

Exact CI source:
`7f07aa34ffb45860d55bcd755372abca98019717`

Runtime observed:
- CPython `3.10.21`
- NumPy `1.26.4`
- SciPy `1.15.3`.

All 20 frozen fixture classifications matched exactly. The result class counts were `13 / 4 / 3` as preregistered.

Notable positive synthetic cases that passed:
- dominant second harmonic;
- perfect-fifth dyad selected root;
- major triad selected root;
- major triad selected third;
- minor triad selected fifth;
- dense six-note mixture selected note;
- equal close dyad selected note.

Notable negative synthetic cases that were correctly rejected:
- wrong octave up;
- wrong octave down;
- stronger neighboring semitone;
- temporal pitch change.

Low support and truncation remained insufficient evidence.

The CI also verified:
- exact constants/runtime pins;
- exact fixture population and class counts;
- no Basic Pitch, Demucs, Torch or `songsterr_pipeline` import in the V5 corroborator;
- no real-corpus standalone mode;
- no real GuitarSet/IDMT fixture present;
- no protected-song fixture use;
- `modelValidationComplete:false`, customer eligibility `0`, delivery false, duration authority unchanged.

## Synthetic audio identities from the green run

- mono_low_m40 `c3bd521a3c4f2e96db99c97402e1e25fb9e4ec3b53778dfd11d809e47b5b8666`
- mono_mid_m64 `bf1c804f1875c88d41b5752e7c14df9e06860c6c79689865e06b3dc34d04037f`
- mono_high_m88 `77a2fe51bb99bd1dafcf5c38e35790bed1f1388b53ea4ec8d4884dc31908338d`
- detuned_plus25_m64 `182efed28af3849fd3571ffa44e3aa7c36f3da565d80e04bfeefadbc59061fe5`
- detuned_minus25_m52 `68c3bda10d48aaa63b3ced18409eac02e846bb8857bb96b15db505a662ac09b5`
- attack_noise_m64 `68b532721c958a6e03d52941325539ee2763fd50ea2c7d730dea420c006e42be`
- dominant_second_harmonic_m52 `7980b1a2c3976b21d0c7c109eed5926e1072949012fde4733c537cc902d37da4`
- perfect_fifth_dyad_selected_root `a3bf6f5b654aade08f69ddf7195658f84a7fae7fb50b4f1548ee6c600cd9485e`
- major triad shared audio `1c5e4e3bbc386ec915f52194fbf625ccec0978dea9d30d324f800bbb8b52abed`
- minor_triad_selected_fifth `23bd1f7f850d3b42c5d7130a05e526220fad8d7ca8ca94822ab697b5d0e4c63e`
- dense_six_note_mixture_selected64 `99c26e412f3cf4ab371bcf97e3def61fb0caee4b149a80ff0d541e7fdfbe45b4`
- equal_close_dyad_selected60 `07d15a20792daabf9bcf0f4db298c1b80b3bef9a6a62f533a0cc807a55461228`
- wrong_octave_down_selected64 `4e951d2716b8d651a55e9de9c65838bd3ce3cc1af511d73ecf78d6d97e743cae`
- stronger_neighbor_selected60 `80915414418c3c026ecde7dfff32f6b3e2d843b18ba2db692a3f1b61f1bfa241`
- temporal_pitch_change_selected60 `9d94625080d58fcd0c82a6ffb8b8a8c4eef673e02257e4eb7830df37151f47a8`
- silence_m60 `39aae763b0cb272253dbce5bae2d88305407acfa8f729b31072ea4c11bbad5a2`
- low_noise_m60 `fbccbbbdacf21f47e887b38074d20df8f13ed4f8a74520c10bd0a57dd3b0a457`
- truncated_m60 `d5d85bfe7d76a2535d0748bd0da1580a5a75dd114b86f2df3b4dd706dedc8e03`.

## Interpretation

This is meaningful synthetic progress because V5 can preserve multiple simultaneously present chord tones while still rejecting several common harmonic/neighbor traps. It demonstrates that the polyphonic-NNLS formulation is mathematically viable under its frozen synthetic contract.

It does **not** establish real-guitar reliability or admission authority.

## Next gate

Select a genuinely untouched external corpus using metadata/inventory only. Previously observed GuitarSet and IDMT results are excluded as untouched V5 admission holdouts. Any corpus already materially analyzed in this repository must also be treated as contaminated/historical unless an untouched preregistered partition can be independently established before correctness results are viewed.

Before any V5 real-corpus correctness run, freeze a separate external-validation preregistration covering exact corpus/version/files, exclusions, annotation semantics, inference runtime/settings, matching, uncertainty, minimum positives, overall/stratum gates, provenance and fail-closed policy boundary.

Authority remains false/0/false and duration remains paused.
