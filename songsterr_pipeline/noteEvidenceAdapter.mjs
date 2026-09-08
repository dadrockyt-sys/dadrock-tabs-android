import { buildStructureIdentity } from './structureIdentity.mjs';
import { snapTimestampToStructureMap } from './structureMap.mjs';

const EPSILON = 1e-9;
const SLOT_TOLERANCE_SECONDS = 1e-6;

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

function normalizeDurationEvidence(onset, onsetIndex, sourceStart, structureMap) {
  const hasEnd = onset?.sourceEnd !== undefined && onset?.sourceEnd !== null;
  const hasDuration = onset?.durationSeconds !== undefined && onset?.durationSeconds !== null;

  if (!hasEnd && !hasDuration) {
    return { sourceEnd: null, durationSeconds: null, durationConfidence: null };
  }

  let sourceEnd = hasEnd ? finite(onset.sourceEnd, `onsets[${onsetIndex}].sourceEnd`) : null;
  let durationSeconds = hasDuration ? finite(onset.durationSeconds, `onsets[${onsetIndex}].durationSeconds`) : null;

  if (durationSeconds !== null && durationSeconds <= 0) {
    throw new Error(`onsets[${onsetIndex}].durationSeconds must be positive.`);
  }
  if (sourceEnd !== null && sourceEnd <= sourceStart + EPSILON) {
    throw new Error(`onsets[${onsetIndex}].sourceEnd must be greater than sourceStart.`);
  }

  if (sourceEnd === null) sourceEnd = sourceStart + durationSeconds;
  if (durationSeconds === null) durationSeconds = sourceEnd - sourceStart;

  if (sourceEnd > structureMap.durationSeconds + EPSILON) {
    throw new Error(`onsets[${onsetIndex}] duration evidence falls outside structureMap.`);
  }
  if (hasEnd && hasDuration && Math.abs((sourceStart + durationSeconds) - sourceEnd) > SLOT_TOLERANCE_SECONDS) {
    throw new Error(`onsets[${onsetIndex}] sourceEnd and durationSeconds disagree.`);
  }

  const durationConfidence = onset?.durationConfidence === undefined || onset?.durationConfidence === null
    ? null
    : boundedConfidence(onset.durationConfidence, `onsets[${onsetIndex}].durationConfidence`);

  return { sourceEnd, durationSeconds, durationConfidence };
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
  const expectedSlot = snapTimestampToStructureMap(sourceStart, structureMap).projectedStart;
  if (Math.abs(nearestStructureSlot - expectedSlot) > SLOT_TOLERANCE_SECONDS) {
    throw new Error(`onsets[${onsetIndex}].nearestStructureSlot does not match frozen structureMap.`);
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

  const durationEvidence = normalizeDurationEvidence(onset, onsetIndex, sourceStart, structureMap);

  return {
    onsetId: onset?.onsetId ?? `onset-${onsetIndex}`,
    sourceStart,
    nearestStructureSlot,
    structureDisplacementSeconds: sourceStart - nearestStructureSlot,
    onsetConfidence: boundedConfidence(onset?.onsetConfidence ?? 0, `onsets[${onsetIndex}].onsetConfidence`),
    classification,
    selectedMidi: classification === 'unambiguous' ? Number(onset.selectedMidi) : null,
    confidenceMargin,
    ...durationEvidence,
    candidates,
    provenance: onset?.provenance && typeof onset.provenance === 'object' ? { ...onset.provenance } : {},
  };
}

function normalizeCapabilities(raw) {
  const capabilities = raw?.capabilities && typeof raw.capabilities === 'object' ? raw.capabilities : {};
  const rawDurationResolution = typeof capabilities.durationResolution === 'string'
    ? capabilities.durationResolution
    : '';
  const durationResolution = ['none', 'partial', 'complete'].includes(rawDurationResolution)
    ? rawDurationResolution
    : (rawDurationResolution.startsWith('partial-') ? 'partial' : 'undeclared');

  return {
    roleRelevanceResolved: capabilities.roleRelevanceResolved === true,
    polyphonyResolved: capabilities.polyphonyResolved === true,
    durationResolution,
    durationResolutionDetail: rawDurationResolution || 'undeclared',
    instrumentIsolation: typeof capabilities.instrumentIsolation === 'string'
      ? capabilities.instrumentIsolation
      : 'undeclared',
    confidenceCalibration: typeof capabilities.confidenceCalibration === 'string'
      ? capabilities.confidenceCalibration
      : 'undeclared',
  };
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
  onsets.forEach((onset) => {
    if (onset.classification !== 'unambiguous') return;
    const event = {
      evidenceOnsetId: onset.onsetId,
      midi: onset.selectedMidi,
      start: onset.sourceStart,
      evidenceConfidence: onset.candidates[0].confidence,
      onsetConfidence: onset.onsetConfidence,
      durationConfidence: onset.durationConfidence,
      provenance: {
        referenceBlind: true,
        structureIdentity: expectedIdentity.signature,
        noteEvidenceSource: raw?.provenance?.source ?? null,
      },
    };
    if (onset.sourceEnd !== null) event.end = onset.sourceEnd;
    if (onset.durationSeconds !== null) event.duration = onset.durationSeconds;
    promotedEvents.push(event);
  });

  const candidateCount = onsets.reduce((sum, onset) => sum + onset.candidates.length, 0);
  const ambiguousOnsetCount = onsets.filter((onset) => onset.classification === 'ambiguous').length;
  const noCandidateOnsetCount = onsets.filter((onset) => onset.classification === 'no-candidate').length;
  const unambiguousOnsetCount = onsets.filter((onset) => onset.classification === 'unambiguous').length;
  const durationResolvedEvidenceCount = onsets.filter((onset) => onset.durationSeconds !== null).length;
  const provenance = raw?.provenance && typeof raw.provenance === 'object' ? { ...raw.provenance } : {};
  const capabilities = normalizeCapabilities(raw);
  const analyzerDiagnostics = raw?.diagnostics && typeof raw.diagnostics === 'object'
    ? structuredClone(raw.diagnostics)
    : {};

  return {
    adapterContract: {
      name: 'songsterr-fresh-structure-conditioned-note-evidence',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
      nearestStructureSlotsVerified: true,
      syntheticDurationInference: false,
      legacyV143ScorerImported: provenance.legacyV143ScorerImported === true,
      modelInvoked: provenance.modelInvoked === true,
      gpuInvoked: provenance.gpuInvoked === true,
    },
    role: raw.role,
    structureIdentity: expectedIdentity,
    capabilities,
    analyzerDiagnostics,
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
      durationResolvedEvidenceCount,
      unresolvedDurationEvidenceCount: onsets.length - durationResolvedEvidenceCount,
    },
    provenance,
  };
}
