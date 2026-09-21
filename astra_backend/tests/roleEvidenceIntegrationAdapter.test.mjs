import test from 'node:test';
import assert from 'node:assert/strict';

import { adaptRoleEvidenceStreams } from '../roleEvidenceIntegrationAdapter.mjs';
import { buildStructureMap } from '../structureMap.mjs';

function structureMap() {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.9, provenance: { source: 'test' } }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.9, provenance: { source: 'test' } }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.9, provenance: { source: 'test' } }],
    confidence: { overall: 0.9, tempo: 0.9, meter: 0.9, downbeats: 0.9, measures: 0.9, feel: 0.9 },
    provenance: { source: 'test-structure', referenceBlind: true },
  });
}

function event(id, midi, start, confidence = 0.8) {
  return {
    id,
    midi,
    start,
    confidence,
    onsetConfidence: confidence,
    provenance: { source: 'synthetic-role-evidence' },
  };
}

function completeInput(overrides = {}) {
  return {
    requestedRole: 'rhythm',
    roleEvidenceStatus: 'complete',
    structureMap: structureMap(),
    streams: {
      promotedCore: [event('core', 52, 0.5, 0.9)],
      promotedTechnique: [event('bend', 57, 1.0, 0.85)],
      recoveredRecurringOnset: [event('recovered', 64, 1.5, 0.8)],
      ambiguous: [{
        id: 'amb',
        start: 2,
        onsetConfidence: 0.7,
        candidates: [
          { midi: 67, confidence: 0.7 },
          { midi: 71, confidence: 0.68 },
        ],
      }],
      unassigned: [{ id: 'none', start: 2.5, onsetConfidence: 0.4 }],
      rejected: [{
        id: 'reject',
        start: 3,
        onsetConfidence: 0.5,
        candidates: [{ midi: 76, confidence: 0.6 }],
      }],
    },
    capabilities: {
      polyphonyResolved: false,
      durationResolution: 'none',
      instrumentIsolation: 'stereo-role-evidence',
      confidenceCalibration: 'heuristic-not-calibrated-probability',
    },
    provenance: {
      source: 'synthetic-role-integration-test',
      modelValidationComplete: false,
    },
    ...overrides,
  };
}

test('complete role evidence preserves explicit promoted state provenance', () => {
  const result = adaptRoleEvidenceStreams(completeInput());
  assert.equal(result.requestedRole, 'rhythm');
  assert.equal(result.role, 'guitar');
  assert.equal(result.roleEvidenceStatus, 'complete');
  assert.equal(result.customerDeliveryEligible, false);
  assert.equal(result.integrationContract.customerDeliveryEligible, false);
  assert.equal(result.promotedEvents.length, 3);
  assert.deepEqual(
    result.promotedEvents.map((event) => event.provenance.evidenceState),
    ['promoted-core', 'promoted-technique', 'recovered-recurring-onset'],
  );
  assert.equal(result.metrics.evidenceStateCounts['promoted-core'], 1);
  assert.equal(result.metrics.evidenceStateCounts['promoted-technique'], 1);
  assert.equal(result.metrics.evidenceStateCounts['recovered-recurring-onset'], 1);
});

test('ambiguous, unassigned, and rejected evidence is preserved without promotion', () => {
  const result = adaptRoleEvidenceStreams(completeInput());
  assert.equal(result.metrics.ambiguousOnsetCount, 1);
  assert.equal(result.metrics.noCandidateOnsetCount, 1);
  assert.equal(result.metrics.rejectedOnsetCount, 1);
  assert.equal(result.metrics.evidenceStateCounts.ambiguous, 1);
  assert.equal(result.metrics.evidenceStateCounts.unassigned, 1);
  assert.equal(result.metrics.evidenceStateCounts.rejected, 1);
  assert.equal(result.promotedEvents.some((event) => ['amb', 'none', 'reject'].includes(event.evidenceOnsetId)), false);
});

test('abstained role evidence cannot promote any event', () => {
  const input = completeInput({
    roleEvidenceStatus: 'abstained',
    streams: {
      promotedCore: [event('illegal', 52, 0.5)],
      ambiguous: [],
      unassigned: [],
      rejected: [],
      promotedTechnique: [],
      recoveredRecurringOnset: [],
    },
  });
  assert.throws(
    () => adaptRoleEvidenceStreams(input),
    /ABSTAINED_ROLE_EVIDENCE_CANNOT_PROMOTE/,
  );
});

test('abstained evidence may preserve uncertainty while role relevance remains unresolved', () => {
  const input = completeInput({
    roleEvidenceStatus: 'abstained',
    streams: {
      promotedCore: [],
      promotedTechnique: [],
      recoveredRecurringOnset: [],
      ambiguous: [{
        id: 'amb-only',
        start: 1,
        onsetConfidence: 0.6,
        candidates: [{ midi: 64, confidence: 0.6 }],
      }],
      unassigned: [{ id: 'none-only', start: 1.5 }],
      rejected: [],
    },
  });
  const result = adaptRoleEvidenceStreams(input);
  assert.equal(result.promotedEvents.length, 0);
  assert.equal(result.capabilities.roleRelevanceResolved, false);
  assert.equal(result.metrics.unresolvedOnsetCount, 2);
  assert.equal(result.customerDeliveryEligible, false);
});

test('event identities must remain unique across every evidence stream', () => {
  const input = completeInput();
  input.streams.promotedTechnique[0].id = 'core';
  assert.throws(
    () => adaptRoleEvidenceStreams(input),
    /duplicate role evidence event id core/,
  );
});

test('lead and rhythm integrate as guitar while preserving requested role', () => {
  const input = completeInput({ requestedRole: 'lead' });
  const result = adaptRoleEvidenceStreams(input);
  assert.equal(result.requestedRole, 'lead');
  assert.equal(result.role, 'guitar');
  assert.equal(result.analyzerDiagnostics.requestedRole, 'lead');
});

test('bass integrates as bass without widening delivery authority', () => {
  const input = completeInput({ requestedRole: 'bass' });
  const result = adaptRoleEvidenceStreams(input);
  assert.equal(result.role, 'bass');
  assert.equal(result.requestedRole, 'bass');
  assert.equal(result.customerDeliveryEligible, false);
});

test('role evidence integration is deterministic', () => {
  const input = completeInput();
  assert.deepEqual(adaptRoleEvidenceStreams(input), adaptRoleEvidenceStreams(input));
});
