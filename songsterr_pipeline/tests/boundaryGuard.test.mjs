import test from 'node:test';
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');

function importSpecifiers(source) {
  return [...source.matchAll(/\bfrom\s+['"]([^'"]+)['"]/g)].map((match) => match[1]);
}

test('fresh source namespace remains isolated from archived/model-bearing runtime dependencies', async () => {
  const files = (await readdir(ROOT))
    .filter((name) => name.endsWith('.mjs'))
    .sort();

  assert.ok(files.length > 0);

  for (const name of files) {
    const source = await readFile(join(ROOT, name), 'utf8');
    const imports = importSpecifiers(source);

    for (const specifier of imports) {
      assert.ok(
        specifier.startsWith('./'),
        `${name} imports non-local runtime dependency: ${specifier}`,
      );
      assert.doesNotMatch(
        specifier.toLowerCase(),
        /(v143|gomyway|modal|analyzer|professional|reference)/,
        `${name} crosses the fresh pipeline boundary through ${specifier}`,
      );
    }

    assert.doesNotMatch(source, /\bfetch\s*\(/, `${name} must not perform network fetches.`);
    assert.doesNotMatch(source, /\bXMLHttpRequest\b/, `${name} must not perform browser network requests.`);
    assert.doesNotMatch(source, /\bchild_process\b/, `${name} must not spawn processes.`);
    assert.doesNotMatch(source, /\bexecFile\s*\(/, `${name} must not execute external binaries.`);
    assert.doesNotMatch(source, /\bspawn\s*\(/, `${name} must not execute external binaries.`);
  }
});
