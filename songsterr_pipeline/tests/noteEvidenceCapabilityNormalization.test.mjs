import test from 'node:test';
import assert from 'node:assert/strict';

import { adaptStructureConditionedNoteEvidence } from '../noteEvidenceAdapter.mjs';
import { buildStructureIdentity } from '../structureIdentity.mjs';
import { buildStructureMap, snapTimestampToStructureMap } from '../structureMap.mjs';

function map() {
  return buildStructureMap({
    durationSeconds: 2,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  });
}

test('descriptive partial duration capability normalizes to partial without losing detail', () => {
  const structureMap = map();
  const sourceStart = 0.5;
  const raw = {
    version: 1,
    referenceBlind: true,
    structureFrozen: true,
    role: 'guitar',
    structureIdentity: buildStructureIdentity(structureMap),
    capabilities: {
      roleRelevanceResolved: false,
      polyphonyResolved: false,
      durationResolution: 'partial-selected-pitch-release-only',
      instrumentIsolation: 'none',
      confidenceCalibration: 'heuristic-not-calibrated-probability',
    },
    onsets: [{
      sourceStart,
      nearestStructureSlot: snapTimestampToStructureMap(sourceStart, structureMap).projectedStart,
      onsetConfidence: 0.9,
      classification: 'unambiguous',
      selectedMidi: 64,
      sourceEnd: 0.75,
      durationSeconds: 0.25,
      durationConfidence: 0.8,
      candidates: [{ midi: 64, confidence: 0.9 }],
    }],
    provenance: {
      source: 'test',
      modelInvoked: false,
      gpuInvoked: false,
      legacyV143ScorerImported: false,
    },
  };

  const adapted = adaptStructureConditionedNoteEvidence(raw, structureMap);
  assert.equal(adapted.capabilities.durationResolution, 'partial');
  assert.equal(adapted.capabilities.durationResolutionDetail, 'partial-selected-pitch-release-only');
  assert.equal(adapted.metrics.durationResolvedEvidenceCount, 1);
  assert.equal(adapted.promotedEvents[0].duration, 0.25);
  assert.equal(adapted.promotedEvents[0].durationConfidence, 0.8);
});
