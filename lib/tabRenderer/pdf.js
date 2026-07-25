import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

export async function createBlankTabPDF() {
  const pdfDoc = await PDFDocument.create();

  const page = pdfDoc.addPage([612, 792]);

  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);

  page.drawText('DADROCK TABS', {
    x: 175,
    y: 760,
    size: 24,
    font: titleFont,
    color: rgb(0.95, 0.45, 0.05),
  });

  page.drawText('Professional Guitar Tab', {
    x: 205,
    y: 735,
    size: 12,
    font: bodyFont,
  });

  return await pdfDoc.save();
}
