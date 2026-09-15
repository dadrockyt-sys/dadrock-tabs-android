#!/usr/bin/env node

import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

import { adaptStructureConditionedNoteEvidence } from '../../songsterr_pipeline/noteEvidenceAdapter.mjs';
import { summarizeNoteEvidence } from '../../songsterr_pipeline/noteEvidenceDiagnostics.mjs';
import { evaluateNoteEvidence } from '../../songsterr_pipeline/noteEvidenceEvaluator.mjs';
import { buildStructureIdentity } from '../../songsterr_pipeline/structureIdentity.mjs';
import { buildStructureMap } from '../../songsterr_pipeline/structureMap.mjs';

const BUILDER = resolve('scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence.mjs');
const NOTE_SHA = 'a'.repeat(64);

const structureMap = buildStructureMap({
  durationSeconds: 5,
  tempoSegments: [{ start: 0, end: null, bpm: 120 }],
  meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
  feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  confidence: {
    overall: 1,
    tempo: 1,
    meter: 1,
    downbeats: 1,
    measures: 1,
    feel: 1,
  },
});
const structureIdentity = buildStructureIdentity(structureMap);

const context = {
  contract: 'songsterr-fresh-note-evidence-context-v1',
  version: 1,
  referenceBlind: true,
  structureFrozen: true,
  structureAcceptance: { accepted: true },
  structureIdentity,
  structureMap,
};

function makeModel(confidence40 = 0.79, confidence68 = 0.35) {
  return {
    contract: 'songsterr-fresh-basic-pitch-isolated-guitar-v1',
    version: 1,
    referenceBlind: true,
    role: 'guitar',
    notes: [
      {
        noteId: 'basic-pitch-note-000000',
        startSeconds: 0.011,
        diagnosticModelEndSeconds: 4.9,
        midi: 40,
        confidence: confidence40,
      },
      {
        noteId: 'basic-pitch-note-000001',
        startSeconds: 0.360,
        diagnosticModelEndSeconds: 1.53,
        midi: 68,
        confidence: confidence68,
      },
    ],
    noteInferenceIdentity: {
      contract: 'songsterr-fresh-basic-pitch-note-identity-v1',
      version: 1,
      algorithm: 'sha256',
      eventCount: 2,
      sha256: NOTE_SHA,
    },
    activationEvidenceIdentity: null,
    diagnostics: {
      modelNoteEndsUsedAsDuration: false,
      polyphonicStartClusterCount: 2,
      maxStartClusterSize: 1,
    },
    model: { package: 'basic-pitch', packageVersion: '0.4.0' },
    provenance: {
      modelInvoked: true,
      gpuInvoked: false,
      modelValidationComplete: true,
      separationSource: 'synthetic-unit-test-isolated-guitar',
      audioSource: 'synthetic-unit-test',
    },
  };
}

function makeQualification(secondStatus = 'rejected') {
  return {
    contract: 'songsterr-fresh-model-note-qualification-v1',
    version: 1,
    referenceBlind: true,
    modelNoteIdentitySha256: NOTE_SHA,
    method: 'synthetic-independent-onset-birth-fixture-v1',
    candidateConfidenceUsedForDecision: false,
    independentOfBasicPitchCandidateConfidence: true,
    referenceTabUsed: false,
    proposals: [
      {
        noteId: 'basic-pitch-note-000000',
        midi: 40,
        startSeconds: 0.011,
        status: 'corroborated',
        independentOnsetConfidence: 0.95,
        provenance: { reason: 'independent-birth-present' },
      },
      {
        noteId: 'basic-pitch-note-000001',
        midi: 68,
        startSeconds: 0.360,
        status: secondStatus,
        independentOnsetConfidence: secondStatus === 'rejected' ? 0.05 : 0.50,
        provenance: { reason: secondStatus === 'rejected' ? 'no-independent-birth' : 'insufficient-independent-evidence' },
      },
    ],
  };
}

async function runBuilder(root, label, model, qualification, expectSuccess = true) {
  const contextPath = join(root, `${label}-context.json`);
  const modelPath = join(root, `${label}-model.json`);
  const qualificationPath = join(root, `${label}-qualification.json`);
  const outputPath = join(root, `${label}-output.json`);
  await Promise.all([
    writeFile(contextPath, `${JSON.stringify(context, null, 2)}\n`),
    writeFile(modelPath, `${JSON.stringify(model, null, 2)}\n`),
    writeFile(qualificationPath, `${JSON.stringify(qualification, null, 2)}\n`),
  ]);

  const result = spawnSync(process.execPath, [BUILDER, contextPath, modelPath, qualificationPath, outputPath], {
    encoding: 'utf8',
  });
  if (expectSuccess) {
    assert.equal(result.status, 0, `${label} builder failed: ${result.stderr || result.stdout}`);
    return JSON.parse(await readFile(outputPath, 'utf8'));
  }
  assert.notEqual(result.status, 0, `${label} should have failed closed.`);
  return `${result.stderr}\n${result.stdout}`;
}

const root = await mkdtemp(join(tmpdir(), 'songsterr-note-qualification-v1-'));
try {
  // Case 1: one proposal corroborated, one explicitly rejected.
  const rejectedRaw = await runBuilder(root, 'rejected', makeModel(), makeQualification('rejected'));
  assert.equal(rejectedRaw.capabilities.polyphonyResolved, true);
  assert.deepEqual(rejectedRaw.onsets.map((onset) => onset.classification), ['unambiguous', 'rejected']);
  assert.deepEqual(rejectedRaw.onsets.map((onset) => onset.candidates[0].midi), [40, 68]);
  assert.equal(rejectedRaw.diagnostics.allRawModelProposalsAccountedFor, true);
  assert.equal(rejectedRaw.diagnostics.rejectedProposalCount, 1);

  const rejectedAdapted = adaptStructureConditionedNoteEvidence(rejectedRaw, structureMap);
  assert.deepEqual(rejectedAdapted.promotedEvents.map((event) => event.midi), [40]);
  assert.equal(rejectedAdapted.metrics.rejectedOnsetCount, 1);
  assert.equal(rejectedAdapted.metrics.rejectedCandidateCount, 1);
  assert.equal(rejectedAdapted.metrics.unresolvedOnsetCount, 0);
  assert.equal(rejectedAdapted.metrics.resolvedProposalCount, 2);
  assert.equal(rejectedAdapted.metrics.rejectedEvidencePreserved, true);

  const rejectedSummary = summarizeNoteEvidence(rejectedAdapted);
  assert.equal(rejectedSummary.counts.classificationCounts.rejected, 1);
  assert.equal(rejectedSummary.counts.rejectedProposalCount, 1);
  assert.equal(rejectedSummary.counts.unresolvedPitchEvidenceCount, 0);

  const rejectedEvaluation = evaluateNoteEvidence(rejectedAdapted);
  assert.equal(rejectedEvaluation.failureReasons.includes('POLYPHONY_UNRESOLVED'), false);
  assert.equal(rejectedEvaluation.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'), false);

  // Case 2: insufficient independent evidence remains unresolved and fail-closed.
  const insufficientRaw = await runBuilder(root, 'insufficient', makeModel(), makeQualification('insufficient'));
  assert.equal(insufficientRaw.capabilities.polyphonyResolved, false);
  assert.deepEqual(insufficientRaw.onsets.map((onset) => onset.classification), ['unambiguous', 'ambiguous']);
  const insufficientAdapted = adaptStructureConditionedNoteEvidence(insufficientRaw, structureMap);
  assert.deepEqual(insufficientAdapted.promotedEvents.map((event) => event.midi), [40]);
  assert.equal(insufficientAdapted.metrics.unresolvedOnsetCount, 1);
  const insufficientEvaluation = evaluateNoteEvidence(insufficientAdapted);
  assert.equal(insufficientEvaluation.failureReasons.includes('POLYPHONY_UNRESOLVED'), true);
  assert.equal(insufficientEvaluation.failureReasons.includes('PITCH_EVIDENCE_UNRESOLVED'), true);

  // Case 3: candidate confidence is diagnostic only; qualification/promotion is invariant to it.
  const confidenceFlippedRaw = await runBuilder(
    root,
    'confidence-flipped',
    makeModel(0.01, 0.99),
    makeQualification('rejected'),
  );
  const confidenceFlippedAdapted = adaptStructureConditionedNoteEvidence(confidenceFlippedRaw, structureMap);
  assert.deepEqual(
    confidenceFlippedAdapted.onsets.map((onset) => onset.classification),
    rejectedAdapted.onsets.map((onset) => onset.classification),
  );
  assert.deepEqual(
    confidenceFlippedAdapted.promotedEvents.map((event) => event.midi),
    rejectedAdapted.promotedEvents.map((event) => event.midi),
  );

  // Case 4: missing qualification row fails closed.
  const missing = makeQualification('rejected');
  missing.proposals = missing.proposals.slice(0, 1);
  const missingFailure = await runBuilder(root, 'missing', makeModel(), missing, false);
  assert.match(missingFailure, /MODEL_NOTE_QUALIFICATION_POPULATION_MISMATCH/);

  // Case 5: extra qualification row fails closed.
  const extra = makeQualification('rejected');
  extra.proposals.push({
    noteId: 'not-a-model-note',
    midi: 55,
    startSeconds: 1.0,
    status: 'rejected',
    independentOnsetConfidence: 0,
  });
  const extraFailure = await runBuilder(root, 'extra', makeModel(), extra, false);
  assert.match(extraFailure, /MODEL_NOTE_QUALIFICATION_POPULATION_MISMATCH|MODEL_NOTE_QUALIFICATION_EXTRA_NOTE_ID/);

  // Case 6: exact identity fields must match even when noteId matches.
  const mismatched = makeQualification('rejected');
  mismatched.proposals[1].midi = 67;
  const mismatchFailure = await runBuilder(root, 'mismatch', makeModel(), mismatched, false);
  assert.match(mismatchFailure, /MODEL_NOTE_QUALIFICATION_NOTE_IDENTITY_FIELDS_MISMATCH/);

  // Case 7: the qualification sidecar may not claim model confidence was used for the decision.
  const confidenceDriven = makeQualification('rejected');
  confidenceDriven.candidateConfidenceUsedForDecision = true;
  const confidenceDrivenFailure = await runBuilder(root, 'confidence-driven', makeModel(), confidenceDriven, false);
  assert.match(confidenceDrivenFailure, /MODEL_NOTE_QUALIFICATION_MUST_BE_CONFIDENCE_INDEPENDENT/);

  console.log(JSON.stringify({
    contract: 'songsterr-fresh-model-note-qualification-v1-test',
    status: 'PASS',
    cases: 7,
    promotedWhenRejected: rejectedAdapted.promotedEvents.map((event) => event.midi),
    rejectedCandidatesPreserved: rejectedAdapted.onsets
      .filter((onset) => onset.classification === 'rejected')
      .flatMap((onset) => onset.candidates.map((candidate) => candidate.midi)),
    unresolvedWhenInsufficient: insufficientAdapted.metrics.unresolvedOnsetCount,
    confidenceInvariantPromotion: true,
    failClosedIdentityCoverage: true,
  }, null, 2));
} finally {
  await rm(root, { recursive: true, force: true });
}
