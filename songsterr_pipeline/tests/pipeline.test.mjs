import test from 'node:test';
import assert from 'node:assert/strict';

import {
  STANDARD_GUITAR_TUNING_MIDI,
  enumeratePlayablePositions,
  findPlayableShape,
  groupOnsetClusters,
  normalizeConditioning,
  resolveStructureGrid,
  runDeterministicCore,
  snapOnsetToGrid,
} from '../index.mjs';

test('conditioning keeps structure, role, tuning, and capo explicit', () => {
  const conditioning = normalizeConditioning({
    structurePrior: {
      tempoBpm: 120,
      timeSignature: { numerator: 4, denominator: 4 },
      pickupBeats: 1,
      feel: 'straight',
    },
    instrumentConfig: {
      role: 'rhythm',
      tuningMidi: [39, 44, 49, 54, 58, 63],
      capoFret: 2,
    },
  });

  assert.equal(conditioning.referenceBlind, true);
  assert.equal(conditioning.instrumentConfig.role, 'rhythm');
  assert.deepEqual(conditioning.instrumentConfig.tuningMidi, [39, 44, 49, 54, 58, 63]);
  assert.equal(conditioning.instrumentConfig.capoFret, 2);
  assert.deepEqual(conditioning.structurePrior.timeSignature, { numerator: 4, denominator: 4 });
});

test('measure-aware snapping anchors full measures after the pickup', () => {
  const conditioning = normalizeConditioning({
    structurePrior: {
      tempoBpm: 120,
      timeSignature: { numerator: 4, denominator: 4 },
      pickupBeats: 1,
      feel: 'straight',
    },
    instrumentConfig: {
      role: 'lead',
    },
  });
  const grid = resolveStructureGrid(conditioning.structurePrior);
  const snapped = snapOnsetToGrid(0.621, grid);

  assert.equal(grid.pickupSeconds, 0.5);
  assert.equal(grid.subdivisionSeconds, 0.125);
  assert.equal(snapped.projectedStart, 0.625);
  assert.equal(snapped.position.measureNumber, 1);
  assert.equal(snapped.position.beatNumber, 1);
  assert.ok(Math.abs(snapped.position.beatFraction - 0.25) < 1e-9);
});

test('onset clustering is stable and does not chain unrelated attacks', () => {
  const clusters = groupOnsetClusters([
    { start: 1.000, midi: 64 },
    { start: 1.006, midi: 59 },
    { start: 1.018, midi: 56 },
  ], 0.01);

  assert.equal(clusters.length, 2);
  assert.deepEqual(clusters[0].events.map((event) => event.midi), [64, 59]);
  assert.deepEqual(clusters[1].events.map((event) => event.midi), [56]);
});

test('playable positions reconstruct the exact MIDI pitch', () => {
  const instrumentConfig = {
    role: 'lead',
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 2,
  };
  const positions = enumeratePlayablePositions(66, instrumentConfig);

  assert.ok(positions.length > 0);
  for (const position of positions) {
    assert.equal(position.reconstructedMidi, 66);
  }
});

test('simultaneous notes are decoded as one unique-string playable shape', () => {
  const instrumentConfig = {
    role: 'rhythm',
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 0,
  };
  const shape = findPlayableShape([64, 59, 56], instrumentConfig);

  assert.ok(shape);
  assert.equal(shape.assignments.length, 3);
  assert.equal(new Set(shape.assignments.map((assignment) => assignment.lowToHighIndex)).size, 3);
  assert.deepEqual(shape.assignments.map((assignment) => assignment.reconstructedMidi), [64, 59, 56]);
});

test('fresh deterministic core preserves event count and exact pitch', () => {
  const result = runDeterministicCore({
    conditioning: {
      structurePrior: {
        tempoBpm: 120,
        timeSignature: { numerator: 4, denominator: 4 },
        pickupBeats: 1,
        feel: 'straight',
      },
      instrumentConfig: {
        role: 'rhythm',
        tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
        capoFret: 0,
      },
    },
    onsetToleranceSeconds: 0.01,
    events: [
      { start: 0.621, midi: 64 },
      { start: 0.625, midi: 59 },
      { start: 0.628, midi: 56 },
      { start: 1.129, midi: 57 },
    ],
  });

  assert.equal(result.pipeline.referenceBlind, true);
  assert.equal(result.pipeline.legacyV143ScorerImported, false);
  assert.equal(result.metrics.sourceCount, 4);
  assert.equal(result.metrics.outputCount, 4);
  assert.equal(result.metrics.countDelta, 0);
  assert.equal(result.metrics.exactMidiMatches, 4);
  assert.equal(result.metrics.pitchPreservationRate, 1);
  assert.equal(result.clusters.length, 2);
  assert.deepEqual(result.events.map((event) => event.midi), [64, 59, 56, 57]);
  assert.equal(result.events[0].projectedStart, 0.625);
  assert.equal(result.events[1].projectedStart, 0.625);
  assert.equal(result.events[2].projectedStart, 0.625);
  assert.equal(result.events[3].projectedStart, 1.125);

  const firstShapeStrings = result.events.slice(0, 3).map((event) => event.lowToHighIndex);
  assert.equal(new Set(firstShapeStrings).size, 3);
  for (const event of result.events) {
    assert.equal(event.reconstructedMidi, event.midi);
  }
});

test('invalid tuning cannot silently enter the fresh contract', () => {
  assert.throws(() => normalizeConditioning({
    structurePrior: {},
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [40, 45, 45, 55, 59, 64],
      capoFret: 0,
    },
  }), /strictly increasing/);
});
