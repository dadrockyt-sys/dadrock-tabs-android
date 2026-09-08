import { buildStructureIdentity } from './structureIdentity.mjs';

const EPSILON = 1e-9;

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

function normalizeCandidate(candidate, onsetIndex, candidateIndex) {
  const midi = Number(candidate?.midi);
  if (!Number.isInteger(midi) || midi < 0 || midi > 127) {
    throw new Error(`onsets[${onsetIndex}].candidates[${candidateIndex}].midi must be an integer from 0 to 127.`);
  }
  return {
    candidateId: candidate?.candidateId ?? `onset-${onsetIndex}-candidate-${candidateIndex}`,
    midi,
    confidence: boundedConfidence(candidate?.confidence, `onsets[${onsetIndex}].candidates[${candidateIndex}].confidence`),
    spectralDb: candidate?.spectralDb === undefined || candidate?.spectralDb === null
      ? null
      : finite(candidate.spectralDb, `onsets[${onsetIndex}].candidates[${candidateIndex}].spectralDb`),
    prominenceDb: candidate?.prominenceDb === undefined || candidate?.prominenceDb === null
      ? null
      : finite(candidate.prominenceDb, `onsets[${onsetIndex}].candidates[${candidateIndex}].prominenceDb`),
    harmonicSupport: candidate?.harmonicSupport === undefined || candidate?.harmonicSupport === null
      ? null
      : boundedConfidence(candidate.harmonicSupport, `onsets[${onsetIndex}].candidates[${candidateIndex}].harmonicSupport`),
    provenance: candidate?.provenance && typeof candidate.provenance === 'object'
      ? { ...candidate.provenance }
      : {},
  };
}

function normalizeOnset(onset, onsetIndex, structureMap) {
  const sourceStart = finite(onset?.sourceStart, `onsets[${onsetIndex}].sourceStart`);
  if (sourceStart < -EPSILON || sourceStart > structureMap.durationSeconds + EPSILON) {
    throw new Error(`onsets[${onsetIndex}].sourceStart falls outside structureMap.`);
  }
  const nearestStructureSlot = finite(onset?.nearestStructureSlot, `onsets[${onsetIndex}].nearestStructureSlot`);
  if (nearestStructureSlot < -EPSILON || nearestStructureSlot > structureMap.durationSeconds + EPSILON) {
    throw new Error(`onsets[${onsetIndex}].nearestStructureSlot falls outside structureMap.`);
  }
  const candidates = Array.isArray(onset?.candidates)
    ? onset.candidates.map((candidate, candidateIndex) => normalizeCandidate(candidate, onsetIndex, candidateIndex))
    : [];
  const midiSeen = new Set();
  for (const candidate of candidates) {
    if (midiSeen.has(candidate.midi)) throw new Error(`onsets[${onsetIndex}] contains duplicate MIDI candidate ${candidate.midi}.`);
    midiSeen.add(candidate.midi);
  }
  candidates.sort((a, b) => b.confidence - a.confidence || a.midi - b.midi);
  const top = candidates[0] ?? null;
  const second = candidates[1] ?? null;
  const confidenceMargin = top ? top.confidence - (second?.confidence ?? 0) : null;
  const classification = onset?.classification;
  if (!['unambiguous', 'ambiguous', 'no-candidate'].includes(classification)) {
    throw new Error(`onsets[${onsetIndex}].classification is invalid.`);
  }
  if (classification === 'no-candidate' && candidates.length !== 0) {
    throw new Error(`onsets[${onsetIndex}] no-candidate classification cannot contain candidates.`);
  }
  if (classification !== 'no-candidate' && candidates.length === 0) {
    throw new Error(`onsets[${onsetIndex}] ${classification} classification requires candidates.`);
  }
  if (classification === 'unambiguous' && candidates.length > 0 && onset?.selectedMidi !== top.midi) {
    throw new Error(`onsets[${onsetIndex}].selectedMidi must equal its highest-confidence candidate.`);
  }
  return {
    onsetId: onset?.onsetId ?? `onset-${onsetIndex}`,
    sourceStart,
    nearestStructureSlot,
    structureDisplacementSeconds: sourceStart - nearestStructureSlot,
    onsetConfidence: boundedConfidence(onset?.onsetConfidence ?? 0, `onsets[${onsetIndex}].onsetConfidence`),
    classification,
    selectedMidi: classification === 'unambiguous' ? Number(onset.selectedMidi) : null,
    confidenceMargin,
    candidates,
    provenance: onset?.provenance && typeof onset.provenance === 'object' ? { ...onset.provenance } : {},
  };
}

function inferDuration(onsets, index, structureMap) {
  const current = onsets[index];
  const next = onsets[index + 1];
  if (next && next.sourceStart > current.sourceStart + EPSILON) {
    return Math.min(next.sourceStart - current.sourceStart, 2);
  }
  const remaining = structureMap.durationSeconds - current.sourceStart;
  return Math.min(Math.max(remaining, 0.05), 0.5);
}

export function adaptStructureConditionedNoteEvidence(raw = {}, structureMap) {
  if (!structureMap) throw new Error('structureMap is required.');
  if (raw?.version !== 1) throw new Error('note evidence version must be 1.');
  if (raw?.referenceBlind !== true) throw new Error('note evidence must be reference-blind.');
  if (raw?.structureFrozen !== true) throw new Error('note evidence must declare structureFrozen: true.');
  if (!['guitar', 'bass'].includes(raw?.role)) throw new Error('note evidence role must be guitar or bass.');

  const expectedIdentity = buildStructureIdentity(structureMap);
  if (raw?.structureIdentity?.contract !== expectedIdentity.contract
    || raw?.structureIdentity?.signature !== expectedIdentity.signature) {
    throw new Error('NOTE_EVIDENCE_STRUCTURE_IDENTITY_MISMATCH');
  }

  const onsets = Array.isArray(raw?.onsets)
    ? raw.onsets.map((onset, onsetIndex) => normalizeOnset(onset, onsetIndex, structureMap))
      .sort((a, b) => a.sourceStart - b.sourceStart || a.onsetId.localeCompare(b.onsetId))
    : [];

  const promotedEvents = [];
  onsets.forEach((onset, index) => {
    if (onset.classification !== 'unambiguous') return;
    promotedEvents.push({
      evidenceOnsetId: onset.onsetId,
      midi: onset.selectedMidi,
      start: onset.sourceStart,
      duration: inferDuration(onsets, index, structureMap),
      evidenceConfidence: onset.candidates[0].confidence,
      onsetConfidence: onset.onsetConfidence,
      provenance: {
        referenceBlind: true,
        structureIdentity: expectedIdentity.signature,
        noteEvidenceSource: raw?.provenance?.source ?? null,
      },
    });
  });

  const candidateCount = onsets.reduce((sum, onset) => sum + onset.candidates.length, 0);
  const ambiguousOnsetCount = onsets.filter((onset) => onset.classification === 'ambiguous').length;
  const noCandidateOnsetCount = onsets.filter((onset) => onset.classification === 'no-candidate').length;
  const unambiguousOnsetCount = onsets.filter((onset) => onset.classification === 'unambiguous').length;

  return {
    adapterContract: {
      name: 'songsterr-fresh-structure-conditioned-note-evidence',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
      legacyV143ScorerImported: false,
      modelInvoked: false,
    },
    role: raw.role,
    structureIdentity: expectedIdentity,
    onsets,
    promotedEvents,
    metrics: {
      onsetCount: onsets.length,
      candidateCount,
      unambiguousOnsetCount,
      ambiguousOnsetCount,
      noCandidateOnsetCount,
      promotedEventCount: promotedEvents.length,
      unresolvedOnsetCount: ambiguousOnsetCount + noCandidateOnsetCount,
      unresolvedEvidencePreserved: true,
    },
    provenance: raw?.provenance && typeof raw.provenance === 'object' ? { ...raw.provenance } : {},
  };
}
