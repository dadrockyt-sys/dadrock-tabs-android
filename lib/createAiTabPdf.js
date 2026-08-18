import { createTabPdf as createLegacyTabPdf } from '@/lib/createTabPdfPolished';
import { createV143RhythmPdf } from '@/lib/createV143RhythmPdf';
import { projectV143RenderEvents } from '@/lib/v143RenderContract';

export async function createAiTabPdf(options = {}) {
  const renderEvents = projectV143RenderEvents(options?.renderEvents);
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
