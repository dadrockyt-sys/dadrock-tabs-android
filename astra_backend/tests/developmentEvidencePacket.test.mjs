import test from 'node:test';
import assert from 'node:assert/strict';

import { buildDevelopmentEvidencePacket } from '../developmentEvidencePacket.mjs';
import { buildStructureIdentity } from '../structureIdentity.mjs';
import { buildStructureMap } from '../structureMap.mjs';

function structureMap() {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.9, provenance: { source: 'integration-test' } }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.9, provenance: { source: 'integration-test' } }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.9, provenance: { source: 'integration-test' } }],
    confidence: { overall: 0.9, tempo: 0.9, meter: 0.9, downbeats: 0.9, measures: 0.9, feel: 0.9 },
    provenance: { source: 'integration-test-structure', referenceBlind: true },
  });
}

function acceptedEvidence(map) {
  return {
    version: 1,
    referenceBlind: true,
    structureFrozen: true,
    role: 'guitar',
    structureIdentity: buildStructureIdentity(map),
    capabilities: {
      roleRelevanceResolved: true,
      polyphonyResolved: true,
      durationResolution: 'complete',
      instrumentIsolation: 'separator-role-output',
      confidenceCalibration: 'diagnostic-only',
    },
    onsets: [
      {
        onsetId: 'n0',
        sourceStart: 0.5,
        nearestStructureSlot: 0.5,
        sourceEnd: 0.75,
        durationSeconds: 0.25,
        durationConfidence: 0.8,
        onsetConfidence: 0.91,
        classification: 'unambiguous',
        evidenceState: 'promoted-core',
        selectedMidi: 64,
        candidates: [{ midi: 64, confidence: 0.93 }],
      },
      {
        onsetId: 'n1',
        sourceStart: 1.0,
        nearestStructureSlot: 1.0,
        sourceEnd: 1.5,
        durationSeconds: 0.5,
        durationConfidence: 0.82,
        onsetConfidence: 0.88,
        classification: 'unambiguous',
        evidenceState: 'promoted-core',
        selectedMidi: 67,
        candidates: [{ midi: 67, confidence: 0.9 }],
      },
    ],
    provenance: {
      source: 'deterministic-integration-fixture',
      modelInvoked: false,
      modelValidationComplete: true,
    },
  };
}

function unresolvedEvidence(map) {
  const raw = acceptedEvidence(map);
  raw.capabilities = {
    ...raw.capabilities,
    polyphonyResolved: false,
    durationResolution: 'partial',
  };
  raw.onsets[1] = {
    onsetId: 'n1',
    sourceStart: 1.0,
    nearestStructureSlot: 1.0,
    onsetConfidence: 0.88,
    classification: 'ambiguous',
    evidenceState: 'ambiguous',
    selectedMidi: null,
    candidates: [
      { midi: 67, confidence: 0.72 },
      { midi: 79, confidence: 0.69 },
    ],
  };
  return raw;
}

function identities(events) {
  return events.map((e) => [e.evidenceOnsetId, e.start, e.midi]);
}

test('clean complementary accepted evidence becomes complete_tab_eligible end to end', () => {
  const map = structureMap();
  const packet = buildDevelopmentEvidencePacket({
    rawNoteEvidence: acceptedEvidence(map),
    structureMap: map,
    pairContext: {
      state: 'complementary_pair',
      source: 'integration-test',
    },
    crossStemDiagnostics: {
      descriptiveOnly: true,
      exactMidiOverlapF1: 0.0,
      eventDensityBalance: 0.4,
    },
    provenance: { testCase: 'clean-complementary' },
  });

  assert.equal(packet.evidenceEvaluation.acceptedForCompleteTab, true);
  assert.equal(packet.presentation.presentationState, 'complete_tab_eligible');
  assert.equal(packet.presentation.completeTabEligible, true);
  assert.deepEqual(
    identities(packet.presentation.evidence.completeTabEligibleEvents),
    [['n0', 0.5, 64], ['n1', 1, 67]],
  );
  assert.equal(packet.packetContract.productionDeliveryAuthorized, false);
});

test('duplicate-class pair keeps exact notes visible but fails closed for complete tab', () => {
  const map = structureMap();
  const packet = buildDevelopmentEvidencePacket({
    rawNoteEvidence: acceptedEvidence(map),
    structureMap: map,
    pairContext: {
      state: 'duplicate_bass_candidate',
      source: 'frozen-pair-classifier-v1',
    },
    crossStemDiagnostics: {
      descriptiveOnly: true,
      exactMidiOverlapF1: 0.03,
      pitchClassOverlapF1: 0.09,
      eventDensityBalance: 1.0,
    },
    provenance: { testCase: 'duplicate-role' },
  });

  assert.equal(packet.evidenceEvaluation.acceptedForCompleteTab, true);
  assert.equal(packet.eventExposure.completeTabEligibleEvents.length, 2);
  assert.equal(packet.presentation.presentationState, 'evidence_visible_review_required');
  assert.equal(packet.presentation.completeTabEligible, false);
  assert.deepEqual(
    identities(packet.presentation.evidence.pitchResolvedEvents),
    [['n0', 0.5, 64], ['n1', 1, 67]],
  );
  assert.equal(packet.presentation.evidence.completeTabEligibleEvents.length, 0);
  assert.ok(
    packet.presentation.reasonCodes.includes('PAIR_ROLE_AMBIGUITY_DUPLICATE_CLASS_CANDIDATE'),
  );
});

test('unresolved evaluator failure reasons survive end to end and complete-tab events remain empty', () => {
  const map = structureMap();
  const packet = buildDevelopmentEvidencePacket({
    rawNoteEvidence: unresolvedEvidence(map),
    structureMap: map,
    pairContext: { state: 'complementary_pair' },
    provenance: { testCase: 'unresolved-evidence' },
  });

  assert.equal(packet.evidenceEvaluation.acceptedForCompleteTab, false);
  assert.ok(packet.evidenceEvaluation.failureReasons.includes('POLYPHONY_UNRESOLVED'));
  assert.ok(packet.evidenceEvaluation.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'));
  assert.ok(packet.evidenceEvaluation.failureReasons.includes('DURATION_EVIDENCE_INCOMPLETE'));
  assert.equal(packet.eventExposure.completeTabEligibleEvents.length, 0);
  assert.equal(packet.presentation.evidence.completeTabEligibleEvents.length, 0);
  for (const reason of packet.evidenceEvaluation.failureReasons) {
    assert.ok(packet.presentation.reasonCodes.includes(reason));
  }
  assert.equal(packet.presentation.presentationState, 'evidence_visible_review_required');
});

test('MIDI and onset identity remain byte-for-byte stable through every visible event layer', () => {
  const map = structureMap();
  const packet = buildDevelopmentEvidencePacket({
    rawNoteEvidence: acceptedEvidence(map),
    structureMap: map,
    pairContext: { state: 'duplicate_guitar_candidate' },
  });

  const expected = identities(packet.adaptedEvidence.promotedEvents);
  assert.deepEqual(identities(packet.eventExposure.pitchResolvedEvents), expected);
  assert.deepEqual(identities(packet.presentation.evidence.pitchResolvedEvents), expected);
  assert.deepEqual(identities(packet.presentation.evidence.roleAcceptedEvents), expected);
  assert.equal(packet.invariants.exactMidiAndOnsetIdentityPreserved, true);
});

test('no confidence score, automatic correction, mutation, or role reassignment appears in packet', () => {
  const map = structureMap();
  const packet = buildDevelopmentEvidencePacket({
    rawNoteEvidence: acceptedEvidence(map),
    structureMap: map,
    pairContext: { state: 'complementary_pair' },
  });

  assert.equal(packet.packetContract.confidenceScoreDefined, false);
  assert.equal(packet.packetContract.automaticCorrectionAuthorized, false);
  assert.equal(packet.packetContract.automaticStemMutationAuthorized, false);
  assert.equal(packet.packetContract.automaticRoleReassignmentAuthorized, false);
  assert.equal(packet.presentation.uncertaintyContract.confidenceScore, null);
  assert.equal(packet.presentation.uncertaintyContract.automaticCorrectionAuthorized, false);
});

test('non-descriptive cross-stem gate input is rejected before packet completion', () => {
  const map = structureMap();
  assert.throws(
    () => buildDevelopmentEvidencePacket({
      rawNoteEvidence: acceptedEvidence(map),
      structureMap: map,
      crossStemDiagnostics: { descriptiveOnly: false, hiddenGateDecision: 'accept' },
    }),
    /CROSS_STEM_DIAGNOSTICS_MUST_BE_DESCRIPTIVE_ONLY/,
  );
});

test('packet construction is deterministic', () => {
  const map = structureMap();
  const args = {
    rawNoteEvidence: acceptedEvidence(map),
    structureMap: map,
    pairContext: { state: 'complementary_pair' },
    crossStemDiagnostics: { descriptiveOnly: true, eventDensityBalance: 0.5 },
    provenance: { testCase: 'determinism' },
  };
  assert.deepEqual(
    buildDevelopmentEvidencePacket(args),
    buildDevelopmentEvidencePacket(args),
  );
});
