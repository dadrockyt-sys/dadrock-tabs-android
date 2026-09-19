function cloneEvent(event) {
  return structuredClone(event);
}

function eventIdentity(event) {
  return `${event?.evidenceOnsetId ?? ''}|${event?.start ?? ''}|${event?.midi ?? ''}`;
}

function assertExactSubset(subset, superset, label) {
  const source = new Map(superset.map((event) => [eventIdentity(event), event]));
  for (const event of subset) {
    const original = source.get(eventIdentity(event));
    if (!original) throw new Error(`${label} contains an event not present in pitch-resolved evidence.`);
    if (Number(event.midi) !== Number(original.midi) || Number(event.start) !== Number(original.start)) {
      throw new Error(`${label} altered pitch or onset identity.`);
    }
  }
}

export function buildNoteEventExposure(adaptedEvidence = {}, evidenceEvaluation = null) {
  const contract = adaptedEvidence?.adapterContract ?? {};
  if (contract.structureIdentityVerified !== true) {
    throw new Error('NOTE_EVENT_EXPOSURE_STRUCTURE_IDENTITY_UNVERIFIED');
  }
  if (contract.referenceBlind !== true || contract.structureFrozen !== true) {
    throw new Error('NOTE_EVENT_EXPOSURE_REQUIRES_FROZEN_REFERENCE_BLIND_EVIDENCE');
  }

  const provisional = Array.isArray(adaptedEvidence?.promotedEvents)
    ? adaptedEvidence.promotedEvents.map(cloneEvent)
    : [];
  const pitchResolvedEvents = provisional;
  const roleRelevanceResolved = adaptedEvidence?.capabilities?.roleRelevanceResolved === true;
  const roleAcceptedEvents = roleRelevanceResolved ? provisional.map(cloneEvent) : [];
  const acceptedForCompleteTab = evidenceEvaluation?.acceptedForCompleteTab === true;
  const completeTabEligibleEvents = acceptedForCompleteTab ? roleAcceptedEvents.map(cloneEvent) : [];

  assertExactSubset(roleAcceptedEvents, pitchResolvedEvents, 'roleAcceptedEvents');
  assertExactSubset(completeTabEligibleEvents, pitchResolvedEvents, 'completeTabEligibleEvents');

  const blockers = [];
  if (!roleRelevanceResolved) blockers.push('ROLE_RELEVANCE_UNRESOLVED');
  if (!acceptedForCompleteTab) blockers.push('NOTE_EVIDENCE_NOT_ACCEPTED_FOR_COMPLETE_TAB');

  return {
    exposureContract: {
      name: 'songsterr-fresh-note-event-exposure',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      exactPitchIdentityRequired: true,
      legacyV143ScorerImported: false,
    },
    role: adaptedEvidence?.role ?? null,
    structureIdentity: adaptedEvidence?.structureIdentity
      ? structuredClone(adaptedEvidence.structureIdentity)
      : null,
    pitchResolvedEvents,
    roleAcceptedEvents,
    completeTabEligibleEvents,
    metrics: {
      pitchResolvedEventCount: pitchResolvedEvents.length,
      roleAcceptedEventCount: roleAcceptedEvents.length,
      completeTabEligibleEventCount: completeTabEligibleEvents.length,
    },
    blockers,
  };
}
