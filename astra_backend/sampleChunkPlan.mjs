function sampleCount(value, name, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) {
    throw new RangeError(`${name} must be a safe integer >= ${minimum}.`);
  }
  return value;
}

const range = (start, end) => Object.freeze({ start, end });

/**
 * Lazy, repeatable sample-index plan. All ranges are half-open.
 * Input/output use global coordinates; crop uses input-local coordinates.
 * Context clips at file edges; no padding, resampling, or inference is performed.
 * A consumer must produce one aligned output sample per input sample before crop.
 */
export function createSampleChunkPlan(totalSamples, options) {
  sampleCount(totalSamples, 'totalSamples');
  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError('Chunk options must be an object.');
  }
  const allowed = new Set(['coreSamples', 'leftContextSamples', 'rightContextSamples']);
  for (const key of Object.keys(options)) {
    if (!allowed.has(key)) throw new TypeError(`Unknown chunk option: ${key}.`);
  }
  const coreSamples = sampleCount(options.coreSamples, 'coreSamples', 1);
  const leftContextSamples = sampleCount(
    options.leftContextSamples === undefined ? 0 : options.leftContextSamples, 'leftContextSamples',
  );
  const rightContextSamples = sampleCount(
    options.rightContextSamples === undefined ? 0 : options.rightContextSamples, 'rightContextSamples',
  );
  // Reject overflow even when a short input would happen to clip it away.
  const maxInputSamples = sampleCount(
    coreSamples + leftContextSamples + rightContextSamples, 'maximum input window', 1,
  );
  const chunkCount = Math.floor(totalSamples / coreSamples)
    + (totalSamples % coreSamples === 0 ? 0 : 1);

  return Object.freeze({
    totalSamples,
    coreSamples,
    leftContextSamples,
    rightContextSamples,
    maxInputSamples,
    chunkCount,
    *[Symbol.iterator]() {
      let outputStart = 0;
      let index = 0;
      while (outputStart < totalSamples) {
        // Subtract before adding to avoid overflowing near MAX_SAFE_INTEGER.
        const outputEnd = outputStart + Math.min(coreSamples, totalSamples - outputStart);
        const inputStart = outputStart - Math.min(leftContextSamples, outputStart);
        const inputEnd = outputEnd + Math.min(rightContextSamples, totalSamples - outputEnd);
        yield Object.freeze({
          index,
          input: range(inputStart, inputEnd),
          output: range(outputStart, outputEnd),
          crop: range(outputStart - inputStart, outputEnd - inputStart),
          leftContext: range(inputStart, outputStart),
          rightContext: range(outputEnd, inputEnd),
        });
        outputStart = outputEnd;
        index += 1;
      }
    },
  });
}
