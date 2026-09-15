#!/usr/bin/env node

import assert from 'node:assert/strict';

import {
  findPlayableShape,
  findPlayableShapeDetails,
  runDeterministicCore,
} from '../../songsterr_pipeline/index.mjs';

const instrumentConfig = {
  role: 'lead',
  tuningMidi: [40, 45, 50, 55, 59, 64],
  capoFret: 0,
};

const conditioning = {
  structurePrior: {
    tempoBpm: null,
    timeSignature: null,
    pickupBeats: null,
    feel: 'auto',
  },
  instrumentConfig,
};

// Case 1: MIDI 40 can only be played as the open low E under the frozen tuning.
const uniqueDetails = findPlayableShapeDetails([40], instrumentConfig);
assert.equal(uniqueDetails.validShapeCount, 1);
assert.equal(uniqueDetails.best.assignments[0].stringNumberHighToLow, 6);
assert.equal(uniqueDetails.best.assignments[0].fret, 0);
assert.deepEqual(findPlayableShape([40], instrumentConfig), uniqueDetails.best);

const uniqueCore = runDeterministicCore({
  events: [{ start: 0.1, midi: 40 }],
  conditioning,
});
assert.equal(uniqueCore.events[0].midi, 40);
assert.equal(uniqueCore.events[0].shapeResolved, true);
assert.equal(uniqueCore.events[0].shapeCandidateCount, 1);
assert.equal(uniqueCore.events[0].physicalShapeResolved, true);
assert.equal(uniqueCore.events[0].positionSelectionMethod, 'unique-physical-layout');
assert.equal(uniqueCore.events[0].stringNumberHighToLow, 6);
assert.equal(uniqueCore.events[0].fret, 0);

// Case 2: MIDI 64 has multiple playable positions. Preserve the existing preferred
// playable layout, but explicitly refuse to call it physical truth.
const ambiguousSingleDetails = findPlayableShapeDetails([64], instrumentConfig);
assert.ok(ambiguousSingleDetails.validShapeCount > 1);
const ambiguousSingleCore = runDeterministicCore({
  events: [{ start: 0.2, midi: 64 }],
  conditioning,
});
assert.equal(ambiguousSingleCore.events[0].midi, 64);
assert.equal(ambiguousSingleCore.events[0].shapeResolved, true);
assert.equal(ambiguousSingleCore.events[0].shapeCandidateCount, ambiguousSingleDetails.validShapeCount);
assert.equal(ambiguousSingleCore.events[0].physicalShapeResolved, false);
assert.equal(ambiguousSingleCore.events[0].positionSelectionMethod, 'heuristic-preferred-layout');
assert.equal(ambiguousSingleCore.events[0].reconstructedMidi, 64);

// Case 3: simultaneous notes can have multiple complete one-note-per-string layouts.
const chordMidis = [64, 67];
const ambiguousChordDetails = findPlayableShapeDetails(chordMidis, instrumentConfig);
assert.ok(ambiguousChordDetails.validShapeCount > 1);
const chordCore = runDeterministicCore({
  events: [
    { start: 0.3, midi: 64 },
    { start: 0.3, midi: 67 },
  ],
  conditioning,
});
assert.deepEqual(chordCore.events.map((event) => event.midi), chordMidis);
for (const event of chordCore.events) {
  assert.equal(event.shapeResolved, true);
  assert.equal(event.shapeCandidateCount, ambiguousChordDetails.validShapeCount);
  assert.equal(event.physicalShapeResolved, false);
  assert.equal(event.positionSelectionMethod, 'heuristic-preferred-layout');
  assert.equal(event.reconstructedMidi, event.midi);
}

assert.equal(uniqueCore.metrics.physicalShapeResolvedEventCount, 1);
assert.equal(ambiguousSingleCore.metrics.heuristicPreferredEventCount, 1);
assert.equal(chordCore.metrics.physicallyUnresolvedAssignedEventCount, 2);

console.log(JSON.stringify({
  contract: 'songsterr-fresh-physical-position-ambiguity-v1-test',
  status: 'PASS',
  cases: 3,
  uniqueMidi40ShapeCount: uniqueDetails.validShapeCount,
  ambiguousMidi64ShapeCount: ambiguousSingleDetails.validShapeCount,
  ambiguousChordShapeCount: ambiguousChordDetails.validShapeCount,
  preferredPlayableLayoutPreserved: true,
  physicalCertaintySeparated: true,
  exactMidiPreserved: true,
}, null, 2));
