export const AI_TAB_CONDITIONING_V1 = 1;

export const STANDARD_GUITAR_TUNING_MIDI = Object.freeze([
  40, 45, 50, 55, 59, 64,
]);

export const STANDARD_BASS_TUNING_MIDI = Object.freeze([
  28, 33, 38, 43,
]);

const ALLOWED_ROLES = new Set([
  'lead',
  'rhythm',
  'bass',
]);

const ALLOWED_FEELS = new Set([
  'auto',
  'straight',
  'triplet',
]);

const ALLOWED_TIME_SIGNATURE_DENOMINATORS = new Set([
  1,
  2,
  4,
  8,
  16,
  32,
]);

function isPlainRecord(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  );
}

function cloneTuning(values) {
  return values.map((value) => value);
}

export class AiTabConditioningValidationError extends Error {
  constructor(message, code = 'INVALID_AI_TAB_CONDITIONING') {
    super(message);
    this.name = 'AiTabConditioningValidationError';
    this.code = code;
  }
}

function reject(message, code) {
  throw new AiTabConditioningValidationError(message, code);
}

function normalizeNullableFiniteNumber(
  value,
  {
    field,
    minimum,
    maximum,
  }
) {
  if (value === undefined || value === null) {
    return null;
  }

  if (
    typeof value !== 'number' ||
    !Number.isFinite(value) ||
    value < minimum ||
    value > maximum
  ) {
    reject(
      `${field} must be null/Auto or a finite number from ${minimum} to ${maximum}.`,
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  return value;
}

function normalizeTimeSignature(value) {
  if (value === undefined || value === null) {
    return null;
  }

  if (!isPlainRecord(value)) {
    reject(
      'timeSignature must be null/Auto or an object with numerator and denominator.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  const numerator = value.numerator;
  const denominator = value.denominator;

  if (
    !Number.isInteger(numerator) ||
    numerator < 1 ||
    numerator > 32 ||
    !Number.isInteger(denominator) ||
    !ALLOWED_TIME_SIGNATURE_DENOMINATORS.has(denominator)
  ) {
    reject(
      'timeSignature must use numerator 1-32 and denominator 1, 2, 4, 8, 16, or 32.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  return {
    numerator,
    denominator,
  };
}

function normalizeStructurePrior(rawStructurePrior) {
  if (
    rawStructurePrior !== undefined &&
    rawStructurePrior !== null &&
    !isPlainRecord(rawStructurePrior)
  ) {
    reject(
      'structurePrior must be an object when provided.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  const source = rawStructurePrior || {};
  const rawFeel = source.feel;
  const feel =
    rawFeel === undefined || rawFeel === null
      ? 'auto'
      : rawFeel;

  if (
    typeof feel !== 'string' ||
    !ALLOWED_FEELS.has(feel)
  ) {
    reject(
      'feel must be auto, straight, or triplet.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  return {
    tempoBpm: normalizeNullableFiniteNumber(
      source.tempoBpm,
      {
        field: 'tempoBpm',
        minimum: 20,
        maximum: 400,
      }
    ),
    timeSignature: normalizeTimeSignature(
      source.timeSignature
    ),
    pickupBeats: normalizeNullableFiniteNumber(
      source.pickupBeats,
      {
        field: 'pickupBeats',
        minimum: 0,
        maximum: 32,
      }
    ),
    feel,
  };
}

function defaultTuningForRole(role) {
  return cloneTuning(
    role === 'bass'
      ? STANDARD_BASS_TUNING_MIDI
      : STANDARD_GUITAR_TUNING_MIDI
  );
}

function normalizeTuningMidi(rawTuningMidi, role) {
  if (rawTuningMidi === undefined || rawTuningMidi === null) {
    return defaultTuningForRole(role);
  }

  if (!Array.isArray(rawTuningMidi)) {
    reject(
      'tuningMidi must be an ordered array of MIDI open-string pitches.',
      'INVALID_INSTRUMENT_CONFIG'
    );
  }

  const minimumStrings = 4;
  const maximumStrings = role === 'bass' ? 6 : 8;

  if (
    rawTuningMidi.length < minimumStrings ||
    rawTuningMidi.length > maximumStrings
  ) {
    reject(
      `${role === 'bass' ? 'Bass' : 'Guitar'} tuning must contain ${minimumStrings}-${maximumStrings} strings.`,
      'INVALID_INSTRUMENT_CONFIG'
    );
  }

  const tuningMidi = rawTuningMidi.map((pitch) => {
    if (
      !Number.isInteger(pitch) ||
      pitch < 0 ||
      pitch > 127
    ) {
      reject(
        'Every tuningMidi pitch must be an integer from 0 to 127.',
        'INVALID_INSTRUMENT_CONFIG'
      );
    }

    return pitch;
  });

  for (let index = 1; index < tuningMidi.length; index += 1) {
    if (tuningMidi[index] <= tuningMidi[index - 1]) {
      reject(
        'tuningMidi must be strictly increasing from lowest to highest open string.',
        'INVALID_INSTRUMENT_CONFIG'
      );
    }
  }

  return tuningMidi;
}

function normalizeInstrumentConfig(
  rawInstrumentConfig,
  transcriptionType
) {
  if (
    rawInstrumentConfig !== undefined &&
    rawInstrumentConfig !== null &&
    !isPlainRecord(rawInstrumentConfig)
  ) {
    reject(
      'instrumentConfig must be an object when provided.',
      'INVALID_INSTRUMENT_CONFIG'
    );
  }

  const source = rawInstrumentConfig || {};
  const role =
    source.role === undefined || source.role === null
      ? transcriptionType
      : source.role;

  if (
    typeof role !== 'string' ||
    !ALLOWED_ROLES.has(role)
  ) {
    reject(
      'instrumentConfig.role must be lead, rhythm, or bass.',
      'INVALID_INSTRUMENT_CONFIG'
    );
  }

  if (role !== transcriptionType) {
    reject(
      'instrumentConfig.role must match transcriptionType.',
      'INSTRUMENT_ROLE_MISMATCH'
    );
  }

  const capoFret =
    source.capoFret === undefined || source.capoFret === null
      ? 0
      : source.capoFret;

  if (
    !Number.isInteger(capoFret) ||
    capoFret < 0 ||
    capoFret > 24
  ) {
    reject(
      'capoFret must be an integer from 0 to 24.',
      'INVALID_INSTRUMENT_CONFIG'
    );
  }

  return {
    role,
    tuningMidi: normalizeTuningMidi(
      source.tuningMidi,
      role
    ),
    capoFret,
  };
}

export function normalizeAiTabConditioningV1(
  rawConditioning,
  transcriptionType
) {
  if (!ALLOWED_ROLES.has(transcriptionType)) {
    reject(
      'transcriptionType must be lead, rhythm, or bass.',
      'INVALID_TRANSCRIPTION_TYPE'
    );
  }

  if (
    rawConditioning !== undefined &&
    rawConditioning !== null &&
    !isPlainRecord(rawConditioning)
  ) {
    reject(
      'conditioning must be an object when provided.'
    );
  }

  const source = rawConditioning || {};
  const version =
    source.version === undefined || source.version === null
      ? AI_TAB_CONDITIONING_V1
      : source.version;

  if (version !== AI_TAB_CONDITIONING_V1) {
    reject(
      `conditioning.version must be ${AI_TAB_CONDITIONING_V1}.`,
      'UNSUPPORTED_AI_TAB_CONDITIONING_VERSION'
    );
  }

  return {
    version: AI_TAB_CONDITIONING_V1,
    structurePrior: normalizeStructurePrior(
      source.structurePrior
    ),
    instrumentConfig: normalizeInstrumentConfig(
      source.instrumentConfig,
      transcriptionType
    ),
  };
}

export function buildAiTabConditioningContractV1({
  conditioning,
  usingV143RhythmAnalyzer,
}) {
  const normalized = normalizeAiTabConditioningV1(
    conditioning,
    conditioning?.instrumentConfig?.role
  );

  return {
    name: 'structure-instrument-conditioning',
    version: AI_TAB_CONDITIONING_V1,
    referenceBlind: true,
    referenceScoreAuthorized: false,
    structurePrior: normalized.structurePrior,
    instrumentConfig: normalized.instrumentConfig,
    provenance: {
      mixtureSource: {
        kind: 'full-mixture',
        source: 'request-audio',
        preservedForStructureContext: true,
      },
      instrumentCarrierSource: usingV143RhythmAnalyzer
        ? {
            kind: 'selected-analyzer-carrier',
            source: 'v143-rhythm-analyzer',
            relationToMixture: 'analyzer-managed',
          }
        : {
            kind: 'same-as-mixture',
            source: 'request-audio',
            relationToMixture: 'identical-request-source',
          },
    },
  };
}
