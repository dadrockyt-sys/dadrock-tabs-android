import test from 'node:test';
import assert from 'node:assert/strict';

import { runFreshDeterministicPipeline } from '../deterministicPipeline.mjs';
import { buildStructureMap } from '../structureMap.mjs';

function structureMap() {
  return buildStructureMap({
    durationSeconds: 2,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  });
}

const instrumentConfig = {
  role: 'lead',
  tuningMidi: [40, 45, 50, 55, 59, 64],
  capoFret: 0,
};

test('upstream evidence blockers keep an otherwise clean result from delivery', () => {
  const result = runFreshDeterministicPipeline({
    events: [{ start: 0.5, duration: 0.25, midi: 64 }],
    structureMap: structureMap(),
    instrumentConfig,
    productShell: {
      upstreamEvidenceReady: false,
      upstreamEvidenceBlockers: ['UNRESOLVED_ROLE_NOTE_EVIDENCE'],
    },
  });

  assert.equal(result.freshDiagnostics.passedRawIntegrityChecks, true);
  assert.equal(result.productShell.payloadContract.rawResultReady, true);
  assert.equal(result.productShell.payloadContract.upstreamEvidenceReady, false);
  assert.deepEqual(result.productShell.payloadContract.upstreamEvidenceBlockers, ['UNRESOLVED_ROLE_NOTE_EVIDENCE']);
  assert.equal(result.productShell.payloadContract.deliveryReady, false);
  assert.equal(result.productShell.payloadContract.structuredRenderEligible, false);
  assert.deepEqual(result.productShell.renderEvents, []);
  assert.equal(result.productShell.measureGrid, null);
});

test('clean upstream evidence preserves normal delivery behavior', () => {
  const result = runFreshDeterministicPipeline({
    events: [{ start: 0.5, duration: 0.25, midi: 64 }],
    structureMap: structureMap(),
    instrumentConfig,
    productShell: {
      upstreamEvidenceReady: true,
      upstreamEvidenceBlockers: [],
    },
  });

  assert.equal(result.productShell.payloadContract.rawResultReady, true);
  assert.equal(result.productShell.payloadContract.deliveryReady, true);
});

test('contradictory upstream evidence state is rejected', () => {
  assert.throws(() => runFreshDeterministicPipeline({
    events: [{ start: 0.5, duration: 0.25, midi: 64 }],
    structureMap: structureMap(),
    instrumentConfig,
    productShell: {
      upstreamEvidenceReady: true,
      upstreamEvidenceBlockers: ['UNRESOLVED_ROLE_NOTE_EVIDENCE'],
    },
  }), /upstreamEvidenceReady cannot be true/);
});
