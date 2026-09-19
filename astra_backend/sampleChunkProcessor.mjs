import { createSampleChunkPlan } from './sampleChunkPlan.mjs';

function copySamples(value, length, label) {
  if (!(Array.isArray(value) || value instanceof Float32Array || value instanceof Float64Array)) {
    throw new TypeError(`${label} must be an Array, Float32Array or Float64Array.`);
  }
  if (value.length !== length) throw new RangeError(`${label} length must be ${length}.`);
  const copy = new Float64Array(length);
  for (let i = 0; i < length; i++) {
    const sample = value[i];
    if (!Number.isFinite(sample)) throw new TypeError(`${label}[${i}] must be a finite number.`);
    copy[i] = sample;
  }
  return copy;
}

export class SampleChunkProcessingError extends Error {
  constructor(cause, progress) {
    super(`Chunk processing ${progress.status} during ${progress.stage}.`, { cause });
    this.name = 'SampleChunkProcessingError';
    this.progress = Object.freeze(progress);
  }
}

/** Sequential, callback-driven processing; no I/O or model implementation. */
export async function processSampleChunks({ totalSamples, chunkOptions, read, process, write, signal } = {}) {
  const plan = createSampleChunkPlan(totalSamples, chunkOptions);
  for (const [name, callback] of Object.entries({ read, process, write })) {
    if (typeof callback !== 'function') throw new TypeError(`${name} must be a function.`);
  }
  if (signal !== undefined && !(signal instanceof AbortSignal)) {
    throw new TypeError('signal must be an AbortSignal.');
  }
  let writtenSamples = 0;
  let writtenChunks = 0;
  let chunkIndex = null;
  let stage = 'before-read';
  let uncertainOutput = null;
  const checkCancellation = () => {
    if (signal?.aborted) throw signal.reason ?? new Error('Processing cancelled.');
  };
  const progress = (status) => ({
    status, totalSamples, plannedChunks: plan.chunkCount,
    writtenSamples, writtenChunks, chunkIndex, stage, uncertainOutput,
  });

  try {
    checkCancellation();
    for (const chunk of plan) {
      chunkIndex = chunk.index;
      stage = 'before-read';
      checkCancellation();
      stage = 'read';
      const inputLength = chunk.input.end - chunk.input.start;
      const input = copySamples(
        await read({ chunk, signal }), inputLength, 'Reader output',
      );
      stage = 'before-process';
      checkCancellation();
      stage = 'process';
      const processed = copySamples(
        await process({ samples: input, chunk, signal }), inputLength, 'Processor output',
      );
      stage = 'before-write';
      checkCancellation();
      // Writer receives its own buffer, not a view of callback-owned input/output.
      const samples = processed.slice(chunk.crop.start, chunk.crop.end);
      stage = 'write';
      uncertainOutput = chunk.output;
      const acknowledgement = await write({ samples, chunk, signal });
      if (!acknowledgement || acknowledgement.writtenSamples !== chunk.output.end - chunk.output.start) {
        throw new Error('Writer must acknowledge the exact cropped sample count.');
      }
      writtenSamples = chunk.output.end;
      writtenChunks += 1;
      uncertainOutput = null;
      stage = 'after-write';
      checkCancellation();
    }
    stage = 'complete';
    return Object.freeze(progress('complete'));
  } catch (cause) {
    throw new SampleChunkProcessingError(cause, progress(signal?.aborted ? 'cancelled' : 'failed'));
  }
}
