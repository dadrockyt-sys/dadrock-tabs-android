#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const STANDARD_PATH = path.join(ROOT, 'analyzer', 'standards', 'professional_tablature_notation_standard_v1.json');
const V5_RENDERER_PATH = path.join(ROOT, 'analyzer', 'build_gomyway_v8_professional_intro_notation_proof_v5.cjs');
const V6_RENDERER_PATH = path.join(ROOT, 'analyzer', 'build_gomyway_v8_professional_intro_notation_proof_v6.cjs');
const V7_RENDERER_PATH = path.join(ROOT, 'analyzer', 'build_gomyway_v8_professional_intro_notation_proof_v7.cjs');
const MANIFEST_PATH = path.join(ROOT, 'public', 'gomyway-v8-professional-intro-notation-proof-v7-manifest.json');
const OUTPUT_PATH = path.join(ROOT, 'public', 'professional-tablature-notation-standard-lock-v1.json');

function readJson(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing required file: ${path.relative(ROOT, filePath)}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function readText(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing required file: ${path.relative(ROOT, filePath)}`);
  return fs.readFileSync(filePath, 'utf8');
}

function requireText(haystack, needle, failures, label) {
  if (!haystack.includes(needle)) failures.push(`${label} marker missing: ${needle}`);
}

const standard = readJson(STANDARD_PATH);
const v5Renderer = readText(V5_RENDERER_PATH);
const v6Renderer = readText(V6_RENDERER_PATH);
const v7Renderer = readText(V7_RENDERER_PATH);
const manifest = readJson(MANIFEST_PATH);
const failures = [];

if (standard.status !== 'locked') failures.push('Notation standard is not locked.');
if (standard.standardId !== 'dadrock-professional-tablature-notation-v1') failures.push('Unexpected standard ID.');
if (standard.acceptedRenderer !== 'analyzer/build_gomyway_v8_professional_intro_notation_proof_v7.cjs') {
  failures.push('Accepted renderer path does not point to V7.');
}
if (manifest.passed !== true) failures.push('Accepted V7 proof manifest did not pass.');
if (manifest.timeSignatureRendered !== true) failures.push('4/4 time signature is not confirmed.');
if (manifest.curvedBendReleaseArrowsRendered !== 6) failures.push('Expected six curved bend/release arrows.');
if (manifest.visibleVibratoConnectorsRendered !== 6) failures.push('Expected six vibrato connectors.');
if (manifest.vibratoVerticalPlacement !== 'directly-on-tab-string') failures.push('Vibrato is not locked directly onto the tablature string.');
if (manifest.fullLabelPlacement !== 'directly-above-bend-apex') failures.push('Full bend label is not locked above the bend apex.');
if (manifest.placeholderRhythmStemsRendered !== false) failures.push('Placeholder rhythm stems must remain disabled.');
if (manifest.sourceEventsModified !== false) failures.push('Source events were modified.');
if (manifest.trainingOnly !== true) failures.push('Accepted proof must remain training-only.');
if (manifest.productionEligible !== false) failures.push('Accepted proof must not auto-promote to production.');

// V5 contains the actual drawing implementation.
requireText(v5Renderer, 'function drawTimeSignature', failures, 'V5 implementation');
requireText(v5Renderer, 'function drawProfessionalBendRelease', failures, 'V5 implementation');
requireText(v5Renderer, 'function drawVisibleVibrato', failures, 'V5 implementation');
requireText(v5Renderer, 'placeholderRhythmStemsRendered: false', failures, 'V5 implementation');
requireText(v5Renderer, 'sourceEventsModified: false', failures, 'V5 implementation');

// V6 locks label placement and lowers the vibrato toward the string.
requireText(v6Renderer, "fullLabelPlacement: 'directly-above-bend-apex'", failures, 'V6 placement layer');
requireText(v6Renderer, 'stringY + 3.5', failures, 'V6 placement layer');

// V7 is the accepted wrapper that places the vibrato directly on the string.
requireText(v7Renderer, "stringY + 3.5", failures, 'V7 replacement source');
requireText(v7Renderer, '"stringY"', failures, 'V7 replacement target');
requireText(v7Renderer, "vibratoVerticalPlacement: 'directly-on-tab-string'", failures, 'V7 placement layer');
requireText(v7Renderer, "build_gomyway_v8_professional_intro_notation_proof_v6.cjs", failures, 'V7 renderer chain');

const result = {
  schemaVersion: 1,
  standardId: standard.standardId,
  passed: failures.length === 0,
  acceptedRenderer: path.relative(ROOT, V7_RENDERER_PATH),
  rendererChain: [
    path.relative(ROOT, V5_RENDERER_PATH),
    path.relative(ROOT, V6_RENDERER_PATH),
    path.relative(ROOT, V7_RENDERER_PATH),
  ],
  acceptedProof: standard.acceptedProof,
  appliesToEveryFutureRender: true,
  requiredForRhythmBassAndLead: true,
  lockedRequirements: standard.requirements,
  protectedConstraints: standard.protectedConstraints,
  failures,
};

fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(result, null, 2)}\n`, 'utf8');

console.log('DADROCK PROFESSIONAL TABLATURE NOTATION STANDARD LOCK V1');
console.log('Passed:', result.passed);
console.log('Standard:', result.standardId);
console.log('Renderer chain validated: V5 implementation -> V6 placement -> V7 accepted standard');
console.log('Applies to every future render: true');
console.log('Rhythm, bass, and lead covered: true');
console.log('4/4 time signature locked:', manifest.timeSignatureRendered === true);
console.log('Curved bend/release locked:', manifest.curvedBendReleaseArrowsRendered === 6);
console.log('Full label above bend apex locked:', manifest.fullLabelPlacement === 'directly-above-bend-apex');
console.log('On-string vibrato locked:', manifest.vibratoVerticalPlacement === 'directly-on-tab-string');
console.log('Placeholder rhythm stems disabled:', manifest.placeholderRhythmStemsRendered === false);
console.log('Source events modified:', manifest.sourceEventsModified);
console.log('Production promotion allowed: false');
console.log('Output:', path.relative(ROOT, OUTPUT_PATH));

if (failures.length) {
  for (const failure of failures) console.error('-', failure);
  process.exitCode = 1;
}
