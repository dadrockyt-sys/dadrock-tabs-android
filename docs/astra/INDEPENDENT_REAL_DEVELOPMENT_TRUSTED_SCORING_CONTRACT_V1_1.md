# Independent Real-Development Trusted Scoring Contract V1.1

Date: 2026-09-28  
Status: **FROZEN BEFORE ANY CANDIDATE-MODEL OUTPUT**

## Why V1.1 exists

The original V1 design asked for exhaustive pitch-onset precision/recall/F1 across all positive clips.

Pre-inference QA showed that this would overclaim annotation quality: several clips are chordal/polyphonic, while the model-free draft uses spectral-flux onset detection plus YIN fundamental estimation. YIN is monophonic and cannot prove an exhaustive simultaneous-note reference set.

Rather than guess chord tones, V1.1 narrows the scientific claims **before inference**.

## Frozen populations

### Trusted pitch-landmark population

These 12 clips are retained for exact MIDI pitch-onset landmark scoring:

P01, P03, P04, P05, P08, P09, P11, P12, P14, P15, P17, P18.

Combined frozen evaluation duration: **97.803094 seconds**.

They contribute **84 model-free pitch/onset landmarks**:
- **68 high-confidence**
- **4 medium-confidence**
- **12 low-confidence**

The **primary trusted landmark set** contains only the **72 high+medium-confidence landmarks**.

The 12 low-confidence landmarks remain frozen and may be reported only as a sensitivity analysis.

### Polyphonic/onset-only population

These six clips remain part of the development set but are not used for exact pitch precision/recall claims:

P02, P06, P07, P10, P13, P16.

Combined duration: **47.612 seconds**.

They may be used descriptively for:
- onset/activity behavior;
- prediction density;
- qualitative failure review after the primary frozen metrics are computed.

They must not be scored as exhaustive exact-MIDI pitch references.

### Negative-only population

All six negative clips remain unchanged:

N01–N06, **41.366531 seconds** total.

## Primary V1.1 metrics

1. **Trusted pitch-landmark hit rate**
   - denominator: 72 high+medium frozen landmarks;
   - hit requires an exact MIDI pitch prediction within the frozen onset tolerance used by the evaluator;
   - every landmark contributes at most one hit.

2. **High-confidence landmark hit rate**
   - denominator: 68 high-confidence landmarks;
   - same matching rule.

3. **Negative-only false-positive events/second**
   - all decoded guitar events over all six negative-only clips;
   - numerator and exact duration must be reported.

4. **Per-clip landmark hit rate**
   - report every trusted-pitch clip separately;
   - no aggregate may hide a failed clip.

## Secondary / sensitivity outputs

- all-84-landmark hit rate including low-confidence annotations;
- raw decoded event count per positive clip;
- onset/activity summaries for P02/P06/P07/P10/P13/P16;
- qualitative error review after metrics are frozen;
- exact string/fret scoring remains disabled because fingering is not reliably observable from audio alone.

## Explicitly prohibited claims

V1.1 does **not** support:
- exhaustive positive-set precision;
- exhaustive positive-set recall;
- exhaustive positive-set F1;
- exact string/fret accuracy;
- production readiness;
- a claim that polyphonic chord transcription has been fully measured.

Those claims require a genuinely exhaustive human transcription reference set.

## Why this is scientifically trustworthy

The benchmark now makes only claims that the reference data can support:
- whether the frozen candidate recovers prospectively frozen, independently sourced pitch-onset landmarks;
- whether it hallucinates guitar events on known negative audio;
- how behavior varies clip by clip.

It does not treat missing polyphonic annotations as ground truth negatives.

## Frozen boundaries

- no candidate-model output has been viewed;
- no threshold changed;
- no decoder tuning;
- no retraining;
- no candidate selection;
- no P1/P2/P3;
- no A2;
- no main/Production mutation.

## Readiness

Under this amended, narrower scoring contract, the reference set is scientifically adequate for **one bounded real-development evaluation**.

The original V1 exhaustive pitch precision/recall/F1 objective remains unfulfilled and must not be silently revived.
