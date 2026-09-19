import inventory from './clapTextSchema.json' with { type: 'json' };

/** Text-only reference metadata, not a checkpoint reader or execution gate. */
export function validateClapTextMetadata(entries) {
  if (!Array.isArray(entries) || entries.length === 0) throw new TypeError('Metadata entries must be a nonempty array.');
  const expected = new Map(Object.entries(inventory.parameters).map(([key, shape]) => [key, { shape, dtype: 'float32' }]));
  expected.set('text_branch.embeddings.position_ids', { shape: [1, 514], dtype: 'int64' });
  const seen = new Set();
  let prefixed;
  for (const entry of entries) {
    if (!entry || typeof entry.key !== 'string') throw new TypeError('Each entry requires a key.');
    const hasPrefix = entry.key.startsWith('module.');
    const key = hasPrefix ? entry.key.slice(7) : entry.key;
    if (seen.has(key)) throw new TypeError(`Duplicate normalized key: ${key}`);
    if (prefixed !== undefined && prefixed !== hasPrefix) throw new TypeError('Mixed module prefixes.');
    prefixed = hasPrefix;
    seen.add(key);
    const spec = expected.get(key);
    if (!spec) throw new TypeError(`Unexpected text key: ${key}`);
    if (!Array.isArray(entry.shape) || entry.shape.length !== spec.shape.length
      || spec.shape.some((dimension, i) => entry.shape[i] !== dimension)) {
      throw new TypeError(`Shape mismatch: ${key}`);
    }
    if (entry.dtype !== spec.dtype) throw new TypeError(`Reference dtype mismatch: ${key}`);
  }
  const missing = [...expected.keys()].filter(key => !seen.has(key));
  if (missing.length) throw new TypeError(`Missing text keys: ${missing.join(', ')}`);
  return Object.freeze({ status: 'reference-metadata-match', parameterCount: 203, bufferCount: 1,
    checkpointVerified: false, executionReady: false, tensorValuesVerified: false });
}
