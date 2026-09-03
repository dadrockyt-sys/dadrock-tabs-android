import { normalizeAiTabConditioningV1 } from './aiTabConditioningV1.mjs';

export const AI_TAB_CONDITIONED_SHADOW_PROJECTION_V1 = 1;

const MAX_FRET = 24;
const FLOAT_DIGITS = 9;

function stableRound(value, digits = FLOAT_DIGITS) {
  if (value === null || value === undefined) return null;
  const scale = 10 ** digits;
  return Math.round((Number(value) + Number.EPSILON) * scale) / scale;
}

function finiteNonNegative(value, fallback = 0) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(0, parsed);
}

function integerOrNull(value) {
  return Number.isInteger(value) ? value : null;
}

function resolveStructure(structurePrior) {
  const tempoBpm = structurePrior.tempoBpm;
  const timeSignature = structurePrior.timeSignature;
  const pickupBeats = structurePrior.pickupBeats;
  const feel = structurePrior.feel;

  const explicitStructure =
    tempoBpm !== null &&
    timeSignature !== null &&
    pickupBeats !== null;

  if (!explicitStructure) {
    return {
      status: 'UNRESOLVED_AUTO_STRUCTURE',
      quantizationStatus: 'UNRESOLVED_AUTO_STRUCTURE',
      tempoBpm,
      timeSignature,
      pickupBeats,
      feel,
      quarterSeconds: null,
      signatureUnitSeconds: null,
      measureSeconds: null,
      pickupSeconds: null,
      subdivisionsPerSignatureUnit: null,
      subdivisionSeconds: null,
    };
  }

  const quarterSeconds = 60 / tempoBpm;
  const signatureUnitSeconds =
    quarterSeconds * (4 / timeSignature.denominator);
  const measureSeconds =
    signatureUnitSeconds * timeSignature.numerator;
  const pickupSeconds =
    pickupBeats * signatureUnitSeconds;

  let subdivisionsPerSignatureUnit = null;
  let subdivisionSeconds = null;
  let quantizationStatus = 'UNRESOLVED_AUTO_FEEL';

  if (feel === 'straight') {
    subdivisionsPerSignatureUnit = 4;
    subdivisionSeconds =
      signatureUnitSeconds / subdivisionsPerSignatureUnit;
    quantizationStatus = 'STRAIGHT';
  } else if (feel === 'triplet') {
    subdivisionsPerSignatureUnit = 3;
    subdivisionSeconds =
      signatureUnitSeconds / subdivisionsPerSignatureUnit;
    quantizationStatus = 'TRIPLET';
  }

  return {
    status: 'EXPLICIT_STRUCTURE_RESOLVED',
    quantizationStatus,
    tempoBpm,
    timeSignature: {
      numerator: timeSignature.numerator,
      denominator: timeSignature.denominator,
    },
    pickupBeats,
    feel,
    quarterSeconds: stableRound(quarterSeconds),
    signatureUnitSeconds: stableRound(signatureUnitSeconds),
    measureSeconds: stableRound(measureSeconds),
    pickupSeconds: stableRound(pickupSeconds),
    subdivisionsPerSignatureUnit,
    subdivisionSeconds: stableRound(subdivisionSeconds),
  };
}

function projectStart(sourceStart, structure) {
  if (structure.status !== 'EXPLICIT_STRUCTURE_RESOLVED') {
    return {
      projectedStart: null,
      subdivisionIndex: null,
    };
  }

  if (!structure.subdivisionSeconds) {
    return {
      projectedStart: stableRound(sourceStart),
      subdivisionIndex: null,
    };
  }

  const rawSlot = sourceStart / structure.subdivisionSeconds;
  const slot = Math.floor(rawSlot + 0.5);

  return {
    projectedStart: stableRound(
      slot * structure.subdivisionSeconds
    ),
    subdivisionIndex: slot,
  };
}

function musicalPosition(projectedStart, structure) {
  if (
    structure.status !== 'EXPLICIT_STRUCTURE_RESOLVED' ||
    projectedStart === null
  ) {
    return {
      measureNumber: null,
      signatureUnitNumber: null,
      signatureUnitFraction: null,
      pickup: null,
    };
  }

  const timestamp = Math.max(0, projectedStart);
  const pickupSeconds = structure.pickupSeconds;
  const signatureUnitSeconds = structure.signatureUnitSeconds;
  const measureSeconds = structure.measureSeconds;
  const numerator = structure.timeSignature.numerator;

  if (timestamp < pickupSeconds) {
    const unitZero = Math.floor(timestamp / signatureUnitSeconds);
    const withinUnit =
      timestamp - unitZero * signatureUnitSeconds;

    return {
      measureNumber: 0,
      signatureUnitNumber: unitZero + 1,
      signatureUnitFraction: stableRound(
        Math.min(
          0.999999999,
          Math.max(0, withinUnit / signatureUnitSeconds)
        )
      ),
      pickup: true,
    };
  }

  const fromFirstFullMeasure = timestamp - pickupSeconds;
  const measureZero = Math.floor(
    fromFirstFullMeasure / measureSeconds
  );
  const withinMeasure =
    fromFirstFullMeasure - measureZero * measureSeconds;
  const rawUnitZero = Math.floor(
    withinMeasure / signatureUnitSeconds
  );
  const unitZero = Math.min(
    numerator - 1,
    Math.max(0, rawUnitZero)
  );
  const withinUnit =
    withinMeasure - unitZero * signatureUnitSeconds;

  return {
    measureNumber: measureZero + 1,
    signatureUnitNumber: unitZero + 1,
    signatureUnitFraction: stableRound(
      Math.min(
        0.999999999,
        Math.max(0, withinUnit / signatureUnitSeconds)
      )
    ),
    pickup: false,
  };
}

function targetFretForRole(role) {
  if (role === 'bass') return 5;
  if (role === 'rhythm') return 3;
  return 7;
}

function scoreCandidate(
  candidate,
  role,
  previousStringIndex,
  previousFret
) {
  const { stringIndex, fret } = candidate;
  const targetFret = targetFretForRole(role);

  let score = Math.abs(fret - targetFret) * 0.35;

  if (fret === 0) {
    score +=
      role === 'rhythm' || role === 'bass'
        ? -1.0
        : 1.25;
  }

  if (previousFret !== null) {
    const distance = Math.abs(fret - previousFret);
    score += distance * 1.15;
    if (distance > 5) {
      score += (distance - 5) * 2.0;
    }
  }

  if (previousStringIndex !== null) {
    const distance = Math.abs(
      stringIndex - previousStringIndex
    );
    score += distance * 0.8;
    if (distance > 2) {
      score += (distance - 2) * 1.5;
    }
  }

  return score;
}

function decodeStringAndFret(
  midi,
  instrumentConfig,
  previousStringIndex,
  previousFret
) {
  if (!Number.isInteger(midi) || midi < 0 || midi > 127) {
    return null;
  }

  // Conditioning V1 stores physical open strings low-to-high. DadRock's
  // historical rendering convention indexes strings high-to-low.
  const highToLowPhysicalTuning = [
    ...instrumentConfig.tuningMidi,
  ].reverse();

  const candidates = [];

  for (
    let stringIndex = 0;
    stringIndex < highToLowPhysicalTuning.length;
    stringIndex += 1
  ) {
    const physicalOpenMidi =
      highToLowPhysicalTuning[stringIndex];
    const soundingOpenMidi =
      physicalOpenMidi + instrumentConfig.capoFret;
    const fret = midi - soundingOpenMidi;

    if (
      Number.isInteger(fret) &&
      fret >= 0 &&
      fret <= MAX_FRET
    ) {
      candidates.push({
        stringIndex,
        fret,
        physicalOpenMidi,
        soundingOpenMidi,
      });
    }
  }

  if (candidates.length === 0) return null;

  candidates.sort((left, right) => {
    const leftScore = scoreCandidate(
      left,
      instrumentConfig.role,
      previousStringIndex,
      previousFret
    );
    const rightScore = scoreCandidate(
      right,
      instrumentConfig.role,
      previousStringIndex,
      previousFret
    );

    if (leftScore !== rightScore) {
      return leftScore - rightScore;
    }
    if (left.stringIndex !== right.stringIndex) {
      return left.stringIndex - right.stringIndex;
    }
    return left.fret - right.fret;
  });

  const winner = candidates[0];

  return {
    conditionedStringIndex: winner.stringIndex,
    conditionedFret: winner.fret,
    physicalOpenMidi: winner.physicalOpenMidi,
    soundingOpenMidi: winner.soundingOpenMidi,
    candidateCount: candidates.length,
  };
}

export function buildAiTabConditionedShadowProjectionV1({
  events,
  conditioning,
} = {}) {
  const role = conditioning?.instrumentConfig?.role;
  const normalizedConditioning =
    normalizeAiTabConditioningV1(conditioning, role);
  const structure = resolveStructure(
    normalizedConditioning.structurePrior
  );

  const sourceEvents = Array.isArray(events)
    ? events
    : [];

  let previousStringIndex = null;
  let previousFret = null;

  const projectedEvents = sourceEvents.map(
    (event, arrayIndex) => {
      const sourceStart = finiteNonNegative(
        event?.start,
        0
      );
      const sourceEnd = Math.max(
        sourceStart,
        finiteNonNegative(event?.end, sourceStart)
      );
      const midi = integerOrNull(event?.midi);

      const timing = projectStart(
        sourceStart,
        structure
      );
      const position = musicalPosition(
        timing.projectedStart,
        structure
      );

      const decoded = decodeStringAndFret(
        midi,
        normalizedConditioning.instrumentConfig,
        previousStringIndex,
        previousFret
      );

      if (decoded) {
        previousStringIndex =
          decoded.conditionedStringIndex;
        previousFret = decoded.conditionedFret;
      }

      return {
        sourceEventIndex:
          Number.isInteger(event?.eventIndex)
            ? event.eventIndex
            : arrayIndex,
        sourceStart: stableRound(sourceStart),
        sourceEnd: stableRound(sourceEnd),
        projectedStart: timing.projectedStart,
        measureNumber: position.measureNumber,
        signatureUnitNumber:
          position.signatureUnitNumber,
        signatureUnitFraction:
          position.signatureUnitFraction,
        subdivisionIndex:
          timing.subdivisionIndex,
        pickup: position.pickup,
        midi,
        sourceStringIndex:
          integerOrNull(event?.stringIndex),
        sourceFret:
          integerOrNull(event?.fret),
        conditionedStringIndex:
          decoded?.conditionedStringIndex ?? null,
        conditionedFret:
          decoded?.conditionedFret ?? null,
        physicalOpenMidi:
          decoded?.physicalOpenMidi ?? null,
        soundingOpenMidi:
          decoded?.soundingOpenMidi ?? null,
        playableCandidateCount:
          decoded?.candidateCount ?? 0,
        playableUnderConditioning:
          Boolean(decoded),
      };
    }
  );

  return {
    shadowContract: {
      name: 'structure-conditioned-shadow-projection',
      version:
        AI_TAB_CONDITIONED_SHADOW_PROJECTION_V1,
      shadowOnly: true,
      referenceBlind: true,
      referenceScoreAuthorized: false,
      productionEligible: false,
    },
    structure,
    instrumentConfig: {
      role:
        normalizedConditioning.instrumentConfig.role,
      tuningMidi: [
        ...normalizedConditioning.instrumentConfig.tuningMidi,
      ],
      capoFret:
        normalizedConditioning.instrumentConfig.capoFret,
    },
    eventCount: projectedEvents.length,
    events: projectedEvents,
  };
}
