#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const V5_PATH = path.join(__dirname, 'build_gomyway_v8_professional_intro_notation_proof_v5.cjs');
const GENERATED_PATH = path.join(__dirname, '.generated_gomyway_v8_professional_intro_notation_proof_v6.cjs');

if (!fs.existsSync(V5_PATH)) {
  throw new Error(`Required V5 renderer not found: ${V5_PATH}`);
}

let source = fs.readFileSync(V5_PATH, 'utf8');

const replacements = [
  [
    "gomyway-v8-professional-intro-notation-proof-v5.pdf",
    "gomyway-v8-professional-intro-notation-proof-v6.pdf",
  ],
  [
    "gomyway-v8-professional-intro-notation-proof-v5-manifest.json",
    "gomyway-v8-professional-intro-notation-proof-v6-manifest.json",
  ],
  [
    "Jimmy PAIge V8 — Professional Intro Notation Proof V5",
    "Jimmy PAIge V8 — Professional Intro Notation Proof V6",
  ],
  [
    "JIMMY PAIGE V8 PROFESSIONAL INTRO NOTATION PROOF V5",
    "JIMMY PAIGE V8 PROFESSIONAL INTRO NOTATION PROOF V6",
  ],
  [
    "schemaVersion: 5,",
    "schemaVersion: 6,",
  ],
  [
    "x: bendTop.x - 10,\n    y: bendTop.y + 9,",
    "x: bendTop.x - 7,\n    y: bendTop.y + 3,",
  ],
  [
    "drawVisibleVibrato(page, positions.get(2) + 9, positions.get(4) - 9, stringY + 10);",
    "drawVisibleVibrato(page, positions.get(2) + 10, positions.get(4) - 10, stringY + 3.5);",
  ],
  [
    "curved bend/release • visible vibrato • clean tablature",
    "curved bend/release • lowered between-note vibrato • clean tablature",
  ],
];

for (const [before, after] of replacements) {
  if (!source.includes(before)) {
    throw new Error(`V6 renderer replacement target was not found:\n${before}`);
  }
  source = source.replace(before, after);
}

source = source.replace(
  "visibleVibratoConnectorsRendered: 6,",
  "visibleVibratoConnectorsRendered: 6,\n    vibratoVerticalPlacement: 'between-fret-numbers',\n    fullLabelPlacement: 'directly-above-bend-apex',",
);

fs.writeFileSync(GENERATED_PATH, source, 'utf8');

try {
  require(GENERATED_PATH);
} finally {
  process.on('beforeExit', () => {
    try {
      fs.unlinkSync(GENERATED_PATH);
    } catch {
      // The generated file is temporary and safe to leave if cleanup fails.
    }
  });
}
