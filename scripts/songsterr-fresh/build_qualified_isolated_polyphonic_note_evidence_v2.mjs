#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { snapTimestampToStructureMap } from '../../songsterr_pipeline/structureMap.mjs';

const CONTRACT = 'songsterr-fresh-qualified-isolated-polyphonic-note-evidence-v2';
const EXPECTED_MODEL_CONTRACT = 'songsterr-fresh-basic-pitch-isolated-guitar-v1';
const EXPECTED_NOTE_IDENTITY_CONTRACT = 'songsterr-fresh-basic-pitch-note-identity-v1';
const EXPECTED_ACTIVATION_BUNDLE_CONTRACT = 'songsterr-fresh-basic-pitch-inference-bundle-v1';
const EXPECTED_CONTEXT_CONTRACT = 'songsterr-fresh-note-evidence-context-v1';
const EXPECTED_QUALIFICATION_CONTRACT = 'songsterr-fresh-model-note-qualification-v2';
const PLAYABLE_MIDI_MIN = 40;
const PLAYABLE_MIDI_MAX = 88;
const START_TOLERANCE_SECONDS = 1e-9;
const QUALIFICATION_STATUSES = new Set(['corroborated', 'rejected', 'insufficient']);

const [contextArg, modelNotesArg, qualificationArg, outputArg] = process.argv.slice(2);
if (!contextArg || !modelNotesArg || !qualificationArg || !outputArg) {
  throw new Error(
    'Usage: build_qualified_isolated_polyphonic_note_evidence_v2.mjs '
    + '<context.json> <model-notes.json> <qualification.json> <output.json>',
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

function normalizeNote(note, index, durationSeconds) {
  const noteId = note?.noteId;
  if (typeof noteId !== 'string' || noteId.length === 0) {
    throw new Error(`notes[${index}].noteId must be non-empty.`);
  }
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
  return {
    noteId,
    sourceStart,
    diagnosticModelEndSeconds,
    midi,
    confidence,
  };
}

const context = JSON.parse(await readFile(resolve(contextArg), 'utf8'));
const modelNotes = JSON.parse(await readFile(resolve(modelNotesArg), 'utf8'));
const qualification = JSON.parse(await readFile(resolve(qualificationArg), 'utf8'));

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

if (qualification?.contract !== EXPECTED_QUALIFICATION_CONTRACT
  || qualification?.version !== 2
  || qualification?.referenceBlind !== true) {
  throw new Error('MODEL_NOTE_QUALIFICATION_CONTRACT_MISMATCH');
}
if (qualification?.modelNoteIdentitySha256 !== noteInferenceIdentity.sha256) {
  throw new Error('MODEL_NOTE_QUALIFICATION_IDENTITY_MISMATCH');
}
if (qualification?.candidateConfidenceUsedForDecision !== false
  || qualification?.independentOfBasicPitchCandidateConfidence !== true) {
  throw new Error('MODEL_NOTE_QUALIFICATION_MUST_BE_CONFIDENCE_INDEPENDENT');
}
if (qualification?.referenceTabUsed === true) {
  throw new Error('MODEL_NOTE_QUALIFICATION_REFERENCE_TAB_FORBIDDEN');
}
if (typeof qualification?.method !== 'string' || qualification.method.length === 0) {
  throw new Error('MODEL_NOTE_QUALIFICATION_METHOD_REQUIRED');
}

const rows = Array.isArray(qualification?.proposals) ? qualification.proposals : [];
if (rows.length !== notes.length) {
  throw new Error('MODEL_NOTE_QUALIFICATION_POPULATION_MISMATCH');
}
const rowById = new Map();
for (const [index, row] of rows.entries()) {
  const noteId = row?.noteId;
  if (typeof noteId !== 'string' || noteId.length === 0) {
    throw new Error(`qualification.proposals[${index}].noteId must be non-empty.`);
  }
  if (rowById.has(noteId)) throw new Error('MODEL_NOTE_QUALIFICATION_DUPLICATE_NOTE_ID');
  const status = row?.status;
  if (!QUALIFICATION_STATUSES.has(status)) {
    throw new Error(`qualification.proposals[${index}].status is invalid.`);
  }
  rowById.set(noteId, row);
}

const structureMap = context.structureMap;
const durationSeconds = finite(structureMap?.durationSeconds, 'structureMap.durationSeconds');
const normalizedNotes = notes.map((note, index) => normalizeNote(note, index, durationSeconds));
const noteIds = new Set(normalizedNotes.map((note) => note.noteId));
if (noteIds.size !== normalizedNotes.length) throw new Error('MODEL_NOTE_IDENTITY_DUPLICATE_NOTE_ID');
for (const qualificationId of rowById.keys()) {
  if (!noteIds.has(qualificationId)) throw new Error('MODEL_NOTE_QUALIFICATION_EXTRA_NOTE_ID');
}

const onsets = normalizedNotes.map((note, index) => {
  const row = rowById.get(note.noteId);
  if (!row) throw new Error('MODEL_NOTE_QUALIFICATION_MISSING_NOTE_ID');

  const rowMidi = Number(row?.midi);
  const rowStart = finite(row?.startSeconds, `qualification.proposals[${index}].startSeconds`);
  if (rowMidi !== note.midi || Math.abs(rowStart - note.sourceStart) > START_TOLERANCE_SECONDS) {
    throw new Error('MODEL_NOTE_QUALIFICATION_NOTE_IDENTITY_FIELDS_MISMATCH');
  }

  const independentOnsetConfidence = boundedConfidence(
    row?.independentOnsetConfidence,
    `qualification.proposals[${index}].independentOnsetConfidence`,
  );
  const timing = snapTimestampToStructureMap(note.sourceStart, structureMap);
  const status = row.status;
  const classification = status === 'corroborated'
    ? 'unambiguous'
    : (status === 'rejected' ? 'rejected' : 'ambiguous');

  return {
    onsetId: note.noteId,
    sourceStart: note.sourceStart,
    nearestStructureSlot: timing.projectedStart,
    onsetConfidence: independentOnsetConfidence,
    classification,
    selectedMidi: status === 'corroborated' ? note.midi : null,
    sourceEnd: null,
    durationSeconds: null,
    durationConfidence: null,
    candidates: [{
      candidateId: `${note.noteId}-midi-${note.midi}`,
      midi: note.midi,
      confidence: note.confidence,
      spectralDb: null,
      prominenceDb: null,
      harmonicSupport: null,
      provenance: {
        source: EXPECTED_MODEL_CONTRACT,
        modelNoteId: note.noteId,
        candidateConfidenceDiagnosticOnly: true,
      },
    }],
    provenance: {
      source: EXPECTED_MODEL_CONTRACT,
      modelNoteId: note.noteId,
      modelDiagnosticEndSeconds: note.diagnosticModelEndSeconds,
      modelEndUsedAsDuration: false,
      separationSource: modelNotes?.provenance?.separationSource ?? null,
      qualification: {
        contract: EXPECTED_QUALIFICATION_CONTRACT,
        method: qualification.method,
        status,
        independentOnsetConfidence,
        candidateConfidenceUsedForDecision: false,
        independentOfBasicPitchCandidateConfidence: true,
        provenance: row?.provenance && typeof row.provenance === 'object' ? { ...row.provenance } : {},
      },
    },
  };
}).sort((a, b) => a.sourceStart - b.sourceStart || a.onsetId.localeCompare(b.onsetId));

const classificationCounts = onsets.reduce((counts, onset) => {
  counts[onset.classification] = (counts[onset.classification] ?? 0) + 1;
  return counts;
}, {
  unambiguous: 0,
  ambiguous: 0,
  'no-candidate': 0,
  rejected: 0,
});
const insufficientCount = classificationCounts.ambiguous;
const allProposalsResolved = insufficientCount === 0;

const diagnostics = {
  contract: CONTRACT,
  onsetCount: onsets.length,
  candidateCount: onsets.length,
  qualificationPopulationCount: rows.length,
  classificationCounts,
  promotedProposalCount: classificationCounts.unambiguous,
  rejectedProposalCount: classificationCounts.rejected,
  insufficientProposalCount: classificationCounts.ambiguous,
  allRawModelProposalsAccountedFor: true,
  qualificationPopulationIdentityVerified: true,
  candidateConfidenceUsedForQualification: false,
  candidateConfidenceDiagnosticOnly: true,
  analysisMidiRange: [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
  playableMidiRange: [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
  sourceSeparation: modelNotes?.provenance?.separationSource ?? 'undeclared',
  sourceSeparationModelInvoked: true,
  polyphonicInference: modelNotes?.model ?? {},
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
  qualification: {
    contract: EXPECTED_QUALIFICATION_CONTRACT,
    method: qualification.method,
    candidateConfidenceUsedForDecision: false,
    independentOfBasicPitchCandidateConfidence: true,
    referenceTabUsed: false,
  },
  confidenceCalibration: 'basic-pitch-note-amplitude-not-calibrated-probability',
};

const evidence = {
  contract: CONTRACT,
  // Evidence schema remains version 1 so the deterministic adapter can consume it unchanged.
  version: 1,
  referenceBlind: true,
  structureFrozen: true,
  structureIdentity: { ...context.structureIdentity },
  role: 'guitar',
  capabilities: {
    roleRelevanceResolved: true,
    polyphonyResolved: allProposalsResolved,
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
    modelValidationComplete: modelNotes?.provenance?.modelValidationComplete === true,
    noteInferenceIdentity: { ...noteInferenceIdentity },
    activationEvidenceIdentity: activationEvidenceIdentity ? { ...activationEvidenceIdentity } : null,
    activationEvidenceSameInference: activationEvidenceIdentity !== null,
    activationEvidenceActiveDurationAuthority: false,
    qualificationContract: EXPECTED_QUALIFICATION_CONTRACT,
    qualificationMethod: qualification.method,
    qualificationIdentityBound: true,
    candidateConfidenceUsedForQualification: false,
    allRawModelProposalsAccountedFor: true,
    legacyV143ScorerImported: false,
    professionalScorerUsed: false,
    referenceTabUsed: false,
    modelNoteEndsUsedAsDuration: false,
    note: (
      'Basic Pitch emissions remain raw candidates. Promotion requires exact-identity, reference-blind V2 '
      + 'qualification independent of Basic Pitch confidence; clip-start proposals use only genuine post-onset '
      + 'audio and never fabricated pre-context. Rejected proposals remain preserved.'
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
