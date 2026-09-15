#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { adaptStructureConditionedNoteEvidence } from '../../songsterr_pipeline/noteEvidenceAdapter.mjs';
import { summarizeNoteEvidence } from '../../songsterr_pipeline/noteEvidenceDiagnostics.mjs';
import { evaluateNoteEvidence } from '../../songsterr_pipeline/noteEvidenceEvaluator.mjs';

const [contextArg, evidenceArg, outputArg] = process.argv.slice(2);
if (!contextArg || !evidenceArg || !outputArg) {
  throw new Error(
    'Usage: adapt_qualified_note_evidence_v2.mjs <context.json> <qualified-evidence.json> <output.json>',
  );
}

const context = JSON.parse(await readFile(resolve(contextArg), 'utf8'));
const rawEvidence = JSON.parse(await readFile(resolve(evidenceArg), 'utf8'));

if (context?.contract !== 'songsterr-fresh-note-evidence-context-v1'
  || context?.version !== 1
  || context?.referenceBlind !== true
  || context?.structureFrozen !== true
  || context?.structureAcceptance?.accepted !== true
  || !context?.structureMap) {
  throw new Error('QUALIFIED_NOTE_EVIDENCE_ADAPTER_REQUIRES_ACCEPTED_FROZEN_CONTEXT');
}
if (rawEvidence?.contract !== 'songsterr-fresh-qualified-isolated-polyphonic-note-evidence-v2') {
  throw new Error('QUALIFIED_NOTE_EVIDENCE_V2_CONTRACT_REQUIRED');
}

const adapted = adaptStructureConditionedNoteEvidence(rawEvidence, context.structureMap);
const diagnosticSummary = summarizeNoteEvidence(adapted);
const evaluation = evaluateNoteEvidence(adapted);

const output = {
  ...adapted,
  integration: {
    contract: 'songsterr-fresh-qualified-note-evidence-adapter-bridge-v2',
    version: 2,
    referenceBlind: true,
    inputEvidenceContract: rawEvidence?.contract ?? null,
    qualificationRequiredBeforePromotion: true,
    rawModelProposalAutoPromotion: false,
    clipStartSyntheticPreContextAllowed: false,
  },
  diagnosticSummary,
  evaluation,
};

await writeFile(resolve(outputArg), `${JSON.stringify(output, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  contract: output.integration.contract,
  promotedEventCount: output.promotedEvents.length,
  rejectedOnsetCount: output.metrics.rejectedOnsetCount,
  unresolvedOnsetCount: output.metrics.unresolvedOnsetCount,
  evaluatorStatus: output.evaluation.status,
}));
