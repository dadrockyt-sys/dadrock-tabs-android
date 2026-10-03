import test from 'node:test';
import assert from 'node:assert/strict';

import { buildTranscriptionUncertaintyPresentation } from '../transcriptionUncertaintyPresentation.mjs';

function exposure({ roleAccepted = true, complete = true } = {}) {
  const events = [
    { evidenceOnsetId: 'a', start: 0.5, midi: 40, duration: 0.25 },
    { evidenceOnsetId: 'b', start: 1.0, midi: 52, duration: 0.25 },
  ];
  return {
    exposureContract: { referenceBlind: true, structureFrozen: true },
    role: 'guitar',
    structureIdentity: { signature: 'fnv1a32:test' },
    pitchResolvedEvents: structuredClone(events),
    roleAcceptedEvents: roleAccepted ? structuredClone(events) : [],
    completeTabEligibleEvents: complete ? structuredClone(events) : [],
  };
}

test('eligible evidence remains unchanged and carries no invented confidence score', () => {
  const result = buildTranscriptionUncertaintyPresentation({
    evidenceEvaluation: { acceptedForCompleteTab: true, failureReasons: [], diagnostics: {} },
    eventExposure: exposure(),
    pairContext: { state: 'complementary_pair' },
    provenance: { fixture: 'unit' },
  });
  assert.equal(result.presentationState, 'complete_tab_eligible');
  assert.equal(result.completeTabEligible, true);
  assert.equal(result.uncertaintyContract.confidenceScore, null);
  assert.equal(result.uncertaintyContract.automaticCorrectionAuthorized, false);
  assert.deepEqual(
    result.evidence.completeTabEligibleEvents.map((e) => [e.start, e.midi]),
    [[0.5, 40], [1.0, 52]],
  );
});

test('duplicate-class pair keeps notes visible but fails closed for complete tab', () => {
  const result = buildTranscriptionUncertaintyPresentation({
    evidenceEvaluation: { acceptedForCompleteTab: true, failureReasons: [], diagnostics: {} },
    eventExposure: exposure(),
    pairContext: { state: 'duplicate_bass_candidate', source: 'frozen-pair-v1' },
  });
  assert.equal(result.presentationState, 'evidence_visible_review_required');
  assert.equal(result.completeTabEligible, false);
  assert.equal(result.evidence.pitchResolvedEvents.length, 2);
  assert.equal(result.evidence.completeTabEligibleEvents.length, 0);
  assert.ok(result.reasonCodes.includes('PAIR_ROLE_AMBIGUITY_DUPLICATE_CLASS_CANDIDATE'));
  assert.equal(result.guidance.reviewRequired, true);
});

test('evaluator failure reasons are surfaced rather than converted into a score', () => {
  const result = buildTranscriptionUncertaintyPresentation({
    evidenceEvaluation: {
      acceptedForCompleteTab: false,
      failureReasons: ['DURATION_EVIDENCE_INCOMPLETE', 'POLYPHONY_UNRESOLVED'],
      diagnostics: { unresolvedOnsetRate: 0.2 },
    },
    eventExposure: exposure({ complete: false }),
    pairContext: { state: 'complementary_pair' },
  });
  assert.equal(result.completeTabEligible, false);
  assert.deepEqual(
    result.reasonCodes,
    ['DURATION_EVIDENCE_INCOMPLETE', 'POLYPHONY_UNRESOLVED'],
  );
  assert.equal(result.uncertaintyContract.confidenceScoreDefined, false);
});

test('descriptive cross-stem diagnostics can be exposed but cannot own a hidden gate', () => {
  const result = buildTranscriptionUncertaintyPresentation({
    evidenceEvaluation: { acceptedForCompleteTab: false, failureReasons: [], diagnostics: {} },
    eventExposure: exposure({ complete: false }),
    pairContext: { state: 'ambiguous_pair' },
    crossStemDiagnostics: {
      descriptiveOnly: true,
      eventDensityBalance: 1.0,
      exactMidiOverlapF1: 0.03,
    },
  });
  assert.equal(result.diagnostics.crossStemDiagnostics.eventDensityBalance, 1.0);
  assert.ok(result.reasonCodes.includes('PAIR_ROLE_RELATIONSHIP_AMBIGUOUS'));
  assert.equal(result.uncertaintyContract.thresholdsLearnedFromS0, false);
});

test('non-descriptive cross-stem gate input is rejected', () => {
  assert.throws(
    () => buildTranscriptionUncertaintyPresentation({
      evidenceEvaluation: { acceptedForCompleteTab: false, failureReasons: [] },
      eventExposure: exposure({ complete: false }),
      crossStemDiagnostics: { descriptiveOnly: false, accept: true },
    }),
    /CROSS_STEM_DIAGNOSTICS_MUST_BE_DESCRIPTIVE_ONLY/,
  );
});

test('presentation fails closed without frozen reference-blind exposure', () => {
  const broken = exposure();
  broken.exposureContract.referenceBlind = false;
  assert.throws(
    () => buildTranscriptionUncertaintyPresentation({
      evidenceEvaluation: {},
      eventExposure: broken,
    }),
    /REQUIRES_FROZEN_REFERENCE_BLIND_EXPOSURE/,
  );
});
