import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '../lib/aiTabMixtureStructureContextV1.mjs';
import { buildAiTabMixtureStructureContextFromAnalyzerObservationV1 } from '../lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';
import { buildAiTabDualContextShadowFusionV1 } from '../lib/aiTabDualContextShadowFusionV1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
};

function normalizeConditioning(structurePrior = {}, instrumentConfig = {}) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior,
      instrumentConfig: {
        role: 'rhythm',
        ...instrumentConfig,
      },
    },
    'rhythm'
  );
}

function field(value, confidence = 0.85, method = 'synthetic-full-mixture-estimator-v1') {
  return {
    value,
    confidence,
    method,
  };
}

function trustedObservation(fields = {}, overrides = {}) {
  return {
    version: 1,
    provenance: {
      sourceKind: 'full-mixture',
      sourceIdentity: 'request-audio',
      referenceBlind: true,
      referenceRuntimeInputUsed: false,
      ...(overrides.provenance || {}),
    },
    diagnostics: {
      referenceBlind: true,
      carrierInputUsed: false,
      transcribedEventInputUsed: false,
      wavAdapter: {
        fullMixtureOnly: true,
        separatedCarrierUsed: false,
        transcribedEventInputUsed: false,
        ...(overrides.wavAdapter || {}),
      },
      ...(overrides.diagnostics || {}),
    },
    ...fields,
  };
}

function completeStraightObservation() {
  return trustedObservation({
    tempoBpm: field(120, 0.93, 'synthetic-onset-periodicity-v1'),
    timeSignature: field(
      { numerator: 4, denominator: 4 },
      0.88,
      'synthetic-accent-meter-v1'
    ),
    pickupBeats: field(0, 0.81, 'synthetic-downbeat-phase-v1'),
    feel: field('straight', 0.76, 'synthetic-subdivision-evidence-v1'),
  });
}

function baselineContext(conditioning) {
  return buildAiTabMixtureStructureContextV1({
    structurePrior: conditioning.structurePrior,
    mixtureObservation: null,
    mixtureSource,
  });
}

function admittedContext(conditioning, analyzerObservation) {
  const baseline = baselineContext(conditioning);
  return {
    baseline,
    context: buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
      baselineContext: baseline,
      analyzerObservation,
      structurePrior: conditioning.structurePrior,
      mixtureSource,
    }),
  };
}

function fuse(events, conditioning, mixtureStructureContext) {
  return buildAiTabDualContextShadowFusionV1({
    events,
    conditioning,
    mixtureStructureContext,
  });
}

function instrumentProjectionRows(fusion) {
  return fusion.projection.events.map((event) => ({
    sourceEventIndex: event.sourceEventIndex,
    midi: event.midi,
    sourceStringIndex: event.sourceStringIndex,
    sourceFret: event.sourceFret,
    conditionedStringIndex: event.conditionedStringIndex,
    conditionedFret: event.conditionedFret,
    physicalOpenMidi: event.physicalOpenMidi,
    soundingOpenMidi: event.soundingOpenMidi,
    playableCandidateCount: event.playableCandidateCount,
    playableUnderConditioning: event.playableUnderConditioning,
  }));
}

function timingProjectionRows(fusion) {
  return fusion.projection.events.map((event) => ({
    sourceEventIndex: event.sourceEventIndex,
    sourceStart: event.sourceStart,
    projectedStart: event.projectedStart,
    measureNumber: event.measureNumber,
    signatureUnitNumber: event.signatureUnitNumber,
    signatureUnitFraction: event.signatureUnitFraction,
    subdivisionIndex: event.subdivisionIndex,
    pickup: event.pickup,
  }));
}

const events = [
  { eventIndex: 11, start: 0, end: 0.08, midi: 64, stringIndex: 0, fret: 0 },
  { eventIndex: 12, start: 0.13, end: 0.22, midi: 67, stringIndex: 1, fret: 3 },
  { eventIndex: 13, start: 0.26, end: 0.36, midi: 69, stringIndex: 1, fret: 5 },
  { eventIndex: 14, start: 0.51, end: 0.64, midi: 71, stringIndex: 1, fret: 7 },
  { eventIndex: 15, start: 1.02, end: 1.16, midi: 72, stringIndex: 0, fret: 8 },
  { eventIndex: 16, start: 2.02, end: 2.18, midi: 76, stringIndex: 0, fret: 12 },
  { eventIndex: 17, start: 3.49, end: 3.62, midi: 74, stringIndex: 0, fret: 10 },
];

const route = await readFile('app/api/analyze-audio-tab/route.js', 'utf8');
const previewRoute = await readFile('app/api/generate-tab-preview/route.js', 'utf8');
const fullPdfRoute = await readFile('app/api/generate-tab-pdf/route.js', 'utf8');

const tests = {};

// T1 — null observation preserves the unresolved Auto shadow baseline.
const autoConditioning = normalizeConditioning();
const autoBaselineContext = baselineContext(autoConditioning);
const autoBaselineFusion = fuse(events, autoConditioning, autoBaselineContext);
assert.equal(autoBaselineContext.observationStatus, 'NOT_CONNECTED');
assert.equal(autoBaselineContext.completeForMeasureProjection, false);
assert.equal(autoBaselineFusion.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
assert.equal(autoBaselineFusion.projection.structure.quantizationStatus, 'UNRESOLVED_AUTO_STRUCTURE');
for (const event of autoBaselineFusion.projection.events) {
  assert.equal(event.projectedStart, null);
  assert.equal(event.measureNumber, null);
  assert.equal(event.signatureUnitNumber, null);
  assert.equal(event.subdivisionIndex, null);
  assert.equal(event.pickup, null);
}
tests.T1 = 'PASS';

// T2 — a trusted complete observation produces the expected deterministic shadow timing effect.
const trusted = completeStraightObservation();
const { context: trustedContext } = admittedContext(autoConditioning, trusted);
const trustedFusion = fuse(events, autoConditioning, trustedContext);
assert.equal(trustedContext.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.deepEqual(trustedContext.resolved, {
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
assert.equal(trustedContext.completeForMeasureProjection, true);
assert.equal(trustedContext.feelResolved, true);
assert.equal(trustedFusion.projection.structure.status, 'EXPLICIT_STRUCTURE_RESOLVED');
assert.equal(trustedFusion.projection.structure.quantizationStatus, 'STRAIGHT');
assert.equal(trustedFusion.projection.structure.subdivisionSeconds, 0.125);
assert.deepEqual(
  trustedFusion.projection.events.map((event) => event.projectedStart),
  [0, 0.125, 0.25, 0.5, 1, 2, 3.5]
);
assert.deepEqual(
  trustedFusion.projection.events.map((event) => event.subdivisionIndex),
  [0, 1, 2, 4, 8, 16, 28]
);
assert.deepEqual(
  trustedFusion.projection.events.map((event) => event.measureNumber),
  [1, 1, 1, 1, 1, 2, 2]
);
assert.equal(trustedFusion.projection.events[5].signatureUnitNumber, 1);
assert.equal(trustedFusion.projection.events[6].signatureUnitNumber, 4);
tests.T2 = 'PASS';

// T3 — identical inputs produce deep-equal shadow output on repeated calls.
const deterministicA = fuse(events, autoConditioning, trustedContext);
const deterministicB = fuse(events, autoConditioning, trustedContext);
assert.deepEqual(deterministicA, deterministicB);
assert.equal(JSON.stringify(deterministicA), JSON.stringify(deterministicB));
tests.T3 = 'PASS';

// T4 — global structure observation cannot alter instrument authority/decoding.
assert.deepEqual(
  trustedFusion.instrumentAuthority,
  autoBaselineFusion.instrumentAuthority
);
assert.deepEqual(
  trustedFusion.projection.instrumentConfig,
  autoBaselineFusion.projection.instrumentConfig
);
assert.deepEqual(
  instrumentProjectionRows(trustedFusion),
  instrumentProjectionRows(autoBaselineFusion)
);
assert.notDeepEqual(
  timingProjectionRows(trustedFusion),
  timingProjectionRows(autoBaselineFusion)
);
tests.T4 = 'PASS';

// T5 — source events are never mutated by baseline or admitted shadow projection.
const mutableFixture = structuredClone(events);
const beforeMutableFixture = structuredClone(mutableFixture);
fuse(mutableFixture, autoConditioning, autoBaselineContext);
fuse(mutableFixture, autoConditioning, trustedContext);
assert.deepEqual(mutableFixture, beforeMutableFixture);
tests.T5 = 'PASS';

// T6 — explicit user structure priors retain field-by-field authority over a conflicting observation.
const explicitConditioning = normalizeConditioning({
  tempoBpm: 96,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 1,
  feel: 'triplet',
});
const explicitBaseline = baselineContext(explicitConditioning);
const conflictingObservation = trustedObservation({
  tempoBpm: field(140),
  timeSignature: field({ numerator: 5, denominator: 4 }),
  pickupBeats: field(0),
  feel: field('straight'),
});
const { context: explicitAdmitted } = admittedContext(
  explicitConditioning,
  conflictingObservation
);
assert.deepEqual(explicitAdmitted.resolved, explicitBaseline.resolved);
for (const source of Object.values(explicitAdmitted.fieldSources)) {
  assert.equal(source.source, 'user-prior');
}
assert.deepEqual(
  fuse(events, explicitConditioning, explicitAdmitted).projection,
  fuse(events, explicitConditioning, explicitBaseline).projection
);
tests.T6 = 'PASS';

// T7 — forbidden provenance fails open to the exact baseline and exact baseline shadow effect.
const rejectedObservations = [
  trustedObservation({}, { provenance: { sourceKind: 'separated-stem' } }),
  trustedObservation({}, { provenance: { sourceIdentity: 'carrier-audio' } }),
  trustedObservation({}, { provenance: { referenceBlind: false } }),
  trustedObservation({}, { provenance: { referenceRuntimeInputUsed: true } }),
  trustedObservation({}, { diagnostics: { carrierInputUsed: true } }),
  trustedObservation({}, { diagnostics: { transcribedEventInputUsed: true } }),
  trustedObservation({}, { wavAdapter: { fullMixtureOnly: false } }),
  trustedObservation({}, { wavAdapter: { separatedCarrierUsed: true } }),
  trustedObservation({}, { wavAdapter: { transcribedEventInputUsed: true } }),
];
for (const observation of rejectedObservations) {
  const { baseline, context } = admittedContext(autoConditioning, observation);
  assert.strictEqual(context, baseline);
  assert.deepEqual(
    fuse(events, autoConditioning, context),
    fuse(events, autoConditioning, baseline)
  );
}
tests.T7 = 'PASS';

// T8 — malformed/out-of-contract fields also fail open to exact baseline behavior.
const invalidObservations = [
  undefined,
  null,
  [],
  'bad',
  trustedObservation({ tempoBpm: field(401) }),
  trustedObservation({ tempoBpm: field(120, 2) }),
  trustedObservation({ timeSignature: field({ numerator: 4, denominator: 3 }) }),
  trustedObservation({ pickupBeats: field(-1) }),
  trustedObservation({ feel: field('auto') }),
];
for (const observation of invalidObservations) {
  const { baseline, context } = admittedContext(autoConditioning, observation);
  assert.strictEqual(context, baseline);
  assert.deepEqual(
    fuse(events, autoConditioning, context),
    fuse(events, autoConditioning, baseline)
  );
}
tests.T8 = 'PASS';

// T9 — partial trusted observations fill only unresolved fields and never fabricate completeness.
const tempoOnlyObservation = trustedObservation({
  tempoBpm: field(120),
});
const { context: tempoOnlyContext } = admittedContext(
  autoConditioning,
  tempoOnlyObservation
);
assert.deepEqual(tempoOnlyContext.resolved, {
  tempoBpm: 120,
  timeSignature: null,
  pickupBeats: null,
  feel: 'auto',
});
assert.equal(tempoOnlyContext.completeForMeasureProjection, false);
const tempoOnlyFusion = fuse(events, autoConditioning, tempoOnlyContext);
assert.equal(tempoOnlyFusion.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
for (const event of tempoOnlyFusion.projection.events) {
  assert.equal(event.projectedStart, null);
  assert.equal(event.measureNumber, null);
}
const missingTempoConditioning = normalizeConditioning({
  tempoBpm: null,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
const { context: completedByTempo } = admittedContext(
  missingTempoConditioning,
  tempoOnlyObservation
);
assert.equal(completedByTempo.completeForMeasureProjection, true);
assert.equal(
  fuse(events, missingTempoConditioning, completedByTempo).projection.structure.status,
  'EXPLICIT_STRUCTURE_RESOLVED'
);
tests.T9 = 'PASS';

// T10 — straight/triplet only select the expected shadow grid; Auto does not invent one.
const autoFeelConditioning = normalizeConditioning({
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'auto',
});
const autoFeelBaseline = baselineContext(autoFeelConditioning);
const autoFeelFusion = fuse(events, autoFeelConditioning, autoFeelBaseline);
assert.equal(autoFeelFusion.projection.structure.status, 'EXPLICIT_STRUCTURE_RESOLVED');
assert.equal(autoFeelFusion.projection.structure.quantizationStatus, 'UNRESOLVED_AUTO_FEEL');
assert.equal(autoFeelFusion.projection.structure.subdivisionSeconds, null);
for (let index = 0; index < events.length; index += 1) {
  assert.equal(autoFeelFusion.projection.events[index].projectedStart, events[index].start);
  assert.equal(autoFeelFusion.projection.events[index].subdivisionIndex, null);
}
const straightFeelContext = admittedContext(
  autoFeelConditioning,
  trustedObservation({ feel: field('straight') })
).context;
const tripletFeelContext = admittedContext(
  autoFeelConditioning,
  trustedObservation({ feel: field('triplet') })
).context;
const straightFeelFusion = fuse(events, autoFeelConditioning, straightFeelContext);
const tripletFeelFusion = fuse(events, autoFeelConditioning, tripletFeelContext);
assert.equal(straightFeelFusion.projection.structure.quantizationStatus, 'STRAIGHT');
assert.equal(straightFeelFusion.projection.structure.subdivisionSeconds, 0.125);
assert.equal(tripletFeelFusion.projection.structure.quantizationStatus, 'TRIPLET');
assert.equal(tripletFeelFusion.projection.structure.subdivisionSeconds, 0.166666667);
assert.notDeepEqual(
  timingProjectionRows(straightFeelFusion),
  timingProjectionRows(tripletFeelFusion)
);
tests.T10 = 'PASS';

// T11 — both context and fusion remain explicitly research-only/reference-blind.
assert.equal(trustedContext.contextContract.referenceBlind, true);
assert.equal(trustedContext.contextContract.referenceScoreAuthorized, false);
assert.equal(trustedContext.contextContract.carrierStructureBorrowingAllowed, false);
assert.equal(trustedContext.contextContract.productionEligible, false);
assert.equal(trustedFusion.fusionContract.shadowOnly, true);
assert.equal(trustedFusion.fusionContract.referenceBlind, true);
assert.equal(trustedFusion.fusionContract.referenceScoreAuthorized, false);
assert.equal(trustedFusion.fusionContract.carrierStructureBorrowingAllowed, false);
assert.equal(trustedFusion.fusionContract.productionEligible, false);
assert.equal(trustedFusion.projection.shadowContract.shadowOnly, true);
assert.equal(trustedFusion.projection.shadowContract.productionEligible, false);
tests.T11 = 'PASS';

// T12 — canonical payload and Product/PDF paths stay statically isolated from research shadow authority.
const structuredPayloadIndex = route.indexOf('const structuredPayload =');
const baselineContextIndex = route.indexOf('const baselineMixtureStructureContext =');
const dualContextIndex = route.indexOf('const dualContextShadowProjection =');
assert.ok(structuredPayloadIndex >= 0);
assert.ok(baselineContextIndex > structuredPayloadIndex);
assert.ok(dualContextIndex > baselineContextIndex);
const structuredPayloadBlock = route.slice(
  structuredPayloadIndex,
  route.indexOf('const conditioningContract =', structuredPayloadIndex)
);
assert.equal(structuredPayloadBlock.includes('mixtureObservation'), false);
assert.equal(structuredPayloadBlock.includes('mixtureStructureContext'), false);
assert.equal(structuredPayloadBlock.includes('dualContextShadowProjection'), false);
for (const productRoute of [previewRoute, fullPdfRoute]) {
  assert.equal(productRoute.includes('mixtureObservation'), false);
  assert.equal(productRoute.includes('mixtureStructureContext'), false);
  assert.equal(productRoute.includes('dualContextShadowProjection'), false);
}
assert.ok(route.includes('...structuredPayload,'));
assert.ok(route.includes('dualContextShadowProjection,'));
tests.T12 = 'PASS';

const evidence = {
  schemaVersion: 1,
  gate: 'full-mixture-admitted-shadow-effect-validation-v1',
  referenceBlind: true,
  shadowOnly: true,
  trustedObservationEffectObserved:
    timingProjectionRows(trustedFusion).some(
      (row, index) => row.projectedStart !== timingProjectionRows(autoBaselineFusion)[index].projectedStart
    ),
  deterministicShadowEffect: true,
  instrumentAuthorityInvariant: true,
  sourceEventsMutated: false,
  productAuthorityChanged: false,
  pdfAuthorityChanged: false,
  canonicalAnalyzerOutputChanged: false,
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

assert.equal(evidence.trustedObservationEffectObserved, true);

const resultPath = String(
  process.env.FULL_MIXTURE_ADMITTED_SHADOW_EFFECT_V1_RESULT_PATH || ''
).trim();

if (resultPath) {
  const { mkdir, writeFile } = await import('node:fs/promises');
  const { dirname } = await import('node:path');
  await mkdir(dirname(resultPath), { recursive: true });
  await writeFile(resultPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('FULL MIXTURE ADMITTED SHADOW EFFECT VALIDATION V1 T1-T12 VERIFIED');
