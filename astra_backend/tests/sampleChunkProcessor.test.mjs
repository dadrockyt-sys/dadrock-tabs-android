import test from 'node:test';
import assert from 'node:assert/strict';
import { processSampleChunks, SampleChunkProcessingError } from '../index.mjs';

const chunkOptions = { coreSamples: 3, leftContextSamples: 1, rightContextSamples: 1 };
function fixture(totalSamples = 11) {
  const source = Float64Array.from({ length: totalSamples }, (_, i) => i + 1);
  const output = [];
  return {
    source, output,
    args: {
      totalSamples, chunkOptions,
      read: ({ chunk }) => source.subarray(chunk.input.start, chunk.input.end),
      process: ({ samples }) => samples.map(x => x * 2),
      write: ({ samples, chunk }) => {
        assert.equal(output.length, chunk.output.start);
        output.push(...samples);
        return { writtenSamples: samples.length };
      },
    },
  };
}
async function failure(args) {
  try { await processSampleChunks(args); }
  catch (error) {
    assert.ok(error instanceof SampleChunkProcessingError);
    assert.notEqual(error.progress.status, 'complete');
    return error;
  }
  assert.fail('Expected explicit processing failure.');
}

test('processing reconstructs transformed samples across short windows, boundaries and tails', async () => {
  for (const length of [0, 1, 2, 3, 4, 5, 6, 7, 11, 13, 160000, 160001]) {
    const f = fixture(length);
    if (length > 100) f.args.chunkOptions = { coreSamples: 96000, leftContextSamples: 32000, rightContextSamples: 32000 };
    const result = await processSampleChunks(f.args);
    assert.equal(result.status, 'complete');
    assert.equal(result.writtenSamples, length);
    assert.equal(result.writtenChunks, result.plannedChunks);
    assert.equal(result.uncertainOutput, null);
    assert.deepEqual(f.output, Array.from(f.source, x => 2 * x));
  }
});

test('callbacks run sequentially and await a pending write before the next read', async () => {
  const f = fixture(7);
  const calls = [];
  let releaseWrite;
  let announceWrite;
  const enteredWrite = new Promise(resolve => { announceWrite = resolve; });
  const heldWrite = new Promise(resolve => { releaseWrite = resolve; });
  const original = { ...f.args };
  f.args.read = async context => { calls.push(`read${context.chunk.index}`); return original.read(context); };
  f.args.process = async context => { calls.push(`process${context.chunk.index}`); return original.process(context); };
  f.args.write = async context => {
    calls.push(`write${context.chunk.index}`);
    if (context.chunk.index === 0) { announceWrite(); await heldWrite; }
    return original.write(context);
  };
  const running = processSampleChunks(f.args);
  await enteredWrite;
  assert.deepEqual(calls, ['read0', 'process0', 'write0']);
  releaseWrite();
  await running;
  assert.deepEqual(calls, ['read0', 'process0', 'write0', 'read1', 'process1', 'write1', 'read2', 'process2', 'write2']);
});

test('reader and processor outputs reject missing, mis-sized, sparse and nonfinite samples', async () => {
  for (const callback of ['read', 'process']) {
    for (const bad of [undefined, null, [], [1, 2, 3], [1, 2, 3, 4, 5],
      [1, NaN, 3, 4], [1, Infinity, 3, 4], [1, '2', 3, 4], new Array(4), new Int32Array(4)]) {
      const f = fixture();
      f.args[callback] = () => bad;
      const error = await failure(f.args);
      assert.equal(error.progress.stage, callback);
      assert.equal(error.progress.writtenSamples, 0);
      assert.equal(error.progress.uncertainOutput, null);
      assert.deepEqual(f.output, []);
    }
  }
});

test('failed reads or processors retain the confirmed prefix and original cause', async () => {
  for (const callback of ['read', 'process']) {
    const f = fixture();
    const original = f.args[callback];
    const cause = new Error('Synthetic failure');
    f.args[callback] = context => {
      if (context.chunk.index === 1) throw cause;
      return original(context);
    };
    const error = await failure(f.args);
    assert.equal(error.cause, cause);
    assert.equal(error.progress.writtenSamples, 3);
    assert.equal(error.progress.writtenChunks, 1);
    assert.equal(error.progress.chunkIndex, 1);
    assert.equal(error.progress.uncertainOutput, null);
    assert.deepEqual(f.output, [2, 4, 6]);
  }
});

test('writer failure or bad acknowledgement marks attempted range uncertain without counting it', async () => {
  for (const ack of [undefined, {}, { writtenSamples: 1 }, { writtenSamples: '3' }, { writtenSamples: 4 }, 'throw']) {
    const f = fixture();
    const original = f.args.write;
    f.args.write = context => {
      if (context.chunk.index === 0) return original(context);
      // Simulate a sink that might have partly written before returning/throwing.
      f.output.push(context.samples[0]);
      if (ack === 'throw') throw new Error('Sink failed');
      return ack;
    };
    const error = await failure(f.args);
    assert.equal(error.progress.stage, 'write');
    assert.equal(error.progress.writtenSamples, 3);
    assert.deepEqual(error.progress.uncertainOutput, { start: 3, end: 6 });
    assert.equal(f.output.length, 4);
  }
});

test('cancellation before work or after read/process prevents subsequent callbacks', async () => {
  for (const where of ['before', 'read', 'process']) {
    const f = fixture();
    const controller = new AbortController();
    f.args.signal = controller.signal;
    const calls = [];
    for (const name of ['read', 'process', 'write']) {
      const original = f.args[name];
      f.args[name] = context => {
        calls.push(name);
        assert.equal(context.signal, controller.signal);
        const result = original(context);
        if (name === where) controller.abort('Stopped');
        return result;
      };
    }
    if (where === 'before') controller.abort('Stopped');
    const error = await failure(f.args);
    assert.equal(error.progress.status, 'cancelled');
    assert.equal(error.progress.writtenSamples, 0);
    assert.equal(error.progress.uncertainOutput, null);
    assert.deepEqual(calls, where === 'before' ? [] : where === 'read' ? ['read'] : ['read', 'process']);
  }
});

test('cancellation during a pending write waits for acknowledgement and preserves confirmed progress', async () => {
  for (const rejects of [false, true]) {
    const f = fixture(3);
    const controller = new AbortController();
    f.args.signal = controller.signal;
    let release;
    let entered;
    const wait = new Promise(resolve => { release = resolve; });
    const writing = new Promise(resolve => { entered = resolve; });
    const original = f.args.write;
    f.args.write = async context => {
      entered(); await wait;
      if (rejects) throw new Error('Write interrupted');
      return original(context);
    };
    let settled = false;
    const running = failure(f.args).then(error => { settled = true; return error; });
    await writing;
    controller.abort();
    await Promise.resolve();
    assert.equal(settled, false);
    release();
    const error = await running;
    assert.equal(error.progress.status, 'cancelled');
    assert.equal(error.progress.writtenSamples, rejects ? 0 : 3);
    assert.deepEqual(error.progress.uncertainOutput, rejects ? { start: 0, end: 3 } : null);
  }
});

test('callback buffer copies isolate the source and retained writer buffers', async () => {
  const f = fixture(7);
  const retained = [];
  let lastProcessorBuffer;
  f.args.process = ({ samples }) => {
    if (lastProcessorBuffer) lastProcessorBuffer.fill(-999);
    for (let i = 0; i < samples.length; i++) samples[i] *= 2;
    lastProcessorBuffer = samples;
    return samples;
  };
  f.args.write = ({ samples }) => { retained.push(samples); return { writtenSamples: samples.length }; };
  await processSampleChunks(f.args);
  lastProcessorBuffer.fill(-999);
  assert.deepEqual(Array.from(f.source), [1, 2, 3, 4, 5, 6, 7]);
  assert.deepEqual(retained.flatMap(x => [...x]), [2, 4, 6, 8, 10, 12, 14]);
});

test('buffer transfer cannot change the expected processor or writer sample count', async () => {
  for (const stage of ['process', 'write']) {
    const f = fixture(3);
    f.args[stage] = ({ samples }) => {
      structuredClone(samples, { transfer: [samples.buffer] });
      return stage === 'process' ? samples : { writtenSamples: samples.length };
    };
    const error = await failure(f.args);
    assert.equal(error.progress.stage, stage);
    assert.equal(error.progress.writtenSamples, 0);
  }
});

test('invalid configuration fails before callbacks, and empty input invokes none', async () => {
  const f = fixture(0);
  let calls = 0;
  f.args.read = f.args.process = f.args.write = () => { calls++; throw new Error('Unexpected'); };
  assert.equal((await processSampleChunks(f.args)).status, 'complete');
  for (const name of ['read', 'process', 'write']) {
    await assert.rejects(processSampleChunks({ ...f.args, [name]: null }), TypeError);
  }
  await assert.rejects(processSampleChunks({ ...f.args, signal: { aborted: false } }), TypeError);
  await assert.rejects(processSampleChunks({ ...f.args, totalSamples: -1 }), RangeError);
  assert.equal(calls, 0);
});
