#!/usr/bin/env node

import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

import {
  projectV143RenderEvents,
  validateV143RenderEvents,
} from '../../lib/v143RenderContract.js';

const outputPath = process.argv[2] || null;

// Deliberately include rejected raw events so the authenticated projected event
// IDs contain gaps. Legato links refer to those original raw indices. Any later
// compaction/re-numbering would silently corrupt the professional PDF notation.
const rawEvents = [
  {
    measure: 1,
    step: 0,
    stringIndex: 5,
    fret: 0,
    midi: 40,
    rhythmSustain: { durationSteps: 2, tier: 'medium' },
  },
  {
    measure: 1,
    step: 2,
    stringIndex: 9,
    fret: 0,
    midi: 40,
  },
  {
    measure: 1,
    step: 4,
    stringIndex: 4,
    fret: 2,
    midi: 47,
    rhythmSustain: { durationSteps: 2, tier: 'medium' },
    rhythmTechniques: [{ type: 'hammer-on' }],
    legatoTargetEventIndex: 4,
    legatoTargetFret: 4,
    legatoTargetMidi: 49,
  },
  {
    measure: 0,
    step: 6,
    stringIndex: 4,
    fret: 3,
    midi: 48,
  },
  {
    measure: 1,
    step: 8,
    stringIndex: 4,
    fret: 4,
    midi: 49,
    rhythmSustain: { durationSteps: 3, tier: 'long' },
    legatoContinuationFromEventIndex: 2,
    legatoContinuationType: 'hammer-on',
  },
];

const once = projectV143RenderEvents(rawEvents);
assert.deepEqual(
  once.map((event) => event.eventIndex),
  [0, 2, 4],
  'first projection must preserve raw-array identity across rejected events'
);
assert.equal(
  once[1].legatoTargetEventIndex,
  4,
  'source legato target must retain authenticated raw event identity'
);
assert.equal(
  once[2].legatoContinuationFromEventIndex,
  2,
  'target continuation source must retain authenticated raw event identity'
);

const twice = projectV143RenderEvents(once);
assert.deepEqual(
  twice,
  once,
  'projectV143RenderEvents must be idempotent for authenticated render events'
);

const validated = validateV143RenderEvents(once);
assert.deepEqual(
  validated,
  once,
  'validateV143RenderEvents must preserve the exact authenticated event stream'
);

const report = {
  schemaVersion: 1,
  gate: 'v143-render-contract-idempotence',
  rawEventCount: rawEvents.length,
  authenticatedEventCount: once.length,
  authenticatedEventIndices: once.map((event) => event.eventIndex),
  gappedEventIdentityTested: true,
  legatoTargetIdentityPreserved: once[1].legatoTargetEventIndex === 4,
  legatoContinuationIdentityPreserved:
    once[2].legatoContinuationFromEventIndex === 2,
  secondProjectionExactlyEqual: JSON.stringify(twice) === JSON.stringify(once),
  validationExactlyEqual: JSON.stringify(validated) === JSON.stringify(once),
  passed: true,
  productionModified: false,
  productionPromotionAuthorized: false,
};

if (outputPath) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(report, null, 2));
