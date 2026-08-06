#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const BASE_PATH = path.join(__dirname, 'build_gomyway_v8_full_rhythm_proof_v1.cjs');
const GENERATED_PATH = path.join(__dirname, '.generated_gomyway_v8_full_rhythm_sustain_proof_v2.cjs');

if (!fs.existsSync(BASE_PATH)) {
  throw new Error(`Required V1 proof builder not found: ${BASE_PATH}`);
}

let source = fs.readFileSync(BASE_PATH, 'utf8');

function replaceOnce(before, after, label) {
  if (!source.includes(before)) {
    throw new Error(`V2 sustain renderer patch target missing (${label}).`);
  }
  source = source.replace(before, after);
}

replaceOnce(
  "const INTRO_OVERLAY_PATH = path.join(PUBLIC, 'gomyway-v8-supervised-intro-overlay-v3.json');",
  "const INTRO_OVERLAY_PATH = path.join(PUBLIC, 'gomyway-v8-supervised-intro-overlay-v3.json');\nconst SUSTAIN_PROJECTION_PATH = path.join(PUBLIC, 'gomyway-full-rhythm-sustain-projection-v1.json');\nconst SUSTAIN_MANIFEST_PATH = path.join(PUBLIC, 'gomyway-full-rhythm-sustain-projection-v1-manifest.json');",
  'sustain paths',
);

replaceOnce(
  "const OUTPUT_PDF_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-proof-v1.pdf');",
  "const OUTPUT_PDF_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-sustain-proof-v2.pdf');",
  'PDF output',
);
replaceOnce(
  "const OUTPUT_MANIFEST_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-proof-v1-manifest.json');",
  "const OUTPUT_MANIFEST_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-sustain-proof-v2-manifest.json');",
  'manifest output',
);

const sustainHelpers = String.raw`
function normalizeProjectedString(note) {
  const raw = intValue(note?.string ?? note?.stringIndex);
  if (raw == null) return null;
  if (raw >= 1 && raw <= 6) return raw - 1;
  if (raw >= 0 && raw <= 5) return raw;
  return null;
}

function sustainRowsByMeasure(payload) {
  if (!Array.isArray(payload.rows)) throw new Error('Sustain projection has no rows array.');
  const map = new Map();
  for (let measure = 1; measure <= 113; measure += 1) map.set(measure, []);
  for (const row of payload.rows) {
    const measureNumber = intValue(row.measureNumber);
    const startStep = intValue(row.startStep);
    const endStep = intValue(row.endStep);
    if (measureNumber == null || startStep == null || endStep == null) continue;
    const normalizedNotes = (Array.isArray(row.notes) ? row.notes : [])
      .map((note) => ({ stringIndex: normalizeProjectedString(note), fret: intValue(note.fret) }))
      .filter((note) => note.stringIndex != null && note.fret != null);
    if (!normalizedNotes.length || !(endStep > startStep)) continue;
    map.get(measureNumber)?.push({
      measureNumber,
      startStep,
      endStep,
      notes: normalizedNotes,
      evidenceType: row.evidenceType,
      readOnly: row.readOnly === true,
    });
  }
  return map;
}

function stepX(step, x1, x2, reserveTimeSignature) {
  const start = reserveTimeSignature ? x1 + 31 : x1 + 7;
  const end = x2 - 7;
  return start + ((Number(step) + 0.5) / STEPS_PER_MEASURE) * (end - start);
}

function drawSustainLines(page, measureNumber, x1, x2, tabTop, rows) {
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
}
`;

replaceOnce(
  "function drawMeasure(page, fonts, measureNumber, x1, x2, tabTop, events) {",
  `${sustainHelpers}\nfunction drawMeasure(page, fonts, measureNumber, x1, x2, tabTop, events, sustainRows, renderStats) {`,
  'drawMeasure signature',
);

replaceOnce(
  "  if (showTimeSignature) drawTimeSignature(page, fonts, x1 + 8, tabTop);\n\n  const positions = new Map();",
  "  if (showTimeSignature) drawTimeSignature(page, fonts, x1 + 8, tabTop);\n\n  renderStats.sustainLineSegments += drawSustainLines(page, measureNumber, x1, x2, tabTop, sustainRows);\n\n  const positions = new Map();",
  'draw sustain lines',
);

replaceOnce(
  "function drawSystem(page, fonts, systemIndex, measures, measureMap) {",
  "function drawSystem(page, fonts, systemIndex, measures, measureMap, sustainMap, renderStats) {",
  'drawSystem signature',
);

replaceOnce(
  "    drawMeasure(page, fonts, measureNumber, x1, x1 + measureWidth, tabTop, measureMap.get(measureNumber) || []);",
  "    drawMeasure(page, fonts, measureNumber, x1, x1 + measureWidth, tabTop, measureMap.get(measureNumber) || [], sustainMap.get(measureNumber) || [], renderStats);",
  'drawMeasure call',
);

replaceOnce(
  "  const introOverlay = readJson(INTRO_OVERLAY_PATH);",
  "  const introOverlay = readJson(INTRO_OVERLAY_PATH);\n  const sustainProjection = readJson(SUSTAIN_PROJECTION_PATH);\n  const sustainManifest = readJson(SUSTAIN_MANIFEST_PATH);",
  'load sustain artifacts',
);

replaceOnce(
  "  if (notationLock.passed !== true) throw new Error('Professional notation standard lock is not green.');",
  "  if (notationLock.passed !== true) throw new Error('Professional notation standard lock is not green.');\n  if (sustainManifest.passed !== true || sustainManifest.readyForReadOnlySustainRenderer !== true) {\n    throw new Error('Read-only sustain projection is not green.');\n  }\n  if (sustainProjection.readOnly !== true || sustainProjection.rules?.bendOrVibratoInferred !== false) {\n    throw new Error('Sustain projection protection contract failed.');\n  }",
  'sustain gate',
);

replaceOnce(
  "  const measureMap = mapByMeasure(merged.proofEvents);",
  "  const measureMap = mapByMeasure(merged.proofEvents);\n  const sustainMap = sustainRowsByMeasure(sustainProjection);\n  const renderStats = { sustainLineSegments: 0 };",
  'sustain map',
);

replaceOnce(
  "    systems.forEach((measures, systemIndex) => drawSystem(page, fonts, systemIndex, measures, measureMap));",
  "    systems.forEach((measures, systemIndex) => drawSystem(page, fonts, systemIndex, measures, measureMap, sustainMap, renderStats));",
  'system render binding',
);

replaceOnce(
  "Jimmy PAIge V8 — Full Rhythm Tablature Proof",
  "Jimmy PAIge V8 — Full Rhythm Sustain Tablature Proof V2",
  'title',
);
replaceOnce(
  "TRAINING PROOF • measures 1–113 • locked DadRock professional notation standard",
  "TRAINING PROOF • measures 1–113 • approved read-only sustain lines • locked notation standard",
  'subtitle',
);
replaceOnce(
  "JIMMY PAIGE V8 FULL RHYTHM TABLATURE PROOF V1",
  "JIMMY PAIGE V8 FULL RHYTHM SUSTAIN TABLATURE PROOF V2",
  'console title',
);

replaceOnce(
  "    proofType: 'full-rhythm-tablature-training-proof',",
  "    proofType: 'full-rhythm-sustain-tablature-training-proof',\n    sustainProjectionPath: path.relative(ROOT, SUSTAIN_PROJECTION_PATH),\n    sustainProjectionRows: sustainProjection.rowCount,\n    sustainCoveredMeasures: sustainProjection.coveredMeasureCount,\n    sustainLineSegmentsRendered: renderStats.sustainLineSegments,\n    sustainProjectionReadOnly: sustainProjection.readOnly === true,\n    bendOrVibratoInferredBySustainProjection: false,",
  'manifest sustain fields',
);

replaceOnce(
  "  console.log('Rendered bends:', manifest.renderedBends);",
  "  console.log('Rendered bends:', manifest.renderedBends);\n  console.log('Approved sustain projection rows:', manifest.sustainProjectionRows);\n  console.log('Sustain covered measures:', manifest.sustainCoveredMeasures);\n  console.log('Sustain line segments rendered:', manifest.sustainLineSegmentsRendered);\n  console.log('Bend or vibrato inferred by sustain projection: false');",
  'console sustain summary',
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
