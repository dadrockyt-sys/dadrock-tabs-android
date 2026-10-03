const DUPLICATE_STATES = new Set([
  'duplicate_guitar_candidate',
  'duplicate_bass_candidate',
]);

const CRITICAL_PAIR_STATES = new Set([
  ...DUPLICATE_STATES,
  'missing_or_silent_member',
]);

function clone(value) {
  return value === undefined ? undefined : structuredClone(value);
}

function pushUnique(target, code) {
  if (typeof code === 'string' && code && !target.includes(code)) target.push(code);
}

function eventIdentity(event) {
  return [
    event?.evidenceOnsetId ?? '',
    event?.start ?? '',
    event?.midi ?? '',
  ].join('|');
}

function assertEventsUnchanged(label, events, sourceEvents) {
  const source = new Map(sourceEvents.map((event) => [eventIdentity(event), event]));
  for (const event of events) {
    const original = source.get(eventIdentity(event));
    if (!original) throw new Error(`${label} contains an event outside pitch-resolved evidence.`);
    if (Number(event.midi) !== Number(original.midi)
        || Number(event.start) !== Number(original.start)) {
      throw new Error(`${label} altered pitch or onset identity.`);
    }
  }
}

export function buildTranscriptionUncertaintyPresentation({
  evidenceEvaluation = {},
  eventExposure = {},
  pairContext = null,
  crossStemDiagnostics = null,
  provenance = {},
} = {}) {
  const exposureContract = eventExposure?.exposureContract ?? {};
  if (exposureContract.referenceBlind !== true || exposureContract.structureFrozen !== true) {
    throw new Error('UNCERTAINTY_PRESENTATION_REQUIRES_FROZEN_REFERENCE_BLIND_EXPOSURE');
  }

  const pitchResolvedEvents = Array.isArray(eventExposure?.pitchResolvedEvents)
    ? eventExposure.pitchResolvedEvents.map(clone)
    : [];
  const roleAcceptedEvents = Array.isArray(eventExposure?.roleAcceptedEvents)
    ? eventExposure.roleAcceptedEvents.map(clone)
    : [];
  const completeTabEligibleEvents = Array.isArray(eventExposure?.completeTabEligibleEvents)
    ? eventExposure.completeTabEligibleEvents.map(clone)
    : [];

  assertEventsUnchanged('roleAcceptedEvents', roleAcceptedEvents, pitchResolvedEvents);
  assertEventsUnchanged('completeTabEligibleEvents', completeTabEligibleEvents, pitchResolvedEvents);

  const reasonCodes = [];
  const evaluatorFailures = Array.isArray(evidenceEvaluation?.failureReasons)
    ? evidenceEvaluation.failureReasons
    : [];
  for (const code of evaluatorFailures) pushUnique(reasonCodes, code);

  const pairState = typeof pairContext?.state === 'string' ? pairContext.state : null;
  if (DUPLICATE_STATES.has(pairState)) {
    pushUnique(reasonCodes, 'PAIR_ROLE_AMBIGUITY_DUPLICATE_CLASS_CANDIDATE');
  } else if (pairState === 'missing_or_silent_member') {
    pushUnique(reasonCodes, 'PAIR_MEMBER_MISSING_OR_SILENT');
  } else if (pairState === 'ambiguous_pair') {
    pushUnique(reasonCodes, 'PAIR_ROLE_RELATIONSHIP_AMBIGUOUS');
  }

  const crossStemDescriptiveOnly = crossStemDiagnostics?.descriptiveOnly === true;
  if (crossStemDiagnostics && crossStemDescriptiveOnly !== true) {
    throw new Error('CROSS_STEM_DIAGNOSTICS_MUST_BE_DESCRIPTIVE_ONLY');
  }

  const evaluatorAccepted = evidenceEvaluation?.acceptedForCompleteTab === true;
  const pairBlocksCompleteTab = CRITICAL_PAIR_STATES.has(pairState)
    || pairState === 'ambiguous_pair';
  const completeTabEligible = evaluatorAccepted
    && !pairBlocksCompleteTab
    && completeTabEligibleEvents.length > 0;

  let presentationState;
  if (completeTabEligible) presentationState = 'complete_tab_eligible';
  else if (pitchResolvedEvents.length > 0) presentationState = 'evidence_visible_review_required';
  else presentationState = 'no_reliable_note_evidence';

  return {
    uncertaintyContract: {
      name: 'astra-transcription-uncertainty-presentation',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      descriptiveOnly: true,
      confidenceScoreDefined: false,
      confidenceScore: null,
      automaticCorrectionAuthorized: false,
      automaticStemMutationAuthorized: false,
      automaticRoleReassignmentAuthorized: false,
      thresholdsLearnedFromS0: false,
    },
    presentationState,
    completeTabEligible,
    reasonCodes,
    role: eventExposure?.role ?? null,
    structureIdentity: clone(eventExposure?.structureIdentity ?? null),
    evidence: {
      pitchResolvedEvents,
      roleAcceptedEvents,
      completeTabEligibleEvents: completeTabEligible
        ? completeTabEligibleEvents
        : [],
    },
    diagnostics: {
      pairContext: clone(pairContext),
      crossStemDiagnostics: clone(crossStemDiagnostics),
      evaluatorDiagnostics: clone(evidenceEvaluation?.diagnostics ?? {}),
    },
    provenance: clone(provenance),
    guidance: {
      noteIdentityPreserved: true,
      uncertainEvidenceHidden: false,
      reviewRequired: !completeTabEligible,
      messageCode: completeTabEligible
        ? 'TRANSCRIPTION_EVIDENCE_ELIGIBLE'
        : (pitchResolvedEvents.length > 0
          ? 'TRANSCRIPTION_EVIDENCE_REVIEW_REQUIRED'
          : 'TRANSCRIPTION_EVIDENCE_UNAVAILABLE'),
    },
  };
}
