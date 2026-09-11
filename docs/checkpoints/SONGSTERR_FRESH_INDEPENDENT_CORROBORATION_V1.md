# Songsterr Fresh — Independent Pitch Corroboration Research V1

Status: frozen research implementation; **not an admission authority**

This document records the exact implementation frozen before any authorized-song evaluation. It implements the preregistered plan in `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`.

## Fixed input boundary

The research method may consume only:
- the isolated-guitar WAV already bound to upstream model evidence;
- each existing event's `sourceStart` and already-selected MIDI identity;
- frozen structure identity for provenance/binding only.

It does **not** consume Basic Pitch activations, Basic Pitch decision surfaces, Basic Pitch note-span amplitude/confidence, decoded Basic Pitch note ends, downstream duration evidence, reference tabs, professional scorers, or archived V143/Gomyway scorer logic.

Upstream event identity is never changed or deleted by this research output.

## Frozen audio window

- sample rate: exactly `44100 Hz`; any other rate fails closed
- window: `8192` samples, approximately `0.18575963718820862 s`
- start sample: `floor(sourceStartSeconds * 44100 + 0.5)`
- stereo/multichannel input: arithmetic mean to mono
- insufficient remaining samples: `insufficient-evidence`
- fixed minimum demeaned window RMS: `1e-4`

## Fixed competitor set

For selected MIDI `m`, compare against the in-range members of:

`m + {-12, -2, -1, +1, +2, +12}`

Playable range is fixed to MIDI `40..88` inclusive.

## Channel A — harmonic-stack spectral competition

- subtract window mean
- Hann window: `numpy.hanning(8192)`
- real FFT size: `8192`
- power spectrum: `abs(rfft)^2`
- candidate harmonic frequencies: integer harmonics 1 through 5
- harmonic weights: `[1.0, 0.75, 0.5, 0.35, 0.25]`
- sample power at each harmonic with linear interpolation between adjacent FFT power bins
- harmonic contribution: `log1p(power)`
- candidate score: weighted mean over available harmonics below Nyquist

## Channel B — time-domain periodicity / subharmonic competition

For candidate period `T = 44100 / frequency(selectedMidi)`:
- normalized autocorrelation is the dot product at a lag divided by the geometric mean of the two lagged segment energies;
- fractional lags use linear interpolation between adjacent integer-lag normalized autocorrelations;
- candidate score is `NAC(T) - max(0, NAC(T/2))`.

The `T/2` penalty is frozen before authorized-song evaluation and exists to penalize candidates whose apparent periodic support is better explained by a pitch one octave above. This calculation is independent of Channel A's FFT/harmonic-stack path.

## Frozen corroboration rule

- selected MIDI must be the unique best candidate in **both** channels;
- selected-minus-best-competitor margin must be strictly greater than `1e-6` in each channel;
- exact or numerically unresolved ties fail closed;
- channel insufficiency fails closed;
- disagreement between channels returns `not-independently-corroborated`;
- low RMS or unavailable fixed window returns `insufficient-evidence`.

Allowed research classifications only:
- `independently-corroborated-candidate`
- `not-independently-corroborated`
- `insufficient-evidence`

These labels are not customer admission decisions.

## Controlled fixture suite

Fixture manifest: `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`.

The committed suite contains nine exact PCM16 WAV identities generated deterministically by the implementation:
- three clean plucked-like monophonic positives spanning low/mid/high playable MIDI;
- one strong-second-harmonic octave-confusion negative;
- one stronger-neighboring-semitone adversarial negative;
- one close-semitone dyad negative;
- one semitone-cluster triad negative;
- silence and fixed-seed low-noise insufficient-evidence cases.

The generator must reproduce every committed WAV SHA-256 exactly before classification assertions are accepted.

## Promotion boundary

A green controlled-fixture suite proves only that the frozen research contract behaves as preregistered on controlled signals. It does **not** imply model correctness on the authorized song and does not authorize customer output.

Until a later explicit policy review:
- `modelValidationComplete:false`
- customer eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research remains paused

Authorized-song evaluation requires a new Policy C-S epoch enrolled and qualified on the exact frozen implementation commit. The prior qualified epoch at `b2f246769340e4f7f6929e679692956c731efd93` must not be reused or reinterpreted for this code.
