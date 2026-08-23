import {
  BASS_MAX_FRET,
  BASS_STANDARD_OPEN_MIDI,
  projectBassProfessionalRenderEvents,
} from './bassProfessionalRenderContract.js';

const DEFAULT_BASS_PROFESSIONAL_THRESHOLDS = Object.freeze({
  minimumValidRenderEvents: 4,
  minimumRenderEventSurvivalPercent: 70,
  minimumPlayableStringFretPercent: 70,
  minimumTimingCoveragePercent: 70,
  minimumPitchValidityPercent: 70,
  minimumPitchStringFretConsistencyPercent: 70,
});

function percent(numerator, denominator) {
  if (!denominator) return 0;
  return Number(((numerator / denominator) * 100).toFixed(2));
}

function finiteInteger(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? Math.round(numeric) : null;
}

export function buildBassProfessionalQualityReport(
  rawEvents,
  thresholds = DEFAULT_BASS_PROFESSIONAL_THRESHOLDS
) {
  const events = Array.isArray(rawEvents)
    ? rawEvents.filter((event) => event && typeof event === 'object')
    : [];
  const projected = projectBassProfessionalRenderEvents(events);

  let playable = 0;
  let timed = 0;
  let pitchValid = 0;
  let pitchStringFretConsistent = 0;

  for (const event of events) {
    const measure = finiteInteger(event.measure);
    const step = finiteInteger(event.step);
    const stringIndex = finiteInteger(event.stringIndex);
    const fret = finiteInteger(event.fret);
    const midi = finiteInteger(event.midi ?? event.dominantMidi);

    const playableEvent =
      stringIndex !== null &&
      stringIndex >= 0 &&
      stringIndex < BASS_STANDARD_OPEN_MIDI.length &&
      fret !== null &&
      fret >= 0 &&
      fret <= BASS_MAX_FRET;

    if (playableEvent) playable += 1;
    if (measure !== null && measure >= 1 && step !== null && step >= 0 && step <= 15) {
      timed += 1;
    }
    if (midi !== null) pitchValid += 1;
    if (
      playableEvent &&
      midi !== null &&
      midi === BASS_STANDARD_OPEN_MIDI[stringIndex] + fret
    ) {
      pitchStringFretConsistent += 1;
    }
  }

  const rawEventCount = events.length;
  const validRenderEventCount = projected.length;
  const renderEventSurvivalPercent = percent(validRenderEventCount, rawEventCount);
  const playableStringFretPercent = percent(playable, rawEventCount);
  const timingCoveragePercent = percent(timed, rawEventCount);
  const pitchValidityPercent = percent(pitchValid, rawEventCount);
  const pitchStringFretConsistencyPercent = percent(
    pitchStringFretConsistent,
    rawEventCount
  );

  const passed =
    validRenderEventCount >= thresholds.minimumValidRenderEvents &&
    renderEventSurvivalPercent >= thresholds.minimumRenderEventSurvivalPercent &&
    playableStringFretPercent >= thresholds.minimumPlayableStringFretPercent &&
    timingCoveragePercent >= thresholds.minimumTimingCoveragePercent &&
    pitchValidityPercent >= thresholds.minimumPitchValidityPercent &&
    pitchStringFretConsistencyPercent >=
      thresholds.minimumPitchStringFretConsistencyPercent;

  return {
    name: 'bass-professional-quality-gate',
    version: 1,
    instrument: 'bass',
    rawEventCount,
    validRenderEventCount,
    renderEventSurvivalPercent,
    playableStringFretPercent,
    timingCoveragePercent,
    pitchValidityPercent,
    pitchStringFretConsistencyPercent,
    thresholds: { ...thresholds },
    passed,
    diagnosticOnly: true,
    productionCandidate: false,
    analyzerRoutingEnabled: false,
    pdfRendererEnabled: false,
    professionalStructuredIdentityEnabled: false,
    productionPromotionAuthorized: false,
  };
}

export { DEFAULT_BASS_PROFESSIONAL_THRESHOLDS };
