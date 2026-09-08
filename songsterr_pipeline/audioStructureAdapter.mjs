import { buildStructureMap } from './structureMap.mjs';

const EPSILON = 1e-9;

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function confidence(value, field, fallback = null) {
  if (value === undefined || value === null) return fallback;
  const parsed = finiteNumber(value, field);
  if (parsed < 0 || parsed > 1) throw new Error(`${field} must be between 0 and 1.`);
  return parsed;
}

function normalizeBeatTimes(raw, durationSeconds) {
  if (!Array.isArray(raw)) return [];
  const times = raw.map((value, index) => finiteNumber(value, `beatTimes[${index}]`));
  for (let index = 0; index < times.length; index += 1) {
    if (times[index] < -EPSILON || times[index] > durationSeconds + EPSILON) {
      throw new Error(`beatTimes[${index}] falls outside the audio duration.`);
    }
    if (index > 0 && times[index] <= times[index - 1] + EPSILON) {
      throw new Error('beatTimes must be strictly increasing.');
    }
  }
  return times;
}

function nearestDistance(value, candidates) {
  let best = Infinity;
  for (const candidate of candidates) best = Math.min(best, Math.abs(value - candidate));
  return best;
}

function alignmentDiagnostics(structureMap, beatTimes) {
  const gridBeatStarts = structureMap.measures
    .filter((measure) => !measure.pickup)
    .flatMap((measure) => measure.beats.map((beat) => beat.start));

  const observed = beatTimes.filter((time) => (
    time + EPSILON >= structureMap.pickupDurationSeconds
    && time <= structureMap.durationSeconds + EPSILON
  ));

  if (observed.length === 0 || gridBeatStarts.length === 0) {
    return {
      observedBeatCount: observed.length,
      gridBeatCount: gridBeatStarts.length,
      meanAbsoluteErrorSeconds: null,
      rootMeanSquareErrorSeconds: null,
      maxAbsoluteErrorSeconds: null,
    };
  }

  const errors = observed.map((time) => nearestDistance(time, gridBeatStarts));
  const meanAbsoluteErrorSeconds = errors.reduce((sum, value) => sum + value, 0) / errors.length;
  const rootMeanSquareErrorSeconds = Math.sqrt(
    errors.reduce((sum, value) => sum + value ** 2, 0) / errors.length,
  );

  return {
    observedBeatCount: observed.length,
    gridBeatCount: gridBeatStarts.length,
    meanAbsoluteErrorSeconds,
    rootMeanSquareErrorSeconds,
    maxAbsoluteErrorSeconds: Math.max(...errors),
  };
}

export function adaptFullMixtureStructureAnalysis(raw = {}) {
  if (raw?.version !== 1) throw new Error('audio structure analysis version must be 1.');
  if (raw?.referenceBlind !== true) {
    throw new Error('audio structure analysis must be reference-blind.');
  }

  const durationSeconds = finiteNumber(raw?.durationSeconds, 'durationSeconds');
  if (durationSeconds <= 0) throw new Error('durationSeconds must be positive.');

  const bpm = finiteNumber(raw?.tempo?.bpm, 'tempo.bpm');
  if (bpm < 20 || bpm > 400) throw new Error('tempo.bpm must be between 20 and 400.');
  if (raw?.tempo?.beatUnit !== 'quarter-note') {
    throw new Error('AUDIO_STRUCTURE_ADAPTER_TEMPO_BEAT_UNIT_UNSUPPORTED');
  }

  const numerator = raw?.selectedMeter?.numerator;
  const denominator = raw?.selectedMeter?.denominator;
  if (!Number.isInteger(numerator) || numerator < 1 || numerator > 32) {
    throw new Error('selectedMeter.numerator must be an integer from 1 to 32.');
  }
  if (denominator !== 4) {
    throw new Error('AUDIO_STRUCTURE_ADAPTER_METER_DENOMINATOR_UNSUPPORTED');
  }

  const feel = raw?.feel?.feel;
  if (feel !== 'straight' && feel !== 'triplet') {
    throw new Error('feel.feel must be straight or triplet.');
  }

  const pickupDurationSeconds = finiteNumber(
    raw?.pickup?.durationSeconds ?? 0,
    'pickup.durationSeconds',
  );
  if (pickupDurationSeconds < 0 || pickupDurationSeconds >= durationSeconds) {
    throw new Error('pickup.durationSeconds must be non-negative and shorter than the audio.');
  }

  const beatTimes = normalizeBeatTimes(raw?.beatTimes, durationSeconds);
  const tempoConfidence = confidence(raw?.tempo?.confidence, 'tempo.confidence', 0);
  const meterConfidence = confidence(raw?.selectedMeter?.confidence, 'selectedMeter.confidence', 0);
  const feelConfidence = confidence(raw?.feel?.confidence, 'feel.confidence', 0);
  const downbeatConfidence = confidence(raw?.pickup?.confidence, 'pickup.confidence', meterConfidence);
  const overallConfidence = confidence(raw?.confidence?.overall, 'confidence.overall', Math.min(
    tempoConfidence,
    meterConfidence,
    feelConfidence,
  ));

  const upstreamProvenance = raw?.provenance && typeof raw.provenance === 'object'
    ? { ...raw.provenance }
    : { source: 'unknown-full-mixture-analysis' };

  const structureMap = buildStructureMap({
    durationSeconds,
    pickupDurationSeconds,
    tempoSegments: [{
      start: 0,
      end: null,
      bpm,
      confidence: tempoConfidence,
      provenance: {
        source: 'full-mixture-audio-tempo',
        upstream: upstreamProvenance,
      },
    }],
    meterSegments: [{
      start: 0,
      end: null,
      numerator,
      denominator,
      confidence: meterConfidence,
      provenance: {
        source: 'full-mixture-audio-meter',
        upstream: upstreamProvenance,
      },
    }],
    feelSegments: [{
      start: 0,
      end: null,
      feel,
      confidence: feelConfidence,
      provenance: {
        source: 'full-mixture-audio-feel',
        upstream: upstreamProvenance,
      },
    }],
    confidence: {
      overall: overallConfidence,
      tempo: tempoConfidence,
      meter: meterConfidence,
      downbeats: downbeatConfidence,
      measures: Math.min(tempoConfidence, meterConfidence, downbeatConfidence),
      feel: feelConfidence,
    },
    provenance: {
      source: 'songsterr-fresh-full-mixture-structure-adapter-v1',
      upstream: upstreamProvenance,
      audioSource: raw?.audioSource ?? null,
      referenceBlind: true,
    },
  });

  return {
    adapterContract: {
      name: 'songsterr-fresh-full-mixture-structure',
      version: 1,
      referenceBlind: true,
      structureFrozenBeforeNoteInference: true,
      legacyV143ScorerImported: false,
    },
    structureMap,
    alignmentDiagnostics: alignmentDiagnostics(structureMap, beatTimes),
    evidence: {
      beatTimes,
      meterCandidates: Array.isArray(raw?.meterCandidates)
        ? raw.meterCandidates.map((candidate) => ({ ...candidate }))
        : [],
      feelDiagnostics: raw?.feel?.diagnostics ? { ...raw.feel.diagnostics } : {},
      upstreamDiagnostics: raw?.diagnostics ? { ...raw.diagnostics } : {},
    },
  };
}
