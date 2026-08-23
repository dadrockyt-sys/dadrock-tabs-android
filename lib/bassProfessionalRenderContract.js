const BASS_STRING_LABELS = Object.freeze(['G', 'D', 'A', 'E']);
const BASS_STANDARD_OPEN_MIDI = Object.freeze([43, 38, 33, 28]);
const BASS_MAX_FRET = 24;
const STEPS_PER_MEASURE = 16;
const MAX_RENDER_EVENTS = 5000;

function finiteInteger(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? Math.round(numeric) : null;
}

function finiteNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

export function projectBassProfessionalRenderEvents(rawEvents) {
  if (!Array.isArray(rawEvents)) return [];

  const projected = [];

  for (
    let eventIndex = 0;
    eventIndex < Math.min(rawEvents.length, MAX_RENDER_EVENTS);
    eventIndex += 1
  ) {
    const event = rawEvents[eventIndex];
    if (!event || typeof event !== 'object') continue;

    const measure = finiteInteger(event.measure);
    const step = finiteInteger(event.step);
    const stringIndex = finiteInteger(event.stringIndex);
    const fret = finiteInteger(event.fret);
    const midi = finiteInteger(event.midi ?? event.dominantMidi);

    if (
      measure === null ||
      measure < 1 ||
      step === null ||
      step < 0 ||
      step >= STEPS_PER_MEASURE ||
      stringIndex === null ||
      stringIndex < 0 ||
      stringIndex >= BASS_STRING_LABELS.length ||
      fret === null ||
      fret < 0 ||
      fret > BASS_MAX_FRET ||
      midi === null
    ) {
      continue;
    }

    const expectedMidi = BASS_STANDARD_OPEN_MIDI[stringIndex] + fret;
    if (midi !== expectedMidi) continue;

    const durationSteps = Math.max(
      1,
      finiteInteger(event.durationSteps ?? event?.rhythmSustain?.durationSteps ?? 1) || 1
    );
    const durationSeconds = finiteNumber(
      event.durationSeconds ?? event?.rhythmSustain?.durationSeconds
    );

    const techniques = Array.isArray(event.techniques)
      ? event.techniques
          .map((value) => String(value || '').trim().toLowerCase())
          .filter(Boolean)
      : Array.isArray(event.rhythmTechniques)
        ? event.rhythmTechniques
            .map((value) =>
              typeof value === 'string'
                ? value.trim().toLowerCase()
                : String(value?.type || '').trim().toLowerCase()
            )
            .filter(Boolean)
        : [];

    const output = {
      eventIndex,
      measure,
      step,
      stringIndex,
      stringLabel: BASS_STRING_LABELS[stringIndex],
      fret,
      midi,
      durationSteps,
      techniques: [...new Set(techniques)].sort(),
    };

    if (durationSeconds !== null && durationSeconds >= 0) {
      output.durationSeconds = durationSeconds;
    }

    projected.push(output);
  }

  return projected;
}

export function describeBassProfessionalRenderContract() {
  return {
    name: 'bass-professional-render-contract',
    version: 1,
    instrument: 'bass',
    tuning: 'Standard Bass',
    stringLabels: [...BASS_STRING_LABELS],
    openMidi: [...BASS_STANDARD_OPEN_MIDI],
    stringCount: BASS_STRING_LABELS.length,
    maximumFret: BASS_MAX_FRET,
    stepsPerMeasure: STEPS_PER_MEASURE,
    diagnosticOnly: true,
    productionCandidate: false,
    pdfRendererEnabled: false,
    analyzerRoutingEnabled: false,
    professionalStructuredIdentityEnabled: false,
    productionPromotionAuthorized: false,
  };
}

export {
  BASS_STRING_LABELS,
  BASS_STANDARD_OPEN_MIDI,
  BASS_MAX_FRET,
  STEPS_PER_MEASURE,
  MAX_RENDER_EVENTS,
};
