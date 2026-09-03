import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  AiTabConditioningValidationError,
  STANDARD_BASS_TUNING_MIDI,
  STANDARD_GUITAR_TUNING_MIDI,
  buildAiTabConditioningContractV1,
  normalizeAiTabConditioningV1,
} from '../lib/aiTabConditioningV1.mjs';

function expectValidationError(
  label,
  callback,
  expectedCode
) {
  assert.throws(
    callback,
    (error) => {
      assert.ok(
        error instanceof AiTabConditioningValidationError,
        `${label} must fail with AiTabConditioningValidationError`
      );
      assert.equal(
        error.code,
        expectedCode,
        `${label} must fail with ${expectedCode}`
      );
      return true;
    }
  );
}

// T1 — default lead.
const defaultLead = normalizeAiTabConditioningV1(
  undefined,
  'lead'
);
assert.deepEqual(defaultLead, {
  version: 1,
  structurePrior: {
    tempoBpm: null,
    timeSignature: null,
    pickupBeats: null,
    feel: 'auto',
  },
  instrumentConfig: {
    role: 'lead',
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 0,
  },
});

// T2 — default bass.
const defaultBass = normalizeAiTabConditioningV1(
  undefined,
  'bass'
);
assert.deepEqual(defaultBass.instrumentConfig, {
  role: 'bass',
  tuningMidi: [...STANDARD_BASS_TUNING_MIDI],
  capoFret: 0,
});

// T3 — explicit structure survives normalization exactly.
const explicitStructure = normalizeAiTabConditioningV1(
  {
    version: 1,
    structurePrior: {
      tempoBpm: 96,
      timeSignature: {
        numerator: 6,
        denominator: 8,
      },
      pickupBeats: 1.5,
      feel: 'triplet',
    },
  },
  'rhythm'
);
assert.deepEqual(explicitStructure.structurePrior, {
  tempoBpm: 96,
  timeSignature: {
    numerator: 6,
    denominator: 8,
  },
  pickupBeats: 1.5,
  feel: 'triplet',
});

// T4 — alternate physical tuning and capo remain separate.
const dropDWithCapo = normalizeAiTabConditioningV1(
  {
    version: 1,
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [38, 45, 50, 55, 59, 64],
      capoFret: 2,
    },
  },
  'lead'
);
assert.deepEqual(
  dropDWithCapo.instrumentConfig,
  {
    role: 'lead',
    tuningMidi: [38, 45, 50, 55, 59, 64],
    capoFret: 2,
  }
);

// T5 — role mismatch fails closed.
expectValidationError(
  'role mismatch',
  () => normalizeAiTabConditioningV1(
    {
      instrumentConfig: {
        role: 'lead',
      },
    },
    'rhythm'
  ),
  'INSTRUMENT_ROLE_MISMATCH'
);

// T6 — invalid tuning fails closed.
for (const [label, tuningMidi] of [
  ['unordered tuning', [40, 45, 44, 55, 59, 64]],
  ['non-integer tuning', [40, 45, 50.5, 55, 59, 64]],
  ['out-of-range tuning', [40, 45, 50, 55, 59, 128]],
]) {
  expectValidationError(
    label,
    () => normalizeAiTabConditioningV1(
      {
        instrumentConfig: {
          role: 'lead',
          tuningMidi,
        },
      },
      'lead'
    ),
    'INVALID_INSTRUMENT_CONFIG'
  );
}

// T7 — invalid structure fails closed.
for (const [label, structurePrior] of [
  ['tempo below range', { tempoBpm: 19 }],
  ['unsupported denominator', {
    timeSignature: {
      numerator: 4,
      denominator: 3,
    },
  }],
  ['pickup above range', { pickupBeats: 33 }],
  ['invalid feel', { feel: 'swingish' }],
]) {
  expectValidationError(
    label,
    () => normalizeAiTabConditioningV1(
      { structurePrior },
      'lead'
    ),
    'INVALID_STRUCTURE_PRIOR'
  );
}

// T8 — route forwards the normalized object without changing analyzer routing.
const routeSource = await readFile(
  'app/api/analyze-audio-tab/route.js',
  'utf8'
);
for (const requiredSource of [
  'normalizeAiTabConditioningV1(',
  'body?.conditioning,',
  'conditioning,\n        })',
  "transcriptionType === 'rhythm'",
  'process.env.ANALYZER_API_URL',
  'process.env.ANALYZER_API_URL_V143',
]) {
  assert.ok(
    routeSource.includes(requiredSource),
    `Analyzer route must preserve ${requiredSource}`
  );
}

// T9 — response contract is server-owned, reference-blind, and dual-context.
const legacyContract = buildAiTabConditioningContractV1({
  conditioning: defaultLead,
  usingV143RhythmAnalyzer: false,
});
assert.equal(
  legacyContract.name,
  'structure-instrument-conditioning'
);
assert.equal(legacyContract.version, 1);
assert.equal(legacyContract.referenceBlind, true);
assert.equal(
  legacyContract.referenceScoreAuthorized,
  false
);
assert.deepEqual(
  legacyContract.instrumentConfig,
  defaultLead.instrumentConfig
);
assert.equal(
  legacyContract.provenance.mixtureSource.kind,
  'full-mixture'
);
assert.equal(
  legacyContract.provenance.mixtureSource.preservedForStructureContext,
  true
);
assert.equal(
  legacyContract.provenance.instrumentCarrierSource.kind,
  'same-as-mixture'
);

const v143Contract = buildAiTabConditioningContractV1({
  conditioning: explicitStructure,
  usingV143RhythmAnalyzer: true,
});
assert.equal(
  v143Contract.provenance.instrumentCarrierSource.kind,
  'selected-analyzer-carrier'
);
assert.equal(
  v143Contract.provenance.instrumentCarrierSource.relationToMixture,
  'analyzer-managed'
);

for (const serverAuthorityMarker of [
  'const conditioningContract =',
  'buildAiTabConditioningContractV1({',
  'conditioningContract,',
  'The analyzer is therefore never authoritative',
]) {
  assert.ok(
    routeSource.includes(serverAuthorityMarker),
    `Server authority marker missing: ${serverAuthorityMarker}`
  );
}

// T10 — legacy/V143 scientific safety markers remain present.
for (const safetyMarker of [
  "transcriptionType === 'rhythm'",
  'liveV143?.referenceFree === true',
  'liveV143?.professionalReferenceUsed === false',
  'liveV143?.referenceRuntimeInputUsed === false',
  'liveV143?.runtimeLabelsRequired === false',
  'usingV143RhythmAnalyzer &&',
  '!v143RuntimeSafetyVerified',
]) {
  assert.ok(
    routeSource.includes(safetyMarker),
    `V143 safety marker missing: ${safetyMarker}`
  );
}

const result = {
  schemaVersion: 1,
  gate: 'structure-instrument-conditioning-v1-reference-blind-contract',
  tests: [
    'T1-default-lead',
    'T2-default-bass',
    'T3-explicit-structure',
    'T4-alternate-tuning-capo',
    'T5-role-mismatch-fail-closed',
    'T6-invalid-tuning-fail-closed',
    'T7-invalid-structure-fail-closed',
    'T8-analyzer-forwarding-routing-preserved',
    'T9-server-owned-dual-context-provenance',
    'T10-legacy-v143-safety-preserved',
  ],
  referenceBlind: true,
  referenceScoreAuthorized: false,
  referenceScoreCalls: 0,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  gpuUsed: false,
  modalInvoked: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  passed: true,
};

console.log(JSON.stringify(result, null, 2));
console.log('AI TAB CONDITIONING V1 CONTRACT VERIFIED');
