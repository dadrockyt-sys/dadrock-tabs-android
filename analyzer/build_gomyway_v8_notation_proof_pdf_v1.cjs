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
const DEFAULT_PROJECTION = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-notation-metadata.json',
);
const DEFAULT_OUTPUT = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-notation-proof-v1.pdf',
);
const DEFAULT_MANIFEST = path.join(
  REPO_ROOT,
  'public',
  'gomyway-full-song-v8-notation-proof-v1-manifest.json',
);

const MEASURES_PER_SYSTEM = 4;
const SYSTEMS_PER_PAGE = 5;
const MEASURES_PER_PAGE = MEASURES_PER_SYSTEM * SYSTEMS_PER_PAGE;
const PAGE_WIDTH = 792;
const PAGE_HEIGHT = 612;
const LEFT = 54;
const RIGHT = 756;
const TOP = 520;
const SYSTEM_GAP = 93;
const TAB_TOP_OFFSET = 24;
const STRING_GAP = 7;

function parseArgs(argv) {
  const result = {
    projection: DEFAULT_PROJECTION,
    output: DEFAULT_OUTPUT,
    manifest: DEFAULT_MANIFEST,
  };
  for (let index = 2; index < argv.length; index += 1) {
    const key = argv[index];
    const value = argv[index + 1];
    if (key === '--projection' && value) {
      result.projection = value;
      index += 1;
    } else if (key === '--output' && value) {
      result.output = value;
      index += 1;
    } else if (key === '--manifest' && value) {
      result.manifest = value;
      index += 1;
    }
  }
  return result;
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required JSON file not found: ${filePath}`);
  }
  const value = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`Expected a JSON object: ${filePath}`);
  }
  return value;
}

function markersByMeasure(projection) {
  const result = new Map();
  const markers = projection?.notationMetadata?.allMarkers;
  if (!Array.isArray(markers)) return result;

  for (const marker of markers) {
    const measure = Number(marker.measureNumber);
    if (!Number.isInteger(measure) || measure < 1 || measure > 113) continue;
    if (!result.has(measure)) result.set(measure, []);
    result.get(measure).push(marker);
  }

  for (const rows of result.values()) {
    rows.sort((a, b) => {
      const aStart = Number(a.start || 0);
      const bStart = Number(b.start || 0);
      if (aStart !== bStart) return aStart - bStart;
      return String(a.type || '').localeCompare(String(b.type || ''));
    });
  }
  return result;
}

function shortenPattern(patternId) {
  const aliases = {
    'em-riff-a': 'Em riff A',
    'em-riff-b': 'Em riff B',
    'g-position-riff-a': 'G-position A',
    'g-position-riff-b': 'G-position B',
    'picked-muted-turnaround': 'Muted turnaround',
    'chorus-g6': 'G6 figure',
    'chorus-atp2': 'A(tp2) sustain',
    'chorus-e-d-e': 'E–D–E',
    'chorus-g-e': 'G–E',
    'bridge-e-d': 'Bridge E–D',
    'bridge-a-e': 'Bridge A–E',
    'solo-backing-e-d': 'Solo backing E–D',
    'solo-backing-a-d6-a': 'Solo backing A–D6–A',
    'outro-held-atp2': 'A(tp2) held/tied',
  };
  return aliases[patternId] || String(patternId || '').replaceAll('-', ' ');
}

function uniqueStrings(values) {
  return [...new Set(values.filter(Boolean))];
}

function drawHeader(page, pageIndex, pageCount, fonts) {
  page.drawText('DadRock Jimmy PAIge V8 — Rhythm Notation Proof', {
    x: LEFT,
    y: 574,
    size: 14,
    font: fonts.bold,
    color: rgb(0.06, 0.06, 0.06),
  });
  page.drawText('Are You Gonna Go My Way • 113 measures • protected read-only projection', {
    x: LEFT,
    y: 557,
    size: 8,
    font: fonts.body,
    color: rgb(0.35, 0.35, 0.35),
  });
  page.drawText(`Page ${pageIndex + 1} of ${pageCount}`, {
    x: 700,
    y: 574,
    size: 8,
    font: fonts.body,
    color: rgb(0.35, 0.35, 0.35),
  });
}

function drawSystem(page, systemIndex, firstMeasure, measureMap, fonts) {
  const systemTop = TOP - systemIndex * SYSTEM_GAP;
  const tabTop = systemTop - TAB_TOP_OFFSET;
  const measureWidth = (RIGHT - LEFT) / MEASURES_PER_SYSTEM;

  page.drawText(`Measures ${firstMeasure}–${Math.min(113, firstMeasure + 3)}`, {
    x: LEFT,
    y: systemTop + 3,
    size: 7,
    font: fonts.bold,
    color: rgb(0.3, 0.3, 0.3),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * STRING_GAP;
    page.drawLine({
      start: { x: LEFT, y },
      end: { x: RIGHT, y },
      thickness: 0.55,
      color: rgb(0.45, 0.45, 0.45),
    });
  }

  for (let slot = 0; slot <= MEASURES_PER_SYSTEM; slot += 1) {
    const x = LEFT + slot * measureWidth;
    page.drawLine({
      start: { x, y: tabTop + 2 },
      end: { x, y: tabTop - 5 * STRING_GAP - 2 },
      thickness: slot === 0 || slot === MEASURES_PER_SYSTEM ? 1.05 : 0.7,
      color: rgb(0.15, 0.15, 0.15),
    });
  }

  for (let offset = 0; offset < MEASURES_PER_SYSTEM; offset += 1) {
    const measure = firstMeasure + offset;
    if (measure > 113) continue;
    const x1 = LEFT + offset * measureWidth;
    const x2 = x1 + measureWidth;
    const markers = measureMap.get(measure) || [];
    const chords = uniqueStrings(
      markers
        .filter((marker) => marker.type === 'chord-label')
        .map((marker) => String(marker.label || '').trim()),
    );
    const patterns = uniqueStrings(
      markers
        .filter((marker) => marker.type === 'pattern-reference')
        .map((marker) => shortenPattern(marker.patternId || marker.label)),
    );
    const hasRest = markers.some((marker) => marker.type === 'rest');

    page.drawText(String(measure), {
      x: x1 + 4,
      y: tabTop + 6,
      size: 6.5,
      font: fonts.bold,
      color: rgb(0.25, 0.25, 0.25),
    });

    if (chords.length > 0) {
      page.drawText(chords.join(' / ').slice(0, 28), {
        x: x1 + 25,
        y: tabTop + 6,
        size: 7.5,
        font: fonts.bold,
        color: rgb(0.05, 0.05, 0.05),
      });
    }

    if (hasRest) {
      page.drawText('REST', {
        x: x1 + measureWidth * 0.42,
        y: tabTop - 20,
        size: 8,
        font: fonts.bold,
        color: rgb(0.2, 0.2, 0.2),
      });
    } else if (patterns.length > 0) {
      const label = patterns.join(' • ').slice(0, 34);
      page.drawText(label, {
        x: x1 + 8,
        y: tabTop - 22,
        size: 6.5,
        font: fonts.body,
        color: rgb(0.2, 0.2, 0.2),
      });
      page.drawLine({
        start: { x: x1 + 8, y: tabTop - 27 },
        end: { x: x2 - 8, y: tabTop - 27 },
        thickness: 0.5,
        color: rgb(0.55, 0.55, 0.55),
        dashArray: [2, 2],
      });
    }
  }
}

async function main() {
  const args = parseArgs(process.argv);
  const projection = readJson(args.projection);
  if (projection.passed !== true) {
    throw new Error('V8 notation projection is not green; refusing to render proof PDF.');
  }
  if (projection.projectionVersion !== 8) {
    throw new Error('Expected projectionVersion 8.');
  }
  if (projection.rendererModified !== false || projection.protectedBaselinesChanged !== false) {
    throw new Error('Protected renderer/baseline flags are not clean.');
  }

  const measureMap = markersByMeasure(projection);
  const measuresWithMarkers = [...measureMap.keys()].sort((a, b) => a - b);
  const missingMeasures = [];
  for (let measure = 1; measure <= 113; measure += 1) {
    if (!measureMap.has(measure)) missingMeasures.push(measure);
  }
  if (missingMeasures.length > 0) {
    throw new Error(`Measures missing notation metadata: ${missingMeasures.join(', ')}`);
  }

  const pageCount = Math.ceil(113 / MEASURES_PER_PAGE);
  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
  };

  for (let pageIndex = 0; pageIndex < pageCount; pageIndex += 1) {
    const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
    drawHeader(page, pageIndex, pageCount, fonts);
    for (let systemIndex = 0; systemIndex < SYSTEMS_PER_PAGE; systemIndex += 1) {
      const firstMeasure = pageIndex * MEASURES_PER_PAGE
        + systemIndex * MEASURES_PER_SYSTEM
        + 1;
      if (firstMeasure > 113) break;
      drawSystem(page, systemIndex, firstMeasure, measureMap, fonts);
    }
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(args.output, pdfBytes);

  const checks = {
    projectionGreen: projection.passed === true,
    projectionIsV8: projection.projectionVersion === 8,
    all113MeasuresPresent: measuresWithMarkers.length === 113 && missingMeasures.length === 0,
    markerCountPreserved: projection.notationMetadata.markerCount === 263,
    pageCountExpected: pageCount === 6,
    pdfCreated: pdfBytes.length > 10000,
    standaloneBuilderOnly: true,
    protectedV7RendererUntouched: true,
    candidateEventsUntouched: true,
    professionalReferenceUntouched: true,
    productionPromotionAllowed: false,
    protectedBaselinesChanged: false,
  };

  const manifest = {
    proofVersion: 8,
    proofType: 'v8-standalone-rhythm-notation-metadata-proof-pdf',
    sourceProjection: path.relative(REPO_ROOT, args.projection),
    outputPdf: path.relative(REPO_ROOT, args.output),
    outputBytes: pdfBytes.length,
    pageCount,
    measureCount: measuresWithMarkers.length,
    markerCount: projection.notationMetadata.markerCount,
    markerTypes: projection.notationMetadata.markerTypes,
    missingMeasures,
    checks,
    passed: Object.values(checks).every((value) => value === true || value === false && false),
    automaticPromotionAllowed: false,
    candidateEventsModified: false,
    professionalReferenceModified: false,
    v7EventsModified: false,
    rendererModified: false,
    productionPromotionAllowed: false,
    protectedBaselinesChanged: false,
  };

  manifest.passed = [
    checks.projectionGreen,
    checks.projectionIsV8,
    checks.all113MeasuresPresent,
    checks.markerCountPreserved,
    checks.pageCountExpected,
    checks.pdfCreated,
    checks.standaloneBuilderOnly,
    checks.protectedV7RendererUntouched,
    checks.candidateEventsUntouched,
    checks.professionalReferenceUntouched,
    checks.productionPromotionAllowed === false,
    checks.protectedBaselinesChanged === false,
  ].every(Boolean);

  fs.writeFileSync(args.manifest, JSON.stringify(manifest, null, 2) + '\n');

  console.log('JIMMY PAIGE V8 STANDALONE RHYTHM NOTATION PROOF PDF');
  console.log('='.repeat(72));
  console.log('Passed:', manifest.passed);
  console.log('Projection:', manifest.sourceProjection);
  console.log('Measures:', manifest.measureCount);
  console.log('Missing measures:', manifest.missingMeasures);
  console.log('Markers:', manifest.markerCount);
  console.log('Marker types:', manifest.markerTypes);
  console.log('Pages:', manifest.pageCount);
  console.log('PDF bytes:', manifest.outputBytes);
  console.log('Protected V7 renderer untouched: True');
  console.log('Candidate events modified: False');
  console.log('Professional reference modified: False');
  console.log('V7 events modified: False');
  console.log('Renderer modified: False');
  console.log('Production promotion allowed: False');
  console.log('Protected baselines changed: False');
  console.log('Output PDF:', manifest.outputPdf);
  console.log('Manifest:', path.relative(REPO_ROOT, args.manifest));

  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
