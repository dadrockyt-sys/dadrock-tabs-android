import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createJimmyPaigeV8Pdf } from '../lib/tabRenderer/pdfV8.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

const ADAPTER_PATH = path.join(
  ROOT,
  'public',
  'gomyway-jimmy-paige-readonly-production-renderer-adapter.json'
);
const DRY_RUN_PATH = path.join(
  ROOT,
  'public',
  'gomyway-jimmy-paige-protected-production-renderer-dry-run.json'
);
const REPORT_PATH = path.join(
  ROOT,
  'public',
  'gomyway-jimmy-paige-production-renderer-shadow-invocation.json'
);

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, 'utf8'));
}

function assertion(condition, message) {
  if (!condition) throw new Error(message);
}

const adapterBytesBefore = await fs.readFile(ADAPTER_PATH);
const dryRunBytesBefore = await fs.readFile(DRY_RUN_PATH);
const rendererBytesBefore = await fs.readFile(
  path.join(ROOT, 'lib', 'tabRenderer', 'pdfV8.js')
);

const adapter = JSON.parse(adapterBytesBefore.toString('utf8'));
const dryRun = JSON.parse(dryRunBytesBefore.toString('utf8'));

assertion(adapter.adapterPassed === true, 'Read-only adapter is not passing');
assertion(
  adapter.readyForFeatureFlaggedNoOutputSmokeTest === true,
  'Read-only adapter is not ready'
);
assertion(dryRun.dryRunPassed === true, 'Protected production dry run is not passing');
assertion(
  dryRun.readyForProductionRendererShadowInvocation === true,
  'Dry run is not ready for renderer shadow invocation'
);

const adaptedRows = Array.isArray(adapter.adaptedRows)
  ? adapter.adaptedRows
  : [];
assertion(adaptedRows.length === 44, 'Expected exactly 44 adapted rows');

const rhythmEvents = [];
const measureNumbers = new Set();
let invalidRows = 0;

for (const row of adaptedRows) {
  const measureNumber = Number(row?.measureNumber);
  const attackNumber = Number(row?.attackNumber);
  const positionInMeasure = Number(row?.phase ?? 0);
  const frets = row?.fretsHighToLow;

  if (
    !Number.isInteger(measureNumber) ||
    !Number.isInteger(attackNumber) ||
    !Number.isFinite(positionInMeasure) ||
    !Array.isArray(frets) ||
    frets.length !== 6
  ) {
    invalidRows += 1;
    continue;
  }

  measureNumbers.add(measureNumber);

  frets.forEach((fret, stringIndex) => {
    if (fret === null || fret === undefined || fret === '' || fret === -1) {
      return;
    }

    const numericFret = Number(fret);
    if (!Number.isFinite(numericFret) || numericFret < 0) {
      invalidRows += 1;
      return;
    }

    rhythmEvents.push({
      measureNumber,
      attackNumber,
      eventIndex: rhythmEvents.length,
      positionInMeasure: Math.max(0, Math.min(0.999, positionInMeasure)),
      stringIndex,
      fret: Math.round(numericFret),
      shadowOnly: true,
      productionEligible: false,
    });
  });
}

assertion(invalidRows === 0, `Invalid adapter rows/events: ${invalidRows}`);
assertion(measureNumbers.size === 11, 'Expected 11 unique measures');

const totalMeasures = Math.max(...measureNumbers);
const sections = [
  { startMeasure: 33, label: 'Professional reference' },
  { startMeasure: 63, label: 'Held-out shadow' },
];

const pdfBytes = await createJimmyPaigeV8Pdf({
  songTitle: 'Gomyway — Jimmy Training Shadow',
  artistName: 'DadRock AI',
  transcriptionType: 'Rhythm Guitar',
  tuning: 'Standard Tuning',
  bpm: 136,
  timeSignature: '4/4',
  totalMeasures,
  sections,
  rhythmEvents,
});

const pdfBuffer = Buffer.from(pdfBytes);
const pdfHeaderValid = pdfBuffer.subarray(0, 8).toString('latin1').startsWith('%PDF-');
const pdfEofValid = pdfBuffer.toString('latin1').trimEnd().endsWith('%%EOF');
const pageCount = (pdfBuffer.toString('latin1').match(/\/Type \/Page\b/g) || []).length;

const adapterBytesAfter = await fs.readFile(ADAPTER_PATH);
const dryRunBytesAfter = await fs.readFile(DRY_RUN_PATH);
const rendererBytesAfter = await fs.readFile(
  path.join(ROOT, 'lib', 'tabRenderer', 'pdfV8.js')
);

const checks = {
  adapterPassed: adapter.adapterPassed === true,
  dryRunPassed: dryRun.dryRunPassed === true,
  adapterRows44: adaptedRows.length === 44,
  uniqueMeasures11: measureNumbers.size === 11,
  invalidRowsZero: invalidRows === 0,
  rendererInvokedInMemory: pdfBuffer.length > 0,
  pdfHeaderValid,
  pdfEofValid,
  pdfHasPages: pageCount > 0,
  adapterShaUnchanged: sha256(adapterBytesBefore) === sha256(adapterBytesAfter),
  dryRunShaUnchanged: sha256(dryRunBytesBefore) === sha256(dryRunBytesAfter),
  rendererSourceShaUnchanged:
    sha256(rendererBytesBefore) === sha256(rendererBytesAfter),
  outputPdfWrittenFalse: true,
  productionOutputCreatedFalse: true,
};

const passed = Object.values(checks).every(Boolean);

const report = {
  benchmarkVersion: 1,
  benchmarkType: 'production-renderer-shadow-invocation',
  rendererEntryPoint: 'lib/tabRenderer/pdfV8.js#createJimmyPaigeV8Pdf',
  checks,
  adaptedRowCount: adaptedRows.length,
  rhythmEventCount: rhythmEvents.length,
  uniqueMeasureCount: measureNumbers.size,
  highestMeasureNumber: totalMeasures,
  inMemoryPdfByteLength: pdfBuffer.length,
  inMemoryPdfSha256: sha256(pdfBuffer),
  inMemoryPdfPageCount: pageCount,
  shadowInvocationPassed: passed,
  rendererCalled: true,
  rendererOutputKeptInMemoryOnly: true,
  outputPdfWritten: false,
  productionOutputCreated: false,
  rendererSourceChanged: false,
  productionPromotionAllowed: false,
  professionalPdfRemainsScoringAuthority: true,
  readyForCapturedProductionRendererPreview: passed,
};

await fs.writeFile(REPORT_PATH, `${JSON.stringify(report, null, 2)}\n`, 'utf8');

console.log('Production renderer shadow invocation complete');
console.log('Renderer entry point: lib/tabRenderer/pdfV8.js#createJimmyPaigeV8Pdf');
console.log(`Adapter rows supplied: ${adaptedRows.length}/44`);
console.log(`Unique measures supplied: ${measureNumbers.size}/11`);
console.log(`Renderer events supplied: ${rhythmEvents.length}`);
console.log(`In-memory PDF bytes: ${pdfBuffer.length}`);
console.log(`In-memory PDF pages: ${pageCount}`);
console.log(`Adapter SHA unchanged: ${checks.adapterShaUnchanged}`);
console.log(`Dry-run SHA unchanged: ${checks.dryRunShaUnchanged}`);
console.log(`Renderer source SHA unchanged: ${checks.rendererSourceShaUnchanged}`);
console.log(`Shadow invocation passed: ${passed}`);
console.log('Renderer called: True');
console.log('Renderer output kept in memory only: True');
console.log('Output PDF written: False');
console.log('Production output created: False');
console.log('Production promotion allowed: False');
console.log('Professional PDF remains scoring authority: True');
console.log(`Output: ${path.relative(ROOT, REPORT_PATH)}`);
