import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '../lib/aiTabMixtureStructureContextV1.mjs';
import { buildAiTabMixtureStructureContextFromAnalyzerObservationV1 } from '../lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';
import { buildAiTabDualContextShadowFusionV1 } from '../lib/aiTabDualContextShadowFusionV1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
};

const syntheticEvents = [
  { eventIndex: 0, start: 0.05, end: 0.20, midi: 66, stringIndex: 0, fret: 0 },
  { eventIndex: 1, start: 0.38, end: 0.52, midi: 69, stringIndex: 0, fret: 3 },
  { eventIndex: 2, start: 1.03, end: 1.20, midi: 71, stringIndex: 1, fret: 0 },
  { eventIndex: 3, start: 2.10, end: 2.30, midi: 74, stringIndex: 1, fret: 3 },
];

function normalizedConditioning(structurePrior = {}, instrumentOverrides = {}) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior,
      instrumentConfig: {
        role: 'lead',
        tuningMidi: [40, 45, 50, 55, 59, 64],
        capoFret: 2,
        ...instrumentOverrides,
      },
    },
    'lead'
  );
}

function field(value, confidence = 0.8, method = 'synthetic-full-mixture-estimator') {
  return { value, confidence, method };
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

function baselineContext(conditioning) {
  return buildAiTabMixtureStructureContextV1({
    structurePrior: conditioning.structurePrior,
    mixtureObservation: null,
    mixtureSource,
  });
}

function admittedContext(conditioning, analyzerObservation) {
  const baseline = baselineContext(conditioning);
  const result = buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
    baselineContext: baseline,
    analyzerObservation,
    structurePrior: conditioning.structurePrior,
    mixtureSource,
  });
  return { baseline, result };
}

function projection(conditioning, context, events = syntheticEvents) {
  return buildAiTabDualContextShadowFusionV1({
    events,
    conditioning,
    mixtureStructureContext: context,
  });
}

function instrumentEventView(result) {
  return result.projection.events.map((event) => ({
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

const tests = {};
const baseConditioning = normalizedConditioning();
const completeObservation = trustedObservation({
  tempoBpm: field(120, 0.91, 'waveform-onset-periodicity-v1'),
  timeSignature: field({ numerator: 4, denominator: 4 }, 0.82, 'waveform-accent-meter-v1'),
  pickupBeats: field(0, 0.77, 'waveform-downbeat-phase-v1'),
  feel: field('straight', 0.69, 'waveform-subdivision-evidence-v1'),
});

// E1 — null observation preserves unresolved Auto shadow structure.
const e1Baseline = baselineContext(baseConditioning);
const e1Projection = projection(baseConditioning, e1Baseline);
assert.equal(e1Baseline.observationStatus, 'NOT_CONNECTED');
assert.deepEqual(e1Baseline.resolved, {
  tempoBpm: null,
  timeSignature: null,
  pickupBeats: null,
  feel: 'auto',
});
assert.equal(e1Projection.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
for (const event of e1Projection.projection.events) {
  assert.equal(event.projectedStart, null);
  assert.equal(event.subdivisionIndex, null);
  assert.equal(event.measureNumber, null);
}
tests.E1 = 'PASS';

// E2 — trusted complete observation changes only expected shadow timing/measure projection.
const e2Context = admittedContext(baseConditioning, completeObservation).result;
const e2Projection = projection(baseConditioning, e2Context);
assert.equal(e2Context.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.equal(e2Context.completeForMeasureProjection, true);
assert.equal(e2Context.feelResolved, true);
assert.deepEqual(e2Context.resolved, {
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
assert.equal(e2Projection.projection.structure.status, 'EXPLICIT_STRUCTURE_RESOLVED');
assert.equal(e2Projection.projection.structure.quantizationStatus, 'STRAIGHT');
assert.equal(e2Projection.projection.structure.subdivisionsPerSignatureUnit, 4);
assert.deepEqual(
  e2Projection.projection.events.map((event) => event.projectedStart),
  [0, 0.375, 1, 2.125]
);
assert.deepEqual(
  e2Projection.projection.events.map((event) => event.subdivisionIndex),
  [0, 3, 8, 17]
);
assert.deepEqual(
  e2Projection.projection.events.map((event) => event.measureNumber),
  [1, 1, 1, 2]
);
tests.E2 = 'PASS';

// E3 — identical inputs are deterministic across repeated calls.
const e3a = projection(baseConditioning, e2Context);
const e3b = projection(baseConditioning, e2Context);
assert.deepEqual(e3a, e3b);
assert.equal(JSON.stringify(e3a), JSON.stringify(e3b));
tests.E3 = 'PASS';

// E4 — instrument authority and string/fret decoding are invariant to global structure observation.
assert.deepEqual(e1Projection.instrumentAuthority, e2Projection.instrumentAuthority);
assert.deepEqual(instrumentEventView(e1Projection), instrumentEventView(e2Projection));
assert.deepEqual(e2Projection.instrumentAuthority, {
  source: 'conditioning-v1',
  role: 'lead',
  tuningMidi: [40, 45, 50, 55, 59, 64],
  capoFret: 2,
});
tests.E4 = 'PASS';

// E5 — source events are never mutated.
const e5Events = structuredClone(syntheticEvents);
const e5Before = structuredClone(e5Events);
projection(baseConditioning, e2Context, e5Events);
assert.deepEqual(e5Events, e5Before);
tests.E5 = 'PASS';

// E6 — explicit user priors retain exact field-by-field precedence.
const e6Conditioning = normalizedConditioning({
  tempoBpm: 96,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 1,
  feel: 'triplet',
});
const e6Context = admittedContext(e6Conditioning, completeObservation).result;
const e6Projection = projection(e6Conditioning, e6Context);
assert.deepEqual(e6Context.resolved, {
  tempoBpm: 96,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 1,
  feel: 'triplet',
});
for (const source of Object.values(e6Context.fieldSources)) {
  assert.equal(source.source, 'user-prior');
}
assert.equal(e6Projection.projection.structure.quantizationStatus, 'TRIPLET');
assert.equal(e6Projection.projection.structure.tempoBpm, 96);
tests.E6 = 'PASS';

// E7 — forbidden provenance returns exact baseline context and baseline shadow effect.
const e7Bad = trustedObservation({}, {
  provenance: { referenceBlind: false },
});
const e7 = admittedContext(baseConditioning, e7Bad);
assert.strictEqual(e7.result, e7.baseline);
assert.deepEqual(projection(baseConditioning, e7.result), projection(baseConditioning, e7.baseline));
tests.E7 = 'PASS';

// E8 — malformed/out-of-contract fields also return exact baseline effect.
const e8Bad = trustedObservation({ tempoBpm: field(401) });
const e8 = admittedContext(baseConditioning, e8Bad);
assert.strictEqual(e8.result, e8.baseline);
assert.deepEqual(projection(baseConditioning, e8.result), projection(baseConditioning, e8.baseline));
tests.E8 = 'PASS';

// E9 — partial trusted observation fills only its field and cannot fabricate complete projection.
const e9Observation = trustedObservation({
  tempoBpm: field(110, 0.74, 'synthetic-partial-tempo-v1'),
});
const e9Context = admittedContext(baseConditioning, e9Observation).result;
const e9Projection = projection(baseConditioning, e9Context);
assert.equal(e9Context.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.deepEqual(e9Context.resolved, {
  tempoBpm: 110,
  timeSignature: null,
  pickupBeats: null,
  feel: 'auto',
});
assert.equal(e9Context.fieldSources.tempoBpm.source, 'full-mixture-observation');
assert.equal(e9Context.fieldSources.timeSignature.source, 'unresolved');
assert.equal(e9Context.completeForMeasureProjection, false);
assert.equal(e9Projection.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
for (const event of e9Projection.projection.events) {
  assert.equal(event.projectedStart, null);
  assert.equal(event.measureNumber, null);
}
tests.E9 = 'PASS';

// E10 — feel changes only the subdivision grid; auto is never accepted as an observation value.
const e10Conditioning = normalizedConditioning({
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'auto',
});
const e10Baseline = baselineContext(e10Conditioning);
const e10AutoProjection = projection(e10Conditioning, e10Baseline);
const e10StraightContext = admittedContext(
  e10Conditioning,
  trustedObservation({ feel: field('straight') })
).result;
const e10TripletContext = admittedContext(
  e10Conditioning,
  trustedObservation({ feel: field('triplet') })
).result;
const e10Straight = projection(e10Conditioning, e10StraightContext);
const e10Triplet = projection(e10Conditioning, e10TripletContext);
assert.equal(e10AutoProjection.projection.structure.quantizationStatus, 'UNRESOLVED_AUTO_FEEL');
assert.equal(e10AutoProjection.projection.structure.subdivisionsPerSignatureUnit, null);
assert.equal(e10Straight.projection.structure.subdivisionsPerSignatureUnit, 4);
assert.equal(e10Triplet.projection.structure.subdivisionsPerSignatureUnit, 3);
assert.deepEqual(instrumentEventView(e10Straight), instrumentEventView(e10Triplet));
assert.notEqual(
  e10Straight.projection.events[1].projectedStart,
  e10Triplet.projection.events[1].projectedStart
);
const e10InvalidAuto = admittedContext(
  e10Conditioning,
  trustedObservation({ feel: field('auto') })
);
assert.strictEqual(e10InvalidAuto.result, e10InvalidAuto.baseline);
tests.E10 = 'PASS';

// E11 — both context and fusion remain explicitly research-only/reference-blind.
assert.equal(e2Context.contextContract.productionEligible, false);
assert.equal(e2Context.contextContract.referenceBlind, true);
assert.equal(e2Context.contextContract.referenceScoreAuthorized, false);
assert.equal(e2Projection.fusionContract.shadowOnly, true);
assert.equal(e2Projection.fusionContract.productionEligible, false);
assert.equal(e2Projection.fusionContract.referenceBlind, true);
assert.equal(e2Projection.fusionContract.referenceScoreAuthorized, false);
assert.equal(e2Projection.fusionContract.carrierStructureBorrowingAllowed, false);
tests.E11 = 'PASS';

// E12 — canonical Product/PDF construction remains statically isolated from mixture/shadow metadata.
const route = await readFile('app/api/analyze-audio-tab/route.js', 'utf8');
const payloadBuilder = await readFile('lib/jimmyPaigeAnalysisPayload.js', 'utf8');
const previewRoute = await readFile('app/api/generate-tab-preview/route.js', 'utf8');
const pdfRoute = await readFile('app/api/generate-tab-pdf/route.js', 'utf8');
const structuredPayloadIndex = route.indexOf('const structuredPayload =');
const observationTrustIndex = route.indexOf('analyzerObservation: analyzerData?.mixtureObservation');
assert.ok(structuredPayloadIndex >= 0 && observationTrustIndex > structuredPayloadIndex);
for (const source of [payloadBuilder, previewRoute, pdfRoute]) {
  assert.equal(source.includes('mixtureObservation'), false);
  assert.equal(source.includes('mixtureStructureContext'), false);
  assert.equal(source.includes('dualContextShadowProjection'), false);
}
assert.equal(payloadBuilder.includes('generatedTab'), true);
assert.equal(payloadBuilder.includes('renderEvents'), true);
assert.equal(payloadBuilder.includes('measureGrid'), true);
tests.E12 = 'PASS';

const evidence = {
  schemaVersion: 1,
  gate: 'full-mixture-admitted-shadow-effect-validation-v1',
  referenceBlind: true,
  shadowOnly: true,
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
  syntheticEventCount: syntheticEvents.length,
  tests,
  passed:
    Object.keys(tests).length === 12 &&
    new Set(Object.values(tests)).size === 1 &&
    tests.E1 === 'PASS',
};

const resultPath = String(
  process.env.FULL_MIXTURE_ADMITTED_SHADOW_EFFECT_V1_RESULT_PATH || ''
).trim();

if (resultPath) {
  await mkdir(dirname(resultPath), { recursive: true });
  await writeFile(resultPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('FULL MIXTURE ADMITTED SHADOW EFFECT V1 E1-E12 VERIFIED');
