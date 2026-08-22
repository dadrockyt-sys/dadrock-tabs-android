import fs from 'node:fs/promises';
import path from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../lib/jimmyPaigeAnalysisPayload.js';

const INPUT_PATH = process.argv[2] || '.canary/v143-product-output.json';
const OUTPUT_PATH =
  process.argv[3] ||
  'debug/v143-contextual-prune/ai-tab-real-audio-canary.json';

function safeNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function cleanText(value, maximumLength = 120) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maximumLength);
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
const payloadContract = structured.payloadContract || {};
const liveV143 = raw.liveV143 || {};
const canary = raw.canary || {};
const routing = raw.rhythmRouting || {};
const handoff = raw.vercelAudioHandoff || {};

const generatedTabCharacterCount = String(
  raw.generatedTab || ''
).length;

const checks = {
  approvedFixture:
    canary.approvedFixture === true,
  referenceFreeIdentity:
    liveV143.referenceFree === true,
  noProfessionalReference:
    liveV143.professionalReferenceUsed === false,
  noRuntimeLabels:
    liveV143.runtimeLabelsRequired === false,
  deterministicSeparator:
    liveV143.separatorDeterministic === true,
  v143QualityPassed:
    quality?.passed === true,
  structuredRenderEligible:
    payloadContract.structuredRenderEligible === true,
  structuredEngineSelected:
    structured.analysisEngine ===
    'v143-reference-free-rhythm',
  renderEventsPresent:
    Array.isArray(structured.renderEvents) &&
    structured.renderEvents.length > 0,
  generatedTabPresent:
    generatedTabCharacterCount > 0,
  productRhythmPipelinePreserved:
    canary.sameProductRhythmPipeline === true,
  productRhythmImagePreserved:
    canary.sameProductRhythmImage === true,
  privateBlobTokenNotUsed:
    canary.privateBlobTokenUsed === false,
  productionUnmodified:
    canary.productionModified === false &&
    canary.liveEndpointDeployedOrModified === false,
  productionPromotionUnauthorized:
    payloadContract.productionPromotionAuthorized === false &&
    quality?.productionPromotionAuthorized === false &&
    canary.productionPromotionAuthorized === false,
};

const failedChecks = Object.entries(checks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);

const report = {
  artifact: 'v143-ai-tab-real-audio-product-canary',
  schemaVersion: 1,
  passed: failedChecks.length === 0,
  checks,
  failedChecks,
  analyzer: {
    analysisEngine: structured.analysisEngine,
    engineVersion:
      cleanText(raw.engineVersion, 120) || null,
    referenceFree:
      liveV143.referenceFree === true,
    liveV143Version:
      safeNumber(liveV143.version),
    modalGpu:
      cleanText(liveV143.modalGpu, 40) || null,
    separatorDeterministic:
      liveV143.separatorDeterministic === true,
    separatorSeed:
      safeNumber(liveV143.separatorSeed),
    demucsShifts:
      safeNumber(liveV143.demucsShifts),
    professionalReferenceUsed:
      liveV143.professionalReferenceUsed === true,
    runtimeLabelsRequired:
      liveV143.runtimeLabelsRequired === true,
  },
  quality,
  payloadContract: {
    name:
      cleanText(payloadContract.name, 120) || null,
    version:
      safeNumber(payloadContract.version),
    referenceFree:
      payloadContract.referenceFree === true,
    renderEventCount:
      safeNumber(payloadContract.renderEventCount),
    renderContractVersion:
      safeNumber(payloadContract.renderContractVersion),
    analyzerQualityGatePassed:
      payloadContract.analyzerQualityGatePassed === true,
    structuredRenderEligible:
      payloadContract.structuredRenderEligible === true,
    productionPromotionAuthorized:
      payloadContract.productionPromotionAuthorized === true,
  },
  productOutput: {
    candidateCount:
      safeNumber(raw.candidateCount),
    selectedCount:
      safeNumber(raw.selectedCount),
    noteCount:
      safeNumber(raw.noteCount),
    rawEventCount:
      Array.isArray(raw.events)
        ? raw.events.length
        : 0,
    renderEventCount:
      Array.isArray(structured.renderEvents)
        ? structured.renderEvents.length
        : 0,
    generatedTabPresent:
      generatedTabCharacterCount > 0,
    generatedTabCharacterCount,
    tuning:
      cleanText(structured.tuning, 80) || null,
    tempo:
      safeNumber(structured.tempo),
    timeSignature:
      cleanText(structured.timeSignature, 20) || null,
    techniqueTypes:
      Array.isArray(structured.techniques)
        ? structured.techniques
        : [],
  },
  routing: {
    mode:
      cleanText(routing.mode, 120) || null,
    requestedPart:
      cleanText(routing.requestedPart, 20) || null,
    legacyLeadChanged:
      routing.legacyLeadChanged === true,
    legacyBassChanged:
      routing.legacyBassChanged === true,
    pairedCarrierStemContractPreserved:
      routing.pairedCarrierStemContractPreserved === true,
    professionalReferenceUsed:
      routing.professionalReferenceUsed === true,
    runtimeLabelsRequired:
      routing.runtimeLabelsRequired === true,
    privateBlobContractPreserved:
      handoff.privateBlobContractPreserved === true,
    normalizedBeforeRouting:
      handoff.normalizedBeforeRouting === true,
  },
  canary: {
    mode:
      cleanText(canary.mode, 120) || null,
    approvedFixture:
      canary.approvedFixture === true,
    approvedFixtureRepositoryPath:
      cleanText(
        canary.approvedFixtureRepositoryPath,
        200
      ) || null,
    sourceSha256:
      cleanText(canary.sourceSha256, 80) || null,
    sourceBytes:
      safeNumber(canary.sourceBytes),
    privateBlobNetworkDownloadBypassed:
      canary.privateBlobNetworkDownloadBypassed === true,
    privateBlobTokenUsed:
      canary.privateBlobTokenUsed === true,
    sameProductRhythmPipeline:
      canary.sameProductRhythmPipeline === true,
    sameProductRhythmImage:
      canary.sameProductRhythmImage === true,
    liveEndpointDeployedOrModified:
      canary.liveEndpointDeployedOrModified === true,
    productionModified:
      canary.productionModified === true,
  },
  productionPromotionAuthorized: false,
};

await fs.mkdir(path.dirname(OUTPUT_PATH), {
  recursive: true,
});
await fs.writeFile(
  OUTPUT_PATH,
  `${JSON.stringify(report, null, 2)}\n`,
  'utf8'
);

console.log(JSON.stringify(report, null, 2));
