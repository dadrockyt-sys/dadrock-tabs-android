import test from 'node:test';
import assert from 'node:assert/strict';
import { runAstraSyntheticEventPipeline } from '../index.mjs';
import { buildStructureMap } from '../structureMap.mjs';
function fixture(role = 'lead') {
  return {
    request: { contractName: 'jimmy-paige-astra-analyzer-request', contractVersion: 1,
      requestId: 'events-v1', audioUrl: 'https://example.invalid/fixture', pathname: 'fixture',
      song: 'Synthetic', artist: 'Tests', transcriptionType: role,
      conditioning: { structurePrior: { tempoBpm: 'auto', timeSignature: 'auto', pickupBeats: 'auto', feel: 'auto' },
        instrumentConfig: { role, tuningMidi: role === 'bass' ? [28,33,38,43] : [40,45,50,55,59,64], capoFret: 0 } } },
    evidence: { kind: 'synthetic-extraction-v1', quality: 'unresolved', requestId: 'events-v1', role,
      sampleCount: 64, sampleRate: 32, sampleIdentity: 'sequence-v1', provenance: { source: 'synthetic', processor: 'identity' } },
    chunks: { totalSamples: 64, chunkOptions: { coreSamples: 20 },
      read: ({ chunk }) => new Float64Array(chunk.input.end - chunk.input.start),
      process: ({ samples }) => samples, write: ({ samples }) => ({ writtenSamples: samples.length }) },
    events: [{ eventId: 'later', start: 0.5, duration: 0.25, midi: role === 'bass' ? 43 : 67 },
      { eventId: 'first', start: 0, duration: 0.25, midi: role === 'bass' ? 40 : 64 }],
    structureMap: buildStructureMap({ durationSeconds: 2,
      tempoSegments: [{ start: 0, end: null, bpm: 120, confidence: 1 }],
      meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4, confidence: 1 }],
      feelSegments: [{ start: 0, end: null, feel: 'straight', confidence: 1 }],
      confidence: { overall: 1, tempo: 1, meter: 1, downbeats: 1, measures: 1, feel: 1 },
      provenance: { source: 'synthetic-events' } }),
  };
}
function blocked(result) {
  assert.equal(result.analysis.astra.delivery.deliveryReady, false);
  assert.equal(result.analysis.generatedTab, '');
  assert.deepEqual(result.analysis.renderEvents, []);
}
test('all roles connect complete chunks to diagnostic tablature preserving event identity', async () => {
  for (const role of ['lead', 'rhythm', 'bass']) {
    const input = fixture(role);
    const result = await runAstraSyntheticEventPipeline(input);
    assert.equal(result.downstream.status, 'complete');
    assert.ok(result.diagnostics.generatedTab.includes('RIFF'));
    assert.deepEqual(result.diagnostics.events.map(e => e.eventId), ['later', 'first']);
    assert.deepEqual(result.diagnostics.events.map(e => e.midi), input.events.map(e => e.midi));
    assert.deepEqual(result.diagnostics.events.map(e => e.sourceStart), [0.5, 0]);
    assert.equal(result.diagnostics.payloadContract.deliveryReady, false);
    assert.equal(result.diagnostics.customerDeliveryEligible, false);
    blocked(result);
  }
});
test('missing duration remains unresolved and empty events invent no notes', async () => {
  for (const events of [[{ eventId: 'unknown', start: 0, midi: 64 }], []]) {
    const result = await runAstraSyntheticEventPipeline({ ...fixture(), events });
    assert.equal(result.downstream.status, 'complete');
    assert.equal(result.diagnostics.events.length, events.length);
    if (events.length) {
      assert.equal(result.diagnostics.events[0].durationStatus, 'unresolved');
      assert.equal(result.diagnostics.events[0].sourceEnd, null);
    }
    blocked(result);
  }
});
test('invalid event timing and identity reject before reading samples', async () => {
  for (const patch of [{ start: -1 }, { start: 2 }, { start: NaN }, { start: '0' },
    { duration: 0 }, { duration: -1 }, { duration: Infinity }, { end: 3 },
    { end: 0.4 }, { midi: 1.5 }, { eventId: '' }]) {
    const input = fixture(); input.events[0] = { ...input.events[0], ...patch };
    input.chunks.read = () => assert.fail('must not read');
    await assert.rejects(runAstraSyntheticEventPipeline(input));
  }
  const input = fixture(); input.events[1].eventId = input.events[0].eventId;
  await assert.rejects(runAstraSyntheticEventPipeline(input));
});
test('end-only boundary duration is accepted; inconsistent duration and structure are rejected', async () => {
  const input = fixture(); input.events = [{ eventId: 'tail', start: 1.5, end: 2, midi: 64 }];
  const result = await runAstraSyntheticEventPipeline(input);
  assert.equal(result.diagnostics.events[0].sourceEnd, 2);
  input.events[0].duration = 0.25;
  await assert.rejects(runAstraSyntheticEventPipeline(input));
  const mismatch = fixture(); mismatch.evidence.sampleRate = 64;
  await assert.rejects(runAstraSyntheticEventPipeline(mismatch));
});
test('failed writes and cancellation never produce downstream event diagnostics', async () => {
  for (const cancel of [false, true]) {
    const input = fixture();
    if (cancel) input.chunks.signal = AbortSignal.abort();
    else input.chunks.write = () => ({ writtenSamples: 0 });
    const result = await runAstraSyntheticEventPipeline(input);
    assert.equal(result.downstream.status, 'not-run');
    assert.equal(result.diagnostics, null);
    blocked(result);
  }
});
test('events and structure are snapshotted before asynchronous sample callbacks', async () => {
  const input = fixture();
  input.chunks.read = ({ chunk }) => {
    input.events[0].midi = 1; input.structureMap.durationSeconds = 100;
    return new Float64Array(chunk.input.end - chunk.input.start);
  };
  const result = await runAstraSyntheticEventPipeline(input);
  assert.equal(result.diagnostics.events[0].midi, 67);
  blocked(result);
});
