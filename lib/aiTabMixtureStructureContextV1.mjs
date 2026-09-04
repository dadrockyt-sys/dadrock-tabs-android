export const AI_TAB_MIXTURE_STRUCTURE_CONTEXT_V1 = 1;

const ALLOWED_DENOMINATORS = new Set([
  1,
  2,
  4,
  8,
  16,
  32,
]);

const ALLOWED_OBSERVED_FEELS = new Set([
  'straight',
  'triplet',
]);

function isPlainRecord(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  );
}

function cleanMethod(value) {
  if (typeof value !== 'string') return null;
  const cleaned = value.replace(/\s+/g, ' ').trim();
  if (!cleaned || cleaned.length > 120) return null;
  return cleaned;
}

export class AiTabMixtureStructureContextValidationError extends Error {
  constructor(
    message,
    code = 'INVALID_MIXTURE_STRUCTURE_CONTEXT'
  ) {
    super(message);
    this.name = 'AiTabMixtureStructureContextValidationError';
    this.code = code;
  }
}

function reject(message, code) {
  throw new AiTabMixtureStructureContextValidationError(
    message,
    code
  );
}

function validateMixtureSource(mixtureSource) {
  if (
    !isPlainRecord(mixtureSource) ||
    mixtureSource.kind !== 'full-mixture' ||
    mixtureSource.source !== 'request-audio'
  ) {
    reject(
      'mixtureSource must be the server-owned full-mixture request-audio provenance.',
      'INVALID_MIXTURE_SOURCE'
    );
  }

  return {
    kind: 'full-mixture',
    source: 'request-audio',
  };
}

function validateObservationProvenance(observation) {
  if (!isPlainRecord(observation)) {
    reject(
      'mixtureObservation must be an object or null.',
      'INVALID_MIXTURE_OBSERVATION'
    );
  }

  if (observation.version !== AI_TAB_MIXTURE_STRUCTURE_CONTEXT_V1) {
    reject(
      `mixtureObservation.version must be ${AI_TAB_MIXTURE_STRUCTURE_CONTEXT_V1}.`,
      'UNSUPPORTED_MIXTURE_OBSERVATION_VERSION'
    );
  }

  const provenance = observation.provenance;

  if (!isPlainRecord(provenance)) {
    reject(
      'mixtureObservation.provenance is required.',
      'INVALID_MIXTURE_OBSERVATION_PROVENANCE'
    );
  }

  if (
    provenance.sourceKind !== 'full-mixture' ||
    provenance.sourceIdentity !== 'request-audio'
  ) {
    reject(
      'Only an exact full-mixture request-audio observation may supply global structure context.',
      'CARRIER_STRUCTURE_BORROWING_FORBIDDEN'
    );
  }

  if (
    provenance.referenceBlind !== true ||
    provenance.referenceRuntimeInputUsed !== false
  ) {
    reject(
      'Mixture structure observations must be reference-blind and must not use reference runtime input.',
      'REFERENCE_PROVENANCE_FORBIDDEN'
    );
  }
}

function normalizeObservationField(
  rawField,
  {
    fieldName,
    normalizeValue,
  }
) {
  if (rawField === undefined || rawField === null) {
    return null;
  }

  if (!isPlainRecord(rawField)) {
    reject(
      `${fieldName} observation must be an object or null.`,
      'INVALID_MIXTURE_OBSERVATION_FIELD'
    );
  }

  const confidence = rawField.confidence;
  if (
    typeof confidence !== 'number' ||
    !Number.isFinite(confidence) ||
    confidence < 0 ||
    confidence > 1
  ) {
    reject(
      `${fieldName} observation confidence must be a finite number from 0 to 1.`,
      'INVALID_MIXTURE_OBSERVATION_CONFIDENCE'
    );
  }

  const method = cleanMethod(rawField.method);
  if (!method) {
    reject(
      `${fieldName} observation method must be a non-empty string no longer than 120 characters.`,
      'INVALID_MIXTURE_OBSERVATION_METHOD'
    );
  }

  return {
    value: normalizeValue(rawField.value),
    confidence,
    method,
  };
}

function normalizeObservedTempo(value) {
  if (
    typeof value !== 'number' ||
    !Number.isFinite(value) ||
    value < 20 ||
    value > 400
  ) {
    reject(
      'Observed tempo must be a finite BPM value from 20 to 400.',
      'INVALID_MIXTURE_OBSERVATION_VALUE'
    );
  }

  return value;
}

function normalizeObservedTimeSignature(value) {
  if (!isPlainRecord(value)) {
    reject(
      'Observed time signature must contain numerator and denominator.',
      'INVALID_MIXTURE_OBSERVATION_VALUE'
    );
  }

  if (
    !Number.isInteger(value.numerator) ||
    value.numerator < 1 ||
    value.numerator > 32 ||
    !Number.isInteger(value.denominator) ||
    !ALLOWED_DENOMINATORS.has(value.denominator)
  ) {
    reject(
      'Observed time signature must use numerator 1-32 and denominator 1, 2, 4, 8, 16, or 32.',
      'INVALID_MIXTURE_OBSERVATION_VALUE'
    );
  }

  return {
    numerator: value.numerator,
    denominator: value.denominator,
  };
}

function normalizeObservedPickup(value) {
  if (
    typeof value !== 'number' ||
    !Number.isFinite(value) ||
    value < 0 ||
    value > 32
  ) {
    reject(
      'Observed pickupBeats must be a finite value from 0 to 32.',
      'INVALID_MIXTURE_OBSERVATION_VALUE'
    );
  }

  return value;
}

function normalizeObservedFeel(value) {
  if (
    typeof value !== 'string' ||
    !ALLOWED_OBSERVED_FEELS.has(value)
  ) {
    reject(
      'Observed feel must be straight or triplet.',
      'INVALID_MIXTURE_OBSERVATION_VALUE'
    );
  }

  return value;
}

function normalizeMixtureObservation(observation) {
  if (observation === undefined || observation === null) {
    return null;
  }

  validateObservationProvenance(observation);

  return {
    tempoBpm: normalizeObservationField(
      observation.tempoBpm,
      {
        fieldName: 'tempoBpm',
        normalizeValue: normalizeObservedTempo,
      }
    ),
    timeSignature: normalizeObservationField(
      observation.timeSignature,
      {
        fieldName: 'timeSignature',
        normalizeValue: normalizeObservedTimeSignature,
      }
    ),
    pickupBeats: normalizeObservationField(
      observation.pickupBeats,
      {
        fieldName: 'pickupBeats',
        normalizeValue: normalizeObservedPickup,
      }
    ),
    feel: normalizeObservationField(
      observation.feel,
      {
        fieldName: 'feel',
        normalizeValue: normalizeObservedFeel,
      }
    ),
  };
}

function validateStructurePrior(structurePrior) {
  if (!isPlainRecord(structurePrior)) {
    reject(
      'structurePrior must be the server-normalized Conditioning V1 structure prior.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  const tempoBpm = structurePrior.tempoBpm;
  const pickupBeats = structurePrior.pickupBeats;
  const timeSignature = structurePrior.timeSignature;
  const feel = structurePrior.feel;

  if (
    tempoBpm !== null &&
    (
      typeof tempoBpm !== 'number' ||
      !Number.isFinite(tempoBpm) ||
      tempoBpm < 20 ||
      tempoBpm > 400
    )
  ) {
    reject(
      'structurePrior.tempoBpm is outside the Conditioning V1 contract.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  if (
    pickupBeats !== null &&
    (
      typeof pickupBeats !== 'number' ||
      !Number.isFinite(pickupBeats) ||
      pickupBeats < 0 ||
      pickupBeats > 32
    )
  ) {
    reject(
      'structurePrior.pickupBeats is outside the Conditioning V1 contract.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  if (timeSignature !== null) {
    normalizeObservedTimeSignature(timeSignature);
  }

  if (!['auto', 'straight', 'triplet'].includes(feel)) {
    reject(
      'structurePrior.feel is outside the Conditioning V1 contract.',
      'INVALID_STRUCTURE_PRIOR'
    );
  }

  return {
    tempoBpm,
    timeSignature:
      timeSignature === null
        ? null
        : {
            numerator: timeSignature.numerator,
            denominator: timeSignature.denominator,
          },
    pickupBeats,
    feel,
  };
}

function unresolvedField() {
  return {
    source: 'unresolved',
    confidence: null,
    method: null,
  };
}

function userPriorField() {
  return {
    source: 'user-prior',
    confidence: null,
    method: null,
  };
}

function mixtureObservationField(field) {
  return {
    source: 'full-mixture-observation',
    confidence: field.confidence,
    method: field.method,
  };
}

function resolveNullableField(priorValue, observedField) {
  if (priorValue !== null) {
    return {
      value: priorValue,
      source: userPriorField(),
    };
  }

  if (observedField) {
    return {
      value: observedField.value,
      source: mixtureObservationField(observedField),
    };
  }

  return {
    value: null,
    source: unresolvedField(),
  };
}

function resolveFeel(priorFeel, observedField) {
  if (priorFeel === 'straight' || priorFeel === 'triplet') {
    return {
      value: priorFeel,
      source: userPriorField(),
    };
  }

  if (observedField) {
    return {
      value: observedField.value,
      source: mixtureObservationField(observedField),
    };
  }

  return {
    value: 'auto',
    source: unresolvedField(),
  };
}

export function buildAiTabMixtureStructureContextV1({
  structurePrior,
  mixtureObservation,
  mixtureSource,
} = {}) {
  const prior = validateStructurePrior(structurePrior);
  const source = validateMixtureSource(mixtureSource);
  const observation = normalizeMixtureObservation(
    mixtureObservation
  );

  const tempo = resolveNullableField(
    prior.tempoBpm,
    observation?.tempoBpm ?? null
  );
  const timeSignature = resolveNullableField(
    prior.timeSignature,
    observation?.timeSignature ?? null
  );
  const pickup = resolveNullableField(
    prior.pickupBeats,
    observation?.pickupBeats ?? null
  );
  const feel = resolveFeel(
    prior.feel,
    observation?.feel ?? null
  );

  const completeForMeasureProjection =
    tempo.value !== null &&
    timeSignature.value !== null &&
    pickup.value !== null;

  return {
    contextContract: {
      name: 'mixture-structure-context',
      version: AI_TAB_MIXTURE_STRUCTURE_CONTEXT_V1,
      referenceBlind: true,
      referenceScoreAuthorized: false,
      carrierStructureBorrowingAllowed: false,
      productionEligible: false,
    },
    mixtureSource: source,
    observationStatus:
      observation === null
        ? 'NOT_CONNECTED'
        : 'TRUSTED_FULL_MIXTURE_OBSERVATION',
    resolved: {
      tempoBpm: tempo.value,
      timeSignature: timeSignature.value,
      pickupBeats: pickup.value,
      feel: feel.value,
    },
    fieldSources: {
      tempoBpm: tempo.source,
      timeSignature: timeSignature.source,
      pickupBeats: pickup.source,
      feel: feel.source,
    },
    completeForMeasureProjection,
    feelResolved:
      feel.value === 'straight' ||
      feel.value === 'triplet',
  };
}
