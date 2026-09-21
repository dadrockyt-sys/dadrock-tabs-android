import { adaptStructureConditionedNoteEvidence } from './noteEvidenceAdapter.mjs';
import { buildStructureIdentity } from './structureIdentity.mjs';
import { snapTimestampToStructureMap } from './structureMap.mjs';

const REQUESTED_ROLES = new Set(['lead', 'rhythm', 'bass']);
const ROLE_EVIDENCE_STATUSES = new Set(['complete', 'abstained']);
const PROMOTED_STREAMS = Object.freeze([
  ['promotedCore', 'promoted-core'],
  ['promotedTechnique', 'promoted-technique'],
  ['recoveredRecurringOnset', 'recovered-recurring-onset'],
]);
const ALL_STREAMS = Object.freeze([
  ...PROMOTED_STREAMS.map(([name]) => name),
  'ambiguous',
  'unassigned',
  'rejected',
]);

function require(condition, message) {
  if (!condition) throw new Error(message);
}

function finite(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function bounded(value, field) {
  const parsed = finite(value, field);
  if (parsed < 0 || parsed > 1) throw new Error(`${field} must be between 0 and 1.`);
  return parsed;
}

function array(value, field) {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value)) throw new Error(`${field} must be an array.`);
  return value;
}

function object(value, field) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${field} must be an object.`);
  }
  return value;
}

function normalizeId(value, fallback, seen) {
  const id = value === undefined || value === null ? fallback : String(value).trim();
  require(id.length > 0, 'role evidence event id must be non-empty.');
  require(!seen.has(id), `duplicate role evidence event id ${id}.`);
  seen.add(id);
  return id;
}

function nearestSlot(start, structureMap) {
  return snapTimestampToStructureMap(start, structureMap).projectedStart;
}

function durationFields(event, index) {
  const output = {};
  const hasEnd = event?.end !== undefined && event?.end !== null;
  const hasDuration = event?.duration !== undefined && event?.duration !== null;
  if (!hasEnd && !hasDuration) return output;

  const start = finite(event.start, `event[${index}].start`);
  let end = hasEnd ? finite(event.end, `event[${index}].end`) : null;
  let duration = hasDuration ? finite(event.duration, `event[${index}].duration`) : null;
  if (duration !== null) require(duration > 0, `event[${index}].duration must be positive.`);
  if (end !== null) require(end > start, `event[${index}].end must be greater than start.`);
  if (end === null) end = start + duration;
  if (duration === null) duration = end - start;
  output.sourceEnd = end;
  output.durationSeconds = duration;
  if (event.durationConfidence !== undefined && event.durationConfidence !== null) {
    output.durationConfidence = bounded(event.durationConfidence, `event[${index}].durationConfidence`);
  }
  return output;
}

function normalizeCandidate(candidate, field) {
  const midi = Number(candidate?.midi);
  require(Number.isInteger(midi) && midi >= 0 && midi <= 127, `${field}.midi must be an integer from 0 to 127.`);
  return {
    midi,
    confidence: bounded(candidate?.confidence, `${field}.confidence`),
    provenance: candidate?.provenance && typeof candidate.provenance === 'object'
      ? { ...candidate.provenance }
      : {},
  };
}

function promotedOnset(event, state, index, structureMap, seen) {
  const id = normalizeId(event?.id, `${state}-${index}`, seen);
  const start = finite(event?.start, `${state}[${index}].start`);
  const midi = Number(event?.midi);
  require(Number.isInteger(midi) && midi >= 0 && midi <= 127, `${state}[${index}].midi must be an integer from 0 to 127.`);
  const confidence = bounded(event?.confidence, `${state}[${index}].confidence`);
  const onsetConfidence = bounded(event?.onsetConfidence, `${state}[${index}].onsetConfidence`);
  return {
    onsetId: id,
    sourceStart: start,
    nearestStructureSlot: nearestSlot(start, structureMap),
    onsetConfidence,
    classification: 'unambiguous',
    evidenceState: state,
    selectedMidi: midi,
    candidates: [{
      candidateId: `${id}:selected`,
      midi,
      confidence,
      provenance: {
        ...(event?.provenance && typeof event.provenance === 'object' ? event.provenance : {}),
        evidenceState: state,
      },
    }],
    ...durationFields(event, index),
    provenance: {
      ...(event?.provenance && typeof event.provenance === 'object' ? event.provenance : {}),
      evidenceState: state,
    },
  };
}

function ambiguousOnset(event, index, structureMap, seen) {
  const id = normalizeId(event?.id, `ambiguous-${index}`, seen);
  const start = finite(event?.start, `ambiguous[${index}].start`);
  const candidates = array(event?.candidates, `ambiguous[${index}].candidates`)
    .map((candidate, candidateIndex) => normalizeCandidate(candidate, `ambiguous[${index}].candidates[${candidateIndex}]`));
  require(candidates.length > 0, `ambiguous[${index}] requires candidates.`);
  return {
    onsetId: id,
    sourceStart: start,
    nearestStructureSlot: nearestSlot(start, structureMap),
    onsetConfidence: bounded(event?.onsetConfidence, `ambiguous[${index}].onsetConfidence`),
    classification: 'ambiguous',
    evidenceState: 'ambiguous',
    selectedMidi: null,
    candidates,
    ...durationFields(event, index),
    provenance: {
      ...(event?.provenance && typeof event.provenance === 'object' ? event.provenance : {}),
      evidenceState: 'ambiguous',
    },
  };
}

function unassignedOnset(event, index, structureMap, seen) {
  const id = normalizeId(event?.id, `unassigned-${index}`, seen);
  const start = finite(event?.start, `unassigned[${index}].start`);
  return {
    onsetId: id,
    sourceStart: start,
    nearestStructureSlot: nearestSlot(start, structureMap),
    onsetConfidence: bounded(event?.onsetConfidence ?? 0, `unassigned[${index}].onsetConfidence`),
    classification: 'no-candidate',
    evidenceState: 'unassigned',
    selectedMidi: null,
    candidates: [],
    ...durationFields(event, index),
    provenance: {
      ...(event?.provenance && typeof event.provenance === 'object' ? event.provenance : {}),
      evidenceState: 'unassigned',
    },
  };
}

function rejectedOnset(event, index, structureMap, seen) {
  const id = normalizeId(event?.id, `rejected-${index}`, seen);
  const start = finite(event?.start, `rejected[${index}].start`);
  const candidates = array(event?.candidates, `rejected[${index}].candidates`)
    .map((candidate, candidateIndex) => normalizeCandidate(candidate, `rejected[${index}].candidates[${candidateIndex}]`));
  require(candidates.length > 0, `rejected[${index}] requires candidates.`);
  return {
    onsetId: id,
    sourceStart: start,
    nearestStructureSlot: nearestSlot(start, structureMap),
    onsetConfidence: bounded(event?.onsetConfidence, `rejected[${index}].onsetConfidence`),
    classification: 'rejected',
    evidenceState: 'rejected',
    selectedMidi: null,
    candidates,
    ...durationFields(event, index),
    provenance: {
      ...(event?.provenance && typeof event.provenance === 'object' ? event.provenance : {}),
      evidenceState: 'rejected',
    },
  };
}

function normalizeCapabilities(raw = {}, roleEvidenceStatus) {
  const input = raw && typeof raw === 'object' ? raw : {};
  return {
    roleRelevanceResolved: roleEvidenceStatus === 'complete',
    polyphonyResolved: input.polyphonyResolved === true,
    durationResolution: typeof input.durationResolution === 'string' ? input.durationResolution : 'none',
    instrumentIsolation: typeof input.instrumentIsolation === 'string'
      ? input.instrumentIsolation
      : (roleEvidenceStatus === 'complete' ? 'role-evidence-resolved' : 'unresolved'),
    confidenceCalibration: typeof input.confidenceCalibration === 'string'
      ? input.confidenceCalibration
      : 'heuristic-not-calibrated-probability',
  };
}

export function adaptRoleEvidenceStreams({
  requestedRole,
  roleEvidenceStatus,
  structureMap,
  streams = {},
  capabilities = {},
  provenance = {},
} = {}) {
  require(REQUESTED_ROLES.has(requestedRole), 'requestedRole must be lead, rhythm, or bass.');
  require(ROLE_EVIDENCE_STATUSES.has(roleEvidenceStatus), 'roleEvidenceStatus must be complete or abstained.');
  require(structureMap && typeof structureMap === 'object', 'structureMap is required.');
  const normalizedStreams = Object.fromEntries(
    ALL_STREAMS.map((name) => [name, array(streams?.[name], `streams.${name}`)]),
  );

  const promotedCount = PROMOTED_STREAMS.reduce(
    (sum, [name]) => sum + normalizedStreams[name].length,
    0,
  );
  if (roleEvidenceStatus === 'abstained' && promotedCount > 0) {
    throw new Error('ABSTAINED_ROLE_EVIDENCE_CANNOT_PROMOTE');
  }

  const seen = new Set();
  const onsets = [];
  for (const [name, state] of PROMOTED_STREAMS) {
    normalizedStreams[name].forEach((event, index) => {
      onsets.push(promotedOnset(event, state, index, structureMap, seen));
    });
  }
  normalizedStreams.ambiguous.forEach((event, index) => {
    onsets.push(ambiguousOnset(event, index, structureMap, seen));
  });
  normalizedStreams.unassigned.forEach((event, index) => {
    onsets.push(unassignedOnset(event, index, structureMap, seen));
  });
  normalizedStreams.rejected.forEach((event, index) => {
    onsets.push(rejectedOnset(event, index, structureMap, seen));
  });

  const raw = {
    version: 1,
    referenceBlind: true,
    structureFrozen: true,
    role: requestedRole === 'bass' ? 'bass' : 'guitar',
    structureIdentity: buildStructureIdentity(structureMap),
    onsets,
    capabilities: normalizeCapabilities(capabilities, roleEvidenceStatus),
    diagnostics: {
      requestedRole,
      roleEvidenceStatus,
      streamCounts: Object.fromEntries(ALL_STREAMS.map((name) => [name, normalizedStreams[name].length])),
    },
    provenance: {
      ...object(provenance, 'provenance'),
      source: provenance?.source ?? 'astra-role-evidence-integration-v1',
      requestedRole,
      roleEvidenceStatus,
      customerDeliveryEligible: false,
    },
  };

  const adapted = adaptStructureConditionedNoteEvidence(raw, structureMap);
  return {
    ...adapted,
    requestedRole,
    roleEvidenceStatus,
    integrationContract: {
      name: 'astra-role-evidence-integration',
      version: 1,
      referenceBlind: true,
      structureFrozen: true,
      explicitEvidenceStates: true,
      failClosedOnRoleAbstention: true,
      customerDeliveryEligible: false,
    },
    customerDeliveryEligible: false,
  };
}
