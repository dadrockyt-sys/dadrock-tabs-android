# Open-Corpus V5 GuitarSet Cross-Player Development — Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## New methodological boundary

V4 is closed after `H72-D035` failed its one-shot player-`05` confirmation. This checkpoint opens a **new V5 development phase**.

For V5 only, all previously used GuitarSet development players are explicitly treated as development data:
- `02` = development;
- `04` = development;
- `05` = development.

The sole untouched prospective test set remains:
- `00`;
- `01`;
- `03`.

Those prospective players remain completely sealed. No V5 prospective reference or score call is permitted during development.

This boundary is frozen **before player-05 per-event outcomes are mined for V5 rule search**. The earlier V4 player-05 aggregate/track confirmation result is known development history and is not treated as an independent V5 validation set.

## Goal

Develop a small, reference-blind, interpretable octave-down gate that is **player-stable across all three development players**, rather than selecting a rule that succeeds on `02/04` and then hoping it transfers to `05`.

The immutable V3 candidate artifact remains the only prediction/evidence source. No audio decoding, Basic Pitch inference, event regeneration, onset edits, duration edits, or pitch candidates outside the already-frozen ordinary V2 octave proposal are permitted.

## Frozen candidate family

Every V5 config applies only when all conditions hold:
1. frozen trigger observation has `triggerEligible == true`;
2. frozen ordinary V2 proposal differs from baseline;
3. ordinary V2 winner is exactly `baselinePitch - 12` (octave-down only);
4. baseline MIDI pitch is >= the config pitch floor;
5. frozen Basic Pitch event duration `end-start` is <= the config maximum duration;
6. frozen common-frame consensus fraction is **1.00**;
7. frozen median ordinary-winner advantage is >= the config advantage threshold.

Frozen pitch floors:
- **72**;
- **76**;
- **79**.

Frozen maximum durations:
- **0.20 s**;
- **0.25 s**;
- **0.30 s**;
- **0.35 s**.

Frozen median-advantage thresholds reuse existing preregistered V3 threshold values:
- **0.05**;
- **0.10**;
- **0.15**;
- **0.20**.

Consensus is fixed at 1.00 and is not swept.

Total family size: **3 × 4 × 4 = 48 configs**.

Config ID format is deterministic:
`P{pitchFloor}-D{durationHundredths:03d}-M{advantageHundredths:03d}`

Examples:
- `P72-D020-M005`;
- `P76-D030-M010`;
- `P79-D035-M020`.

No amplitude, player, track, style, tempo, pitch class, song identity, or reference-derived feature may enter the gate.

## Frozen exact development scoring

Use all 177 admissible development tracks:
- player `02`: 59;
- player `04`: 58;
- player `05`: 60.

Use the unchanged exact-pitch one-to-one GuitarSet scorer at:
- primary onset tolerance 100 ms;
- strict secondary onset tolerance 50 ms.

For every config, score complete multi-event streams and report:
- combined primary macro F1;
- combined primary micro F1;
- combined strict50 micro F1;
- per-player primary macro F1;
- per-player primary micro F1;
- per-player strict50 micro F1;
- changed-pitch count total and per player;
- positive/neutral/negative primary-TP track counts total and per player;
- event-count identity.

## Frozen V5 development qualification gate

A config qualifies only if **all** conditions are true:
1. event-count identity holds for every track;
2. at least **5 changed pitches in each development player**;
3. combined primary macro F1 gain is **strictly >0.00 pp**;
4. combined primary micro F1 gain is **strictly >0.00 pp**;
5. combined strict50 micro F1 delta is **>=0.00 pp**;
6. each player (`02`, `04`, `05`) has primary micro F1 gain **strictly >0.00 pp**;
7. each player has primary macro F1 delta **>=0.00 pp**;
8. each player has strict50 micro F1 delta **>=0.00 pp**;
9. within each player, the number of negative-primary-TP tracks is **<=** the number of positive-primary-TP tracks.

This gate explicitly values cross-player replication over maximum aggregate gain.

## Frozen deterministic development selection rule

Among qualifying configs, select exactly one in this order:
1. maximize the **worst-player primary micro F1 gain**;
2. maximize combined primary micro F1 gain;
3. maximize combined primary macro F1 gain;
4. maximize the **worst-player strict50 micro F1 gain**;
5. minimize total changed pitches;
6. lexical config ID.

If no config qualifies, V5 closes `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL` and prospective players remain sealed.

If one config qualifies and is selected, immediately freeze that exact config and a separate one-shot prospective-evaluation contract before any `00/01/03` reference is touched.

## Prospective boundary

During V5 development:
- `00/01/03` JAMS must not be downloaded/extracted into the development workspace;
- no prospective audio may be processed;
- prospective evaluation processed=false;
- prospective score calls=0.

The eventual prospective run, if reached, will be the first V5 score on those players and must be treated as one-shot/terminal. Its promotion/pass rule must be frozen before references are read.

## Forbidden actions

Do not:
- call V4 confirmation again;
- reinterpret player `05` as an independent confirmation set for V5;
- add/remove V5 thresholds after real V5 development metrics are observed;
- use player identity as a gate feature;
- inspect prospective `00/01/03` references during development;
- regenerate candidate events or run Basic Pitch;
- mutate V168/GOAT policy.

## Counters at preregistration

- V4 player05 confirmation score calls: **1 / terminal**;
- V5 development score calls: **0**;
- V5 prospective evaluation processed: **false**;
- V5 prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
