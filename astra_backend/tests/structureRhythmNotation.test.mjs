import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { buildStructureMap } from '../structureMap.mjs';
import { buildStructureMappedEventSchema } from '../structureRhythmNotation.mjs';

function instrument(role = 'lead') {
  return {
    role,
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 0,
  };
}

function straightMap({ durationSeconds = 4, pickupDurationSeconds = 0 } = {}) {
  return buildStructureMap({
    durationSeconds,
    pickupDurationSeconds,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.95 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.98 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.9 }],
    provenance: { source: 'structure-rhythm-fixture' },
  });
}

test('structure-mapped notation ties a pickup note across the explicit pickup-to-measure boundary', () => {
  const result = buildStructureMappedEventSchema({
    structureMap: straightMap({ durationSeconds: 3, pickupDurationSeconds: 0.5 }),
    instrumentConfig: instrument(),
    events: [{ start: 0.375, end: 0.625, midi: 64 }],
  });

  const event = result.events[0];
  assert.equal(event.notation.segments.length, 2);
  assert.equal(event.notation.segments[0].measureNumber, 0);
  assert.equal(event.notation.segments[0].pickup, true);
  assert.equal(event.notation.segments[0].end, 0.5);
  assert.equal(event.notation.segments[1].measureNumber, 1);
  assert.equal(event.notation.segments[1].pickup, false);
  assert.equal(event.notation.segments[1].start, 0.5);
  assert.equal(result.metrics.countDelta, 0);
});

test('syncopated attack near a beat boundary snaps to the map subdivision and reports quantization displacement', () => {
  const result = buildStructureMappedEventSchema({
    structureMap: straightMap(),
    instrumentConfig: instrument(),
    events: [{ start: 0.371, duration: 0.25, midi: 64 }],
  });

  const event = result.events[0];
  assert.equal(event.projectedStart, 0.375);
  assert.ok(Math.abs(event.onsetDisplacementSeconds - 0.004) < 1e-9);
  assert.equal(event.notation.syncopatedStart, true);
  assert.equal(result.metrics.syncopatedEventCount, 1);
  assert.ok(result.metrics.onsetDisplacement.maxAbsSeconds > 0);
});

test('straight and triplet structure maps produce different timing projections from the same raw attack', () => {
  const straight = straightMap({ durationSeconds: 2 });
  const triplet = buildStructureMap({
    durationSeconds: 2,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'triplet' }],
  });

  const raw = [{ start: 0.17, duration: 0.2, midi: 62 }];
  const straightResult = buildStructureMappedEventSchema({
    structureMap: straight,
    instrumentConfig: instrument(),
    events: raw,
  });
  const tripletResult = buildStructureMappedEventSchema({
    structureMap: triplet,
    instrumentConfig: instrument(),
    events: raw,
  });

  assert.equal(straightResult.events[0].projectedStart, 0.125);
  assert.ok(Math.abs(tripletResult.events[0].projectedStart - (1 / 6)) < 1e-9);
  assert.notEqual(straightResult.events[0].projectedStart, tripletResult.events[0].projectedStart);
});

test('structure-mapped duration crossing a measure boundary becomes tied segments without event duplication', () => {
  const result = buildStructureMappedEventSchema({
    structureMap: straightMap({ durationSeconds: 4 }),
    instrumentConfig: instrument(),
    events: [{ start: 1.875, duration: 0.25, midi: 59 }],
  });

  const event = result.events[0];
  assert.equal(result.events.length, 1);
  assert.equal(event.notation.segments.length, 2);
  assert.equal(event.notation.segments[0].measureNumber, 1);
  assert.equal(event.notation.segments[0].end, 2);
  assert.equal(event.notation.segments[1].measureNumber, 2);
  assert.equal(event.notation.segments[1].start, 2);
  assert.equal(result.metrics.tiedEventCount, 1);
  assert.equal(result.metrics.countDelta, 0);
});

test('structure-mapped silence becomes rest diagnostics and never fake MIDI events', () => {
  const result = buildStructureMappedEventSchema({
    structureMap: straightMap(),
    instrumentConfig: instrument(),
    events: [
      { start: 0, duration: 0.25, midi: 64 },
      { start: 0.75, duration: 0.25, midi: 67 },
    ],
  });

  assert.equal(result.events.length, 2);
  assert.equal(result.rests.length, 1);
  assert.equal(result.rests[0].start, 0.25);
  assert.equal(result.rests[0].end, 0.75);
  assert.equal(result.rests[0].durationSeconds, 0.5);
  assert.equal(result.metrics.restGapCount, 1);
  assert.equal(result.metrics.exactMidiPreservedCount, 2);
});

test('missing duration remains unresolved in the structure-mapped event schema', () => {
  const result = buildStructureMappedEventSchema({
    structureMap: straightMap(),
    instrumentConfig: instrument(),
    events: [{ start: 0.25, midi: 64 }],
  });

  const event = result.events[0];
  assert.equal(event.durationResolved, false);
  assert.equal(event.projectedEnd, null);
  assert.deepEqual(event.notation.segments, []);
  assert.equal(result.metrics.unresolvedDurationCount, 1);
});
