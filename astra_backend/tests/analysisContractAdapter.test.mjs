import test from 'node:test';
import assert from 'node:assert/strict';

import {
  buildAstraAnalyzerResult,
  normalizeAstraAnalyzerRequest,
} from '../analysisContractAdapter.mjs';
import { runFreshDeterministicPipeline } from '../deterministicPipeline.mjs';
import { buildStructureMap } from '../structureMap.mjs';

const TUNINGS = {
  lead: [40, 45, 50, 55, 59, 64],
  rhythm: [40, 45, 50, 55, 59, 64],
  bass: [28, 33, 38, 43],
};

function request(role, id = `fixture-${role}`) {
  return {
    contractName: 'jimmy-paige-astra-analyzer-request',
    contractVersion: 1,
    requestId: id,
    audioUrl: 'https://example.invalid/audio-fixture.wav',
    pathname: `fixtures/${id}.wav`,
    song: 'Synthetic Contract Fixture',
    artist: 'DadRock Tests',
    transcriptionType: role,
    conditioning: {
      structurePrior: {
        tempoBpm: 120,
        timeSignature: { numerator: 4, denominator: 4 },
        pickupBeats: 0,
        feel: 'straight',
      },
      instrumentConfig: {
        role,
        tuningMidi: [...TUNINGS[role]],
        capoFret: 0,
      },
    },
  };
}

function completeStages(rolePresence = 'present') {
  return {
    input: { status: 'complete', blockers: [], synthetic: true },
    extraction: { status: 'complete', blockers: [], rolePresence, synthetic: true },
    events: { status: 'complete', blockers: [], synthetic: true },
    structure: { status: 'complete', blockers: [], synthetic: true },
  };
}

function structureMap(feel = 'straight') {
  return buildStructureMap({
    durationSeconds: 2,
    tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 1 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 1 }],
    feelSegments: [{ start: 0, end: null, feel, confidence: 1 }],
    confidence: { overall: 1, tempo: 1, meter: 1, downbeats: 1, measures: 1, feel: 1 },
    provenance: { source: 'astra-synthetic-contract-fixture' },
  });
}

function pipeline(role, events, options = {}) {
  return runFreshDeterministicPipeline({
    events,
    structureMap: structureMap(options.feel),
    instrumentConfig: { role, tuningMidi: [...TUNINGS[role]], capoFret: 0 },
    fretboardPathOptions: options.fretboardPathOptions,
    productShell: { upstreamEvidenceReady: true },
  });
}

test('request normalization accepts all product roles and preserves server-owned conditioning', () => {
  for (const role of ['lead', 'rhythm', 'bass']) {
    const normalized = normalizeAstraAnalyzerRequest(request(role));
    assert.equal(normalized.transcriptionType, role);
    assert.equal(normalized.conditioning.instrumentConfig.role, role);
    assert.deepEqual(normalized.conditioning.instrumentConfig.tuningMidi, TUNINGS[role]);
  }
});

test('complete lead fixture reaches delivery only with complete stages and a policy identity', () => {
  const result = buildAstraAnalyzerResult({
    request: request('lead'),
    stages: completeStages(),
    pipelineResult: pipeline('lead', [
      { start: 0, duration: 0.25, midi: 64 },
      { start: 0.5, duration: 0.25, midi: 67 },
    ]),
    deliveryPolicyVersion: 'astra-synthetic-fixture-v1',
    lineage: {
      separator: 'synthetic-no-separator',
      eventInference: 'synthetic-authoritative-events',
      structure: 'synthetic-authoritative-structure',
    },
  });

  assert.equal(result.astra.overallStatus, 'complete');
  assert.equal(result.astra.delivery.deliveryReady, true);
  assert.equal(result.renderEvents.length, 2);
  assert.equal(result.events.length, 2);
  assert.ok(result.generatedTab.includes('RIFF 1'));
  assert.deepEqual(result.events.map((event) => event.durationStatus), ['resolved', 'resolved']);
});

test('complete bass fixture preserves the requested role through the product payload', () => {
  const result = buildAstraAnalyzerResult({
    request: request('bass'),
    stages: completeStages(),
    pipelineResult: pipeline('bass', [
      { start: 0, duration: 0.5, midi: 40 },
      { start: 0.5, duration: 0.5, midi: 43 },
    ]),
    deliveryPolicyVersion: 'astra-synthetic-fixture-v1',
  });

  assert.equal(result.transcriptionType, 'bass');
  assert.equal(result.astra.overallStatus, 'complete');
  assert.equal(result.astra.delivery.deliveryReady, true);
  assert.equal(result.events.every((event) => event.sourceIdentity.startsWith('fixture-bass:source:')), true);
});

test('rhythm fixture with unresolved fingering remains partial and cannot render to the customer', () => {
  const result = buildAstraAnalyzerResult({
    request: request('rhythm'),
    stages: completeStages(),
    pipelineResult: pipeline('rhythm', [
      { start: 0, duration: 0.25, midi: 64 },
      { start: 0, duration: 0.25, midi: 65 },
    ], {
      fretboardPathOptions: { policy: { maxFrettedSpan: 0, maxAdjacentFretDelta: 0 } },
    }),
    deliveryPolicyVersion: 'astra-synthetic-fixture-v1',
  });

  assert.equal(result.astra.overallStatus, 'partial');
  assert.equal(result.astra.delivery.deliveryReady, false);
  assert.deepEqual(result.renderEvents, []);
  assert.ok(result.astra.delivery.blockers.includes('tablature:TABLATURE_UPSTREAM_OR_INTEGRITY_BLOCKED'));
});

test('absent requested role abstains without inventing tablature', () => {
  const stages = completeStages();
  stages.extraction = { status: 'abstained', blockers: ['REQUESTED_ROLE_ABSENT'], rolePresence: 'absent' };
  stages.events = { status: 'not-run', blockers: ['EXTRACTION_NOT_AVAILABLE'] };
  stages.structure = { status: 'partial', blockers: ['ROLE_STRUCTURE_NOT_AVAILABLE'] };
  const result = buildAstraAnalyzerResult({ request: request('bass', 'fixture-absent'), stages });

  assert.equal(result.astra.overallStatus, 'abstained');
  assert.equal(result.astra.delivery.deliveryReady, false);
  assert.equal(result.generatedTab, '');
  assert.deepEqual(result.events, []);
});

test('input infrastructure failure reports failed and never masquerades as a musical result', () => {
  const stages = {
    input: { status: 'failed', blockers: ['AUDIO_DECODE_FAILED'] },
    extraction: { status: 'not-run', blockers: ['INPUT_NOT_AVAILABLE'], rolePresence: 'uncertain' },
    events: { status: 'not-run', blockers: ['INPUT_NOT_AVAILABLE'] },
    structure: { status: 'not-run', blockers: ['INPUT_NOT_AVAILABLE'] },
  };
  const result = buildAstraAnalyzerResult({ request: request('lead', 'fixture-failed'), stages });

  assert.equal(result.astra.overallStatus, 'failed');
  assert.equal(result.astra.delivery.deliveryReady, false);
  assert.deepEqual(result.renderEvents, []);
});

test('renderer-incompatible triplet output remains partial despite valid deterministic event integrity', () => {
  const result = buildAstraAnalyzerResult({
    request: request('lead', 'fixture-triplet'),
    stages: completeStages(),
    pipelineResult: pipeline('lead', [{ start: 1 / 6, duration: 1 / 6, midi: 64 }], { feel: 'triplet' }),
    deliveryPolicyVersion: 'astra-synthetic-fixture-v1',
  });

  assert.equal(result.astra.overallStatus, 'partial');
  assert.equal(result.astra.delivery.deliveryReady, false);
  assert.deepEqual(result.renderEvents, []);
  assert.ok(result.astra.delivery.blockers.includes('tablature:LEGACY_RENDER_SUBDIVISION_UNSUPPORTED'));
});

test('request role mismatch fails before any backend work', () => {
  const invalid = request('lead');
  invalid.conditioning.instrumentConfig.role = 'bass';
  assert.throws(() => normalizeAstraAnalyzerRequest(invalid), /must match/);
});
