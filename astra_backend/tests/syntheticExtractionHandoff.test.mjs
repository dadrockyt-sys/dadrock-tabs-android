import test from 'node:test';
import assert from 'node:assert/strict';
import { runAstraSyntheticExtraction } from '../index.mjs';
const request = {
  contractName: 'jimmy-paige-astra-analyzer-request', contractVersion: 1,
  requestId: 'chunk-integration', audioUrl: 'https://example.invalid/synthetic',
  pathname: 'synthetic', song: 'Fixture', artist: 'Test', transcriptionType: 'bass',
  conditioning: {
    structurePrior: { tempoBpm: 'auto', timeSignature: 'auto', pickupBeats: 'auto', feel: 'auto' },
    instrumentConfig: { role: 'bass', tuningMidi: 'auto', capoFret: 'auto' },
  },
};
const options = (overrides = {}) => ({
  totalSamples: 7, chunkOptions: { coreSamples: 3, leftContextSamples: 1, rightContextSamples: 1 },
  read: ({ chunk }) => Array.from({ length: chunk.input.end - chunk.input.start }, (_, i) => chunk.input.start + i),
  process: ({ samples }) => samples,
  write: ({ samples }) => ({ writtenSamples: samples.length }),
  ...overrides,
});
const evidence = () => ({ kind: 'synthetic-extraction-v1', quality: 'unresolved',
  requestId: request.requestId, role: 'bass', sampleCount: 7, sampleRate: 32000,
  sampleIdentity: 'fixture-samples-v1', provenance: { source: 'synthetic-sequence', processor: 'identity-v1' } });

test('synthetic handoff runs after final write with isolated evidence and cannot publish callback output', async () => {
  let writes = 0;
  const raw = evidence();
  const result = await runAstraSyntheticExtraction({ request, evidence: raw,
    chunks: options({ write: ({ samples }) => { writes++; raw.provenance.source = 'mutated'; return { writtenSamples: samples.length }; } }),
    downstream: async ({ evidence: frozen, progress }) => {
      assert.equal(writes, 3);
      assert.equal(progress.writtenSamples, 7);
      assert.equal(frozen.provenance.source, 'synthetic-sequence');
      assert.throws(() => { frozen.quality = 'validated'; }, TypeError);
      return { generatedTab: 'must not publish', deliveryReady: true };
    },
  });
  assert.equal(result.downstream.status, 'complete');
  assert.equal(result.analysis.generatedTab, '');
  assert.equal(result.analysis.astra.delivery.deliveryReady, false);
  assert.deepEqual(result.analysis.renderEvents, []);
});

test('invalid evidence rejects before any sample callback', async () => {
  for (const patch of [{ kind: 'real' }, { quality: 'validated' }, { role: 'lead' },
    { requestId: 'other' }, { sampleCount: 6 }, { sampleCount: 0 }, { sampleRate: 0 },
    { sampleRate: 1.5 }, { sampleIdentity: '' }, { provenance: {} }]) {
    await assert.rejects(runAstraSyntheticExtraction({ request, evidence: { ...evidence(), ...patch },
      chunks: options({ read: () => assert.fail('must not read') }), downstream: () => assert.fail('must not run') }));
  }
});

test('failed and cancelled chunks never call downstream', async () => {
  for (const patch of [
    { process: () => { throw Error('failure'); } },
    { write: () => ({ writtenSamples: 1 }) },
    { signal: AbortSignal.abort() },
  ]) {
    const result = await runAstraSyntheticExtraction({ request, evidence: evidence(), chunks: options(patch),
      downstream: () => assert.fail('must not run') });
    assert.equal(result.downstream.status, 'not-run');
    assert.equal(result.analysis.astra.delivery.deliveryReady, false);
  }
});

test('downstream failure and cancellation remain explicit diagnostics with blocked analysis', async () => {
  for (const cancel of [false, true]) {
    const controller = new AbortController();
    const result = await runAstraSyntheticExtraction({ request, evidence: evidence(),
      chunks: options({ signal: controller.signal }), downstream: async () => {
        if (cancel) controller.abort();
        else throw Error('private diagnostic');
      } });
    assert.equal(result.downstream.status, cancel ? 'cancelled' : 'failed');
    assert.equal(result.analysis.astra.delivery.deliveryReady, false);
    assert.equal(JSON.stringify(result).includes('private diagnostic'), false);
  }
});
