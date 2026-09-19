import test from 'node:test';
import assert from 'node:assert/strict';
import { createSampleChunkPlan } from '../index.mjs';

function reconstruct(total, options) {
  const source = Array.from({ length: total }, (_, i) => i + 1);
  const result = [];
  const plan = createSampleChunkPlan(total, options);
  let count = 0;
  for (const chunk of plan) {
    assert.equal(chunk.index, count++);
    assert.equal(chunk.output.start, result.length);
    assert.ok(chunk.input.start >= 0 && chunk.input.end <= total);
    assert.ok(chunk.input.end - chunk.input.start <= plan.maxInputSamples);
    assert.ok(chunk.output.end > chunk.output.start);
    assert.equal(chunk.leftContext.end, chunk.output.start);
    assert.equal(chunk.rightContext.start, chunk.output.end);
    assert.equal(chunk.leftContext.start, chunk.input.start);
    assert.equal(chunk.rightContext.end, chunk.input.end);
    assert.equal(chunk.leftContext.end - chunk.leftContext.start,
      Math.min(plan.leftContextSamples, chunk.output.start));
    assert.equal(chunk.rightContext.end - chunk.rightContext.start,
      Math.min(plan.rightContextSamples, total - chunk.output.end));
    // Stand-in for a sample-aligned identity processor; uses no audio/model.
    const processed = source.slice(chunk.input.start, chunk.input.end);
    for (const sample of processed.slice(chunk.crop.start, chunk.crop.end)) result.push(sample);
  }
  assert.equal(count, plan.chunkCount);
  assert.deepEqual(result, source);
}

test('chunk coverage preserves short clips, exact five-second windows and one-sample tails', () => {
  const options = { coreSamples: 96000, leftContextSamples: 32000, rightContextSamples: 32000 };
  for (const length of [1, 31999, 32000, 95999, 96000, 96001, 159999, 160000, 160001, 192000, 192001]) {
    reconstruct(length, options);
  }
});

test('chunk coverage and context cropping hold across asymmetric windows and edge lengths', () => {
  for (let total = 0; total <= 75; total++) {
    for (const coreSamples of [1, 2, 3, 8, 17, 76]) {
      for (const [leftContextSamples, rightContextSamples] of [[0, 0], [0, 9], [11, 0], [2, 7], [100, 100]]) {
        reconstruct(total, { coreSamples, leftContextSamples, rightContextSamples });
      }
    }
  }
});

test('empty input schedules no processing', () => {
  const plan = createSampleChunkPlan(0, { coreSamples: 3 });
  assert.equal(plan.chunkCount, 0);
  assert.deepEqual([...plan], []);
});

test('plan validates invalid counts, unknown options and unsafe window sums immediately', () => {
  for (const value of [-1, 0.5, NaN, Infinity, '10', null, undefined, 10n, Number.MAX_SAFE_INTEGER + 1]) {
    assert.throws(() => createSampleChunkPlan(value, { coreSamples: 3 }), RangeError);
    assert.throws(() => createSampleChunkPlan(5, { coreSamples: value }), RangeError);
  }
  assert.throws(() => createSampleChunkPlan(5, { coreSamples: 0 }), RangeError);
  for (const options of [undefined, null, [], 1, '3']) {
    assert.throws(() => createSampleChunkPlan(5, options), TypeError);
  }
  for (const key of ['leftContextSamples', 'rightContextSamples']) {
    for (const value of [-1, 0.5, Infinity, NaN, null, 1n, '1', Number.MAX_SAFE_INTEGER]) {
      assert.throws(() => createSampleChunkPlan(5, { coreSamples: 3, [key]: value }), RangeError);
    }
  }
  assert.throws(() => createSampleChunkPlan(5, { coreSamples: 3, rightContexSamples: 1 }), TypeError);
});

test('huge plans are lazy and safe-integer edge windows retain exact coordinates', () => {
  const max = Number.MAX_SAFE_INTEGER;
  const lazy = createSampleChunkPlan(max, { coreSamples: 1 });
  assert.equal(lazy.chunkCount, max);
  const iterator = lazy[Symbol.iterator]();
  assert.deepEqual(iterator.next().value.output, { start: 0, end: 1 });
  assert.deepEqual(iterator.next().value.output, { start: 1, end: 2 });
  iterator.return();
  const chunks = [...createSampleChunkPlan(max, { coreSamples: max - 2, leftContextSamples: 1, rightContextSamples: 1 })];
  assert.equal(chunks.length, 2);
  assert.deepEqual(chunks[1].output, { start: max - 2, end: max });
  assert.deepEqual(chunks[1].input, { start: max - 3, end: max });
  assert.deepEqual(chunks[1].crop, { start: 1, end: 3 });
});

test('plans are repeatable and insulated from consumer mutation', () => {
  const options = { coreSamples: 3, leftContextSamples: 1 };
  const plan = createSampleChunkPlan(7, options);
  options.coreSamples = 100;
  const chunks = [...plan];
  assert.equal(chunks.length, 3);
  assert.throws(() => { plan.totalSamples = 100; }, TypeError);
  assert.throws(() => { chunks[0].crop.end = 100; }, TypeError);
  assert.deepEqual([...plan], chunks);
});
