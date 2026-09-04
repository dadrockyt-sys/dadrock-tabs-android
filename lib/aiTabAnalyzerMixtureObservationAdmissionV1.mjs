import { buildAiTabMixtureStructureContextV1 } from './aiTabMixtureStructureContextV1.mjs';

export const AI_TAB_ANALYZER_MIXTURE_OBSERVATION_ADMISSION_V1 = 1;

function isPlainRecord(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    !Array.isArray(value)
  );
}

export function admitAiTabAnalyzerMixtureObservationV1(
  observation
) {
  if (!isPlainRecord(observation)) {
    return null;
  }

  if (
    observation.version !==
    AI_TAB_ANALYZER_MIXTURE_OBSERVATION_ADMISSION_V1
  ) {
    return null;
  }

  const provenance = observation.provenance;
  const diagnostics = observation.diagnostics;
  const wavAdapter = diagnostics?.wavAdapter;

  if (
    !isPlainRecord(provenance) ||
    !isPlainRecord(diagnostics) ||
    !isPlainRecord(wavAdapter)
  ) {
    return null;
  }

  if (
    provenance.sourceKind !== 'full-mixture' ||
    provenance.sourceIdentity !== 'request-audio' ||
    provenance.referenceBlind !== true ||
    provenance.referenceRuntimeInputUsed !== false ||
    diagnostics.referenceBlind !== true ||
    diagnostics.carrierInputUsed !== false ||
    diagnostics.transcribedEventInputUsed !== false ||
    wavAdapter.fullMixtureOnly !== true ||
    wavAdapter.separatedCarrierUsed !== false ||
    wavAdapter.transcribedEventInputUsed !== false
  ) {
    return null;
  }

  return observation;
}

export function buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
  baselineContext,
  analyzerObservation,
  structurePrior,
  mixtureSource,
} = {}) {
  const admittedObservation =
    admitAiTabAnalyzerMixtureObservationV1(
      analyzerObservation
    );

  if (!admittedObservation) {
    return baselineContext;
  }

  try {
    return buildAiTabMixtureStructureContextV1({
      structurePrior,
      mixtureObservation: admittedObservation,
      mixtureSource,
    });
  } catch {
    return baselineContext;
  }
}
