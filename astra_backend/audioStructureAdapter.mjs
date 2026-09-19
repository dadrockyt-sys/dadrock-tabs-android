import { buildStructureMap } from './structureMap.mjs';

const EPSILON = 1e-9;
const STRUCTURE_ACCEPTANCE_V1 = Object.freeze({
  minimumTempoConfidence: 0.70,
  minimumMeterConfidence: 0.55,
  minimumDownbeatConfidence: 0.50,
  minimumFeelConfidence: 0.55,
  maximumBeatIntervalCoefficientOfVariation: 0.05,
  maximumMeanAbsoluteAlignmentErrorSeconds: 0.025,
  maximumRootMeanSquareAlignmentErrorSeconds: 0.04,
  maximumAlignmentErrorSeconds: 0.08,
});

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

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function coefficientOfVariation(values) {
  if (values.length < 2) return 0;
  const average = mean(values);
  if (average <= EPSILON) return 0;
  const variance = mean(values.map((value) => (value - average) ** 2));
  return Math.sqrt(variance) / average;
}

function median(values) {
  if (values.length === 0) return null;
  const ordered = [...values].sort((a, b) => a - b);
  const middle = Math.floor(ordered.length / 2);
  return ordered.length % 2 === 1
    ? ordered[middle]
    : (ordered[middle - 1] + ordered[middle]) / 2;
}

function deriveMeasureTempoSegments({
  beatTimes,
  numerator,
  phaseBeatOffset,
  durationSeconds,
  tempoConfidence,
  upstreamProvenance,
}) {
  if (!Number.isInteger(phaseBeatOffset) || phaseBeatOffset < 0 || phaseBeatOffset >= beatTimes.length) {
    return null;
  }

  const downbeatIndices = [];
  for (let index = phaseBeatOffset; index < beatTimes.length; index += numerator) {
    downbeatIndices.push(index);
  }
  if (downbeatIndices.length < 2) return null;

  const segments = [];
  const observedBpms = [];
  for (let barIndex = 0; barIndex < downbeatIndices.length - 1; barIndex += 1) {
    const startIndex = downbeatIndices[barIndex];
    const endIndex = downbeatIndices[barIndex + 1];
    const observedStart = beatTimes[startIndex];
    const observedEnd = beatTimes[endIndex];
    const barDuration = observedEnd - observedStart;
    if (barDuration <= EPSILON) throw new Error('Observed downbeat times must be strictly increasing.');

    const bpm = 60 * numerator / barDuration;
    if (bpm < 20 || bpm > 400) throw new Error('Observed measure tempo falls outside supported BPM range.');
    observedBpms.push(bpm);

    const localIntervals = [];
    for (let beatIndex = startIndex; beatIndex < endIndex; beatIndex += 1) {
      localIntervals.push(beatTimes[beatIndex + 1] - beatTimes[beatIndex]);
    }
    const localCv = coefficientOfVariation(localIntervals);
    const localConfidence = Math.max(0.05, Math.min(0.98, tempoConfidence * Math.exp(-8 * localCv)));

    segments.push({
      start: barIndex === 0 ? 0 : observedStart,
      end: observedEnd,
      bpm,
      confidence: localConfidence,
      provenance: {
        source: 'full-mixture-observed-measure-tempo',
        upstream: upstreamProvenance,
        observedDownbeatStartSeconds: observedStart,
        observedDownbeatEndSeconds: observedEnd,
        localBeatIntervalCoefficientOfVariation: localCv,
      },
    });
  }

  const recentBpms = observedBpms.slice(-Math.min(8, observedBpms.length));
  const extrapolatedBpm = median(recentBpms) ?? observedBpms.at(-1);
  const lastDownbeat = beatTimes[downbeatIndices.at(-1)];
  segments.push({
    start: lastDownbeat,
    end: null,
    bpm: extrapolatedBpm,
    confidence: Math.max(0.05, Math.min(0.98, tempoConfidence * 0.75)),
    provenance: {
      source: 'full-mixture-observed-measure-tempo-tail-extrapolation',
      upstream: upstreamProvenance,
      observedDownbeatStartSeconds: lastDownbeat,
      extrapolatedToAudioEndSeconds: durationSeconds,
      recentObservedMeasureCount: recentBpms.length,
    },
  });

  return segments;
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
  const meanAbsoluteErrorSeconds = mean(errors);
  const rootMeanSquareErrorSeconds = Math.sqrt(mean(errors.map((value) => value ** 2)));

  return {
    observedBeatCount: observed.length,
    gridBeatCount: gridBeatStarts.length,
    meanAbsoluteErrorSeconds,
    rootMeanSquareErrorSeconds,
    maxAbsoluteErrorSeconds: Math.max(...errors),
  };
}

function evaluateStructureAcceptance({ raw, alignment, tempoConfidence, meterConfidence, downbeatConfidence, feelConfidence }) {
  const beatCv = Number(raw?.diagnostics?.beatIntervalCoefficientOfVariation);
  const reasons = [];
  if (tempoConfidence < STRUCTURE_ACCEPTANCE_V1.minimumTempoConfidence) reasons.push('TEMPO_CONFIDENCE_LOW');
  if (meterConfidence < STRUCTURE_ACCEPTANCE_V1.minimumMeterConfidence) reasons.push('METER_CONFIDENCE_LOW');
  if (downbeatConfidence < STRUCTURE_ACCEPTANCE_V1.minimumDownbeatConfidence) reasons.push('DOWNBEAT_CONFIDENCE_LOW');
  if (feelConfidence < STRUCTURE_ACCEPTANCE_V1.minimumFeelConfidence) reasons.push('FEEL_CONFIDENCE_LOW');
  if (!Number.isFinite(beatCv) || beatCv > STRUCTURE_ACCEPTANCE_V1.maximumBeatIntervalCoefficientOfVariation) {
    reasons.push('BEAT_INTERVAL_VARIATION_HIGH');
  }
  if (!Number.isFinite(alignment.meanAbsoluteErrorSeconds)
    || alignment.meanAbsoluteErrorSeconds > STRUCTURE_ACCEPTANCE_V1.maximumMeanAbsoluteAlignmentErrorSeconds) {
    reasons.push('BEAT_ALIGNMENT_MAE_HIGH');
  }
  if (!Number.isFinite(alignment.rootMeanSquareErrorSeconds)
    || alignment.rootMeanSquareErrorSeconds > STRUCTURE_ACCEPTANCE_V1.maximumRootMeanSquareAlignmentErrorSeconds) {
    reasons.push('BEAT_ALIGNMENT_RMSE_HIGH');
  }
  if (!Number.isFinite(alignment.maxAbsoluteErrorSeconds)
    || alignment.maxAbsoluteErrorSeconds > STRUCTURE_ACCEPTANCE_V1.maximumAlignmentErrorSeconds) {
    reasons.push('BEAT_ALIGNMENT_MAX_ERROR_HIGH');
  }
  return {
    contract: 'songsterr-fresh-structure-acceptance-v1',
    accepted: reasons.length === 0,
    reasons,
    thresholds: { ...STRUCTURE_ACCEPTANCE_V1 },
    observed: {
      tempoConfidence,
      meterConfidence,
      downbeatConfidence,
      feelConfidence,
      beatIntervalCoefficientOfVariation: Number.isFinite(beatCv) ? beatCv : null,
      ...alignment,
    },
  };
}

export function adaptFullMixtureStructureAnalysis(raw = {}) {
  if (raw?.version !== 1) throw new Error('audio structure analysis version must be 1.');
  if (raw?.referenceBlind !== true) throw new Error('audio structure analysis must be reference-blind.');

  const durationSeconds = finiteNumber(raw?.durationSeconds, 'durationSeconds');
  if (durationSeconds <= 0) throw new Error('durationSeconds must be positive.');

  const bpm = finiteNumber(raw?.tempo?.bpm, 'tempo.bpm');
  if (bpm < 20 || bpm > 400) throw new Error('tempo.bpm must be between 20 and 400.');
  if (raw?.tempo?.beatUnit !== 'quarter-note') throw new Error('AUDIO_STRUCTURE_ADAPTER_TEMPO_BEAT_UNIT_UNSUPPORTED');

  const numerator = raw?.selectedMeter?.numerator;
  const denominator = raw?.selectedMeter?.denominator;
  if (!Number.isInteger(numerator) || numerator < 1 || numerator > 32) {
    throw new Error('selectedMeter.numerator must be an integer from 1 to 32.');
  }
  if (denominator !== 4) throw new Error('AUDIO_STRUCTURE_ADAPTER_METER_DENOMINATOR_UNSUPPORTED');

  const feel = raw?.feel?.feel;
  if (feel !== 'straight' && feel !== 'triplet') throw new Error('feel.feel must be straight or triplet.');

  const pickupDurationSeconds = finiteNumber(raw?.pickup?.durationSeconds ?? 0, 'pickup.durationSeconds');
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

  const observedTempoSegments = deriveMeasureTempoSegments({
    beatTimes,
    numerator,
    phaseBeatOffset: raw?.selectedMeter?.phaseBeatOffset,
    durationSeconds,
    tempoConfidence,
    upstreamProvenance,
  });
  const tempoSegments = observedTempoSegments ?? [{
    start: 0,
    end: null,
    bpm,
    confidence: tempoConfidence,
    provenance: { source: 'full-mixture-audio-tempo', upstream: upstreamProvenance },
  }];

  const structureMap = buildStructureMap({
    durationSeconds,
    pickupDurationSeconds,
    tempoSegments,
    meterSegments: [{
      start: 0,
      end: null,
      numerator,
      denominator,
      confidence: meterConfidence,
      provenance: { source: 'full-mixture-audio-meter', upstream: upstreamProvenance },
    }],
    feelSegments: [{
      start: 0,
      end: null,
      feel,
      confidence: feelConfidence,
      provenance: { source: 'full-mixture-audio-feel', upstream: upstreamProvenance },
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

  const alignment = alignmentDiagnostics(structureMap, beatTimes);
  const structureAcceptance = evaluateStructureAcceptance({
    raw,
    alignment,
    tempoConfidence,
    meterConfidence,
    downbeatConfidence,
    feelConfidence,
  });

  return {
    adapterContract: {
      name: 'songsterr-fresh-full-mixture-structure',
      version: 1,
      referenceBlind: true,
      structureFrozenBeforeNoteInference: true,
      legacyV143ScorerImported: false,
      observedMeasureTempoPreserved: observedTempoSegments !== null,
    },
    structureMap,
    alignmentDiagnostics: alignment,
    structureAcceptance,
    evidence: {
      beatTimes,
      tempoSegmentCount: tempoSegments.length,
      meterCandidates: Array.isArray(raw?.meterCandidates)
        ? raw.meterCandidates.map((candidate) => ({ ...candidate }))
        : [],
      feelDiagnostics: raw?.feel?.diagnostics ? { ...raw.feel.diagnostics } : {},
      upstreamDiagnostics: raw?.diagnostics ? { ...raw.diagnostics } : {},
    },
  };
}
