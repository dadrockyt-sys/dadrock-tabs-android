import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  buildBassProfessionalStructuredAnalysis,
  PROVEN_BASS_TECHNIQUES,
} from '../lib/bassProfessionalStructuredAnalysis.js';

const REQUIRED_VIEW_AGREEMENT = 2;

function parseArgs(argv) {
  const out = {};
  for (let index = 2; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--input' || value === '--output') {
      out[value.slice(2)] = argv[index + 1];
      index += 1;
    }
  }
  if (!out.input || !out.output) {
    throw new Error(
      'Usage: node verify_bass_real_audio_structured_integration.mjs --input <json> --output <json>'
    );
  }
  return out;
}

function normalizedTechniques(event) {
  return Array.isArray(event?.techniques)
    ? [...new Set(event.techniques.map((value) => String(value || '').trim().toLowerCase()).filter(Boolean))].sort()
    : [];
}

function renderIdentityFromRaw(event, eventIndex) {
  const output = {
    eventIndex,
    measure: Math.round(Number(event.measure)),
    step: Math.round(Number(event.step)),
    stringIndex: Math.round(Number(event.stringIndex)),
    stringLabel: String(event.stringLabel || ''),
    fret: Math.round(Number(event.fret)),
    midi: Math.round(Number(event.midi)),
    durationSteps: Math.max(1, Math.round(Number(event.durationSteps || 1))),
    techniques: normalizedTechniques(event),
  };
  const durationSeconds = Number(event.durationSeconds);
  if (Number.isFinite(durationSeconds) && durationSeconds >= 0) {
    output.durationSeconds = durationSeconds;
  }
  return JSON.stringify(output);
}

function renderIdentity(event) {
  return JSON.stringify({
    eventIndex: event?.eventIndex,
    measure: event?.measure,
    step: event?.step,
    stringIndex: event?.stringIndex,
    stringLabel: event?.stringLabel,
    fret: event?.fret,
    midi: event?.midi,
    durationSteps: event?.durationSteps,
    techniques: Array.isArray(event?.techniques) ? event.techniques : [],
    ...(Number.isFinite(Number(event?.durationSeconds))
      ? { durationSeconds: Number(event.durationSeconds) }
      : {}),
  });
}

const args = parseArgs(process.argv);
const raw = JSON.parse(await readFile(args.input, 'utf8'));
const events = Array.isArray(raw.events) ? raw.events : [];
const subsetDiagnostics =
  raw.subsetTechniqueDiagnostics && typeof raw.subsetTechniqueDiagnostics === 'object'
    ? raw.subsetTechniqueDiagnostics
    : {};
const harmonicDiagnostics =
  raw.harmonicDiagnostics && typeof raw.harmonicDiagnostics === 'object'
    ? raw.harmonicDiagnostics
    : {};

const structured = buildBassProfessionalStructuredAnalysis(events);

let exactRenderIdentityCount = 0;
let evidenceBackedTechniqueLabelCount = 0;
let techniqueLabelCount = 0;
let harmonicLabelCount = 0;
let highRiskLabelCount = 0;
const highRiskLabels = new Set(['harmonic', 'natural-harmonic', 'pinch-harmonic', 'slap', 'pop', 'tap', 'bend', 'vibrato']);

for (let index = 0; index < events.length; index += 1) {
  const rawEvent = events[index];
  const renderEvent = structured.renderEvents[index];
  if (
    renderEvent &&
    renderIdentityFromRaw(rawEvent, index) === renderIdentity(renderEvent)
  ) {
    exactRenderIdentityCount += 1;
  }

  const labels = normalizedTechniques(rawEvent);
  const evidence = Array.isArray(rawEvent?.bassTechniqueEvidence)
    ? rawEvent.bassTechniqueEvidence.filter((row) => row && typeof row === 'object')
    : [];

  for (const label of labels) {
    techniqueLabelCount += 1;
    if (label === 'harmonic') harmonicLabelCount += 1;
    if (highRiskLabels.has(label)) highRiskLabelCount += 1;

    const matching = evidence.find(
      (row) =>
        String(row.type || '').trim().toLowerCase() === label &&
        row.consensusPassed === true &&
        Number(row.viewAgreement) >= REQUIRED_VIEW_AGREEMENT &&
        Number(row.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
        row.referenceFree === true &&
        row.professionalReferenceUsed === false &&
        row.runtimeLabelsRequired === false
    );
    if (matching) evidenceBackedTechniqueLabelCount += 1;
  }
}

const quality = structured.qualityReport || {};
const boundaryChecks = {
  approvedFixture: raw.approvedFixture === 'public/gomywayfullaitest.m4a',
  referenceFree: raw.referenceFree === true,
  crossViewConsensusRequired:
    raw.crossViewConsensusRequired === true &&
    Number(raw.requiredConsensusViews) === REQUIRED_VIEW_AGREEMENT,
  noteTimingPlayabilityPrecondition: raw.noteTimingPlayabilityPreconditionPassed === true,
  subsetTechniquePrecondition: raw.subsetTechniqueBoundaryPreconditionPassed === true,
  subsetDiagnosticsSound:
    Number(subsetDiagnostics.eventCount) === events.length &&
    Number(subsetDiagnostics.techniqueEventCount) >= 4 &&
    Number(subsetDiagnostics.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
    subsetDiagnostics.referenceFree === true &&
    subsetDiagnostics.futureHighRiskFamiliesEnabled === false,
  harmonicSafeAbstentionPreserved:
    raw.harmonicEvidenceImplemented === true &&
    raw.harmonicEvidenceObserved === false &&
    raw.harmonicFamilyProven === false &&
    harmonicDiagnostics.harmonicEvidenceImplemented === true &&
    harmonicDiagnostics.harmonicEvidenceObserved === false &&
    harmonicDiagnostics.harmonicFamilyProven === false &&
    harmonicDiagnostics.safeAbstention === true &&
    harmonicLabelCount === 0,
  structuredContractPassed: structured.structuredDataIntegrationPassed === true,
  eventCountStable:
    events.length > 0 &&
    structured.rawEventCount === events.length &&
    structured.renderEventCount === events.length,
  renderSurvival100: structured.renderSurvivalPercent === 100,
  exactRenderIdentity100:
    events.length > 0 && exactRenderIdentityCount === events.length,
  supportedTechniqueLabelsOnly:
    structured.unsupportedTechniqueLabelsPresent === false &&
    structured.unsupportedTechniqueLabels.length === 0 &&
    Object.keys(structured.observedTechniqueCounts).every((label) =>
      PROVEN_BASS_TECHNIQUES.includes(label)
    ),
  everyTechniqueEvidenceBacked:
    techniqueLabelCount > 0 &&
    evidenceBackedTechniqueLabelCount === techniqueLabelCount,
  noHarmonicOrHighRiskLabels: harmonicLabelCount === 0 && highRiskLabelCount === 0,
  qualityPassed100:
    quality.passed === true &&
    quality.renderEventSurvivalPercent === 100 &&
    quality.playableStringFretPercent === 100 &&
    quality.timingCoveragePercent === 100 &&
    quality.pitchValidityPercent === 100 &&
    quality.pitchStringFretConsistencyPercent === 100,
  standardBassMapping:
    JSON.stringify(structured.stringLabels) === JSON.stringify(['G', 'D', 'A', 'E']) &&
    JSON.stringify(structured.openMidi) === JSON.stringify([43, 38, 33, 28]),
};

const safetyChecks = {
  diagnosticOnly: structured.diagnosticOnly === true,
  productionCandidateDisabled: structured.productionCandidate === false,
  structuredIdentityDisabled:
    structured.professionalStructuredIdentityEnabled === false &&
    raw.professionalStructuredIdentityEnabled === false,
  routingDisabled:
    structured.analyzerRoutingEnabled === false && raw.analyzerRoutingEnabled === false,
  pdfDisabled:
    structured.pdfRendererEnabled === false && raw.pdfRendererEnabled === false,
  liveEndpointUnchanged:
    structured.liveEndpointDeployedOrModified === false &&
    raw.liveEndpointDeployedOrModified === false,
  vercelNotAttempted:
    structured.vercelDeploymentAttempted === false && raw.vercelDeploymentAttempted === false,
  productionUnchanged:
    structured.productionModified === false && raw.productionModified === false,
  promotionDisabled:
    structured.productionPromotionAuthorized === false &&
    raw.productionPromotionAuthorized === false,
  purchaseNotAttempted:
    structured.paidPurchaseAttempted === false && raw.paidPurchaseAttempted === false,
  tokenNotRedeemed:
    structured.customerTokenRedeemed === false && raw.customerTokenRedeemed === false,
  emailNotSent:
    structured.customerEmailSent === false && raw.customerEmailSent === false,
  professionalBassNotClaimed: raw.professionalBassComplete === false,
};

const passed =
  Object.values(boundaryChecks).every(Boolean) &&
  Object.values(safetyChecks).every(Boolean);

const evidence = {
  schemaVersion: 1,
  gate: 'bass-real-audio-structured-event-integration',
  approvedFixture: raw.approvedFixture,
  sourceSha256: raw.sourceSha256,
  sourceBytes: raw.sourceBytes,
  eventCount: events.length,
  renderEventCount: structured.renderEventCount,
  renderSurvivalPercent: structured.renderSurvivalPercent,
  exactRenderIdentityEventCount: exactRenderIdentityCount,
  exactRenderIdentityPercent: events.length
    ? Number(((exactRenderIdentityCount / events.length) * 100).toFixed(2))
    : 0,
  techniqueBearingEventCount: structured.techniqueBearingEventCount,
  techniqueLabelCount,
  evidenceBackedTechniqueLabelCount,
  evidenceBackedTechniquePercent: techniqueLabelCount
    ? Number(((evidenceBackedTechniqueLabelCount / techniqueLabelCount) * 100).toFixed(2))
    : 0,
  observedTechniqueCounts: structured.observedTechniqueCounts,
  supportedTechniqueLabels: structured.supportedTechniqueLabels,
  explicitlyUnprovenTechniqueLabels: structured.explicitlyUnprovenTechniqueLabels,
  unsupportedTechniqueLabels: structured.unsupportedTechniqueLabels,
  harmonicSafeAbstention: harmonicDiagnostics.safeAbstention === true,
  harmonicFamilyProven: false,
  qualityReport: quality,
  boundaryChecks,
  safetyChecks,
  structuredEventIntegrationBoundaryPassed: passed,
  diagnosticOnly: true,
  professionalBassComplete: false,
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
  passed,
};

const outputPath = path.resolve(args.output);
await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
console.log(JSON.stringify(evidence, null, 2));

if (!passed) {
  process.exitCode = 1;
} else {
  console.log('BASS REAL-AUDIO STRUCTURED EVENT INTEGRATION PASSED');
}
