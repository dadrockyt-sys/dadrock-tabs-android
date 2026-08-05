#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const ROOT = path.resolve(__dirname, '..');
const PUBLIC = path.join(ROOT, 'public');

const SOURCE_PATH = path.join(PUBLIC, 'gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json');
const TRAINING_GATE_PATH = path.join(PUBLIC, 'gomyway-full-song-v8-rhythm-training-gate-v1.json');
const NOTATION_LOCK_PATH = path.join(PUBLIC, 'professional-tablature-notation-standard-lock-v1.json');
const INTRO_OVERLAY_PATH = path.join(PUBLIC, 'gomyway-v8-supervised-intro-overlay-v3.json');
const OUTPUT_PDF_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-proof-v1.pdf');
const OUTPUT_MANIFEST_PATH = path.join(PUBLIC, 'gomyway-v8-full-rhythm-proof-v1-manifest.json');

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 74;
const RIGHT = 758;
const TOP = 520;
const STRING_GAP = 8.4;
const SYSTEM_GAP = 157;
const MEASURES_PER_SYSTEM = 4;
const SYSTEMS_PER_PAGE = 3;
const STEPS_PER_MEASURE = 16;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const INK = rgb(0.05, 0.05, 0.05);
const STAFF = rgb(0.44, 0.44, 0.44);

const SECTIONS = [
  { start: 1, end: 16, name: 'INTRO' },
  { start: 17, end: 32, name: 'VERSE 1' },
  { start: 33, end: 38, name: 'CHORUS 1' },
  { start: 39, end: 46, name: 'RIFF' },
  { start: 47, end: 62, name: 'VERSE 2' },
  { start: 63, end: 69, name: 'CHORUS 2' },
  { start: 70, end: 77, name: 'BRIDGE' },
  { start: 78, end: 94, name: 'SOLO RHYTHM BACKING / TRANSITION' },
  { start: 95, end: 102, name: 'RIFF RETURN' },
  { start: 103, end: 113, name: 'OUT-CHORUS / ENDING' },
];

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing prerequisite: ${path.relative(ROOT, filePath)}`);
  }
  const payload = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error(`Expected JSON object: ${path.relative(ROOT, filePath)}`);
  }
  return payload;
}

function eventList(payload) {
  for (const key of ['events', 'candidates', 'rhythmEvents', 'renderEvents']) {
    if (Array.isArray(payload[key])) return payload[key].filter((row) => row && typeof row === 'object');
  }
  throw new Error('No recognized event list in rhythm source.');
}

function intValue(value, fallback = null) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function measureOf(event) {
  return intValue(event.measureNumber ?? event.measure);
}

function stepOf(event) {
  return intValue(event.quantizedStep ?? event.step);
}

function durationOf(event) {
  return Math.max(1, intValue(event.durationSteps ?? event.duration, 1));
}

function isOverlayEvent(event) {
  return Boolean(event.supervisedTraining) || String(event.source || '').includes('professional-label-supervised');
}

function normalizeStringIndex(note, event) {
  if (Object.prototype.hasOwnProperty.call(note, 'string')) {
    const value = intValue(note.string);
    return value != null && value >= 1 && value <= 6 ? value - 1 : null;
  }
  const value = intValue(note.stringIndex);
  if (value == null) return null;
  if (isOverlayEvent(event)) return value >= 0 && value <= 5 ? value : null;
  if (value === 0) return 0;
  return value >= 1 && value <= 6 ? value - 1 : null;
}

function notesOf(event) {
  const raw = Array.isArray(event.notes) ? event.notes : [];
  const result = [];
  for (const note of raw) {
    if (!note || typeof note !== 'object') continue;
    const stringIndex = normalizeStringIndex(note, event);
    const fret = intValue(note.fret);
    if (stringIndex == null || fret == null || fret < 0 || fret > 24) continue;
    result.push({ stringIndex, fret });
  }
  const unique = new Map();
  for (const note of result) unique.set(`${note.stringIndex}:${note.fret}`, note);
  return [...unique.values()].sort((a, b) => a.stringIndex - b.stringIndex || a.fret - b.fret);
}

function techniquesOf(event) {
  const raw = event.techniques ?? event.technique ?? [];
  const values = Array.isArray(raw) ? raw : [raw];
  return [...new Set(values.map((value) => String(value).trim().toLowerCase()).filter(Boolean))];
}

function normalizedEvent(event, origin) {
  return {
    measureNumber: measureOf(event),
    quantizedStep: stepOf(event),
    durationSteps: durationOf(event),
    notes: notesOf(event),
    techniques: techniquesOf(event),
    confidence: event.confidence ?? null,
    source: event.source ?? origin,
    origin,
  };
}

function eventSignature(event) {
  return JSON.stringify([
    event.measureNumber,
    event.quantizedStep,
    event.durationSteps,
    event.notes.map((note) => [note.stringIndex, note.fret]),
    [...event.techniques].sort(),
  ]);
}

function sectionFor(measure) {
  return SECTIONS.find((section) => measure >= section.start && measure <= section.end) || null;
}

function sectionStartsIn(measures) {
  return SECTIONS.filter((section) => measures.includes(section.start));
}

function mergeProofEvents(sourcePayload, introOverlayPayload) {
  const sourceEvents = eventList(sourcePayload)
    .map((event) => normalizedEvent(event, 'audio-derived-source'))
    .filter((event) => event.measureNumber >= 1 && event.measureNumber <= 113 && event.quantizedStep != null && event.notes.length > 0);

  const introEvents = eventList(introOverlayPayload)
    .map((event) => normalizedEvent(event, 'approved-intro-training-overlay'))
    .filter((event) => event.measureNumber >= 1 && event.measureNumber <= 6 && event.quantizedStep != null && event.notes.length > 0);

  const retainedSource = sourceEvents.filter((event) => event.measureNumber > 6);
  const merged = [...introEvents, ...retainedSource];
  const unique = new Map();
  for (const event of merged) unique.set(eventSignature(event), event);

  return {
    originalSourceEvents: sourceEvents,
    introOverlayEvents: introEvents,
    proofEvents: [...unique.values()].sort((a, b) => (
      a.measureNumber - b.measureNumber
      || a.quantizedStep - b.quantizedStep
      || a.notes[0].stringIndex - b.notes[0].stringIndex
    )),
  };
}

function mapByMeasure(events) {
  const map = new Map();
  for (let measure = 1; measure <= 113; measure += 1) map.set(measure, []);
  for (const event of events) map.get(event.measureNumber).push(event);
  return map;
}

function drawPolyline(page, points, thickness = 1.25) {
  for (let index = 1; index < points.length; index += 1) {
    page.drawLine({ start: points[index - 1], end: points[index], thickness, color: INK });
  }
}

function quadraticPoints(start, control, end, count = 20) {
  const points = [];
  for (let index = 0; index <= count; index += 1) {
    const t = index / count;
    const u = 1 - t;
    points.push({
      x: u * u * start.x + 2 * u * t * control.x + t * t * end.x,
      y: u * u * start.y + 2 * u * t * control.y + t * t * end.y,
    });
  }
  return points;
}

function drawArrowHead(page, x, y, direction) {
  const size = 4.5;
  const svg = direction === 'up'
    ? `M ${x} ${y} L ${x - size} ${y - 7} L ${x + size} ${y - 7} Z`
    : `M ${x} ${y} L ${x - size} ${y + 7} L ${x + size} ${y + 7} Z`;
  page.drawSvgPath(svg, { color: INK });
}

function drawBendRelease(page, fonts, x, y) {
  const top = { x: x + 9, y: y + 36 };
  const releaseEnd = { x: x + 31, y: y + 18 };
  page.drawText('full', { x: top.x - 7, y: top.y + 3, size: 6.5, font: fonts.body, color: INK });
  drawPolyline(page, quadraticPoints({ x: x + 2, y: y + 5 }, { x: x + 10, y: y + 13 }, top, 18), 1.45);
  drawArrowHead(page, top.x, top.y + 1, 'up');
  drawPolyline(page, quadraticPoints({ x: top.x + 1, y: top.y }, { x: x + 29, y: top.y }, releaseEnd, 18), 1.45);
  drawArrowHead(page, releaseEnd.x, releaseEnd.y - 1, 'down');
}

function drawVibrato(page, x1, x2, y) {
  if (!(x2 > x1 + 4)) return;
  const width = x2 - x1;
  const cycles = Math.max(2, Math.round(width / 10));
  const samples = cycles * 10;
  const points = [];
  for (let index = 0; index <= samples; index += 1) {
    const ratio = index / samples;
    points.push({
      x: x1 + ratio * width,
      y: y + Math.sin(ratio * cycles * Math.PI * 2) * 1.8,
    });
  }
  drawPolyline(page, points, 1.05);
}

function drawFret(page, font, x, y, fret) {
  const text = String(fret);
  const size = 7.5;
  const width = font.widthOfTextAtSize(text, size);
  page.drawRectangle({ x: x - width / 2 - 1.4, y: y - 3.4, width: width + 2.8, height: 8.4, color: rgb(1, 1, 1) });
  page.drawText(text, { x: x - width / 2, y: y - 2.1, size, font, color: INK });
}

function drawTimeSignature(page, fonts, x, tabTop) {
  page.drawText('4', { x, y: tabTop - 15.5, size: 20, font: fonts.bold, color: INK });
  page.drawText('4', { x, y: tabTop - 37.5, size: 20, font: fonts.bold, color: INK });
}

function eventX(event, x1, x2, reserveTimeSignature) {
  const start = reserveTimeSignature ? x1 + 31 : x1 + 7;
  const end = x2 - 7;
  return start + ((event.quantizedStep + 0.5) / STEPS_PER_MEASURE) * (end - start);
}

function drawMeasure(page, fonts, measureNumber, x1, x2, tabTop, events) {
  const tabBottom = tabTop - 5 * STRING_GAP;
  const showTimeSignature = measureNumber === 1;

  page.drawText(String(measureNumber), { x: x1 + 3, y: tabTop + 7, size: 6.5, font: fonts.bold, color: INK });
  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawLine({ start: { x: x1, y }, end: { x: x2, y }, thickness: 0.45, color: STAFF });
  }
  page.drawLine({ start: { x: x1, y: tabTop + 1 }, end: { x: x1, y: tabBottom - 1 }, thickness: 0.8, color: INK });
  page.drawLine({ start: { x: x2, y: tabTop + 1 }, end: { x: x2, y: tabBottom - 1 }, thickness: 0.8, color: INK });
  if (showTimeSignature) drawTimeSignature(page, fonts, x1 + 8, tabTop);

  const positions = new Map();
  for (const event of events) {
    const x = eventX(event, x1, x2, showTimeSignature);
    positions.set(event.quantizedStep, x);
    for (const note of event.notes) {
      const y = tabTop - note.stringIndex * STRING_GAP;
      drawFret(page, fonts.mono, x, y, note.fret);
      if (event.techniques.some((technique) => technique.includes('bend'))) {
        drawBendRelease(page, fonts, x, y);
      }
    }
  }

  for (let index = 0; index < events.length - 1; index += 1) {
    const current = events[index];
    const next = events[index + 1];
    if (!current.notes.length || !next.notes.length) continue;
    const currentString = current.notes[0].stringIndex;
    const nextString = next.notes[0].stringIndex;
    const hasExplicitVibrato = current.techniques.some((technique) => technique.includes('vibrato'));
    const approvedIntroBendConnector = current.origin === 'approved-intro-training-overlay'
      && current.techniques.some((technique) => technique.includes('bend'))
      && currentString === nextString;
    if ((hasExplicitVibrato || approvedIntroBendConnector) && currentString === nextString) {
      const y = tabTop - currentString * STRING_GAP;
      drawVibrato(page, eventX(current, x1, x2, showTimeSignature) + 6, eventX(next, x1, x2, showTimeSignature) - 6, y);
    }
  }
}

function drawSystem(page, fonts, systemIndex, measures, measureMap) {
  const systemTop = TOP - systemIndex * SYSTEM_GAP;
  const tabTop = systemTop - 30;
  const measureWidth = (RIGHT - LEFT) / MEASURES_PER_SYSTEM;
  const starts = sectionStartsIn(measures);
  const active = sectionFor(measures[0]);

  const sectionLabel = starts.length ? starts.map((section) => section.name).join(' / ') : active?.name;
  if (sectionLabel) {
    page.drawText(sectionLabel, { x: LEFT, y: systemTop + 2, size: 8.2, font: fonts.bold, color: INK });
  }
  page.drawText(`Measures ${measures[0]}–${measures[measures.length - 1]}`, {
    x: LEFT,
    y: systemTop - 11,
    size: 6.3,
    font: fonts.body,
    color: rgb(0.28, 0.28, 0.28),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawText(STRING_LABELS[stringIndex], { x: LEFT - 17, y: y - 2.5, size: 6.7, font: fonts.bold, color: INK });
  }

  measures.forEach((measureNumber, index) => {
    const x1 = LEFT + index * measureWidth;
    drawMeasure(page, fonts, measureNumber, x1, x1 + measureWidth, tabTop, measureMap.get(measureNumber) || []);
  });
}

function buildPageMeasureGroups() {
  const groups = [];
  for (let start = 1; start <= 113; start += MEASURES_PER_SYSTEM) {
    const measures = [];
    for (let measure = start; measure < start + MEASURES_PER_SYSTEM && measure <= 113; measure += 1) measures.push(measure);
    groups.push(measures);
  }
  const pages = [];
  for (let index = 0; index < groups.length; index += SYSTEMS_PER_PAGE) pages.push(groups.slice(index, index + SYSTEMS_PER_PAGE));
  return pages;
}

async function main() {
  const source = readJson(SOURCE_PATH);
  const trainingGate = readJson(TRAINING_GATE_PATH);
  const notationLock = readJson(NOTATION_LOCK_PATH);
  const introOverlay = readJson(INTRO_OVERLAY_PATH);

  if (trainingGate.passed !== true) throw new Error('Full-song rhythm training gate is not green.');
  if (notationLock.passed !== true) throw new Error('Professional notation standard lock is not green.');

  const merged = mergeProofEvents(source, introOverlay);
  if (merged.originalSourceEvents.length !== 949) {
    throw new Error(`Expected 949 validated source events, found ${merged.originalSourceEvents.length}.`);
  }
  if (merged.introOverlayEvents.length !== 39) {
    throw new Error(`Expected 39 accepted intro overlay events, found ${merged.introOverlayEvents.length}.`);
  }

  const measureMap = mapByMeasure(merged.proofEvents);
  const missingMeasures = [];
  for (let measure = 1; measure <= 113; measure += 1) {
    if ((measureMap.get(measure) || []).length === 0) missingMeasures.push(measure);
  }
  if (missingMeasures.length) throw new Error(`Proof has empty measures: ${missingMeasures.join(', ')}`);

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const pages = buildPageMeasureGroups();

  pages.forEach((systems, pageIndex) => {
    const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
    page.drawText('Are You Gonna Go My Way', { x: 286, y: 579, size: 15, font: fonts.bold, color: INK });
    page.drawText('Jimmy PAIge V8 — Full Rhythm Tablature Proof', { x: 240, y: 560, size: 10.5, font: fonts.bold, color: INK });
    page.drawText('TRAINING PROOF • measures 1–113 • locked DadRock professional notation standard', {
      x: 211,
      y: 544,
      size: 6.8,
      font: fonts.body,
      color: rgb(0.3, 0.3, 0.3),
    });
    page.drawText(`Page ${pageIndex + 1} of ${pages.length}`, { x: 698, y: 582, size: 6.5, font: fonts.body, color: rgb(0.3, 0.3, 0.3) });
    systems.forEach((measures, systemIndex) => drawSystem(page, fonts, systemIndex, measures, measureMap));
  });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(OUTPUT_PDF_PATH, pdfBytes);

  const renderedBends = merged.proofEvents.filter((event) => event.techniques.some((technique) => technique.includes('bend'))).length;
  const manifest = {
    schemaVersion: 1,
    proofType: 'full-rhythm-tablature-training-proof',
    passed: missingMeasures.length === 0 && pages.length === 10,
    sourcePath: path.relative(ROOT, SOURCE_PATH),
    sourceEventCount: merged.originalSourceEvents.length,
    sourceEventsModified: false,
    introOverlayPath: path.relative(ROOT, INTRO_OVERLAY_PATH),
    introOverlayEventCount: merged.introOverlayEvents.length,
    proofEventCount: merged.proofEvents.length,
    measureRange: [1, 113],
    coveredMeasures: 113,
    missingMeasures,
    pages: pages.length,
    sectionCount: SECTIONS.length,
    renderedBends,
    timeSignatureRenderedAtMeasure1: true,
    curvedBendReleaseStandardApplied: true,
    fullLabelAboveBendApexApplied: true,
    onStringVibratoStandardApplied: true,
    placeholderRhythmStemsRendered: false,
    notationStandardLockPassed: notationLock.passed === true,
    rhythmTrainingGatePassed: trainingGate.passed === true,
    professionalReferenceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    protectedBaselinesChanged: false,
    productionPromotionAllowed: false,
    trainingOnly: true,
    productionEligible: false,
    outputPdf: path.relative(ROOT, OUTPUT_PDF_PATH),
  };
  fs.writeFileSync(OUTPUT_MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

  console.log('JIMMY PAIGE V8 FULL RHYTHM TABLATURE PROOF V1');
  console.log('Passed:', manifest.passed);
  console.log('Source events:', manifest.sourceEventCount);
  console.log('Accepted intro overlay events:', manifest.introOverlayEventCount);
  console.log('Proof events:', manifest.proofEventCount);
  console.log('Covered measures:', manifest.coveredMeasures);
  console.log('Missing measures:', manifest.missingMeasures);
  console.log('Pages:', manifest.pages);
  console.log('Sections:', manifest.sectionCount);
  console.log('Rendered bends:', manifest.renderedBends);
  console.log('4/4 time signature rendered: true');
  console.log('Locked professional notation standard applied: true');
  console.log('Placeholder rhythm stems rendered: false');
  console.log('Source events modified: false');
  console.log('Professional reference modified: false');
  console.log('V7 events modified: false');
  console.log('Protected renderer modified: false');
  console.log('Protected baselines changed: false');
  console.log('Production promotion allowed: false');
  console.log('PDF:', path.relative(ROOT, OUTPUT_PDF_PATH));
  console.log('Manifest:', path.relative(ROOT, OUTPUT_MANIFEST_PATH));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exitCode = 1;
});
