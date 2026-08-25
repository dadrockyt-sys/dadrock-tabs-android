import fs from 'node:fs/promises';
import path from 'node:path';
import { createV143RhythmPdf } from '../lib/createV143RhythmPdf.js';
import { projectV143RenderEvents, summarizeV143RhythmPresentation } from '../lib/v143RenderContract.js';

const input = process.argv[2];
const output = process.argv[3];
if (!input || !output) {
  throw new Error('Usage: node scripts/v143-render-real-candidate-pdf.mjs <candidate-product.json> <output.pdf>');
}

const product = JSON.parse(await fs.readFile(input, 'utf8'));
const renderEvents = projectV143RenderEvents(product.events);
if (renderEvents.length !== 967) {
  throw new Error(`Expected 967 preserved render events, received ${renderEvents.length}`);
}

const summary = summarizeV143RhythmPresentation(renderEvents);
if (Number(summary.measureCount) !== 113) {
  throw new Error(`Expected 113 measures, received ${summary.measureCount}`);
}
if (summary.oneNotePerMeasureCollapseDetected) {
  throw new Error('Refusing suspicious collapsed render stream.');
}

await fs.mkdir(path.dirname(output), { recursive: true });
const bytes = await createV143RhythmPdf({
  song: 'V143 Approved Rhythm Reference',
  artist: 'DadRock Tabs Studio',
  generatedTab: product.generatedTab,
  renderEvents: product.events,
  tuning: product.tuning || 'E Standard',
  tempo: Number(product.tempo) || 129.19921875,
  timeSignature: product.timeSignature || '4/4',
  keySignature: product.keySignature || '',
  preview: false,
});
await fs.writeFile(output, bytes);

const report = {
  input,
  output,
  sourceEventCount: Array.isArray(product.events) ? product.events.length : 0,
  projectedEventCount: renderEvents.length,
  measureCount: summary.measureCount,
  maximumEventsInMeasure: summary.maximumEventsInMeasure,
  denseMeasureCount: summary.denseMeasureCount,
  tempo: Number(product.tempo) || 129.19921875,
  tuning: product.tuning || 'E Standard',
  timeSignature: product.timeSignature || '4/4',
  keySignature: product.keySignature || '',
  pdfBytes: bytes.length,
  referenceFree: true,
  professionalReferenceUsed: false,
  modalInvoked: false,
  productionModified: false,
};
console.log(JSON.stringify(report, null, 2));
