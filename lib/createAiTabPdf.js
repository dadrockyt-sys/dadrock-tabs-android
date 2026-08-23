import { createTabPdf as createLegacyTabPdf } from '@/lib/createTabPdfPolished';
import { createV143RhythmPdf } from '@/lib/createV143RhythmPdf';
import { validateV143RenderEvents } from '@/lib/v143RenderContract';

export async function createAiTabPdf(options = {}) {
  // Professional Rhythm rendering accepts only the already-authenticated event
  // stream produced by the structured analyzer payload. Validate it without
  // re-projecting/re-numbering event identities used by technique connectors.
  const renderEvents = validateV143RenderEvents(options?.renderEvents);
  const useV143StructuredRenderer =
    String(options?.transcriptionType || '').toLowerCase() === 'rhythm' &&
    String(options?.analysisEngine || '') === 'v143-reference-free-rhythm' &&
    renderEvents.length > 0;

  if (useV143StructuredRenderer) {
    return createV143RhythmPdf({
      ...options,
      renderEvents,
    });
  }

  return createLegacyTabPdf(options);
}
