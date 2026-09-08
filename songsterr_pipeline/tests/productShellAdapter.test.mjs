import test from 'node:test';
import assert from 'node:assert/strict';

import { buildProductShellPayload } from '../productShellAdapter.mjs';

function structureMap({ pickup = false, triplet = false } = {}) {
  const beatSeconds = 0.5;
  const pickupDurationSeconds = pickup ? 0.5 : 0;
  const measures = [];

  if (pickup) {
    measures.push({
      measureNumber: 0,
      start: 0,
      end: 0.5,
      pickup: true,
      timeSignature: { numerator: 1, denominator: 4 },
      tempoBpm: 120,
      feel: 'straight',
      beats: [{
        beatNumber: 1,
        start: 0,
        end: 0.5,
        subdivisions: [0, 0.125, 0.25, 0.375],
      }],
    });
  }

  const start = pickupDurationSeconds;
  const subdivisions = triplet ? [0, 1 / 6, 1 / 3] : [0, 0.125, 0.25, 0.375];
  const beats = [];
  for (let beat = 0; beat < 4; beat += 1) {
    beats.push({
      beatNumber: beat + 1,
      start: start + beat * beatSeconds,
      end: start + (beat + 1) * beatSeconds,
      subdivisions: subdivisions.map((offset) => start + beat * beatSeconds + offset),
    });
  }

  measures.push({
    measureNumber: 1,
    start,
    end: start + 2,
    pickup: false,
    timeSignature: { numerator: 4, denominator: 4 },
    tempoBpm: 120,
    feel: triplet ? 'triplet' : 'straight',
    beats,
  });

  return {
    version: 1,
    durationSeconds: start + 2,
    pickupDurationSeconds,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: triplet ? 'triplet' : 'straight' }],
    measures,
    downbeats: [{ measureNumber: 1, time: start }],
    confidence: { overall: 0.9 },
  };
}

function event({
  id = 0,
  midi = 64,
  start = 0,
  measure = 1,
  beatNumber = 1,
  beatFraction = 0,
  stringNumber = 1,
  lowToHigh = 5,
  fret = 0,
  duration = 0.25,
  triplet = false,
} = {}) {
  return {
    eventId: `event-${id}`,
    sourceEventIndex: id,
    clusterId: id,
    midi,
    sourceStart: start,
    sourceEnd: start + duration,
    projectedStart: start,
    projectedEnd: start + duration,
    projectedDurationSeconds: duration,
    durationResolved: true,
    measureNumber: measure,
    beatNumber,
    beatFraction,
    pickup: measure === 0,
    tempoBpm: 120,
    timeSignature: { numerator: 4, denominator: 4 },
    feel: triplet ? 'triplet' : 'straight',
    notation: {
      segments: [{
        segmentIndex: 0,
        start,
        end: start + duration,
        durationSeconds: duration,
        measureNumber: measure,
        beatNumber,
        beatFraction,
        pickup: measure === 0,
        feel: triplet ? 'triplet' : 'straight',
      }],
      unresolvedSpellingSegmentCount: 0,
    },
    fretboard: {
      stringNumberHighToLow: stringNumber,
      lowToHighIndex: lowToHigh,
      fret,
      reconstructedMidi: midi,
      shapeResolved: true,
      pathOptimized: true,
    },
  };
}

function result(options = {}) {
  const map = structureMap(options);
  const start = options.pickup ? 0.5 : 0;
  const item = event({
    start,
    measure: 1,
    beatNumber: 1,
    beatFraction: options.triplet ? 1 / 3 : 0,
    stringNumber: 1,
    lowToHigh: 5,
    fret: 0,
    duration: options.triplet ? 1 / 6 : 0.25,
    triplet: options.triplet,
  });

  if (options.triplet) {
    item.projectedStart = start + 1 / 6;
    item.sourceStart = item.projectedStart;
    item.sourceEnd = item.projectedStart + 1 / 6;
    item.projectedEnd = item.sourceEnd;
    item.notation.segments[0] = {
      ...item.notation.segments[0],
      start: item.projectedStart,
      end: item.projectedEnd,
      durationSeconds: 1 / 6,
      beatFraction: 1 / 3,
    };
  }

  return {
    structureMap: map,
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [40, 45, 50, 55, 59, 64],
      capoFret: 0,
    },
    events: [item],
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
        totalCenterFretMovement: 0,
        maxCenterFretMovement: 0,
        stringSetChangeCount: 0,
        candidateCounts: [4],
        unresolvedOnsetCount: 0,
      },
    },
  };
}

test('clean straight result maps to existing product shell and structured renderer contract', () => {
  const input = result();
  const payload = buildProductShellPayload({
    result: input,
    sourceEvents: [{ midi: 64 }],
    difficulty: 'beginner',
  });

  assert.equal(payload.payloadContract.deliveryReady, true);
  assert.equal(payload.payloadContract.structuredRenderEligible, true);
  assert.equal(payload.analysisEngine, 'songsterr-fresh-pipeline-v1');
  assert.equal(payload.transcriptionType, 'lead');
  assert.equal(payload.tuning, 'E A D G B E');
  assert.equal(payload.tempo, 120);
  assert.equal(payload.timeSignature, '4/4');
  assert.equal(payload.renderEvents.length, 1);
  assert.deepEqual(payload.renderEvents[0], {
    eventIndex: 0,
    measure: 1,
    step: 0,
    stringIndex: 0,
    fret: 0,
    midi: 64,
    durationSteps: 2,
    techniques: [],
    durationSeconds: 0.25,
    source: 'songsterr-fresh-pipeline-v1',
  });
  assert.equal(payload.measureGrid.measureGridVersion, 7);
  assert.equal(payload.measureGrid.measuresPerRow, 6);
  assert.equal(payload.measureGrid.rows[0].notes[0].measureGridReadOnly, true);
  assert.match(payload.generatedTab, /^RIFF 1/m);
});

test('triplet timing fails closed to complete text fallback instead of fake sixteenth quantization', () => {
  const input = result({ triplet: true });
  const payload = buildProductShellPayload({
    result: input,
    sourceEvents: [{ midi: 64 }],
  });

  assert.equal(payload.payloadContract.deliveryReady, true);
  assert.equal(payload.payloadContract.structuredRenderEligible, false);
  assert.equal(payload.payloadContract.legacyProjectionReason, 'LEGACY_RENDER_SUBDIVISION_UNSUPPORTED');
  assert.deepEqual(payload.renderEvents, []);
  assert.equal(payload.measureGrid, null);
  assert.ok(payload.generatedTab.length > 0);
});

test('pickup fails closed for legacy structured projection but keeps full text payload', () => {
  const input = result({ pickup: true });
  input.events.unshift(event({
    id: 1,
    midi: 62,
    start: 0.25,
    measure: 0,
    beatNumber: 1,
    beatFraction: 0.5,
    stringNumber: 2,
    lowToHigh: 4,
    fret: 3,
    duration: 0.125,
  }));
  input.events[1].sourceEventIndex = 0;
  input.events[0].sourceEventIndex = 1;

  const payload = buildProductShellPayload({
    result: input,
    sourceEvents: [{ midi: 64 }, { midi: 62 }],
  });

  assert.equal(payload.payloadContract.structuredRenderEligible, false);
  assert.equal(payload.payloadContract.legacyProjectionReason, 'LEGACY_RENDER_PICKUP_UNSUPPORTED');
  assert.ok(payload.generatedTab.includes('RIFF 1'));
});

test('raw evaluator failure blocks delivery readiness and structured render data', () => {
  const input = result();
  input.events[0].fretboard.reconstructedMidi = 65;

  const payload = buildProductShellPayload({
    result: input,
    sourceEvents: [{ midi: 64 }],
  });

  assert.equal(payload.payloadContract.deliveryReady, false);
  assert.equal(payload.payloadContract.structuredRenderEligible, false);
  assert.deepEqual(payload.renderEvents, []);
  assert.ok(payload.freshDiagnostics.failures.some((item) => item.code === 'UNPLAYABLE_ASSIGNMENT'));
});

test('custom tuning metadata projects without changing positional fret identity', () => {
  const input = result();
  input.instrumentConfig = {
    role: 'lead',
    tuningMidi: [38, 45, 50, 55, 59, 64],
    capoFret: 2,
  };

  const payload = buildProductShellPayload({
    result: input,
    sourceEvents: [{ midi: 64 }],
  });

  assert.equal(payload.tuning, 'D A D G B E');
  assert.equal(payload.transcriptionType, 'lead');
  assert.equal(payload.events[0].midi, 64);
});

test('adapter is deterministic and declares no legacy scorer import', () => {
  const input = {
    result: result(),
    sourceEvents: [{ midi: 64 }],
  };

  const first = buildProductShellPayload(input);
  const second = buildProductShellPayload(input);

  assert.deepEqual(first, second);
  assert.equal(first.payloadContract.legacyV143ScorerImported, false);
  assert.equal(first.measureGrid.legacyV143ScorerImported, false);
});
