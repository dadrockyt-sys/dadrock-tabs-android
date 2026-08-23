#!/usr/bin/env node

import path from 'node:path';
import { pathToFileURL } from 'node:url';

const modulePath = process.argv[2];
if (!modulePath) {
  throw new Error('Usage: verify_v143_runtime_safety_contract.mjs <jimmyPaigeAnalysisPayload.mjs>');
}

const { buildJimmyPaigeAnalysisPayload } = await import(
  pathToFileURL(path.resolve(modulePath)).href
);

const baseEvents = [
  {
    start: 0,
    end: 0.2,
    duration: 0.2,
    measure: 1,
    step: 0,
    stringIndex: 5,
    fret: 0,
    midi: 40,
    durationSteps: 2,
    techniques: [],
  },
  {
    start: 0.25,
    end: 0.45,
    duration: 0.2,
    measure: 1,
    step: 4,
    stringIndex: 4,
    fret: 2,
    midi: 47,
    durationSteps: 2,
    techniques: [],
  },
];

function analyzerResponse(overrides = {}) {
  return {
    generatedTab: 'Synthetic safe Rhythm tablature',
    tuning: 'E Standard',
    tempo: 120,
    timeSignature: '4/4',
    events: baseEvents,
    liveV143: {
      referenceFree: true,
      professionalReferenceUsed: false,
      referenceRuntimeInputUsed: false,
      runtimeLabelsRequired: false,
      ...(overrides.liveV143 || {}),
    },
    ...Object.fromEntries(
      Object.entries(overrides).filter(([key]) => key !== 'liveV143')
    ),
  };
}

function build(response) {
  return buildJimmyPaigeAnalysisPayload(response, {
    transcriptionType: 'rhythm',
    usingV143RhythmAnalyzer: true,
  });
}

const safe = build(analyzerResponse());
const safeChecks = {
  accepted: Boolean(safe),
  payloadContractVersion3: safe?.payloadContract?.version === 3,
  runtimeSafetyVerified: safe?.payloadContract?.v143RuntimeSafetyVerified === true,
  professionalReferenceNotUsed: safe?.payloadContract?.professionalReferenceNotUsed === true,
  referenceRuntimeInputNotUsed: safe?.payloadContract?.referenceRuntimeInputNotUsed === true,
  runtimeLabelsNotRequired: safe?.payloadContract?.runtimeLabelsNotRequired === true,
  renderEventsPresent: Array.isArray(safe?.renderEvents) && safe.renderEvents.length === 2,
};

const unsafeCases = [
  ['professional-reference-used', { professionalReferenceUsed: true }],
  ['reference-runtime-input-used', { referenceRuntimeInputUsed: true }],
  ['runtime-labels-required', { runtimeLabelsRequired: true }],
  ['missing-professional-reference-flag', { professionalReferenceUsed: undefined }],
  ['missing-reference-runtime-input-flag', { referenceRuntimeInputUsed: undefined }],
  ['missing-runtime-labels-flag', { runtimeLabelsRequired: undefined }],
  ['reference-free-false', { referenceFree: false }],
];

const unsafeResults = [];
for (const [name, liveOverrides] of unsafeCases) {
  let rejected = false;
  let errorMessage = '';
  try {
    build(analyzerResponse({ liveV143: liveOverrides }));
  } catch (error) {
    rejected = true;
    errorMessage = error instanceof Error ? error.message : String(error);
  }
  unsafeResults.push({ name, rejected, errorMessage });
}

const failedSafeChecks = Object.entries(safeChecks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);
const unsafeAccepted = unsafeResults
  .filter((result) => !result.rejected)
  .map((result) => result.name);

const report = {
  schemaVersion: 1,
  gate: 'v143-runtime-anti-leakage-contract',
  safeChecks,
  unsafeResults,
  failedSafeChecks,
  unsafeAccepted,
  professionalReferenceOpened: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: failedSafeChecks.length === 0 && unsafeAccepted.length === 0,
};

console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
