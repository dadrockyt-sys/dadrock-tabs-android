#!/usr/bin/env node

import assert from 'node:assert/strict';
import { projectV143RenderEvents } from '../../lib/v143RenderContract.js';

const rawEvents = [
  {
    eventIndex: 0,
    measure: 7,
    step: 3,
    stringIndex: 2,
    fret: 2,
    midi: 57,
    timeSeconds: 10.0,
    start: 10.0,
    onsetTime: 10.083,
    end: 10.42,
    offsetTime: 10.42,
    duration: 0.42,
    physicalOnsetDeltaFromGridSeconds: 0.083,
    rhythmSustain: {
      durationSteps: 3,
      durationSeconds: 0.42,
      tier: 'medium',
      attackTimingChanged: false,
      physicalOnsetPreserved: true,
      analysisTimingBasis: 'quantized-timeSeconds',
      presentationStartBasis: 'quantized-timeSeconds',
      offsetTimingBasis: 'quantized-timeSeconds-plus-durationSeconds',
    },
    rhythmTechniques: [{ type: 'palm-mute' }],
  },
  {
    eventIndex: 1,
    measure: 7,
    step: 8,
    stringIndex: 0,
    fret: 0,
    midi: 64,
    timeSeconds: 10.5,
    start: 10.5,
    onsetTime: 10.472,
    end: 10.71,
    offsetTime: 10.71,
    duration: 0.21,
    physicalOnsetDeltaFromGridSeconds: -0.028,
    rhythmSustain: {
      durationSteps: 2,
      durationSeconds: 0.21,
      tier: 'short',
      attackTimingChanged: false,
      physicalOnsetPreserved: true,
      analysisTimingBasis: 'quantized-timeSeconds',
      presentationStartBasis: 'quantized-timeSeconds',
      offsetTimingBasis: 'quantized-timeSeconds-plus-durationSeconds',
    },
    rhythmTechniques: [{ type: 'hammer-on' }],
  },
];

const roundTrip = JSON.parse(JSON.stringify(rawEvents));
assert.equal(roundTrip[0].onsetTime, 10.083);
assert.equal(roundTrip[1].onsetTime, 10.472);
assert.equal(roundTrip[0].physicalOnsetDeltaFromGridSeconds, 0.083);
assert.equal(roundTrip[1].physicalOnsetDeltaFromGridSeconds, -0.028);

const projection = projectV143RenderEvents(roundTrip);
assert.equal(projection.length, rawEvents.length);

const physicalOnlyMutation = structuredClone(roundTrip);
physicalOnlyMutation[0].onsetTime = 10.211;
physicalOnlyMutation[0].physicalOnsetDeltaFromGridSeconds = 0.211;
physicalOnlyMutation[1].onsetTime = 10.401;
physicalOnlyMutation[1].physicalOnsetDeltaFromGridSeconds = -0.099;

const mutatedProjection = projectV143RenderEvents(physicalOnlyMutation);
assert.deepEqual(mutatedProjection, projection);

const forbiddenTimingKeys = [
  'timeSeconds',
  'start',
  'onsetTime',
  'end',
  'offsetTime',
  'duration',
  'physicalOnsetDeltaFromGridSeconds',
];
for (const event of projection) {
  for (const key of forbiddenTimingKeys) {
    assert.equal(Object.hasOwn(event, key), false, `render projection unexpectedly contains ${key}`);
  }
}

assert.deepEqual(
  projection.map(({ eventIndex, measure, step, stringIndex, fret, midi, durationSteps }) => ({
    eventIndex,
    measure,
    step,
    stringIndex,
    fret,
    midi,
    durationSteps,
  })),
  [
    { eventIndex: 0, measure: 7, step: 3, stringIndex: 2, fret: 2, midi: 57, durationSteps: 3 },
    { eventIndex: 1, measure: 7, step: 8, stringIndex: 0, fret: 0, midi: 64, durationSteps: 2 },
  ]
);

console.log(JSON.stringify({
  schemaVersion: 1,
  gate: 'v143-precision-dual-timing-render-projection',
  rawPhysicalOnsetRoundTripPreserved: true,
  renderProjectionIndependentOfPhysicalOnset: true,
  renderProjectionUsesAuthenticatedGridIdentity: true,
  physicalTimingNotSerializedIntoRenderEvents: true,
  professionalReferenceUsed: false,
  runtimeLabelsRequired: false,
  productionModified: false,
  modalGpuUsed: false,
  passed: true,
}, null, 2));
