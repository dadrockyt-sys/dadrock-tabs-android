#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { buildStructureIdentity } from '../../songsterr_pipeline/structureIdentity.mjs';

const [structureResultArg, outputArg] = process.argv.slice(2);
if (!structureResultArg || !outputArg) {
  throw new Error('Usage: build_note_evidence_context.mjs <adapted-structure.json> <context.json>');
}

const structureResult = JSON.parse(await readFile(resolve(structureResultArg), 'utf8'));
if (structureResult?.structureAcceptance?.accepted !== true) {
  throw new Error('NOTE_EVIDENCE_REQUIRES_ACCEPTED_STRUCTURE');
}
if (structureResult?.adapterContract?.structureFrozenBeforeNoteInference !== true) {
  throw new Error('NOTE_EVIDENCE_REQUIRES_FROZEN_STRUCTURE');
}

const structureMap = structureResult.structureMap;
const structureIdentity = buildStructureIdentity(structureMap);
const context = {
  contract: 'songsterr-fresh-note-evidence-context-v1',
  version: 1,
  referenceBlind: true,
  structureFrozen: true,
  structureIdentity,
  structureAcceptance: structureResult.structureAcceptance,
  structureMap,
};

await writeFile(resolve(outputArg), `${JSON.stringify(context, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  contract: context.contract,
  structureIdentity,
  structureAccepted: true,
  measureCount: structureMap.measures?.length ?? 0,
  tempoSegmentCount: structureMap.tempoSegments?.length ?? 0,
}));
