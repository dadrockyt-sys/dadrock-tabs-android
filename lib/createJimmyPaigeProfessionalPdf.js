import { createTabPdf as createStructuredPolishedTabPdf } from '@/lib/createTabPdfPolishedV7';
import { buildJimmyPaigeProfessionalPdfOptions } from '@/lib/jimmyPaigeProfessionalPdfContract';

export async function createJimmyPaigeProfessionalPdf(input = {}) {
  const contract = buildJimmyPaigeProfessionalPdfOptions(input);

  const pdfBytes = await createStructuredPolishedTabPdf(
    contract.rendererOptions
  );

  return {
    pdfBytes,
    rendererContract: contract.rendererContract,
    analysisSummary: contract.analysisSummary,
  };
}
