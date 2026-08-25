import fs from 'node:fs/promises';
import path from 'node:path';
import { createV143RhythmPdf } from '../lib/createV143RhythmPdf.js';
import { projectV143RenderEvents, summarizeV143RhythmPresentation } from '../lib/v143RenderContract.js';

const input = process.argv[2];
const output = process.argv[3];
if (!input || !output) {
  throw new Error('Usage: node scripts/v143-render-v5-shadow-pdf.mjs <v5-render-stream.json> <output.pdf>');
}

const stream = JSON.parse(await fs.readFile(input, 'utf8'));
if (stream.validationPassed !== true || stream.freezeReady !== false) {
  throw new Error('Expected a passing, explicitly non-freeze-ready V5 shadow stream.');
}
const renderEvents = projectV143RenderEvents(stream.events);
const summary = summarizeV143RhythmPresentation(renderEvents);
if (renderEvents.length !== 1209) throw new Error(`Expected 1209 V5 render events, got ${renderEvents.length}`);
if (Number(summary.uniqueMeasureCount) !== 113) throw new Error(`Expected 113 measures, got ${summary.uniqueMeasureCount}`);
if (Number(summary.uniqueOnsetCount) !== 891) throw new Error(`Expected 891 onsets, got ${summary.uniqueOnsetCount}`);
if (summary.oneNotePerMeasureCollapseDetected) throw new Error('Refusing suspicious collapsed V5 stream.');

await fs.mkdir(path.dirname(output), { recursive: true });
const bytes = await createV143RhythmPdf({
  song: 'Rhythm Guitar — V5 Reference-Free Shadow',
  artist: 'DadRock Tabs Studio',
  renderEvents: stream.events,
  tuning: stream.tuning || 'E Standard',
  tempo: Number(stream.tempo) || 129.19921875,
  timeSignature: stream.timeSignature || '4/4',
  keySignature: stream.keySignature || '',
  preview: false,
});
await fs.writeFile(output, bytes);
console.log(JSON.stringify({
  output,
  renderedEventCount: renderEvents.length,
  uniqueMeasureCount: summary.uniqueMeasureCount,
  uniqueOnsetCount: summary.uniqueOnsetCount,
  maximumNotesPerPopulatedMeasure: summary.maximumNotesPerPopulatedMeasure,
  maximumChordSize: summary.maximumChordSize,
  multiNoteOnsetCount: summary.multiNoteOnsetCount,
  techniqueEventCount: summary.techniqueEventCount,
  techniqueTypes: summary.techniqueTypes,
  sectionCount: summary.sectionCount,
  pdfBytes: bytes.length,
  freezeReady: false,
  referenceFree: true,
  professionalReferenceUsed: false,
  modalInvoked: false,
  productionModified: false,
}, null, 2));
