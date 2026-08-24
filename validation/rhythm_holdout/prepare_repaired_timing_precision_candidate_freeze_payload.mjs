#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../../lib/jimmyPaigeAnalysisPayload.js';

const inputPath = process.argv[2] || 'debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json';
const outputPath = process.argv[3] || '.candidate/rhythm-freeze-input.json';

const raw = JSON.parse(await fs.readFile(inputPath, 'utf8'));
const live = raw?.liveV143 || {};
const candidate = raw?.candidate || {};
const precision = raw?.precisionDiagnostics || {};
const timing = raw?.timing || {};

const safetyChecks = {
  approvedFixture: candidate.approvedFixture === true,
  referenceFree: live.referenceFree === true && candidate.professionalReferenceUsed === false,
  professionalReferenceNotUsed: live.professionalReferenceUsed === false,
  referenceRuntimeInputNotUsed: live.referenceRuntimeInputUsed === false,
  runtimeLabelsNotRequired: live.runtimeLabelsRequired === false && candidate.runtimeLabelsRequired === false,
  protectedLivePipelineUnmodified: candidate.protectedLivePipelineModified === false,
  liveEndpointUnmodified: candidate.liveEndpointDeployedOrModified === false,
  productionUnmodified: candidate.productionModified === false,
  measureRangeDerivedFromAudio: candidate.measureRangeDerivedFromAudio === true && timing.measureRangeDerivedFromAudio === true,
  repairedTimingOutliersZero: candidate.repairedIntervalOutliersZero === true && Number(timing.repairedIntervalOutlierCount) === 0,
  tempoNotChangedByRepair: candidate.tempoChangedByRepair === false,
  barPhaseNotChangedByRepair: candidate.barPhaseChangedByRepair === false,
  noUnobservedAttack: candidate.addsUnobservedAttack === false,
  noUnobservedPitch: candidate.addsUnobservedPitch === false,
  noAttackRelocation: candidate.relocatesAttack === false,
  precisionReferenceFree: precision.referenceFree === true,
  precisionRuntimeLabelsNotRequired: precision.runtimeLabelsRequired === false,
  precisionNoUnobservedAttack: precision.candidateAddsUnobservedAttack === false,
  precisionNoUnobservedPitch: precision.candidateAddsUnobservedPitch === false,
  precisionNoRelocation: precision.candidateRelocatesEvents === false,
  explicitPrimaryComplete: precision.explicitPrimaryMidiComplete === true,
};
const failedSafetyChecks = Object.entries(safetyChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
if (failedSafetyChecks.length) {
  throw new Error(`Repaired-timing precision candidate is not eligible for freeze: ${failedSafetyChecks.join(', ')}`);
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
  throw new Error(`Repaired-timing precision structured payload is not eligible for freeze: ${failedStructuredChecks.join(', ')}`);
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
  structuredMode: 'v143-repaired-timing-contextual-prune-precision-candidate',
  sourceAudioSha256: String(candidate.sourceSha256 || ''),
  sourceAudioBytes: Number(candidate.sourceBytes || 0),
  renderEvents: structured.renderEvents,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(freezeInput, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({
  gate: 'rhythm-repaired-timing-precision-candidate-freeze-payload-preparation',
  schemaVersion: 1,
  safetyChecks,
  structuredChecks,
  analysisQuality: structured.analysisQuality,
  sourceAudioSha256: freezeInput.sourceAudioSha256,
  audioDerivedMeasureCount: Number(raw?.audioDerivedMeasureCount || 0),
  selectedAttackCount: Number(raw?.selectedCount || 0),
  renderEventCount: freezeInput.renderEvents.length,
  referenceOpened: false,
  passed: true,
}, null, 2));
