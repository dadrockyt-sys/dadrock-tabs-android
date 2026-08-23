import { createAiTabPdf } from '@/lib/createAiTabPdf';
import { createTabPdf as createStructuredPolishedTabPdf } from '@/lib/createTabPdfPolishedV7';
import { buildJimmyPaigeProfessionalPdfOptions } from '@/lib/jimmyPaigeProfessionalPdfContract';
import { validateV143RenderEvents } from '@/lib/v143RenderContract';

export async function createJimmyPaigeProfessionalPdf(input = {}) {
  const contract = buildJimmyPaigeProfessionalPdfOptions(input);
  const analysisEngine = String(input?.analysisEngine || '').trim();

  const requestedV143StructuredRhythm =
    contract.rendererOptions.transcriptionType === 'rhythm' &&
    analysisEngine === 'v143-reference-free-rhythm';

  // Authenticated V143 renderEvents have already been projected by the analyzer
  // payload boundary. Validate that exact stream here instead of projecting it
  // again: the PDF wrapper must never compact/drop malformed events and then
  // present the surviving subset as a successful V143 transcription.
  const renderEvents = requestedV143StructuredRhythm
    ? validateV143RenderEvents(input?.renderEvents)
    : [];

  // Never silently downgrade a response that explicitly identifies itself as
  // authenticated V143 Rhythm. Missing/invalid structured events fail closed
  // instead of falling through to the legacy polished renderer.
  if (requestedV143StructuredRhythm && renderEvents.length === 0) {
    throw new Error(
      'Authenticated V143 Rhythm requires non-empty valid renderEvents; legacy PDF fallback is not allowed.'
    );
  }

  if (requestedV143StructuredRhythm) {
    const pdfBytes = await createAiTabPdf({
      ...contract.rendererOptions,
      analysisEngine,
      renderEvents,
    });

    return {
      pdfBytes,
      rendererContract: {
        ...contract.rendererContract,
        mode: 'v143-structured-rhythm',
        structuredNotationEnabled: true,
        structuredNotationSource: 'v143-render-contract-v1',
        structuredRenderEventCount: renderEvents.length,
        structuredNotationFallbackReason: null,
      },
      analysisSummary: contract.analysisSummary,
    };
  }

  const pdfBytes = await createStructuredPolishedTabPdf(
    contract.rendererOptions
  );

  return {
    pdfBytes,
    rendererContract: contract.rendererContract,
    analysisSummary: contract.analysisSummary,
  };
}
