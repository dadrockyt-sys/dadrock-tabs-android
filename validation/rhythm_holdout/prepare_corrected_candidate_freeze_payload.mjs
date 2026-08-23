#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../../lib/jimmyPaigeAnalysisPayload.js';

const inputPath = process.argv[2] || 'debug/v143-contextual-prune/corrected-candidate-product.json';
const outputPath = process.argv[3] || '.candidate/rhythm-freeze-input.json';

const raw = JSON.parse(await fs.readFile(inputPath, 'utf8'));
const live = raw?.liveV143 || {};
const candidate = raw?.candidate || {};

const safetyChecks = {
  approvedFixture: candidate.approvedFixture === true,
  referenceFree: live.referenceFree === true && candidate.professionalReferenceUsed === false,
  professionalReferenceNotUsed: live.professionalReferenceUsed === false,
  referenceRuntimeInputNotUsed: live.referenceRuntimeInputUsed === false,
  runtimeLabelsNotRequired: live.runtimeLabelsRequired === false && candidate.runtimeLabelsRequired === false,
  protectedLivePipelineUnmodified: candidate.protectedLivePipelineModified === false,
  liveEndpointUnmodified: candidate.liveEndpointDeployedOrModified === false,
  productionUnmodified: candidate.productionModified === false,
};
const failedSafetyChecks = Object.entries(safetyChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
if (failedSafetyChecks.length) {
  throw new Error(`Corrected candidate is not eligible for freeze: ${failedSafetyChecks.join(', ')}`);
}

const structured = buildJimmyPaigeAnalysisPayload(raw, {
  transcriptionType: 'rhythm',
  usingV143RhythmAnalyzer: true,
});

const structuredChecks = {
  analysisEngine: structured.analysisEngine === 'v143-reference-free-rhythm',
  analyzerQualityPassed: structured.analysisQuality?.passed === true,
  structuredRenderEligible: structured.payloadContract?.structuredRenderEligible === true,
  payloadReferenceFree: structured.payloadContract?.referenceFree === true,
  payloadProfessionalReferenceNotUsed: structured.payloadContract?.professionalReferenceNotUsed === true,
  payloadReferenceRuntimeInputNotUsed: structured.payloadContract?.referenceRuntimeInputNotUsed === true,
  payloadRuntimeLabelsNotRequired: structured.payloadContract?.runtimeLabelsNotRequired === true,
  payloadRuntimeSafetyVerified: structured.payloadContract?.v143RuntimeSafetyVerified === true,
  renderEventsPresent: Array.isArray(structured.renderEvents) && structured.renderEvents.length > 0,
};
const failedStructuredChecks = Object.entries(structuredChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
if (failedStructuredChecks.length) {
  throw new Error(`Corrected candidate structured payload is not eligible for freeze: ${failedStructuredChecks.join(', ')}`);
}

const freezeInput = {
  schemaVersion: 3,
  instrument: 'rhythm',
  referenceFree: true,
  professionalReferenceUsed: false,
  referenceRuntimeInputUsed: false,
  runtimeLabelsRequired: false,
  v143RuntimeSafetyVerified: true,
  tempoBpm: structured.tempo,
  timeSignature: structured.timeSignature,
  tuning: structured.tuning,
  structuredMode: 'v143-contextual-prune-corrected-candidate',
  sourceAudioSha256: String(candidate.sourceSha256 || ''),
  sourceAudioBytes: Number(candidate.sourceBytes || 0),
  renderEvents: structured.renderEvents,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(freezeInput, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({
  gate: 'rhythm-corrected-candidate-freeze-payload-preparation',
  schemaVersion: 1,
  safetyChecks,
  structuredChecks,
  analysisQuality: structured.analysisQuality,
  sourceAudioSha256: freezeInput.sourceAudioSha256,
  renderEventCount: freezeInput.renderEvents.length,
  referenceOpened: false,
  passed: true,
}, null, 2));
