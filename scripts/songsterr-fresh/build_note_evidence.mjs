#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { adaptStructureConditionedNoteEvidence } from '../../songsterr_pipeline/noteEvidenceAdapter.mjs';

const [contextArg, rawEvidenceArg, outputArg] = process.argv.slice(2);
if (!contextArg || !rawEvidenceArg || !outputArg) {
  throw new Error('Usage: build_note_evidence.mjs <context.json> <raw-note-evidence.json> <adapted-note-evidence.json>');
}

const context = JSON.parse(await readFile(resolve(contextArg), 'utf8'));
const raw = JSON.parse(await readFile(resolve(rawEvidenceArg), 'utf8'));

if (context?.contract !== 'songsterr-fresh-note-evidence-context-v1') {
  throw new Error('NOTE_EVIDENCE_CONTEXT_CONTRACT_MISMATCH');
}
if (context?.structureAcceptance?.accepted !== true || context?.structureFrozen !== true) {
  throw new Error('NOTE_EVIDENCE_CONTEXT_NOT_ACCEPTED_AND_FROZEN');
}
if (raw?.provenance?.modelInvoked === true) {
  throw new Error('CPU_NOTE_EVIDENCE_CANARY_MODEL_NOT_ALLOWED');
}
if (raw?.provenance?.gpuInvoked === true) {
  throw new Error('CPU_NOTE_EVIDENCE_CANARY_GPU_NOT_ALLOWED');
}
if (raw?.provenance?.legacyV143ScorerImported === true) {
  throw new Error('CPU_NOTE_EVIDENCE_CANARY_LEGACY_SCORER_NOT_ALLOWED');
}

const adapted = adaptStructureConditionedNoteEvidence(raw, context.structureMap);

if (adapted.adapterContract.modelInvoked || adapted.adapterContract.gpuInvoked || adapted.adapterContract.legacyV143ScorerImported) {
  throw new Error('CPU_NOTE_EVIDENCE_CANARY_EXECUTION_PROVENANCE_VIOLATION');
}
if (adapted.adapterContract.syntheticDurationInference !== false) {
  throw new Error('CPU_NOTE_EVIDENCE_CANARY_SYNTHETIC_DURATION_NOT_ALLOWED');
}

await writeFile(resolve(outputArg), `${JSON.stringify(adapted, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  contract: adapted.adapterContract,
  structureIdentity: adapted.structureIdentity,
  role: adapted.role,
  metrics: adapted.metrics,
}));
