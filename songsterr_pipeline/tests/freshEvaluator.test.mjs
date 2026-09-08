import test from 'node:test';
import assert from 'node:assert/strict';

import { evaluateFreshPipeline } from '../freshEvaluator.mjs';

function structureMap() {
  return {
    durationSeconds: 2,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
    measures: [{ measureNumber: 1, start: 0, end: 2, pickup: false }],
    downbeats: [{ measureNumber: 1, time: 0 }],
    confidence: { overall: 0.9 },
  };
}

function event(id, midi, start, stringIndex, fret, cluster = id) {
  return {
    eventId: `event-${id}`,
    sourceEventIndex: id,
    clusterId: cluster,
    midi,
    sourceStart: start,
    sourceEnd: start + 0.25,
    projectedStart: start,
    projectedEnd: start + 0.25,
    durationResolved: true,
    notation: {
      segments: [{ start, end: start + 0.25 }],
      unresolvedSpellingSegmentCount: 0,
    },
    fretboard: {
      lowToHighIndex: stringIndex,
      fret,
      reconstructedMidi: midi,
    },
  };
}

function goodResult() {
  const events = [
    event(0, 64, 0, 5, 0),
    event(1, 67, 0.5, 4, 8),
  ];
  return {
    structureMap: structureMap(),
    events,
    rests: [],
    rhythmSpelling: {
      unresolvedRestSegmentCount: 0,
      restSegmentCount: 0,
      feel: { consistent: true },
    },
    fretboardPath: {
      resolved: true,
      applied: true,
      metrics: {
        totalCenterFretMovement: 8,
        maxCenterFretMovement: 8,
        stringSetChangeCount: 2,
        candidateCounts: [4, 4],
        unresolvedOnsetCount: 0,
      },
    },
  };
}

const sourceEvents = [{ midi: 64 }, { midi: 67 }];

test('clean result emits raw diagnostics with no composite score and no failures', () => {
  const result = evaluateFreshPipeline(goodResult(), { sourceEvents });

  assert.equal(result.passedRawIntegrityChecks, true);
  assert.deepEqual(result.failures, []);
  assert.equal(result.events.exactMidiPreservationRate, 1);
  assert.equal(result.playability.playableAssignedCount, 2);
  assert.equal(result.evaluator.compositeScoreDefined, false);
  assert.equal(result.evaluator.compositeScore, null);
});

test('count and MIDI identity drift are explicit independent failures', () => {
  const bad = goodResult();
  bad.events = [{
    ...bad.events[0],
    midi: 65,
    fretboard: {
      ...bad.events[0].fretboard,
      reconstructedMidi: 65,
    },
  }];

  const result = evaluateFreshPipeline(bad, { sourceEvents });
  const codes = result.failures.map((item) => item.code);

  assert.ok(codes.includes('EVENT_COUNT_DRIFT'));
  assert.ok(codes.includes('MIDI_IDENTITY_MISMATCH'));
  assert.ok(codes.includes('SOURCE_IDENTITY_DRIFT'));
});

test('structure boundary and downbeat problems remain visible', () => {
  const bad = goodResult();
  bad.structureMap = {
    ...structureMap(),
    measures: [{ measureNumber: 1, start: 0.1, end: 2, pickup: false }],
    downbeats: [],
  };

  const result = evaluateFreshPipeline(bad, { sourceEvents });
  const codes = result.failures.map((item) => item.code);

  assert.ok(codes.includes('MEASURE_BOUNDARY_INCONSISTENT'));
  assert.ok(codes.includes('DOWNBEAT_INCONSISTENT'));
  assert.ok(codes.includes('STRUCTURE_MAP_INCOMPLETE'));
});

test('playability and unique-string chord violations are explicit', () => {
  const bad = goodResult();
  bad.events = [
    event(0, 64, 0, 5, 0, 0),
    event(1, 59, 0, 5, 5, 0),
  ];
  bad.events[1].fretboard.reconstructedMidi = 60;

  const result = evaluateFreshPipeline(bad, {
    sourceEvents: [{ midi: 64 }, { midi: 59 }],
  });
  const codes = result.failures.map((item) => item.code);

  assert.ok(codes.includes('UNPLAYABLE_ASSIGNMENT'));
  assert.ok(codes.includes('UNIQUE_STRING_CHORD_VIOLATION'));
});

test('unresolved rhythm and fretboard path remain separate raw failure reasons', () => {
  const bad = goodResult();
  bad.events[0] = {
    ...bad.events[0],
    sourceEnd: null,
    projectedEnd: null,
    durationResolved: false,
    notation: {
      segments: [],
      unresolvedSpellingSegmentCount: 2,
    },
  };
  bad.fretboardPath = {
    resolved: false,
    applied: false,
    diagnostics: { unresolvedOnsetCount: 1 },
  };

  const result = evaluateFreshPipeline(bad, { sourceEvents });
  const codes = result.failures.map((item) => item.code);

  assert.ok(codes.includes('UNRESOLVED_DURATION'));
  assert.ok(codes.includes('UNRESOLVED_RHYTHM_SPELLING'));
  assert.ok(codes.includes('FRETBOARD_PATH_UNRESOLVED'));
});

test('evaluation is deterministic and retains raw movement diagnostics', () => {
  const first = evaluateFreshPipeline(goodResult(), { sourceEvents });
  const second = evaluateFreshPipeline(goodResult(), { sourceEvents });

  assert.deepEqual(first, second);
  assert.equal(first.playability.totalCenterFretMovement, 8);
  assert.equal(first.playability.maxCenterFretMovement, 8);
});
