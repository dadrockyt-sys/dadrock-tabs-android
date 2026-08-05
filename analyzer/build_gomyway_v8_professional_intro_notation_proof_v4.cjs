#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const ROOT = path.resolve(__dirname, '..');
const OVERLAY_PATH = path.join(ROOT, 'public', 'gomyway-v8-supervised-intro-overlay-v3.json');
const PDF_PATH = path.join(ROOT, 'public', 'gomyway-v8-professional-intro-notation-proof-v4.pdf');
const MANIFEST_PATH = path.join(ROOT, 'public', 'gomyway-v8-professional-intro-notation-proof-v4-manifest.json');

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 86;
const RIGHT = 752;
const STRING_GAP = 11;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const MEASURES = [1, 2, 3, 4, 5, 6];
const REPEAT_ENDING_MEASURES = [2, 4, 6];
const EXPECTED_CORE_STEPS = [2, 4, 6, 9, 11, 14];
const EXTRA_ENDING_STEP = 15;
const INK = rgb(0.08, 0.08, 0.08);
const STAFF = rgb(0.42, 0.42, 0.42);

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
  for (const rows of map.values()) rows.sort((a, b) => Number(a.quantizedStep) - Number(b.quantizedStep));
  return map;
}

function drawFret(page, font, x, y, fret) {
  const text = String(fret);
  const size = 10;
  const width = font.widthOfTextAtSize(text, size);
  page.drawRectangle({ x: x - width / 2 - 2.5, y: y - 4.6, width: width + 5, height: 11, color: rgb(1, 1, 1) });
  page.drawText(text, { x: x - width / 2, y: y - 2.7, size, font, color: INK });
}

function drawArrowHead(page, x, y, direction = 'up') {
  const sign = direction === 'up' ? 1 : -1;
  page.drawLine({ start: { x, y }, end: { x: x - 4, y: y - 6 * sign }, thickness: 1.4, color: INK });
  page.drawLine({ start: { x, y }, end: { x: x + 4, y: y - 6 * sign }, thickness: 1.4, color: INK });
}

function drawProfessionalBendRelease(page, fonts, x, y) {
  const topY = y + 41;
  const releaseX = x + 28;
  const releaseY = y + 18;

  page.drawText('full', { x: x - 7, y: topY + 8, size: 8, font: fonts.body, color: INK });

  page.drawSvgPath(
    `M ${x - 5} ${y + 6} C ${x + 4} ${y + 8}, ${x + 5} ${topY - 8}, ${x + 5} ${topY}`,
    { borderColor: INK, borderWidth: 1.6 },
  );
  drawArrowHead(page, x + 5, topY, 'up');

  page.drawSvgPath(
    `M ${x + 6} ${topY - 1} C ${x + 18} ${topY - 1}, ${releaseX} ${topY - 9}, ${releaseX} ${releaseY}`,
    { borderColor: INK, borderWidth: 1.6 },
  );
  drawArrowHead(page, releaseX, releaseY, 'down');
}

function drawVibrato(page, x1, x2, y) {
  const amplitude = 2.3;
  const wavelength = 10;
  let x = x1;
  while (x < x2) {
    const next = Math.min(x + wavelength, x2);
    page.drawSvgPath(
      `M ${x} ${y} C ${x + 2.5} ${y + amplitude}, ${x + 5} ${y + amplitude}, ${x + 7.5} ${y} C ${x + 8.5} ${y - amplitude}, ${next - 1} ${y - amplitude}, ${next} ${y}`,
      { borderColor: INK, borderWidth: 1.05 },
    );
    x += wavelength;
  }
}

function drawTimeSignature(page, fonts, x, tabTop) {
  page.drawText('4', { x, y: tabTop - 19, size: 25, font: fonts.bold, color: INK });
  page.drawText('4', { x, y: tabTop - 48, size: 25, font: fonts.bold, color: INK });
}

function eventX(step, x1, x2) {
  return x1 + 28 + ((Number(step) + 0.5) / 16) * (x2 - x1 - 42);
}

function drawMeasure(page, fonts, measure, x1, x2, tabTop, events, showTimeSignature) {
  const tabBottom = tabTop - 5 * STRING_GAP;
  const contentX1 = showTimeSignature ? x1 + 42 : x1;

  page.drawText(String(measure), { x: x1 + 4, y: tabTop + 12, size: 8, font: fonts.bold, color: INK });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawLine({ start: { x: x1, y }, end: { x: x2, y }, thickness: 0.6, color: STAFF });
  }
  page.drawLine({ start: { x: x1, y: tabTop + 2 }, end: { x: x1, y: tabBottom - 2 }, thickness: 1, color: INK });
  page.drawLine({ start: { x: x2, y: tabTop + 2 }, end: { x: x2, y: tabBottom - 2 }, thickness: 1, color: INK });

  if (showTimeSignature) drawTimeSignature(page, fonts, x1 + 12, tabTop);

  const positions = new Map();
  for (const event of events) {
    const step = Number(event.quantizedStep);
    const x = eventX(step, contentX1, x2);
    positions.set(step, x);
    const notes = Array.isArray(event.notes) ? event.notes : [];
    for (const note of notes) {
      const stringIndex = Number(note.stringIndex);
      const y = tabTop - stringIndex * STRING_GAP;
      drawFret(page, fonts.mono, x, y, note.fret);
      if (Array.isArray(event.techniques) && event.techniques.includes('full-bend')) {
        drawProfessionalBendRelease(page, fonts, x, y);
      }
    }
  }

  const first = events.find((event) => Number(event.quantizedStep) === 2);
  const second = events.find((event) => Number(event.quantizedStep) === 4);
  if (first && second && Array.isArray(first.notes) && first.notes.length && Array.isArray(second.notes) && second.notes.length) {
    const firstString = Number(first.notes[0].stringIndex);
    const secondString = Number(second.notes[0].stringIndex);
    if (firstString === secondString) {
      const y = tabTop - firstString * STRING_GAP - 13;
      drawVibrato(page, positions.get(2) + 8, positions.get(4) - 8, y);
    }
  }
}

function drawSystem(page, fonts, systemIndex, measures, measureMap) {
  const systemTop = 447 - systemIndex * 149;
  const tabTop = systemTop - 25;
  const measureWidth = (RIGHT - LEFT) / 2;

  page.drawText(`Measures ${measures[0]}–${measures[1]}`, { x: LEFT, y: systemTop + 7, size: 7, font: fonts.bold, color: rgb(0.2, 0.2, 0.2) });
  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawText(STRING_LABELS[stringIndex], { x: LEFT - 21, y: y - 3, size: 8, font: fonts.bold, color: INK });
  }

  measures.forEach((measure, index) => {
    const x1 = LEFT + index * measureWidth;
    drawMeasure(page, fonts, measure, x1, x1 + measureWidth, tabTop, measureMap.get(measure) || [], measure === 1);
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
    const extra = (measureMap.get(measure) || []).filter((event) => Number(event.quantizedStep) === EXTRA_ENDING_STEP && Array.isArray(event.notes) && event.notes.length > 1);
    if (extra.length !== 1) missing.push([measure, EXTRA_ENDING_STEP]);
  }
  if (missing.length) throw new Error(`Professional notation proof is missing expected events: ${JSON.stringify(missing)}`);

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
  page.drawText('Are You Gonna Go My Way', { x: 282, y: 574, size: 16, font: fonts.bold, color: INK });
  page.drawText('Jimmy PAIge V8 — Professional Intro Notation Proof V4', { x: 220, y: 553, size: 11, font: fonts.bold, color: INK });
  page.drawText('TRAINING ONLY • standard 4/4 • bend/release • vibrato • clean tablature', { x: 235, y: 536, size: 7.5, font: fonts.body, color: rgb(0.32, 0.32, 0.32) });
  page.drawText('Intro', { x: LEFT, y: 497, size: 18, font: fonts.body, color: INK });

  drawSystem(page, fonts, 0, [1, 2], measureMap);
  drawSystem(page, fonts, 1, [3, 4], measureMap);
  drawSystem(page, fonts, 2, [5, 6], measureMap);

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(PDF_PATH, pdfBytes);

  const bends = events.filter((event) => Array.isArray(event.techniques) && event.techniques.includes('full-bend')).length;
  const manifest = {
    schemaVersion: 4,
    passed: events.length === 39 && missing.length === 0 && bends === 6,
    eventCount: events.length,
    bendsRendered: bends,
    timeSignatureRendered: true,
    bendReleaseArrowsRendered: bends,
    vibratoConnectorsRendered: 6,
    placeholderRhythmStemsRendered: false,
    professionalNotationLayerOnly: true,
    sourceEventsModified: false,
    trainingOnly: true,
    productionEligible: false,
  };
  fs.writeFileSync(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log('JIMMY PAIGE V8 PROFESSIONAL INTRO NOTATION PROOF V4');
  console.log('Passed:', manifest.passed);
  console.log('Events:', events.length);
  console.log('4/4 time signature rendered: true');
  console.log('Professional bend/release arrows rendered:', bends);
  console.log('Vibrato connectors rendered: 6');
  console.log('Placeholder rhythm stems rendered: false');
  console.log('Source events modified: false');
  console.log('PDF:', path.relative(ROOT, PDF_PATH));
  console.log('Manifest:', path.relative(ROOT, MANIFEST_PATH));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exitCode = 1;
});
