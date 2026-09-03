import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

import {
  normalizeAiTabConditioningV1,
} from '../lib/aiTabConditioningV1.mjs';
import {
  AiTabMixtureStructureContextValidationError,
  buildAiTabMixtureStructureContextV1,
} from '../lib/aiTabMixtureStructureContextV1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
  preservedForStructureContext: true,
};

function structurePrior(raw = {}) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior: raw,
    },
    'lead'
  ).structurePrior;
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

function field(value, confidence = 0.8, method = 'synthetic-full-mixture-estimator') {
  return {
    value,
    confidence,
    method,
  };
}

function build(prior, mixtureObservation = null) {
  return buildAiTabMixtureStructureContextV1({
    structurePrior: prior,
    mixtureObservation,
    mixtureSource,
  });
}

function expectValidationError(fn, expectedCode) {
  assert.throws(
    fn,
    (error) => {
      assert.ok(
        error instanceof AiTabMixtureStructureContextValidationError,
        'Expected AiTabMixtureStructureContextValidationError'
      );
      if (expectedCode) {
        assert.equal(error.code, expectedCode);
      }
      return true;
    }
  );
}

// M1 — no observation + all Auto.
const m1 = build(structurePrior());
assert.equal(m1.observationStatus, 'NOT_CONNECTED');
assert.deepEqual(m1.resolved, {
  tempoBpm: null,
  timeSignature: null,
  pickupBeats: null,
  feel: 'auto',
});
assert.equal(m1.completeForMeasureProjection, false);
assert.equal(m1.feelResolved, false);
for (const source of Object.values(m1.fieldSources)) {
  assert.equal(source.source, 'unresolved');
  assert.equal(source.confidence, null);
  assert.equal(source.method, null);
}

// M2 — explicit user values resolve without observation.
const m2 = build(structurePrior({
  tempoBpm: 128,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 1,
  feel: 'straight',
}));
assert.deepEqual(m2.resolved, {
  tempoBpm: 128,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 1,
  feel: 'straight',
});
assert.equal(m2.completeForMeasureProjection, true);
assert.equal(m2.feelResolved, true);
for (const source of Object.values(m2.fieldSources)) {
  assert.equal(source.source, 'user-prior');
  assert.equal(source.confidence, null);
  assert.equal(source.method, null);
}

// M3 — trusted mixture fills Auto tempo only.
const m3 = build(
  structurePrior(),
  observation({
    tempoBpm: field(121, 0.73, ' mixture   tempo '),
  })
);
assert.equal(m3.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.equal(m3.resolved.tempoBpm, 121);
assert.equal(m3.fieldSources.tempoBpm.source, 'full-mixture-observation');
assert.equal(m3.fieldSources.tempoBpm.confidence, 0.73);
assert.equal(m3.fieldSources.tempoBpm.method, 'mixture tempo');
assert.equal(m3.resolved.timeSignature, null);
assert.equal(m3.resolved.pickupBeats, null);
assert.equal(m3.resolved.feel, 'auto');
assert.equal(m3.completeForMeasureProjection, false);

// M4 — field-by-field mixture filling without inventing absent tempo.
const m4 = build(
  structurePrior(),
  observation({
    timeSignature: field(
      { numerator: 6, denominator: 8 },
      0.71,
      'synthetic meter'
    ),
    pickupBeats: field(0.5, 0.62, 'synthetic pickup'),
    feel: field('triplet', 0.65, 'synthetic feel'),
  })
);
assert.equal(m4.resolved.tempoBpm, null);
assert.deepEqual(m4.resolved.timeSignature, {
  numerator: 6,
  denominator: 8,
});
assert.equal(m4.resolved.pickupBeats, 0.5);
assert.equal(m4.resolved.feel, 'triplet');
assert.equal(m4.fieldSources.tempoBpm.source, 'unresolved');
assert.equal(m4.fieldSources.timeSignature.source, 'full-mixture-observation');
assert.equal(m4.fieldSources.pickupBeats.source, 'full-mixture-observation');
assert.equal(m4.fieldSources.feel.source, 'full-mixture-observation');
assert.equal(m4.completeForMeasureProjection, false);
assert.equal(m4.feelResolved, true);

// M5 — every explicit user prior wins over a disagreeing mixture observation.
const m5 = build(
  structurePrior({
    tempoBpm: 100,
    timeSignature: { numerator: 3, denominator: 4 },
    pickupBeats: 2,
    feel: 'straight',
  }),
  observation({
    tempoBpm: field(180),
    timeSignature: field({ numerator: 7, denominator: 8 }),
    pickupBeats: field(0),
    feel: field('triplet'),
  })
);
assert.deepEqual(m5.resolved, {
  tempoBpm: 100,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 2,
  feel: 'straight',
});
for (const source of Object.values(m5.fieldSources)) {
  assert.equal(source.source, 'user-prior');
}

// M6 — explicit and observed zero pickup are preserved.
const m6Explicit = build(
  structurePrior({ pickupBeats: 0 }),
  observation({ pickupBeats: field(4) })
);
assert.equal(m6Explicit.resolved.pickupBeats, 0);
assert.equal(m6Explicit.fieldSources.pickupBeats.source, 'user-prior');

const m6Observed = build(
  structurePrior(),
  observation({ pickupBeats: field(0, 0.51, 'zero pickup') })
);
assert.equal(m6Observed.resolved.pickupBeats, 0);
assert.equal(
  m6Observed.fieldSources.pickupBeats.source,
  'full-mixture-observation'
);

// M7 — carrier/separated source is rejected.
for (const sourceKind of [
  'instrument-carrier',
  'separated-stem',
  'v143-rhythm-carrier',
]) {
  expectValidationError(
    () => build(
      structurePrior(),
      observation(
        { tempoBpm: field(120) },
        { sourceKind }
      )
    ),
    'CARRIER_STRUCTURE_BORROWING_FORBIDDEN'
  );
}
expectValidationError(
  () => build(
    structurePrior(),
    {
      version: 1,
      tempoBpm: field(120),
    }
  ),
  'INVALID_MIXTURE_OBSERVATION_PROVENANCE'
);

// M8 — reference provenance is rejected.
expectValidationError(
  () => build(
    structurePrior(),
    observation(
      { tempoBpm: field(120) },
      { referenceBlind: false }
    )
  ),
  'REFERENCE_PROVENANCE_FORBIDDEN'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation(
      { tempoBpm: field(120) },
      { referenceRuntimeInputUsed: true }
    )
  ),
  'REFERENCE_PROVENANCE_FORBIDDEN'
);

// M9 — invalid version, confidence, musical value, method and feel fail closed.
expectValidationError(
  () => build(
    structurePrior(),
    {
      ...observation({ tempoBpm: field(120) }),
      version: 2,
    }
  ),
  'UNSUPPORTED_MIXTURE_OBSERVATION_VERSION'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation({ tempoBpm: field(120, 1.1) })
  ),
  'INVALID_MIXTURE_OBSERVATION_CONFIDENCE'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation({ tempoBpm: field(401) })
  ),
  'INVALID_MIXTURE_OBSERVATION_VALUE'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation({ tempoBpm: field(120, 0.8, '   ') })
  ),
  'INVALID_MIXTURE_OBSERVATION_METHOD'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation({ feel: field('auto') })
  ),
  'INVALID_MIXTURE_OBSERVATION_VALUE'
);
expectValidationError(
  () => build(
    structurePrior(),
    observation({
      timeSignature: field({ numerator: 4, denominator: 3 }),
    })
  ),
  'INVALID_MIXTURE_OBSERVATION_VALUE'
);

// Shared contract safety assertions.
for (const context of [m1, m2, m3, m4, m5, m6Explicit, m6Observed]) {
  assert.equal(context.contextContract.referenceBlind, true);
  assert.equal(context.contextContract.referenceScoreAuthorized, false);
  assert.equal(context.contextContract.carrierStructureBorrowingAllowed, false);
  assert.equal(context.contextContract.productionEligible, false);
  assert.deepEqual(context.mixtureSource, {
    kind: 'full-mixture',
    source: 'request-audio',
  });
}

// M10 — route/product isolation. Current integration must keep the real mixture
// observation channel intentionally disconnected and PDFs must never consume it.
const route = await readFile(
  'app/api/analyze-audio-tab/route.js',
  'utf8'
);
const preview = await readFile(
  'app/api/generate-tab-preview/route.js',
  'utf8'
);
const full = await readFile(
  'app/api/generate-tab-pdf/route.js',
  'utf8'
);

for (const expected of [
  'buildAiTabMixtureStructureContextV1({',
  'structurePrior: conditioning.structurePrior,',
  'mixtureObservation: null,',
  'mixtureSource: conditioningContract.provenance.mixtureSource,',
  'mixtureStructureContext,',
]) {
  assert.ok(
    route.includes(expected),
    `Analyze route must include ${expected}`
  );
}

for (const forbidden of [
  'mixtureObservation: analyzerData',
  'mixtureObservation: liveV143',
  'mixtureObservation: structuredPayload',
]) {
  assert.equal(
    route.includes(forbidden),
    false,
    `Analyze route must not include ${forbidden}`
  );
}

assert.equal(
  preview.includes('mixtureStructureContext'),
  false,
  'Preview PDF must not consume mixtureStructureContext'
);
assert.equal(
  full.includes('mixtureStructureContext'),
  false,
  'Full PDF must not consume mixtureStructureContext'
);

const evidence = {
  schemaVersion: 1,
  gate: 'mixture-structure-context-v1-reference-blind-contract',
  tests: [
    'M1-no-observation-all-auto',
    'M2-explicit-user-values',
    'M3-mixture-fills-auto-tempo',
    'M4-field-by-field-mixture-fill',
    'M5-user-prior-precedence',
    'M6-zero-pickup-preserved',
    'M7-carrier-source-rejected',
    'M8-reference-provenance-rejected',
    'M9-invalid-observation-rejected',
    'M10-route-product-isolation',
  ],
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
console.log('MIXTURE STRUCTURE CONTEXT V1 CONTRACT VERIFIED');
