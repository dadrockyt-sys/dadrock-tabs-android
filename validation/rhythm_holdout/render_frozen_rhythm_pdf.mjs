#!/usr/bin/env node

import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { PDFDocument } from 'pdf-lib';
import { projectV143RenderEvents } from '../../lib/v143RenderContract.js';

const snapshotPath = process.argv[2] || '.canary/rhythm-freeze/rhythm-frozen-analysis.json';
const outputDir = process.argv[3] || '.canary/rhythm-freeze/pdf';
const rendererModulePath = process.argv[4];

if (!rendererModulePath) {
  throw new Error('renderer module path is required');
}

const frozen = JSON.parse(await fs.readFile(snapshotPath, 'utf8'));
if (frozen?.instrument !== 'rhythm') {
  throw new Error('frozen analysis is not Rhythm');
}
if (
  frozen?.safety?.referenceFree !== true ||
  frozen?.safety?.professionalReferenceUsed !== false ||
  frozen?.safety?.referenceRuntimeInputUsed !== false
) {
  throw new Error('frozen analysis fails anti-leakage safety contract');
}

const renderEvents = frozen?.renderEvents;
if (!Array.isArray(renderEvents) || renderEvents.length === 0) {
  throw new Error('frozen analysis contains no render events');
}

// The professional renderer internally uses this same projection helper. Prove
// before rendering that its validation pass is exactly idempotent on the frozen
// authenticated stream, including eventIndex/legato relationships.
const rendererProjection = projectV143RenderEvents(renderEvents);
assert.deepEqual(
  rendererProjection,
  renderEvents,
  'professional renderer would alter the frozen authenticated event stream'
);

const moduleUrl = pathToFileURL(path.resolve(rendererModulePath)).href;
const rendererModule = await import(moduleUrl);
if (typeof rendererModule.createV143RhythmPdf !== 'function') {
  throw new Error('renderer module does not export createV143RhythmPdf');
}

const metadata = frozen?.metadata || {};
const common = {
  song: 'Rhythm Professional Holdout Canary',
  artist: 'DadRock Tabs',
  generatedTab: '',
  renderEvents,
  tuning: metadata.tuning || 'E Standard',
  tempo: metadata.tempoBpm || 120,
  timeSignature: metadata.timeSignature || '4/4',
  keySignature: '',
};

const fullBytes = await rendererModule.createV143RhythmPdf({
  ...common,
  preview: false,
});
const previewBytes = await rendererModule.createV143RhythmPdf({
  ...common,
  preview: true,
  previewSystems: 4,
});

await fs.mkdir(outputDir, { recursive: true });
const fullPath = path.join(outputDir, 'full-frozen-rhythm.pdf');
const previewPath = path.join(outputDir, 'preview-frozen-rhythm.pdf');
const evidencePath = path.join(outputDir, 'pdf-event-evidence.json');
await fs.writeFile(fullPath, fullBytes);
await fs.writeFile(previewPath, previewBytes);

const fullDocument = await PDFDocument.load(fullBytes);
const previewDocument = await PDFDocument.load(previewBytes);
const evidence = {
  schemaVersion: 1,
  gate: 'rhythm-frozen-professional-pdf-render',
  instrument: 'rhythm',
  referenceOpened: false,
  renderer: 'createV143RhythmPdf',
  rendererProjectionExactlyEqual: true,
  renderEventCount: renderEvents.length,
  renderEvents,
  fullPdfBytes: fullBytes.length,
  previewPdfBytes: previewBytes.length,
  fullPageCount: fullDocument.getPageCount(),
  previewPageCount: previewDocument.getPageCount(),
  fullPdfHeaderValid:
    Buffer.from(fullBytes).subarray(0, 5).toString('ascii') === '%PDF-',
  previewPdfHeaderValid:
    Buffer.from(previewBytes).subarray(0, 5).toString('ascii') === '%PDF-',
  productionModified: false,
  productionPromotionAuthorized: false,
};

evidence.passed = Boolean(
  evidence.rendererProjectionExactlyEqual &&
  evidence.fullPdfHeaderValid &&
  evidence.previewPdfHeaderValid &&
  evidence.fullPdfBytes > 20000 &&
  evidence.previewPdfBytes > 20000 &&
  evidence.fullPageCount >= 1 &&
  evidence.previewPageCount >= 1
);

await fs.writeFile(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  ...evidence,
  renderEvents: `[${renderEvents.length} frozen events]`,
}, null, 2));

if (!evidence.passed) {
  process.exitCode = 1;
}
