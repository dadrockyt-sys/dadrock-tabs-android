import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabConditionedShadowProjectionV1 } from '../lib/aiTabConditionedShadowProjectionV1.mjs';

function conditioningFor(
  role,
  {
    tempoBpm = null,
    timeSignature = null,
    pickupBeats = null,
    feel = 'auto',
    tuningMidi,
    capoFret = 0,
  } = {}
) {
  return normalizeAiTabConditioningV1(
    {
      version: 1,
      structurePrior: {
        tempoBpm,
        timeSignature,
        pickupBeats,
        feel,
      },
      instrumentConfig: {
        role,
        ...(tuningMidi ? { tuningMidi } : {}),
        capoFret,
      },
    },
    role
  );
}

function event({
  start,
  end = start + 0.1,
  midi,
  stringIndex = 0,
  fret = 0,
  eventIndex,
}) {
  return {
    ...(Number.isInteger(eventIndex)
      ? { eventIndex }
      : {}),
    start,
    end,
    midi,
    stringIndex,
    fret,
  };
}

// S1 — Auto structure does not invent placement; tuning decode still operates.
const defaultLead = conditioningFor('lead');
const s1 = buildAiTabConditionedShadowProjectionV1({
  events: [
    event({
      start: 0.3,
      midi: 64,
      stringIndex: 0,
      fret: 0,
    }),
  ],
  conditioning: defaultLead,
});
assert.equal(
  s1.structure.status,
  'UNRESOLVED_AUTO_STRUCTURE'
);
assert.equal(
  s1.structure.quantizationStatus,
  'UNRESOLVED_AUTO_STRUCTURE'
);
assert.equal(s1.events[0].projectedStart, null);
assert.equal(s1.events[0].measureNumber, null);
assert.equal(s1.events[0].signatureUnitNumber, null);
assert.equal(s1.events[0].pickup, null);
assert.equal(s1.events[0].playableUnderConditioning, true);

// S2 — 120 BPM 4/4 straight with explicit zero pickup.
const fourFourStraight = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 0,
  feel: 'straight',
});
const s2 = buildAiTabConditionedShadowProjectionV1({
  events: [
    event({ start: 0.26, midi: 64 }),
    event({ start: 2.0, midi: 64 }),
  ],
  conditioning: fourFourStraight,
});
assert.equal(s2.structure.quarterSeconds, 0.5);
assert.equal(s2.structure.signatureUnitSeconds, 0.5);
assert.equal(s2.structure.measureSeconds, 2);
assert.equal(s2.structure.subdivisionSeconds, 0.125);
assert.equal(s2.events[0].projectedStart, 0.25);
assert.equal(s2.events[0].subdivisionIndex, 2);
assert.equal(s2.events[0].measureNumber, 1);
assert.equal(s2.events[0].signatureUnitNumber, 1);
assert.equal(s2.events[0].signatureUnitFraction, 0.5);
assert.equal(s2.events[1].measureNumber, 2);
assert.equal(s2.events[1].signatureUnitNumber, 1);

// S3 — denominator-aware 120 BPM 6/8 straight; no hard-coded 4/4.
const sixEightStraight = conditioningFor('rhythm', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 6,
    denominator: 8,
  },
  pickupBeats: 0,
  feel: 'straight',
});
const s3 = buildAiTabConditionedShadowProjectionV1({
  events: [event({ start: 1.4, midi: 64 })],
  conditioning: sixEightStraight,
});
assert.equal(s3.structure.quarterSeconds, 0.5);
assert.equal(s3.structure.signatureUnitSeconds, 0.25);
assert.equal(s3.structure.measureSeconds, 1.5);
assert.equal(s3.structure.subdivisionSeconds, 0.0625);
assert.equal(s3.events[0].projectedStart, 1.375);
assert.equal(s3.events[0].measureNumber, 1);
assert.equal(s3.events[0].signatureUnitNumber, 6);
assert.equal(s3.events[0].signatureUnitFraction, 0.5);

// S4 — explicit one-signature-unit pickup: pickup is measure 0.
const oneUnitPickup = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 1,
  feel: 'straight',
});
const s4 = buildAiTabConditionedShadowProjectionV1({
  events: [
    event({ start: 0.25, midi: 64 }),
    event({ start: 0.5, midi: 64 }),
  ],
  conditioning: oneUnitPickup,
});
assert.equal(s4.structure.pickupSeconds, 0.5);
assert.equal(s4.events[0].measureNumber, 0);
assert.equal(s4.events[0].pickup, true);
assert.equal(s4.events[1].measureNumber, 1);
assert.equal(s4.events[1].pickup, false);
assert.equal(s4.events[1].signatureUnitNumber, 1);
assert.equal(s4.events[1].signatureUnitFraction, 0);

// S5 — triplet feel uses three subdivisions per signature unit.
const triplet = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 0,
  feel: 'triplet',
});
const s5 = buildAiTabConditionedShadowProjectionV1({
  events: [event({ start: 0.18, midi: 64 })],
  conditioning: triplet,
});
assert.equal(s5.structure.quantizationStatus, 'TRIPLET');
assert.equal(s5.structure.subdivisionsPerSignatureUnit, 3);
assert.equal(s5.structure.subdivisionSeconds, 0.166666667);
assert.equal(s5.events[0].subdivisionIndex, 1);
assert.equal(s5.events[0].projectedStart, 0.166666667);

// S6 — Auto feel resolves bar position but does not invent a subdivision feel.
const autoFeelExplicitStructure = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 0,
  feel: 'auto',
});
const s6 = buildAiTabConditionedShadowProjectionV1({
  events: [event({ start: 0.37, midi: 64 })],
  conditioning: autoFeelExplicitStructure,
});
assert.equal(
  s6.structure.status,
  'EXPLICIT_STRUCTURE_RESOLVED'
);
assert.equal(
  s6.structure.quantizationStatus,
  'UNRESOLVED_AUTO_FEEL'
);
assert.equal(s6.events[0].projectedStart, 0.37);
assert.equal(s6.events[0].subdivisionIndex, null);
assert.equal(s6.events[0].measureNumber, 1);
assert.equal(s6.events[0].signatureUnitNumber, 1);
assert.equal(s6.events[0].signatureUnitFraction, 0.74);

// S7 — Drop D + capo changes deterministic playable decoding while stored
// physical tuning remains unchanged.
const standardLeadExplicit = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 0,
  feel: 'straight',
});
const dropDWithCapo = conditioningFor('lead', {
  tempoBpm: 120,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  pickupBeats: 0,
  feel: 'straight',
  tuningMidi: [38, 45, 50, 55, 59, 64],
  capoFret: 2,
});
const standardDecode = buildAiTabConditionedShadowProjectionV1({
  events: [event({ start: 0, midi: 66 })],
  conditioning: standardLeadExplicit,
});
const dropDDecode = buildAiTabConditionedShadowProjectionV1({
  events: [event({ start: 0, midi: 66 })],
  conditioning: dropDWithCapo,
});
assert.deepEqual(
  dropDDecode.instrumentConfig.tuningMidi,
  [38, 45, 50, 55, 59, 64]
);
assert.equal(dropDDecode.instrumentConfig.capoFret, 2);
assert.equal(standardDecode.events[0].conditionedStringIndex, 1);
assert.equal(standardDecode.events[0].conditionedFret, 7);
assert.equal(dropDDecode.events[0].conditionedStringIndex, 1);
assert.equal(dropDDecode.events[0].conditionedFret, 5);
assert.equal(dropDDecode.events[0].physicalOpenMidi, 59);
assert.equal(dropDDecode.events[0].soundingOpenMidi, 61);

// S8 — an impossible conditioned pitch fails closed without altering source
// placement evidence.
const s8Source = event({
  start: 0.1,
  midi: 20,
  stringIndex: 5,
  fret: 12,
});
const s8 = buildAiTabConditionedShadowProjectionV1({
  events: [s8Source],
  conditioning: standardLeadExplicit,
});
assert.equal(s8.events[0].playableUnderConditioning, false);
assert.equal(s8.events[0].conditionedStringIndex, null);
assert.equal(s8.events[0].conditionedFret, null);
assert.equal(s8.events[0].sourceStringIndex, 5);
assert.equal(s8.events[0].sourceFret, 12);
assert.equal(s8Source.stringIndex, 5);
assert.equal(s8Source.fret, 12);

// S9 — pure adapter and route preserve source/product ownership.
const immutableEvents = [
  event({
    start: 0.26,
    end: 0.8,
    midi: 64,
    stringIndex: 0,
    fret: 0,
    eventIndex: 99,
  }),
];
const immutableConditioning = dropDWithCapo;
const eventsBefore = structuredClone(immutableEvents);
const conditioningBefore = structuredClone(immutableConditioning);
buildAiTabConditionedShadowProjectionV1({
  events: immutableEvents,
  conditioning: immutableConditioning,
});
assert.deepEqual(immutableEvents, eventsBefore);
assert.deepEqual(immutableConditioning, conditioningBefore);

const routeSource = await readFile(
  'app/api/analyze-audio-tab/route.js',
  'utf8'
);
for (const marker of [
  'const conditioningShadowProjection =',
  'buildAiTabConditionedShadowProjectionV1({',
  'events: structuredPayload.events,',
  'conditioningShadowProjection,',
  '...structuredPayload,',
]) {
  assert.ok(
    routeSource.includes(marker),
    `Shadow route marker missing: ${marker}`
  );
}
for (const forbiddenMutation of [
  'structuredPayload.generatedTab =',
  'structuredPayload.events =',
  'structuredPayload.renderEvents =',
  'structuredPayload.measureGrid =',
  'structuredPayload.analysisEngine =',
]) {
  assert.ok(
    !routeSource.includes(forbiddenMutation),
    `Shadow route must not mutate product payload: ${forbiddenMutation}`
  );
}

// S10 — explicit safety accounting.
for (const projection of [s1, s2, s3, s4, s5, s6, dropDDecode, s8]) {
  assert.equal(projection.shadowContract.shadowOnly, true);
  assert.equal(projection.shadowContract.referenceBlind, true);
  assert.equal(
    projection.shadowContract.referenceScoreAuthorized,
    false
  );
  assert.equal(projection.shadowContract.productionEligible, false);
}

const result = {
  schemaVersion: 1,
  gate: 'structure-conditioned-shadow-projection-v1-reference-blind-contract',
  tests: [
    'S1-auto-structure-unresolved',
    'S2-120bpm-4-4-straight',
    'S3-120bpm-6-8-denominator-aware',
    'S4-explicit-pickup-measure-zero',
    'S5-triplet-subdivision',
    'S6-auto-feel-no-subdivision-guess',
    'S7-drop-d-capo-conditioned-decode',
    'S8-impossible-pitch-fail-closed',
    'S9-source-product-immutability',
    'S10-safety-accounting',
  ],
  shadowOnly: true,
  referenceBlind: true,
  referenceScoreAuthorized: false,
  referenceScoreCalls: 0,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  modalInvoked: false,
  gpuUsed: false,
  productionModified: false,
  productionEligible: false,
  productionPromotionAuthorized: false,
  passed: true,
};

console.log(JSON.stringify(result, null, 2));
console.log('AI TAB CONDITIONED SHADOW PROJECTION V1 VERIFIED');
