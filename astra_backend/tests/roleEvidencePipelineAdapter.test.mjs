import test from 'node:test';
import assert from 'node:assert/strict';

import { runRoleEvidenceDeterministicPipeline } from '../roleEvidencePipelineAdapter.mjs';
import { buildStructureMap } from '../structureMap.mjs';

const STANDARD_GUITAR = [40, 45, 50, 55, 59, 64];

function structureMap() {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.95 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.98 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.9 }],
    confidence: {
      overall: 0.92,
      tempo: 0.95,
      meter: 0.98,
      downbeats: 0.95,
      measures: 0.95,
      feel: 0.9,
    },
    provenance: { source: 'role-pipeline-test', referenceBlind: true },
  });
}

function promoted(id, midi, start, stateSource) {
  return {
    id,
    midi,
    start,
    duration: 0.25,
    durationConfidence: 0.9,
    confidence: 0.9,
    onsetConfidence: 0.9,
    provenance: { source: stateSource },
  };
}

function completeInput(overrides = {}) {
  return {
    requestedRole: 'lead',
    roleEvidenceStatus: 'complete',
    structureMap: structureMap(),
    streams: {
      promotedCore: [promoted('core', 64, 0, 'recurring-core')],
      promotedTechnique: [promoted('bend', 67, 0.5, 'glide-continuity')],
      recoveredRecurringOnset: [promoted('recover', 69, 1, 'raw-onset-recovery')],
      ambiguous: [],
      unassigned: [],
      rejected: [],
    },
    capabilities: {
      polyphonyResolved: true,
      durationResolution: 'complete',
      instrumentIsolation: 'stereo-role-evidence',
      confidenceCalibration: 'heuristic-not-calibrated-probability',
    },
    provenance: {
      source: 'synthetic-role-evidence',
      modelInvoked: false,
      modelValidationComplete: false,
    },
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [...STANDARD_GUITAR],
      capoFret: 0,
    },
    productShell: { difficulty: 'intermediate' },
    ...overrides,
  };
}

test('fully resolved role evidence reaches deterministic tablature with evidence states preserved', () => {
  const result = runRoleEvidenceDeterministicPipeline(completeInput());
  assert.equal(result.evidenceEvaluation.acceptedForCompleteTab, true);
  assert.ok(result.pipeline);
  assert.equal(result.pipeline.productShell.payloadContract.deliveryReady, true);
  assert.deepEqual(
    result.eventEvidence.map((event) => event.evidenceState),
    ['promoted-core', 'promoted-technique', 'recovered-recurring-onset'],
  );
  assert.deepEqual(
    result.eventEvidence.map((event) => event.evidenceOnsetId),
    ['core', 'bend', 'recover'],
  );
  assert.equal(result.customerDeliveryEligible, false);
  assert.equal(result.integrationContract.customerDeliveryEligible, false);
});

test('ambiguous evidence blocks deterministic tablature instead of leaking a promoted event', () => {
  const input = completeInput();
  input.streams.ambiguous.push({
    id: 'amb',
    start: 1.5,
    onsetConfidence: 0.8,
    candidates: [
      { midi: 71, confidence: 0.7 },
      { midi: 74, confidence: 0.68 },
    ],
  });
  const result = runRoleEvidenceDeterministicPipeline(input);
  assert.equal(result.evidenceEvaluation.acceptedForCompleteTab, false);
  assert.ok(result.evidenceEvaluation.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'));
  assert.equal(result.pipeline, null);
  assert.deepEqual(result.eventEvidence, []);
  assert.ok(result.blockers.includes('DETERMINISTIC_PIPELINE_NOT_RUN'));
});

test('unassigned evidence blocks deterministic tablature', () => {
  const input = completeInput();
  input.streams.unassigned.push({
    id: 'none',
    start: 1.5,
    onsetConfidence: 0.4,
  });
  const result = runRoleEvidenceDeterministicPipeline(input);
  assert.equal(result.evidenceEvaluation.acceptedForCompleteTab, false);
  assert.ok(result.evidenceEvaluation.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'));
  assert.equal(result.pipeline, null);
});

test('role abstention cannot produce deterministic events or customer delivery', () => {
  const input = completeInput({
    roleEvidenceStatus: 'abstained',
    streams: {
      promotedCore: [],
      promotedTechnique: [],
      recoveredRecurringOnset: [],
      ambiguous: [{
        id: 'amb-only',
        start: 0.5,
        onsetConfidence: 0.6,
        candidates: [{ midi: 64, confidence: 0.6 }],
      }],
      unassigned: [],
      rejected: [],
    },
  });
  const result = runRoleEvidenceDeterministicPipeline(input);
  assert.equal(result.capabilities, undefined);
  assert.equal(result.adaptedEvidence.capabilities.roleRelevanceResolved, false);
  assert.equal(result.pipeline, null);
  assert.equal(result.customerDeliveryEligible, false);
  assert.ok(result.evidenceEvaluation.failureReasons.includes('ROLE_RELEVANCE_UNRESOLVED'));
});

test('instrument role must match requested role before pipeline execution', () => {
  const input = completeInput();
  input.instrumentConfig.role = 'rhythm';
  assert.throws(
    () => runRoleEvidenceDeterministicPipeline(input),
    /instrumentConfig.role must match requestedRole/,
  );
});

test('wrapper remains deterministic', () => {
  const input = completeInput();
  assert.deepEqual(
    runRoleEvidenceDeterministicPipeline(input),
    runRoleEvidenceDeterministicPipeline(input),
  );
});
