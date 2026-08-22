import fs from 'node:fs/promises';
import { PDFDocument } from 'pdf-lib';
import {
  projectV143RenderEvents,
  summarizeV143Techniques,
} from '../lib/v143RenderContract.js';
import { createV143RhythmPdf } from '../lib/createV143RhythmPdf.js';

const OUTPUT_DIR = new URL('../debug/v143-contextual-prune/jimmy-paige-pdf-fixture/', import.meta.url);

function event({
  measure,
  step,
  stringIndex,
  fret,
  midi,
  techniques = [],
  durationSteps = 1,
  bendSemitones = null,
  bendTargetFret = null,
  bendTargetMidi = null,
  bendRelease = false,
  legatoTargetEventIndex = null,
}) {
  const result = {
    measure,
    step,
    stringIndex,
    fret,
    midi,
    rhythmTechniques: techniques.map((type) => ({ type })),
    rhythmSustain: {
      durationSteps,
      durationSeconds: durationSteps * 0.125,
      tier: durationSteps >= 8 ? 'long' : durationSteps >= 4 ? 'medium' : 'short',
    },
  };

  if (bendSemitones !== null) result.bendSemitones = bendSemitones;
  if (bendTargetFret !== null) result.bendTargetFret = bendTargetFret;
  if (bendTargetMidi !== null) result.bendTargetMidi = bendTargetMidi;
  if (bendRelease) result.bendRelease = true;
  if (legatoTargetEventIndex !== null) {
    result.legatoTargetEventIndex = legatoTargetEventIndex;
  }

  return result;
}

const rawEvents = [
  event({ measure: 1, step: 0, stringIndex: 5, fret: 3, midi: 43, techniques: ['palm-mute'], durationSteps: 2 }),
  event({ measure: 1, step: 4, stringIndex: 4, fret: 5, midi: 50, techniques: ['let-ring'], durationSteps: 8 }),
  event({ measure: 1, step: 8, stringIndex: 2, fret: 7, midi: 62, techniques: ['hammer-on'], legatoTargetEventIndex: 3 }),
  event({ measure: 1, step: 12, stringIndex: 2, fret: 9, midi: 64, techniques: ['vibrato'], durationSteps: 3 }),

  event({ measure: 2, step: 0, stringIndex: 1, fret: 10, midi: 69, techniques: ['bend', 'bend-release', 'vibrato'], bendSemitones: 2, bendTargetFret: 12, bendTargetMidi: 71, bendRelease: true, durationSteps: 4 }),
  event({ measure: 2, step: 6, stringIndex: 3, fret: 5, midi: 55, techniques: ['slide-up'], legatoTargetEventIndex: 6 }),
  event({ measure: 2, step: 10, stringIndex: 3, fret: 7, midi: 57, techniques: ['sustain-tie'], durationSteps: 6 }),
  event({ measure: 2, step: 14, stringIndex: 0, fret: 12, midi: 76, techniques: ['natural-harmonic'] }),

  event({ measure: 3, step: 0, stringIndex: 3, fret: 7, midi: 57, techniques: ['pull-off'], legatoTargetEventIndex: 9 }),
  event({ measure: 3, step: 4, stringIndex: 3, fret: 5, midi: 55, techniques: ['dead-note'] }),
  event({ measure: 3, step: 8, stringIndex: 2, fret: 9, midi: 64, techniques: ['pinch-harmonic'] }),
  event({ measure: 3, step: 12, stringIndex: 1, fret: 12, midi: 71, techniques: ['tap'] }),

  event({ measure: 4, step: 0, stringIndex: 4, fret: 7, midi: 52, techniques: ['muted-strum'] }),
  event({ measure: 4, step: 4, stringIndex: 2, fret: 9, midi: 64, techniques: ['slide-down'], legatoTargetEventIndex: 14 }),
  event({ measure: 4, step: 8, stringIndex: 2, fret: 7, midi: 62, techniques: ['trill'], durationSteps: 4 }),
  event({ measure: 4, step: 12, stringIndex: 1, fret: 10, midi: 69, techniques: ['pre-bend'], bendSemitones: 1, bendTargetFret: 11, bendTargetMidi: 70 }),
];

// Extend to 28 measures so the fixture verifies real pagination and continuation headers.
for (let measure = 5; measure <= 28; measure += 1) {
  rawEvents.push(event({
    measure,
    step: (measure * 3) % 16,
    stringIndex: measure % 6,
    fret: 3 + (measure % 10),
    midi: 45 + (measure % 24),
    techniques: measure % 4 === 0 ? ['palm-mute'] : measure % 5 === 0 ? ['let-ring'] : [],
    durationSteps: measure % 3 === 0 ? 4 : 2,
  }));
}

const expectedTechniques = [
  'bend',
  'bend-release',
  'dead-note',
  'hammer-on',
  'let-ring',
  'muted-strum',
  'natural-harmonic',
  'palm-mute',
  'pinch-harmonic',
  'pre-bend',
  'pull-off',
  'slide-down',
  'slide-up',
  'sustain-tie',
  'tap',
  'trill',
  'vibrato',
];

const projected = projectV143RenderEvents(rawEvents);
const projectedTechniques = summarizeV143Techniques(rawEvents);
const missingTechniques = expectedTechniques.filter((value) => !projectedTechniques.includes(value));

if (projected.length !== rawEvents.length) {
  throw new Error(`Fixture projection lost events: ${projected.length}/${rawEvents.length}`);
}
if (missingTechniques.length) {
  throw new Error(`Fixture projection lost techniques: ${missingTechniques.join(', ')}`);
}

await fs.mkdir(OUTPUT_DIR, { recursive: true });

const common = {
  song: 'Jimmy PAIge Structured PDF Quality Fixture',
  artist: 'DadRock Tabs',
  generatedTab: 'Structured V143 render-event fixture',
  renderEvents: projected,
  tuning: 'E Standard',
  tempo: 120,
  timeSignature: '4/4',
  keySignature: 'E minor',
};

const fullBytes = await createV143RhythmPdf({ ...common, preview: false });
const previewBytes = await createV143RhythmPdf({ ...common, preview: true, previewSystems: 4 });

const fullPath = new URL('full-structured-fixture.pdf', OUTPUT_DIR);
const previewPath = new URL('preview-structured-fixture.pdf', OUTPUT_DIR);
await fs.writeFile(fullPath, fullBytes);
await fs.writeFile(previewPath, previewBytes);

const fullDoc = await PDFDocument.load(fullBytes);
const previewDoc = await PDFDocument.load(previewBytes);
const fullPageCount = fullDoc.getPageCount();
const previewPageCount = previewDoc.getPageCount();

const fullHeader = Buffer.from(fullBytes).subarray(0, 5).toString('ascii');
const previewHeader = Buffer.from(previewBytes).subarray(0, 5).toString('ascii');

const checks = {
  allRawEventsProjected: projected.length === rawEvents.length,
  allTechniqueClassesProjected: missingTechniques.length === 0,
  fullPdfHeaderValid: fullHeader === '%PDF-',
  previewPdfHeaderValid: previewHeader === '%PDF-',
  fullPdfHasUsefulSize: fullBytes.length > 20000,
  previewPdfHasUsefulSize: previewBytes.length > 20000,
  fullPdfPaginates: fullPageCount >= 2,
  previewPdfPaginates: previewPageCount >= 2,
  previewIsDistinctFromFull: Buffer.compare(Buffer.from(fullBytes), Buffer.from(previewBytes)) !== 0,
  maximumMeasureIs28: Math.max(...projected.map((row) => row.measure)) === 28,
};

const failedChecks = Object.entries(checks)
  .filter(([, passed]) => !passed)
  .map(([name]) => name);

const result = {
  artifact: 'jimmy-paige-v143-structured-pdf-quality-fixture',
  schemaVersion: 1,
  passed: failedChecks.length === 0,
  checks,
  failedChecks,
  rawEventCount: rawEvents.length,
  projectedRenderEventCount: projected.length,
  expectedTechniques,
  projectedTechniques,
  fullPdfBytes: fullBytes.length,
  previewPdfBytes: previewBytes.length,
  fullPageCount,
  previewPageCount,
  fullPdfPath: 'debug/v143-contextual-prune/jimmy-paige-pdf-fixture/full-structured-fixture.pdf',
  previewPdfPath: 'debug/v143-contextual-prune/jimmy-paige-pdf-fixture/preview-structured-fixture.pdf',
  renderer: 'createV143RhythmPdf',
  renderContract: 'v143-render-contract-v1',
  productionPromotionPerformed: false,
};

await fs.writeFile(
  new URL('validation.json', OUTPUT_DIR),
  `${JSON.stringify(result, null, 2)}\n`,
  'utf8'
);

console.log(JSON.stringify(result, null, 2));
if (!result.passed) process.exitCode = 1;
