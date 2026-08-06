#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const V2_PATH = path.join(__dirname, 'build_gomyway_v8_full_rhythm_sustain_proof_v2.cjs');
const GENERATED_PATH = path.join(__dirname, '.generated_gomyway_v8_full_rhythm_sustain_proof_v3.cjs');

if (!fs.existsSync(V2_PATH)) {
  throw new Error(`Required V2 sustain proof builder not found: ${V2_PATH}`);
}

let source = fs.readFileSync(V2_PATH, 'utf8');

function replaceOnce(before, after, label) {
  if (!source.includes(before)) {
    throw new Error(`V3 curved-sustain patch target missing (${label}).`);
  }
  source = source.replace(before, after);
}

replaceOnce(
  "gomyway-v8-full-rhythm-sustain-proof-v2.pdf",
  "gomyway-v8-full-rhythm-sustain-proof-v3.pdf",
  'PDF output',
);
replaceOnce(
  "gomyway-v8-full-rhythm-sustain-proof-v2-manifest.json",
  "gomyway-v8-full-rhythm-sustain-proof-v3-manifest.json",
  'manifest output',
);
replaceOnce(
  "Full Rhythm Sustain Tablature Proof V2",
  "Full Rhythm Sustain Tablature Proof V3",
  'PDF title',
);
replaceOnce(
  "JIMMY PAIGE V8 FULL RHYTHM SUSTAIN TABLATURE PROOF V2",
  "JIMMY PAIGE V8 FULL RHYTHM SUSTAIN TABLATURE PROOF V3",
  'console title',
);
replaceOnce(
  "approved read-only sustain lines",
  "approved read-only curved sustain ties",
  'subtitle',
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

const curvedRenderer = String.raw`function drawSustainLines(page, measureNumber, x1, x2, tabTop, rows) {
  const reserveTimeSignature = measureNumber === 1;
  let rendered = 0;
  for (const row of rows) {
    const xStart = stepX(row.startStep, x1, x2, reserveTimeSignature) + 5;
    const xEnd = stepX(row.endStep, x1, x2, reserveTimeSignature) - 4;
    const width = xEnd - xStart;
    if (!(width > 7)) continue;

    const arcHeight = Math.max(4.5, Math.min(8.5, width * 0.16));
    const slashHeight = Math.max(3.5, Math.min(6.0, arcHeight * 0.8));

    for (const note of row.notes) {
      const stringY = tabTop - note.stringIndex * STRING_GAP;
      const start = { x: xStart, y: stringY + 1.2 };
      const end = { x: xEnd, y: stringY + 1.2 };
      const control = {
        x: (xStart + xEnd) / 2,
        y: stringY + arcHeight,
      };

      drawPolyline(page, quadraticPoints(start, control, end, 24), 1.05);

      page.drawLine({
        start: { x: xEnd - 0.8, y: stringY + 1.0 },
        end: { x: xEnd + 3.2, y: stringY + slashHeight },
        thickness: 1.05,
        color: INK,
      });

      rendered += 1;
    }
  }
  return rendered;
}`;

replaceOnce(straightRenderer, curvedRenderer, 'straight sustain renderer');

replaceOnce(
  "    sustainLineSegmentsRendered: renderStats.sustainLineSegments,",
  "    sustainLineSegmentsRendered: renderStats.sustainLineSegments,\n    sustainVisualStyle: 'professional-curved-tie-arcs',\n    sustainEndMark: 'short-diagonal-release-slash',\n    straightTabLineSustainRendered: false,",
  'manifest visual standard',
);

replaceOnce(
  "  console.log('Sustain line segments rendered:', manifest.sustainLineSegmentsRendered);",
  "  console.log('Curved sustain ties rendered:', manifest.sustainLineSegmentsRendered);\n  console.log('Sustain visual style: professional curved tie arcs');\n  console.log('Straight tab-line sustain rendered: false');",
  'console visual summary',
);

fs.writeFileSync(GENERATED_PATH, source, 'utf8');

try {
  require(GENERATED_PATH);
} finally {
  process.on('beforeExit', () => {
    try {
      fs.unlinkSync(GENERATED_PATH);
    } catch {
      // Temporary generated renderer cleanup is best-effort only.
    }
  });
}
