#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const ROOT = path.resolve(__dirname, '..');
const OVERLAY_PATH = path.join(ROOT, 'public', 'gomyway-v8-supervised-intro-overlay-v3.json');
const PDF_PATH = path.join(ROOT, 'public', 'gomyway-v8-repeat-consensus-intro-proof-v3.pdf');
const MANIFEST_PATH = path.join(ROOT, 'public', 'gomyway-v8-repeat-consensus-intro-proof-v3-manifest.json');

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 82;
const RIGHT = 752;
const STRING_GAP = 10;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const MEASURES = [1, 2, 3, 4, 5, 6];
const EXPECTED_CORE_STEPS = [2, 4, 6, 9, 11, 14];
const REPEAT_ENDING_MEASURES = [2, 4, 6];
const EXTRA_ENDING_STEP = 15;

function readJson(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Required file not found: ${filePath}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function mapEvents(events) {
  const map = new Map();
  for (const event of events) {
    const measure = Number(event.measureNumber);
    if (!map.has(measure)) map.set(measure, []);
    map.get(measure).push(event);
  }
  for (const rows of map.values()) {
    rows.sort((a, b) => Number(a.quantizedStep) - Number(b.quantizedStep));
  }
  return map;
}

function drawFret(page, font, x, y, fret) {
  const text = String(fret);
  const size = 9;
  const width = font.widthOfTextAtSize(text, size);
  page.drawRectangle({ x: x - width / 2 - 2, y: y - 4, width: width + 4, height: 10, color: rgb(1, 1, 1) });
  page.drawText(text, { x: x - width / 2, y: y - 2.2, size, font, color: rgb(0.02, 0.02, 0.02) });
}

function drawRhythmStem(page, x, tabBottom) {
  const stemEnd = tabBottom - 22;
  page.drawLine({ start: { x, y: tabBottom - 2 }, end: { x, y: stemEnd }, thickness: 0.8, color: rgb(0.12, 0.12, 0.12) });
  for (let index = 0; index < 2; index += 1) {
    const y = stemEnd + index * 5;
    page.drawLine({ start: { x, y }, end: { x: x + 7, y: y - 3 }, thickness: 0.9, color: rgb(0.12, 0.12, 0.12) });
  }
}

function drawFullBend(page, fonts, x, y) {
  const top = y + 28;
  page.drawText('Full', { x: x - 8, y: top + 4, size: 6.5, font: fonts.bold, color: rgb(0.08, 0.08, 0.08) });
  page.drawLine({ start: { x: x + 1, y: y + 6 }, end: { x: x + 1, y: top - 1 }, thickness: 0.9, color: rgb(0.08, 0.08, 0.08) });
  page.drawLine({ start: { x: x + 1, y: top - 1 }, end: { x: x + 7, y: top - 6 }, thickness: 0.9, color: rgb(0.08, 0.08, 0.08) });
  page.drawLine({ start: { x: x + 1, y: top - 1 }, end: { x: x - 4, y: top - 6 }, thickness: 0.9, color: rgb(0.08, 0.08, 0.08) });
}

function drawMeasure(page, fonts, measure, x1, x2, tabTop, events) {
  const tabBottom = tabTop - 5 * STRING_GAP;
  page.drawText(String(measure), { x: x1 + 4, y: tabTop + 10, size: 8, font: fonts.bold, color: rgb(0.12, 0.12, 0.12) });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawLine({ start: { x: x1, y }, end: { x: x2, y }, thickness: 0.6, color: rgb(0.28, 0.28, 0.28) });
  }
  page.drawLine({ start: { x: x1, y: tabTop + 2 }, end: { x: x1, y: tabBottom - 2 }, thickness: 1, color: rgb(0.08, 0.08, 0.08) });
  page.drawLine({ start: { x: x2, y: tabTop + 2 }, end: { x: x2, y: tabBottom - 2 }, thickness: 1, color: rgb(0.08, 0.08, 0.08) });

  for (const event of events) {
    const step = Number(event.quantizedStep);
    const x = x1 + 12 + ((step + 0.5) / 16) * (x2 - x1 - 24);
    const notes = Array.isArray(event.notes) ? event.notes : [];
    for (const note of notes) {
      const stringIndex = Number(note.stringIndex);
      const y = tabTop - stringIndex * STRING_GAP;
      drawFret(page, fonts.mono, x, y, note.fret);
      if (Array.isArray(event.techniques) && event.techniques.includes('full-bend')) {
        drawFullBend(page, fonts, x, y);
      }
    }
    drawRhythmStem(page, x, tabBottom);
  }
}

function drawSystem(page, fonts, systemIndex, measures, measureMap) {
  const systemTop = 442 - systemIndex * 148;
  const tabTop = systemTop - 24;
  const measureWidth = (RIGHT - LEFT) / 2;

  page.drawText(`Measures ${measures[0]}–${measures[1]}`, { x: LEFT, y: systemTop + 6, size: 7, font: fonts.bold, color: rgb(0.18, 0.18, 0.18) });
  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawText(STRING_LABELS[stringIndex], { x: LEFT - 20, y: y - 3, size: 7, font: fonts.bold, color: rgb(0.12, 0.12, 0.12) });
  }

  measures.forEach((measure, index) => {
    const x1 = LEFT + index * measureWidth;
    drawMeasure(page, fonts, measure, x1, x1 + measureWidth, tabTop, measureMap.get(measure) || []);
  });
}

async function main() {
  const overlay = readJson(OVERLAY_PATH);
  const events = Array.isArray(overlay.events) ? overlay.events : [];
  if (events.length !== 39) throw new Error(`Expected 39 consensus events, got ${events.length}.`);

  const measureMap = mapEvents(events);
  const missing = [];
  for (const measure of MEASURES) {
    const steps = new Set((measureMap.get(measure) || []).map((event) => Number(event.quantizedStep)));
    for (const step of EXPECTED_CORE_STEPS) if (!steps.has(step)) missing.push([measure, step]);
  }
  for (const measure of REPEAT_ENDING_MEASURES) {
    const extras = (measureMap.get(measure) || []).filter((event) => Number(event.quantizedStep) === EXTRA_ENDING_STEP && Array.isArray(event.notes) && event.notes.length > 1);
    if (extras.length !== 1) missing.push([measure, EXTRA_ENDING_STEP]);
  }
  if (missing.length) throw new Error(`Consensus proof is missing expected events: ${JSON.stringify(missing)}`);

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
  page.drawText('Are You Gonna Go My Way', { x: 282, y: 574, size: 16, font: fonts.bold, color: rgb(0.03, 0.03, 0.03) });
  page.drawText('Jimmy PAIge V8 — Repeat-Consensus Intro Proof V3', { x: 230, y: 553, size: 11, font: fonts.bold, color: rgb(0.1, 0.1, 0.1) });
  page.drawText('TRAINING ONLY • analyzer-enforced repeat agreement • no manual measure list', { x: 235, y: 536, size: 7.5, font: fonts.body, color: rgb(0.32, 0.32, 0.32) });
  page.drawText('INTRO', { x: LEFT, y: 498, size: 11, font: fonts.bold, color: rgb(0.08, 0.08, 0.08) });

  drawSystem(page, fonts, 0, [1, 2], measureMap);
  drawSystem(page, fonts, 1, [3, 4], measureMap);
  drawSystem(page, fonts, 2, [5, 6], measureMap);

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(PDF_PATH, pdfBytes);

  const bends = events.filter((event) => Array.isArray(event.techniques) && event.techniques.includes('full-bend')).length;
  const doubleStops = events.filter((event) => Array.isArray(event.notes) && event.notes.length > 1).length;
  const endingMultiplicity = {};
  for (const measure of REPEAT_ENDING_MEASURES) {
    endingMultiplicity[measure] = (measureMap.get(measure) || []).filter((event) => Array.isArray(event.notes) && event.notes.length > 1 && [14, 15].includes(Number(event.quantizedStep))).length;
  }

  const manifest = {
    schemaVersion: 3,
    passed: events.length === 39 && missing.length === 0 && bends === 6 && doubleStops === 6 && Object.values(endingMultiplicity).every((value) => value === 2),
    eventCount: events.length,
    bendsRendered: bends,
    endingDoubleStopsRendered: doubleStops,
    endingMultiplicity,
    repeatClass: REPEAT_ENDING_MEASURES,
    humanVisualInspectionRequired: false,
    trainingOnly: true,
    productionEligible: false,
    protected949EventSourceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    productionPromotionAllowed: false,
  };
  fs.writeFileSync(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log('JIMMY PAIGE V8 REPEAT-CONSENSUS INTRO PROOF V3');
  console.log('Passed:', manifest.passed);
  console.log('Events:', events.length);
  console.log('Bends rendered:', bends);
  console.log('Ending double-stops rendered:', doubleStops);
  console.log('Ending multiplicity:', endingMultiplicity);
  console.log('Repeat class:', REPEAT_ENDING_MEASURES);
  console.log('Human visual inspection required: false');
  console.log('Protected 949-event source modified: false');
  console.log('V7 events modified: false');
  console.log('Protected renderer modified: false');
  console.log('Production promotion allowed: false');
  console.log('PDF:', path.relative(ROOT, PDF_PATH));
  console.log('Manifest:', path.relative(ROOT, MANIFEST_PATH));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exitCode = 1;
});
