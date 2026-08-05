#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  PDFDocument,
  StandardFonts,
  rgb,
} = require('pdf-lib');

const REPO_ROOT = path.resolve(__dirname, '..');
const INPUT_PATH = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-render-events-overlay-v1.json',
);
const OUTPUT_PATH = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-genuine-tablature-proof-v1.pdf',
);
const MANIFEST_PATH = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-genuine-tablature-proof-v1-manifest.json',
);

const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 68;
const RIGHT = 756;
const TOP = 520;
const MEASURES_PER_SYSTEM = 4;
const SYSTEMS_PER_PAGE = 4;
const MEASURES_PER_PAGE = MEASURES_PER_SYSTEM * SYSTEMS_PER_PAGE;
const SYSTEM_GAP = 112;
const STRING_GAP = 8;
const STEPS_PER_MEASURE = 16;
const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];

const SECTION_STARTS = new Map([
  [1, 'INTRO'],
  [17, 'VERSE 1'],
  [33, 'CHORUS 1'],
  [39, 'RIFF'],
  [47, 'VERSE 2'],
  [63, 'CHORUS 2'],
  [70, 'BRIDGE'],
  [78, 'SOLO RHYTHM BACKING'],
  [95, 'TRANSITION'],
  [103, 'OUT-CHORUS / ENDING'],
]);

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required input not found: ${filePath}`);
  }
  const value = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('Expected input JSON object.');
  }
  return value;
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
  return Math.trunc(numberValue(
    event.measureNumber ?? event.measure ?? event.barNumber ?? event.bar,
    0,
  ));
}

function eventNotes(event) {
  const result = [];
  if (Array.isArray(event.notes)) {
    for (const note of event.notes) {
      if (!note || typeof note !== 'object') continue;
      const string = numberValue(note.string ?? note.stringIndex);
      const fret = numberValue(note.fret);
      if (string !== null && fret !== null) {
        result.push({ string: Math.trunc(string), fret: Math.trunc(fret) });
      }
    }
  }

  if (result.length === 0) {
    const string = numberValue(event.string ?? event.stringIndex);
    const fret = numberValue(event.fret);
    if (string !== null && fret !== null) {
      result.push({ string: Math.trunc(string), fret: Math.trunc(fret) });
    }
  }
  return result;
}

function normalizeString(rawString) {
  // Most training artifacts use 1..6. Support 0..5 defensively.
  if (rawString >= 1 && rawString <= 6) return rawString - 1;
  if (rawString >= 0 && rawString <= 5) return rawString;
  return null;
}

function normalizedEvent(event) {
  const measure = measureNumber(event);
  const step = Math.max(0, Math.min(15, Math.trunc(numberValue(
    event.quantizedStep ?? event.step ?? event.positionInMeasure,
    0,
  ))));
  const duration = Math.max(1, Math.trunc(numberValue(event.durationSteps, 1)));
  const notes = eventNotes(event)
    .map((note) => ({
      stringIndex: normalizeString(note.string),
      fret: note.fret,
    }))
    .filter((note) => note.stringIndex !== null && note.fret >= 0 && note.fret <= 36)
    .sort((a, b) => a.stringIndex - b.stringIndex || a.fret - b.fret);
  const techniques = Array.isArray(event.techniques)
    ? [...new Set(event.techniques.map(String).filter(Boolean))].sort()
    : [];

  return {
    measure,
    step,
    duration,
    notes,
    techniques,
    overlay: event.source === 'read-only-consensus-overlay',
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
    const event = normalizedEvent(rawEvent);
    if (event.measure < 1 || event.measure > 113 || event.notes.length === 0) {
      invalid += 1;
      continue;
    }
    const key = signature(event);
    if (!unique.has(key)) unique.set(key, event);
  }

  const measureMap = new Map();
  for (const event of unique.values()) {
    if (!measureMap.has(event.measure)) measureMap.set(event.measure, []);
    measureMap.get(event.measure).push(event);
  }

  for (const events of measureMap.values()) {
    events.sort((a, b) => a.step - b.step || a.duration - b.duration || signature(a).localeCompare(signature(b)));
  }

  return {
    measureMap,
    uniqueEvents: [...unique.values()],
    invalid,
  };
}

function techniqueLabel(techniques) {
  const aliases = {
    bend: 'b',
    vibrato: '~',
    slide: '/',
    hammerOn: 'h',
    pullOff: 'p',
    palmMute: 'PM',
    mute: 'x',
    tie: 'tie',
    sustain: 'let ring',
  };
  return techniques.map((value) => aliases[value] || value).join(', ');
}

function drawHeader(page, pageIndex, pageCount, fonts) {
  page.drawText('DadRock Jimmy PAIge V8 — Genuine Rhythm Tablature Proof', {
    x: LEFT,
    y: 576,
    size: 14,
    font: fonts.bold,
    color: rgb(0.04, 0.04, 0.04),
  });
  page.drawText('Are You Gonna Go My Way • actual string/fret events • protected read-only render source', {
    x: LEFT,
    y: 558,
    size: 8,
    font: fonts.body,
    color: rgb(0.3, 0.3, 0.3),
  });
  page.drawText(`Page ${pageIndex + 1} of ${pageCount}`, {
    x: 700,
    y: 576,
    size: 8,
    font: fonts.body,
    color: rgb(0.3, 0.3, 0.3),
  });
}

function drawFret(page, fonts, x, y, fret, overlay) {
  const text = String(fret);
  const width = fonts.mono.widthOfTextAtSize(text, 7.5) + 3;
  page.drawRectangle({
    x: x - width / 2,
    y: y - 3.2,
    width,
    height: 8,
    color: rgb(1, 1, 1),
  });
  page.drawText(text, {
    x: x - fonts.mono.widthOfTextAtSize(text, 7.5) / 2,
    y: y - 1.4,
    size: 7.5,
    font: fonts.mono,
    color: overlay ? rgb(0.15, 0.15, 0.15) : rgb(0.02, 0.02, 0.02),
  });
}

function drawRhythmStem(page, x, tabBottom, duration) {
  const stemBottom = tabBottom - 18;
  page.drawLine({
    start: { x, y: tabBottom - 2 },
    end: { x, y: stemBottom },
    thickness: 0.7,
    color: rgb(0.15, 0.15, 0.15),
  });

  // Duration is expressed in sixteenth-note steps.
  if (duration <= 1) {
    page.drawLine({
      start: { x, y: stemBottom },
      end: { x: x + 6, y: stemBottom - 3 },
      thickness: 0.8,
      color: rgb(0.15, 0.15, 0.15),
    });
    page.drawLine({
      start: { x, y: stemBottom + 4 },
      end: { x: x + 6, y: stemBottom + 1 },
      thickness: 0.8,
      color: rgb(0.15, 0.15, 0.15),
    });
  } else if (duration <= 2) {
    page.drawLine({
      start: { x, y: stemBottom },
      end: { x: x + 6, y: stemBottom - 3 },
      thickness: 0.8,
      color: rgb(0.15, 0.15, 0.15),
    });
  }
}

function drawSystem(page, systemIndex, firstMeasure, measureMap, fonts) {
  const systemTop = TOP - systemIndex * SYSTEM_GAP;
  const tabTop = systemTop - 25;
  const tabBottom = tabTop - 5 * STRING_GAP;
  const measureWidth = (RIGHT - LEFT) / MEASURES_PER_SYSTEM;
  const section = SECTION_STARTS.get(firstMeasure);

  if (section) {
    page.drawText(section, {
      x: LEFT,
      y: systemTop + 8,
      size: 8,
      font: fonts.bold,
      color: rgb(0.1, 0.1, 0.1),
    });
  }

  page.drawText(`Measures ${firstMeasure}–${Math.min(113, firstMeasure + 3)}`, {
    x: LEFT,
    y: systemTop - 3,
    size: 6.5,
    font: fonts.body,
    color: rgb(0.38, 0.38, 0.38),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawText(STRING_LABELS[stringIndex], {
      x: LEFT - 16,
      y: y - 2.5,
      size: 6.5,
      font: fonts.bold,
      color: rgb(0.15, 0.15, 0.15),
    });
    page.drawLine({
      start: { x: LEFT, y },
      end: { x: RIGHT, y },
      thickness: 0.55,
      color: rgb(0.35, 0.35, 0.35),
    });
  }

  for (let slot = 0; slot <= MEASURES_PER_SYSTEM; slot += 1) {
    const x = LEFT + slot * measureWidth;
    page.drawLine({
      start: { x, y: tabTop + 2 },
      end: { x, y: tabBottom - 2 },
      thickness: slot === 0 || slot === MEASURES_PER_SYSTEM ? 1.1 : 0.75,
      color: rgb(0.1, 0.1, 0.1),
    });
  }

  for (let offset = 0; offset < MEASURES_PER_SYSTEM; offset += 1) {
    const measure = firstMeasure + offset;
    if (measure > 113) continue;
    const x1 = LEFT + offset * measureWidth;
    const x2 = x1 + measureWidth;
    const events = measureMap.get(measure) || [];

    page.drawText(String(measure), {
      x: x1 + 3,
      y: tabTop + 6,
      size: 6.5,
      font: fonts.bold,
      color: rgb(0.2, 0.2, 0.2),
    });

    if (events.length === 0) {
      page.drawText('REST / NO EVENT', {
        x: x1 + 28,
        y: tabTop - 22,
        size: 6.5,
        font: fonts.body,
        color: rgb(0.4, 0.4, 0.4),
      });
      continue;
    }

    for (const event of events) {
      const stepRatio = (event.step + 0.5) / STEPS_PER_MEASURE;
      const x = x1 + 8 + stepRatio * (measureWidth - 16);
      for (const note of event.notes) {
        const y = tabTop - note.stringIndex * STRING_GAP;
        drawFret(page, fonts, x, y, note.fret, event.overlay);
      }
      drawRhythmStem(page, x, tabBottom, event.duration);

      if (event.techniques.length > 0) {
        const label = techniqueLabel(event.techniques).slice(0, 16);
        page.drawText(label, {
          x: Math.min(x - 3, x2 - 30),
          y: tabTop + 7,
          size: 5.5,
          font: fonts.body,
          color: rgb(0.2, 0.2, 0.2),
        });
      }

      if (event.duration > 1) {
        const endStep = Math.min(16, event.step + event.duration);
        const endX = x1 + 8 + ((endStep + 0.25) / STEPS_PER_MEASURE) * (measureWidth - 16);
        page.drawLine({
          start: { x: x + 3, y: tabTop + 2 },
          end: { x: Math.max(x + 4, endX), y: tabTop + 2 },
          thickness: 0.45,
          color: rgb(0.3, 0.3, 0.3),
          dashArray: [2, 2],
        });
      }
    }
  }
}

async function main() {
  const source = readJson(INPUT_PATH);
  if (source.passed !== true) {
    throw new Error('Render-event overlay is not green; refusing to build tablature.');
  }
  if (!Array.isArray(source.renderEvents) || source.renderEvents.length !== 574) {
    throw new Error('Expected exactly 574 renderEvents.');
  }
  if (!Array.isArray(source.coveredMeasures) || source.coveredMeasures.length !== 113) {
    throw new Error('Expected complete 113-measure coverage.');
  }

  const built = buildMeasureMap(source.renderEvents);
  const missingMeasures = [];
  for (let measure = 1; measure <= 113; measure += 1) {
    if (!built.measureMap.has(measure)) missingMeasures.push(measure);
  }
  if (missingMeasures.length > 0) {
    throw new Error(`Renderable event map is missing measures: ${missingMeasures.join(', ')}`);
  }

  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
    mono: await pdfDoc.embedFont(StandardFonts.CourierBold),
  };
  const pageCount = Math.ceil(113 / MEASURES_PER_PAGE);

  for (let pageIndex = 0; pageIndex < pageCount; pageIndex += 1) {
    const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
    drawHeader(page, pageIndex, pageCount, fonts);
    for (let systemIndex = 0; systemIndex < SYSTEMS_PER_PAGE; systemIndex += 1) {
      const firstMeasure = pageIndex * MEASURES_PER_PAGE
        + systemIndex * MEASURES_PER_SYSTEM
        + 1;
      if (firstMeasure > 113) break;
      drawSystem(page, systemIndex, firstMeasure, built.measureMap, fonts);
    }
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(OUTPUT_PATH, pdfBytes);

  const overlayEvents = built.uniqueEvents.filter((event) => event.overlay);
  const manifest = {
    schemaVersion: 1,
    proofType: 'jimmy-paige-v8-genuine-event-tablature-proof',
    source: path.relative(REPO_ROOT, INPUT_PATH),
    outputPdf: path.relative(REPO_ROOT, OUTPUT_PATH),
    sourceEventCount: source.renderEvents.length,
    visuallyUniqueEventCount: built.uniqueEvents.length,
    sourceDuplicateSignaturesCollapsedForDrawing: source.renderEvents.length - built.uniqueEvents.length,
    invalidEventsSkipped: built.invalid,
    measureCount: built.measureMap.size,
    missingMeasures,
    overlayEventsRendered: overlayEvents.length,
    pageCount,
    outputBytes: pdfBytes.length,
    passed: (
      source.passed === true
      && source.renderEvents.length === 574
      && built.measureMap.size === 113
      && missingMeasures.length === 0
      && overlayEvents.length === 2
      && built.invalid === 0
      && pageCount === 8
      && pdfBytes.length > 20000
    ),
    automaticPromotionAllowed: false,
    candidateEventsModified: false,
    professionalReferenceModified: false,
    v7EventsModified: false,
    protectedRendererModified: false,
    productionPromotionAllowed: false,
    protectedBaselinesChanged: false,
  };

  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n');

  console.log('JIMMY PAIGE V8 GENUINE RHYTHM TABLATURE PROOF V1');
  console.log('='.repeat(72));
  console.log('Passed:', manifest.passed);
  console.log('Source events:', manifest.sourceEventCount);
  console.log('Visually unique events:', manifest.visuallyUniqueEventCount);
  console.log('Source duplicate signatures collapsed for drawing:', manifest.sourceDuplicateSignaturesCollapsedForDrawing);
  console.log('Invalid events skipped:', manifest.invalidEventsSkipped);
  console.log('Measures:', manifest.measureCount);
  console.log('Missing measures:', manifest.missingMeasures);
  console.log('Overlay events rendered:', manifest.overlayEventsRendered);
  console.log('Pages:', manifest.pageCount);
  console.log('PDF bytes:', manifest.outputBytes);
  console.log('Candidate events modified: False');
  console.log('Professional reference modified: False');
  console.log('V7 events modified: False');
  console.log('Protected renderer modified: False');
  console.log('Production promotion allowed: False');
  console.log('Protected baselines changed: False');
  console.log('Output PDF:', manifest.outputPdf);
  console.log('Manifest:', path.relative(REPO_ROOT, MANIFEST_PATH));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
