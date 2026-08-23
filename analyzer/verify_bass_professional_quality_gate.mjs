import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  buildBassProfessionalQualityReport,
} from '../lib/bassProfessionalQuality.js';

function goodEvents() {
  return [
    { measure: 1, step: 0, stringIndex: 3, fret: 0, midi: 28 },
    { measure: 1, step: 4, stringIndex: 3, fret: 3, midi: 31 },
    { measure: 1, step: 8, stringIndex: 2, fret: 2, midi: 35 },
    { measure: 1, step: 12, stringIndex: 2, fret: 5, midi: 38 },
    { measure: 2, step: 0, stringIndex: 1, fret: 2, midi: 40 },
    { measure: 2, step: 4, stringIndex: 1, fret: 5, midi: 43 },
    { measure: 2, step: 8, stringIndex: 0, fret: 2, midi: 45 },
    { measure: 2, step: 12, stringIndex: 0, fret: 5, midi: 48 },
  ];
}

const passing = buildBassProfessionalQualityReport(goodEvents());
assert.equal(passing.passed, true);
assert.equal(passing.validRenderEventCount, 8);
assert.equal(passing.renderEventSurvivalPercent, 100);
assert.equal(passing.playableStringFretPercent, 100);
assert.equal(passing.timingCoveragePercent, 100);
assert.equal(passing.pitchValidityPercent, 100);
assert.equal(passing.pitchStringFretConsistencyPercent, 100);

const weak = buildBassProfessionalQualityReport([
  ...goodEvents().slice(0, 3),
  { measure: 0, step: 0, stringIndex: 3, fret: 0, midi: 28 },
  { measure: 2, step: 16, stringIndex: 2, fret: 5, midi: 38 },
  { measure: 2, step: 8, stringIndex: 4, fret: 2, midi: 45 },
  { measure: 2, step: 12, stringIndex: 0, fret: 25, midi: 68 },
  { measure: 3, step: 0, stringIndex: 0, fret: 2, midi: 46 },
]);
assert.equal(weak.passed, false);
assert.ok(weak.validRenderEventCount < 4);
assert.ok(weak.renderEventSurvivalPercent < 70);
assert.ok(weak.pitchStringFretConsistencyPercent < 70);

const legacyUntimed = buildBassProfessionalQualityReport([
  { start: 0.0, end: 0.3, stringIndex: 3, fret: 0, midi: 28 },
  { start: 0.3, end: 0.6, stringIndex: 3, fret: 3, midi: 31 },
  { start: 0.6, end: 0.9, stringIndex: 2, fret: 2, midi: 35 },
  { start: 0.9, end: 1.2, stringIndex: 2, fret: 5, midi: 38 },
]);
assert.equal(legacyUntimed.passed, false);
assert.equal(legacyUntimed.timingCoveragePercent, 0);
assert.equal(legacyUntimed.validRenderEventCount, 0);

assert.equal(passing.diagnosticOnly, true);
assert.equal(passing.productionCandidate, false);
assert.equal(passing.analyzerRoutingEnabled, false);
assert.equal(passing.pdfRendererEnabled, false);
assert.equal(passing.professionalStructuredIdentityEnabled, false);
assert.equal(passing.productionPromotionAuthorized, false);

const evidence = {
  schemaVersion: 1,
  gate: 'bass-professional-quality-scaffold',
  thresholds: DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  passingFixture: passing,
  weakFixturePassed: weak.passed,
  legacyUntimedPassed: legacyUntimed.passed,
  legacyUntimedTimingCoveragePercent: legacyUntimed.timingCoveragePercent,
  diagnosticOnly: true,
  productionCandidate: false,
  analyzerRoutingEnabled: false,
  pdfRendererEnabled: false,
  professionalStructuredIdentityEnabled: false,
  realAudioBassCanaryPassed: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: true,
};

const resultPath = String(process.env.BASS_QUALITY_RESULT_PATH || '').trim();
if (resultPath) {
  const absolute = path.resolve(resultPath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('BASS PROFESSIONAL QUALITY SCAFFOLD VERIFIED');
