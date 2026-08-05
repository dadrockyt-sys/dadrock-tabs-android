#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const V6_PATH = path.join(__dirname, 'build_gomyway_v8_professional_intro_notation_proof_v6.cjs');
const GENERATED_PATH = path.join(__dirname, '.generated_gomyway_v8_professional_intro_notation_proof_v7.cjs');

if (!fs.existsSync(V6_PATH)) {
  throw new Error(`Required V6 renderer not found: ${V6_PATH}`);
}

let source = fs.readFileSync(V6_PATH, 'utf8');

const replacements = [
  [
    "gomyway-v8-professional-intro-notation-proof-v6.pdf",
    "gomyway-v8-professional-intro-notation-proof-v7.pdf",
  ],
  [
    "gomyway-v8-professional-intro-notation-proof-v6-manifest.json",
    "gomyway-v8-professional-intro-notation-proof-v7-manifest.json",
  ],
  [
    "Jimmy PAIge V8 — Professional Intro Notation Proof V6",
    "Jimmy PAIge V8 — Professional Intro Notation Proof V7",
  ],
  [
    "JIMMY PAIGE V8 PROFESSIONAL INTRO NOTATION PROOF V6",
    "JIMMY PAIGE V8 PROFESSIONAL INTRO NOTATION PROOF V7",
  ],
  [
    "schemaVersion: 6,",
    "schemaVersion: 7,",
  ],
  [
    "stringY + 3.5",
    "stringY",
  ],
  [
    "vibratoVerticalPlacement: 'between-fret-numbers'",
    "vibratoVerticalPlacement: 'directly-on-tab-string'",
  ],
  [
    "lowered between-note vibrato",
    "on-string between-note vibrato",
  ],
];

for (const [before, after] of replacements) {
  if (!source.includes(before)) {
    throw new Error(`V7 renderer replacement target was not found:\n${before}`);
  }
  source = source.replace(before, after);
}

fs.writeFileSync(GENERATED_PATH, source, 'utf8');

try {
  require(GENERATED_PATH);
} finally {
  process.on('beforeExit', () => {
    try {
      fs.unlinkSync(GENERATED_PATH);
    } catch {
      // Temporary generated renderer cleanup is best-effort only.
    }
  });
}
