#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../../lib/jimmyPaigeAnalysisPayload.js';

const inputPath = process.argv[2] || '.canary/v143-product-output.json';
const outputPath = process.argv[3] || '.canary/rhythm-freeze-input.json';

const raw = JSON.parse(await fs.readFile(inputPath, 'utf8'));
const live = raw?.liveV143 || {};
const canary = raw?.canary || {};

const safetyChecks = {
  referenceFree: live.referenceFree === true,
  professionalReferenceNotUsed: live.professionalReferenceUsed === false,
  referenceRuntimeInputNotUsed: live.referenceRuntimeInputUsed === false,
  runtimeLabelsNotRequired: live.runtimeLabelsRequired === false,
  sameProductRhythmPipeline: canary.sameProductRhythmPipeline === true,
  sameProductRhythmImage: canary.sameProductRhythmImage === true,
  productionUnmodified:
    canary.productionModified === false &&
    canary.liveEndpointDeployedOrModified === false,
  productionPromotionUnauthorized:
    canary.productionPromotionAuthorized === false,
};

const failedSafetyChecks = Object.entries(safetyChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
if (failedSafetyChecks.length) {
  throw new Error(
    `Raw Rhythm product output is not eligible for freeze: ${failedSafetyChecks.join(', ')}`
  );
}

const structured = buildJimmyPaigeAnalysisPayload(raw, {
  transcriptionType: 'rhythm',
  usingV143RhythmAnalyzer: true,
});

const structuredChecks = {
  analysisEngine: structured.analysisEngine === 'v143-reference-free-rhythm',
  analyzerQualityPassed: structured.analysisQuality?.passed === true,
  structuredRenderEligible:
    structured.payloadContract?.structuredRenderEligible === true,
  payloadReferenceFree: structured.payloadContract?.referenceFree === true,
  renderEventsPresent:
    Array.isArray(structured.renderEvents) && structured.renderEvents.length > 0,
};
const failedStructuredChecks = Object.entries(structuredChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
if (failedStructuredChecks.length) {
  throw new Error(
    `Structured Rhythm payload is not eligible for freeze: ${failedStructuredChecks.join(', ')}`
  );
}

const freezeInput = {
  schemaVersion: 1,
  instrument: 'rhythm',
  referenceFree: true,
  professionalReferenceUsed: false,
  referenceRuntimeInputUsed: false,
  tempoBpm: structured.tempo,
  timeSignature: structured.timeSignature,
  tuning: structured.tuning,
  structuredMode: structured.analysisEngine,
  sourceAudioSha256: String(canary.sourceSha256 || ''),
  sourceAudioBytes: Number(canary.sourceBytes || 0),
  renderEvents: structured.renderEvents,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(freezeInput, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({
  gate: 'rhythm-freeze-payload-preparation',
  safetyChecks,
  structuredChecks,
  sourceAudioSha256: freezeInput.sourceAudioSha256,
  renderEventCount: freezeInput.renderEvents.length,
  firstEventIndex: freezeInput.renderEvents[0]?.eventIndex ?? null,
  lastEventIndex:
    freezeInput.renderEvents[freezeInput.renderEvents.length - 1]?.eventIndex ?? null,
  referenceOpened: false,
  passed: true,
}, null, 2));
