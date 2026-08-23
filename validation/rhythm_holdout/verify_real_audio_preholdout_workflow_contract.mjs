#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const outputPath = process.argv[2] || '';
const workflowPath = '.github/workflows/rhythm-professional-preholdout-real-audio.yml';
const canaryPath = 'analyzer/v143_ai_tab_product_canary_modal.py';
const [workflowSource, canarySource] = await Promise.all([
  fs.readFile(path.join(root, workflowPath), 'utf8'),
  fs.readFile(path.join(root, canaryPath), 'utf8'),
]);

function requireAll(label, source, patterns) {
  const missing = patterns.filter((pattern) => !source.includes(pattern));
  return { label, passed: missing.length === 0, missing };
}

function forbidAll(label, source, patterns) {
  const present = patterns.filter((pattern) => source.includes(pattern));
  return { label, passed: present.length === 0, forbiddenPresent: present };
}

const checks = [
  requireAll('approved-audio-and-product-analyzer', workflowSource, [
    'public/gomywayfullaitest.m4a',
    'analyzer/v143_ai_tab_product_canary_modal.py::run',
    '.preholdout/raw-product-output.json',
  ]),
  requireAll('product-canary-locked-to-approved-fixture', canarySource, [
    'APPROVED_FIXTURE = "public/gomywayfullaitest.m4a"',
    'source.as_posix() != APPROVED_FIXTURE',
    'This canary is locked to the approved repository fixture',
  ]),
  requireAll('product-canary-reuses-live-rhythm-image', canarySource, [
    'from v143_modal_live_endpoint import rhythm_image as live_rhythm_image',
    'canary_image = live_rhythm_image.add_local_python_source(',
    'live_rhythm_image',
  ]),
  requireAll('product-canary-complete-runtime-safety-flags', canarySource, [
    '"referenceFree": True',
    '"professionalReferenceUsed": False',
    '"referenceRuntimeInputUsed": False',
    '"runtimeLabelsRequired": False',
    '"productionModified": False',
    '"productionPromotionAuthorized": False',
  ]),
  requireAll('repository-local-esm-render-environment', workflowSource, [
    'mkdir -p .preholdout/esm',
    '.preholdout/esm/render-frozen.mjs',
    '.preholdout/esm/createV143RhythmPdf.mjs',
  ]),
  requireAll('freeze-before-render-sequence', workflowSource, [
    'prepare_rhythm_freeze_payload.mjs',
    'freeze_rhythm_analysis.py',
    '.preholdout/freeze/rhythm-frozen-analysis.json',
    'render_frozen_rhythm_pdf.mjs',
    'verify_pdf_event_fidelity.py',
  ]),
  requireAll('anti-leakage-proof-fields', workflowSource, [
    "'referenceFree': live.get('referenceFree') is True",
    "'professionalReferenceNotUsed': live.get('professionalReferenceUsed') is False",
    "'referenceRuntimeInputNotUsed': live.get('referenceRuntimeInputUsed') is False",
    "'humanReferenceStillSealed': True",
    "'realProfessionalReferenceOpened': False",
    "'professionalHumanScoreRun': False",
  ]),
  requireAll('exact-pdf-event-proof', workflowSource, [
    "'pdfRendererProjectionExact'",
    "'pdfEventFidelityExact'",
    "'pdfHashMatchesFrozenHash'",
    "'frozenEventSha256'",
    "'pdfEventSha256'",
  ]),
  requireAll('preview-full-artifacts-and-compact-proof', workflowSource, [
    '.preholdout/freeze/pdf/full-frozen-rhythm.pdf',
    '.preholdout/freeze/pdf/preview-frozen-rhythm.pdf',
    'debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json',
    'retention-days: 14',
  ]),
  requireAll('production-safety-fields', workflowSource, [
    "'productionUnmodified': canary.get('productionModified') is False",
    "'productionModified': False",
    "'productionPromotionAuthorized': False",
  ]),
  forbidAll('workflow-has-no-holdout-reference-path-or-tmp-renderer', workflowSource, [
    'validation/rhythm_holdout/reference/',
    '/tmp/rhythm-preholdout-static',
  ]),
  forbidAll('canary-has-no-holdout-reference-path', canarySource, [
    'validation/rhythm_holdout/reference/',
    'gomyway2_full_tab_reference.json',
    'gomyway_full_chord_sustain_reference.json',
  ]),
];

const failedChecks = checks.filter((check) => !check.passed);
const report = {
  schemaVersion: 2,
  gate: 'rhythm-real-audio-preholdout-workflow-contract',
  workflow: workflowPath,
  productCanarySource: canaryPath,
  approvedAudioFixture: 'public/gomywayfullaitest.m4a',
  productAnalyzer: 'analyzer/v143_ai_tab_product_canary_modal.py::run',
  rendererWorkspace: '.preholdout/esm',
  canaryReusesLiveRhythmImage:
    checks.find((check) => check.label === 'product-canary-reuses-live-rhythm-image')?.passed === true,
  canaryCompleteRuntimeSafetyFlags:
    checks.find((check) => check.label === 'product-canary-complete-runtime-safety-flags')?.passed === true,
  humanReferencePathPresent:
    workflowSource.includes('validation/rhythm_holdout/reference/') ||
    canarySource.includes('validation/rhythm_holdout/reference/'),
  tmpRendererWorkspacePresent: workflowSource.includes('/tmp/rhythm-preholdout-static'),
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
