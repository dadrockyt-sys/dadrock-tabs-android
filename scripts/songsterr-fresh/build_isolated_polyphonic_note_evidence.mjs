#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { snapTimestampToStructureMap } from '../../songsterr_pipeline/structureMap.mjs';

const CONTRACT = 'songsterr-fresh-isolated-polyphonic-note-evidence-v1';
const EXPECTED_MODEL_CONTRACT = 'songsterr-fresh-basic-pitch-isolated-guitar-v1';
const EXPECTED_NOTE_IDENTITY_CONTRACT = 'songsterr-fresh-basic-pitch-note-identity-v1';
const EXPECTED_ACTIVATION_BUNDLE_CONTRACT = 'songsterr-fresh-basic-pitch-inference-bundle-v1';
const EXPECTED_CONTEXT_CONTRACT = 'songsterr-fresh-note-evidence-context-v1';
const PLAYABLE_MIDI_MIN = 40;
const PLAYABLE_MIDI_MAX = 88;

const [contextArg, modelNotesArg, outputArg] = process.argv.slice(2);
if (!contextArg || !modelNotesArg || !outputArg) {
  throw new Error(
    'Usage: build_isolated_polyphonic_note_evidence.mjs <context.json> <model-notes.json> <output.json>',
  );
}

function finite(value, field) {
  const number = Number(value);
  if (!Number.isFinite(number)) throw new Error(`${field} must be finite.`);
  return number;
}

function boundedConfidence(value, field) {
  const number = finite(value, field);
  if (number < 0 || number > 1) throw new Error(`${field} must be between 0 and 1.`);
  return number;
}

function validSha256(value) {
  return typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
}

const context = JSON.parse(await readFile(resolve(contextArg), 'utf8'));
const modelNotes = JSON.parse(await readFile(resolve(modelNotesArg), 'utf8'));

if (context?.contract !== EXPECTED_CONTEXT_CONTRACT
  || context?.version !== 1
  || context?.referenceBlind !== true
  || context?.structureFrozen !== true) {
  throw new Error('MODEL_NOTE_EVIDENCE_REQUIRES_FROZEN_REFERENCE_BLIND_CONTEXT');
}
if (context?.structureAcceptance?.accepted !== true) {
  throw new Error('MODEL_NOTE_EVIDENCE_REQUIRES_ACCEPTED_STRUCTURE');
}
if (modelNotes?.contract !== EXPECTED_MODEL_CONTRACT
  || modelNotes?.version !== 1
  || modelNotes?.referenceBlind !== true
  || modelNotes?.role !== 'guitar') {
  throw new Error('MODEL_NOTE_EVIDENCE_BASIC_PITCH_CONTRACT_MISMATCH');
}
if (modelNotes?.provenance?.modelInvoked !== true) {
  throw new Error('MODEL_NOTE_EVIDENCE_MUST_DECLARE_MODEL_INFERENCE');
}
if (modelNotes?.diagnostics?.modelNoteEndsUsedAsDuration !== false) {
  throw new Error('MODEL_NOTE_ENDS_MUST_NOT_OWN_DURATION');
}

const notes = Array.isArray(modelNotes?.notes) ? modelNotes.notes : [];
if (notes.length === 0) throw new Error('MODEL_NOTE_EVIDENCE_EMPTY');

const noteInferenceIdentity = modelNotes?.noteInferenceIdentity;
if (noteInferenceIdentity?.contract !== EXPECTED_NOTE_IDENTITY_CONTRACT
  || noteInferenceIdentity?.version !== 1
  || noteInferenceIdentity?.algorithm !== 'sha256'
  || Number(noteInferenceIdentity?.eventCount) !== notes.length
  || !validSha256(noteInferenceIdentity?.sha256)) {
  throw new Error('MODEL_NOTE_EVIDENCE_NOTE_IDENTITY_INVALID');
}

const activationEvidenceIdentity = modelNotes?.activationEvidenceIdentity ?? null;
if (activationEvidenceIdentity !== null) {
  if (activationEvidenceIdentity?.contract !== EXPECTED_ACTIVATION_BUNDLE_CONTRACT
    || activationEvidenceIdentity?.version !== 1
    || activationEvidenceIdentity?.algorithm !== 'sha256'
    || activationEvidenceIdentity?.noteIdentitySha256 !== noteInferenceIdentity.sha256
    || !validSha256(activationEvidenceIdentity?.activationMatrixSha256)
    || !validSha256(activationEvidenceIdentity?.frameTimesSha256)
    || !validSha256(activationEvidenceIdentity?.sha256)) {
    throw new Error('MODEL_NOTE_EVIDENCE_ACTIVATION_IDENTITY_INVALID');
  }
}

const structureMap = context.structureMap;
const durationSeconds = finite(structureMap?.durationSeconds, 'structureMap.durationSeconds');

const onsets = notes.map((note, index) => {
  const sourceStart = finite(note?.startSeconds, `notes[${index}].startSeconds`);
  const diagnosticModelEndSeconds = finite(
    note?.diagnosticModelEndSeconds,
    `notes[${index}].diagnosticModelEndSeconds`,
  );
  const midi = Number(note?.midi);
  const confidence = boundedConfidence(note?.confidence, `notes[${index}].confidence`);
  if (sourceStart < 0 || sourceStart > durationSeconds) {
    throw new Error(`notes[${index}].startSeconds falls outside frozen structure.`);
  }
  if (diagnosticModelEndSeconds <= sourceStart) {
    throw new Error(`notes[${index}].diagnosticModelEndSeconds must follow start.`);
  }
  if (!Number.isInteger(midi) || midi < PLAYABLE_MIDI_MIN || midi > PLAYABLE_MIDI_MAX) {
    throw new Error(`notes[${index}].midi falls outside supported guitar range.`);
  }

  const timing = snapTimestampToStructureMap(sourceStart, structureMap);
  const onsetId = note?.noteId ?? `basic-pitch-note-${String(index).padStart(6, '0')}`;
  return {
    onsetId,
    sourceStart,
    nearestStructureSlot: timing.projectedStart,
    onsetConfidence: confidence,
    classification: 'unambiguous',
    selectedMidi: midi,
    // Deliberately null: Basic Pitch note-off output remains diagnostic only.
    sourceEnd: null,
    durationSeconds: null,
    durationConfidence: null,
    candidates: [{
      candidateId: `${onsetId}-midi-${midi}`,
      midi,
      confidence,
      spectralDb: null,
      prominenceDb: null,
      harmonicSupport: null,
      provenance: {
        source: EXPECTED_MODEL_CONTRACT,
        modelNoteId: onsetId,
      },
    }],
    provenance: {
      source: EXPECTED_MODEL_CONTRACT,
      modelNoteId: onsetId,
      modelDiagnosticEndSeconds: diagnosticModelEndSeconds,
      modelEndUsedAsDuration: false,
      separationSource: modelNotes?.provenance?.separationSource ?? null,
    },
  };
}).sort((a, b) => a.sourceStart - b.sourceStart || a.selectedMidi - b.selectedMidi || a.onsetId.localeCompare(b.onsetId));

const diagnostics = {
  contract: CONTRACT,
  onsetCount: onsets.length,
  candidateCount: onsets.length,
  classificationCounts: {
    unambiguous: onsets.length,
    ambiguous: 0,
    'no-candidate': 0,
  },
  analysisMidiRange: [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
  playableMidiRange: [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
  sourceSeparation: modelNotes?.provenance?.separationSource ?? 'undeclared',
  sourceSeparationModelInvoked: true,
  polyphonicInference: modelNotes?.model ?? {},
  polyphonicStartClusterCount: Number(modelNotes?.diagnostics?.polyphonicStartClusterCount ?? 0),
  maxStartClusterSize: Number(modelNotes?.diagnostics?.maxStartClusterSize ?? 0),
  noteInferenceIdentity: { ...noteInferenceIdentity },
  activationEvidenceIdentity: activationEvidenceIdentity ? { ...activationEvidenceIdentity } : null,
  sameInferenceActivationEvidenceCaptured: activationEvidenceIdentity !== null,
  modelNoteEndsAreDiagnosticOnly: true,
  modelNoteEndsUsedAsDuration: false,
  durationEvidence: {
    authority: 'none-in-model-pitch-stage',
    resolvedCount: 0,
    nextOnsetUsedAsDuration: false,
    syntheticDurationInference: false,
  },
  confidenceCalibration: 'basic-pitch-note-amplitude-not-calibrated-probability',
};

const evidence = {
  contract: CONTRACT,
  version: 1,
  referenceBlind: true,
  structureFrozen: true,
  structureIdentity: { ...context.structureIdentity },
  role: 'guitar',
  capabilities: {
    roleRelevanceResolved: true,
    polyphonyResolved: true,
    durationResolution: 'none',
    instrumentIsolation: modelNotes?.provenance?.separationSource ?? 'demucs-guitar-stem',
    confidenceCalibration: 'basic-pitch-note-amplitude-not-calibrated-probability',
  },
  onsets,
  diagnostics,
  provenance: {
    source: CONTRACT,
    audioSource: modelNotes?.provenance?.audioSource ?? null,
    referenceBlind: true,
    structureConditioned: true,
    structureFrozen: true,
    roleConditioning: 'guitar-isolated-stem',
    sourceSeparationModelInvoked: true,
    sourceSeparationSource: modelNotes?.provenance?.separationSource ?? null,
    modelInvoked: true,
    gpuInvoked: modelNotes?.provenance?.gpuInvoked === true,
    noteInferenceIdentity: { ...noteInferenceIdentity },
    activationEvidenceIdentity: activationEvidenceIdentity ? { ...activationEvidenceIdentity } : null,
    activationEvidenceSameInference: activationEvidenceIdentity !== null,
    activationEvidenceActiveDurationAuthority: false,
    legacyV143ScorerImported: false,
    professionalScorerUsed: false,
    referenceTabUsed: false,
    modelNoteEndsUsedAsDuration: false,
    note: (
      'Role is established by an isolated guitar stem and polyphonic pitch identities come from Basic Pitch; '
      + 'model note-off times are retained only as diagnostics and the dedicated release stage remains sole duration authority.'
    ),
  },
};

await writeFile(resolve(outputArg), `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({
  contract: evidence.contract,
  structureIdentity: evidence.structureIdentity,
  capabilities: evidence.capabilities,
  diagnostics,
  provenance: evidence.provenance,
}));
