import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fs from 'fs/promises';
import path from 'path';

export async function createBlankTabPDF() {
  const pdfDoc = await PDFDocument.create();

  const page = pdfDoc.addPage([612, 792]);

  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);

  // Header
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

  page.drawText('Song Title', {
    x: 50,
    y: 690,
    size: 18,
    font: titleFont,
  });

  page.drawText('Artist Name', {
    x: 50,
    y: 668,
    size: 14,
    font: bodyFont,
  });

  page.drawText('INTRO', {
  x: 50,
  y: 625,
  size: 12,
  font: titleFont,
});

page.drawText('Standard Tuning • 4/4 • 120 BPM', {
  x: 360,
  y: 625,
  size: 9,
  font: bodyFont,
});

  // Six guitar strings
  const labelX = 34;
const startX = 50;
const endX = 560;
const startY = 600;
const spacing = 14;

const stringNames = ['e', 'B', 'G', 'D', 'A', 'E'];

  for (let i = 0; i < 6; i++) {
  const y = startY - i * spacing;

  page.drawText(stringNames[i], {
    x: labelX,
    y: y - 4,
    size: 10,
    font: bodyFont,
  });

  page.drawLine({
    start: { x: startX, y },
    end: { x: endX, y },
    thickness: 1,
    color: rgb(0, 0, 0),
  });
  }

  // Four measure bars
  const barPositions = [50, 177.5, 305, 432.5, 560];

  barPositions.forEach((x) => {
    page.drawLine({
      start: { x, y: startY },
      end: { x, y: startY - spacing * 5 },
      thickness: 1,
      color: rgb(0, 0, 0),
    });
  });

  return await pdfDoc.save();
}
