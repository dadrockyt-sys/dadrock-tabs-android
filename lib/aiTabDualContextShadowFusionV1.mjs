import {
  normalizeAiTabConditioningV1,
} from './aiTabConditioningV1.mjs';
import {
  buildAiTabConditionedShadowProjectionV1,
} from './aiTabConditionedShadowProjectionV1.mjs';

export const AI_TAB_DUAL_CONTEXT_SHADOW_FUSION_V1 = 1;

const ALLOWED_DENOMINATORS = new Set([
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

export class AiTabDualContextShadowFusionValidationError extends Error {
  constructor(
    message,
    code = 'INVALID_DUAL_CONTEXT_SHADOW_FUSION'
  ) {
    super(message);
    this.name = 'AiTabDualContextShadowFusionValidationError';
    this.code = code;
  }
}

function reject(message, code) {
  throw new AiTabDualContextShadowFusionValidationError(
    message,
    code
  );
}

function validateResolvedStructure(resolved) {
  if (!isPlainRecord(resolved)) {
    reject(
      'mixtureStructureContext.resolved must be an object.',
      'INVALID_MIXTURE_STRUCTURE_CONTEXT'
    );
  }

  const tempoBpm = resolved.tempoBpm;
  const pickupBeats = resolved.pickupBeats;
  const timeSignature = resolved.timeSignature;
  const feel = resolved.feel;

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
      'Resolved tempo is outside the Conditioning V1 range.',
      'INVALID_RESOLVED_STRUCTURE'
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
      'Resolved pickup is outside the Conditioning V1 range.',
      'INVALID_RESOLVED_STRUCTURE'
    );
  }

  if (timeSignature !== null) {
    if (
      !isPlainRecord(timeSignature) ||
      !Number.isInteger(timeSignature.numerator) ||
      timeSignature.numerator < 1 ||
      timeSignature.numerator > 32 ||
      !Number.isInteger(timeSignature.denominator) ||
      !ALLOWED_DENOMINATORS.has(timeSignature.denominator)
    ) {
      reject(
        'Resolved time signature is outside the Conditioning V1 range.',
        'INVALID_RESOLVED_STRUCTURE'
      );
    }
  }

  if (!['auto', 'straight', 'triplet'].includes(feel)) {
    reject(
      'Resolved feel must be auto, straight, or triplet.',
      'INVALID_RESOLVED_STRUCTURE'
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

function validateMixtureStructureContext(context) {
  if (!isPlainRecord(context)) {
    reject(
      'mixtureStructureContext is required.',
      'INVALID_MIXTURE_STRUCTURE_CONTEXT'
    );
  }

  const contract = context.contextContract;

  if (
    !isPlainRecord(contract) ||
    contract.name !== 'mixture-structure-context' ||
    contract.version !== 1 ||
    contract.referenceBlind !== true ||
    contract.referenceScoreAuthorized !== false ||
    contract.carrierStructureBorrowingAllowed !== false ||
    contract.productionEligible !== false
  ) {
    reject(
      'mixtureStructureContext contract does not satisfy the Phase 3 safety boundary.',
      'INVALID_MIXTURE_STRUCTURE_CONTEXT_CONTRACT'
    );
  }

  if (
    !isPlainRecord(context.mixtureSource) ||
    context.mixtureSource.kind !== 'full-mixture' ||
    context.mixtureSource.source !== 'request-audio'
  ) {
    reject(
      'Dual-context fusion requires the full-mixture request-audio source.',
      'CARRIER_STRUCTURE_BORROWING_FORBIDDEN'
    );
  }

  if (
    ![
      'NOT_CONNECTED',
      'TRUSTED_FULL_MIXTURE_OBSERVATION',
    ].includes(context.observationStatus)
  ) {
    reject(
      'mixtureStructureContext observation status is invalid.',
      'INVALID_MIXTURE_STRUCTURE_CONTEXT'
    );
  }

  const resolved = validateResolvedStructure(
    context.resolved
  );

  return {
    resolved,
    observationStatus: context.observationStatus,
    completeForMeasureProjection:
      context.completeForMeasureProjection === true,
    feelResolved: context.feelResolved === true,
    fieldSources:
      isPlainRecord(context.fieldSources)
        ? JSON.parse(JSON.stringify(context.fieldSources))
        : {},
  };
}

export function buildAiTabDualContextShadowFusionV1({
  events,
  conditioning,
  mixtureStructureContext,
} = {}) {
  const role = conditioning?.instrumentConfig?.role;
  const normalizedConditioning =
    normalizeAiTabConditioningV1(conditioning, role);
  const context = validateMixtureStructureContext(
    mixtureStructureContext
  );

  const fusedConditioning =
    normalizeAiTabConditioningV1(
      {
        version: 1,
        structurePrior: context.resolved,
        instrumentConfig: {
          role:
            normalizedConditioning.instrumentConfig.role,
          tuningMidi: [
            ...normalizedConditioning.instrumentConfig.tuningMidi,
          ],
          capoFret:
            normalizedConditioning.instrumentConfig.capoFret,
        },
      },
      normalizedConditioning.instrumentConfig.role
    );

  const projection =
    buildAiTabConditionedShadowProjectionV1({
      events: Array.isArray(events)
        ? events.map((event) => ({ ...event }))
        : [],
      conditioning: fusedConditioning,
    });

  return {
    fusionContract: {
      name: 'dual-context-shadow-fusion',
      version: AI_TAB_DUAL_CONTEXT_SHADOW_FUSION_V1,
      shadowOnly: true,
      referenceBlind: true,
      referenceScoreAuthorized: false,
      carrierStructureBorrowingAllowed: false,
      productionEligible: false,
    },
    structureAuthority: {
      source: 'mixture-structure-context-v1',
      observationStatus: context.observationStatus,
      completeForMeasureProjection:
        context.completeForMeasureProjection,
      feelResolved: context.feelResolved,
      fieldSources: context.fieldSources,
    },
    instrumentAuthority: {
      source: 'conditioning-v1',
      role:
        normalizedConditioning.instrumentConfig.role,
      tuningMidi: [
        ...normalizedConditioning.instrumentConfig.tuningMidi,
      ],
      capoFret:
        normalizedConditioning.instrumentConfig.capoFret,
    },
    projection,
  };
}
