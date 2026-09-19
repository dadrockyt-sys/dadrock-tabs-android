import test from 'node:test';
import assert from 'node:assert/strict';
import { runAstraChunkedAnalysis } from '../index.mjs';

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
function blocked(result) {
  assert.equal(result.astra.delivery.deliveryReady, false);
  assert.equal(result.generatedTab, '');
  assert.deepEqual(result.renderEvents, []);
  assert.deepEqual(result.events, []);
  assert.equal(result.astra.stages.events.status, 'not-run');
  assert.equal(result.astra.stages.structure.status, 'not-run');
  assert.equal(result.astra.stages.tablature.status, 'not-run');
}

test('complete chunks reconstruct samples but cannot supply musical or delivery evidence', async () => {
  const output = [];
  const result = await runAstraChunkedAnalysis({ request, chunks: options({
    write: ({ samples }) => { output.push(...samples); return { writtenSamples: samples.length }; },
  }), pipelineResult: { productShell: { generatedTab: 'untrusted' } }, deliveryPolicyVersion: 'untrusted' });
  assert.deepEqual(output, [0, 1, 2, 3, 4, 5, 6]);
  assert.equal(result.astra.stages.extraction.chunkProgress.writtenSamples, 7);
  assert.equal(result.astra.stages.extraction.chunkProgress.status, 'complete');
  assert.equal(result.astra.stages.extraction.status, 'partial');
  blocked(result);
});

test('mid-stream read and processor failure preserve confirmed prefix and stop the pipeline', async () => {
  for (const stage of ['read', 'process']) {
    const base = options();
    const result = await runAstraChunkedAnalysis({ request, chunks: options({
      [stage]: (args) => { if (args.chunk.index === 1) throw Error('synthetic failure'); return base[stage](args); },
    }) });
    const progress = result.astra.stages.extraction.chunkProgress;
    assert.equal(progress.writtenSamples, 3);
    assert.equal(progress.stage, stage);
    assert.equal(progress.uncertainOutput, null);
    assert.equal(result.astra.overallStatus, 'failed');
    blocked(result);
  }
});

test('uncertain sink range survives serialization without being counted as written', async () => {
  const result = await runAstraChunkedAnalysis({ request, chunks: options({
    write: ({ samples, chunk }) => chunk.index === 1 ? { writtenSamples: 1 } : { writtenSamples: samples.length },
  }) });
  const progress = JSON.parse(JSON.stringify(result)).astra.stages.extraction.chunkProgress;
  assert.equal(progress.writtenSamples, 3);
  assert.deepEqual(progress.uncertainOutput, { start: 3, end: 6 });
  blocked(result);
});

test('cancellation during acknowledged write retains progress and abstains', async () => {
  const controller = new AbortController();
  let writes = 0;
  const result = await runAstraChunkedAnalysis({ request, chunks: options({ signal: controller.signal,
    write: async ({ samples }) => { writes++; controller.abort(); return { writtenSamples: samples.length }; },
  }) });
  assert.equal(writes, 1);
  assert.equal(result.astra.overallStatus, 'abstained');
  assert.equal(result.astra.stages.extraction.chunkProgress.status, 'cancelled');
  assert.equal(result.astra.stages.extraction.chunkProgress.writtenSamples, 3);
  blocked(result);
});

test('pre-cancellation and empty input never create evidence', async () => {
  for (const chunks of [options({ signal: AbortSignal.abort() }), options({ totalSamples: 0 })]) {
    chunks.read = () => assert.fail('must not read');
    const result = await runAstraChunkedAnalysis({ request, chunks });
    assert.equal(result.astra.stages.extraction.chunkProgress.writtenSamples, 0);
    blocked(result);
  }
});

test('invalid request and chunk configuration reject before external callbacks', async () => {
  const chunks = options({ read: () => assert.fail('must not read') });
  await assert.rejects(runAstraChunkedAnalysis({ request: { ...request, transcriptionType: 'other' }, chunks }));
  await assert.rejects(runAstraChunkedAnalysis({ request, chunks: { ...chunks, totalSamples: -1 } }));
});
