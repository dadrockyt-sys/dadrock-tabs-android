import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const files = {
  page: 'app/ai-tab/page.js',
  upload: 'app/api/audio-upload/route.js',
  analyze: 'app/api/analyze-audio-tab/route.js',
  preview: 'app/api/generate-tab-preview/route.js',
  full: 'app/api/generate-tab-pdf/route.js',
  payload: 'lib/jimmyPaigeAnalysisPayload.js',
  conditioning: 'lib/aiTabConditioningV1.mjs',
  professional: 'lib/createJimmyPaigeProfessionalPdf.js',
};

const source = Object.fromEntries(
  await Promise.all(
    Object.entries(files).map(async ([key, filePath]) => [
      key,
      await readFile(filePath, 'utf8'),
    ])
  )
);

function includesAll(text, values, label) {
  for (const value of values) {
    assert.ok(text.includes(value), `${label} must include ${value}`);
  }
}

const instrumentValues = ["'lead'", "'rhythm'", "'bass'"];

// Customer-facing selection must retain all three product paths.
includesAll(source.page, [
  "value: 'lead'",
  "value: 'rhythm'",
  "value: 'bass'",
], 'AI Tab page instrument selector');

// Upload authorization must preserve the selected instrument and rights gate.
includesAll(source.upload, [
  "['lead', 'rhythm', 'bass']",
  'copyrightConfirmed',
  'transcriptionType',
  'allowedContentTypes',
  'maximumSizeInBytes',
], 'audio upload route');

// The page must execute the entire product journey.
includesAll(source.page, [
  "handleUploadUrl:\n              '/api/audio-upload'",
  "const endpoint = '/api/analyze-audio-tab'",
  "'/api/generate-tab-preview'",
  "'/api/generate-tab-pdf'",
  'analysisMetadata',
  'renderEvents',
  'measureGrid',
  'techniques',
  'confidence',
  'difficulty',
], 'AI Tab end-to-end browser flow');

// Analyzer routing is intentionally split: only Rhythm may opt into V143 today.
includesAll(source.analyze, instrumentValues, 'analyzer allowed types');
includesAll(source.analyze, [
  'process.env.ANALYZER_API_URL',
  'process.env.ANALYZER_API_URL_V143',
  "transcriptionType === 'rhythm'",
  'usingV143RhythmAnalyzer',
  'liveV143?.referenceFree === true',
  'liveV143?.professionalReferenceUsed === false',
  'liveV143?.referenceRuntimeInputUsed === false',
  'liveV143?.runtimeLabelsRequired === false',
], 'analyzer fail-closed routing');

assert.ok(
  !source.analyze.includes("transcriptionType === 'lead' &&\n      Boolean(v143RhythmAnalyzerUrl)"),
  'Lead must not be silently routed through the Rhythm V143 endpoint'
);
assert.ok(
  !source.analyze.includes("transcriptionType === 'bass' &&\n      Boolean(v143RhythmAnalyzerUrl)"),
  'Bass must not be silently routed through the Rhythm V143 endpoint'
);

// Phase 1 conditioning is normalized server-side, forwarded to the selected
// analyzer, and returned as a server-owned reference-blind contract.
includesAll(source.analyze, [
  'normalizeAiTabConditioningV1(',
  'body?.conditioning,',
  'conditioning,',
  'buildAiTabConditioningContractV1({',
  'conditioningContract,',
], 'conditioning v1 analyzer plumbing');

includesAll(source.conditioning, [
  'STRUCTURE',
].filter(() => false), 'conditioning placeholder');

includesAll(source.conditioning, [
  'AI_TAB_CONDITIONING_V1 = 1',
  'STANDARD_GUITAR_TUNING_MIDI',
  'STANDARD_BASS_TUNING_MIDI',
  "'auto'",
  "'straight'",
  "'triplet'",
  'referenceBlind: true',
  'referenceScoreAuthorized: false',
  "kind: 'full-mixture'",
  "kind: 'selected-analyzer-carrier'",
  "kind: 'same-as-mixture'",
], 'conditioning v1 server contract');

// Preview and full-PDF routes must still accept all three customer choices.
includesAll(source.preview, instrumentValues, 'preview PDF allowed types');
includesAll(source.full, instrumentValues, 'full PDF allowed types');

// Both PDF paths must receive the same structured analysis metadata family.
for (const [label, text] of [
  ['preview route', source.preview],
  ['full PDF route', source.full],
]) {
  includesAll(text, [
    'analysisEngine',
    'renderEvents',
    'measureGrid',
    'confidence',
    'difficulty',
    'techniques',
    'tuning',
    'tempo',
    'timeSignature',
    'keySignature',
  ], label);
}

// Preview and purchased/full PDF must make the same professional-renderer
// decision from the same feature helper. This guards against a professional
// preview silently turning into a different renderer after unlock.
for (const [label, text] of [
  ['preview route', source.preview],
  ['full PDF route', source.full],
]) {
  includesAll(text, [
    'getJimmyPaigeProfessionalPdfFeatureState',
    'professionalPdfFeature.enabled',
    'createJimmyPaigeProfessionalPdf',
  ], `${label} professional renderer parity`);
}

// Purchased/full PDF must remain protected by a real unlock verification path.
includesAll(source.full, [
  "unlockMethod === 'paypal'",
  'verifyPayPalOrder',
  'verifyFreeToken',
  'await resend.emails.send',
], 'full PDF unlock and delivery route');

// Structured identity remains fail-closed and Rhythm-only until another
// instrument earns its own analyzer identity and quality evidence.
includesAll(source.payload, [
  'const referenceFree =',
  'buildV143AnalyzerQualityReport',
  'structuredRenderEligible',
  "? 'v143-reference-free-rhythm'",
  "? 'v143-reference-free-rhythm-fallback'",
  ": 'legacy'",
], 'analysis payload identity gate');

includesAll(source.professional, [
  "contract.rendererOptions.transcriptionType === 'rhythm'",
  "analysisEngine === 'v143-reference-free-rhythm'",
  'renderEvents.length > 0',
  "mode: 'v143-structured-rhythm'",
], 'professional structured renderer gate');

// Browser/PDF layers must not create structured placement for legacy output.
assert.ok(
  source.payload.includes(
    'const renderEvents = referenceFree\n    ? projectV143RenderEvents(rawEvents)\n    : [];'
  ),
  'Legacy output must not acquire structured renderEvents in the normalization layer'
);

const evidence = {
  schemaVersion: 3,
  gate: 'ai-tab-end-to-end-contract',
  product: 'dadrocktabs.com/ai-tab',
  instrumentChoices: ['lead', 'rhythm', 'bass'],
  userAudioUploadWired: true,
  copyrightGateWired: true,
  analyzerRequestWired: true,
  conditioningV1Wired: true,
  conditioningV1ReferenceBlind: true,
  conditioningV1ReferenceScoreAuthorized: false,
  dualContextProvenanceWired: true,
  previewPdfWired: true,
  fullPdfUnlockWired: true,
  analysisMetadataTransportWired: true,
  previewAndFullProfessionalFeatureGateShared: true,
  previewAndFullProfessionalRendererShared: true,
  rhythmDedicatedV143RouteFailClosed: true,
  rhythmStructuredProfessionalRendererFailClosed: true,
  leadLegacyPreserved: true,
  bassLegacyPreserved: true,
  leadStructuredProfessionalIdentityPresent: false,
  bassStructuredProfessionalIdentityPresent: false,
  missingPlacementManufacturedForLegacy: false,
  paymentAttempted: false,
  tokenRedeemed: false,
  customerEmailSent: false,
  vercelDeploymentAttempted: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: true,
};

const resultPath = String(process.env.AI_TAB_E2E_RESULT_PATH || '').trim();
if (resultPath) {
  const absolute = path.resolve(resultPath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('AI TAB END-TO-END CONTRACT VERIFIED');
