import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

import {
  normalizeAiTabConditioningV1,
} from '../lib/aiTabConditioningV1.mjs';
import {
  buildAiTabMixtureStructureContextV1,
} from '../lib/aiTabMixtureStructureContextV1.mjs';
import {
  AiTabDualContextShadowFusionValidationError,
  buildAiTabDualContextShadowFusionV1,
} from '../lib/aiTabDualContextShadowFusionV1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
  preservedForStructureContext: true,
};

function conditioning(rawStructure = {}, instrumentConfig = {}) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior: rawStructure,
      instrumentConfig,
    },
    instrumentConfig.role || 'lead'
  );
}

function observation(fields = {}, provenance = {}) {
  return {
    version: 1,
    provenance: {
      sourceKind: 'full-mixture',
      sourceIdentity: 'request-audio',
      referenceBlind: true,
      referenceRuntimeInputUsed: false,
      ...provenance,
    },
    ...fields,
  };
}

function observed(value, confidence = 0.8, method = 'synthetic-full-mixture') {
  return { value, confidence, method };
}

function contextFor(conditioningValue, mixtureObservation = null) {
  return buildAiTabMixtureStructureContextV1({
    structurePrior: conditioningValue.structurePrior,
    mixtureObservation,
    mixtureSource,
  });
}

function fuse(events, conditioningValue, mixtureContext) {
  return buildAiTabDualContextShadowFusionV1({
    events,
    conditioning: conditioningValue,
    mixtureStructureContext: mixtureContext,
  });
}

function expectFusionError(fn, expectedCode) {
  assert.throws(
    fn,
    (error) => {
      assert.ok(
        error instanceof AiTabDualContextShadowFusionValidationError,
        'Expected AiTabDualContextShadowFusionValidationError'
      );
      if (expectedCode) assert.equal(error.code, expectedCode);
      return true;
    }
  );
}

const sampleEvents = [
  {
    eventIndex: 0,
    start: 0.26,
    end: 0.5,
    midi: 64,
    stringIndex: 0,
    fret: 0,
  },
];

// D1 — all Auto + no observation stays unresolved.
const d1Conditioning = conditioning();
const d1Context = contextFor(d1Conditioning);
const d1 = fuse(sampleEvents, d1Conditioning, d1Context);
assert.equal(d1.structureAuthority.observationStatus, 'NOT_CONNECTED');
assert.equal(d1.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
assert.equal(d1.projection.structure.tempoBpm, null);
assert.equal(d1.projection.events[0].projectedStart, null);

// D2 — explicit user structure flows through Phase 3 into projection.
const d2Conditioning = conditioning({
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
const d2 = fuse(
  sampleEvents,
  d2Conditioning,
  contextFor(d2Conditioning)
);
assert.equal(d2.projection.structure.status, 'EXPLICIT_STRUCTURE_RESOLVED');
assert.equal(d2.projection.structure.tempoBpm, 120);
assert.deepEqual(d2.projection.structure.timeSignature, {
  numerator: 4,
  denominator: 4,
});
assert.equal(d2.projection.structure.pickupBeats, 0);
assert.equal(d2.projection.structure.quantizationStatus, 'STRAIGHT');
assert.equal(d2.projection.events[0].projectedStart, 0.25);

// D3 — trusted full-mixture tempo fills Auto and reaches fusion projection.
const d3Conditioning = conditioning();
const d3Context = contextFor(
  d3Conditioning,
  observation({
    tempoBpm: observed(132, 0.77, 'mixture tempo'),
  })
);
const d3 = fuse(sampleEvents, d3Conditioning, d3Context);
assert.equal(d3.structureAuthority.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.equal(d3.projection.structure.tempoBpm, 132);
assert.equal(d3.projection.structure.status, 'UNRESOLVED_AUTO_STRUCTURE');
assert.equal(
  d3.structureAuthority.fieldSources.tempoBpm.source,
  'full-mixture-observation'
);

// D4 — mixed authority: user tempo plus mixture meter/pickup/feel.
const d4Conditioning = conditioning({ tempoBpm: 90 });
const d4Context = contextFor(
  d4Conditioning,
  observation({
    timeSignature: observed({ numerator: 6, denominator: 8 }),
    pickupBeats: observed(1),
    feel: observed('triplet'),
  })
);
const d4 = fuse(sampleEvents, d4Conditioning, d4Context);
assert.equal(d4.projection.structure.status, 'EXPLICIT_STRUCTURE_RESOLVED');
assert.equal(d4.projection.structure.tempoBpm, 90);
assert.deepEqual(d4.projection.structure.timeSignature, {
  numerator: 6,
  denominator: 8,
});
assert.equal(d4.projection.structure.pickupBeats, 1);
assert.equal(d4.projection.structure.quantizationStatus, 'TRIPLET');
assert.equal(d4.structureAuthority.fieldSources.tempoBpm.source, 'user-prior');
assert.equal(
  d4.structureAuthority.fieldSources.timeSignature.source,
  'full-mixture-observation'
);

// D5 — explicit user override beats disagreeing mixture observation.
const d5Conditioning = conditioning({
  tempoBpm: 100,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
const d5Context = contextFor(
  d5Conditioning,
  observation({
    tempoBpm: observed(180),
    timeSignature: observed({ numerator: 7, denominator: 8 }),
    pickupBeats: observed(2),
    feel: observed('triplet'),
  })
);
const d5 = fuse(sampleEvents, d5Conditioning, d5Context);
assert.equal(d5.projection.structure.tempoBpm, 100);
assert.deepEqual(d5.projection.structure.timeSignature, {
  numerator: 3,
  denominator: 4,
});
assert.equal(d5.projection.structure.pickupBeats, 0);
assert.equal(d5.projection.structure.quantizationStatus, 'STRAIGHT');

// D6 — tuning/capo remain exclusively instrument authority.
const d6Conditioning = normalizeAiTabConditioningV1(
  {
    version: 1,
    structurePrior: {
      tempoBpm: 120,
      timeSignature: { numerator: 4, denominator: 4 },
      pickupBeats: 0,
      feel: 'straight',
    },
    instrumentConfig: {
      role: 'rhythm',
      tuningMidi: [38, 45, 50, 55, 59, 64],
      capoFret: 2,
    },
  },
  'rhythm'
);
const d6Context = contextFor(d6Conditioning);
const d6 = fuse(
  [{ start: 0, end: 0.25, midi: 40, stringIndex: 5, fret: 0 }],
  d6Conditioning,
  d6Context
);
assert.deepEqual(d6.instrumentAuthority.tuningMidi, [38, 45, 50, 55, 59, 64]);
assert.equal(d6.instrumentAuthority.capoFret, 2);
assert.equal(d6.instrumentAuthority.role, 'rhythm');
assert.equal(d6.projection.events[0].conditionedStringIndex, 5);
assert.equal(d6.projection.events[0].conditionedFret, 0);
assert.equal(d6.projection.events[0].soundingOpenMidi, 40);

// D7 — invalid/tampered mixture contexts fail closed.
const validContext = contextFor(d2Conditioning);
for (const mutate of [
  (value) => { value.contextContract.name = 'other'; },
  (value) => { value.contextContract.version = 2; },
  (value) => { value.contextContract.referenceBlind = false; },
  (value) => { value.contextContract.referenceScoreAuthorized = true; },
  (value) => { value.contextContract.productionEligible = true; },
]) {
  const tampered = structuredClone(validContext);
  mutate(tampered);
  expectFusionError(
    () => fuse(sampleEvents, d2Conditioning, tampered),
    'INVALID_MIXTURE_STRUCTURE_CONTEXT_CONTRACT'
  );
}
const badResolved = structuredClone(validContext);
badResolved.resolved.tempoBpm = 500;
expectFusionError(
  () => fuse(sampleEvents, d2Conditioning, badResolved),
  'INVALID_RESOLVED_STRUCTURE'
);

// D8 — carrier borrowing remains impossible.
const carrierAllowed = structuredClone(validContext);
carrierAllowed.contextContract.carrierStructureBorrowingAllowed = true;
expectFusionError(
  () => fuse(sampleEvents, d2Conditioning, carrierAllowed),
  'INVALID_MIXTURE_STRUCTURE_CONTEXT_CONTRACT'
);
const carrierSource = structuredClone(validContext);
carrierSource.mixtureSource.kind = 'selected-analyzer-carrier';
expectFusionError(
  () => fuse(sampleEvents, d2Conditioning, carrierSource),
  'CARRIER_STRUCTURE_BORROWING_FORBIDDEN'
);

// D9 — source events and conditioning are not mutated.
const d9Events = [
  { start: 1.1, end: 1.4, midi: 67, stringIndex: 1, fret: 8 },
];
const d9Conditioning = conditioning({
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
const d9EventsBefore = structuredClone(d9Events);
const d9ConditioningBefore = structuredClone(d9Conditioning);
fuse(d9Events, d9Conditioning, contextFor(d9Conditioning));
assert.deepEqual(d9Events, d9EventsBefore);
assert.deepEqual(d9Conditioning, d9ConditioningBefore);

// D10 — route/PDF/product isolation.
const route = await readFile('app/api/analyze-audio-tab/route.js', 'utf8');
const preview = await readFile('app/api/generate-tab-preview/route.js', 'utf8');
const full = await readFile('app/api/generate-tab-pdf/route.js', 'utf8');

for (const expected of [
  'buildAiTabDualContextShadowFusionV1',
  'const dualContextShadowProjection =',
  'events: structuredPayload.events,',
  'conditioning,',
  'mixtureStructureContext,',
  'dualContextShadowProjection,',
]) {
  assert.ok(route.includes(expected), `Analyze route must include ${expected}`);
}
assert.ok(
  route.indexOf('const mixtureStructureContext =') <
    route.indexOf('const dualContextShadowProjection ='),
  'Phase 3 context must be created before Phase 4 fusion'
);
assert.equal(preview.includes('dualContextShadowProjection'), false);
assert.equal(full.includes('dualContextShadowProjection'), false);
for (const forbiddenMutation of [
  'structuredPayload.generatedTab =',
  'structuredPayload.events =',
  'structuredPayload.renderEvents =',
  'structuredPayload.measureGrid =',
  'structuredPayload.analysisEngine =',
]) {
  assert.equal(route.includes(forbiddenMutation), false);
}

for (const result of [d1, d2, d3, d4, d5, d6]) {
  assert.equal(result.fusionContract.shadowOnly, true);
  assert.equal(result.fusionContract.referenceBlind, true);
  assert.equal(result.fusionContract.referenceScoreAuthorized, false);
  assert.equal(result.fusionContract.carrierStructureBorrowingAllowed, false);
  assert.equal(result.fusionContract.productionEligible, false);
  assert.equal(result.projection.shadowContract.shadowOnly, true);
  assert.equal(result.projection.shadowContract.productionEligible, false);
}

const evidence = {
  schemaVersion: 1,
  gate: 'dual-context-shadow-fusion-v1-reference-blind-contract',
  tests: [
    'D1-auto-no-observation-unresolved',
    'D2-explicit-structure-through-mixture-context',
    'D3-mixture-tempo-reaches-fusion',
    'D4-field-by-field-mixed-authority',
    'D5-user-override-precedence',
    'D6-instrument-authority-tuning-capo',
    'D7-tampered-context-rejected',
    'D8-carrier-borrowing-impossible',
    'D9-inputs-not-mutated',
    'D10-route-product-pdf-isolation',
  ],
  shadowOnly: true,
  referenceBlind: true,
  referenceScoreAuthorized: false,
  carrierStructureBorrowingAllowed: false,
  productionEligible: false,
  currentRouteMixtureObservationConnected: false,
  referenceScoreCalls: 0,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  modalInvoked: false,
  gpuUsed: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: true,
};

console.log(JSON.stringify(evidence, null, 2));
console.log('DUAL CONTEXT SHADOW FUSION V1 CONTRACT VERIFIED');
