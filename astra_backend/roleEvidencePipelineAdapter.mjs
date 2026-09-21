import { adaptRoleEvidenceStreams } from './roleEvidenceIntegrationAdapter.mjs';
import { evaluateNoteEvidence } from './noteEvidenceEvaluator.mjs';
import { buildNoteEventExposure } from './noteEventExposure.mjs';
import { runFreshDeterministicPipeline } from './deterministicPipeline.mjs';

const ROLES = new Set(['lead', 'rhythm', 'bass']);

function require(condition, message) {
  if (!condition) throw new Error(message);
}

function sourceEvent(event) {
  const output = {
    midi: event.midi,
    start: event.start,
  };
  if (event.end !== undefined && event.end !== null) output.end = event.end;
  if (event.duration !== undefined && event.duration !== null) output.duration = event.duration;
  return output;
}

function eventEvidence(exposure, pipeline) {
  if (!pipeline) return [];
  const accepted = exposure.completeTabEligibleEvents;
  return pipeline.events.map((event) => {
    const source = accepted[event.sourceEventIndex];
    require(source, 'PIPELINE_SOURCE_EVENT_EVIDENCE_MISSING');
    return {
      sourceEventIndex: event.sourceEventIndex,
      evidenceOnsetId: source.evidenceOnsetId ?? null,
      midi: source.midi,
      start: source.start,
      evidenceState: source?.provenance?.evidenceState ?? null,
      evidenceProvenance: source?.provenance ? structuredClone(source.provenance) : {},
    };
  });
}

export function runRoleEvidenceDeterministicPipeline({
  requestedRole,
  roleEvidenceStatus,
  structureMap,
  streams = {},
  capabilities = {},
  provenance = {},
  instrumentConfig,
  productShell = {},
  onsetToleranceSeconds = 0.01,
  fretboardPathOptions = {},
} = {}) {
  require(ROLES.has(requestedRole), 'requestedRole must be lead, rhythm, or bass.');
  require(instrumentConfig && typeof instrumentConfig === 'object', 'instrumentConfig is required.');
  require(instrumentConfig.role === requestedRole, 'instrumentConfig.role must match requestedRole.');

  const adaptedEvidence = adaptRoleEvidenceStreams({
    requestedRole,
    roleEvidenceStatus,
    structureMap,
    streams,
    capabilities,
    provenance,
  });
  const evidenceEvaluation = evaluateNoteEvidence(adaptedEvidence);
  const exposure = buildNoteEventExposure(adaptedEvidence, evidenceEvaluation);

  const mayRunDeterministicPipeline = (
    evidenceEvaluation.acceptedForCompleteTab === true
    && exposure.completeTabEligibleEvents.length > 0
  );

  const pipeline = mayRunDeterministicPipeline
    ? runFreshDeterministicPipeline({
      events: exposure.completeTabEligibleEvents.map(sourceEvent),
      structureMap,
      instrumentConfig,
      onsetToleranceSeconds,
      fretboardPathOptions,
      productShell,
    })
    : null;

  const blockers = [...new Set([
    ...evidenceEvaluation.failureReasons,
    ...exposure.blockers,
    ...(pipeline ? [] : ['DETERMINISTIC_PIPELINE_NOT_RUN']),
  ])].sort();

  return {
    integrationContract: {
      name: 'astra-role-evidence-deterministic-pipeline',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      evidenceEvaluatorOwnsAcceptance: true,
      ambiguousEvidenceCanEnterDeterministicPipeline: false,
      unassignedEvidenceCanEnterDeterministicPipeline: false,
      customerDeliveryEligible: false,
    },
    requestedRole,
    roleEvidenceStatus,
    adaptedEvidence,
    evidenceEvaluation,
    exposure,
    pipeline,
    eventEvidence: eventEvidence(exposure, pipeline),
    blockers,
    customerDeliveryEligible: false,
  };
}
