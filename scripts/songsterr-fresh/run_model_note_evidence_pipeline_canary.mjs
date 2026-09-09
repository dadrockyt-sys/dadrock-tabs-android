#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { runFreshDeterministicPipeline } from '../../songsterr_pipeline/deterministicPipeline.mjs';
import { buildNoteEventExposure } from '../../songsterr_pipeline/noteEventExposure.mjs';
import { evaluateNoteEvidence } from '../../songsterr_pipeline/noteEvidenceEvaluator.mjs';
import { buildStructureIdentity } from '../../songsterr_pipeline/structureIdentity.mjs';

const [structureArg, noteEvidenceArg, outputArg] = process.argv.slice(2);
if (!structureArg || !noteEvidenceArg || !outputArg) {
  throw new Error(
    'Usage: run_model_note_evidence_pipeline_canary.mjs <adapted-structure.json> <adapted-note-evidence.json> <output.json>',
  );
}

const structureResult = JSON.parse(await readFile(resolve(structureArg), 'utf8'));
const noteEvidence = JSON.parse(await readFile(resolve(noteEvidenceArg), 'utf8'));
const structureMap = structureResult?.structureMap;
if (!structureMap) throw new Error('MODEL_NOTE_CANARY_STRUCTURE_MAP_MISSING');
if (structureResult?.structureAcceptance?.accepted !== true) {
  throw new Error('MODEL_NOTE_CANARY_STRUCTURE_NOT_ACCEPTED');
}

const identity = buildStructureIdentity(structureMap);
if (identity.signature !== noteEvidence?.structureIdentity?.signature) {
  throw new Error('MODEL_NOTE_CANARY_STRUCTURE_IDENTITY_MISMATCH');
}
if (noteEvidence?.adapterContract?.structureIdentityVerified !== true
  || noteEvidence?.adapterContract?.referenceBlind !== true) {
  throw new Error('MODEL_NOTE_CANARY_NOTE_EVIDENCE_NOT_VERIFIED');
}
if (noteEvidence?.adapterContract?.modelInvoked !== true) {
  throw new Error('MODEL_NOTE_CANARY_REQUIRES_MODEL_PROVENANCE');
}
if (noteEvidence?.adapterContract?.legacyV143ScorerImported !== false) {
  throw new Error('MODEL_NOTE_CANARY_LEGACY_BOUNDARY_VIOLATION');
}
if (noteEvidence?.provenance?.modelValidationComplete === true) {
  throw new Error('MODEL_NOTE_CANARY_MUST_BEGIN_VALIDATION_PENDING');
}

const evidenceEvaluation = evaluateNoteEvidence(noteEvidence);
for (const resolvedBlocker of [
  'ROLE_RELEVANCE_UNRESOLVED',
  'POLYPHONY_UNRESOLVED',
  'PITCH_EVIDENCE_UNRESOLVED',
]) {
  if (evidenceEvaluation.failureReasons.includes(resolvedBlocker)) {
    throw new Error(`MODEL_NOTE_CANARY_UNEXPECTED_${resolvedBlocker}`);
  }
}
if (!evidenceEvaluation.failureReasons.includes('MODEL_EVIDENCE_VALIDATION_PENDING')) {
  throw new Error('MODEL_NOTE_CANARY_MUST_FAIL_CLOSED_ON_VALIDATION_PENDING');
}

const eventExposure = buildNoteEventExposure(noteEvidence, evidenceEvaluation);
if (eventExposure.metrics.pitchResolvedEventCount <= 0) {
  throw new Error('MODEL_NOTE_CANARY_EXPECTS_PITCH_RESOLVED_EVENTS');
}
if (eventExposure.metrics.roleAcceptedEventCount !== eventExposure.metrics.pitchResolvedEventCount) {
  throw new Error('MODEL_NOTE_CANARY_ROLE_EXPOSURE_MUST_MATCH_RESOLVED_MODEL_NOTES');
}
if (eventExposure.metrics.completeTabEligibleEventCount !== 0) {
  throw new Error('MODEL_NOTE_CANARY_VALIDATION_PENDING_MUST_BLOCK_CUSTOMER_EVENTS');
}

const sourceEvents = eventExposure.pitchResolvedEvents.map((event) => {
  const source = { start: event.start, midi: event.midi };
  if (event.end !== undefined && event.end !== null) source.end = event.end;
  if (event.duration !== undefined && event.duration !== null) source.duration = event.duration;
  return source;
});

const pipelineResult = runFreshDeterministicPipeline({
  events: sourceEvents,
  structureMap,
  instrumentConfig: {
    role: 'lead',
    tuningMidi: [40, 45, 50, 55, 59, 64],
    capoFret: 0,
  },
  productShell: {
    transcriptionType: 'Guitar',
    difficulty: 'unrated-model-canary',
    upstreamEvidenceReady: evidenceEvaluation.acceptedForCompleteTab,
    upstreamEvidenceBlockers: evidenceEvaluation.failureReasons,
  },
});

if (pipelineResult.productShell?.payloadContract?.deliveryReady !== false) {
  throw new Error('MODEL_NOTE_CANARY_MUST_REMAIN_BLOCKED_FROM_DELIVERY');
}

const output = {
  contract: {
    name: 'songsterr-fresh-model-note-evidence-pipeline-canary',
    version: 1,
    referenceBlind: true,
    structureFrozen: true,
    structureIdentity: identity,
    noteAcceptanceOwnedBy: evidenceEvaluation.evaluatorContract.name,
    eventExposureOwnedBy: eventExposure.exposureContract.name,
    diagnosticPipelineUses: 'pitchResolvedEvents',
    customerEligibilityUses: 'completeTabEligibleEvents',
    modelInvoked: true,
    gpuInvoked: noteEvidence?.adapterContract?.gpuInvoked === true,
    legacyV143ScorerImported: false,
  },
  evidenceEvaluation,
  evidenceInventory: evidenceEvaluation.inventory,
  eventExposure: {
    contract: eventExposure.exposureContract,
    metrics: eventExposure.metrics,
    blockers: eventExposure.blockers,
  },
  pipelineSummary: {
    sourceEventCount: sourceEvents.length,
    pitchResolvedEventCount: eventExposure.metrics.pitchResolvedEventCount,
    roleAcceptedEventCount: eventExposure.metrics.roleAcceptedEventCount,
    completeTabEligibleEventCount: eventExposure.metrics.completeTabEligibleEventCount,
    finalEventCount: pipelineResult.events.length,
    exactMidiPreservedCount: pipelineResult.freshDiagnostics?.events?.exactMidiPreservedCount ?? null,
    unresolvedDurationCount: pipelineResult.freshDiagnostics?.rhythm?.unresolvedDurationCount ?? null,
    fretboardPathResolved: pipelineResult.fretboardPath?.resolved ?? null,
    rawIntegrityPassed: pipelineResult.freshDiagnostics?.passedRawIntegrityChecks ?? false,
    failures: pipelineResult.freshDiagnostics?.failures ?? [],
    upstreamEvidenceReady: pipelineResult.productShell?.payloadContract?.upstreamEvidenceReady ?? null,
    upstreamEvidenceBlockers: pipelineResult.productShell?.payloadContract?.upstreamEvidenceBlockers ?? [],
    rawResultReady: pipelineResult.productShell?.payloadContract?.rawResultReady ?? false,
    deliveryReady: pipelineResult.productShell?.payloadContract?.deliveryReady ?? false,
    structuredRenderEligible: pipelineResult.productShell?.payloadContract?.structuredRenderEligible ?? false,
  },
};

await writeFile(resolve(outputArg), `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify(output));
