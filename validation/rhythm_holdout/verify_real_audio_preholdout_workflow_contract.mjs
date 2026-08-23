#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const outputPath = process.argv[2] || '';
const workflowPath = '.github/workflows/rhythm-professional-preholdout-real-audio.yml';
const source = await fs.readFile(path.join(root, workflowPath), 'utf8');

function requireAll(label, patterns) {
  const missing = patterns.filter((pattern) => !source.includes(pattern));
  return { label, passed: missing.length === 0, missing };
}

function forbidAll(label, patterns) {
  const present = patterns.filter((pattern) => source.includes(pattern));
  return { label, passed: present.length === 0, forbiddenPresent: present };
}

const checks = [
  requireAll('approved-audio-and-product-analyzer', [
    'public/gomywayfullaitest.m4a',
    'analyzer/v143_ai_tab_product_canary_modal.py::run',
    '.preholdout/raw-product-output.json',
  ]),
  requireAll('repository-local-esm-render-environment', [
    'mkdir -p .preholdout/esm',
    '.preholdout/esm/render-frozen.mjs',
    '.preholdout/esm/createV143RhythmPdf.mjs',
  ]),
  requireAll('freeze-before-render-sequence', [
    'prepare_rhythm_freeze_payload.mjs',
    'freeze_rhythm_analysis.py',
    '.preholdout/freeze/rhythm-frozen-analysis.json',
    'render_frozen_rhythm_pdf.mjs',
    'verify_pdf_event_fidelity.py',
  ]),
  requireAll('anti-leakage-proof-fields', [
    "'referenceFree': live.get('referenceFree') is True",
    "'professionalReferenceNotUsed': live.get('professionalReferenceUsed') is False",
    "'referenceRuntimeInputNotUsed': live.get('referenceRuntimeInputUsed') is False",
    "'humanReferenceStillSealed': True",
    "'realProfessionalReferenceOpened': False",
    "'professionalHumanScoreRun': False",
  ]),
  requireAll('exact-pdf-event-proof', [
    "'pdfRendererProjectionExact'",
    "'pdfEventFidelityExact'",
    "'pdfHashMatchesFrozenHash'",
    "'frozenEventSha256'",
    "'pdfEventSha256'",
  ]),
  requireAll('preview-full-artifacts-and-compact-proof', [
    '.preholdout/freeze/pdf/full-frozen-rhythm.pdf',
    '.preholdout/freeze/pdf/preview-frozen-rhythm.pdf',
    'debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json',
    'retention-days: 14',
  ]),
  requireAll('production-safety-fields', [
    "'productionUnmodified': canary.get('productionModified') is False",
    "'productionModified': False",
    "'productionPromotionAuthorized': False",
  ]),
  forbidAll('no-holdout-reference-path-or-tmp-renderer', [
    'validation/rhythm_holdout/reference/',
    '/tmp/rhythm-preholdout-static',
  ]),
];

const failedChecks = checks.filter((check) => !check.passed);
const report = {
  schemaVersion: 1,
  gate: 'rhythm-real-audio-preholdout-workflow-contract',
  workflow: workflowPath,
  approvedAudioFixture: 'public/gomywayfullaitest.m4a',
  productAnalyzer: 'analyzer/v143_ai_tab_product_canary_modal.py::run',
  rendererWorkspace: '.preholdout/esm',
  humanReferencePathPresent: source.includes('validation/rhythm_holdout/reference/'),
  tmpRendererWorkspacePresent: source.includes('/tmp/rhythm-preholdout-static'),
  realProfessionalReferenceOpened: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  checks,
  failedChecks: failedChecks.map((check) => check.label),
  passed: failedChecks.length === 0,
};

if (outputPath) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
}

console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
