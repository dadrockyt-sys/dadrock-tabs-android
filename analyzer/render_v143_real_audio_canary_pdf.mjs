import fs from 'node:fs/promises';
import path from 'node:path';

import { PDFDocument } from 'pdf-lib';
import { buildJimmyPaigeAnalysisPayload } from '../lib/jimmyPaigeAnalysisPayload.js';
import { createV143RhythmPdf } from '../lib/createV143RhythmPdf.js';

const INPUT_PATH = process.argv[2] || '.canary/v143-product-output.json';
const ARTIFACT_DIR =
  process.argv[3] || '.canary/ai-tab-real-audio-pdf';
const VALIDATION_PATH =
  process.argv[4] ||
  'debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json';

async function writeValidation(result) {
  await fs.mkdir(path.dirname(VALIDATION_PATH), {
    recursive: true,
  });
  await fs.writeFile(
    VALIDATION_PATH,
    `${JSON.stringify(result, null, 2)}\n`,
    'utf8'
  );
  console.log(JSON.stringify(result, null, 2));
}

const raw = JSON.parse(
  await fs.readFile(INPUT_PATH, 'utf8')
);

const structured = buildJimmyPaigeAnalysisPayload(
  raw,
  {
    transcriptionType: 'rhythm',
    usingV143RhythmAnalyzer: true,
  }
);

const quality = structured.analysisQuality;
const structuredEligible =
  structured.payloadContract?.structuredRenderEligible === true &&
  quality?.passed === true &&
  structured.analysisEngine === 'v143-reference-free-rhythm' &&
  Array.isArray(structured.renderEvents) &&
  structured.renderEvents.length > 0;

if (!structuredEligible) {
  await writeValidation({
    artifact: 'v143-ai-tab-real-audio-exact-response-pdf',
    schemaVersion: 1,
    attempted: false,
    passed: false,
    reason: 'analyzer-quality-gate-failed',
    analysisEngine: structured.analysisEngine,
    analyzerQualityPassed: quality?.passed === true,
    analyzerQualityFailures:
      Array.isArray(quality?.failures)
        ? quality.failures
        : [],
    structuredRenderEligible:
      structured.payloadContract?.structuredRenderEligible === true,
    renderEventCount:
      Array.isArray(structured.renderEvents)
        ? structured.renderEvents.length
        : 0,
    sourceSha256:
      String(raw.canary?.sourceSha256 || ''),
    productionPromotionAuthorized: false,
    productionModified: false,
  });
  process.exit(0);
}

await fs.mkdir(ARTIFACT_DIR, {
  recursive: true,
});

const common = {
  song: 'V143 AI Tab Real Audio Canary',
  artist: 'DadRock Tabs',
  generatedTab: structured.generatedTab,
  renderEvents: structured.renderEvents,
  tuning: structured.tuning || 'E Standard',
  tempo: structured.tempo || 120,
  timeSignature: structured.timeSignature || '4/4',
  keySignature: structured.keySignature || '',
};

const fullBytes = await createV143RhythmPdf({
  ...common,
  preview: false,
});
const previewBytes = await createV143RhythmPdf({
  ...common,
  preview: true,
  previewSystems: 4,
});

const fullPath = path.join(
  ARTIFACT_DIR,
  'full-real-audio-canary.pdf'
);
const previewPath = path.join(
  ARTIFACT_DIR,
  'preview-real-audio-canary.pdf'
);

await fs.writeFile(fullPath, fullBytes);
await fs.writeFile(previewPath, previewBytes);

const fullDocument = await PDFDocument.load(fullBytes);
const previewDocument = await PDFDocument.load(previewBytes);
const renderEvents = structured.renderEvents;
const maximumMeasure = Math.max(
  ...renderEvents.map((event) => Number(event.measure))
);
const expectedMaximumMeasure = Number(
  quality?.metrics?.measureRange?.last
);

const checks = {
  analyzerQualityPassed:
    quality?.passed === true,
  structuredRenderEligible:
    structured.payloadContract?.structuredRenderEligible === true,
  structuredEngineSelected:
    structured.analysisEngine === 'v143-reference-free-rhythm',
  exactReturnedRenderEventsUsed:
    renderEvents.length ===
    Number(quality?.metrics?.validRenderEventCount),
  maximumMeasureMatchesQualityReport:
    Number.isFinite(expectedMaximumMeasure) &&
    maximumMeasure === expectedMaximumMeasure,
  fullPdfHeaderValid:
    Buffer.from(fullBytes)
      .subarray(0, 5)
      .toString('ascii') === '%PDF-',
  previewPdfHeaderValid:
    Buffer.from(previewBytes)
      .subarray(0, 5)
      .toString('ascii') === '%PDF-',
  fullPdfHasUsefulSize:
    fullBytes.length > 20000,
  previewPdfHasUsefulSize:
    previewBytes.length > 20000,
  fullPdfHasAtLeastOnePage:
    fullDocument.getPageCount() >= 1,
  previewPdfHasAtLeastOnePage:
    previewDocument.getPageCount() >= 1,
  previewIsDistinctFromFull:
    Buffer.compare(
      Buffer.from(fullBytes),
      Buffer.from(previewBytes)
    ) !== 0,
};

const failedChecks = Object.entries(checks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);

await writeValidation({
  artifact: 'v143-ai-tab-real-audio-exact-response-pdf',
  schemaVersion: 1,
  attempted: true,
  passed: failedChecks.length === 0,
  checks,
  failedChecks,
  sourceSha256:
    String(raw.canary?.sourceSha256 || ''),
  analysisEngine: structured.analysisEngine,
  analyzerQualityPassed: quality?.passed === true,
  renderEventCount: renderEvents.length,
  firstMeasure:
    Number(quality?.metrics?.measureRange?.first),
  maximumMeasure,
  fullPdfBytes: fullBytes.length,
  previewPdfBytes: previewBytes.length,
  fullPageCount: fullDocument.getPageCount(),
  previewPageCount: previewDocument.getPageCount(),
  fullPdfArtifactPath: fullPath,
  previewPdfArtifactPath: previewPath,
  renderer: 'createV143RhythmPdf',
  renderContract: 'v143-render-contract-v1',
  productionPromotionAuthorized: false,
  productionModified: false,
});
