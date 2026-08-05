#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const STANDARD_PATH = path.join(ROOT, 'analyzer', 'standards', 'professional_tablature_notation_standard_v1.json');
const RENDERER_PATH = path.join(ROOT, 'analyzer', 'build_gomyway_v8_professional_intro_notation_proof_v7.cjs');
const MANIFEST_PATH = path.join(ROOT, 'public', 'gomyway-v8-professional-intro-notation-proof-v7-manifest.json');
const OUTPUT_PATH = path.join(ROOT, 'public', 'professional-tablature-notation-standard-lock-v1.json');

function readJson(filePath) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing required file: ${path.relative(ROOT, filePath)}`);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function requireText(haystack, needle, failures) {
  if (!haystack.includes(needle)) failures.push(`Renderer marker missing: ${needle}`);
}

const standard = readJson(STANDARD_PATH);
if (!fs.existsSync(RENDERER_PATH)) throw new Error(`Missing accepted renderer: ${path.relative(ROOT, RENDERER_PATH)}`);
const renderer = fs.readFileSync(RENDERER_PATH, 'utf8');
const manifest = readJson(MANIFEST_PATH);
const failures = [];

if (standard.status !== 'locked') failures.push('Notation standard is not locked.');
if (standard.standardId !== 'dadrock-professional-tablature-notation-v1') failures.push('Unexpected standard ID.');
if (manifest.passed !== true) failures.push('Accepted V7 proof manifest did not pass.');
if (manifest.timeSignatureRendered !== true) failures.push('4/4 time signature is not confirmed.');
if (manifest.curvedBendReleaseArrowsRendered !== 6) failures.push('Expected six curved bend/release arrows.');
if (manifest.visibleVibratoConnectorsRendered !== 6) failures.push('Expected six vibrato connectors.');
if (manifest.placeholderRhythmStemsRendered !== false) failures.push('Placeholder rhythm stems must remain disabled.');
if (manifest.sourceEventsModified !== false) failures.push('Source events were modified.');
if (manifest.trainingOnly !== true) failures.push('Accepted proof must remain training-only.');
if (manifest.productionEligible !== false) failures.push('Accepted proof must not auto-promote to production.');

requireText(renderer, "drawTimeSignature", failures);
requireText(renderer, "drawProfessionalBendRelease", failures);
requireText(renderer, "drawVisibleVibrato", failures);
requireText(renderer, "stringY", failures);
requireText(renderer, "placeholderRhythmStemsRendered: false", failures);
requireText(renderer, "sourceEventsModified: false", failures);

const result = {
  schemaVersion: 1,
  standardId: standard.standardId,
  passed: failures.length === 0,
  acceptedRenderer: path.relative(ROOT, RENDERER_PATH),
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
console.log('Applies to every future render: true');
console.log('Rhythm, bass, and lead covered: true');
console.log('4/4 time signature locked:', manifest.timeSignatureRendered === true);
console.log('Curved bend/release locked:', manifest.curvedBendReleaseArrowsRendered === 6);
console.log('On-string vibrato locked:', manifest.visibleVibratoConnectorsRendered === 6);
console.log('Placeholder rhythm stems disabled:', manifest.placeholderRhythmStemsRendered === false);
console.log('Source events modified:', manifest.sourceEventsModified);
console.log('Production promotion allowed: false');
console.log('Output:', path.relative(ROOT, OUTPUT_PATH));

if (failures.length) {
  for (const failure of failures) console.error('-', failure);
  process.exitCode = 1;
}
