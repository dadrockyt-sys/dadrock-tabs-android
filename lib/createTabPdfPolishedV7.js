import { PDFDocument, StandardFonts } from 'pdf-lib';
import { createTabPdf as createPolishedTabPdf } from '@/lib/createTabPdfPolished';
import { drawV7MeasureGridOverlay } from '@/lib/v7MeasureGridOverlay';

function v7OverlayRequested(options) {
  return (
    options?.enableV7MeasureGrid === true &&
    options?.measureGrid &&
    typeof options.measureGrid === 'object'
  );
}

export async function createTabPdf(options = {}) {
  const polishedBytes = await createPolishedTabPdf(options);

  if (!v7OverlayRequested(options)) {
    return polishedBytes;
  }

  const pdfDoc = await PDFDocument.load(polishedBytes);
  const pages = pdfDoc.getPages();

  if (!pages.length) {
    return polishedBytes;
  }

  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  const overlayResult = drawV7MeasureGridOverlay({
    pages,
    generatedTab: options.generatedTab,
    transcriptionType: options.transcriptionType,
    measureGrid: options.measureGrid,
    bodyFont,
    boldFont,
  });

  if (!overlayResult.enabled) {
    return polishedBytes;
  }

  return pdfDoc.save();
}
