import test from 'node:test';
import assert from 'node:assert/strict';

import { summarizeNoteEvidence } from '../noteEvidenceDiagnostics.mjs';

function adapted() {
  return {
    adapterContract: {
      referenceBlind: true,
      structureIdentityVerified: true,
    },
    onsets: [
      {
        classification: 'unambiguous',
        candidates: [{ midi: 64, confidence: 0.9 }],
      },
      {
        classification: 'ambiguous',
        candidates: [{ midi: 52, confidence: 0.8 }],
      },
      {
        classification: 'ambiguous',
        candidates: [
          { midi: 52, confidence: 0.78 },
          { midi: 64, confidence: 0.74 },
        ],
      },
      {
        classification: 'ambiguous',
        candidates: [
          { midi: 60, confidence: 0.76 },
          { midi: 67, confidence: 0.71 },
        ],
      },
      {
        classification: 'no-candidate',
        candidates: [],
      },
    ],
    promotedEvents: [
      { midi: 64, start: 0.5 },
    ],
  };
}

test('diagnostics preserve unresolved evidence categories without creating a composite score', () => {
  const result = summarizeNoteEvidence(adapted());
  assert.equal(result.contract.compositeScoreDefined, false);
  assert.equal(result.contract.compositeScore, null);
  assert.equal(result.contract.descriptiveOnly, true);
  assert.equal(result.contract.ownsAcceptanceDecision, false);
  assert.equal(result.counts.onsetCount, 5);
  assert.equal(result.counts.unresolvedPitchEvidenceCount, 4);
  assert.equal(result.counts.singleCandidateAmbiguousCount, 1);
  assert.equal(result.counts.competingCandidateAmbiguousCount, 2);
  assert.equal(result.counts.harmonicRelationAmbiguousCount, 1);
  assert.equal(result.counts.octaveRelationAmbiguousCount, 1);
  assert.equal(result.counts.closeIntervalAmbiguousCount, 1);
  assert.deepEqual(result.topSecondIntervalHistogram, { '7': 1, '12': 1 });
});

test('diagnostics report missing promoted duration but do not own readiness decisions', () => {
  const result = summarizeNoteEvidence(adapted());
  assert.equal(result.counts.promotedWithDurationCount, 0);
  assert.equal(result.counts.promotedMissingDurationCount, 1);
  assert.equal('blockers' in result, false);
  assert.equal('noHumanCorrectionReady' in result, false);
});

test('null duration/end are not mistaken for real duration evidence', () => {
  const input = adapted();
  input.onsets = [input.onsets[0]];
  input.promotedEvents = [{ midi: 64, start: 0.5, duration: null, end: null }];
  const result = summarizeNoteEvidence(input);
  assert.equal(result.counts.promotedWithDurationCount, 0);
  assert.equal(result.counts.promotedMissingDurationCount, 1);
});

test('fully resolved evidence stays descriptive and scoreless', () => {
  const input = adapted();
  input.onsets = [{ classification: 'unambiguous', candidates: [{ midi: 64, confidence: 0.9 }] }];
  input.promotedEvents = [{ midi: 64, start: 0.5, duration: 0.25 }];
  const result = summarizeNoteEvidence(input);
  assert.equal(result.counts.unresolvedPitchEvidenceCount, 0);
  assert.equal(result.counts.promotedMissingDurationCount, 0);
  assert.equal(result.contract.compositeScore, null);
  assert.equal(result.contract.ownsAcceptanceDecision, false);
});


test('diagnostics expose evidence-state inventory without defining a score', () => {
  const input = adapted();
  input.onsets = [
    { classification: 'unambiguous', evidenceState: 'promoted-core', candidates: [{ midi: 52, confidence: 0.9 }] },
    { classification: 'unambiguous', evidenceState: 'promoted-technique', candidates: [{ midi: 57, confidence: 0.8 }] },
    { classification: 'unambiguous', evidenceState: 'recovered-recurring-onset', candidates: [{ midi: 64, confidence: 0.75 }] },
    { classification: 'ambiguous', evidenceState: 'ambiguous', candidates: [{ midi: 67, confidence: 0.7 }] },
    { classification: 'no-candidate', evidenceState: 'unassigned', candidates: [] },
    { classification: 'rejected', evidenceState: 'rejected', candidates: [{ midi: 76, confidence: 0.6 }] },
  ];
  input.promotedEvents = [
    { midi: 52, start: 0.5 },
    { midi: 57, start: 1.0 },
    { midi: 64, start: 1.5 },
  ];
  const result = summarizeNoteEvidence(input);
  assert.deepEqual(result.counts.evidenceStateCounts, {
    'promoted-core': 1,
    'promoted-technique': 1,
    'recovered-recurring-onset': 1,
    ambiguous: 1,
    unassigned: 1,
    rejected: 1,
    unspecified: 0,
  });
  assert.equal(result.contract.compositeScore, null);
  assert.equal(result.contract.ownsAcceptanceDecision, false);
});

test('legacy evidence without explicit state is counted as unspecified', () => {
  const result = summarizeNoteEvidence(adapted());
  assert.equal(result.counts.evidenceStateCounts.unspecified, result.counts.onsetCount);
});
