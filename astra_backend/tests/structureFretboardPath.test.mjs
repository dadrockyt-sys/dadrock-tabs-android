import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { applyOptimizedFretboardPath } from '../structureFretboardPath.mjs';

function event({ id, cluster, midi, start, fret }) {
  return {
    schemaVersion: 2,
    eventId: `event-${id}`,
    sourceEventIndex: id,
    clusterId: cluster,
    midi,
    sourceStart: start,
    sourceEnd: start + 0.25,
    projectedStart: start,
    projectedEnd: start + 0.25,
    measureNumber: 1,
    beatNumber: cluster + 1,
    beatFraction: 0,
    pickup: false,
    tempoBpm: 120,
    timeSignature: { numerator: 4, denominator: 4 },
    feel: 'straight',
    notation: {
      segments: [{ start, end: start + 0.25 }],
      syncopatedStart: false,
    },
    provenance: { referenceBlind: true },
    fretboard: {
      fret,
      reconstructedMidi: midi,
      shapeResolved: true,
    },
  };
}

function schema(events, role = 'lead') {
  return {
    pipeline: { name: 'fixture' },
    structureMap: { version: 1 },
    instrumentConfig: {
      role,
      tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
      capoFret: 0,
    },
    events,
    rests: [{ start: 1.5, end: 1.75 }],
    metrics: { sourceCount: events.length },
  };
}

test('integration preserves protected event structure while reducing targeted phrase movement', () => {
  const input = schema([
    event({ id: 0, cluster: 0, midi: 64, start: 0, fret: 5 }),
    event({ id: 1, cluster: 1, midi: 76, start: 0.5, fret: 12 }),
    event({ id: 2, cluster: 2, midi: 64, start: 1, fret: 5 }),
  ]);

  const before = input.events.map((item) => ({
    eventId: item.eventId,
    midi: item.midi,
    projectedStart: item.projectedStart,
    projectedEnd: item.projectedEnd,
    notation: item.notation,
  }));

  const result = applyOptimizedFretboardPath(input);
  const after = result.events.map((item) => ({
    eventId: item.eventId,
    midi: item.midi,
    projectedStart: item.projectedStart,
    projectedEnd: item.projectedEnd,
    notation: item.notation,
  }));

  assert.deepEqual(after, before);
  assert.deepEqual(result.rests, input.rests);
  assert.equal(result.fretboardPath.invariantProjectionPreserved, true);
  assert.ok(result.fretboardPath.movementDelta < 0);
});

test('optimized chord mapping preserves each source MIDI and unique strings inside the cluster', () => {
  const input = schema([
    event({ id: 0, cluster: 0, midi: 64, start: 0, fret: 0 }),
    event({ id: 1, cluster: 0, midi: 59, start: 0, fret: 0 }),
    event({ id: 2, cluster: 0, midi: 56, start: 0, fret: 1 }),
  ], 'rhythm');

  const result = applyOptimizedFretboardPath(input);

  assert.equal(result.fretboardPath.applied, true);
  assert.deepEqual(result.events.map((item) => item.fretboard.reconstructedMidi), [64, 59, 56]);
  assert.equal(new Set(result.events.map((item) => item.fretboard.lowToHighIndex)).size, 3);
});

test('unresolved path returns explicitly and leaves event objects semantically untouched', () => {
  const input = schema([
    event({ id: 0, cluster: 0, midi: 64, start: 0, fret: 0 }),
    event({ id: 1, cluster: 1, midi: 64, start: 0.5, fret: 5 }),
    event({ id: 2, cluster: 1, midi: 65, start: 0.5, fret: 6 }),
  ], 'rhythm');

  const result = applyOptimizedFretboardPath(input, {
    policy: {
      maxFrettedSpan: 0,
      maxAdjacentFretDelta: 0,
    },
  });

  assert.equal(result.fretboardPath.resolved, false);
  assert.equal(result.fretboardPath.applied, false);
  assert.deepEqual(result.events, input.events);
  assert.deepEqual(result.rests, input.rests);
});

test('structure-fretboard integration is deterministic', () => {
  const input = schema([
    event({ id: 0, cluster: 0, midi: 64, start: 0, fret: 5 }),
    event({ id: 1, cluster: 1, midi: 76, start: 0.5, fret: 12 }),
    event({ id: 2, cluster: 2, midi: 67, start: 1, fret: 8 }),
  ]);

  assert.deepEqual(applyOptimizedFretboardPath(input), applyOptimizedFretboardPath(input));
});

test('cluster timing inconsistency is rejected instead of being silently averaged', () => {
  const input = schema([
    event({ id: 0, cluster: 0, midi: 64, start: 0, fret: 5 }),
    event({ id: 1, cluster: 0, midi: 59, start: 0.125, fret: 0 }),
  ], 'rhythm');

  assert.throws(() => applyOptimizedFretboardPath(input), /inconsistent projectedStart/);
});
