# Open-Corpus V4 GuitarSet Discovery Family — Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose and timing

This checkpoint is frozen **after** the preregistered `02/04` event-level discovery result was observed and **before** any exact multi-event scoring of a V4 family and before any player `05` V4 reference use.

The discovery result is frozen at:
- report SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`;
- labeled rows SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`;
- artifact ID `9829078706`, ZIP SHA256 `2f7353b3bd82cd3d0dc5db08bcc0490656defb956e55c1a7da3cd6a0f5b4eff1`.

This is a new V4 hypothesis family, not a recovery or weakening of V3.

## Discovery evidence used to formulate the family

The full discovery population showed ordinary-V2 octave changes are overwhelmingly harmful, especially octave-up changes.

A conservative reference-blind pocket appeared only in **high-register octave-down proposals on short Basic Pitch events**. In the frozen labeled rows, the rule:
- V2 direction = octave-down;
- baseline MIDI pitch >= 72;
- duration <= 0.35 s;

selected 157 discovery events with primary one-event labels:
- beneficial 11;
- neutral 146;
- harmful 0;
- net delta TP +11.

The same rule had nonnegative/positive primary net delta TP in both discovery players (`02`: +1, `04`: +10), and strict50 net delta TP +12 (`02`: +1, `04`: +11).

Nearby nested duration cutoffs 0.25 and 0.30 s also had zero harmful primary one-event labels, so the family below is deliberately limited to those three monotonic duration thresholds. No amplitude, style, track identity, player identity, pitch class, or learned opaque model is admitted.

## Frozen V4 discovery family

Every config applies only when all conditions hold:
1. frozen trigger observation has `triggerEligible == true`;
2. frozen ordinary V2 proposal differs from baseline;
3. ordinary V2 winner is exactly `baselinePitch - 12` (octave-down only);
4. `baselinePitch >= 72`;
5. frozen Basic Pitch event duration `end - start` is <= the config duration threshold.

Configs:
- `H72-D025`: duration <= **0.25 s**;
- `H72-D030`: duration <= **0.30 s**;
- `H72-D035`: duration <= **0.35 s**.

For selected events, only pitch changes to the already-frozen `ordinaryV2Winner`; onset, end, amplitude, event identity and event count remain unchanged. All nonselected events retain baseline pitch.

No additional thresholds may be added to this family after exact discovery-family scoring. No 0.40 s config is included because it added events without improving the frozen primary one-event net signal relative to 0.35 s.

## Frozen exact discovery-family scoring

Exact scoring will use only discovery players `02/04`, the immutable V3 candidate artifact, and the unchanged V3 exact-pitch one-to-one onset matcher:
- primary tolerance 100 ms;
- secondary tolerance 50 ms.

No audio, Basic Pitch, candidate regeneration, player `05` reference, or prospective player reference is permitted.

For each config, score the complete multi-event stream per track, then aggregate:
- primary macro F1;
- primary combined micro F1;
- primary per-player micro F1 for `02` and `04`;
- strict50 combined micro F1;
- changed-pitch count;
- per-track primary TP delta.

## Frozen discovery-family qualification gate

A config qualifies only if all are true:
1. event-count identity holds for every track;
2. primary macro F1 gain vs baseline is **strictly > 0.00 pp**;
3. primary combined micro F1 gain vs baseline is **strictly > 0.00 pp**;
4. primary player-`02` micro F1 delta is **>= 0.00 pp**;
5. primary player-`04` micro F1 delta is **>= 0.00 pp**;
6. strict50 combined micro F1 delta is **>= 0.00 pp**;
7. no discovery track has primary TP delta < 0.

This gate is intentionally conservative because the event-level hypothesis was zero-harm in the selected pocket. If multi-event interactions create any primary discovery-track TP loss, that config fails.

## Frozen deterministic discovery selection rule

Among qualifying configs, choose exactly one by this order:
1. highest primary combined micro F1 gain;
2. highest primary macro F1 gain;
3. highest strict50 combined micro F1 gain;
4. fewest changed pitches;
5. lexical config ID.

If no config qualifies, V4 closes `NO_V4_DISCOVERY_FAMILY_SIGNAL`; player `05` must remain unread for V4 confirmation.

If one config is selected, that config alone may proceed to a separately preregistered player-`05` one-shot confirmation. The player-05 confirmation gate and scorer must be frozen before any player-05 V4 reference is read.

## Forbidden actions

This family-scoring step must not:
- read player `05` JAMS or compute player-05 V4 labels;
- read `00/01/03` references or audio;
- run Basic Pitch or decode audio;
- regenerate candidates;
- alter V2/V3 code or thresholds;
- change the family after exact discovery-family metrics are observed;
- arm a prospective evaluation;
- modify V168/GOAT policy.

## Counters at preregistration

- exact V4 discovery-family score calls: **0**;
- player `05` V4 reference read: **false**;
- player `05` V4 confirmation score calls: **0**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
