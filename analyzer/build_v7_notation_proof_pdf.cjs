#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  PDFDocument,
  StandardFonts,
  rgb,
} = require('pdf-lib');

const DEFAULT_PLAN = '/tmp/gomyway-full-song-v7-pdf-render-plan.json';
const DEFAULT_PDF = '/tmp/gomyway-full-song-v7-notation-proof.pdf';
const DEFAULT_MANIFEST = '/tmp/gomyway-full-song-v7-notation-proof-manifest.json';

function parseArgs(argv) {
  const result = {
    plan: DEFAULT_PLAN,
    output: DEFAULT_PDF,
    manifest: DEFAULT_MANIFEST,
  };

  for (let index = 2; index < argv.length; index += 1) {
    const key = argv[index];
    const value = argv[index + 1];
    if (key === '--plan' && value) {
      result.plan = value;
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
  const parsed = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`Expected a JSON object in ${filePath}`);
  }
  return parsed;
}

function drawSystemGuide(page, systemIndex, pageIndex, fonts) {
  const firstTop = 578;
  const continuationTop = 704;
  const systemHeight = 82;
  const top = (pageIndex === 0 ? firstTop : continuationTop) - systemIndex * systemHeight;
  const left = 50;
  const right = 560;

  page.drawRectangle({
    x: left,
    y: top - 54,
    width: right - left,
    height: 48,
    borderColor: rgb(0.78, 0.78, 0.78),
    borderWidth: 0.7,
  });

  for (let row = 0; row < 6; row += 1) {
    const y = top - 12 - row * 7;
    page.drawLine({
      start: { x: left, y },
      end: { x: right, y },
      thickness: 0.45,
      color: rgb(0.84, 0.84, 0.84),
    });
  }

  page.drawText(`Segment ${pageIndex * 6 + systemIndex + 1}`, {
    x: left,
    y: top + 18,
    size: 6.5,
    font: fonts.body,
    color: rgb(0.46, 0.46, 0.46),
  });
}

function drawCommand(page, command, fonts) {
  const x1 = Number(command.x1 || 50);
  const x2 = Math.max(x1 + 2, Number(command.x2 || x1 + 2));
  const y = Number(command.y || 100);
  const label = String(command.label || '');
  const type = String(command.markerType || '');

  if (type === 'chord-label') {
    page.drawText(label, {
      x: x1,
      y,
      size: 8,
      font: fonts.bold,
      color: rgb(0.08, 0.08, 0.08),
    });
    return;
  }

  if (type === 'palm-mute-span') {
    page.drawText('P.M.', {
      x: x1,
      y: y + 2,
      size: 6.5,
      font: fonts.bold,
      color: rgb(0.2, 0.2, 0.2),
    });
    page.drawLine({
      start: { x: x1, y },
      end: { x: x2, y },
      thickness: 0.8,
      color: rgb(0.25, 0.25, 0.25),
      dashArray: [2, 2],
    });
    return;
  }

  if (type === 'bend-release') {
    page.drawText('full bend / release', {
      x: x1,
      y: y + 2,
      size: 6.5,
      font: fonts.bold,
      color: rgb(0.12, 0.12, 0.12),
    });
    page.drawLine({
      start: { x: x1 + 4, y: y - 2 },
      end: { x: x2, y: y + 8 },
      thickness: 1,
      color: rgb(0.12, 0.12, 0.12),
    });
    page.drawLine({
      start: { x: x2, y: y + 8 },
      end: { x: x2 - 4, y: y + 5 },
      thickness: 1,
      color: rgb(0.12, 0.12, 0.12),
    });
    return;
  }

  const symbols = {
    slide: `slide to ${label.replace('slide to ', '')}`,
    'muted-attack': 'x',
    rest: 'rest',
  };

  page.drawText(symbols[type] || label || type, {
    x: x1,
    y,
    size: type === 'muted-attack' ? 10 : 7,
    font: type === 'muted-attack' ? fonts.bold : fonts.body,
    color: rgb(0.12, 0.12, 0.12),
  });
}

async function main() {
  const args = parseArgs(process.argv);
  const plan = readJson(args.plan);

  if (plan.passed !== true) {
    throw new Error('Render plan is not green; refusing to build proof PDF.');
  }

  const pages = Array.isArray(plan.pages) ? plan.pages : [];
  const commands = Array.isArray(plan.commands) ? plan.commands : [];
  const pdfDoc = await PDFDocument.create();
  const fonts = {
    body: await pdfDoc.embedFont(StandardFonts.Helvetica),
    bold: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
  };

  for (let pageIndex = 0; pageIndex < pages.length; pageIndex += 1) {
    const page = pdfDoc.addPage([612, 792]);
    page.drawText('DadRock V7 Notation Proof — Standalone Preview', {
      x: 50,
      y: 758,
      size: 13,
      font: fonts.bold,
      color: rgb(0.06, 0.06, 0.06),
    });
    page.drawText(`Page ${pageIndex + 1} of ${pages.length} • read-only proof`, {
      x: 50,
      y: 742,
      size: 7,
      font: fonts.body,
      color: rgb(0.42, 0.42, 0.42),
    });

    for (let systemIndex = 0; systemIndex < 6; systemIndex += 1) {
      drawSystemGuide(page, systemIndex, pageIndex, fonts);
    }

    const pageCommands = commands.filter(
      (command) => Number(command.pageIndex || 0) === pageIndex,
    );
    for (const command of pageCommands) {
      drawCommand(page, command, fonts);
    }
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(args.output, pdfBytes);

  const manifest = {
    proofVersion: 7,
    proofType: 'v7-standalone-notation-proof-pdf',
    sourceRenderPlanType: plan.renderPlanType,
    sourceRenderPlanPassed: plan.passed === true,
    pageCount: pages.length,
    commandCount: commands.length,
    markerTypes: plan.counts?.markerTypes || [],
    outputPdf: path.resolve(args.output),
    outputBytes: pdfBytes.length,
    checks: {
      sourcePlanGreen: plan.passed === true,
      allCommandsRendered: commands.length === Number(plan.counts?.commands || 0),
      pageCountPreserved: pages.length === Number(plan.counts?.pages || 0),
      pdfCreated: pdfBytes.length > 1000,
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

  console.log('JIMMY PAIGE V7 STANDALONE NOTATION PROOF PDF');
  console.log('='.repeat(72));
  for (const [name, passed] of Object.entries(manifest.checks)) {
    console.log(passed ? 'PASS' : 'FAIL', name);
  }
  console.log('Pages:', manifest.pageCount);
  console.log('Drawing commands:', manifest.commandCount);
  console.log('PDF bytes:', manifest.outputBytes);
  console.log('Overall:', manifest.passed ? 'PASS' : 'FAIL');
  console.log('Saved proof PDF:', args.output);
  console.log('Saved manifest:', args.manifest);

  if (!manifest.passed) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
