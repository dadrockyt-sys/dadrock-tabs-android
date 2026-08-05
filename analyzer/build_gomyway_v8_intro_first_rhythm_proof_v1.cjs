#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  PDFDocument,
  StandardFonts,
  rgb,
} = require('pdf-lib');

const ROOT = path.resolve(__dirname, '..');
const EVENTS_PATH = path.join(
  ROOT,
  'public',
  'gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json',
);
const GATE_PATH = path.join(
  ROOT,
  'public',
  'gomyway-full-song-v8-rhythm-training-gate-v1.json',
);
const OUTPUT_PATH = path.join(
  ROOT,
  'public',
  'gomyway-v8-intro-first-rhythm-proof-v1.pdf',
);
const MANIFEST_PATH = path.join(
  ROOT,
  'public',
  'gomyway-v8-intro-first-rhythm-proof-v1-manifest.json',
);

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 82;
const RIGHT = 752;
const STRING_GAP = 10;
const STEPS_PER_MEASURE = 16;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const MEASURES = [1, 2, 3, 4, 5, 6];
const EXPECTED_STEPS = new Set([2, 4, 6, 9, 11, 14]);

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required file not found: ${filePath}`);
  }
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

function measureNumber(event) {
  return Math.trunc(numberValue(event.measureNumber ?? event.measure, 0));
}

function stepNumber(event) {
  return Math.max(0, Math.min(15, Math.trunc(numberValue(
    event.quantizedStep ?? event.step,
    0,
  ))));
}

function normalizeString(raw) {
  const value = Math.trunc(numberValue(raw, -1));
  if (value >= 1 && value <= 6) return value - 1;
  if (value >= 0 && value <= 5) return value;
  return null;
}

function eventNotes(event) {
  const source = Array.isArray(event.notes) ? event.notes : [event];
  const result = [];
  for (const note of source) {
    if (!note || typeof note !== 'object') continue;
    const stringIndex = normalizeString(note.string ?? note.stringIndex);
    const fret = Math.trunc(numberValue(note.fret, -1));
    if (stringIndex !== null && fret >= 0 && fret <= 24) {
      result.push({ stringIndex, fret });
    }
  }
  return result.sort((a, b) => a.stringIndex - b.stringIndex || a.fret - b.fret);
}

function normalizeEvent(event) {
  return {
    measure: measureNumber(event),
    step: stepNumber(event),
    duration: Math.max(1, Math.trunc(numberValue(event.durationSteps, 1))),
    notes: eventNotes(event),
    techniques: Array.isArray(event.techniques)
      ? [...new Set(event.techniques.map(String).filter(Boolean))]
      : [],
    source: String(event.source || ''),
  };
}

function signature(event) {
  return JSON.stringify({
    measure: event.measure,
    step: event.step,
    duration: event.duration,
    notes: event.notes,
    techniques: event.techniques,
  });
}

function buildMeasureMap(rawEvents) {
  const unique = new Map();
  let invalid = 0;
  for (const rawEvent of rawEvents) {
    if (!rawEvent || typeof rawEvent !== 'object') {
      invalid += 1;
      continue;
    }
    const event = normalizeEvent(rawEvent);
    if (!MEASURES.includes(event.measure) || event.notes.length === 0) continue;
    const key = signature(event);
    if (!unique.has(key)) unique.set(key, event);
  }

  const map = new Map();
  for (const event of unique.values()) {
    if (!map.has(event.measure)) map.set(event.measure, []);
    map.get(event.measure).push(event);
  }
  for (const events of map.values()) {
    events.sort((a, b) => a.step - b.step || a.duration - b.duration || signature(a).localeCompare(signature(b)));
  }
  return { map, invalid, uniqueEvents: [...unique.values()] };
}

function drawFret(page, font, x, y, fret) {
  const text = String(fret);
  const size = 9;
  const textWidth = font.widthOfTextAtSize(text, size);
  page.drawRectangle({
    x: x - textWidth / 2 - 2,
    y: y - 4,
    width: textWidth + 4,
    height: 10,
    color: rgb(1, 1, 1),
  });
  page.drawText(text, {
    x: x - textWidth / 2,
    y: y - 2.2,
    size,
    font,
    color: rgb(0.02, 0.02, 0.02),
  });
}

function techniqueText(techniques) {
  const aliases = {
    bend: 'full',
    vibrato: '~',
    slide: '/',
    hammerOn: 'h',
    pullOff: 'p',
    palmMute: 'P.M.',
    sustain: 'let ring',
    tie: 'tie',
  };
  return techniques.map((value) => aliases[value] || value).join(' ');
}

function drawDuration(page, x, tabBottom, duration) {
  const stemEnd = tabBottom - 22;
  page.drawLine({
    start: { x, y: tabBottom - 2 },
    end: { x, y: stemEnd },
    thickness: 0.8,
    color: rgb(0.12, 0.12, 0.12),
  });
  const flags = duration <= 1 ? 2 : duration <= 2 ? 1 : 0;
  for (let index = 0; index < flags; index += 1) {
    const y = stemEnd + index * 5;
    page.drawLine({
      start: { x, y },
      end: { x: x + 7, y: y - 3 },
      thickness: 0.9,
      color: rgb(0.12, 0.12, 0.12),
    });
  }
}

function drawMeasure(page, fonts, measure, x1, x2, tabTop, events) {
  const tabBottom = tabTop - 5 * STRING_GAP;
  page.drawText(String(measure), {
    x: x1 + 4,
    y: tabTop + 10,
    size: 8,
    font: fonts.bold,
    color: rgb(0.12, 0.12, 0.12),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawLine({
      start: { x: x1, y },
      end: { x: x2, y },
      thickness: 0.6,
      color: rgb(0.28, 0.28, 0.28),
    });
  }
  page.drawLine({
    start: { x: x1, y: tabTop + 2 },
    end: { x: x1, y: tabBottom - 2 },
    thickness: 1,
    color: rgb(0.08, 0.08, 0.08),
  });
  page.drawLine({
    start: { x: x2, y: tabTop + 2 },
    end: { x: x2, y: tabBottom - 2 },
    thickness: 1,
    color: rgb(0.08, 0.08, 0.08),
  });

  for (const event of events) {
    const x = x1 + 12 + ((event.step + 0.5) / STEPS_PER_MEASURE) * (x2 - x1 - 24);
    for (const note of event.notes) {
      drawFret(page, fonts.mono, x, tabTop - note.stringIndex * STRING_GAP, note.fret);
    }
    drawDuration(page, x, tabBottom, event.duration);

    if (event.techniques.length > 0) {
      const label = techniqueText(event.techniques).slice(0, 18);
      page.drawText(label, {
        x: Math.max(x1 + 3, Math.min(x - 6, x2 - 36)),
        y: tabTop + 10,
        size: 6,
        font: fonts.body,
        color: rgb(0.18, 0.18, 0.18),
      });
    }

    if (event.duration > 1) {
      const endStep = Math.min(16, event.step + event.duration);
      const endX = x1 + 12 + ((endStep + 0.25) / STEPS_PER_MEASURE) * (x2 - x1 - 24);
      page.drawLine({
        start: { x: x + 4, y: tabTop + 3 },
        end: { x: Math.max(x + 5, endX), y: tabTop + 3 },
        thickness: 0.5,
        color: rgb(0.25, 0.25, 0.25),
        dashArray: [2, 2],
      });
    }
  }
}

function drawSystem(page, fonts, systemIndex, measures, measureMap) {
  const systemTop = 442 - systemIndex * 148;
  const tabTop = systemTop - 24;
  const systemWidth = RIGHT - LEFT;
  const measureWidth = systemWidth / 2;

  page.drawText(`Measures ${measures[0]}–${measures[1]}`, {
    x: LEFT,
    y: systemTop + 6,
    size: 7,
    font: fonts.bold,
    color: rgb(0.18, 0.18, 0.18),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawText(STRING_LABELS[stringIndex], {
      x: LEFT - 20,
      y: y - 3,
      size: 7,
      font: fonts.bold,
      color: rgb(0.12, 0.12, 0.12),
    });
  }

  measures.forEach((measure, index) => {
    const x1 = LEFT + index * measureWidth;
    const x2 = x1 + measureWidth;
    drawMeasure(page, fonts, measure, x1, x2, tabTop, measureMap.get(measure) || []);
  });
}

async function main() {
  const gate = readJson(GATE_PATH);
  if (gate.passed !== true || gate.readyForRhythmTablatureProof !== true) {
    throw new Error('Rhythm training gate is not green; refusing to render proof.');
  }

  const source = readJson(EVENTS_PATH);
  const rawEvents = Array.isArray(source.events)
    ? source.events
    : Array.isArray(source.candidates)
      ? source.candidates
      : null;
  if (!rawEvents || rawEvents.length !== 949) {
    throw new Error('Expected exactly 949 recovered rhythm events.');
  }

  const built = buildMeasureMap(rawEvents);
  const missingMeasures = MEASURES.filter((measure) => !built.map.has(measure));
  const missingLockedSlots = [];
  const attackCounts = {};

  for (const measure of MEASURES) {
    const steps = new Set((built.map.get(measure) || []).map((event) => event.step));
    attackCounts[measure] = [...steps].sort((a, b) => a - b);
    for (const expectedStep of EXPECTED_STEPS) {
      if (!steps.has(expectedStep)) missingLockedSlots.push([measure, expectedStep]);
    }
  }

  if (missingMeasures.length > 0 || missingLockedSlots.length > 0) {
    throw new Error(
      `Intro proof prerequisites failed. Missing measures=${JSON.stringify(missingMeasures)} ` +
      `missing locked slots=${JSON.stringify(missingLockedSlots)}`,
    );
  }

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);

  page.drawText('Are You Gonna Go My Way', {
    x: 282,
    y: 574,
    size: 16,
    font: fonts.bold,
    color: rgb(0.03, 0.03, 0.03),
  });
  page.drawText('Jimmy PAIge V8 — Intro-First Rhythm Proof', {
    x: 265,
    y: 553,
    size: 11,
    font: fonts.bold,
    color: rgb(0.1, 0.1, 0.1),
  });
  page.drawText('J = 129   4/4   separated other.wav • 949-event protected training source', {
    x: 241,
    y: 536,
    size: 7.5,
    font: fonts.body,
    color: rgb(0.32, 0.32, 0.32),
  });
  page.drawText('INTRO', {
    x: LEFT,
    y: 498,
    size: 11,
    font: fonts.bold,
    color: rgb(0.08, 0.08, 0.08),
  });

  drawSystem(page, fonts, 0, [1, 2], built.map);
  drawSystem(page, fonts, 1, [3, 4], built.map);
  drawSystem(page, fonts, 2, [5, 6], built.map);

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(OUTPUT_PATH, pdfBytes);

  const renderedEvents = built.uniqueEvents.length;
  const manifest = {
    schemaVersion: 1,
    passed: true,
    gatePath: path.relative(ROOT, GATE_PATH),
    eventSourcePath: path.relative(ROOT, EVENTS_PATH),
    measures: MEASURES,
    sourceEvents: rawEvents.length,
    introUniqueRenderableEvents: renderedEvents,
    missingMeasures,
    missingLockedSlots,
    attackStepsByMeasure: attackCounts,
    pages: 1,
    pdfBytes: pdfBytes.length,
    candidateEventsModified: false,
    professionalReferenceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    productionPromotionAllowed: false,
    protectedBaselinesChanged: false,
  };
  fs.writeFileSync(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log('JIMMY PAIGE V8 INTRO-FIRST RHYTHM PROOF V1');
  console.log('Passed: true');
  console.log('Source events:', rawEvents.length);
  console.log('Intro unique renderable events:', renderedEvents);
  console.log('Measures:', MEASURES);
  console.log('Missing measures:', missingMeasures);
  console.log('Missing locked slots:', missingLockedSlots);
  console.log('Attack steps by measure:', attackCounts);
  console.log('Pages: 1');
  console.log('PDF bytes:', pdfBytes.length);
  console.log('Candidate events modified: false');
  console.log('Professional reference modified: false');
  console.log('V7 events modified: false');
  console.log('Protected renderer modified: false');
  console.log('Production promotion allowed: false');
  console.log('Protected baselines changed: false');
  console.log('Output PDF:', path.relative(ROOT, OUTPUT_PATH));
  console.log('Manifest:', path.relative(ROOT, MANIFEST_PATH));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exitCode = 1;
});
