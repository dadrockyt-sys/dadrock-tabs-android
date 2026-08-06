#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const V2_PATH = path.join(__dirname, 'build_gomyway_v8_full_rhythm_sustain_proof_v2.cjs');
const GENERATED_PATH = path.join(__dirname, '.generated_gomyway_v8_full_rhythm_sustain_proof_v5.cjs');

if (!fs.existsSync(V2_PATH)) {
  throw new Error(`Required V2 sustain proof builder not found: ${V2_PATH}`);
}

let source = fs.readFileSync(V2_PATH, 'utf8');

function replaceOnce(before, after, label) {
  if (!source.includes(before)) {
    throw new Error(`V5 sustain patch target missing (${label}).`);
  }
  source = source.replace(before, after);
}

replaceOnce(
  "gomyway-v8-full-rhythm-sustain-proof-v2.pdf",
  "gomyway-v8-full-rhythm-sustain-proof-v5.pdf",
  'PDF output',
);
replaceOnce(
  "gomyway-v8-full-rhythm-sustain-proof-v2-manifest.json",
  "gomyway-v8-full-rhythm-sustain-proof-v5-manifest.json",
  'manifest output',
);
replaceOnce(
  "Full Rhythm Sustain Tablature Proof V2",
  "Full Rhythm Repeated-Note Sustain Proof V5",
  'PDF title',
);
replaceOnce(
  "JIMMY PAIGE V8 FULL RHYTHM SUSTAIN TABLATURE PROOF V2",
  "JIMMY PAIGE V8 FULL RHYTHM REPEATED-NOTE SUSTAIN PROOF V5",
  'console title',
);

const straightRenderer = String.raw`function drawSustainLines(page, measureNumber, x1, x2, tabTop, rows) {
  const reserveTimeSignature = measureNumber === 1;
  let rendered = 0;
  for (const row of rows) {
    const xStart = stepX(row.startStep, x1, x2, reserveTimeSignature) + 5;
    const xEnd = stepX(row.endStep, x1, x2, reserveTimeSignature) - 3;
    if (!(xEnd > xStart + 2)) continue;
    for (const note of row.notes) {
      const y = tabTop - note.stringIndex * STRING_GAP;
      page.drawLine({
        start: { x: xStart, y },
        end: { x: xEnd, y },
        thickness: 1.0,
        color: INK,
        opacity: 0.78,
      });
      rendered += 1;
    }
  }
  return rendered;
}`;

const repeatedNoteRenderer = String.raw`function drawSustainLines(page, measureNumber, x1, x2, tabTop, rows) {
  const reserveTimeSignature = measureNumber === 1;
  let rendered = 0;

  // Measures 1-6 already use the approved bend/vibrato notation layer.
  // Do not add sustain arcs there because they overlap the bend-release symbols.
  if (measureNumber <= 6) return rendered;

  for (const row of rows) {
    const evidenceType = String(row.evidenceType || '').toLowerCase();

    // A curved tie is only correct when the same note or chord is attacked again.
    // Duration-only evidence does not prove a visible tie endpoint.
    if (!evidenceType.includes('same-note')) continue;

    const xStart = stepX(row.startStep, x1, x2, reserveTimeSignature) + 5;
    const xEnd = stepX(row.endStep, x1, x2, reserveTimeSignature) - 5;
    const width = xEnd - xStart;
    if (!(width > 8)) continue;

    const arcHeight = Math.max(4.0, Math.min(7.0, width * 0.14));

    for (const note of row.notes) {
      const stringY = tabTop - note.stringIndex * STRING_GAP;
      const start = { x: xStart, y: stringY + 1.1 };
      const end = { x: xEnd, y: stringY + 1.1 };
      const control = {
        x: (xStart + xEnd) / 2,
        y: stringY + arcHeight,
      };

      drawPolyline(
        page,
        quadraticPoints(start, control, end, 24),
        1.0,
      );

      rendered += 1;
    }
  }

  return rendered;
}`;

replaceOnce(
  straightRenderer,
  repeatedNoteRenderer,
  'straight sustain renderer',
);

fs.writeFileSync(GENERATED_PATH, source, 'utf8');

try {
  require(GENERATED_PATH);
} finally {
  process.on('beforeExit', () => {
    try {
      fs.unlinkSync(GENERATED_PATH);
    } catch {
      // Best-effort cleanup only.
    }
  });
}
