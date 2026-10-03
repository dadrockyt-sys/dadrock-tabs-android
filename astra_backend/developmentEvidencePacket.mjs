import { adaptStructureConditionedNoteEvidence } from './noteEvidenceAdapter.mjs';
import { evaluateNoteEvidence } from './noteEvidenceEvaluator.mjs';
import { buildNoteEventExposure } from './noteEventExposure.mjs';
import { buildTranscriptionUncertaintyPresentation } from './transcriptionUncertaintyPresentation.mjs';

function clone(value) {
  return value === undefined ? undefined : structuredClone(value);
}

function eventIdentity(event) {
  return [
    event?.evidenceOnsetId ?? '',
    event?.start ?? '',
    event?.midi ?? '',
  ].join('|');
}

function assertExactIdentity(label, candidateEvents, sourceEvents) {
  const source = new Map(sourceEvents.map((event) => [eventIdentity(event), event]));
  for (const event of candidateEvents) {
    const original = source.get(eventIdentity(event));
    if (!original) {
      throw new Error(`${label} contains an event not present in adapted promoted evidence.`);
    }
    if (Number(event.midi) !== Number(original.midi)
        || Number(event.start) !== Number(original.start)) {
      throw new Error(`${label} altered MIDI or onset identity.`);
    }
  }
}

function assertNoHiddenAutomation(packet) {
  const contract = packet?.presentation?.uncertaintyContract ?? {};
  if (contract.confidenceScoreDefined !== false || contract.confidenceScore !== null) {
    throw new Error('END_TO_END_PACKET_FORBIDS_COMPOSITE_CONFIDENCE_SCORE');
  }
  if (contract.automaticCorrectionAuthorized !== false
      || contract.automaticStemMutationAuthorized !== false
      || contract.automaticRoleReassignmentAuthorized !== false) {
    throw new Error('END_TO_END_PACKET_FORBIDS_AUTOMATIC_CORRECTION');
  }
}

export function buildDevelopmentEvidencePacket({
  rawNoteEvidence,
  structureMap,
  pairContext = null,
  crossStemDiagnostics = null,
  provenance = {},
} = {}) {
  if (!rawNoteEvidence || typeof rawNoteEvidence !== 'object') {
    throw new Error('rawNoteEvidence is required.');
  }
  if (!structureMap || typeof structureMap !== 'object') {
    throw new Error('structureMap is required.');
  }

  const adaptedEvidence = adaptStructureConditionedNoteEvidence(rawNoteEvidence, structureMap);
  const evidenceEvaluation = evaluateNoteEvidence(adaptedEvidence);
  const eventExposure = buildNoteEventExposure(adaptedEvidence, evidenceEvaluation);
  const presentation = buildTranscriptionUncertaintyPresentation({
    evidenceEvaluation,
    eventExposure,
    pairContext,
    crossStemDiagnostics,
    provenance,
  });

  const promoted = adaptedEvidence.promotedEvents ?? [];
  const exposedPitchResolved = eventExposure.pitchResolvedEvents ?? [];
  const presentedPitchResolved = presentation?.evidence?.pitchResolvedEvents ?? [];
  const presentedRoleAccepted = presentation?.evidence?.roleAcceptedEvents ?? [];
  const presentedComplete = presentation?.evidence?.completeTabEligibleEvents ?? [];

  assertExactIdentity('eventExposure.pitchResolvedEvents', exposedPitchResolved, promoted);
  assertExactIdentity('presentation.pitchResolvedEvents', presentedPitchResolved, promoted);
  assertExactIdentity('presentation.roleAcceptedEvents', presentedRoleAccepted, promoted);
  assertExactIdentity('presentation.completeTabEligibleEvents', presentedComplete, promoted);

  const packet = {
    packetContract: {
      name: 'astra-development-end-to-end-note-evidence-packet',
      version: 1,
      developmentOnly: true,
      productionDeliveryAuthorized: false,
      referenceBlind: true,
      structureFrozen: true,
      exactMidiAndOnsetIdentityRequired: true,
      confidenceScoreDefined: false,
      automaticCorrectionAuthorized: false,
      automaticStemMutationAuthorized: false,
      automaticRoleReassignmentAuthorized: false,
      thresholdsLearnedFromS0: false,
    },
    role: adaptedEvidence.role,
    structureIdentity: clone(adaptedEvidence.structureIdentity),
    adaptedEvidence,
    evidenceEvaluation,
    eventExposure,
    pairContext: clone(pairContext),
    crossStemDiagnostics: clone(crossStemDiagnostics),
    presentation,
    provenance: clone(provenance),
    invariants: {
      adaptedPromotedEventCount: promoted.length,
      exposurePitchResolvedEventCount: exposedPitchResolved.length,
      presentationPitchResolvedEventCount: presentedPitchResolved.length,
      exactMidiAndOnsetIdentityPreserved: true,
      confidenceScoreAbsent: true,
      automaticCorrectionAbsent: true,
    },
  };

  assertNoHiddenAutomation(packet);

  return packet;
}
