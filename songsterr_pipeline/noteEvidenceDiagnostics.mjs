const HARMONIC_INTERVALS = new Set([12, 19, 24, 28, 31, 34, 36]);
const OCTAVE_INTERVALS = new Set([12, 24, 36]);

function increment(object, key) {
  object[key] = (object[key] ?? 0) + 1;
}

function sortedNumericHistogram(histogram) {
  return Object.fromEntries(
    Object.entries(histogram)
      .map(([key, value]) => [Number(key), value])
      .sort((a, b) => a[0] - b[0])
      .map(([key, value]) => [String(key), value]),
  );
}

function hasFiniteEvidenceValue(value) {
  return value !== null && value !== undefined && Number.isFinite(Number(value));
}

export function summarizeNoteEvidence(adapted = {}) {
  const onsets = Array.isArray(adapted?.onsets) ? adapted.onsets : [];
  const promotedEvents = Array.isArray(adapted?.promotedEvents) ? adapted.promotedEvents : [];

  const classificationCounts = {
    unambiguous: 0,
    ambiguous: 0,
    'no-candidate': 0,
  };
  const candidateCountHistogram = {};
  const topSecondIntervalHistogram = {};
  let singleCandidateAmbiguousCount = 0;
  let competingCandidateAmbiguousCount = 0;
  let harmonicRelationAmbiguousCount = 0;
  let octaveRelationAmbiguousCount = 0;
  let closeIntervalAmbiguousCount = 0;

  for (const onset of onsets) {
    if (classificationCounts[onset?.classification] !== undefined) {
      classificationCounts[onset.classification] += 1;
    }
    const candidates = Array.isArray(onset?.candidates) ? onset.candidates : [];
    increment(candidateCountHistogram, String(candidates.length));

    if (onset?.classification !== 'ambiguous') continue;
    if (candidates.length <= 1) {
      singleCandidateAmbiguousCount += 1;
      continue;
    }

    competingCandidateAmbiguousCount += 1;
    const interval = Math.abs(Number(candidates[0]?.midi) - Number(candidates[1]?.midi));
    if (Number.isFinite(interval)) {
      increment(topSecondIntervalHistogram, String(interval));
      if (HARMONIC_INTERVALS.has(interval)) harmonicRelationAmbiguousCount += 1;
      if (OCTAVE_INTERVALS.has(interval)) octaveRelationAmbiguousCount += 1;
      if (interval <= 7) closeIntervalAmbiguousCount += 1;
    }
  }

  const promotedWithDurationCount = promotedEvents.filter((event) => (
    hasFiniteEvidenceValue(event?.duration) || hasFiniteEvidenceValue(event?.end)
  )).length;
  const promotedMissingDurationCount = promotedEvents.length - promotedWithDurationCount;
  const unresolvedPitchEvidenceCount = classificationCounts.ambiguous + classificationCounts['no-candidate'];

  return {
    contract: {
      name: 'songsterr-fresh-note-evidence-diagnostics',
      version: 2,
      descriptiveOnly: true,
      ownsAcceptanceDecision: false,
      compositeScoreDefined: false,
      compositeScore: null,
      referenceBlind: adapted?.adapterContract?.referenceBlind === true,
      structureIdentityVerified: adapted?.adapterContract?.structureIdentityVerified === true,
      legacyV143ScorerImported: false,
    },
    counts: {
      onsetCount: onsets.length,
      promotedEventCount: promotedEvents.length,
      promotedWithDurationCount,
      promotedMissingDurationCount,
      unresolvedPitchEvidenceCount,
      classificationCounts,
      singleCandidateAmbiguousCount,
      competingCandidateAmbiguousCount,
      harmonicRelationAmbiguousCount,
      octaveRelationAmbiguousCount,
      closeIntervalAmbiguousCount,
    },
    candidateCountHistogram: sortedNumericHistogram(candidateCountHistogram),
    topSecondIntervalHistogram: sortedNumericHistogram(topSecondIntervalHistogram),
  };
}
