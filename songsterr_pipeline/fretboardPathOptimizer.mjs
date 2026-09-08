import { enumeratePlayableShapes } from './playableShapeDecoder.mjs';

const EPSILON = 1e-9;

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function stringSet(candidate) {
  return new Set(candidate.assignments.map((assignment) => assignment.lowToHighIndex));
}

function symmetricDifferenceSize(left, right) {
  let count = 0;
  for (const value of left) if (!right.has(value)) count += 1;
  for (const value of right) if (!left.has(value)) count += 1;
  return count;
}

function transitionCost(previous, current, weights) {
  const centerMovement = Math.abs(current.diagnostics.centerFret - previous.diagnostics.centerFret);
  const stringChanges = symmetricDifferenceSize(stringSet(previous), stringSet(current));
  return {
    centerMovement,
    stringChanges,
    cost: centerMovement * weights.centerMovement + stringChanges * weights.stringSetChange,
  };
}

function stateKey(pathKeys) {
  return pathKeys.join('>');
}

export function optimizeFretboardPath({
  onsetGroups,
  instrumentConfig,
  policy = {},
  maxCandidatesPerOnset = 24,
  weights = {},
} = {}) {
  if (!Array.isArray(onsetGroups)) throw new Error('onsetGroups must be an array.');

  const resolvedWeights = {
    centerMovement: finiteNumber(weights.centerMovement ?? 20, 'weights.centerMovement'),
    stringSetChange: finiteNumber(weights.stringSetChange ?? 2, 'weights.stringSetChange'),
    localShape: finiteNumber(weights.localShape ?? 0.1, 'weights.localShape'),
  };

  const candidateSets = [];
  for (let index = 0; index < onsetGroups.length; index += 1) {
    const group = onsetGroups[index];
    if (!Array.isArray(group?.midis) || group.midis.length === 0) {
      throw new Error(`onsetGroups[${index}].midis must be a non-empty array.`);
    }

    const enumeration = enumeratePlayableShapes(group.midis, instrumentConfig, {
      policy,
      limit: maxCandidatesPerOnset,
    });

    if (!enumeration.resolved) {
      return {
        resolved: false,
        reason: 'UNRESOLVED_ONSET_SHAPE',
        unresolvedOnsetIndex: index,
        unresolvedOnsetId: group.onsetId ?? index,
        sourceMidis: onsetGroups.map((item) => [...item.midis]),
        candidateCounts: [...candidateSets.map((item) => item.candidates.length), 0],
        diagnostics: {
          unresolvedOnsetCount: 1,
        },
      };
    }

    candidateSets.push(enumeration);
  }

  if (onsetGroups.length === 0) {
    return {
      resolved: true,
      reason: 'EMPTY_PHRASE',
      path: [],
      metrics: {
        onsetCount: 0,
        totalCenterFretMovement: 0,
        maxCenterFretMovement: 0,
        stringSetChangeCount: 0,
        openStringCount: 0,
        candidateCounts: [],
        unresolvedOnsetCount: 0,
      },
    };
  }

  let states = candidateSets[0].candidates.map((candidate) => ({
    candidate,
    cost: candidate.localScore * resolvedWeights.localShape,
    previous: null,
    pathKeys: [candidate.tieKey],
  }));

  for (let index = 1; index < candidateSets.length; index += 1) {
    const nextStates = [];
    for (const current of candidateSets[index].candidates) {
      let best = null;
      for (const previousState of states) {
        const transition = transitionCost(previousState.candidate, current, resolvedWeights);
        const cost = previousState.cost
          + current.localScore * resolvedWeights.localShape
          + transition.cost;
        const pathKeys = [...previousState.pathKeys, current.tieKey];
        const key = stateKey(pathKeys);

        if (!best || cost < best.cost - EPSILON || (Math.abs(cost - best.cost) <= EPSILON && key < best.key)) {
          best = {
            candidate: current,
            cost,
            previous: previousState,
            pathKeys,
            key,
          };
        }
      }
      nextStates.push(best);
    }
    states = nextStates;
  }

  states.sort((a, b) => a.cost - b.cost || stateKey(a.pathKeys).localeCompare(stateKey(b.pathKeys)));
  const finalState = states[0];

  const reversed = [];
  let cursor = finalState;
  while (cursor) {
    reversed.push(cursor);
    cursor = cursor.previous;
  }
  const chosenStates = reversed.reverse();

  let totalMovement = 0;
  let maxMovement = 0;
  let stringSetChangeCount = 0;
  let openStringCount = 0;

  const path = chosenStates.map((state, index) => {
    if (index > 0) {
      const transition = transitionCost(chosenStates[index - 1].candidate, state.candidate, resolvedWeights);
      totalMovement += transition.centerMovement;
      maxMovement = Math.max(maxMovement, transition.centerMovement);
      stringSetChangeCount += transition.stringChanges;
    }
    openStringCount += state.candidate.diagnostics.openStringCount;

    return {
      onsetIndex: index,
      onsetId: onsetGroups[index].onsetId ?? index,
      time: onsetGroups[index].time ?? null,
      sourceMidis: [...onsetGroups[index].midis],
      assignments: state.candidate.assignments,
      diagnostics: {
        ...state.candidate.diagnostics,
        localScore: state.candidate.localScore,
        tieKey: state.candidate.tieKey,
      },
      candidateCount: candidateSets[index].candidates.length,
    };
  });

  return {
    resolved: true,
    reason: 'FRETBOARD_PATH_RESOLVED',
    path,
    metrics: {
      onsetCount: path.length,
      totalCost: finalState.cost,
      totalCenterFretMovement: totalMovement,
      maxCenterFretMovement: maxMovement,
      stringSetChangeCount,
      openStringCount,
      candidateCounts: candidateSets.map((item) => item.candidates.length),
      unresolvedOnsetCount: 0,
    },
    weights: resolvedWeights,
  };
}
