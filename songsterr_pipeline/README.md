# Songsterr Fresh Pipeline V1

This directory is a clean, reference-blind deterministic transcription core inspired by public Songsterr product clues already documented in this repository.

It is intentionally isolated from the historical V143/Gomyway experiment stack.

## Design boundary

The fresh core treats these as first-class inputs:

- global musical structure: tempo, time signature, pickup, straight/triplet feel;
- instrument configuration: lead/rhythm/bass role, tuning, capo;
- local note evidence: MIDI pitch + onset events.

The first deterministic pass then:

1. normalizes the conditioning contract;
2. resolves a measure/beat/subdivision grid when structure is explicit;
3. groups near-simultaneous note events into onset clusters;
4. snaps the cluster onset to a pickup-aware musical grid;
5. solves simultaneous MIDI notes as one playable shape with unique strings;
6. preserves every input MIDI event and reports raw transformation metrics.

## What is deliberately not imported

The fresh package does not import the old V143 real-audio canaries, professional/reference graders, rhythm-holdout scorer, correction-plan/sidecar scoring, Jimmy Page payload helpers, optimizer/training code, or legacy candidate replay gates.

Historical values such as `100% pitch / 90.321% onset / 69.004% note-count` are not acceptance criteria here.

## Current invariant tests

The synthetic tests currently check:

- structure + role + tuning + capo serialization;
- pickup-aware measure-grid snapping;
- stable onset clustering without chain-merging unrelated attacks;
- exact MIDI reconstruction from string/fret positions;
- simultaneous-note decoding onto unique strings;
- zero event-count drift and 100% source MIDI preservation;
- rejection of invalid tuning.

Run locally from this directory with:

```bash
npm test
```

No third-party package install is required; tests use Node's built-in test runner.

## Next steps

The next implementation stages should stay deterministic and CPU-only:

1. separate timing projection from rhythm spelling;
2. add beat-boundary-aware ties/rests/syncopation representation;
3. extend simultaneous-shape scoring with ergonomic chord constraints;
4. add phrase-level fretboard path optimization;
5. define transparent reference-free diagnostics for every transformation;
6. only then add a narrow audio-inference adapter.

Do not connect this package to Production, Modal/GPU inference, professional scorers, or legacy V143 acceptance gates merely to continue development.
