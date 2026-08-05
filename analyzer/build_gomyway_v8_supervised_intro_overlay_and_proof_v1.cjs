#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const ROOT = path.resolve(__dirname, '..');
const PACK_PATH = path.join(ROOT, 'public', 'gomyway-intro-pitch-technique-training-pack-v1.json');
const SOURCE_PATH = path.join(ROOT, 'public', 'gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json');
const OVERLAY_PATH = path.join(ROOT, 'public', 'gomyway-v8-supervised-intro-overlay-v1.json');
const PDF_PATH = path.join(ROOT, 'public', 'gomyway-v8-supervised-intro-proof-v1.pdf');
const MANIFEST_PATH = path.join(ROOT, 'public', 'gomyway-v8-supervised-intro-proof-v1-manifest.json');

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 82;
const RIGHT = 752;
const STRING_GAP = 10;
const STEPS_PER_MEASURE = 16;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const MEASURES = [1, 2, 3, 4, 5, 6];
const EXPECTED_STEPS = [2, 4, 6, 9, 11, 14];

function readJson(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Required file not found: ${filePath}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function numberValue(value, fallback = null) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
}

function buildSupervisedEvents(pack) {
  if (pack.readyForSupervisedIntroTraining !== true) {
    throw new Error('Pitch-technique training pack is not ready.');
  }
  if (!Array.isArray(pack.rows) || pack.rows.length !== 36) {
    throw new Error(`Expected 36 training rows, got ${Array.isArray(pack.rows) ? pack.rows.length : 'invalid'}.`);
  }

  const events = pack.rows.map((row) => {
    const target = row.target || {};
    const notes = Array.isArray(target.notes) ? target.notes : [];
    if (notes.length === 0) {
      throw new Error(`Missing target notes for measure ${row.measureNumber}, step ${row.step}`);
    }
    return {
      measureNumber: Number(row.measureNumber),
      quantizedStep: Number(row.step),
      durationSteps: 1,
      notes: notes.map((note) => ({
        stringIndex: Number(note.stringIndex),
        fret: Number(note.fret),
      })),
      techniques: Array.isArray(target.techniques) ? [...target.techniques] : [],
      chordIds: Array.isArray(target.chordIds) ? [...target.chordIds] : [],
      confidence: 1,
      source: 'professional-label-supervised-training-only',
      supervisedTraining: {
        schemaVersion: 1,
        targetLabelOnly: true,
        productionEligible: false,
        originalCandidate: row.candidate || null,
        originalAction: row.trainingAction,
      },
    };
  });

  events.sort((a, b) => a.measureNumber - b.measureNumber || a.quantizedStep - b.quantizedStep);
  return events;
}

function buildMeasureMap(events) {
  const map = new Map();
  for (const event of events) {
    if (!map.has(event.measureNumber)) map.set(event.measureNumber, []);
    map.get(event.measureNumber).push(event);
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
    const x = x1 + 12 + ((event.quantizedStep + 0.5) / STEPS_PER_MEASURE) * (x2 - x1 - 24);
    for (const note of event.notes) {
      const y = tabTop - note.stringIndex * STRING_GAP;
      drawFret(page, fonts.mono, x, y, note.fret);
      if (event.techniques.includes('full-bend')) drawFullBend(page, fonts, x, y);
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
  const pack = readJson(PACK_PATH);
  const source = readJson(SOURCE_PATH);
  const sourceEvents = Array.isArray(source.events) ? source.events : source.candidates;
  if (!Array.isArray(sourceEvents) || sourceEvents.length !== 949) {
    throw new Error('Expected protected 949-event source.');
  }

  const events = buildSupervisedEvents(pack);
  const map = buildMeasureMap(events);
  const missingSlots = [];
  for (const measure of MEASURES) {
    const steps = new Set((map.get(measure) || []).map((event) => event.quantizedStep));
    for (const step of EXPECTED_STEPS) if (!steps.has(step)) missingSlots.push([measure, step]);
  }
  if (missingSlots.length > 0) throw new Error(`Missing supervised slots: ${JSON.stringify(missingSlots)}`);

  const overlay = {
    schemaVersion: 1,
    overlayType: 'supervised-intro-training-target',
    measureRange: [1, 6],
    sourceEventPath: path.relative(ROOT, SOURCE_PATH),
    trainingPackPath: path.relative(ROOT, PACK_PATH),
    events,
    eventCount: events.length,
    trainingOnly: true,
    productionEligible: false,
    professionalReferenceUsedAsTrainingLabel: true,
    protected949EventSourceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    productionPromotionAllowed: false,
  };
  fs.writeFileSync(OVERLAY_PATH, `${JSON.stringify(overlay, null, 2)}\n`);

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
  page.drawText('Are You Gonna Go My Way', { x: 282, y: 574, size: 16, font: fonts.bold, color: rgb(0.03, 0.03, 0.03) });
  page.drawText('Jimmy PAIge V8 — Supervised Intro Target Proof', { x: 248, y: 553, size: 11, font: fonts.bold, color: rgb(0.1, 0.1, 0.1) });
  page.drawText('TRAINING ONLY • professional labels • bends and exact string/fret targets', { x: 246, y: 536, size: 7.5, font: fonts.body, color: rgb(0.32, 0.32, 0.32) });
  page.drawText('INTRO', { x: LEFT, y: 498, size: 11, font: fonts.bold, color: rgb(0.08, 0.08, 0.08) });

  drawSystem(page, fonts, 0, [1, 2], map);
  drawSystem(page, fonts, 1, [3, 4], map);
  drawSystem(page, fonts, 2, [5, 6], map);

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(PDF_PATH, pdfBytes);

  const bends = events.filter((event) => event.techniques.includes('full-bend')).length;
  const doubleStops = events.filter((event) => event.notes.length > 1).length;
  const manifest = {
    schemaVersion: 1,
    passed: events.length === 36 && missingSlots.length === 0 && bends === 6 && doubleStops === 3,
    eventCount: events.length,
    bendsRendered: bends,
    endingDoubleStopsRendered: doubleStops,
    missingSlots,
    pages: 1,
    pdfBytes: pdfBytes.length,
    trainingOnly: true,
    productionEligible: false,
    protected949EventSourceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    productionPromotionAllowed: false,
  };
  fs.writeFileSync(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log('JIMMY PAIGE V8 SUPERVISED INTRO OVERLAY + PROOF V1');
  console.log('Passed:', manifest.passed);
  console.log('Supervised events:', events.length);
  console.log('Bends rendered:', bends);
  console.log('Ending double-stops rendered:', doubleStops);
  console.log('Missing slots:', missingSlots);
  console.log('Training only: true');
  console.log('Production eligible: false');
  console.log('Protected 949-event source modified: false');
  console.log('V7 events modified: false');
  console.log('Protected renderer modified: false');
  console.log('Production promotion allowed: false');
  console.log('Overlay:', path.relative(ROOT, OVERLAY_PATH));
  console.log('PDF:', path.relative(ROOT, PDF_PATH));
  console.log('Manifest:', path.relative(ROOT, MANIFEST_PATH));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exitCode = 1;
});
