#!/usr/bin/env node

import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

import { adaptStructureConditionedNoteEvidence } from '../../songsterr_pipeline/noteEvidenceAdapter.mjs';
import { buildStructureIdentity } from '../../songsterr_pipeline/structureIdentity.mjs';
import { buildStructureMap } from '../../songsterr_pipeline/structureMap.mjs';

const BUILDER = resolve('scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence_v2.mjs');
const NOTE_SHA = 'd'.repeat(64);

const structureMap = buildStructureMap({
  durationSeconds: 5,
  tempoSegments: [{ start: 0, end: null, bpm: 120 }],
  meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
  feelSegments: [{ start: 0, end: null, feel: 'straight' }],
  confidence: { overall: 1, tempo: 1, meter: 1, downbeats: 1, measures: 1, feel: 1 },
});
const context = {
  contract: 'songsterr-fresh-note-evidence-context-v1',
  version: 1,
  referenceBlind: true,
  structureFrozen: true,
  structureAcceptance: { accepted: true },
  structureIdentity: buildStructureIdentity(structureMap),
  structureMap,
};

function model() {
  return {
    contract: 'songsterr-fresh-basic-pitch-isolated-guitar-v1',
    version: 1,
    referenceBlind: true,
    role: 'guitar',
    notes: [
      { noteId: 'n40', startSeconds: 0.011, diagnosticModelEndSeconds: 4.9, midi: 40, confidence: 0.79 },
      { noteId: 'n68', startSeconds: 0.360, diagnosticModelEndSeconds: 1.53, midi: 68, confidence: 0.35 },
    ],
    noteInferenceIdentity: {
      contract: 'songsterr-fresh-basic-pitch-note-identity-v1',
      version: 1,
      algorithm: 'sha256',
      eventCount: 2,
      sha256: NOTE_SHA,
    },
    activationEvidenceIdentity: null,
    diagnostics: { modelNoteEndsUsedAsDuration: false },
    provenance: {
      modelInvoked: true,
      gpuInvoked: false,
      modelValidationComplete: false,
      separationSource: 'synthetic-isolated-guitar',
      audioSource: 'synthetic-unit-test',
    },
  };
}

function qualification() {
  return {
    contract: 'songsterr-fresh-model-note-qualification-v2',
    version: 2,
    referenceBlind: true,
    modelNoteIdentitySha256: NOTE_SHA,
    method: 'synthetic-v2-fixture',
    candidateConfidenceUsedForDecision: false,
    independentOfBasicPitchCandidateConfidence: true,
    referenceTabUsed: false,
    proposals: [
      { noteId: 'n40', midi: 40, startSeconds: 0.011, status: 'corroborated', independentOnsetConfidence: 1, provenance: {} },
      { noteId: 'n68', midi: 68, startSeconds: 0.360, status: 'rejected', independentOnsetConfidence: 0, provenance: {} },
    ],
  };
}

async function runBuilder(root, label, modelPayload, qualificationPayload, expectSuccess = true) {
  const contextPath = join(root, `${label}-context.json`);
  const modelPath = join(root, `${label}-model.json`);
  const qualificationPath = join(root, `${label}-qualification.json`);
  const outputPath = join(root, `${label}-output.json`);
  await Promise.all([
    writeFile(contextPath, `${JSON.stringify(context, null, 2)}\n`),
    writeFile(modelPath, `${JSON.stringify(modelPayload, null, 2)}\n`),
    writeFile(qualificationPath, `${JSON.stringify(qualificationPayload, null, 2)}\n`),
  ]);
  const result = spawnSync(process.execPath, [BUILDER, contextPath, modelPath, qualificationPath, outputPath], { encoding: 'utf8' });
  if (!expectSuccess) {
    assert.notEqual(result.status, 0, `${label} should fail closed.`);
    return `${result.stderr}\n${result.stdout}`;
  }
  assert.equal(result.status, 0, `${label} builder failed: ${result.stderr || result.stdout}`);
  return JSON.parse(await readFile(outputPath, 'utf8'));
}

const root = await mkdtemp(join(tmpdir(), 'songsterr-note-qualification-v2-'));
try {
  const raw = await runBuilder(root, 'baseline', model(), qualification());
  assert.equal(raw.contract, 'songsterr-fresh-qualified-isolated-polyphonic-note-evidence-v2');
  assert.deepEqual(raw.onsets.map((onset) => onset.classification), ['unambiguous', 'rejected']);
  const adapted = adaptStructureConditionedNoteEvidence(raw, structureMap);
  assert.deepEqual(adapted.promotedEvents.map((event) => event.midi), [40]);
  assert.deepEqual(
    adapted.onsets.filter((onset) => onset.classification === 'rejected').flatMap((onset) => onset.candidates.map((candidate) => candidate.midi)),
    [68],
  );
  assert.equal(adapted.metrics.unresolvedOnsetCount, 0);

  const missing = qualification();
  missing.proposals = missing.proposals.slice(0, 1);
  assert.match(await runBuilder(root, 'missing', model(), missing, false), /MODEL_NOTE_QUALIFICATION_POPULATION_MISMATCH/);

  const mismatch = qualification();
  mismatch.proposals[1].midi = 67;
  assert.match(await runBuilder(root, 'mismatch', model(), mismatch, false), /MODEL_NOTE_QUALIFICATION_NOTE_IDENTITY_FIELDS_MISMATCH/);

  const confidenceDriven = qualification();
  confidenceDriven.candidateConfidenceUsedForDecision = true;
  assert.match(await runBuilder(root, 'confidence-driven', model(), confidenceDriven, false), /MODEL_NOTE_QUALIFICATION_MUST_BE_CONFIDENCE_INDEPENDENT/);

  console.log(JSON.stringify({
    contract: 'songsterr-fresh-model-note-qualification-v2-builder-test',
    status: 'PASS',
    cases: 4,
    promotedMidis: adapted.promotedEvents.map((event) => event.midi),
    failClosedCoverageAndIdentity: true,
    candidateConfidenceDiagnosticOnly: true,
  }, null, 2));
} finally {
  await rm(root, { recursive: true, force: true });
}
