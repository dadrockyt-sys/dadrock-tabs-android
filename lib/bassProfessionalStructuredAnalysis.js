import { buildBassProfessionalQualityReport } from './bassProfessionalQuality.js';
import {
  BASS_STANDARD_OPEN_MIDI,
  BASS_STRING_LABELS,
  projectBassProfessionalRenderEvents,
} from './bassProfessionalRenderContract.js';

const PROVEN_BASS_TECHNIQUES = Object.freeze([
  'slide-up',
  'slide-down',
  'hammer-on',
  'pull-off',
  'mute',
  'sustain',
]);

const UNPROVEN_BASS_TECHNIQUES = Object.freeze([
  'harmonic',
  'natural-harmonic',
  'pinch-harmonic',
  'slap',
  'pop',
  'tap',
  'bend',
  'vibrato',
]);

function normalizedTechniqueLabels(event) {
  if (!Array.isArray(event?.techniques)) return [];
  return [
    ...new Set(
      event.techniques
        .map((value) => String(value || '').trim().toLowerCase())
        .filter(Boolean)
    ),
  ].sort();
}

function percent(numerator, denominator) {
  if (!denominator) return 0;
  return Number(((numerator / denominator) * 100).toFixed(2));
}

/**
 * Build an inactive structured Bass analysis from already-authenticated events.
 *
 * This contract does not analyze audio, infer placement, add techniques, route an
 * analyzer, or authorize a renderer. It only projects the exact supplied events
 * through the existing four-string Bass render contract and reports whether the
 * same data is structurally ready for a future professional integration boundary.
 */
export function buildBassProfessionalStructuredAnalysis(rawEvents) {
  const events = Array.isArray(rawEvents)
    ? rawEvents.filter((event) => event && typeof event === 'object')
    : [];
  const renderEvents = projectBassProfessionalRenderEvents(events);
  const qualityReport = buildBassProfessionalQualityReport(events);

  const observedTechniqueCounts = {};
  const unsupportedTechniqueCounts = {};
  let techniqueBearingEventCount = 0;

  for (const event of events) {
    const labels = normalizedTechniqueLabels(event);
    if (labels.length > 0) techniqueBearingEventCount += 1;
    for (const label of labels) {
      observedTechniqueCounts[label] = (observedTechniqueCounts[label] || 0) + 1;
      if (!PROVEN_BASS_TECHNIQUES.includes(label)) {
        unsupportedTechniqueCounts[label] = (unsupportedTechniqueCounts[label] || 0) + 1;
      }
    }
  }

  const rawEventCount = events.length;
  const renderEventCount = renderEvents.length;
  const renderSurvivalPercent = percent(renderEventCount, rawEventCount);
  const unsupportedTechniqueLabels = Object.keys(unsupportedTechniqueCounts).sort();

  const structuredDataIntegrationPassed =
    rawEventCount > 0 &&
    renderEventCount === rawEventCount &&
    renderSurvivalPercent === 100 &&
    qualityReport.passed === true &&
    unsupportedTechniqueLabels.length === 0;

  return {
    name: 'bass-reference-free-structured-analysis-diagnostic',
    version: 1,
    instrument: 'bass',
    tuning: 'Standard Bass',
    stringLabels: [...BASS_STRING_LABELS],
    openMidi: [...BASS_STANDARD_OPEN_MIDI],
    rawEventCount,
    renderEventCount,
    renderSurvivalPercent,
    techniqueBearingEventCount,
    observedTechniqueCounts,
    supportedTechniqueLabels: [...PROVEN_BASS_TECHNIQUES],
    explicitlyUnprovenTechniqueLabels: [...UNPROVEN_BASS_TECHNIQUES],
    unsupportedTechniqueCounts,
    unsupportedTechniqueLabels,
    unsupportedTechniqueLabelsPresent: unsupportedTechniqueLabels.length > 0,
    qualityReport,
    renderEvents,
    structuredDataIntegrationPassed,
    diagnosticOnly: true,
    productionCandidate: false,
    professionalStructuredIdentityEnabled: false,
    analyzerRoutingEnabled: false,
    pdfRendererEnabled: false,
    liveEndpointDeployedOrModified: false,
    vercelDeploymentAttempted: false,
    productionModified: false,
    productionPromotionAuthorized: false,
    paidPurchaseAttempted: false,
    customerTokenRedeemed: false,
    customerEmailSent: false,
  };
}

export {
  PROVEN_BASS_TECHNIQUES,
  UNPROVEN_BASS_TECHNIQUES,
};
