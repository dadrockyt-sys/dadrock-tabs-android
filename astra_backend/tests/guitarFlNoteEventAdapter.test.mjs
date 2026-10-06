import test from 'node:test';
import assert from 'node:assert/strict';

import {
  adaptFrozenGuitarFlEvents,
  GUITAR_FL_EXPECTED_CHECKPOINT_SHA256,
} from '../guitarFlNoteEventAdapter.mjs';
import { runFreshDeterministicPipeline } from '../deterministicPipeline.mjs';
import { buildStructureMap } from '../structureMap.mjs';

const STANDARD_GUITAR = [40, 45, 50, 55, 59, 64];

function payload(events) {
  return {
    schema: 'astra-fresh-front-end-candidate-v1',
    trackStem: 'synthetic-stage-a',
    sourceAudioSha256: 'synthetic-audio-sha',
    frontEnd: 'xavriley_guitar_fl',
    identity: {
      checkpointSha256: GUITAR_FL_EXPECTED_CHECKPOINT_SHA256,
      effectiveOnsetThreshold: 0.3,
      effectiveOffsetThreshold: 0.3,
      effectiveFrameThreshold: 0.1,
      sampleRateHz: 16000,
      framesPerSecond: 100,
    },
    events,
    eventCount: events.length,
    referenceRead: false,
    predictionMutation: false,
    thresholdSearch: false,
    optimizerSteps: 0,
  };
}

function structureMap(durationSeconds = 4) {
  return buildStructureMap({
    durationSeconds,
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
    provenance: { source: 'guitar-fl-stage-a-fixture' },
  });
}

test('adapter preserves count, MIDI, onset, offset, order and duplicate simultaneous pitches', () => {
  const source = payload([
    { eventId: 0, start: 0.25, end: 0.5, pitch: 64, velocity: 90 },
    { eventId: 1, start: 0.5, end: 0.75, pitch: 67, velocity: 120 },
    { eventId: 2, start: 0.5, end: 0.8, pitch: 67, velocity: 20 },
  ]);

  const adapted = adaptFrozenGuitarFlEvents(source);

  assert.equal(adapted.events.length, 3);
  assert.deepEqual(adapted.events.map((e) => e.sourceEventIndex), [0, 1, 2]);
  assert.deepEqual(adapted.events.map((e) => e.midi), [64, 67, 67]);
  assert.deepEqual(adapted.events.map((e) => e.start), [0.25, 0.5, 0.5]);
  assert.deepEqual(adapted.events.map((e) => e.end), [0.5, 0.75, 0.8]);
  assert.deepEqual(adapted.events.slice(0, 2).map((e) => e.duration), [0.25, 0.25]);
  assert.ok(Math.abs(adapted.events[2].duration - 0.3) < 1e-12);
  assert.equal(adapted.adapterContract.duplicateSimultaneousPitchesDeduplicated, false);
  assert.equal(adapted.adapterContract.confidenceSynthesized, false);
  assert.equal(adapted.adapterContract.roleAuthority, false);
  assert.equal('confidence' in adapted.events[1], false);
  assert.equal('string' in adapted.events[1], false);
  assert.equal('fret' in adapted.events[1], false);
});

test('adapter fails closed on wrong checkpoint identity and any reference-facing/mutated payload', () => {
  const valid = payload([{ eventId: 0, start: 0.25, end: 0.5, pitch: 64 }]);

  assert.throws(
    () => adaptFrozenGuitarFlEvents({
      ...valid,
      identity: { ...valid.identity, checkpointSha256: 'bad' },
    }),
    /checkpoint SHA-256/,
  );
  assert.throws(() => adaptFrozenGuitarFlEvents({ ...valid, referenceRead: true }), /referenceRead/);
  assert.throws(() => adaptFrozenGuitarFlEvents({ ...valid, predictionMutation: true }), /predictionMutation/);
  assert.throws(() => adaptFrozenGuitarFlEvents({ ...valid, thresholdSearch: true }), /thresholdSearch/);
  assert.throws(() => adaptFrozenGuitarFlEvents({ ...valid, optimizerSteps: 1 }), /optimizerSteps/);
});

test('adapter rejects malformed, unsorted, invalid-pitch and nonpositive-duration events', () => {
  assert.throws(
    () => adaptFrozenGuitarFlEvents(payload([
      { eventId: 0, start: 0.5, end: 0.7, pitch: 64 },
      { eventId: 1, start: 0.25, end: 0.4, pitch: 65 },
    ])),
    /deterministically sorted/,
  );
  assert.throws(
    () => adaptFrozenGuitarFlEvents(payload([{ eventId: 0, start: 0.25, end: 0.5, pitch: 128 }])),
    /integer from 0 to 127/,
  );
  assert.throws(
    () => adaptFrozenGuitarFlEvents(payload([{ eventId: 0, start: 0.25, end: 0.25, pitch: 64 }])),
    /end must be greater/,
  );
});

test('adapted events enter deterministic pipeline without pitch/onset/source identity corruption', () => {
  const adapted = adaptFrozenGuitarFlEvents(payload([
    { eventId: 0, start: 0.0, end: 0.25, pitch: 64 },
    { eventId: 1, start: 0.5, end: 0.75, pitch: 67 },
    { eventId: 2, start: 1.0, end: 1.25, pitch: 71 },
  ]));

  const result = runFreshDeterministicPipeline({
    events: adapted.events,
    structureMap: structureMap(2),
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [...STANDARD_GUITAR],
      capoFret: 0,
    },
  });

  assert.deepEqual(result.sourceIdentity.map((e) => e.midi), [64, 67, 71]);
  assert.deepEqual(result.sourceIdentity.map((e) => e.start), [0, 0.5, 1]);
  assert.deepEqual(result.sourceIdentity.map((e) => e.end), [0.25, 0.75, 1.25]);
  assert.deepEqual(result.finalIdentity.map((e) => e.midi), [64, 67, 71]);
  assert.deepEqual(result.finalIdentity.map((e) => e.start), [0, 0.5, 1]);
  assert.deepEqual(result.finalIdentity.map((e) => e.end), [0.25, 0.75, 1.25]);
  assert.deepEqual(result.events.map((e) => e.sourceEventIndex), [0, 1, 2]);
});

test('adapter never supplies role evidence and does not bypass existing role-abstention logic', async () => {
  const adapted = adaptFrozenGuitarFlEvents(payload([
    { eventId: 0, start: 0.25, end: 0.5, pitch: 64 },
  ]));
  assert.equal(adapted.adapterContract.roleAuthority, false);
  assert.equal(adapted.events[0].provenance.roleAuthority, false);

  const { adaptRoleEvidenceStreams } = await import('../roleEvidenceIntegrationAdapter.mjs');
  assert.throws(
    () => adaptRoleEvidenceStreams({
      requestedRole: 'lead',
      roleEvidenceStatus: 'abstained',
      structureMap: structureMap(2),
      streams: {
        promotedCore: [{
          id: 'not-from-guitar-fl-adapter',
          start: 0.25,
          midi: 64,
          confidence: 1,
          onsetConfidence: 1,
        }],
      },
    }),
    /ABSTAINED_ROLE_EVIDENCE_CANNOT_PROMOTE/,
  );
});
