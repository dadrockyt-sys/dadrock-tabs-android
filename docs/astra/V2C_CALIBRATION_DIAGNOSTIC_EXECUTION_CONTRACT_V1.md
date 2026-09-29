# V2C Calibration Diagnostic Execution Contract V1

Date: 2026-09-28  
Status: **FROZEN BEFORE V2C MODEL OUTPUT**

## Inputs

Use only the frozen V2B calibration-development set and annotations.

Candidate:
- S9 30-voicing intervention
- checkpoint SHA-256 `8428e7ced49331153e5bd3a038115235c06aac483dab6f82fbc0257d07dd5036`

V1.1 remains sealed and must not be read for threshold selection.

## Raw diagnostics at historical thresholds

At state/onset thresholds 0.50/0.50, record:
- active-state maximum probability at each trusted pitch landmark;
- silence probability for the corresponding candidate string/pitch states where representable;
- maximum onset sigmoid compatible with the landmark pitch;
- fraction failing state admission only;
- fraction failing onset admission only;
- fraction failing both;
- decoded event density per clip;
- negative-only decoded events/sec.

These are diagnostic outputs, not tuning targets by themselves.

## Frozen finite threshold grid

State threshold:
- 0.20
- 0.30
- 0.40
- 0.50

Onset threshold:
- 0.20
- 0.30
- 0.40
- 0.50

Exactly 16 pairs. No extra thresholds may be added after output is viewed.

## Frozen selection rule

A threshold pair is **eligible** only if:

- aggregate negative-only false-positive rate <= **0.10 events/second**.

Among eligible pairs:
1. maximize high+medium trusted pitch-landmark hit rate;
2. tie-break by lower negative-only false-positive event count;
3. then choose the higher state threshold;
4. then choose the higher onset threshold.

If no pair meets the negative-FP constraint, V2C returns **no calibration candidate**.

The selected V2C pair is only a calibration-development result. It is not validated until a fresh V2D holdout confirms it.

## Claims

Allowed:
- calibration-development diagnostics;
- whether a finite threshold pair materially restores landmark admission;
- whether restoration is compatible with the frozen negative-FP constraint.

Not allowed:
- product readiness;
- validated improvement;
- V1.1 improvement;
- threshold confirmation on the same V2B set;
- architecture conclusions.

## Boundaries

No training, fine-tuning, decoder change, frontend change, gain change, candidate reselection, P1/P2/P3, A2, main, or Production mutation.
