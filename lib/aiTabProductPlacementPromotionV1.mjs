import { buildFullMixtureProductPlacementCandidateV1 } from '../analyzer/full_mixture_product_placement_candidate_v1.mjs';
import { buildV143AnalyzerQualityReport } from './v143AnalyzerQuality.js';
import { validateV143RenderEvents } from './v143RenderContract.js';

export const AI_TAB_PRODUCT_PLACEMENT_PROMOTION_V1 = 1;

function isRecord(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  );
}

function nonNegativeInteger(value) {
  return Number.isInteger(value) && value >= 0;
}

function promotionContract() {
  return {
    name: 'full-mixture-product-placement-canonical-promotion',
    version: AI_TAB_PRODUCT_PLACEMENT_PROMOTION_V1,
    placementOnlyAuthority: true,
    referenceBlind: true,
    referenceScoreAuthorized: false,
    productAuthority: true,
    pdfAuthority: true,
    productionDeploymentAuthorized: false,
  };
}

function summary({
  promoted,
  reason,
  baselineRenderEventCount,
  canonicalRenderEventCount,
}) {
  return {
    promotionContract: promotionContract(),
    promoted: promoted === true,
    reason,
    baselineRenderEventCount:
      nonNegativeInteger(baselineRenderEventCount)
        ? baselineRenderEventCount
        : 0,
    canonicalRenderEventCount:
      nonNegativeInteger(canonicalRenderEventCount)
        ? canonicalRenderEventCount
        : 0,
  };
}

function baselineResult(
  structuredPayload,
  reason,
  baselineRenderEventCount
) {
  return {
    promotedPayload: structuredPayload,
    productPlacementPromotion: summary({
      promoted: false,
      reason,
      baselineRenderEventCount,
      canonicalRenderEventCount:
        baselineRenderEventCount,
    }),
  };
}

function candidateContractAccepted(contract) {
  return Boolean(
    isRecord(contract) &&
    contract.name ===
      'full-mixture-product-placement-candidate' &&
    contract.version === 1 &&
    contract.experimentOnly === true &&
    contract.placementOnlyAuthority === true &&
    contract.liveProductWiringAuthorized === false &&
    contract.pdfAuthorityAuthorized === false &&
    contract.referenceBlind === true &&
    contract.referenceScoreAuthorized === false &&
    contract.productionEligible === false
  );
}

function exactValidatedRows(candidateRows, validatedRows) {
  if (
    !Array.isArray(candidateRows) ||
    !Array.isArray(validatedRows) ||
    candidateRows.length !== validatedRows.length
  ) {
    return false;
  }

  for (let index = 0; index < candidateRows.length; index += 1) {
    const candidate = candidateRows[index];
    const validated = validatedRows[index];

    if (
      !isRecord(candidate) ||
      !isRecord(validated) ||
      candidate.eventIndex !== validated.eventIndex ||
      candidate.measure !== validated.measure ||
      candidate.step !== validated.step ||
      candidate.stringIndex !== validated.stringIndex ||
      candidate.fret !== validated.fret ||
      candidate.midi !== validated.midi ||
      candidate.durationSteps !== validated.durationSteps ||
      !Array.isArray(candidate.techniques) ||
      !Array.isArray(validated.techniques) ||
      candidate.techniques.length !== 0 ||
      validated.techniques.length !== 0
    ) {
      return false;
    }
  }

  return true;
}

function canonicalIdentityAccepted(
  canonicalEvents,
  validatedRows
) {
  if (
    !Array.isArray(canonicalEvents) ||
    !Array.isArray(validatedRows) ||
    canonicalEvents.length !== validatedRows.length
  ) {
    return false;
  }

  for (let index = 0; index < canonicalEvents.length; index += 1) {
    const canonical = canonicalEvents[index];
    const promoted = validatedRows[index];

    if (
      !isRecord(canonical) ||
      !isRecord(promoted) ||
      canonical.eventIndex !== promoted.eventIndex ||
      canonical.stringIndex !== promoted.stringIndex ||
      canonical.fret !== promoted.fret ||
      canonical.midi !== promoted.midi
    ) {
      return false;
    }
  }

  return true;
}

function effectiveQualityEvents(
  canonicalEvents,
  validatedRows
) {
  return canonicalEvents.map((event, index) => ({
    ...event,
    measure: validatedRows[index].measure,
    step: validatedRows[index].step,
  }));
}

export function buildAiTabProductPlacementPromotionV1({
  structuredPayload,
  dualContextShadowProjection,
  candidateBuilder =
    buildFullMixtureProductPlacementCandidateV1,
  renderValidator = validateV143RenderEvents,
  qualityBuilder = buildV143AnalyzerQualityReport,
} = {}) {
  const baselineRenderEventCount =
    Array.isArray(structuredPayload?.renderEvents)
      ? structuredPayload.renderEvents.length
      : 0;

  try {
    if (!isRecord(structuredPayload)) {
      return baselineResult(
        structuredPayload,
        'NON_V143_RHYTHM_BASELINE',
        baselineRenderEventCount
      );
    }

    const payloadContract =
      structuredPayload.payloadContract;

    if (baselineRenderEventCount > 0) {
      return baselineResult(
        structuredPayload,
        'AUTHENTICATED_RENDER_EVENTS_PRESENT',
        baselineRenderEventCount
      );
    }

    if (
      !Array.isArray(structuredPayload.renderEvents) ||
      !isRecord(payloadContract) ||
      payloadContract.v143RuntimeSafetyVerified !== true ||
      payloadContract.transcriptionType !== 'rhythm' ||
      structuredPayload.analysisEngine !==
        'v143-reference-free-rhythm-fallback' ||
      !Array.isArray(structuredPayload.events) ||
      structuredPayload.events.length === 0
    ) {
      return baselineResult(
        structuredPayload,
        'NON_V143_RHYTHM_BASELINE',
        baselineRenderEventCount
      );
    }

    if (
      typeof candidateBuilder !== 'function' ||
      typeof renderValidator !== 'function' ||
      typeof qualityBuilder !== 'function'
    ) {
      return baselineResult(
        structuredPayload,
        'PROMOTION_FAIL_OPEN',
        baselineRenderEventCount
      );
    }

    const candidate = candidateBuilder({
      structuredPayload,
      dualContextShadowProjection,
    });

    if (
      !isRecord(candidate) ||
      !candidateContractAccepted(
        candidate.candidateContract
      ) ||
      candidate.baselineRenderEventCount !== 0 ||
      !nonNegativeInteger(
        candidate.candidateRenderEventCount
      ) ||
      candidate.candidateRenderEventCount !==
        structuredPayload.events.length ||
      !Array.isArray(candidate.renderEvents) ||
      candidate.renderEvents.length !==
        candidate.candidateRenderEventCount
    ) {
      return baselineResult(
        structuredPayload,
        'CANDIDATE_INELIGIBLE',
        baselineRenderEventCount
      );
    }

    const validatedRows = renderValidator(
      candidate.renderEvents
    );

    if (
      !exactValidatedRows(
        candidate.renderEvents,
        validatedRows
      ) ||
      !canonicalIdentityAccepted(
        structuredPayload.events,
        validatedRows
      )
    ) {
      return baselineResult(
        structuredPayload,
        'CANDIDATE_INELIGIBLE',
        baselineRenderEventCount
      );
    }

    const qualityEvents = effectiveQualityEvents(
      structuredPayload.events,
      validatedRows
    );

    const analysisQuality = qualityBuilder({
      referenceFree: true,
      rawEvents: qualityEvents,
      renderEvents: validatedRows,
    });

    if (
      !isRecord(analysisQuality) ||
      analysisQuality.passed !== true
    ) {
      return baselineResult(
        structuredPayload,
        'QUALITY_GATE_REJECTED',
        baselineRenderEventCount
      );
    }

    const promotedPayload = {
      ...structuredPayload,
      payloadContract: {
        ...payloadContract,
        renderEventCount: validatedRows.length,
        renderContractVersion: 1,
        analyzerQualityGatePassed: true,
        structuredRenderEligible: true,
        productionPromotionAuthorized: false,
        placementPromotion: {
          name:
            'full-mixture-product-placement-canonical-promotion',
          version:
            AI_TAB_PRODUCT_PLACEMENT_PROMOTION_V1,
          source:
            'full-mixture-product-placement-candidate-v1',
          placementOnlyAuthority: true,
          referenceBlind: true,
          referenceScoreAuthorized: false,
          productAuthority: true,
          pdfAuthority: true,
          productionDeploymentAuthorized: false,
        },
      },
      analysisQuality,
      analysisEngine:
        'v143-reference-free-rhythm',
      renderEvents: validatedRows,
      renderContractVersion: 1,
    };

    return {
      promotedPayload,
      productPlacementPromotion: summary({
        promoted: true,
        reason: 'PROMOTED_PLACEMENT_ONLY',
        baselineRenderEventCount,
        canonicalRenderEventCount:
          validatedRows.length,
      }),
    };
  } catch {
    return baselineResult(
      structuredPayload,
      'PROMOTION_FAIL_OPEN',
      baselineRenderEventCount
    );
  }
}
