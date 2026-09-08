#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { adaptFullMixtureStructureAnalysis } from '../../songsterr_pipeline/audioStructureAdapter.mjs';

const [inputArg, outputArg] = process.argv.slice(2);
if (!inputArg || !outputArg) {
  throw new Error('Usage: build_structure_map.mjs <analysis.json> <structure-map.json>');
}

const inputPath = resolve(inputArg);
const outputPath = resolve(outputArg);
const raw = JSON.parse(await readFile(inputPath, 'utf8'));
const result = adaptFullMixtureStructureAnalysis(raw);

await writeFile(outputPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');

const map = result.structureMap;
const summary = {
  adapter: result.adapterContract.name,
  durationSeconds: map.durationSeconds,
  pickupDurationSeconds: map.pickupDurationSeconds,
  tempoBpm: map.tempoSegments[0].bpm,
  meter: `${map.meterSegments[0].numerator}/${map.meterSegments[0].denominator}`,
  feel: map.feelSegments[0].feel,
  measureCount: map.measures.length,
  downbeatCount: map.downbeats.length,
  confidence: map.confidence,
  alignmentDiagnostics: result.alignmentDiagnostics,
  referenceBlind: map.referenceBlind,
  structureFrozenBeforeNoteInference: result.adapterContract.structureFrozenBeforeNoteInference,
  legacyV143ScorerImported: result.adapterContract.legacyV143ScorerImported,
};

console.log(JSON.stringify(summary));
