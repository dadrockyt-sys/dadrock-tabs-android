# Songsterr Fresh — Independent Pitch Corroboration Research V2

Status: frozen controlled-research implementation; **not an admission authority**

Recorded: 2026-09-11 America/Toronto

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`

Implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`

Controlled fixtures: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`

## Fixed input boundary

V2 may consume only:
- the isolated-guitar WAV already bound to upstream model evidence;
- each existing event's `sourceStart` and already-selected MIDI identity;
- frozen structure/stem/evidence identities for provenance/binding only.

It does not consume Basic Pitch activations, decision surfaces, note-span amplitude/confidence, decoded note ends, downstream duration evidence, next onset, same-pitch reattack timing, reference tabs, professional scorers, GOAT material, or archived V143/Gomyway scorer logic.

Upstream event identity is never changed or deleted.

## Frozen shared constants

- sample rate: exactly `44100 Hz`
- fixed post-onset analysis window: `16384` samples
- start sample: `floor(sourceStartSeconds * 44100 + 0.5)`
- RFFT size used by Channel A and the linear-autocorrelation implementation: `32768`
- playable MIDI: `40..88`
- competitor offsets: `[-12,-7,-2,-1,+1,+2,+7,+12]`, clipped to playable range
- minimum demeaned window RMS: `1e-4`
- strict score winner: selected score must be strictly `>` every competitor score; exact equality fails closed
- substantive score-margin threshold: **none**

A truncated fixed window is `insufficient-evidence`; the evaluator does not borrow note end, next onset, or reattack timing to resize it.

## Channel A — coherent semitone-cell harmonic product

1. Demean the exact window.
2. Multiply by `numpy.hanning(16384)`.
3. Compute `rfft(..., n=32768)` and magnitude.
4. Normalize magnitude by the full-spectrum magnitude sum.
5. For each candidate MIDI, search that candidate's semitone frequency cell `[m-0.5, m+0.5)` and choose the maximum-magnitude FFT bin; an exact bin tie chooses the lower-frequency bin through first-index `argmax` behavior.
6. Use that one coherent frequency `f_hat` for harmonics 1 through 4.
7. For each harmonic, take the maximum normalized magnitude among the nearest FFT bin and its immediate left/right neighbors.
8. Floor sampled magnitudes only at `1e-15` to keep logarithms finite.
9. Score = arithmetic mean of the four natural-log harmonic magnitudes.

The selected MIDI is Channel-A unique best only when its score is strictly greater than every fixed in-range competitor.

## Channel B — octave-disambiguated YIN/CMND competition

1. Demean the exact window.
2. Compute positive-lag linear autocorrelation by zero-padded FFT; no cyclic lag is used.
3. Construct the standard squared-difference function and cumulative-mean normalized difference (CMND).
4. For each candidate MIDI, search integer lags whose implied frequency lies inside that MIDI semitone cell.
5. Select minimum CMND; ties choose the lag closest to the equal-tempered center period, then the smaller lag.
6. Linearly interpolate CMND at half the selected lag.
7. Score = `CMND(tau/2) - CMND(tau)`; higher is better.

The selected MIDI is Channel-B unique best only when its score is strictly greater than every fixed in-range competitor.

## Frozen classification

Allowed research classifications only:
- `independently-corroborated-candidate`
- `not-independently-corroborated`
- `insufficient-evidence`

Rules:
- both channels strict unique-best selected MIDI => corroborated research candidate;
- channel disagreement or non-unique selected => not independently corroborated;
- low RMS, truncated window, invalid spectral support, invalid CMND support, or non-finite required score => insufficient evidence.

There is no voting, fallback channel, learned calibration, confidence weighting, reference scoring, or customer promotion in this contract.

## Frozen controlled suite

Fixture contract: `songsterr-fresh-independent-pitch-corroboration-fixtures-v2`.

The manifest contains 15 deterministic exact PCM16 WAV identities:
- 6 expected corroborated: low/mid/high plucked-like tones, +35-cent and -35-cent in-cell detuning, deterministic attack-noise robustness;
- 7 expected not corroborated: wrong octave in both directions, dominant-second-harmonic ambiguity, stronger neighboring semitone, stronger perfect fifth, equal close dyad, clustered/polyphonic ambiguity;
- 2 expected insufficient: silence and fixed-seed very-low-level broadband noise.

The evaluator regenerates every fixture and requires the exact committed SHA-256 before accepting the classification assertion.

## Controlled verification already performed before CI wiring

Local controlled-only checks passed before CI was added:
- Python compile;
- 15/15 exact fixture classifications, distribution 6/7/2;
- direct-dot-product versus FFT positive-lag autocorrelation numerical check (maximum absolute difference approximately `1.99e-13` in that deterministic check);
- exact score tie fails unique-best;
- duration-bearing upstream evidence is rejected;
- fixed-window overrun returns insufficient evidence;
- policy boundary remains non-promotional.

No authorized-song evaluation was performed during these checks.

## Promotion / execution boundary

Hosted CI may run only controlled fixtures and contract tests. It must not evaluate the authorized song.

Authorized-song evaluation requires a new Policy C-S epoch enrolled and three-canary qualified on the exact frozen V2 source commit after controlled CI is green.

Even a successful future authorized-song V2 research run does not automatically set customer eligibility. A separate explicit policy review is mandatory.

Until such a review:
- `modelValidationComplete:false`
- customer eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
