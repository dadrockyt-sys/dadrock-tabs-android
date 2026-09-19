import test from 'node:test';
import assert from 'node:assert/strict';
import inventory from '../../docs/astra/CLAP_TEXT_KEY_INVENTORY_V1.json' with { type: 'json' };
import { validateClapTextMetadata } from '../index.mjs';
const fixture = () => [...Object.entries(inventory.parameters).map(([key, shape]) => ({ key, shape: [...shape], dtype: 'float32' })),
  { key: 'text_branch.embeddings.position_ids', shape: [1, 514], dtype: 'int64' }];

test('reference inventory accepts uniform prefixes without authorizing execution or verifying tensors', () => {
  for (const prefix of ['', 'module.']) {
    const result = validateClapTextMetadata(fixture().map(e => ({ ...e, key: prefix + e.key })));
    assert.equal(result.parameterCount, 203);
    assert.equal(result.bufferCount, 1);
    assert.equal(result.executionReady, false);
    assert.equal(result.checkpointVerified, false);
  }
});
test('metadata rejects missing, extra, duplicate and normalized collision keys', () => {
  const full = fixture();
  for (const entries of [full.slice(1), full.slice(0, -1), [...full, full[0]],
    [...full, { ...full[0], key: 'module.' + full[0].key }],
    [...full, { key: 'text_branch.embeddings.token_type_ids', shape: [1, 514], dtype: 'int64' }]]) {
    assert.throws(() => validateClapTextMetadata(entries));
  }
});
test('metadata rejects mixed prefixes, shape and dtype errors and malformed inputs', () => {
  for (const patch of [{ key: 'module.text_branch.embeddings.word_embeddings.weight' },
    { shape: [50265, 767] }, { shape: ['50265', 768] }, { shape: [50265, 768, 1] },
    { dtype: 'float16' }, { dtype: undefined }]) {
    const entries = fixture(); entries[0] = { ...entries[0], ...patch };
    assert.throws(() => validateClapTextMetadata(entries));
  }
  for (const value of [null, {}, [], [null]]) assert.throws(() => validateClapTextMetadata(value));
  const entries = fixture(); entries.at(-1).dtype = 'float32';
  assert.throws(() => validateClapTextMetadata(entries));
});
