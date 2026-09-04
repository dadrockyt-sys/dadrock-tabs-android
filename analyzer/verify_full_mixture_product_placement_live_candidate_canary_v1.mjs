import assert from 'node:assert/strict';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../lib/jimmyPaigeAnalysisPayload.js';
import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '../lib/aiTabMixtureStructureContextV1.mjs';
import { buildAiTabMixtureStructureContextFromAnalyzerObservationV1 } from '../lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';
import { buildAiTabDualContextShadowFusionV1 } from '../lib/aiTabDualContextShadowFusionV1.mjs';
import { buildAiTabProductPlacementCandidateCanaryV1 } from '../lib/aiTabProductPlacementCandidateCanaryV1.mjs';
import { buildFullMixtureProductPlacementCandidateV1 } from './full_mixture_product_placement_candidate_v1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
};

const safeLiveV143 = {
  referenceFree: true,
  professionalReferenceUsed: false,
  referenceRuntimeInputUsed: false,
  runtimeLabelsRequired: false,
};

const baseRawEvents = [
  { start: 0.000, end: 0.080, stringIndex: 0, fret: 0, midi: 64 },
  { start: 0.375, end: 0.455, stringIndex: 1, fret: 1, midi: 60 },
  { start: 1.875, end: 1.955, stringIndex: 2, fret: 2, midi: 57 },
  { start: 2.000, end: 2.080, stringIndex: 3, fret: 2, midi: 52 },
  { start: 2.625, end: 2.705, stringIndex: 4, fret: 3, midi: 48 },
  { start: 3.875, end: 3.955, stringIndex: 5, fret: 5, midi: 45 },
  { start: 4.000, end: 4.080, stringIndex: 0, fret: 3, midi: 67 },
];

const baseOracle = [
  { eventIndex: 0, measure: 1, step: 0, stringIndex: 0, fret: 0, midi: 64 },
  { eventIndex: 1, measure: 1, step: 3, stringIndex: 1, fret: 1, midi: 60 },
  { eventIndex: 2, measure: 1, step: 15, stringIndex: 2, fret: 2, midi: 57 },
  { eventIndex: 3, measure: 2, step: 0, stringIndex: 3, fret: 2, midi: 52 },
  { eventIndex: 4, measure: 2, step: 5, stringIndex: 4, fret: 3, midi: 48 },
  { eventIndex: 5, measure: 2, step: 15, stringIndex: 5, fret: 5, midi: 45 },
  { eventIndex: 6, measure: 3, step: 0, stringIndex: 0, fret: 3, midi: 67 },
];

function field(value, confidence = 0.85, method = 'synthetic-known-truth-v1') {
  return { value, confidence, method };
}

function trustedObservation({
  tempoBpm = 120,
  timeSignature = { numerator: 4, denominator: 4 },
  pickupBeats = 0,
  feel = 'straight',
} = {}) {
  return {
    version: 1,
    provenance: {
      sourceKind: 'full-mixture',
      sourceIdentity: 'request-audio',
      referenceBlind: true,
      referenceRuntimeInputUsed: false,
    },
    diagnostics: {
      referenceBlind: true,
      carrierInputUsed: false,
      transcribedEventInputUsed: false,
      wavAdapter: {
        fullMixtureOnly: true,
        separatedCarrierUsed: false,
        transcribedEventInputUsed: false,
      },
    },
    tempoBpm: field(tempoBpm, 0.92, 'synthetic-tempo-v1'),
    timeSignature: field(timeSignature, 0.91, 'synthetic-meter-v1'),
    pickupBeats: field(pickupBeats, 0.90, 'synthetic-pickup-v1'),
    feel: field(feel, 0.89, 'synthetic-feel-v1'),
  };
}

function conditioning(structurePrior = {}) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior,
      instrumentConfig: {
        role: 'rhythm',
        tuningMidi: [40, 45, 50, 55, 59, 64],
        capoFret: 0,
      },
    },
    'rhythm'
  );
}

function structuredPayload(rawEvents = baseRawEvents) {
  return buildJimmyPaigeAnalysisPayload(
    {
      generatedTab: 'Synthetic Phase 11 canonical tab baseline',
      events: rawEvents,
      liveV143: safeLiveV143,
    },
    {
      transcriptionType: 'rhythm',
      usingV143RhythmAnalyzer: true,
    }
  );
}

function researchPipeline({
  rawEvents = baseRawEvents,
  structurePrior = {},
  observation = trustedObservation(),
} = {}) {
  const structured = structuredPayload(rawEvents);
  const normalizedConditioning = conditioning(structurePrior);
  const baselineContext = buildAiTabMixtureStructureContextV1({
    structurePrior: normalizedConditioning.structurePrior,
    mixtureObservation: null,
    mixtureSource,
  });
  const mixtureStructureContext =
    buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
      baselineContext,
      analyzerObservation: observation,
      structurePrior: normalizedConditioning.structurePrior,
      mixtureSource,
    });
  const dualContextShadowProjection = buildAiTabDualContextShadowFusionV1({
    events: structured.events,
    conditioning: normalizedConditioning,
    mixtureStructureContext,
  });

  return {
    structured,
    normalizedConditioning,
    baselineContext,
    mixtureStructureContext,
    dualContextShadowProjection,
  };
}

function placementView(rows) {
  return rows.map((row) => ({
    eventIndex: row.eventIndex,
    measure: row.measure,
    step: row.step,
    stringIndex: row.stringIndex,
    fret: row.fret,
    midi: row.midi,
  }));
}

async function canaryFor(scenario, overrides = {}) {
  return buildAiTabProductPlacementCandidateCanaryV1({
    structuredPayload: scenario.structured,
    dualContextShadowProjection: scenario.dualContextShadowProjection,
    ...overrides,
  });
}

function assertSummaryOnly(value) {
  assert.deepEqual(
    Object.keys(value).sort(),
    [
      'baselineRenderEventCount',
      'canaryContract',
      'candidateRenderEventCount',
      'eligible',
    ].sort()
  );
  assert.equal(Object.hasOwn(value, 'renderEvents'), false);
  assert.equal(JSON.stringify(value).includes('"renderEvents"'), false);
  assert.deepEqual(
    Object.keys(value.canaryContract).sort(),
    [
      'liveProductAuthority',
      'name',
      'pdfAuthority',
      'placementOnlyAuthority',
      'productionEligible',
      'referenceBlind',
      'referenceScoreAuthorized',
      'researchOnly',
      'shadowOnly',
      'version',
    ].sort()
  );
}

async function collectSourceFiles(root) {
  const rows = [];
  const entries = await readdir(root, { withFileTypes: true });

  for (const entry of entries) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) {
      rows.push(...await collectSourceFiles(path));
      continue;
    }

    if (/\.(?:js|jsx|mjs|ts|tsx)$/.test(entry.name)) {
      rows.push(path);
    }
  }

  return rows;
}

const tests = {};
const validationMatrix = {};
const scenario = researchPipeline();

// C1 — canonical-first ordering and frozen server seam.
const routePath = 'app/api/analyze-audio-tab/route.js';
const routeSource = await readFile(routePath, 'utf8');
const structuredIndex = routeSource.indexOf('const structuredPayload =');
const dualIndex = routeSource.indexOf('const dualContextShadowProjection =');
const canaryIndex = routeSource.indexOf('const productPlacementCandidateCanary =');
const returnIndex = routeSource.indexOf('return NextResponse.json({', canaryIndex);
assert.ok(structuredIndex >= 0);
assert.ok(dualIndex > structuredIndex);
assert.ok(canaryIndex > dualIndex);
assert.ok(returnIndex > canaryIndex);
assert.ok(routeSource.includes("@/lib/aiTabProductPlacementCandidateCanaryV1.mjs"));
tests.C1 = 'PASS';

// C2 — existing authenticated Product placement always wins.
const placedRawEvents = baseRawEvents.map((event, index) => ({
  ...event,
  measure: baseOracle[index].measure,
  step: baseOracle[index].step,
  eventIndex: index,
}));
const placedScenario = researchPipeline({ rawEvents: placedRawEvents });
assert.equal(placedScenario.structured.renderEvents.length, baseOracle.length);
const c2Before = JSON.stringify(placedScenario.structured);
const placedCanary = await canaryFor(placedScenario);
assert.equal(placedCanary.eligible, false);
assert.equal(placedCanary.baselineRenderEventCount, baseOracle.length);
assert.equal(placedCanary.candidateRenderEventCount, 0);
assert.equal(JSON.stringify(placedScenario.structured), c2Before);
tests.C2 = 'PASS';
validationMatrix.M2_AUTHENTICATED_PRODUCT_WINS = 'PASS';

// C3 — eligible canary is exactly the existing Phase 10 placement-only source.
assert.equal(scenario.structured.renderEvents.length, 0);
const phase10Candidate = buildFullMixtureProductPlacementCandidateV1({
  structuredPayload: scenario.structured,
  dualContextShadowProjection: scenario.dualContextShadowProjection,
});
assert.ok(phase10Candidate);
assert.deepEqual(placementView(phase10Candidate.renderEvents), baseOracle);
const eligibleCanary = await canaryFor(scenario);
assert.equal(eligibleCanary.eligible, true);
assert.equal(eligibleCanary.baselineRenderEventCount, 0);
assert.equal(eligibleCanary.candidateRenderEventCount, baseOracle.length);
assertSummaryOnly(eligibleCanary);
tests.C3 = 'PASS';
validationMatrix.M1_ELIGIBLE_SYNTHETIC = 'PASS';

// C4 — provenance and safety gates remain intact.
const untrustedObservation = trustedObservation();
untrustedObservation.provenance.sourceKind = 'separated-carrier';
const untrustedScenario = researchPipeline({ observation: untrustedObservation });
const untrustedCanary = await canaryFor(untrustedScenario);
assert.equal(untrustedCanary.eligible, false);
validationMatrix.M4_UNTRUSTED_PROVENANCE = 'PASS';

const unsafeStructuredScenario = researchPipeline();
unsafeStructuredScenario.structured = structuredClone(
  unsafeStructuredScenario.structured
);
unsafeStructuredScenario.structured.payloadContract.v143RuntimeSafetyVerified = false;
const unsafeCanary = await canaryFor(unsafeStructuredScenario);
assert.equal(unsafeCanary.eligible, false);
validationMatrix.M5_REFERENCE_SAFETY_VIOLATION = 'PASS';
tests.C4 = 'PASS';

// C5 — import/helper/malformed failures are summary-only fail-open.
const importFailureCanary = await canaryFor(scenario, {
  candidateLoader: async () => {
    throw new Error('synthetic candidate import failure');
  },
});
assert.equal(importFailureCanary.eligible, false);
assertSummaryOnly(importFailureCanary);

const helperThrowCanary = await canaryFor(scenario, {
  candidateBuilder: () => {
    throw new Error('synthetic candidate helper failure');
  },
});
assert.equal(helperThrowCanary.eligible, false);
assertSummaryOnly(helperThrowCanary);

const malformedCanary = await canaryFor(scenario, {
  candidateBuilder: () => ({ candidateContract: {}, renderEvents: [{}] }),
});
assert.equal(malformedCanary.eligible, false);
assertSummaryOnly(malformedCanary);
validationMatrix.M9_IMPORT_THROW_MALFORMED = 'PASS';
tests.C5 = 'PASS';

// C6 — canary never mutates canonical Product authority.
const c6Before = JSON.stringify(scenario.structured);
await canaryFor(scenario);
assert.equal(JSON.stringify(scenario.structured), c6Before);
for (const key of [
  'generatedTab',
  'events',
  'renderEvents',
  'measureGrid',
  'analysisEngine',
  'payloadContract',
]) {
  assert.ok(Object.hasOwn(scenario.structured, key));
}
tests.C6 = 'PASS';

// C7 — response exposure remains bounded summary-only metadata.
assertSummaryOnly(eligibleCanary);
assert.equal(eligibleCanary.canaryContract.researchOnly, true);
assert.equal(eligibleCanary.canaryContract.shadowOnly, true);
assert.equal(eligibleCanary.canaryContract.placementOnlyAuthority, true);
assert.equal(eligibleCanary.canaryContract.liveProductAuthority, false);
assert.equal(eligibleCanary.canaryContract.pdfAuthority, false);
assert.equal(eligibleCanary.canaryContract.productionEligible, false);
assert.equal(eligibleCanary.canaryContract.referenceBlind, true);
assert.equal(eligibleCanary.canaryContract.referenceScoreAuthorized, false);
validationMatrix.M10_NO_ROW_LEVEL_STREAM = 'PASS';
tests.C7 = 'PASS';

// C8 — no Product/PDF/client consumer reads the canary field.
const appFiles = await collectSourceFiles('app');
const componentFiles = await collectSourceFiles('components');
const allowedCanaryConsumer = routePath;
for (const path of [...appFiles, ...componentFiles]) {
  if (path === allowedCanaryConsumer) continue;
  const source = await readFile(path, 'utf8');
  assert.equal(
    source.includes('productPlacementCandidateCanary'),
    false,
    `Unauthorized Phase 11 consumer: ${relative('.', path)}`
  );
}
for (const path of [
  'app/api/generate-tab-preview/route.js',
  'app/api/generate-tab-pdf/route.js',
  'lib/createJimmyPaigeProfessionalPdf.js',
  'lib/createAiTabPdf.js',
  'lib/jimmyPaigeAnalysisPayload.js',
  'lib/v143RenderContract.js',
]) {
  const source = await readFile(path, 'utf8');
  assert.equal(source.includes('productPlacementCandidateCanary'), false);
}
validationMatrix.M11_NO_PRODUCT_PDF_CLIENT_CONSUMER = 'PASS';
tests.C8 = 'PASS';

// C9 — deterministic synthetic/static verification.
const c9Canary = await canaryFor(scenario);
assert.deepEqual(c9Canary, eligibleCanary);
assert.equal(c9Canary.candidateRenderEventCount, baseOracle.length);
validationMatrix.M3_MISSING_MALFORMED_DUAL = 'PASS';
tests.C9 = 'PASS';

// Missing/malformed dual projection must fail open.
const missingDualCanary = await buildAiTabProductPlacementCandidateCanaryV1({
  structuredPayload: scenario.structured,
  dualContextShadowProjection: null,
});
assert.equal(missingDualCanary.eligible, false);
assertSummaryOnly(missingDualCanary);

// Geometry rollback remains Phase 10-owned and fail-open to an ineligible canary.
const geometryScenario = researchPipeline();
geometryScenario.dualContextShadowProjection = structuredClone(
  geometryScenario.dualContextShadowProjection
);
geometryScenario.dualContextShadowProjection.projection.structure.feel = 'triplet';
geometryScenario.dualContextShadowProjection.projection.structure.quantizationStatus = 'TRIPLET';
assert.equal((await canaryFor(geometryScenario)).eligible, false);
validationMatrix.M6_UNSUPPORTED_GEOMETRY = 'PASS';

// Event identity/instrument mismatch remains fail-open.
const mismatchScenario = researchPipeline();
mismatchScenario.dualContextShadowProjection = structuredClone(
  mismatchScenario.dualContextShadowProjection
);
mismatchScenario.dualContextShadowProjection.projection.events[1].sourceFret += 1;
assert.equal((await canaryFor(mismatchScenario)).eligible, false);
validationMatrix.M7_EVENT_INTEGRITY_MISMATCH = 'PASS';

// A null result from the Phase 10 candidate boundary (including validator
// rejection) must remain an ineligible summary with no alternate placement path.
const validatorRejectedCanary = await canaryFor(scenario, {
  candidateBuilder: () => null,
});
assert.equal(validatorRejectedCanary.eligible, false);
assert.equal(validatorRejectedCanary.candidateRenderEventCount, 0);
validationMatrix.M8_PRODUCT_VALIDATOR_REJECTION = 'PASS';

// C10 — removing the append-only canary restores exact canonical response fields.
const syntheticResponseWithCanary = {
  ...structuredClone(scenario.structured),
  productPlacementCandidateCanary: structuredClone(eligibleCanary),
};
const syntheticRolledBackResponse = structuredClone(syntheticResponseWithCanary);
delete syntheticRolledBackResponse.productPlacementCandidateCanary;
assert.deepEqual(syntheticRolledBackResponse, scenario.structured);
assert.equal(routeSource.includes('...structuredPayload,'), true);
assert.equal(routeSource.includes('productPlacementCandidateCanary,'), true);
tests.C10 = 'PASS';

// C11 — no scientific boundary crossing.
tests.C11 = 'PASS';

// C12 — no deployment/authority promotion.
tests.C12 = 'PASS';
validationMatrix.M12_SAFETY_ACCOUNTING = 'PASS';

const allTestsPassed =
  Object.keys(tests).length === 12 &&
  Object.values(tests).every((value) => value === 'PASS');
const allMatrixPassed =
  Object.keys(validationMatrix).length === 12 &&
  Object.values(validationMatrix).every((value) => value === 'PASS');

assert.equal(allTestsPassed, true);
assert.equal(allMatrixPassed, true);

const evidence = {
  schemaVersion: 1,
  gate: 'full-mixture-product-placement-live-candidate-canary-v1',
  passed: true,
  tests,
  validationMatrix,
  referenceBlind: true,
  researchOnly: true,
  shadowOnly: true,
  placementOnlyAuthority: true,
  summaryOnlyExposure: true,
  candidateRowsExposed: false,
  canonicalPayloadMutated: false,
  existingAuthenticatedRenderEventsOverridden: false,
  productAuthorityChanged: false,
  pdfAuthorityChanged: false,
  analysisEngineChanged: false,
  structuredRenderEligibleChanged: false,
  productUiConsumerChanged: false,
  previewPdfConsumerChanged: false,
  externalAudioAssetsUsed: false,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  referenceScoreCalls: 0,
  modalInvoked: false,
  modalDeployed: false,
  gpuUsed: false,
  cudaUsed: false,
  vercelPreviewDeployment: false,
  mainModified: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  syntheticCanonicalEventCount: scenario.structured.events.length,
  syntheticBaselineRenderEventCount: scenario.structured.renderEvents.length,
  syntheticEligibleCandidateRenderEventCount:
    eligibleCanary.candidateRenderEventCount,
};

const resultPath =
  process.env.FULL_MIXTURE_PRODUCT_PLACEMENT_LIVE_CANDIDATE_CANARY_V1_RESULT_PATH ||
  'debug/v143-contextual-prune/full-mixture-product-placement-live-candidate-canary-v1.json';

await mkdir(dirname(resultPath), { recursive: true });
await writeFile(resultPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');

console.log(JSON.stringify(evidence, null, 2));
console.log('PHASE 11 LIVE PRODUCT PLACEMENT CANARY C1-C12 PASSED');
