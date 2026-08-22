const ALLOWED_TRANSCRIPTION_TYPES = new Set([
  'lead',
  'rhythm',
  'bass',
]);

const MEASURES_PER_SYSTEM = 6;
const MEASURE_GRID_VERSION = 7;

function cleanText(value, fallback = '', maximumLength = 160) {
  const cleaned = String(value ?? fallback)
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maximumLength);

  return cleaned || fallback;
}

function cleanTabText(value) {
  return String(value || '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .slice(0, 30000)
    .trim();
}

function boundedTempo(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 120;
  return Math.min(300, Math.max(20, parsed));
}

function validPositiveInteger(value) {
  return Number.isInteger(Number(value)) && Number(value) > 0;
}

function validateReadOnlyNotes(rows) {
  for (const row of rows) {
    if (!row || typeof row !== 'object') return false;
    if (!validPositiveInteger(row.rowNumber)) return false;

    const notes = Array.isArray(row.notes) ? row.notes : [];
    for (const note of notes) {
      if (!note || typeof note !== 'object') return false;
      if (note.measureGridReadOnly !== true) return false;
      if (note.musicallyFiltered !== true) return false;
      if (!Number.isFinite(Number(note.rowRatio))) return false;
      if (Number(note.rowRatio) < 0 || Number(note.rowRatio) > 1) return false;
      if (!Number.isFinite(Number(note.stringIndex))) return false;
      if (!Number.isFinite(Number(note.fret))) return false;
    }
  }

  return true;
}

function validateReadOnlyFragments(rows) {
  for (const row of rows) {
    const fragments = Array.isArray(row?.fragments)
      ? row.fragments
      : [];

    for (const fragment of fragments) {
      if (!fragment || typeof fragment !== 'object') return false;
      if (fragment.readOnly !== true) return false;
      if (!Number.isFinite(Number(fragment.rowStartRatio))) return false;
      if (!Number.isFinite(Number(fragment.rowEndRatio))) return false;
      if (Number(fragment.rowStartRatio) < 0 || Number(fragment.rowStartRatio) > 1) {
        return false;
      }
      if (Number(fragment.rowEndRatio) < 0 || Number(fragment.rowEndRatio) > 1) {
        return false;
      }
    }
  }

  return true;
}

export function validateJimmyPaigeMeasureGrid(measureGrid) {
  if (!measureGrid || typeof measureGrid !== 'object') {
    return {
      valid: false,
      reason: 'missing-measure-grid',
    };
  }

  if (measureGrid.passed !== true) {
    return {
      valid: false,
      reason: 'measure-grid-did-not-pass-source-checks',
    };
  }

  if (Number(measureGrid.measureGridVersion) !== MEASURE_GRID_VERSION) {
    return {
      valid: false,
      reason: 'unsupported-measure-grid-version',
    };
  }

  if (Number(measureGrid.measuresPerRow) !== MEASURES_PER_SYSTEM) {
    return {
      valid: false,
      reason: 'measure-grid-layout-mismatch',
    };
  }

  if (!Array.isArray(measureGrid.rows) || !measureGrid.rows.length) {
    return {
      valid: false,
      reason: 'measure-grid-has-no-rows',
    };
  }

  if (!validateReadOnlyNotes(measureGrid.rows)) {
    return {
      valid: false,
      reason: 'measure-grid-note-contract-failed',
    };
  }

  if (!validateReadOnlyFragments(measureGrid.rows)) {
    return {
      valid: false,
      reason: 'measure-grid-fragment-contract-failed',
    };
  }

  if (
    Array.isArray(measureGrid.markers) &&
    measureGrid.markers.some(
      (marker) =>
        !marker ||
        typeof marker !== 'object' ||
        marker.measureGridReadOnly !== true
    )
  ) {
    return {
      valid: false,
      reason: 'measure-grid-marker-contract-failed',
    };
  }

  return {
    valid: true,
    reason: null,
  };
}

export function buildJimmyPaigeProfessionalPdfOptions({
  song,
  artist,
  transcriptionType,
  generatedTab,
  tuning,
  tempo,
  timeSignature,
  keySignature,
  preview = false,
  previewSystems = 4,
  measureGrid = null,
  analysisEngine = '',
  confidence = null,
  difficulty = null,
  techniques = [],
} = {}) {
  const safeSong = cleanText(song, 'Untitled', 120);
  const safeArtist = cleanText(artist, 'Unknown Artist', 120);
  const safeType = cleanText(transcriptionType, 'lead', 20).toLowerCase();
  const safeTab = cleanTabText(generatedTab);

  if (!ALLOWED_TRANSCRIPTION_TYPES.has(safeType)) {
    throw new Error('Transcription type must be lead, rhythm, or bass.');
  }

  if (!safeTab) {
    throw new Error('Jimmy PAIge professional PDF requires generated tablature.');
  }

  const gridValidation = validateJimmyPaigeMeasureGrid(measureGrid);
  const enableStructuredNotation = gridValidation.valid;

  return {
    rendererContract: {
      name: 'jimmy-paige-professional-pdf',
      version: 1,
      mode: enableStructuredNotation
        ? 'polished-v7-structured-overlay'
        : 'polished-safe-fallback',
      structuredNotationEnabled: enableStructuredNotation,
      structuredNotationFallbackReason: gridValidation.reason,
      productionPromotionAuthorized: false,
    },
    rendererOptions: {
      song: safeSong,
      artist: safeArtist,
      transcriptionType: safeType,
      generatedTab: safeTab,
      tuning: cleanText(tuning, 'Standard Tuning', 80),
      tempo: boundedTempo(tempo),
      timeSignature: cleanText(timeSignature, '4/4', 20),
      keySignature: cleanText(keySignature, '', 40),
      preview: preview === true,
      previewSystems: Math.min(4, Math.max(1, Number(previewSystems) || 4)),
      enableV7MeasureGrid: enableStructuredNotation,
      measureGrid: enableStructuredNotation ? measureGrid : null,
    },
    analysisSummary: {
      analysisEngine: cleanText(analysisEngine, 'unknown', 80),
      confidence:
        Number.isFinite(Number(confidence))
          ? Number(confidence)
          : null,
      difficulty: cleanText(difficulty, '', 80) || null,
      techniques: Array.isArray(techniques)
        ? techniques
            .map((value) => cleanText(value, '', 80))
            .filter(Boolean)
            .slice(0, 40)
        : [],
    },
  };
}
