import { createTabPdf as createLegacyTabPdf } from '@/lib/createTabPdfPolished';
import { createV143RhythmPdf } from '@/lib/createV143RhythmPdf';
import { validateV143RenderEvents } from '@/lib/v143RenderContract';

export async function createAiTabPdf(options = {}) {
  const requestedV143StructuredRhythm =
    String(options?.transcriptionType || '').toLowerCase() === 'rhythm' &&
    String(options?.analysisEngine || '') === 'v143-reference-free-rhythm';

  // Professional Rhythm rendering accepts only the already-authenticated event
  // stream produced by the structured analyzer payload. Validate it without
  // re-projecting/re-numbering event identities used by technique connectors.
  const renderEvents = requestedV143StructuredRhythm
    ? validateV143RenderEvents(options?.renderEvents)
    : [];

  // Defense in depth: even if this lower-level router is called directly,
  // an authenticated V143 request may never fall through to legacy rendering
  // merely because its structured event stream is missing or invalid.
  if (requestedV143StructuredRhythm && renderEvents.length === 0) {
    throw new Error(
      'Authenticated V143 Rhythm requires non-empty valid renderEvents; legacy AI PDF fallback is not allowed.'
    );
  }

  if (requestedV143StructuredRhythm) {
    return createV143RhythmPdf({
      ...options,
      renderEvents,
    });
  }

  return createLegacyTabPdf(options);
}
