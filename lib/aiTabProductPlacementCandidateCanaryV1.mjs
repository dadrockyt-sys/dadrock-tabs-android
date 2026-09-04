export const AI_TAB_PRODUCT_PLACEMENT_CANDIDATE_CANARY_V1 = 1;

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

function buildContract() {
  return {
    name: 'full-mixture-product-placement-live-candidate-canary',
    version: AI_TAB_PRODUCT_PLACEMENT_CANDIDATE_CANARY_V1,
    researchOnly: true,
    shadowOnly: true,
    placementOnlyAuthority: true,
    liveProductAuthority: false,
    pdfAuthority: false,
    productionEligible: false,
    referenceBlind: true,
    referenceScoreAuthorized: false,
  };
}

function failOpenSummary(baselineRenderEventCount = 0) {
  return {
    canaryContract: buildContract(),
    eligible: false,
    baselineRenderEventCount:
      nonNegativeInteger(baselineRenderEventCount)
        ? baselineRenderEventCount
        : 0,
    candidateRenderEventCount: 0,
  };
}

async function loadCandidateBuilder() {
  const module = await import(
    '../analyzer/full_mixture_product_placement_candidate_v1.mjs'
  );

  return module?.buildFullMixtureProductPlacementCandidateV1;
}

export async function buildAiTabProductPlacementCandidateCanaryV1({
  structuredPayload,
  dualContextShadowProjection,
  candidateBuilder = null,
} = {}) {
  const baselineRenderEventCount =
    Array.isArray(structuredPayload?.renderEvents)
      ? structuredPayload.renderEvents.length
      : 0;

  const fallback = failOpenSummary(
    baselineRenderEventCount
  );

  try {
    const builder =
      typeof candidateBuilder === 'function'
        ? candidateBuilder
        : await loadCandidateBuilder();

    if (typeof builder !== 'function') {
      return fallback;
    }

    const maybeCandidate = builder({
      structuredPayload,
      dualContextShadowProjection,
    });

    const candidate =
      maybeCandidate &&
      typeof maybeCandidate.then === 'function'
        ? await maybeCandidate
        : maybeCandidate;

    if (!isRecord(candidate)) {
      return fallback;
    }

    const contract = candidate.candidateContract;
    const rows = candidate.renderEvents;

    if (
      !isRecord(contract) ||
      contract.name !== 'full-mixture-product-placement-candidate' ||
      contract.version !== 1 ||
      contract.experimentOnly !== true ||
      contract.placementOnlyAuthority !== true ||
      contract.liveProductWiringAuthorized !== false ||
      contract.pdfAuthorityAuthorized !== false ||
      contract.referenceBlind !== true ||
      contract.referenceScoreAuthorized !== false ||
      contract.productionEligible !== false ||
      !Array.isArray(rows) ||
      rows.length === 0 ||
      !nonNegativeInteger(candidate.baselineRenderEventCount) ||
      !nonNegativeInteger(candidate.candidateRenderEventCount) ||
      candidate.baselineRenderEventCount !== baselineRenderEventCount ||
      candidate.candidateRenderEventCount !== rows.length
    ) {
      return fallback;
    }

    // Phase 11 intentionally exposes summary counts only. Candidate placement
    // rows remain local to the Phase 10 helper result and never enter the live
    // response or any Product/PDF authority path.
    return {
      canaryContract: buildContract(),
      eligible: true,
      baselineRenderEventCount,
      candidateRenderEventCount: rows.length,
    };
  } catch {
    // Canary-only failures must never change an otherwise valid canonical
    // analyzer response. The caller receives bounded ineligible metadata only.
    return fallback;
  }
}
