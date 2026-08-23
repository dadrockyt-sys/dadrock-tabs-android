import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  buildBassProfessionalQualityReport,
  DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
} from '../lib/bassProfessionalQuality.js';

const REQUIRED_VIEW_AGREEMENT = 2;
const MINIMUM_SUBSET_TECHNIQUE_EVENTS = 4;
const ALLOWED_TECHNIQUES = new Set([
  'slide-up',
  'slide-down',
  'hammer-on',
  'pull-off',
  'mute',
  'sustain',
  'harmonic',
]);
const HIGH_RISK_UNPROVEN_TECHNIQUES = new Set([
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
    throw new Error('Usage: node verify_bass_real_audio_harmonics.mjs --input <json> --output <json>');
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

function normalizedLabels(event) {
  return Array.isArray(event?.techniques)
    ? [...new Set(event.techniques.map((value) => String(value || '').trim().toLowerCase()).filter(Boolean))]
    : [];
}

const args = parseArgs(process.argv);
const raw = JSON.parse(await readFile(args.input, 'utf8'));
const baseEvents = Array.isArray(raw.baseEvents) ? raw.baseEvents : [];
const subsetEvents = Array.isArray(raw.subsetEvents) ? raw.subsetEvents : [];
const events = Array.isArray(raw.events) ? raw.events : [];
const subsetDiagnostics =
  raw.subsetTechniqueDiagnostics && typeof raw.subsetTechniqueDiagnostics === 'object'
    ? raw.subsetTechniqueDiagnostics
    : {};
const harmonicDiagnostics =
  raw.harmonicDiagnostics && typeof raw.harmonicDiagnostics === 'object'
    ? raw.harmonicDiagnostics
    : {};
const harmonicThresholds =
  harmonicDiagnostics.thresholds && typeof harmonicDiagnostics.thresholds === 'object'
    ? harmonicDiagnostics.thresholds
    : {};

let baseToSubsetIdentityCount = 0;
let subsetToFinalIdentityCount = 0;
let baseTechniqueFreeCount = 0;
let subsetLabelsPreservedCount = 0;
let allowedTechniqueLabelCount = 0;
let highRiskTechniqueLabelCount = 0;
let harmonicEventCount = 0;
let harmonicLabelCount = 0;
let consensusHarmonicLabelCount = 0;
let unexpectedAddedLabelCount = 0;
const observedTechniqueCounts = {};
const observedFamilyCounts = {};

for (let index = 0; index < Math.max(baseEvents.length, subsetEvents.length, events.length); index += 1) {
  const base = baseEvents[index];
  const subset = subsetEvents[index];
  const event = events[index];

  if (base && subset && canonicalIdentity(base) === canonicalIdentity(subset)) {
    baseToSubsetIdentityCount += 1;
  }
  if (subset && event && canonicalIdentity(subset) === canonicalIdentity(event)) {
    subsetToFinalIdentityCount += 1;
  }

  const baseLabels = normalizedLabels(base);
  if (base && baseLabels.length === 0) baseTechniqueFreeCount += 1;

  const subsetLabels = normalizedLabels(subset);
  const finalLabels = normalizedLabels(event);
  const subsetPreserved = subsetLabels.every((label) => finalLabels.includes(label));
  if (subset && event && subsetPreserved) subsetLabelsPreservedCount += 1;

  for (const label of finalLabels) {
    observedTechniqueCounts[label] = (observedTechniqueCounts[label] || 0) + 1;
    if (ALLOWED_TECHNIQUES.has(label)) allowedTechniqueLabelCount += 1;
    if (HIGH_RISK_UNPROVEN_TECHNIQUES.has(label)) highRiskTechniqueLabelCount += 1;
    if (!subsetLabels.includes(label) && label !== 'harmonic') unexpectedAddedLabelCount += 1;
  }

  if (finalLabels.includes('harmonic')) {
    harmonicEventCount += 1;
    harmonicLabelCount += 1;
    const evidence = Array.isArray(event?.bassTechniqueEvidence)
      ? event.bassTechniqueEvidence.filter((row) => row && typeof row === 'object')
      : [];
    const matching = evidence.find(
      (row) =>
        String(row.type || '').trim().toLowerCase() === 'harmonic' &&
        String(row.family || '').trim().toLowerCase() === 'harmonic' &&
        row.consensusPassed === true &&
        Number(row.viewAgreement) >= REQUIRED_VIEW_AGREEMENT &&
        Number(row.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
        row.referenceFree === true &&
        row.professionalReferenceUsed === false &&
        row.runtimeLabelsRequired === false &&
        String(row.detector || '').includes('v2-strict') &&
        Array.isArray(row.views) &&
        row.views.length >= REQUIRED_VIEW_AGREEMENT &&
        row.views.every(
          (view) =>
            view &&
            view.type === 'harmonic' &&
            view.referenceFree === true &&
            view.mappedNodeMatched === true &&
            Number(view.tonalPurity) >= Number(harmonicThresholds.minimumTonalPurity) &&
            Number(view.upperPartialRatio) >= Number(harmonicThresholds.minimumUpperPartialRatio) &&
            Number(view.subharmonicRatio) <= Number(harmonicThresholds.maximumSubharmonicRatio) &&
            Number(view.onsetStrength) <= Number(harmonicThresholds.maximumOnsetStrength) &&
            Number(view.durationSeconds) >= Number(harmonicThresholds.minimumDurationSeconds) &&
            Array.isArray(view.naturalHarmonicSources) &&
            view.naturalHarmonicSources.length > 0
        )
    );
    if (matching) consensusHarmonicLabelCount += 1;
  }
}

const finalLabelCount = Object.values(observedTechniqueCounts).reduce((sum, count) => sum + count, 0);
const baseToSubsetIdentityPercent = subsetEvents.length
  ? Number(((baseToSubsetIdentityCount / subsetEvents.length) * 100).toFixed(2))
  : 0;
const subsetToFinalIdentityPercent = events.length
  ? Number(((subsetToFinalIdentityCount / events.length) * 100).toFixed(2))
  : 0;
const harmonicConsensusPercent = harmonicLabelCount
  ? Number(((consensusHarmonicLabelCount / harmonicLabelCount) * 100).toFixed(2))
  : 100;
const qualityReport = buildBassProfessionalQualityReport(events);

const subsetFamilies = Array.isArray(subsetDiagnostics.provenTechniqueFamilies)
  ? subsetDiagnostics.provenTechniqueFamilies.map((value) => String(value || '').trim())
  : [];
for (const family of subsetFamilies) {
  if (family) observedFamilyCounts[family] = Number(subsetDiagnostics.techniqueFamilyCounts?.[family] || 0);
}
if (harmonicEventCount > 0) observedFamilyCounts.harmonic = harmonicEventCount;

const safeAbstention = harmonicEventCount === 0;
const harmonicFamilyProven = harmonicEventCount > 0 && consensusHarmonicLabelCount === harmonicLabelCount;

const boundaryChecks = {
  approvedFixture: raw.approvedFixture === 'public/gomywayfullaitest.m4a',
  referenceFree: raw.referenceFree === true,
  crossViewConsensusRequired:
    raw.crossViewConsensusRequired === true && Number(raw.requiredConsensusViews) === REQUIRED_VIEW_AGREEMENT,
  noteTimingPlayabilityPrecondition: raw.noteTimingPlayabilityPreconditionPassed === true,
  subsetTechniquePrecondition: raw.subsetTechniqueBoundaryPreconditionPassed === true,
  subsetDiagnosticSound:
    Number(subsetDiagnostics.eventCount) === subsetEvents.length &&
    Number(subsetDiagnostics.techniqueEventCount) >= MINIMUM_SUBSET_TECHNIQUE_EVENTS &&
    Number(subsetDiagnostics.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
    subsetDiagnostics.referenceFree === true &&
    subsetDiagnostics.futureHighRiskFamiliesEnabled === false,
  eventCountStable:
    baseEvents.length > 0 &&
    baseEvents.length === subsetEvents.length &&
    subsetEvents.length === events.length,
  baseTechniqueFree: baseEvents.length > 0 && baseTechniqueFreeCount === baseEvents.length,
  baseToSubsetIdentityPreserved:
    subsetEvents.length > 0 && baseToSubsetIdentityCount === subsetEvents.length,
  subsetToFinalIdentityPreserved:
    events.length > 0 && subsetToFinalIdentityCount === events.length,
  subsetLabelsPreserved:
    events.length > 0 && subsetLabelsPreservedCount === events.length,
  allowedTechniqueLabelsOnly:
    finalLabelCount > 0 && allowedTechniqueLabelCount === finalLabelCount,
  noUnexpectedAddedLabels: unexpectedAddedLabelCount === 0,
  highRiskFamiliesRemainDisabled:
    highRiskTechniqueLabelCount === 0 && raw.futureHighRiskFamiliesEnabled === false,
  harmonicImplemented:
    raw.harmonicEvidenceImplemented === true && harmonicDiagnostics.harmonicEvidenceImplemented === true,
  strictHarmonicDetector:
    String(harmonicDiagnostics.detector || '').includes('v2-strict') &&
    harmonicThresholds.mappedNaturalHarmonicNodeRequired === true,
  everyObservedHarmonicHasStrictTwoViewEvidence:
    harmonicLabelCount === 0 || consensusHarmonicLabelCount === harmonicLabelCount,
  harmonicDiagnosticsAgree:
    Number(harmonicDiagnostics.eventCount) === events.length &&
    Number(harmonicDiagnostics.harmonicEventCount) === harmonicEventCount &&
    Number(harmonicDiagnostics.requiredViewAgreement) === REQUIRED_VIEW_AGREEMENT &&
    harmonicDiagnostics.harmonicEvidenceObserved === (harmonicEventCount > 0) &&
    harmonicDiagnostics.harmonicFamilyProven === (harmonicEventCount > 0) &&
    harmonicDiagnostics.safeAbstention === safeAbstention,
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
  schemaVersion: 2,
  gate: 'bass-real-audio-reference-free-harmonic-diagnostic',
  approvedFixture: raw.approvedFixture,
  sourceSha256: raw.sourceSha256,
  sourceBytes: raw.sourceBytes,
  eventCount: events.length,
  baseToSubsetIdentityPreservedEventCount: baseToSubsetIdentityCount,
  baseToSubsetIdentityPreservationPercent: baseToSubsetIdentityPercent,
  subsetToFinalIdentityPreservedEventCount: subsetToFinalIdentityCount,
  subsetToFinalIdentityPreservationPercent: subsetToFinalIdentityPercent,
  harmonicEventCount,
  harmonicLabelCount,
  consensusHarmonicLabelCount,
  harmonicConsensusPercent,
  observedTechniqueCounts,
  observedTechniqueFamilyCounts: observedFamilyCounts,
  currentRunSubsetTechniqueFamilies: subsetFamilies,
  harmonicFamilyProven: passed && harmonicFamilyProven,
  safeAbstention: passed && safeAbstention,
  allInitialTechniqueFamiliesProven: false,
  thresholds: {
    minimumSubsetTechniqueEvents: MINIMUM_SUBSET_TECHNIQUE_EVENTS,
    requiredViewAgreement: REQUIRED_VIEW_AGREEMENT,
    requiredIdentityPreservationPercent: 100,
    requiredObservedHarmonicConsensusPercent: 100,
    harmonicDetector: harmonicThresholds,
  },
  qualityThresholds: DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  qualityReport,
  boundaryChecks,
  safetyChecks,
  bassHarmonicDiagnosticBoundaryPassed: passed,
  harmonicEvidenceImplemented: true,
  harmonicEvidenceObserved: harmonicEventCount > 0,
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
  console.log(
    harmonicFamilyProven
      ? 'BASS REAL-AUDIO STRICT HARMONIC EVIDENCE PASSED'
      : 'BASS REAL-AUDIO HARMONIC SAFE-ABSTENTION BOUNDARY PASSED'
  );
}
