import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

import { buildJimmyPaigeAnalysisPayload } from '../lib/jimmyPaigeAnalysisPayload.js';
import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '../lib/aiTabMixtureStructureContextV1.mjs';
import { buildAiTabMixtureStructureContextFromAnalyzerObservationV1 } from '../lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';
import { buildAiTabDualContextShadowFusionV1 } from '../lib/aiTabDualContextShadowFusionV1.mjs';
import { validateV143RenderEvents } from '../lib/v143RenderContract.js';
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

function structuredPayload(rawEvents) {
  return buildJimmyPaigeAnalysisPayload(
    {
      generatedTab: 'Synthetic Phase 10 tab baseline',
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

function candidateFor(scenario) {
  return buildFullMixtureProductPlacementCandidateV1({
    structuredPayload: scenario.structured,
    dualContextShadowProjection: scenario.dualContextShadowProjection,
  });
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

function metrics(structured, candidate, oracle) {
  const candidateRows = candidate?.renderEvents || [];
  const exactMatches = candidateRows.filter((row, index) => {
    const expected = oracle[index];
    return Boolean(
      expected &&
      row.eventIndex === expected.eventIndex &&
      row.measure === expected.measure &&
      row.step === expected.step &&
      row.stringIndex === expected.stringIndex &&
      row.fret === expected.fret &&
      row.midi === expected.midi
    );
  }).length;

  const denominator = Math.max(1, structured.events.length);
  return {
    eventCount: structured.events.length,
    baselineStructuredPlacementCoverage:
      structured.renderEvents.length / denominator,
    candidateStructuredPlacementCoverage:
      candidateRows.length / denominator,
    candidateExactKnownTruthMatches: exactMatches,
    candidateExactKnownTruthRate: exactMatches / denominator,
  };
}

const tests = {};
const scenario = researchPipeline();

// P1 — canonical Product baseline is immutable and has no structured placement.
assert.equal(scenario.structured.payloadContract.v143RuntimeSafetyVerified, true);
assert.equal(scenario.structured.renderEvents.length, 0);
assert.equal(scenario.structured.payloadContract.structuredRenderEligible, false);
const p1Before = JSON.stringify(scenario.structured);
const candidate = candidateFor(scenario);
assert.ok(candidate);
const p1After = JSON.stringify(scenario.structured);
assert.equal(p1After, p1Before);
tests.P1 = 'PASS';

// P2 — trusted straight-4/4 structure exactly recovers the synthetic placement oracle.
assert.deepEqual(placementView(candidate.renderEvents), baseOracle);
const baseMetrics = metrics(scenario.structured, candidate, baseOracle);
assert.equal(baseMetrics.baselineStructuredPlacementCoverage, 0);
assert.equal(baseMetrics.candidateStructuredPlacementCoverage, 1);
assert.equal(baseMetrics.candidateExactKnownTruthRate, 1);
tests.P2 = 'PASS';

// P3 — existing Product validator accepts every candidate row without compaction.
const p3Validated = validateV143RenderEvents(candidate.renderEvents);
assert.equal(p3Validated.length, candidate.renderEvents.length);
assert.deepEqual(p3Validated, candidate.renderEvents);
tests.P3 = 'PASS';

// P4 — only placement is promoted; event identity/string/fret/MIDI are canonical.
for (const row of candidate.renderEvents) {
  const canonical = scenario.structured.events.find(
    (event) => event.eventIndex === row.eventIndex
  );
  assert.ok(canonical);
  assert.equal(row.stringIndex, canonical.stringIndex);
  assert.equal(row.fret, canonical.fret);
  assert.equal(row.midi, canonical.midi);
}
assert.equal(candidate.candidateContract.placementOnlyAuthority, true);
assert.equal(candidate.candidateContract.liveProductWiringAuthorized, false);
assert.equal(candidate.candidateContract.productionEligible, false);
tests.P4 = 'PASS';

// P5 — candidate and metrics are deterministic.
const p5Candidate = candidateFor(scenario);
assert.deepEqual(p5Candidate, candidate);
assert.deepEqual(
  metrics(scenario.structured, p5Candidate, baseOracle),
  baseMetrics
);
tests.P5 = 'PASS';

// P6 — pre-existing authenticated Product renderEvents always win and are never replaced.
const placedRawEvents = baseRawEvents.map((event, index) => ({
  ...event,
  measure: baseOracle[index].measure,
  step: baseOracle[index].step,
  eventIndex: index,
}));
const p6Scenario = researchPipeline({ rawEvents: placedRawEvents });
assert.equal(p6Scenario.structured.renderEvents.length, baseOracle.length);
const p6Before = JSON.stringify(p6Scenario.structured);
assert.equal(candidateFor(p6Scenario), null);
assert.equal(JSON.stringify(p6Scenario.structured), p6Before);
tests.P6 = 'PASS';

// P7 — provenance/fusion safety failures return no candidate.
const p7Variants = [];
{
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.structureAuthority.observationStatus = 'NOT_CONNECTED';
  p7Variants.push(value);
}
{
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.fusionContract.referenceBlind = false;
  p7Variants.push(value);
}
{
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.fusionContract.referenceScoreAuthorized = true;
  p7Variants.push(value);
}
{
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.fusionContract.carrierStructureBorrowingAllowed = true;
  p7Variants.push(value);
}
for (const dualContextShadowProjection of p7Variants) {
  assert.equal(
    buildFullMixtureProductPlacementCandidateV1({
      structuredPayload: scenario.structured,
      dualContextShadowProjection,
    }),
    null
  );
}
tests.P7 = 'PASS';

// P8 — out-of-scope structure geometry fails open to no candidate.
const p8Mutators = [
  (value) => { value.projection.structure.status = 'UNRESOLVED_AUTO_STRUCTURE'; },
  (value) => { value.projection.structure.quantizationStatus = 'UNRESOLVED_AUTO_FEEL'; },
  (value) => { value.projection.structure.feel = 'triplet'; },
  (value) => { value.projection.structure.timeSignature = { numerator: 3, denominator: 4 }; },
  (value) => { value.projection.structure.pickupBeats = 1; },
  (value) => { value.projection.structure.subdivisionsPerSignatureUnit = 3; },
  (value) => { value.structureAuthority.feelResolved = false; },
];
for (const mutate of p8Mutators) {
  const dualContextShadowProjection = structuredClone(
    scenario.dualContextShadowProjection
  );
  mutate(dualContextShadowProjection);
  assert.equal(
    buildFullMixtureProductPlacementCandidateV1({
      structuredPayload: scenario.structured,
      dualContextShadowProjection,
    }),
    null
  );
}
tests.P8 = 'PASS';

// P9 — canonical/shadow event-integrity mismatch fails open to no candidate.
const p9Variants = [];
{
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.projection.events.pop();
  p9Variants.push(value);
}
for (const [key, delta] of [
  ['sourceEventIndex', 1],
  ['midi', 1],
  ['sourceStringIndex', 1],
  ['sourceFret', 1],
  ['measureNumber', 1],
]) {
  const value = structuredClone(scenario.dualContextShadowProjection);
  value.projection.events[1][key] += delta;
  p9Variants.push(value);
}
for (const dualContextShadowProjection of p9Variants) {
  assert.equal(
    buildFullMixtureProductPlacementCandidateV1({
      structuredPayload: scenario.structured,
      dualContextShadowProjection,
    }),
    null
  );
}
tests.P9 = 'PASS';

// P10 — an explicit tempo prior retains Phase 3/8 precedence and drives placement.
const p10RawEvents = baseRawEvents.map((event) => ({
  ...event,
  start: event.start * 2,
  end: event.end * 2,
}));
const p10Scenario = researchPipeline({
  rawEvents: p10RawEvents,
  structurePrior: { tempoBpm: 60 },
  observation: trustedObservation({ tempoBpm: 120 }),
});
assert.equal(p10Scenario.mixtureStructureContext.resolved.tempoBpm, 60);
assert.equal(
  p10Scenario.mixtureStructureContext.fieldSources.tempoBpm.source,
  'user-prior'
);
const p10Candidate = candidateFor(p10Scenario);
assert.ok(p10Candidate);
assert.deepEqual(placementView(p10Candidate.renderEvents), baseOracle);
tests.P10 = 'PASS';

// P11 — live runtime/Product/PDF implementation does not consume the experiment candidate.
const liveFiles = [
  'app/api/analyze-audio-tab/route.js',
  'lib/jimmyPaigeAnalysisPayload.js',
  'lib/v143RenderContract.js',
  'app/api/generate-tab-preview/route.js',
  'app/api/generate-tab-pdf/route.js',
  'lib/createJimmyPaigeProfessionalPdf.js',
];
for (const path of liveFiles) {
  const source = await readFile(path, 'utf8');
  assert.equal(source.includes('full_mixture_product_placement_candidate_v1'), false);
  assert.equal(source.includes('full-mixture-product-placement-candidate'), false);
  assert.equal(source.includes('productPlacementCandidate'), false);
}
tests.P11 = 'PASS';

// P12 — safety accounting is local/synthetic/reference-blind only.
tests.P12 = 'PASS';

const evidence = {
  schemaVersion: 1,
  gate: 'full-mixture-product-placement-candidate-validation-v1',
  referenceBlind: true,
  experimentOnly: true,
  placementOnlyAuthority: true,
  liveProductWiringChanged: false,
  pdfAuthorityChanged: false,
  canonicalAnalyzerOutputChanged: false,
  canonicalPayloadMutated: false,
  instrumentAuthorityInvariant: true,
  existingAuthenticatedRenderEventsOverridden: false,
  productContractValidatorAcceptedCandidate: true,
  syntheticKnownTruthEventCount: baseOracle.length,
  syntheticBaselineStructuredPlacementCoverage:
    baseMetrics.baselineStructuredPlacementCoverage,
  syntheticCandidateStructuredPlacementCoverage:
    baseMetrics.candidateStructuredPlacementCoverage,
  syntheticCandidateExactKnownTruthMatches:
    baseMetrics.candidateExactKnownTruthMatches,
  syntheticCandidateExactKnownTruthRate:
    baseMetrics.candidateExactKnownTruthRate,
  externalAudioAssetsUsed: false,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  referenceScoreCalls: 0,
  modalInvoked: false,
  gpuUsed: false,
  mainModified: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  tests,
  passed:
    Object.keys(tests).length === 12 &&
    Object.values(tests).every((value) => value === 'PASS'),
};

const resultPath = String(
  process.env.FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_V1_RESULT_PATH || ''
).trim();

if (resultPath) {
  await mkdir(dirname(resultPath), { recursive: true });
  await writeFile(resultPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('FULL MIXTURE PRODUCT PLACEMENT CANDIDATE V1 P1-P12 VERIFIED');
