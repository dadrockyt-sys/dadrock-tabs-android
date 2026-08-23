import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  BASS_MAX_FRET,
  BASS_STANDARD_OPEN_MIDI,
  BASS_STRING_LABELS,
  describeBassProfessionalRenderContract,
  projectBassProfessionalRenderEvents,
} from '../lib/bassProfessionalRenderContract.js';

assert.deepEqual(BASS_STRING_LABELS, ['G', 'D', 'A', 'E']);
assert.deepEqual(BASS_STANDARD_OPEN_MIDI, [43, 38, 33, 28]);
assert.equal(BASS_MAX_FRET, 24);

const valid = [
  { measure: 1, step: 0, stringIndex: 0, fret: 2, midi: 45, durationSteps: 2 },
  { measure: 1, step: 4, stringIndex: 1, fret: 3, midi: 41, durationSteps: 1 },
  { measure: 1, step: 8, stringIndex: 2, fret: 5, midi: 38, techniques: ['slide-up'] },
  { measure: 1, step: 12, stringIndex: 3, fret: 7, midi: 35, techniques: ['hammer-on'] },
];

const projected = projectBassProfessionalRenderEvents(valid);
assert.equal(projected.length, 4);
assert.deepEqual(projected.map((event) => event.stringLabel), ['G', 'D', 'A', 'E']);

const rejected = projectBassProfessionalRenderEvents([
  { measure: 1, step: 0, stringIndex: 4, fret: 3, midi: 60 },
  { measure: 1, step: 0, stringIndex: 0, fret: 25, midi: 68 },
  { measure: 1, step: 16, stringIndex: 0, fret: 2, midi: 45 },
  { measure: 0, step: 0, stringIndex: 0, fret: 2, midi: 45 },
  { measure: 1, step: 0, stringIndex: 0, fret: 2, midi: 46 },
]);
assert.equal(rejected.length, 0);

const description = describeBassProfessionalRenderContract();
assert.equal(description.instrument, 'bass');
assert.equal(description.tuning, 'Standard Bass');
assert.equal(description.stringCount, 4);
assert.equal(description.maximumFret, 24);
assert.equal(description.diagnosticOnly, true);
assert.equal(description.productionCandidate, false);
assert.equal(description.pdfRendererEnabled, false);
assert.equal(description.analyzerRoutingEnabled, false);
assert.equal(description.professionalStructuredIdentityEnabled, false);
assert.equal(description.productionPromotionAuthorized, false);

const evidence = {
  schemaVersion: 1,
  gate: 'bass-professional-render-contract-scaffold',
  instrument: 'bass',
  tuning: description.tuning,
  stringLabels: description.stringLabels,
  openMidi: description.openMidi,
  stringCount: description.stringCount,
  maximumFret: description.maximumFret,
  stepsPerMeasure: description.stepsPerMeasure,
  validFixtureEvents: valid.length,
  projectedFixtureEvents: projected.length,
  invalidFixtureEventsRejected: 5,
  pitchStringFretConsistencyRequired: true,
  diagnosticOnly: true,
  productionCandidate: false,
  pdfRendererEnabled: false,
  analyzerRoutingEnabled: false,
  professionalStructuredIdentityEnabled: false,
  realAudioBassCanaryPassed: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: true,
};

const resultPath = String(process.env.BASS_RENDER_CONTRACT_RESULT_PATH || '').trim();
if (resultPath) {
  const absolute = path.resolve(resultPath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('BASS PROFESSIONAL RENDER CONTRACT SCAFFOLD VERIFIED');
