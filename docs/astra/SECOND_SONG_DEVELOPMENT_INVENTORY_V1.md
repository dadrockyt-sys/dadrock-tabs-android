# Second-song development inventory V1

Date: 2026-09-21
Branch: `astra-work`
Purpose: determine whether Astra can prospectively validate the frozen Gomyway development rules on a different song without inventing or weakening ground truth.

## Inventory result

No currently available second song combines:

1. audio already authorized/available for development,
2. independent note-level truth suitable for onset + MIDI evaluation,
3. enough timing information to bind that truth to the recording,
4. a scope that is not merely another Gomyway derivative.

## Repository evidence

The repository contains these relevant public audio/reference assets:

- Gomyway audio variants and the professional rhythm/lead/bass reference material.
- `public/Stairway to Heaven AI test.m4a`.

The archived analyzer fixtures contain:

- Gomyway note/bend/separation fixtures.
- `analyzer/fixtures/stairway_intro_reference.json`.

The Stairway fixture is **not a note-level transcription reference**. Its `notes` array is empty. It contains phrase/chord-position expectations such as Am, C/G, D/F#, Fmaj7 and G/B-Am position ranges. That can still be useful for fretboard/fingering regression, but it cannot establish note-onset precision/recall or validate the recurring raw-onset recovery rule.

The archived Stairway baseline is likewise a fingering/position baseline, not independent note-event truth.

## Library evidence

A Library/conversation search for additional reference/audio pairs returned the existing Gomyway development artifacts and no separate song with independently normalized note-level truth.

## Boundary decision

- Do **not** present Stairway as a fresh or locked holdout.
- Do **not** score pitch/onset recovery against its position-only fixture.
- Do **not** reopen archived V143 task queues merely to manufacture a second benchmark.
- The current Gomyway result remains exposed development evidence, not proof of cross-song generalization.

## Consequence

The frozen Gomyway winner remains:

- 118 TP
- 125 FP
- 85 FN
- precision 48.56%
- recall 58.13%
- F1 52.91%

No further Gomyway-specific threshold/rule tuning should be used to claim broader quality.

Until a second user-authorized song with independent note-level truth is supplied, the next quality path is **model/component research**: identify a stronger general pitch/event inference component that can be evaluated under Astra's existing artifact-rights, runtime, CPU-cost, provenance and fail-closed delivery gates.

Stairway may still be used later as an exposed fingering/path regression fixture, but not as note-event ground truth.

No main or Production change is authorized by this inventory.
