# Songsterr Fresh — Model-Evidence Admission Research Preregistration V2

Status: preregistered successor research plan; **not an admission authority**

Recorded: 2026-09-11 America/Toronto

## Why V2 exists

Independent Corroboration V1 remains frozen as a research diagnostic and is rejected as customer-admission authority. V2 is a new contract, not a patch to V1.

The authorized-song V1 result, including the historical MIDI-55 and MIDI-64 stress diagnostics, MUST NOT be used to tune V2 constants, thresholds, competitor definitions, channel logic, or controlled-fixture expectations. Those song observations are retrospective evaluation history only.

V2 is derived from independent signal-processing principles:
- a candidate pitch should exhibit a coherent harmonic series anchored by energy inside that MIDI pitch class's semitone cell; and
- a candidate fundamental period should be supported in the time domain without being equally well explained by its half-period/octave-up periodicity.

## Hard scope and allowed inputs

V2 remains:
- reference-blind with respect to any tab/transcription reference for the authorized song;
- independent of archived V143/Gomyway/GOAT implementation and all reference/professional scorer logic;
- independent of Basic Pitch activation values, onset/decision surfaces, note-span amplitude/confidence, and decoded note ends;
- duration-free;
- event-identity preserving;
- non-promotional until a later explicit policy review.

The evaluator may consume only:
- the exact isolated-guitar WAV already bound to upstream model evidence;
- each candidate event's existing `selectedMidi` and `sourceStart`;
- frozen structure identity and bound stem/evidence identities for provenance only.

It may not consume duration evidence, downstream rendering/customer output, reference tabs, historical scorer output, or any authorized-song-derived tuning parameter.

## Frozen shared constants

- sample rate: exactly `44100 Hz`
- analysis window: exactly `16384` samples beginning at rounded `sourceStart * 44100` (`floor(x + 0.5)`), approximately `0.37151927437641723 s`
- playable MIDI range: `40..88` inclusive
- competitor offsets: `{-12, -7, -2, -1, +1, +2, +7, +12}` with out-of-range values omitted
- competitor rationale: adjacent semitone/tone ambiguity plus octave and perfect-fifth harmonic confusions; this set is frozen before authorized-song execution
- demeaned RMS below `1e-4` => `insufficient-evidence`; this is inherited unchanged as a low-support numerical guard and is not derived from the authorized song
- no substantive score-margin threshold is allowed; winner tests use strict `>` and exact equality fails closed
- any non-finite channel score fails closed
- no next onset, note end, inferred duration, or same-pitch reattack may alter the fixed window

## Channel A — coherent semitone-cell harmonic product

Purpose: require the selected MIDI to have a coherent spectral harmonic pattern anchored by an actual fundamental-region peak, rather than allowing unrelated harmonics to be collected independently.

For the fixed analysis window:
1. subtract the arithmetic mean;
2. multiply by `numpy.hanning(16384)`;
3. compute `rfft` with fixed FFT size `32768`;
4. use magnitude, not power;
5. normalize magnitudes by their full-spectrum sum; zero total magnitude is insufficient evidence.

For each candidate MIDI `m`:
1. define its fundamental semitone cell as frequencies from MIDI `m-0.5` inclusive to `m+0.5` exclusive;
2. among FFT-bin center frequencies inside that cell, choose the bin with maximum normalized magnitude; ties choose the lower-frequency bin deterministically;
3. call that bin-center frequency `f_hat`;
4. for harmonics `h = 1..4`, sample the maximum normalized magnitude over the nearest FFT bin to `h * f_hat` plus its immediate left/right neighbors;
5. floor each sampled normalized magnitude to `1e-15` only to keep the logarithm finite;
6. Channel-A score is the arithmetic mean of the four natural-log sampled magnitudes, i.e. the log of a four-harmonic geometric-mean salience.

All four harmonics remain below Nyquist throughout MIDI 40..88. No candidate-specific weights, learned calibration, Basic Pitch values, or authorized-song-derived threshold enter this score.

The selected MIDI is Channel-A unique best only when its score is strictly greater than every in-range competitor score.

## Channel B — octave-disambiguated YIN/CMND competition

Purpose: provide an independent time-domain periodicity view and explicitly penalize octave-down candidates whose apparent period is already strongly explained by the half-period.

For the same demeaned fixed window:
1. compute the standard squared-difference function `d(tau) = sum_t (x[t] - x[t+tau])^2` for integer lags required to cover the complete MIDI-40 semitone cell;
2. convert it to the cumulative-mean normalized difference function (CMND), with `CMND(0)=1` and standard cumulative normalization for positive lags;
3. for candidate MIDI `m`, map its semitone cell `[m-0.5, m+0.5)` to the corresponding inverse-frequency lag interval;
4. among integer lags whose implied frequency lies in that cell, choose the lag with minimum CMND; ties choose the lag nearest the equal-tempered center period, then the smaller lag;
5. linearly interpolate CMND at half that chosen lag;
6. Channel-B score is `CMND(tau/2) - CMND(tau)`; higher is better.

This score rewards a candidate period whose CMND minimum is better than its half-period explanation. It does not use a learned YIN threshold, a Basic Pitch threshold, or any margin fitted from the authorized song.

The selected MIDI is Channel-B unique best only when its score is strictly greater than every in-range competitor score.

## Frozen V2 classification rule

Allowed research labels only:
- `independently-corroborated-candidate`
- `not-independently-corroborated`
- `insufficient-evidence`

Classification:
- low RMS, unavailable fixed window, empty/invalid spectral cell, invalid CMND support, or any non-finite required score => `insufficient-evidence`;
- selected MIDI strict unique best in **both** Channel A and Channel B => `independently-corroborated-candidate`;
- otherwise => `not-independently-corroborated`.

Channel disagreement always fails closed. No 2-of-N voting, confidence averaging, fallback channel, score-margin fitting, or event deletion is permitted.

## Controlled-fixture suite required before any authorized-song run

The implementation must deterministically generate and commit exact PCM16 fixture identities before authorized-song evaluation. The minimum frozen fixture families are:

Positive / expected corroborated:
1. standard plucked-like MIDI 40;
2. standard plucked-like MIDI 64;
3. standard plucked-like MIDI 88;
4. MIDI 64 detuned +35 cents but still inside its MIDI semitone cell;
5. MIDI 52 detuned -35 cents but still inside its MIDI semitone cell;
6. MIDI 64 with a deterministic short attack-noise transient added to the same pitched body.

Negative / expected not corroborated:
7. selected MIDI 52 while the signal is a clean MIDI-64 octave-up tone;
8. selected MIDI 64 while the signal is a clean MIDI-52 octave-down tone;
9. selected MIDI 52 with deliberately dominant second harmonic and only weak fundamental support;
10. selected MIDI 60 with a stronger MIDI-61 neighboring-semitone component;
11. selected MIDI 60 with a stronger MIDI-67 perfect-fifth component;
12. selected MIDI 60 in an equal MIDI-60/MIDI-61 dyad;
13. selected MIDI 60 in a deterministic clustered/polyphonic mixture where competing pitch support prevents two-channel unique-best corroboration.

Insufficient-evidence:
14. exact silence;
15. fixed-seed very-low-level broadband noise below the inherited RMS guard.

The exact generator constants, seeds, PCM conversion, and SHA-256 identities must be committed with the implementation. If any preregistered expected classification fails, V2 must **not** be adjusted in place after inspecting the authorized song; any method change requires a new preregistration version before authorized-song evaluation.

Additional contract tests must prove:
- strict score ties fail closed;
- duration-bearing upstream evidence is rejected;
- unavailable/truncated fixed windows return insufficient evidence rather than borrowing later note timing;
- event MIDI and onset identity are never rewritten;
- all promotion guards remain false/zero.

## Public validation boundary

No public audio corpus is authorized by this V2 preregistration. The initial V2 implementation/CI may use only deterministic controlled fixtures and contract tests.

If a public validation corpus is later added, its exact dataset version, license/right-to-use basis, file subset, annotation interpretation, sampling protocol, metrics, and acceptance policy must be preregistered in a new version **before** viewing those validation results. Public-corpus results may not be mixed into V2 post hoc.

## CI and authorized-song execution boundary

Hosted CI may run only controlled fixtures and contract/self-tests. It must not evaluate the authorized song.

The authorized song may be evaluated with V2 only after:
1. V2 implementation and fixture manifest are frozen in branch commits;
2. controlled-fixture/contract CI is green;
3. hard non-promotion guards are green;
4. a **new** Policy C-S Codespaces epoch is enrolled on the exact frozen source commit;
5. that epoch passes three exact qualification canaries.

No previous C-S epoch may be reused or reinterpreted for V2.

## Promotion boundary

Even a green controlled suite, green C-S qualification, and a completed authorized-song V2 research run do **not** automatically authorize customer output.

A separate explicit policy review is mandatory. The previously observed MIDI-55/MIDI-64 song cases may be inspected only after the frozen V2 authorized-song run and only as retrospective stress diagnostics; they may not change V2 under the same preregistration.

Until a later policy review independently authorizes promotion:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research remains paused
