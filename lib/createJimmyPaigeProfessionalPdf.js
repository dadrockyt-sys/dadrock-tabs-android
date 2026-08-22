import { createAiTabPdf } from '@/lib/createAiTabPdf';
import { createTabPdf as createStructuredPolishedTabPdf } from '@/lib/createTabPdfPolishedV7';
import { buildJimmyPaigeProfessionalPdfOptions } from '@/lib/jimmyPaigeProfessionalPdfContract';
import { projectV143RenderEvents } from '@/lib/v143RenderContract';

export async function createJimmyPaigeProfessionalPdf(input = {}) {
  const contract = buildJimmyPaigeProfessionalPdfOptions(input);
  const analysisEngine = String(input?.analysisEngine || '').trim();
  const renderEvents = projectV143RenderEvents(input?.renderEvents);

  const useV143StructuredRhythm =
    contract.rendererOptions.transcriptionType === 'rhythm' &&
    analysisEngine === 'v143-reference-free-rhythm' &&
    renderEvents.length > 0;

  if (useV143StructuredRhythm) {
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
