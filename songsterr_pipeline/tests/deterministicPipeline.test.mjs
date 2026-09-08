import test from 'node:test';
import assert from 'node:assert/strict';

import { runFreshDeterministicPipeline } from '../deterministicPipeline.mjs';
import { buildStructureMap } from '../structureMap.mjs';

const STANDARD_GUITAR = [40, 45, 50, 55, 59, 64];

function map({ feel = 'straight', durationSeconds = 4 } = {}) {
  return buildStructureMap({
    durationSeconds,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.95 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.98 }],
    feelSegments: [{ start: 0, end: null, feel, confidence: 0.9 }],
    confidence: {
      overall: 0.92,
      tempo: 0.95,
      meter: 0.98,
      downbeats: 0.95,
      measures: 0.95,
      feel: 0.9,
    },
    provenance: { source: 'deterministic-pipeline-fixture' },
  });
}

function instrument(role = 'lead') {
  return {
    role,
    tuningMidi: [...STANDARD_GUITAR],
    capoFret: 0,
  };
}

test('full deterministic composition preserves identity and reaches a delivery-ready straight product payload', () => {
  const sourceEvents = [
    { start: 0, duration: 0.25, midi: 64 },
    { start: 0.5, duration: 0.25, midi: 76 },
    { start: 1.0, duration: 0.25, midi: 64 },
  ];

  const result = runFreshDeterministicPipeline({
    events: sourceEvents,
    structureMap: map(),
    instrumentConfig: instrument('lead'),
    productShell: { difficulty: 'intermediate' },
  });

  assert.equal(result.pipeline.modelOrAudioAnalyzerInvoked, false);
  assert.equal(result.pipeline.legacyV143ScorerImported, false);
  assert.deepEqual(result.events.map((event) => event.sourceEventIndex), [0, 1, 2]);
  assert.deepEqual(result.events.map((event) => event.midi), [64, 76, 64]);
  assert.deepEqual(result.events.map((event) => event.sourceStart), [0, 0.5, 1]);
  assert.equal(result.fretboardPath.resolved, true);
  assert.equal(result.fretboardPath.applied, true);
  assert.equal(result.freshDiagnostics.passedRawIntegrityChecks, true);
  assert.deepEqual(result.freshDiagnostics.failures, []);
  assert.equal(result.productShell.payloadContract.deliveryReady, true);
  assert.equal(result.productShell.payloadContract.structuredRenderEligible, true);
  assert.equal(result.productShell.renderEvents.length, 3);
  assert.ok(result.productShell.generatedTab.includes('RIFF 1'));
});

test('triplet composition stays delivery-ready but fails closed from the legacy sixteenth renderer', () => {
  const start = 1 / 6;
  const result = runFreshDeterministicPipeline({
    events: [{ start, duration: 1 / 6, midi: 64 }],
    structureMap: map({ feel: 'triplet', durationSeconds: 2 }),
    instrumentConfig: instrument('lead'),
  });

  assert.equal(result.freshDiagnostics.passedRawIntegrityChecks, true);
  assert.equal(result.productShell.payloadContract.deliveryReady, true);
  assert.equal(result.productShell.payloadContract.structuredRenderEligible, false);
  assert.equal(
    result.productShell.payloadContract.legacyProjectionReason,
    'LEGACY_RENDER_SUBDIVISION_UNSUPPORTED',
  );
  assert.deepEqual(result.productShell.renderEvents, []);
  assert.equal(result.productShell.measureGrid, null);
  assert.equal(result.events[0].midi, 64);
});

test('unresolved phrase fingering remains explicit end-to-end and never drops the simultaneous source pitches', () => {
  const sourceEvents = [
    { start: 0, duration: 0.25, midi: 64 },
    { start: 0, duration: 0.25, midi: 65 },
  ];

  const result = runFreshDeterministicPipeline({
    events: sourceEvents,
    structureMap: map({ durationSeconds: 2 }),
    instrumentConfig: instrument('rhythm'),
    fretboardPathOptions: {
      policy: {
        maxFrettedSpan: 0,
        maxAdjacentFretDelta: 0,
      },
    },
  });

  assert.equal(result.fretboardPath.resolved, false);
  assert.equal(result.fretboardPath.applied, false);
  assert.deepEqual(result.events.map((event) => event.midi), [64, 65]);
  assert.equal(result.events.length, 2);
  assert.equal(result.productShell.payloadContract.deliveryReady, false);
  assert.ok(
    result.freshDiagnostics.failures.some((failure) => failure.code === 'FRETBOARD_PATH_UNRESOLVED'),
  );
});

test('deterministic pipeline composition is stable across repeated runs', () => {
  const input = {
    events: [
      { start: 0.125, duration: 0.25, midi: 64 },
      { start: 0.625, duration: 0.25, midi: 67 },
    ],
    structureMap: map({ durationSeconds: 2 }),
    instrumentConfig: instrument('lead'),
    productShell: { keySignature: 'C' },
  };

  const first = runFreshDeterministicPipeline(input);
  const second = runFreshDeterministicPipeline(input);

  assert.deepEqual(first, second);
});
