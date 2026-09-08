import test from 'node:test';
import assert from 'node:assert/strict';

import { adaptStructureConditionedNoteEvidence } from '../noteEvidenceAdapter.mjs';
import { buildStructureIdentity } from '../structureIdentity.mjs';
import { buildStructureMap } from '../structureMap.mjs';

function structureMap() {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 0.9, provenance: { source: 'test' } }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 0.8, provenance: { source: 'test' } }],
    feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 0.8, provenance: { source: 'test' } }],
    confidence: { overall: 0.8, tempo: 0.9, meter: 0.8, downbeats: 0.8, measures: 0.8, feel: 0.8 },
    provenance: { source: 'test-structure', referenceBlind: true },
  });
}

function evidence(map, overrides = {}) {
  return {
    version: 1,
    referenceBlind: true,
    structureFrozen: true,
    role: 'guitar',
    structureIdentity: buildStructureIdentity(map),
    onsets: [
      {
        onsetId: 'o0',
        sourceStart: 0.51,
        nearestStructureSlot: 0.5,
        onsetConfidence: 0.9,
        classification: 'unambiguous',
        selectedMidi: 64,
        candidates: [
          { midi: 64, confidence: 0.88, spectralDb: -8, prominenceDb: 12, harmonicSupport: 0.7 },
        ],
      },
      {
        onsetId: 'o1',
        sourceStart: 1.01,
        nearestStructureSlot: 1,
        onsetConfidence: 0.8,
        classification: 'ambiguous',
        candidates: [
          { midi: 67, confidence: 0.72 },
          { midi: 71, confidence: 0.69 },
        ],
      },
      {
        onsetId: 'o2',
        sourceStart: 1.5,
        nearestStructureSlot: 1.5,
        onsetConfidence: 0.45,
        classification: 'no-candidate',
        candidates: [],
      },
    ],
    provenance: { source: 'cpu-note-evidence-test', modelInvoked: false },
    ...overrides,
  };
}

test('note evidence verifies the exact frozen structure identity', () => {
  const map = structureMap();
  const result = adaptStructureConditionedNoteEvidence(evidence(map), map);
  assert.equal(result.adapterContract.structureIdentityVerified, true);
  assert.equal(result.adapterContract.structureFrozen, true);
  assert.equal(result.structureIdentity.signature, buildStructureIdentity(map).signature);
});

test('ambiguous and no-candidate onsets remain explicit instead of being silently promoted or dropped', () => {
  const map = structureMap();
  const result = adaptStructureConditionedNoteEvidence(evidence(map), map);
  assert.equal(result.metrics.onsetCount, 3);
  assert.equal(result.metrics.candidateCount, 3);
  assert.equal(result.metrics.unambiguousOnsetCount, 1);
  assert.equal(result.metrics.ambiguousOnsetCount, 1);
  assert.equal(result.metrics.noCandidateOnsetCount, 1);
  assert.equal(result.metrics.unresolvedOnsetCount, 2);
  assert.equal(result.metrics.unresolvedEvidencePreserved, true);
  assert.equal(result.onsets[1].candidates.length, 2);
  assert.deepEqual(result.onsets[1].candidates.map((candidate) => candidate.midi), [67, 71]);
});

test('only explicitly unambiguous highest-confidence MIDI is exposed to the deterministic event layer', () => {
  const map = structureMap();
  const result = adaptStructureConditionedNoteEvidence(evidence(map), map);
  assert.equal(result.promotedEvents.length, 1);
  assert.equal(result.promotedEvents[0].midi, 64);
  assert.equal(result.promotedEvents[0].start, 0.51);
  assert.equal(result.promotedEvents[0].provenance.structureIdentity, result.structureIdentity.signature);
});

test('evidence generated against a different structure is rejected before note promotion', () => {
  const map = structureMap();
  const wrongMap = buildStructureMap({
    durationSeconds: 4,
    tempoSegments: [{ start: 0, end: null, bpm: 100 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  });
  assert.throws(
    () => adaptStructureConditionedNoteEvidence(evidence(wrongMap), map),
    /NOTE_EVIDENCE_STRUCTURE_IDENTITY_MISMATCH/,
  );
});

test('duplicate MIDI candidates inside one onset are rejected rather than double-counted', () => {
  const map = structureMap();
  const raw = evidence(map, {
    onsets: [{
      sourceStart: 0.5,
      nearestStructureSlot: 0.5,
      onsetConfidence: 0.8,
      classification: 'ambiguous',
      candidates: [
        { midi: 64, confidence: 0.8 },
        { midi: 64, confidence: 0.7 },
      ],
    }],
  });
  assert.throws(() => adaptStructureConditionedNoteEvidence(raw, map), /duplicate MIDI candidate 64/);
});

test('note evidence adaptation is deterministic', () => {
  const map = structureMap();
  assert.deepEqual(
    adaptStructureConditionedNoteEvidence(evidence(map), map),
    adaptStructureConditionedNoteEvidence(evidence(map), map),
  );
});
