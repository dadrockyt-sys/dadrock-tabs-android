import { validateV143RenderEvents } from '../lib/v143RenderContract.js';

export const FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_V1 = 1;

function isRecord(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  );
}

function validInteger(value, minimum, maximum = Number.MAX_SAFE_INTEGER) {
  return (
    Number.isInteger(value) &&
    value >= minimum &&
    value <= maximum
  );
}

function fusionContractAccepted(contract) {
  return Boolean(
    isRecord(contract) &&
    contract.name === 'dual-context-shadow-fusion' &&
    contract.version === 1 &&
    contract.shadowOnly === true &&
    contract.referenceBlind === true &&
    contract.referenceScoreAuthorized === false &&
    contract.carrierStructureBorrowingAllowed === false &&
    contract.productionEligible === false
  );
}

function shadowContractAccepted(contract) {
  return Boolean(
    isRecord(contract) &&
    contract.name === 'structure-conditioned-shadow-projection' &&
    contract.version === 1 &&
    contract.shadowOnly === true &&
    contract.referenceBlind === true &&
    contract.referenceScoreAuthorized === false &&
    contract.productionEligible === false
  );
}

function structureAccepted(structure) {
  return Boolean(
    isRecord(structure) &&
    structure.status === 'EXPLICIT_STRUCTURE_RESOLVED' &&
    structure.quantizationStatus === 'STRAIGHT' &&
    Number.isFinite(structure.tempoBpm) &&
    structure.tempoBpm >= 20 &&
    structure.tempoBpm <= 400 &&
    isRecord(structure.timeSignature) &&
    structure.timeSignature.numerator === 4 &&
    structure.timeSignature.denominator === 4 &&
    structure.pickupBeats === 0 &&
    structure.feel === 'straight' &&
    structure.subdivisionsPerSignatureUnit === 4 &&
    Number.isFinite(structure.subdivisionSeconds) &&
    structure.subdivisionSeconds > 0
  );
}

function authorityAccepted(authority) {
  return Boolean(
    isRecord(authority) &&
    authority.source === 'mixture-structure-context-v1' &&
    authority.observationStatus === 'TRUSTED_FULL_MIXTURE_OBSERVATION' &&
    authority.completeForMeasureProjection === true &&
    authority.feelResolved === true
  );
}

function exactValidatedRow(candidate, validated) {
  return Boolean(
    validated &&
    candidate.eventIndex === validated.eventIndex &&
    candidate.measure === validated.measure &&
    candidate.step === validated.step &&
    candidate.stringIndex === validated.stringIndex &&
    candidate.fret === validated.fret &&
    candidate.midi === validated.midi &&
    candidate.durationSteps === validated.durationSteps &&
    Array.isArray(validated.techniques) &&
    validated.techniques.length === 0
  );
}

export function buildFullMixtureProductPlacementCandidateV1({
  structuredPayload,
  dualContextShadowProjection,
} = {}) {
  try {
    if (!isRecord(structuredPayload)) return null;

    const payloadContract = structuredPayload.payloadContract;
    if (
      !isRecord(payloadContract) ||
      payloadContract.v143RuntimeSafetyVerified !== true
    ) {
      return null;
    }

    if (
      !Array.isArray(structuredPayload.renderEvents) ||
      structuredPayload.renderEvents.length !== 0
    ) {
      // Existing authenticated Product placement always wins.
      return null;
    }

    const canonicalEvents = structuredPayload.events;
    if (!Array.isArray(canonicalEvents) || canonicalEvents.length === 0) {
      return null;
    }

    const dual = dualContextShadowProjection;
    if (
      !isRecord(dual) ||
      !fusionContractAccepted(dual.fusionContract) ||
      !authorityAccepted(dual.structureAuthority)
    ) {
      return null;
    }

    const projection = dual.projection;
    if (
      !isRecord(projection) ||
      !shadowContractAccepted(projection.shadowContract) ||
      !structureAccepted(projection.structure) ||
      !Array.isArray(projection.events) ||
      projection.events.length !== canonicalEvents.length
    ) {
      return null;
    }

    const candidate = [];

    for (let index = 0; index < canonicalEvents.length; index += 1) {
      const canonical = canonicalEvents[index];
      const shadow = projection.events[index];

      if (!isRecord(canonical) || !isRecord(shadow)) return null;

      const eventIndex = canonical.eventIndex;
      const stringIndex = canonical.stringIndex;
      const fret = canonical.fret;
      const midi = canonical.midi;

      if (
        !validInteger(eventIndex, 0) ||
        !validInteger(stringIndex, 0, 5) ||
        !validInteger(fret, 0, 36) ||
        !validInteger(midi, 0, 127)
      ) {
        return null;
      }

      // Placement-only authority: source identity/instrument facts must match
      // exactly. Conditioned string/fret values are deliberately ignored.
      if (
        shadow.sourceEventIndex !== eventIndex ||
        shadow.sourceStringIndex !== stringIndex ||
        shadow.sourceFret !== fret ||
        shadow.midi !== midi
      ) {
        return null;
      }

      if (
        shadow.pickup !== false ||
        !validInteger(shadow.measureNumber, 1) ||
        !validInteger(shadow.subdivisionIndex, 0)
      ) {
        return null;
      }

      const measure = Math.floor(shadow.subdivisionIndex / 16) + 1;
      const step = shadow.subdivisionIndex % 16;

      if (measure !== shadow.measureNumber) return null;

      candidate.push({
        eventIndex,
        measure,
        step,
        stringIndex,
        fret,
        midi,
        durationSteps: 1,
        techniques: [],
      });
    }

    const validated = validateV143RenderEvents(candidate);
    if (validated.length !== candidate.length) return null;

    for (let index = 0; index < candidate.length; index += 1) {
      if (!exactValidatedRow(candidate[index], validated[index])) {
        return null;
      }
    }

    return {
      candidateContract: {
        name: 'full-mixture-product-placement-candidate',
        version: FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_V1,
        experimentOnly: true,
        placementOnlyAuthority: true,
        liveProductWiringAuthorized: false,
        pdfAuthorityAuthorized: false,
        referenceBlind: true,
        referenceScoreAuthorized: false,
        productionEligible: false,
      },
      baselineRenderEventCount: 0,
      candidateRenderEventCount: validated.length,
      renderEvents: validated,
    };
  } catch {
    // Phase 10 experiment remains fail-open: no candidate is safer than a
    // partially admitted or malformed placement stream.
    return null;
  }
}
