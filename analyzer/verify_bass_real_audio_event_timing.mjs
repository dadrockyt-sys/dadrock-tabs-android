import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  buildBassProfessionalQualityReport,
} from '../lib/bassProfessionalQuality.js';
import { projectBassProfessionalRenderEvents } from '../lib/bassProfessionalRenderContract.js';

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
    throw new Error('Usage: node verify_bass_real_audio_event_timing.mjs --input <json> --output <json>');
  }
  return out;
}

function finiteNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function unique(values) {
  return [...new Set(values)];
}

const args = parseArgs(process.argv);
const raw = JSON.parse(await readFile(args.input, 'utf8'));
const events = Array.isArray(raw.events) ? raw.events : [];
const timing = raw.timing && typeof raw.timing === 'object' ? raw.timing : {};
const candidateDiagnostics =
  raw.candidateDiagnostics && typeof raw.candidateDiagnostics === 'object'
    ? raw.candidateDiagnostics
    : {};

const qualityReport = buildBassProfessionalQualityReport(events);
const projected = projectBassProfessionalRenderEvents(events);
const uniqueMeasures = unique(
  projected.map((event) => event.measure).filter((measure) => Number.isInteger(measure))
).length;

const consensusEvents = events.filter((event) => {
  const sources = Array.isArray(event?.sources) ? event.sources.map(String) : [];
  return (
    Number(event?.sourceCount) >= 2 &&
    sources.includes('direct') &&
    sources.includes('cascade')
  );
}).length;

const techniqueFreeEvents = events.filter(
  (event) => Array.isArray(event?.techniques) && event.techniques.length === 0
).length;

const bassRangeEvents = events.filter((event) => {
  const midi = finiteNumber(event?.midi);
  return midi !== null && midi >= 28 && midi <= 67;
}).length;

const gridErrorEvents = events.filter((event) => {
  const gridError = finiteNumber(event?.gridErrorSeconds);
  return gridError !== null && gridError >= 0 && gridError <= 0.1;
}).length;

const tempoBpm = finiteNumber(timing.tempoBpm);
const beatCount = Number(timing.beatCount || 0);
const eventCount = events.length;

const boundaryChecks = {
  approvedFixture: raw.approvedFixture === 'public/gomywayfullaitest.m4a',
  referenceFree: raw.referenceFree === true && timing.referenceFree === true,
  crossViewConsensusRequired:
    raw.crossViewConsensusRequired === true && Number(raw.requiredConsensusViews) === 2,
  candidateNoteTimingGenerated: raw.candidateNoteTimingGenerated === true,
  eventCountMinimum: eventCount >= DEFAULT_BASS_PROFESSIONAL_THRESHOLDS.minimumValidRenderEvents,
  consensusCoverage: eventCount > 0 && consensusEvents === eventCount,
  bassRangeCoverage: eventCount > 0 && bassRangeEvents === eventCount,
  gridErrorCoverage: eventCount > 0 && gridErrorEvents === eventCount,
  techniqueBoundaryPreserved: eventCount > 0 && techniqueFreeEvents === eventCount,
  timingBeatCount: beatCount >= 8,
  timingTempoRange: tempoBpm !== null && tempoBpm >= 55 && tempoBpm <= 210,
  timingMeter:
    Number(timing.meterNumerator) === 4 && Number(timing.meterDenominator) === 4,
  multipleMeasures: uniqueMeasures >= 2,
  requiredConsensusDiagnostics:
    Number(candidateDiagnostics.requiredConsensusViews) === 2,
  bassMidiDiagnostics:
    Number(candidateDiagnostics.bassMidiMinimum) === 28 &&
    Number(candidateDiagnostics.bassMidiMaximum) === 67,
  qualityGatePassed: qualityReport.passed === true,
  techniqueQualityNotClaimed: raw.techniqueQualityProven === false,
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
  gate: 'bass-real-audio-candidate-note-timing-playability',
  approvedFixture: raw.approvedFixture,
  sourceSha256: raw.sourceSha256,
  sourceBytes: raw.sourceBytes,
  separator: raw.separator,
  timing,
  candidateDiagnostics,
  eventCount,
  projectedRenderEventCount: projected.length,
  uniqueMeasures,
  consensusEventCount: consensusEvents,
  bassRangeEventCount: bassRangeEvents,
  gridErrorAuthenticatedEventCount: gridErrorEvents,
  techniqueFreeEventCount: techniqueFreeEvents,
  qualityThresholds: DEFAULT_BASS_PROFESSIONAL_THRESHOLDS,
  qualityReport,
  boundaryChecks,
  safetyChecks,
  realAudioBassCandidateTimingPassed: passed,
  noteTimingPlayabilityBoundaryPassed: passed,
  techniqueQualityProven: false,
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
  console.log('BASS REAL-AUDIO CANDIDATE / NOTE / TIMING / PLAYABILITY PASSED');
}
