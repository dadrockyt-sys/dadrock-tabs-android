#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const outputPath = process.argv[2] || '';

async function read(relativePath) {
  return fs.readFile(path.join(root, relativePath), 'utf8');
}

function section(source, startMarker, endMarker) {
  const start = source.indexOf(startMarker);
  if (start < 0) throw new Error(`Missing section start: ${startMarker}`);
  const end = source.indexOf(endMarker, start + startMarker.length);
  if (end < 0) throw new Error(`Missing section end after ${startMarker}: ${endMarker}`);
  return source.slice(start, end);
}

function requireAll(label, source, patterns) {
  const missing = patterns.filter((pattern) => !source.includes(pattern));
  return {
    label,
    passed: missing.length === 0,
    missing,
  };
}

const [
  pageSource,
  previewRouteSource,
  fullRouteSource,
  professionalWrapperSource,
  aiPdfSource,
] = await Promise.all([
  read('app/ai-tab/page.js'),
  read('app/api/generate-tab-preview/route.js'),
  read('app/api/generate-tab-pdf/route.js'),
  read('lib/createJimmyPaigeProfessionalPdf.js'),
  read('lib/createAiTabPdf.js'),
]);

const previewSection = section(
  pageSource,
  'const requestPreviewPdf',
  'const handleGeneratePreview'
);
const fullSection = section(
  pageSource,
  'const handleDownloadPdf',
  'return ('
);

const sharedMusicalFields = [
  'song:',
  'artist:',
  'transcriptionType:',
  'generatedTab',
  'tuning:',
  'tempo:',
  'timeSignature:',
  'keySignature:',
  'analysisEngine:',
  'techniques:',
  'renderEvents:',
  'measureGrid:',
  'confidence:',
  'difficulty:',
];

const checks = [
  requireAll('page-preview-endpoint-and-musical-payload', previewSection, [
    "'/api/generate-tab-preview'",
    ...sharedMusicalFields,
    'previewSystems: 4',
    "'DADROCK TABS PREVIEW'",
    'locked:',
    'true',
  ]),
  requireAll('page-purchased-endpoint-and-musical-payload', fullSection, [
    "'/api/generate-tab-pdf'",
    ...sharedMusicalFields,
    'orderId:',
    'tokenReference:',
    'unlockMethod:',
    'customerEmail:',
  ]),
  requireAll('preview-route-professional-renderer', previewRouteSource, [
    "from '@/lib/createJimmyPaigeProfessionalPdf'",
    'createJimmyPaigeProfessionalPdf({',
    'renderEvents:',
    'analysisEngine:',
    'preview: true',
    'previewSystems',
  ]),
  requireAll('purchased-route-professional-renderer', fullRouteSource, [
    "from '@/lib/createJimmyPaigeProfessionalPdf'",
    'createJimmyPaigeProfessionalPdf({',
    'renderEvents:',
    'analysisEngine',
    'preview: false',
  ]),
  requireAll('professional-wrapper-v143-routing', professionalWrapperSource, [
    "from '@/lib/createAiTabPdf'",
    "from '@/lib/v143RenderContract'",
    "contract.rendererOptions.transcriptionType === 'rhythm'",
    "analysisEngine === 'v143-reference-free-rhythm'",
    'renderEvents.length > 0',
    'createAiTabPdf({',
    'renderEvents,',
    "mode: 'v143-structured-rhythm'",
  ]),
  requireAll('ai-pdf-v143-underlying-renderer', aiPdfSource, [
    "from '@/lib/createV143RhythmPdf'",
    "from '@/lib/v143RenderContract'",
    'validateV143RenderEvents(options?.renderEvents)',
    "String(options?.transcriptionType || '').toLowerCase() === 'rhythm'",
    "String(options?.analysisEngine || '') === 'v143-reference-free-rhythm'",
    'createV143RhythmPdf({',
    'renderEvents,',
  ]),
];

const failedChecks = checks.filter((check) => !check.passed);
const report = {
  schemaVersion: 1,
  gate: 'ai-tab-pdf-product-contract',
  sourceOfTruth: 'app/ai-tab/page.js',
  previewEndpoint: '/api/generate-tab-preview',
  purchasedEndpoint: '/api/generate-tab-pdf',
  structuredRhythmPath:
    'page.js -> API route -> createJimmyPaigeProfessionalPdf -> createAiTabPdf -> createV143RhythmPdf',
  sharedMusicalFields,
  previewAndPurchasedBothCarryRenderEvents: true,
  browserInventsMusicalPlacement: false,
  checks,
  failedChecks: failedChecks.map((check) => check.label),
  realProfessionalReferenceOpened: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: failedChecks.length === 0,
};

if (outputPath) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
