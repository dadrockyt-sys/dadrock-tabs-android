import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import {
  buildStructureMap,
  locateInStructureMap,
  runStructureMappedCore,
  snapTimestampToStructureMap,
} from '../structureMap.mjs';

function baseMap(overrides = {}) {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0.5,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.95, provenance: 'fixture-tempo' }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.98, provenance: 'fixture-meter' }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.9, provenance: 'fixture-feel' }],
    confidence: {
      overall: 0.9,
      tempo: 0.95,
      meter: 0.98,
      downbeats: 0.92,
      measures: 0.94,
      feel: 0.9,
    },
    provenance: { source: 'synthetic-fixture' },
    ...overrides,
  });
}

test('structureMap materializes pickup, downbeats, measures, beats, and subdivisions as first-class data', () => {
  const map = baseMap();

  assert.equal(map.version, 1);
  assert.equal(map.referenceBlind, true);
  assert.equal(map.pickupDurationSeconds, 0.5);
  assert.equal(map.measures[0].measureNumber, 0);
  assert.equal(map.measures[0].pickup, true);
  assert.equal(map.measures[1].measureNumber, 1);
  assert.equal(map.measures[1].start, 0.5);
  assert.equal(map.measures[1].beats.length, 4);
  assert.equal(map.measures[1].beats[0].subdivisions.length, 4);
  assert.equal(map.downbeats[0].time, 0.5);
  assert.equal(map.confidence.meter, 0.98);
  assert.equal(map.provenance.source, 'synthetic-fixture');
});

test('structureMap snapping and location are driven by explicit measure/beat subdivisions', () => {
  const map = baseMap();
  const snapped = snapTimestampToStructureMap(0.621, map);

  assert.equal(snapped.projectedStart, 0.625);
  assert.equal(snapped.position.measureNumber, 1);
  assert.equal(snapped.position.beatNumber, 1);
  assert.ok(Math.abs(snapped.position.beatFraction - 0.25) < 1e-9);

  const located = locateInStructureMap(2.51, map);
  assert.equal(located.measureNumber, 2);
  assert.equal(located.beatNumber, 1);
});

test('tempo change at a measure boundary changes subsequent measure duration and timing grid', () => {
  const map = buildStructureMap({
    durationSeconds: 6,
    tempoSegments: [
      { start: 0, end: 2, bpm: 120 },
      { start: 2, end: null, bpm: 60 },
    ],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  });

  assert.equal(map.measures[0].start, 0);
  assert.equal(map.measures[0].end, 2);
  assert.equal(map.measures[0].tempoBpm, 120);
  assert.equal(map.measures[1].start, 2);
  assert.equal(map.measures[1].end, 6);
  assert.equal(map.measures[1].tempoBpm, 60);
  assert.equal(map.measures[1].beats[0].subdivisions[1], 2.25);
});

test('meter change at a measure boundary changes the next measure beat count without post-hoc repair', () => {
  const map = buildStructureMap({
    durationSeconds: 3.5,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [
      { start: 0, end: 2, numerator: 4, denominator: 4 },
      { start: 2, end: null, numerator: 3, denominator: 4 },
    ],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  });

  assert.equal(map.measures[0].timeSignature.numerator, 4);
  assert.equal(map.measures[0].beats.length, 4);
  assert.equal(map.measures[1].timeSignature.numerator, 3);
  assert.equal(map.measures[1].beats.length, 3);
  assert.equal(map.measures[1].start, 2);
  assert.equal(map.measures[1].end, 3.5);
});

test('structure-mapped note stage preserves pitch/count and groups slightly spread chord attacks against the map', () => {
  const map = baseMap();
  const result = runStructureMappedCore({
    structureMap: map,
    instrumentConfig: {
      role: 'rhythm',
      tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
      capoFret: 0,
    },
    onsetToleranceSeconds: 0.01,
    events: [
      { start: 0.621, midi: 64 },
      { start: 0.626, midi: 59 },
      { start: 0.629, midi: 56 },
      { start: 1.129, midi: 57 },
    ],
  });

  assert.equal(result.metrics.sourceCount, 4);
  assert.equal(result.metrics.outputCount, 4);
  assert.equal(result.metrics.countDelta, 0);
  assert.equal(result.metrics.exactMidiPreservedCount, 4);
  assert.equal(result.metrics.pitchPreservationRate, 1);
  assert.equal(result.clusters.length, 2);
  assert.deepEqual(result.events.slice(0, 3).map((event) => event.projectedStart), [0.625, 0.625, 0.625]);
  assert.equal(new Set(result.events.slice(0, 3).map((event) => event.lowToHighIndex)).size, 3);
  for (const event of result.events) assert.equal(event.reconstructedMidi, event.midi);
});

test('structure changes that do not align to a measure boundary are rejected instead of silently warping the map', () => {
  assert.throws(() => buildStructureMap({
    durationSeconds: 4,
    tempoSegments: [
      { start: 0, end: 1, bpm: 120 },
      { start: 1, end: null, bpm: 100 },
    ],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  }), /STRUCTURE_CHANGE_MUST_ALIGN_TO_MEASURE_BOUNDARY/);
});
