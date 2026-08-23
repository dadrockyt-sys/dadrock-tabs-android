import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  buildBassProfessionalQualityReport,
  DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
} from '../lib/bassProfessionalQuality.js';

const MINIMUM_TECHNIQUE_EVENTS = 4;
const REQUIRED_VIEW_AGREEMENT = 2;
const ALLOWED_TECHNIQUES = new Set([
  'slide-up',
  'slide-down',
  'hammer-on',
  'pull-off',
  'mute',
  'sustain',
]);
const FORBIDDEN_UNPROVEN_TECHNIQUES = new Set([
  'harmonic',
  'natural-harmonic',
  'pinch-harmonic',
  'slap',
  'pop',
  'tap',
  'bend',
  'vibrato',
]);

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
    throw new Error('Usage: node verify_bass_real_audio_techniques.mjs --input <json> --output <json>');
  }
  return out;
}

function canonicalIdentity(event) {
  return JSON.stringify({
    measure: event?.measure,
    step: event?.step,
    timeSeconds: event?.timeSeconds,
    midi: event?.midi,
    stringIndex: event?.stringIndex,
    stringLabel: event?.stringLabel,
    fret: event?.fret,
    durationSeconds: event?.durationSeconds,
    durationSteps: event?.durationSteps,
    sourceCount: event?.sourceCount,
    sources: event?.sources,
    gridErrorSeconds: event?.gridErrorSeconds,
  });
}

const args = parseArgs(process.argv);
const raw = JSON.parse(await readFile(args.input, 'utf8'));
const baseEvents = Array.isArray(raw.baseEvents) ? raw.baseEvents : [];
const events = Array.isArray(raw.events) ? raw.events : [];
const diagnostics =
  raw.techniqueDiagnostics && typeof raw.techniqueDiagnostics === 'object'
    ? raw.techniqueDiagnostics
    : {};

let identityPreservedCount = 0;
let baseTechniqueFreeCount = 0;
let techniqueEventCount = 0;
let techniqueLabelCount = 0;
let consensusTechniqueLabelCount = 0;
let allowedTechniqueLabelCount = 0;
let forbiddenTechniqueLabelCount = 0;
const observedTechniqueCounts = {};
const observedFamilyCounts = {};

for (let index = 0; index < Math.max(baseEvents.length, events.length); index += 1) {
  const base = baseEvents[index];
  const event = events[index];
  if (base && event && canonicalIdentity(base) === canonicalIdentity(event)) {
    identityPreservedCount += 1;
  }

  const baseTechniques = Array.isArray(base?.techniques) ? base.techniques : [];
  if (base && baseTechniques.length === 0) baseTechniqueFreeCount += 1;

  const techniques = Array.isArray(event?.techniques)
    ? [...new Set(event.techniques.map((value) => String(value || '').trim().toLowerCase()).filter(Boolean))]
    : [];
  const evidence = Array.isArray(event?.bassTechniqueEvidence)
    ? event.bassTechniqueEvidence.filter((row) => row && typeof row === 'object')
    : [];

  if (techniques.length) techniqueEventCount += 1;
  for (const technique of techniques) {
    techniqueLabelCount += 1;
    observedTechniqueCounts[technique] = (observedTechniqueCounts[technique] || 0) + 1;
    if (ALLOWED_TECHNIQUES.has(technique)) allowedTechniqueLabelCount += 1;
    if (FORBIDDEN_UNPROVEN_TECHNIQUES.has(technique)) forbiddenTechniqueLabelCount += 1;

    const matching = evidence.find(
      (row) =>
        String(row.type || '').trim().toLowerCase() === technique &&
        row.consensusPassed === true &&
        Number(row.viewAgreement) >= REQUIRED_VIEW_AGREEMENT &&
        Number(row.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
        row.referenceFree === true &&
        row.professionalReferenceUsed === false &&
        row.runtimeLabelsRequired === false
    );
    if (matching) {
      consensusTechniqueLabelCount += 1;
      const family = String(matching.family || '').trim();
      if (family) observedFamilyCounts[family] = (observedFamilyCounts[family] || 0) + 1;
    }
  }
}

const eventCount = events.length;
const identityPreservationPercent = eventCount
  ? Number(((identityPreservedCount / eventCount) * 100).toFixed(2))
  : 0;
const consensusTechniquePercent = techniqueLabelCount
  ? Number(((consensusTechniqueLabelCount / techniqueLabelCount) * 100).toFixed(2))
  : 0;
const techniqueEventPercent = eventCount
  ? Number(((techniqueEventCount / eventCount) * 100).toFixed(2))
  : 0;
const qualityReport = buildBassProfessionalQualityReport(events);
const provenFamilies = Object.keys(observedFamilyCounts)
  .filter((family) => observedFamilyCounts[family] > 0)
  .sort();
const initialFamilies = ['slide', 'hammer_on', 'pull_off', 'mute', 'harmonic', 'sustain'];
const unprovenInitialFamilies = initialFamilies.filter((family) => !provenFamilies.includes(family));

const boundaryChecks = {
  approvedFixture: raw.approvedFixture === 'public/gomywayfullaitest.m4a',
  referenceFree: raw.referenceFree === true,
  crossViewConsensusRequired:
    raw.crossViewConsensusRequired === true && Number(raw.requiredConsensusViews) === 2,
  noteTimingPlayabilityPrecondition: raw.noteTimingPlayabilityPreconditionPassed === true,
  eventCountStable: baseEvents.length > 0 && baseEvents.length === events.length,
  baseTechniqueFree: baseEvents.length > 0 && baseTechniqueFreeCount === baseEvents.length,
  identityPreserved: eventCount > 0 && identityPreservedCount === eventCount,
  minimumTechniqueEvents: techniqueEventCount >= MINIMUM_TECHNIQUE_EVENTS,
  allowedTechniqueLabelsOnly:
    techniqueLabelCount > 0 && allowedTechniqueLabelCount === techniqueLabelCount,
  noForbiddenUnprovenLabels: forbiddenTechniqueLabelCount === 0,
  everyTechniqueHasTwoViewEvidence:
    techniqueLabelCount > 0 && consensusTechniqueLabelCount === techniqueLabelCount,
  diagnosticsAgree:
    Number(diagnostics.eventCount) === eventCount &&
    Number(diagnostics.techniqueEventCount) === techniqueEventCount &&
    Number(diagnostics.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT,
  harmonicRemainsUnimplemented:
    raw.harmonicEvidenceImplemented === false &&
    diagnostics.harmonicEvidenceImplemented === false,
  highRiskFamiliesRemainDisabled:
    raw.futureHighRiskFamiliesEnabled === false &&
    diagnostics.futureHighRiskFamiliesEnabled === false,
  qualityGateStillPassed: qualityReport.passed === true,
  professionalBassNotClaimed: raw.professionalBassComplete === false,
};

const safetyChecks = {
  trainingDisabled: raw.trainingRunAuthorized === false,
  routingDisabled: raw.analyzerRoutingEnabled === false,
  structuredIdentityDisabled: raw.professionalStructuredIdentityEnabled === false,
  pdfDisabled: raw.pdfRendererEnabled === false,
  liveEndpointUnchanged: raw.liveEndpointDeployedOrModified === false,
  vercelNotAttempted: raw.vercelDeploymentAttempted === false,
  productionUnchanged: raw.productionModified === false,
  promotionDisabled: raw.productionPromotionAuthorized === false,
  purchaseNotAttempted: raw.paidPurchaseAttempted === false,
  tokenNotRedeemed: raw.customerTokenRedeemed === false,
  emailNotSent: raw.customerEmailSent === false,
};

const passed =
  Object.values(boundaryChecks).every(Boolean) &&
  Object.values(safetyChecks).every(Boolean);

const evidence = {
  schemaVersion: 1,
  gate: 'bass-real-audio-reference-free-technique-evidence',
  approvedFixture: raw.approvedFixture,
  sourceSha256: raw.sourceSha256,
  sourceBytes: raw.sourceBytes,
  eventCount,
  identityPreservedEventCount: identityPreservedCount,
  identityPreservationPercent,
  techniqueEventCount,
  techniqueEventPercent,
  techniqueLabelCount,
  consensusTechniqueLabelCount,
  consensusTechniquePercent,
  observedTechniqueCounts,
  observedTechniqueFamilyCounts: observedFamilyCounts,
  provenTechniqueFamilies: provenFamilies,
  unprovenInitialTechniqueFamilies: unprovenInitialFamilies,
  allInitialTechniqueFamiliesProven: unprovenInitialFamilies.length === 0,
  thresholds: {
    minimumTechniqueEvents: MINIMUM_TECHNIQUE_EVENTS,
    requiredViewAgreement: REQUIRED_VIEW_AGREEMENT,
    requiredIdentityPreservationPercent: 100,
    requiredConsensusTechniquePercent: 100,
  },
  qualityThresholds: DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  qualityReport,
  boundaryChecks,
  safetyChecks,
  bassTechniqueEvidenceBoundaryPassed: passed,
  techniqueEvidenceGenerated: techniqueEventCount > 0,
  harmonicEvidenceImplemented: false,
  futureHighRiskFamiliesEnabled: false,
  professionalBassComplete: false,
  trainingRunAuthorized: false,
  analyzerRoutingEnabled: false,
  professionalStructuredIdentityEnabled: false,
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
  console.log('BASS REAL-AUDIO REFERENCE-FREE TECHNIQUE EVIDENCE PASSED');
}
