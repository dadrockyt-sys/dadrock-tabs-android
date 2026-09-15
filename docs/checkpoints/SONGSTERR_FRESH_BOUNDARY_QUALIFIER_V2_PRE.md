# PRE — Songsterr Fresh Boundary Qualifier V2 + One Authorized EGFxSet Diagnostic

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Lets take what was learned, repair and run again`

## Scope

This authorizes one engineering repair cycle for the concrete clip-start weakness discovered by hardened run `34938917218`, followed by exactly one new non-authoritative EGFxSet diagnostic if and only if the prospectively frozen synthetic gates below pass.

It does not authorize V143/Gomyway, official correctness, real calibration/holdout work, threshold tuning from the real result, alternate candidates, or repeated real retries.

The real diagnostic will reuse the immutable Basic Pitch output from repaired run `34936227380`; Basic Pitch will not be invoked again.

Frozen real inputs remain:

- EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`
- archive MD5 `cdb1b401960f56becc8640387910e78a`
- member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- member bytes `722976`
- immutable prior artifact `10383413992`
- prior artifact ZIP SHA-256 `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- immutable `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256 `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- raw proposals remain exactly MIDI `[40,68]`

## Concrete defect being repaired

The V1 wrapper fabricated missing clip-start pre-context with zero padding. The genuine MIDI-40 proposal at about 11.6 ms then received a hard negative from the inherited pre/post onset-birth classifier. Synthetic zero padding is not genuine physical pre-onset evidence and must not own a hard clip-start decision.

The historical V1 result remains frozen FAIL and is never rewritten.

## V2 qualification policy — prospectively frozen

### Normal in-clip proposals

When the proposal onset has at least the inherited required genuine left context (`3584` samples at 44.1 kHz), use the existing V6 complex-harmonic onset-birth classifier unchanged. No V6 threshold or DSP constant changes.

### Clip-start proposals

When the proposal onset is earlier than `3584` analysis samples, do **not** zero-pad and do **not** run the pre/post birth classifier. Use a separate one-sided clip-start pitch-presence classifier on genuine post-onset audio only.

Frozen clip-start algorithm:

1. analysis sample rate remains `44100 Hz`;
2. take exactly `8192` genuine samples beginning at the proposal onset; `8192` is the already-frozen V6 FFT size;
3. if those real post-onset samples are unavailable, return `insufficient` — no right padding;
4. demean the frame, apply a Hann window, and compute an `8192`-point real FFT magnitude spectrum;
5. inherit unchanged V6 constants: playable MIDI `40..88`, maximum `6` harmonics, minimum analysis RMS `1e-5`, minimum feature energy `1e-6`, fundamental-to-max-harmonic template ratio `0.20`, and necessity fraction minimum `0.01`;
6. build the same physical harmonic candidate templates over MIDI `40..88` against the post-onset magnitude spectrum;
7. fit the complete template dictionary by non-negative least squares, then remove the selected candidate and recompute residual; selected-candidate necessity is `(residual_without_selected - full_residual) / feature_energy`;
8. detect possible lower-fundamental harmonic owners for harmonics `2..6`: a lower valid MIDI owns the selected pitch when the selected MIDI is within `±50 cents` of that lower MIDI's harmonic, the lower candidate has positive fitted coefficient, lower necessity is at least `0.01`, and lower necessity is greater than or equal to the selected candidate necessity;
9. clip-start proposal is `corroborated` only when its template is physically valid, its fitted coefficient is positive, its necessity is at least `0.01`, and no dominant lower harmonic owner exists;
10. otherwise a finite, adequately supported clip-start fit is `rejected`; missing real post-context, low audio support, numerical failure, or other unavailable evidence is `insufficient`.

Basic Pitch candidate confidence remains diagnostic-only and is never read for either normal or clip-start decisions.

This V2 algorithm is general by MIDI/harmonic relationships; there is no special case for MIDI 40, MIDI 68, EGFxSet, the expected string/fret label, or the observed confidence values.

## Synthetic gate before any new EGFxSet execution

The exact V2 code must pass synthetic/non-real fixtures before the real diagnostic is allowed to proceed:

- ordinary in-clip E2 birth corroborates while a later fifth-harmonic proposal is rejected;
- reversing Basic Pitch candidate confidences leaves decisions unchanged;
- clip-start genuine single-note proposals across multiple MIDI values (including values other than 40) corroborate;
- on clip-start E2 audio, harmonic aliases including octave MIDI 52 and fifth-harmonic-area MIDI 68 reject while MIDI 40 corroborates;
- a strong genuine clip-start harmonic-interval polyphony fixture must not be rejected merely because one note is also a harmonic of another when the selected note has greater independent necessity;
- noise-only clip-start proposals do not corroborate;
- unavailable real post-context remains `insufficient`;
- V2 exact identity/population builder rules remain fail-closed.

If any synthetic gate fails, no EGFxSet V2 diagnostic executes until the software repair is corrected prospectively. Synthetic repair iterations do not authorize threshold tuning from real EGFxSet observations.

## Exactly one real V2 diagnostic after synthetic PASS

After all synthetic gates pass, execute exactly one real-media V2 diagnostic with:

`exact EGFxSet WAV + immutable prior Basic Pitch JSON -> V2 boundary-aware qualifier -> V2 exact-identity evidence builder -> adapter/evaluator -> deterministic position check`

No Basic Pitch invocation, reference-tab lookup, waveform listening, manual event deletion, confidence thresholding, candidate substitution, or retry.

Frozen diagnostic PASS requires all of:

- exact input identities pass;
- raw proposal MIDI list remains exactly `[40,68]`;
- MIDI 40 qualification = `corroborated`;
- MIDI 68 qualification = `rejected`;
- `insufficientCount == 0`;
- promoted MIDI list exactly `[40]`;
- rejected preserved MIDI list exactly `[68]`;
- promoted MIDI 40 has exactly one standard-tuning position: string 6 / fret 0 / reconstructed MIDI 40.

Any other observation is a frozen diagnostic FAIL. No same-authorization retry follows.

## Authority effects

Regardless of result, keep:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The historical V1 all-events and hardened-boundary results remain immutable historical FAILs.