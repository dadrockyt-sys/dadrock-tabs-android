# Astra V2 Stage-A failure analysis — polyphonic pitch metric validity

Date: 2026-09-28  
Status: **FROZEN POST-HOC MEASUREMENT ANALYSIS — ORIGINAL STAGE-A RESULT REMAINS FAILED**

## Frozen Stage-A result

- workflow run **36484128430**
- job **109136731820**
- artifact **10997847232**
- artifact digest `sha256:1e918e7b5a95dc692f5a81761fe7cdcba4b76dd6b34f29a56cc4cec86e8a8343`
- result JSON SHA-256 `5778104fe505f5a38b4e2a0ed3e049a9993db92a9a1a3a078851c6cb7df8e0c2`
- Stage-A scientific admission: **FAIL**

All gates passed except:
- `fundamentalWithin15Cents = false`.

Maximum reported absolute error:
- **205.8039 cents**.

Execution remained within all frozen bounds:
- waveform renders **84**
- synthetic audio **168 s**
- elapsed about **6.04 s**
- models **0**
- inference **false**
- optimizer steps **0**
- P1/P2/P3 **not accessed**
- no automatic retry.

## Localization of the failed metric

The result contains **86 measurable attacked events**.

Events outside ±15 cents:
- **4 / 86**.

All four are in the **chords** family:
1. training row 84, event 4: **-205.8039 cents**
2. training row 84, event 5: **-199.4970 cents**
3. challenge row 120, event 1: **+195.3974 cents**
4. challenge row 120, event 4: **+103.3990 cents**

Every measured non-chord attacked event is inside ±15 cents.

Maximum absolute non-chord error:
- **8.0898 cents**.

Family maximum absolute errors:
- chords: **205.8039 cents**
- isolated: **5.6200**
- legato: **3.5470**
- mixed: **4.9686**
- palmmute: **6.7869**
- repeated: **6.5576**
- scales: **8.0898**

This does not erase the preregistered failure. It localizes it.

## Source-code validity review

### Chord construction is simultaneous polyphony

Both frozen chord constructors create three notes at exactly the same onset time.

S0:
- for each onset time (.32 and 1.08), loop across three selected strings and append three events with the same start/end.

S9 training chord replacement:
- same structure: three strings at .32 and three at 1.08.

Thus each attacked chord event is observed inside a waveform containing two other simultaneously sounding chord components.

### Existing pitch estimator is monophonic-style

Frozen helper:
`_fundamental_cents(audio, freq, start, end)`

It:
1. takes the **mixed rendered waveform** over the sustain window;
2. computes one FFT magnitude spectrum;
3. searches for the **largest spectral peak** in:
   - `freq * 0.85` through `freq * 1.15`;
4. interprets that single winning peak as the target event's fundamental.

The search interval is extremely broad in musical pitch terms:
- upper edge +15% ≈ **+241.96 cents**;
- lower edge -15% ≈ **-281.36 cents**.

A neighboring chord fundamental one or two semitones away therefore lies well inside the target event's search band and can legitimately have greater magnitude in the mixed waveform.

### Failed values are consistent with chord-tone selection

The four failed estimates are about:
- +103 cents;
- +195 cents;
- -199 cents;
- -206 cents.

Those values are close to one- and two-semitone separations and are well inside the estimator's ±15% search band.

This pattern is qualitatively consistent with the largest spectral peak belonging to another simultaneous chord component.

It is not, by itself, evidence that the V2 renderer shifted oscillator frequency by 1–2 semitones.

## Renderer structural evidence

The source-domain renderer derives each event oscillator directly from the frozen pitch label:

`pitch = OPEN_MIDI[string] + fret`

`freq = 440 * 2 ** ((pitch - 69) / 12)`

V2 clip-level source parameters change:
- envelope/attack;
- damping;
- pick position;
- brightness;
- filtering;
- static nonlinear wet mix;
- additive noise/hum.

No V2 manifest parameter changes the oscillator frequency or sample-time basis.

This structural fact is supportive but is **not** used to retroactively override the failed acoustic gate.

## Interpretation

Supported:
- Stage-A V1 failed exactly as preregistered.
- The failure is confined to four chord-event pitch measurements.
- The frozen per-event FFT peak estimator is not source-separating and is methodologically confounded for simultaneous polyphony.
- Non-chord acoustic pitch checks all passed with maximum error < 8.1 cents.
- No evidence from this run supports a broad V2 oscillator-frequency corruption.

Not supported:
- declaring the original Stage-A run a pass;
- ignoring the failed chord events;
- continuing to Stage B under the original design;
- lowering the ±15-cent threshold post hoc;
- replacing failed rows.

## Correct next scientific action

Define a **new prospective measurement design version** for polyphonic pitch validity.

It must:
1. leave the failed Stage-A V1 result frozen;
2. keep the ±15-cent monophonic acoustic criterion unchanged where a single source is measurable;
3. avoid assigning one mixed-spectrum maximum to an individual simultaneous chord event;
4. define the polyphonic validity method before any new waveform execution;
5. not use the four failed numerical values to tune thresholds;
6. preserve the exact V2 manifest, renderer equations, sample rows and all non-pitch Stage-A gates unless separately justified.

No Stage B or model work is authorized by this analysis.
