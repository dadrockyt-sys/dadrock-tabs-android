import test from 'node:test';
import assert from 'node:assert/strict';

import { evaluateNoteEvidence } from '../noteEvidenceEvaluator.mjs';

function cleanEvidence(overrides = {}) {
  const onsets = [
    {
      onsetId: 'o0',
      sourceStart: 0.5,
      nearestStructureSlot: 0.5,
      structureDisplacementSeconds: 0,
      classification: 'unambiguous',
      selectedMidi: 64,
      durationSeconds: 0.25,
      candidates: [{ midi: 64, confidence: 0.91 }],
    },
    {
      onsetId: 'o1',
      sourceStart: 1,
      nearestStructureSlot: 1,
      structureDisplacementSeconds: 0,
      classification: 'unambiguous',
      selectedMidi: 67,
      durationSeconds: 0.25,
      candidates: [{ midi: 67, confidence: 0.9 }],
    },
  ];
  const promotedEvents = [
    { midi: 64, start: 0.5, duration: 0.25 },
    { midi: 67, start: 1, duration: 0.25 },
  ];
  return {
    adapterContract: {
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
      nearestStructureSlotsVerified: true,
      syntheticDurationInference: false,
      legacyV143ScorerImported: false,
    },
    capabilities: {
      roleRelevanceResolved: true,
      polyphonyResolved: true,
      durationResolution: 'complete',
      instrumentIsolation: 'role-conditioned',
      confidenceCalibration: 'declared',
    },
    onsets,
    promotedEvents,
    metrics: {
      onsetCount: 2,
      promotedEventCount: 2,
      unresolvedOnsetCount: 0,
      durationResolvedEvidenceCount: 2,
    },
    ...overrides,
  };
}

test('complete evidence can pass without defining a composite score', () => {
  const result = evaluateNoteEvidence(cleanEvidence());
  assert.equal(result.acceptedForCompleteTab, true);
  assert.deepEqual(result.failureReasons, []);
  assert.equal(result.evaluatorContract.compositeScoreDefined, false);
  assert.equal(result.evaluatorContract.compositeScore, null);
});

test('unresolved role relevance, polyphony, pitch, and duration remain separate blockers', () => {
  const evidence = cleanEvidence({
    capabilities: {
      roleRelevanceResolved: false,
      polyphonyResolved: false,
      durationResolution: 'none',
      instrumentIsolation: 'none',
      confidenceCalibration: 'heuristic-not-calibrated-probability',
    },
    onsets: [
      {
        structureDisplacementSeconds: 0.01,
        classification: 'ambiguous',
        candidates: [{ midi: 64, confidence: 0.8 }, { midi: 76, confidence: 0.7 }],
      },
    ],
    promotedEvents: [],
    metrics: {
      onsetCount: 1,
      promotedEventCount: 0,
      unresolvedOnsetCount: 1,
      durationResolvedEvidenceCount: 0,
    },
  });
  const result = evaluateNoteEvidence(evidence);
  assert.equal(result.acceptedForCompleteTab, false);
  assert.ok(result.failureReasons.includes('ROLE_RELEVANCE_UNRESOLVED'));
  assert.ok(result.failureReasons.includes('POLYPHONY_UNRESOLVED'));
  assert.ok(result.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'));
  assert.ok(result.failureReasons.includes('DURATION_EVIDENCE_INCOMPLETE'));
  assert.ok(result.failureReasons.includes('NO_PROMOTED_NOTE_EVENTS'));
});

test('candidate density and octave competition are raw diagnostics rather than a hidden score', () => {
  const evidence = cleanEvidence({
    onsets: [
      {
        structureDisplacementSeconds: 0.01,
        classification: 'ambiguous',
        candidates: [
          { midi: 52, confidence: 0.82 },
          { midi: 64, confidence: 0.74 },
          { midi: 59, confidence: 0.5 },
        ],
      },
      {
        structureDisplacementSeconds: -0.02,
        classification: 'ambiguous',
        candidates: [
          { midi: 55, confidence: 0.8 },
          { midi: 62, confidence: 0.65 },
        ],
      },
    ],
    promotedEvents: [],
    metrics: {
      onsetCount: 2,
      promotedEventCount: 0,
      unresolvedOnsetCount: 2,
      durationResolvedEvidenceCount: 0,
    },
  });
  const result = evaluateNoteEvidence(evidence);
  assert.equal(result.diagnostics.candidateCount, 5);
  assert.equal(result.diagnostics.multiCandidateOnsetCount, 2);
  assert.equal(result.diagnostics.octaveCompetitorOnsetCount, 1);
  assert.equal(result.diagnostics.octaveCompetitorRateAmongMultiCandidateOnsets, 0.5);
  assert.equal(result.evaluatorContract.compositeScore, null);
});

test('dominant MIDI concentration remains visible without automatically rewriting or dropping events', () => {
  const onsets = Array.from({ length: 4 }, (_, index) => ({
    structureDisplacementSeconds: 0,
    classification: 'unambiguous',
    selectedMidi: index < 3 ? 40 : 52,
    durationSeconds: 0.2,
    candidates: [{ midi: index < 3 ? 40 : 52, confidence: 0.9 }],
  }));
  const promotedEvents = onsets.map((onset, index) => ({
    midi: onset.selectedMidi,
    start: index * 0.5,
    duration: 0.2,
  }));
  const evidence = cleanEvidence({
    onsets,
    promotedEvents,
    metrics: {
      onsetCount: 4,
      promotedEventCount: 4,
      unresolvedOnsetCount: 0,
      durationResolvedEvidenceCount: 4,
    },
  });
  const result = evaluateNoteEvidence(evidence);
  assert.equal(result.diagnostics.dominantPromotedMidi.value, 40);
  assert.equal(result.diagnostics.dominantPromotedMidi.count, 3);
  assert.equal(result.diagnostics.dominantPromotedMidi.share, 0.75);
  assert.equal(promotedEvents.length, 4);
});

test('evaluator is deterministic', () => {
  const evidence = cleanEvidence();
  assert.deepEqual(evaluateNoteEvidence(evidence), evaluateNoteEvidence(evidence));
});
