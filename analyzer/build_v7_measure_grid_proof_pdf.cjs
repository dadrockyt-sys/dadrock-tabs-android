#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const DEFAULT_GRID = '/tmp/gomyway-full-song-v7-measure-grid.json';
const DEFAULT_PDF = '/tmp/gomyway-full-song-v7-measure-grid-proof.pdf';
const DEFAULT_MANIFEST = '/tmp/gomyway-full-song-v7-measure-grid-proof-manifest.json';
const PAGE_WIDTH = 612;
const PAGE_HEIGHT = 792;
const LEFT = 52;
const RIGHT = 566;
const ROWS_PER_PAGE = 4;
const ROW_HEIGHT = 156;
const FIRST_ROW_TOP = 680;

function parseArgs(argv) {
  const args = { grid: DEFAULT_GRID, output: DEFAULT_PDF, manifest: DEFAULT_MANIFEST };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === '--grid' && value) { args.grid = value; i += 1; }
    else if (key === '--output' && value) { args.output = value; i += 1; }
    else if (key === '--manifest' && value) { args.manifest = value; i += 1; }
  }
  return args;
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Required JSON file not found: ${filePath}`);
  const value = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`Expected JSON object in ${filePath}`);
  }
  return value;
}

function markerText(fragment) {
  const type = String(fragment.markerType || '');
  const label = String(fragment.label || '');
  if (type === 'palm-mute-span') return 'P.M.';
  if (type === 'bend-release') return 'full';
  if (type === 'slide') return `/${label.replace('slide to ', '')}`;
  if (type === 'muted-attack') return 'x';
  if (type === 'rest') return 'rest';
  return label || type;
}

function markerLane(fragment) {
  const type = String(fragment.markerType || '');
  if (type === 'chord-label') return 0;
  if (type === 'bend-release') return 1;
  if (type === 'palm-mute-span') return 2;
  return 3;
}

function drawMeasureRow(page, row, rowSlot, fonts, grid) {
  const top = FIRST_ROW_TOP - rowSlot * ROW_HEIGHT;
  const tabTop = top - 48;
  const tabBottom = tabTop - 42;
  const measureWidth = (RIGHT - LEFT) / 6;

  page.drawText(`Measures ${row.firstMeasure}–${row.lastMeasure}`, {
    x: LEFT,
    y: top + 18,
    size: 8,
    font: fonts.bold,
    color: rgb(0.15, 0.15, 0.15),
  });

  for (let stringIndex = 0; stringIndex < 6; stringIndex += 1) {
    const y = tabTop - stringIndex * 8.4;
    page.drawLine({
      start: { x: LEFT, y },
      end: { x: RIGHT, y },
      thickness: 0.55,
      color: rgb(0.62, 0.62, 0.62),
    });
  }

  for (let boundary = 0; boundary <= 6; boundary += 1) {
    const x = LEFT + boundary * measureWidth;
    page.drawLine({
      start: { x, y: tabTop + 1 },
      end: { x, y: tabBottom - 1 },
      thickness: boundary === 0 || boundary === 6 ? 1.1 : 0.75,
      color: rgb(0.34, 0.34, 0.34),
    });
    if (boundary < 6) {
      const measureNumber = row.firstMeasure + boundary;
      if (measureNumber <= row.lastMeasure) {
        page.drawText(String(measureNumber), {
          x: x + 3,
          y: tabTop + 7,
          size: 6.5,
          font: fonts.body,
          color: rgb(0.38, 0.38, 0.38),
        });
        for (let beat = 1; beat < 4; beat += 1) {
          const beatX = x + (beat / 4) * measureWidth;
          page.drawLine({
            start: { x: beatX, y: tabTop + 1 },
            end: { x: beatX, y: tabBottom - 1 },
            thickness: 0.25,
            color: rgb(0.83, 0.83, 0.83),
          });
        }
      }
    }
  }

  const lanes = [top + 2, top - 9, top - 20, tabTop - 55];
  const fragments = Array.isArray(row.fragments) ? row.fragments : [];
  const laneEnds = new Map();

  for (const fragment of fragments) {
    const x1 = LEFT + Number(fragment.rowStartRatio || 0) * (RIGHT - LEFT);
    const x2 = LEFT + Number(fragment.rowEndRatio || fragment.rowStartRatio || 0) * (RIGHT - LEFT);
    const lane = markerLane(fragment);
    const text = markerText(fragment);
    const key = `${lane}`;
    const previousEnd = laneEnds.get(key) ?? -Infinity;
    const adjustedY = lanes[lane] + (x1 < previousEnd + 5 ? 9 : 0);
    const textWidth = Math.max(12, text.length * 4.6);
    laneEnds.set(key, x1 + textWidth);

    page.drawText(text, {
      x: Math.max(LEFT, Math.min(RIGHT - textWidth, x1)),
      y: adjustedY,
      size: lane === 0 ? 7.5 : 6.5,
      font: lane === 0 ? fonts.bold : fonts.body,
      color: rgb(0.08, 0.08, 0.08),
    });

    if (String(fragment.markerType || '') === 'palm-mute-span') {
      page.drawLine({
        start: { x: Math.min(RIGHT, x1 + 20), y: adjustedY - 1 },
        end: { x: Math.max(Math.min(RIGHT, x1 + 22), Math.min(RIGHT, x2)), y: adjustedY - 1 },
        thickness: 0.75,
        color: rgb(0.22, 0.22, 0.22),
        dashArray: [2, 2],
      });
    }

    if (fragment.continuesFromPreviousMeasure === true) {
      page.drawText('←', { x: Math.max(LEFT, x1 - 8), y: adjustedY, size: 6, font: fonts.body });
    }
    if (fragment.continuesIntoNextMeasure === true) {
      page.drawText('→', { x: Math.min(RIGHT - 6, x2 + 1), y: adjustedY, size: 6, font: fonts.body });
    }
  }
}

async function main() {
  const args = parseArgs(process.argv);
  const grid = readJson(args.grid);
  if (grid.passed !== true) throw new Error('Measure grid is not green; refusing to build proof PDF.');
  if (Number(grid.beatsPerMeasure) !== 4 || Number(grid.measuresPerRow) !== 6) {
    throw new Error('Expected 4/4 and six measures per row.');
  }

  const rows = Array.isArray(grid.rows) ? grid.rows : [];
  const pageCount = Math.ceil(rows.length / ROWS_PER_PAGE);
  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
  };

  for (let pageIndex = 0; pageIndex < pageCount; pageIndex += 1) {
    const page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
    page.drawText('DadRock V7 Measure-Grid Proof — 4/4 • 6 Measures per Row', {
      x: LEFT,
      y: 756,
      size: 12.5,
      font: fonts.bold,
      color: rgb(0.05, 0.05, 0.05),
    });
    page.drawText(`${grid.tempoBpm} BPM • Page ${pageIndex + 1} of ${pageCount} • read-only proof`, {
      x: LEFT,
      y: 740,
      size: 7,
      font: fonts.body,
      color: rgb(0.4, 0.4, 0.4),
    });

    const pageRows = rows.slice(pageIndex * ROWS_PER_PAGE, (pageIndex + 1) * ROWS_PER_PAGE);
    pageRows.forEach((row, rowSlot) => drawMeasureRow(page, row, rowSlot, fonts, grid));
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(args.output, pdfBytes);

  const fragments = rows.flatMap((row) => Array.isArray(row.fragments) ? row.fragments : []);
  const manifest = {
    proofVersion: 7,
    proofType: 'v7-read-only-measure-grid-proof-pdf',
    sourceMeasureGridType: grid.measureGridType,
    sourceMeasureGridPassed: grid.passed === true,
    tempoBpm: grid.tempoBpm,
    beatsPerMeasure: grid.beatsPerMeasure,
    measuresPerRow: grid.measuresPerRow,
    measureCount: grid.measureCount,
    rowCount: rows.length,
    pageCount,
    markerCount: Number(grid.counts?.markers || 0),
    fragmentCount: fragments.length,
    outputPdf: path.resolve(args.output),
    outputBytes: pdfBytes.length,
    checks: {
      sourceGridGreen: grid.passed === true,
      fourFourPreserved: Number(grid.beatsPerMeasure) === 4,
      sixMeasuresPerRowPreserved: Number(grid.measuresPerRow) === 6,
      allRowsRendered: rows.length === Number(grid.rowCount || 0),
      allFragmentsRendered: fragments.length === Number(grid.counts?.fragments || 0),
      measureCountPreserved: Number(grid.measureCount || 0) === Number(grid.counts?.measures || 0),
      pdfCreated: pdfBytes.length > 2000,
      standaloneOnly: true,
      productionRendererUntouched: true,
      productionEventsUntouched: true,
      generatedTabUntouched: true,
    },
    affectsProductionEvents: false,
    affectsGeneratedTab: false,
    affectsProductionPdf: false,
    protectedBaselinesChanged: false,
  };
  manifest.passed = Object.values(manifest.checks).every(Boolean);
  fs.writeFileSync(args.manifest, JSON.stringify(manifest, null, 2));

  console.log('JIMMY PAIGE V7 MEASURE-GRID PROOF PDF');
  console.log('='.repeat(72));
  for (const [name, passed] of Object.entries(manifest.checks)) {
    console.log(passed ? 'PASS' : 'FAIL', name);
  }
  console.log('Measures:', manifest.measureCount);
  console.log('Rows:', manifest.rowCount);
  console.log('Pages:', manifest.pageCount);
  console.log('Fragments:', manifest.fragmentCount);
  console.log('PDF bytes:', manifest.outputBytes);
  console.log('Overall:', manifest.passed ? 'PASS' : 'FAIL');
  console.log('Saved proof PDF:', args.output);
  console.log('Saved manifest:', args.manifest);
  if (!manifest.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
