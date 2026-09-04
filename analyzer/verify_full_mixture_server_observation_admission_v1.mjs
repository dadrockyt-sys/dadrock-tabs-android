import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

import { normalizeAiTabConditioningV1 } from '../lib/aiTabConditioningV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '../lib/aiTabMixtureStructureContextV1.mjs';
import {
  admitAiTabAnalyzerMixtureObservationV1,
  buildAiTabMixtureStructureContextFromAnalyzerObservationV1,
} from '../lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';

const mixtureSource = {
  kind: 'full-mixture',
  source: 'request-audio',
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

function baseline(prior = structurePrior()) {
  return buildAiTabMixtureStructureContextV1({
    structurePrior: prior,
    mixtureObservation: null,
    mixtureSource,
  });
}

function candidate(prior, analyzerObservation) {
  const baselineContext = baseline(prior);
  return {
    baselineContext,
    result: buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
      baselineContext,
      analyzerObservation,
      structurePrior: prior,
      mixtureSource,
    }),
  };
}

const route = await readFile('app/api/analyze-audio-tab/route.js', 'utf8');
const helper = await readFile('lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs', 'utf8');
const preview = await readFile('app/api/generate-tab-preview/route.js', 'utf8');
const full = await readFile('app/api/generate-tab-pdf/route.js', 'utf8');

const tests = {};

// T1 — exact null-observation baseline is built before analyzer observation trust.
const baselineIndex = route.indexOf('const baselineMixtureStructureContext =');
const nullObservationIndex = route.indexOf('mixtureObservation: null,', baselineIndex);
const analyzerObservationIndex = route.indexOf('analyzerObservation: analyzerData?.mixtureObservation');
assert.ok(baselineIndex >= 0 && nullObservationIndex > baselineIndex);
assert.ok(analyzerObservationIndex > nullObservationIndex);
tests.T1 = 'PASS';

// T2 — trusted Phase-7-shaped observation fills unresolved Auto research fields.
const t2Prior = structurePrior();
const t2Observation = trustedObservation({
  tempoBpm: field(120, 0.91, 'waveform-onset-periodicity-v1'),
  timeSignature: field({ numerator: 4, denominator: 4 }, 0.82, 'waveform-accent-meter-v1'),
  pickupBeats: field(0, 0.77, 'waveform-downbeat-phase-v1'),
  feel: field('straight', 0.69, 'waveform-subdivision-evidence-v1'),
});
assert.strictEqual(admitAiTabAnalyzerMixtureObservationV1(t2Observation), t2Observation);
const t2 = candidate(t2Prior, t2Observation).result;
assert.equal(t2.observationStatus, 'TRUSTED_FULL_MIXTURE_OBSERVATION');
assert.deepEqual(t2.resolved, {
  tempoBpm: 120,
  timeSignature: { numerator: 4, denominator: 4 },
  pickupBeats: 0,
  feel: 'straight',
});
for (const source of Object.values(t2.fieldSources)) {
  assert.equal(source.source, 'full-mixture-observation');
}
tests.T2 = 'PASS';

// T3 — explicit user priors retain field-by-field authority.
const t3Prior = structurePrior({
  tempoBpm: 96,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 1,
  feel: 'triplet',
});
const t3 = candidate(t3Prior, t2Observation).result;
assert.deepEqual(t3.resolved, {
  tempoBpm: 96,
  timeSignature: { numerator: 3, denominator: 4 },
  pickupBeats: 1,
  feel: 'triplet',
});
for (const source of Object.values(t3.fieldSources)) {
  assert.equal(source.source, 'user-prior');
}
tests.T3 = 'PASS';

// T4 — absent/null analyzer observation returns the exact baseline object.
for (const value of [undefined, null]) {
  const { baselineContext, result } = candidate(t2Prior, value);
  assert.strictEqual(result, baselineContext);
}
tests.T4 = 'PASS';

// T5 — malformed observations return the exact baseline object.
for (const value of [[], 'bad', 7, {}, { version: 1 }]) {
  const { baselineContext, result } = candidate(t2Prior, value);
  assert.strictEqual(result, baselineContext);
}
tests.T5 = 'PASS';

// T6 — bad source/reference/carrier/event provenance fails open to baseline.
const badObservations = [
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
for (const value of badObservations) {
  const { baselineContext, result } = candidate(t2Prior, value);
  assert.strictEqual(result, baselineContext);
}
tests.T6 = 'PASS';

// T7 — provenance-valid but invalid musical fields fail open rather than throwing.
const invalidFields = [
  trustedObservation({ tempoBpm: field(401) }),
  trustedObservation({ tempoBpm: field(120, 1.5) }),
  trustedObservation({ tempoBpm: field(120, 0.8, '   ') }),
  trustedObservation({ timeSignature: field({ numerator: 4, denominator: 3 }) }),
  trustedObservation({ pickupBeats: field(-1) }),
  trustedObservation({ feel: field('auto') }),
];
for (const value of invalidFields) {
  const { baselineContext, result } = candidate(t2Prior, value);
  assert.strictEqual(result, baselineContext);
}
tests.T7 = 'PASS';

// T8 — structured Product payload is built before research observation trust.
const structuredPayloadIndex = route.indexOf('const structuredPayload =');
assert.ok(structuredPayloadIndex >= 0 && structuredPayloadIndex < baselineIndex);
const structuredPayloadBlock = route.slice(
  structuredPayloadIndex,
  route.indexOf('const conditioningContract =', structuredPayloadIndex)
);
assert.equal(structuredPayloadBlock.includes('mixtureObservation'), false);
assert.equal(structuredPayloadBlock.includes('mixtureStructureContext'), false);
tests.T8 = 'PASS';

// T9 — analyzer selection/status/V143 safety complete before observation trust.
const analyzerUrlIndex = route.indexOf('const analyzerUrl =');
const responseOkIndex = route.indexOf('if (!analyzerResponse.ok)');
const v143SafetyIndex = route.indexOf('const v143RuntimeSafetyVerified =');
assert.ok(analyzerUrlIndex >= 0 && analyzerUrlIndex < responseOkIndex);
assert.ok(responseOkIndex < v143SafetyIndex && v143SafetyIndex < structuredPayloadIndex);
assert.ok(analyzerObservationIndex > structuredPayloadIndex);
const preObservationRoute = route.slice(0, analyzerObservationIndex);
assert.equal(preObservationRoute.includes('mixtureObservation: analyzerData'), false);
tests.T9 = 'PASS';

// T10 — Product/PDF paths remain isolated from research mixture context.
assert.equal(preview.includes('mixtureStructureContext'), false);
assert.equal(preview.includes('mixtureObservation'), false);
assert.equal(full.includes('mixtureStructureContext'), false);
assert.equal(full.includes('mixtureObservation'), false);
tests.T10 = 'PASS';

// T11 — static/local verification only; no deployment/invocation/reference path.
assert.equal(route.includes('.remote('), false);
assert.equal(route.includes('modal.run'), false);
tests.T11 = 'PASS';

// T12 — rollback is the explicit baseline; helper returns it on every rejected candidate.
assert.ok(helper.includes('return baselineContext;'));
assert.ok(route.includes('baselineContext: baselineMixtureStructureContext,'));
assert.ok(route.includes('mixtureObservation: null,'));
assert.equal(route.match(/analyzerObservation: analyzerData\?\.mixtureObservation/g)?.length, 1);
tests.T12 = 'PASS';

const evidence = {
  schemaVersion: 1,
  gate: 'full-mixture-server-observation-admission-wiring-v1',
  referenceBlind: true,
  serverResearchContextTrustConnected: true,
  productAuthorityChanged: false,
  pdfAuthorityChanged: false,
  externalAudioAssetsUsed: false,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  referenceScoreCalls: 0,
  modalInvoked: false,
  gpuUsed: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  tests,
  passed: Object.keys(tests).length === 12 && new Set(Object.values(tests)).size === 1 && tests.T1 === 'PASS',
};

const resultPath = String(
  process.env.FULL_MIXTURE_SERVER_ADMISSION_V1_RESULT_PATH || ''
).trim();
if (resultPath) {
  const { mkdir, writeFile } = await import('node:fs/promises');
  const { dirname } = await import('node:path');
  await mkdir(dirname(resultPath), { recursive: true });
  await writeFile(resultPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(evidence, null, 2));
console.log('FULL MIXTURE SERVER OBSERVATION ADMISSION V1 T1-T12 VERIFIED');
