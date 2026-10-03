# Go My Way Three-Role Professional Failure Anatomy V1

Date: 2026-10-03
Branch: `astra-work`

## Purpose

Explain why the frozen current-pipeline predictions fail the professional scorer without tuning or rerunning any model.

For each professional target, inspect predictions within the same fixed 50 ms onset window and classify whether an exact pitch, octave-related pitch, nearby pitch, harmonic relation, other pitch, or no prediction is available.

This is reference-centered diagnostic availability, not a replacement for the one-to-one F1 score.

## Aggregate - 1,965 targets

- no prediction within 50 ms: **1,183 / 1,965 = 60.20%**
- exact MIDI available: **131 = 6.67%**
- same pitch class / wrong octave: **77 = 3.92%**
- within +/-1-2 semitones: **120 = 6.11%**
- fourth/fifth-class harmonic relation: **217 = 11.04%**
- other wrong pitch only: **237 = 12.06%**

This demonstrates two simultaneous bottlenecks:
1. many professional attacks are not represented by any nearby Basic Pitch event;
2. when a nearby event exists, pitch identity is often wrong.

## Rhythm

Targets: **971**

- no nearby prediction: **58.60%**
- exact MIDI available: **3.71%**
- octave-related: **5.25%**
- near +/-1-2 semitones: **3.50%**
- fourth/fifth relation: **14.01%**
- other wrong pitch: **14.93%**

Register:
- professional median MIDI: **55**
- prediction median MIDI: **62**
- professional P90: **64**
- prediction P90: **69**
- prediction max: **101**

The generic guitar transcription is substantially biased upward relative to the rhythm part.

Most common nonzero pitch relations include +7, +12, +19 and +/-5 semitones, consistent with strong harmonic/register confusion.

## Lead

Targets: **447**

- no nearby prediction: **59.06%**
- exact MIDI available: **9.84%**
- octave-related: **4.70%**
- near +/-1-2 semitones: **5.59%**
- fourth/fifth relation: **10.74%**
- other wrong pitch: **10.07%**

Register:
- professional median MIDI: **64**
- generic guitar prediction median: **62**

The generic guitar stream is much closer in register to lead than rhythm, consistent with the higher lead exact recall.

## Bass

Targets: **547**

- no nearby prediction: **63.99%**
- exact MIDI available: **9.32%**
- octave-related: **0.91%**
- near +/-1-2 semitones: **11.15%**
- fourth/fifth relation: **6.03%**
- other wrong pitch: **8.59%**

Register:
- professional median MIDI: **38**
- bass prediction median MIDI: **40**
- professional P90: **41**
- bass prediction P90: **50**

Bass is not dominated by octave confusion. Its separator/transcriber output has an overly high upper register and substantial near-semitone errors.

## Interpretation

This professional benchmark changes the immediate research priority.

The dominant end-to-end problem is not safe duplicate consolidation. It is the **note front end itself**:
- attack recall is poor;
- pitch identity is poor even when attacks are nearby;
- rhythm suffers a strong high-register/harmonic bias;
- bass separation does not currently improve exact professional-tab score.

The next useful work should compare or improve note-evidence extraction using the frozen full-song prediction/reference contract, while leaving separator output untouched.

## GitHub Actions evidence

Run:
`37095293247` - **success**

Head:
`bedb64979c67a812dfb836d32a592be1ca921080`

Artifact:
- id: `11264455653`
- digest: `sha256:c01753615a1caf6b3294d16321fd1fdbfbde01576fbdd5db114ca1f1de63f1fa`
