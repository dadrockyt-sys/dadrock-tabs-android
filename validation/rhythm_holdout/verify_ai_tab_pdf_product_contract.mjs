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
  analyzerRouteSource,
  analysisPayloadSource,
  previewRouteSource,
  fullRouteSource,
  professionalWrapperSource,
  aiPdfSource,
  structuredRhythmRendererSource,
] = await Promise.all([
  read('app/ai-tab/page.js'),
  read('app/api/analyze-audio-tab/route.js'),
  read('lib/jimmyPaigeAnalysisPayload.js'),
  read('app/api/generate-tab-preview/route.js'),
  read('app/api/generate-tab-pdf/route.js'),
  read('lib/createJimmyPaigeProfessionalPdf.js'),
  read('lib/createAiTabPdf.js'),
  read('lib/createV143RhythmPdf.js'),
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
    "'content-type'",
    "'application/pdf'",
  ]),
  requireAll('page-purchased-endpoint-and-musical-payload', fullSection, [
    "'/api/generate-tab-pdf'",
    ...sharedMusicalFields,
    'orderId:',
    'tokenReference:',
    'unlockMethod:',
    'customerEmail:',
    "'content-type'",
    "'application/pdf'",
  ]),
  requireAll('analyzer-route-complete-v143-runtime-safety-gate', analyzerRouteSource, [
    'const v143RuntimeSafetyVerified =',
    'liveV143?.referenceFree === true',
    'liveV143?.professionalReferenceUsed === false',
    'liveV143?.referenceRuntimeInputUsed === false',
    'liveV143?.runtimeLabelsRequired === false',
    'usingV143RhythmAnalyzer &&',
    '!v143RuntimeSafetyVerified',
    'status: 502',
    'buildJimmyPaigeAnalysisPayload(',
  ]),
  requireAll('analysis-payload-complete-v143-runtime-safety-gate', analysisPayloadSource, [
    'const v143RuntimeSafetyVerified =',
    'professionalReferenceNotUsed &&',
    'referenceRuntimeInputNotUsed &&',
    'runtimeLabelsNotRequired',
    'usingV143RhythmAnalyzer &&',
    '!v143RuntimeSafetyVerified',
    'const renderEvents = v143RuntimeSafetyVerified',
    'version: 3',
    'v143RuntimeSafetyVerified,',
    'productionPromotionAuthorized: false',
  ]),
  requireAll('preview-route-professional-renderer', previewRouteSource, [
    "from '@/lib/createJimmyPaigeProfessionalPdf'",
    "from '@/lib/jimmyPaigeProfessionalPdfFeature'",
    'getJimmyPaigeProfessionalPdfFeatureState()',
    'professionalPdfFeature.enabled',
    'createJimmyPaigeProfessionalPdf({',
    'renderEvents:',
    'analysisEngine:',
    'preview: true',
    'previewSystems',
    "'Content-Type': 'application/pdf'",
  ]),
  requireAll('purchased-route-professional-renderer', fullRouteSource, [
    "from '@/lib/createJimmyPaigeProfessionalPdf'",
    "from '@/lib/jimmyPaigeProfessionalPdfFeature'",
    'getJimmyPaigeProfessionalPdfFeatureState()',
    'professionalPdfFeature.enabled',
    'createJimmyPaigeProfessionalPdf({',
    'renderEvents:',
    'analysisEngine',
    'preview: false',
    "'Content-Type': 'application/pdf'",
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
  requireAll('structured-rhythm-polished-branding-and-preview-lock', structuredRhythmRendererSource, [
    "path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png')",
    "'DIY Guitar & Bass TAB Generator'",
    "'Powered by DadRock AI • V143 Rhythm'",
    "'DADROCK TABS PREVIEW'",
    "'FULL TAB LOCKED'",
    "'Generated by DadRock Tabs Studio • dadrocktabs.com'",
    'preview && index >= clearPreviewSystems',
  ]),
];

const byLabel = Object.fromEntries(checks.map((check) => [check.label, check]));
const previewPayloadPassed =
  byLabel['page-preview-endpoint-and-musical-payload']?.passed === true;
const purchasedPayloadPassed =
  byLabel['page-purchased-endpoint-and-musical-payload']?.passed === true;
const analyzerRouteSafetyPassed =
  byLabel['analyzer-route-complete-v143-runtime-safety-gate']?.passed === true;
const analysisPayloadSafetyPassed =
  byLabel['analysis-payload-complete-v143-runtime-safety-gate']?.passed === true;
const previewRoutePassed =
  byLabel['preview-route-professional-renderer']?.passed === true;
const purchasedRoutePassed =
  byLabel['purchased-route-professional-renderer']?.passed === true;
const wrapperRoutingPassed =
  byLabel['professional-wrapper-v143-routing']?.passed === true &&
  byLabel['ai-pdf-v143-underlying-renderer']?.passed === true;
const polishedBrandingContractPassed =
  byLabel['structured-rhythm-polished-branding-and-preview-lock']?.passed === true;

const failedChecks = checks.filter((check) => !check.passed);
const report = {
  schemaVersion: 3,
  gate: 'ai-tab-pdf-product-contract',
  sourceOfTruth: 'app/ai-tab/page.js',
  analyzerEndpoint: '/api/analyze-audio-tab',
  previewEndpoint: '/api/generate-tab-preview',
  purchasedEndpoint: '/api/generate-tab-pdf',
  structuredRhythmPath:
    'page.js -> analyze route/payload safety gates -> PDF API route -> createJimmyPaigeProfessionalPdf -> createAiTabPdf -> createV143RhythmPdf',
  polishedRhythmRenderer: 'lib/createV143RhythmPdf.js',
  sharedMusicalFields,
  previewAndPurchasedBothCarryRenderEvents:
    previewPayloadPassed && purchasedPayloadPassed,
  previewAndPurchasedExpectPdf:
    previewPayloadPassed && purchasedPayloadPassed,
  analyzerRuntimeSafetyDefenseInDepth:
    analyzerRouteSafetyPassed && analysisPayloadSafetyPassed,
  routesUseProfessionalFeatureGate:
    previewRoutePassed && purchasedRoutePassed,
  authenticatedV143RhythmRoutesToStructuredRenderer: wrapperRoutingPassed,
  polishedBrandingContractPassed,
  dadRockLogoPath: 'public/DadRock-Tabs-Logo.png',
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
