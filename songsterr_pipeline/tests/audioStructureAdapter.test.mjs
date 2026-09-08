import test from 'node:test';
import assert from 'node:assert/strict';

import { adaptFullMixtureStructureAnalysis } from '../audioStructureAdapter.mjs';

function rawAnalysis(overrides = {}) {
  return {
    version: 1,
    referenceBlind: true,
    audioSource: 'synthetic-audio-fixture.wav',
    durationSeconds: 4.5,
    tempo: {
      bpm: 120,
      beatUnit: 'quarter-note',
      confidence: 0.94,
    },
    selectedMeter: {
      numerator: 4,
      denominator: 4,
      confidence: 0.82,
    },
    meterCandidates: [
      { numerator: 4, denominator: 4, score: 0.8 },
      { numerator: 3, denominator: 4, score: 0.3 },
    ],
    feel: {
      feel: 'straight',
      confidence: 0.76,
      diagnostics: { straightError: 0.02, tripletError: 0.11 },
    },
    pickup: {
      durationSeconds: 0.5,
      confidence: 0.8,
    },
    beatTimes: [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4],
    confidence: { overall: 0.76 },
    provenance: {
      source: 'synthetic-full-mixture-analysis',
      analyzerVersion: 1,
    },
    diagnostics: { beatFitRmseSeconds: 0 },
    ...overrides,
  };
}

test('audio structure adapter creates a first-class reference-blind map aligned to observed beats', () => {
  const result = adaptFullMixtureStructureAnalysis(rawAnalysis());

  assert.equal(result.adapterContract.referenceBlind, true);
  assert.equal(result.adapterContract.structureFrozenBeforeNoteInference, true);
  assert.equal(result.adapterContract.legacyV143ScorerImported, false);
  assert.equal(result.structureMap.referenceBlind, true);
  assert.equal(result.structureMap.pickupDurationSeconds, 0.5);
  assert.equal(result.structureMap.measures[0].pickup, true);
  assert.equal(result.structureMap.downbeats[0].time, 0.5);
  assert.equal(result.structureMap.measures[1].timeSignature.numerator, 4);
  assert.equal(result.structureMap.measures[1].tempoBpm, 120);
  assert.equal(result.structureMap.measures[1].feel, 'straight');
  assert.equal(result.alignmentDiagnostics.observedBeatCount, 8);
  assert.equal(result.alignmentDiagnostics.meanAbsoluteErrorSeconds, 0);
  assert.equal(result.alignmentDiagnostics.rootMeanSquareErrorSeconds, 0);
});

test('audio structure adapter preserves raw confidence, candidates, diagnostics, and provenance without scoring them', () => {
  const result = adaptFullMixtureStructureAnalysis(rawAnalysis());

  assert.equal(result.structureMap.confidence.overall, 0.76);
  assert.equal(result.structureMap.confidence.tempo, 0.94);
  assert.equal(result.structureMap.confidence.meter, 0.82);
  assert.equal(result.structureMap.confidence.feel, 0.76);
  assert.equal(result.evidence.meterCandidates.length, 2);
  assert.equal(result.evidence.upstreamDiagnostics.beatFitRmseSeconds, 0);
  assert.equal(result.structureMap.provenance.upstream.source, 'synthetic-full-mixture-analysis');
});

test('audio structure adapter fails closed on non-reference-blind input', () => {
  assert.throws(() => adaptFullMixtureStructureAnalysis(rawAnalysis({
    referenceBlind: false,
  })), /reference-blind/);
});

test('audio structure adapter fails closed when tempo/meter beat-unit semantics are not yet representable', () => {
  assert.throws(() => adaptFullMixtureStructureAnalysis(rawAnalysis({
    tempo: { bpm: 120, beatUnit: 'dotted-quarter', confidence: 0.8 },
  })), /TEMPO_BEAT_UNIT_UNSUPPORTED/);

  assert.throws(() => adaptFullMixtureStructureAnalysis(rawAnalysis({
    selectedMeter: { numerator: 6, denominator: 8, confidence: 0.8 },
  })), /METER_DENOMINATOR_UNSUPPORTED/);
});

test('audio structure adapter is deterministic', () => {
  const first = adaptFullMixtureStructureAnalysis(rawAnalysis());
  const second = adaptFullMixtureStructureAnalysis(rawAnalysis());
  assert.deepEqual(first, second);
});
