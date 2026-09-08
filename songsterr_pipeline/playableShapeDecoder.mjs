import { enumeratePlayablePositions } from './index.mjs';

const EPSILON = 1e-9;

const ROLE_POLICIES = Object.freeze({
  lead: Object.freeze({ maxFrettedSpan: 5, maxStringSpan: 5, maxAdjacentFretDelta: 7, targetFret: 7, openStringWeight: 8, movementWeight: 3 }),
  rhythm: Object.freeze({ maxFrettedSpan: 4, maxStringSpan: 5, maxAdjacentFretDelta: 6, targetFret: 3, openStringWeight: -15, movementWeight: 2 }),
  bass: Object.freeze({ maxFrettedSpan: 4, maxStringSpan: 3, maxAdjacentFretDelta: 6, targetFret: 5, openStringWeight: -4, movementWeight: 3 }),
});

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function resolvePolicy(role, overrides = {}) {
  const base = ROLE_POLICIES[role];
  if (!base) throw new Error('instrumentConfig.role must be lead, rhythm, or bass.');
  const policy = { ...base, ...overrides };
  for (const field of ['maxFrettedSpan', 'maxStringSpan', 'maxAdjacentFretDelta', 'targetFret', 'movementWeight']) {
    policy[field] = finiteNumber(policy[field], `policy.${field}`);
    if (policy[field] < 0) throw new Error(`policy.${field} must be non-negative.`);
  }
  policy.openStringWeight = finiteNumber(policy.openStringWeight, 'policy.openStringWeight');
  return policy;
}

function shapeDiagnostics(assignments) {
  const frets = assignments.map((assignment) => assignment.fret);
  const fretted = frets.filter((fret) => fret > 0);
  const strings = assignments.map((assignment) => assignment.lowToHighIndex);
  const openStringCount = frets.filter((fret) => fret === 0).length;
  const frettedSpan = fretted.length <= 1 ? 0 : Math.max(...fretted) - Math.min(...fretted);
  const stringSpan = strings.length <= 1 ? 0 : Math.max(...strings) - Math.min(...strings);
  const centerFret = fretted.length === 0 ? 0 : fretted.reduce((sum, fret) => sum + fret, 0) / fretted.length;
  const sorted = assignments.slice().sort((a, b) => a.lowToHighIndex - b.lowToHighIndex);
  let maxAdjacentFretDelta = 0;
  for (let index = 1; index < sorted.length; index += 1) {
    maxAdjacentFretDelta = Math.max(maxAdjacentFretDelta, Math.abs(sorted[index].fret - sorted[index - 1].fret));
  }
  return {
    frettedSpan,
    stringSpan,
    openStringCount,
    centerFret,
    maxAdjacentFretDelta,
    minFret: Math.min(...frets),
    maxFret: Math.max(...frets),
  };
}

function rejectionReasons(diagnostics, policy) {
  const reasons = [];
  if (diagnostics.frettedSpan > policy.maxFrettedSpan + EPSILON) reasons.push('FRET_SPAN_EXCEEDED');
  if (diagnostics.stringSpan > policy.maxStringSpan + EPSILON) reasons.push('STRING_SPAN_EXCEEDED');
  if (diagnostics.maxAdjacentFretDelta > policy.maxAdjacentFretDelta + EPSILON) reasons.push('ADJACENT_STRETCH_EXCEEDED');
  return reasons;
}

function baseShapeScore(assignments, diagnostics, role, policy) {
  const fretted = assignments.filter((assignment) => assignment.fret > 0);
  const targetPenalty = fretted.length === 0
    ? policy.targetFret
    : fretted.reduce((sum, assignment) => sum + Math.abs(assignment.fret - policy.targetFret), 0) / fretted.length;
  const roleStringPenalty = role === 'bass' ? diagnostics.stringSpan * 16 : diagnostics.stringSpan * 8;
  return diagnostics.frettedSpan * 100
    + diagnostics.maxAdjacentFretDelta * 12
    + roleStringPenalty
    + targetPenalty
    + diagnostics.openStringCount * policy.openStringWeight
    + assignments.reduce((sum, assignment) => sum + assignment.fret, 0) * 0.001;
}

function contextualScore(candidate, policy, context) {
  let movementPenalty = 0;
  for (const value of [context?.previousCenterFret, context?.nextCenterFret]) {
    if (value !== undefined && value !== null) {
      movementPenalty += Math.abs(candidate.diagnostics.centerFret - finiteNumber(value, 'context center fret')) * policy.movementWeight;
    }
  }
  return candidate.localScore + movementPenalty;
}

function tieKey(assignments) {
  return assignments
    .map((assignment) => `${String(assignment.stringNumberHighToLow).padStart(2, '0')}:${String(assignment.fret).padStart(2, '0')}`)
    .join('|');
}

function collectPlayableShapes(midis, instrumentConfig, policy) {
  if (!Array.isArray(midis) || midis.length === 0) {
    return {
      resolved: false,
      reason: 'EMPTY_CHORD',
      candidates: [],
      candidateCount: 0,
      rejectedCandidateCount: 0,
      rejectionCounts: {},
      sourceMidis: Array.isArray(midis) ? [...midis] : [],
    };
  }

  if (midis.length > instrumentConfig.tuningMidi.length) {
    return {
      resolved: false,
      reason: 'MORE_NOTES_THAN_STRINGS',
      candidates: [],
      candidateCount: 0,
      rejectedCandidateCount: 0,
      rejectionCounts: {},
      sourceMidis: [...midis],
    };
  }

  const positionSets = midis.map((midi) => enumeratePlayablePositions(midi, instrumentConfig));
  if (positionSets.some((positions) => positions.length === 0)) {
    return {
      resolved: false,
      reason: 'UNPLAYABLE_PITCH',
      candidates: [],
      candidateCount: 0,
      rejectedCandidateCount: 0,
      rejectionCounts: {},
      sourceMidis: [...midis],
      unplayableMidis: midis.filter((_, index) => positionSets[index].length === 0),
    };
  }

  const order = midis
    .map((midi, index) => ({ index, midi, optionCount: positionSets[index].length }))
    .sort((a, b) => a.optionCount - b.optionCount || b.midi - a.midi || a.index - b.index);

  const assigned = new Array(midis.length).fill(null);
  const usedStrings = new Set();
  const candidates = [];
  let candidateCount = 0;
  let rejectedCandidateCount = 0;
  const rejectionCounts = {};

  function visit(depth) {
    if (depth === order.length) {
      candidateCount += 1;
      const assignments = assigned.map((assignment) => ({ ...assignment }));
      const diagnostics = shapeDiagnostics(assignments);
      const reasons = rejectionReasons(diagnostics, policy);
      if (reasons.length > 0) {
        rejectedCandidateCount += 1;
        for (const reason of reasons) rejectionCounts[reason] = (rejectionCounts[reason] ?? 0) + 1;
        return;
      }
      candidates.push({
        assignments,
        diagnostics,
        localScore: baseShapeScore(assignments, diagnostics, instrumentConfig.role, policy),
        tieKey: tieKey(assignments),
      });
      return;
    }

    const eventIndex = order[depth].index;
    for (const position of positionSets[eventIndex]) {
      if (usedStrings.has(position.lowToHighIndex)) continue;
      usedStrings.add(position.lowToHighIndex);
      assigned[eventIndex] = position;
      visit(depth + 1);
      assigned[eventIndex] = null;
      usedStrings.delete(position.lowToHighIndex);
    }
  }

  visit(0);
  candidates.sort((a, b) => a.localScore - b.localScore || a.tieKey.localeCompare(b.tieKey));

  return {
    resolved: candidates.length > 0,
    reason: candidates.length > 0 ? 'PLAYABLE_SHAPES_ENUMERATED' : 'NO_PLAYABLE_SHAPE_WITHIN_CONSTRAINTS',
    candidates,
    candidateCount,
    rejectedCandidateCount,
    rejectionCounts,
    sourceMidis: [...midis],
  };
}

export function enumeratePlayableShapes(midis, instrumentConfig, { policy: policyOverrides = {}, limit = 64 } = {}) {
  const policy = resolvePolicy(instrumentConfig?.role, policyOverrides);
  if (!Number.isInteger(limit) || limit < 1) throw new Error('limit must be a positive integer.');
  const collected = collectPlayableShapes(midis, instrumentConfig, policy);
  return {
    ...collected,
    policy,
    validCandidateCount: collected.candidates.length,
    candidates: collected.candidates.slice(0, limit),
  };
}

export function decodePlayableShape(midis, instrumentConfig, { policy: policyOverrides = {}, context = {} } = {}) {
  const policy = resolvePolicy(instrumentConfig?.role, policyOverrides);
  const collected = collectPlayableShapes(midis, instrumentConfig, policy);

  if (!collected.resolved) {
    return {
      resolved: false,
      reason: collected.reason,
      assignments: collected.reason === 'EMPTY_CHORD' ? [] : null,
      diagnostics: null,
      candidateCount: collected.candidateCount,
      rejectedCandidateCount: collected.rejectedCandidateCount,
      rejectionCounts: collected.rejectionCounts,
      policy,
      sourceMidis: collected.sourceMidis,
      unplayableMidis: collected.unplayableMidis,
    };
  }

  let best = null;
  for (const candidate of collected.candidates) {
    const score = contextualScore(candidate, policy, context);
    if (!best || score < best.score - EPSILON || (Math.abs(score - best.score) <= EPSILON && candidate.tieKey < best.candidate.tieKey)) {
      best = { score, candidate };
    }
  }

  return {
    resolved: true,
    reason: 'PLAYABLE_SHAPE_RESOLVED',
    assignments: best.candidate.assignments,
    diagnostics: {
      ...best.candidate.diagnostics,
      score: best.score,
      localScore: best.candidate.localScore,
      tieKey: best.candidate.tieKey,
    },
    candidateCount: collected.candidateCount,
    rejectedCandidateCount: collected.rejectedCandidateCount,
    rejectionCounts: collected.rejectionCounts,
    policy,
    sourceMidis: [...midis],
  };
}
