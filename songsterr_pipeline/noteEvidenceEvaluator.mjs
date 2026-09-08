const EPSILON = 1e-12;

function finiteOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function ratio(numerator, denominator) {
  return denominator > 0 ? numerator / denominator : 0;
}

function mean(values) {
  return values.length > 0 ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
}

function percentile(values, fraction) {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const position = Math.max(0, Math.min(sorted.length - 1, (sorted.length - 1) * fraction));
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  const weight = position - lower;
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

function dominantValue(values) {
  if (values.length === 0) return { value: null, count: 0, share: 0 };
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  const ranked = [...counts.entries()].sort((a, b) => b[1] - a[1] || Number(a[0]) - Number(b[0]));
  return {
    value: ranked[0][0],
    count: ranked[0][1],
    share: ranked[0][1] / values.length,
  };
}

function normalizeCapabilities(evidence) {
  const raw = evidence?.capabilities && typeof evidence.capabilities === 'object'
    ? evidence.capabilities
    : {};
  return {
    roleRelevanceResolved: raw.roleRelevanceResolved === true,
    polyphonyResolved: raw.polyphonyResolved === true,
    durationResolution: ['none', 'partial', 'complete'].includes(raw.durationResolution)
      ? raw.durationResolution
      : 'undeclared',
    instrumentIsolation: typeof raw.instrumentIsolation === 'string'
      ? raw.instrumentIsolation
      : 'undeclared',
    confidenceCalibration: typeof raw.confidenceCalibration === 'string'
      ? raw.confidenceCalibration
      : 'undeclared',
  };
}

function eventMidi(event) {
  const midi = Number(event?.midi);
  return Number.isInteger(midi) ? midi : null;
}

export function evaluateNoteEvidence(evidence = {}) {
  const onsets = Array.isArray(evidence?.onsets) ? evidence.onsets : [];
  const promotedEvents = Array.isArray(evidence?.promotedEvents) ? evidence.promotedEvents : [];
  const metrics = evidence?.metrics && typeof evidence.metrics === 'object' ? evidence.metrics : {};
  const contract = evidence?.adapterContract && typeof evidence.adapterContract === 'object'
    ? evidence.adapterContract
    : {};
  const capabilities = normalizeCapabilities(evidence);

  const candidateCounts = [];
  const topConfidences = [];
  const topSecondMargins = [];
  const structureDisplacements = [];
  const topMidis = [];
  let multiCandidateOnsetCount = 0;
  let octaveCompetitorOnsetCount = 0;

  for (const onset of onsets) {
    const candidates = Array.isArray(onset?.candidates) ? onset.candidates : [];
    candidateCounts.push(candidates.length);
    const displacement = finiteOrNull(onset?.structureDisplacementSeconds);
    if (displacement !== null) structureDisplacements.push(Math.abs(displacement));

    if (candidates.length > 0) {
      const topConfidence = finiteOrNull(candidates[0]?.confidence);
      const topMidi = Number(candidates[0]?.midi);
      if (topConfidence !== null) topConfidences.push(topConfidence);
      if (Number.isInteger(topMidi)) topMidis.push(topMidi);

      const secondConfidence = candidates.length > 1 ? finiteOrNull(candidates[1]?.confidence) : 0;
      if (topConfidence !== null && secondConfidence !== null) {
        topSecondMargins.push(topConfidence - secondConfidence);
      }
    }

    if (candidates.length > 1) {
      multiCandidateOnsetCount += 1;
      const topMidi = Number(candidates[0]?.midi);
      const hasOctaveCompetitor = Number.isInteger(topMidi) && candidates.slice(1).some((candidate) => {
        const midi = Number(candidate?.midi);
        if (!Number.isInteger(midi)) return false;
        const distance = Math.abs(midi - topMidi);
        return distance >= 12 && distance % 12 === 0;
      });
      if (hasOctaveCompetitor) octaveCompetitorOnsetCount += 1;
    }
  }

  const promotedMidis = promotedEvents.map(eventMidi).filter((midi) => midi !== null);
  const topDominant = dominantValue(topMidis);
  const promotedDominant = dominantValue(promotedMidis);

  const onsetCount = Number.isInteger(metrics.onsetCount) ? metrics.onsetCount : onsets.length;
  const promotedEventCount = Number.isInteger(metrics.promotedEventCount)
    ? metrics.promotedEventCount
    : promotedEvents.length;
  const unresolvedOnsetCount = Number.isInteger(metrics.unresolvedOnsetCount)
    ? metrics.unresolvedOnsetCount
    : onsets.filter((onset) => onset?.classification !== 'unambiguous').length;
  const durationResolvedEvidenceCount = Number.isInteger(metrics.durationResolvedEvidenceCount)
    ? metrics.durationResolvedEvidenceCount
    : onsets.filter((onset) => finiteOrNull(onset?.durationSeconds) !== null).length;

  const failures = [];
  if (contract.referenceBlind !== true) failures.push('NOTE_EVIDENCE_NOT_REFERENCE_BLIND');
  if (contract.structureFrozen !== true) failures.push('NOTE_EVIDENCE_STRUCTURE_NOT_FROZEN');
  if (contract.structureIdentityVerified !== true) failures.push('NOTE_EVIDENCE_STRUCTURE_IDENTITY_UNVERIFIED');
  if (contract.nearestStructureSlotsVerified !== true) failures.push('NOTE_EVIDENCE_STRUCTURE_SLOTS_UNVERIFIED');
  if (contract.syntheticDurationInference !== false) failures.push('SYNTHETIC_DURATION_INFERENCE_PRESENT');
  if (contract.legacyV143ScorerImported === true) failures.push('LEGACY_SCORER_BOUNDARY_VIOLATION');
  if (onsetCount <= 0) failures.push('NOTE_EVIDENCE_EMPTY');
  if (!capabilities.roleRelevanceResolved) failures.push('ROLE_RELEVANCE_UNRESOLVED');
  if (!capabilities.polyphonyResolved) failures.push('POLYPHONY_UNRESOLVED');
  if (unresolvedOnsetCount > 0) failures.push('PITCH_EVIDENCE_UNRESOLVED');
  if (capabilities.durationResolution !== 'complete'
      || promotedEventCount <= 0
      || durationResolvedEvidenceCount + EPSILON < promotedEventCount) {
    failures.push('DURATION_EVIDENCE_INCOMPLETE');
  }
  if (promotedEventCount <= 0) failures.push('NO_PROMOTED_NOTE_EVENTS');

  return {
    evaluatorContract: {
      name: 'songsterr-fresh-note-evidence-evaluator',
      version: 1,
      compositeScoreDefined: false,
      compositeScore: null,
      referenceBlind: true,
      legacyV143ScorerImported: false,
    },
    acceptedForCompleteTab: failures.length === 0,
    failureReasons: failures,
    capabilities,
    diagnostics: {
      onsetCount,
      promotedEventCount,
      unresolvedOnsetCount,
      unresolvedOnsetRate: ratio(unresolvedOnsetCount, onsetCount),
      durationResolvedEvidenceCount,
      durationCoverageAgainstPromotedEvents: ratio(durationResolvedEvidenceCount, promotedEventCount),
      candidateCount: candidateCounts.reduce((sum, value) => sum + value, 0),
      candidateCountPerOnset: {
        mean: mean(candidateCounts),
        median: percentile(candidateCounts, 0.5),
        p95: percentile(candidateCounts, 0.95),
        max: candidateCounts.length > 0 ? Math.max(...candidateCounts) : 0,
      },
      multiCandidateOnsetCount,
      multiCandidateOnsetRate: ratio(multiCandidateOnsetCount, onsetCount),
      octaveCompetitorOnsetCount,
      octaveCompetitorRateAmongMultiCandidateOnsets: ratio(
        octaveCompetitorOnsetCount,
        multiCandidateOnsetCount,
      ),
      topConfidence: {
        mean: mean(topConfidences),
        median: percentile(topConfidences, 0.5),
        p10: percentile(topConfidences, 0.1),
        p90: percentile(topConfidences, 0.9),
      },
      topSecondConfidenceMargin: {
        mean: mean(topSecondMargins),
        median: percentile(topSecondMargins, 0.5),
        p10: percentile(topSecondMargins, 0.1),
        p90: percentile(topSecondMargins, 0.9),
      },
      structureDisplacementSeconds: {
        meanAbsolute: mean(structureDisplacements),
        medianAbsolute: percentile(structureDisplacements, 0.5),
        p95Absolute: percentile(structureDisplacements, 0.95),
        maxAbsolute: structureDisplacements.length > 0 ? Math.max(...structureDisplacements) : 0,
      },
      dominantTopCandidateMidi: topDominant,
      dominantPromotedMidi: promotedDominant,
    },
  };
}
