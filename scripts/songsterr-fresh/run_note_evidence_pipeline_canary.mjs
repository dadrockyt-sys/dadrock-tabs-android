#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { runFreshDeterministicPipeline } from '../../songsterr_pipeline/deterministicPipeline.mjs';
import { buildNoteEventExposure } from '../../songsterr_pipeline/noteEventExposure.mjs';
import { evaluateNoteEvidence } from '../../songsterr_pipeline/noteEvidenceEvaluator.mjs';
import { buildStructureIdentity } from '../../songsterr_pipeline/structureIdentity.mjs';

const [structureArg, noteEvidenceArg, outputArg] = process.argv.slice(2);
if (!structureArg || !noteEvidenceArg || !outputArg) {
  throw new Error('Usage: run_note_evidence_pipeline_canary.mjs <adapted-structure.json> <adapted-note-evidence.json> <output.json>');
}

const structureResult = JSON.parse(await readFile(resolve(structureArg), 'utf8'));
const noteEvidence = JSON.parse(await readFile(resolve(noteEvidenceArg), 'utf8'));
const structureMap = structureResult?.structureMap;
if (!structureMap) throw new Error('REAL_NOTE_CANARY_STRUCTURE_MAP_MISSING');
if (structureResult?.structureAcceptance?.accepted !== true) {
  throw new Error('REAL_NOTE_CANARY_STRUCTURE_NOT_ACCEPTED');
}

const identity = buildStructureIdentity(structureMap);
if (identity.signature !== noteEvidence?.structureIdentity?.signature) {
  throw new Error('REAL_NOTE_CANARY_STRUCTURE_IDENTITY_MISMATCH');
}
if (noteEvidence?.adapterContract?.structureIdentityVerified !== true) {
  throw new Error('REAL_NOTE_CANARY_NOTE_EVIDENCE_NOT_VERIFIED');
}
if (noteEvidence?.adapterContract?.referenceBlind !== true) {
  throw new Error('REAL_NOTE_CANARY_NOTE_EVIDENCE_NOT_REFERENCE_BLIND');
}
if (noteEvidence?.adapterContract?.modelInvoked !== false
  || noteEvidence?.adapterContract?.gpuInvoked !== false
  || noteEvidence?.adapterContract?.legacyV143ScorerImported !== false) {
  throw new Error('REAL_NOTE_CANARY_PROVENANCE_BOUNDARY_VIOLATION');
}

const evidenceEvaluation = evaluateNoteEvidence(noteEvidence);
const eventExposure = buildNoteEventExposure(noteEvidence, evidenceEvaluation);

// Diagnostic downstream exercise only: pitch-resolved events remain visible so exact
// MIDI/fretboard/rhythm behavior can be inspected. They are NOT role-accepted or
// customer-eligible unless the upstream evidence contract says so.
const sourceEvents = eventExposure.pitchResolvedEvents.map((event) => {
  const source = {
    start: event.start,
    midi: event.midi,
  };
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
    difficulty: 'unrated-real-audio-canary',
    upstreamEvidenceReady: evidenceEvaluation.acceptedForCompleteTab,
    upstreamEvidenceBlockers: evidenceEvaluation.failureReasons,
  },
});

const output = {
  contract: {
    name: 'songsterr-fresh-real-note-evidence-pipeline-canary',
    version: 3,
    referenceBlind: true,
    structureFrozen: true,
    structureIdentity: identity,
    noteAcceptanceOwnedBy: evidenceEvaluation.evaluatorContract.name,
    eventExposureOwnedBy: eventExposure.exposureContract.name,
    diagnosticPipelineUses: 'pitchResolvedEvents',
    customerEligibilityUses: 'completeTabEligibleEvents',
    modelInvoked: false,
    gpuInvoked: false,
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
