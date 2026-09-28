# Astra V2 Stage-A chord fundamental measurement-validity review V1

Date: 2026-09-28  
Status: **MEASUREMENT DEFECT CONFIRMED — NO RERENDER / NO RETRY**

## Scope

Review only the failed `fundamentalWithin15Cents` Stage-A gate using:
- the frozen Stage-A result;
- deterministic template-generation source;
- the existing fundamental estimator source.

No waveform is rerendered. No Stage-A retry occurs. No Stage B or model work occurs.

## Frozen Stage-A outcome

Run:
- workflow **36484128430**
- job **109136731820**
- artifact **10997847232**
- artifact digest `sha256:1e918e7b5a95dc692f5a81761fe7cdcba4b76dd6b34f29a56cc4cec86e8a8343`

Stage A executed:
- **84 waveform renders**
- **168 synthetic audio seconds**
- models loaded **0**
- optimizer steps **0**
- P1/P2/P3 access **none**

All frozen gates passed except:
- `fundamentalWithin15Cents = false`

Maximum reported absolute error:
- **205.8039 cents**

There were **86** measurable attacked-event pitch checks.
Exactly **4** exceeded ±15 cents.
All four were chord events.
Maximum absolute non-chord error was **8.0898 cents**.

## Existing estimator

The frozen helper `_fundamental_cents`:
1. extracts one mixed waveform window from the full rendered clip;
2. computes one FFT magnitude spectrum;
3. searches frequencies from **0.85 × target frequency to 1.15 × target frequency**;
4. reports the strongest spectral peak in that band as the target note's fundamental.

This is not a source-separated estimator.

For simultaneous chord notes, another note fundamental or harmonic can be the strongest peak inside the target band.

## Exact failed chord cases

### Train row 84 — S9 chord slot 0, second attack

Simultaneous MIDI pitches:
- event 3: **54**
- event 4: **56**
- event 5: **68**

Failed measurements:
- event 4, target MIDI 56: **-205.8039 cents**
- event 5, target MIDI 68: **-199.4970 cents**

Interpretation:
- for target MIDI 56, simultaneous MIDI 54 is two semitones below and lies inside the ±15% search band;
- for target MIDI 68, the second harmonic of simultaneous MIDI 54 is MIDI 66, two semitones below target and lies inside the same target search band.

Thus the FFT maximum can select a real simultaneous chord component rather than the target note.

### Challenge row 120 — chord base 12

First attack simultaneous MIDI pitches:
- event 0: **55**
- event 1: **57**
- event 2: **59**

Failed:
- event 1, target MIDI 57: **+195.3974 cents**

The reported displacement is essentially the simultaneous MIDI-59 component, two semitones above target.

Second attack simultaneous MIDI pitches:
- event 3: **53**
- event 4: **64**
- event 5: **65**

Failed:
- event 4, target MIDI 64: **+103.3990 cents**

The displacement is essentially the simultaneous MIDI-65 component, one semitone above target.

## Why this is a measurement defect

The renderer generates each chord as multiple labeled sinusoidal/harmonic note components summed into one waveform.

The existing estimator observes only the mixture and has no mechanism to isolate the target event.

All four out-of-tolerance cases have an explicit simultaneous competing spectral component at approximately the reported displaced pitch.

All non-chord selected measurements remain within the frozen ±15-cent tolerance.

Therefore the Stage-A failure establishes:
- the current **polyphonic measurement procedure is invalid for the intended per-note fundamental-preservation gate**.

It does **not** establish:
- that the source renderer shifted chord note fundamentals;
- that the V2 source-domain parameters caused pitch corruption;
- that the ±15-cent tolerance itself is too strict.

## Corrective principle

Do not weaken the ±15-cent threshold.

Instead, a corrected validation must make the pitch-preservation measurement **source-isolating by construction**.

The cleanest model-free correction is to validate the renderer at the individual component level before summation:
- for each note event, render or inspect the deterministic note component using the exact same frozen per-note parameters;
- apply the same clip-level coloration/nonlinearity only if the check can still isolate that note unambiguously;
- otherwise perform the pitch check immediately before mixture-wide nonlinear processing and separately verify that the mixture processing does not alter time/frequency axes.

No correction may:
- alter the V2 manifest;
- alter waveform equations;
- change the ±15-cent tolerance;
- change selected Stage-A rows;
- use model scores;
- use P1/P2/P3.

## Decision

The frozen Stage-A scientific result remains a **failed admission under the original measurement contract**.

However, the only failing gate is now shown to be confounded by a non-source-separating chord estimator.

Next justified work is **offline design only** for a corrected source-isolating fundamental-preservation measurement protocol.

Do not rerun Stage A yet.
