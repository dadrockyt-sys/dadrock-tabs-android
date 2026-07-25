import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fs from 'fs/promises';
import path from 'path';

export async function createBlankTabPDF() {
  const pdfDoc = await PDFDocument.create();

  const page = pdfDoc.addPage([612, 792]);
  const logoPath = path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png');
const logoBytes = await fs.readFile(logoPath);

const logoImage = await pdfDoc.embedPng(logoBytes);

const logo = logoImage.scale(0.09);

page.drawImage(logoImage, {
  x: (612 - logo.width) / 2,
 y: 690,
  width: logo.width,
  height: logo.height,
});

  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);

  // 
  page.drawText('Professional Guitar Tab', {
  x: 230,
  y: 665,
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

      // TAB LAYOUT
  const labelX = 34;
  const startX = 50;
  const endX = 560;

  const firstRowY = 600;

  // Half-height tab staff
  const stringSpacing = 7;
  const staffHeight = stringSpacing * 5;

  // Space between the top of each tab row
  const rowSpacing = 68;

  // Keep the final row above the bottom margin
  const bottomMargin = 55;

  const measuresPerRow = 6;
  const measureWidth = (endX - startX) / measuresPerRow;

  const stringNames = ['e', 'B', 'G', 'D', 'A', 'E'];

  function drawTabRow(rowTopY, firstMeasureNumber) {
    // Measure numbers above the row
    for (let measure = 0; measure < measuresPerRow; measure++) {
      const measureX = startX + measure * measureWidth;

      page.drawText(
        String(firstMeasureNumber + measure),
        {
          x: measureX + 4,
          y: rowTopY + 9,
          size: 7,
          font: bodyFont,
        }
      );
    }

    // String labels and horizontal lines
    for (let stringIndex = 0; stringIndex < 6; stringIndex++) {
      const y = rowTopY - stringIndex * stringSpacing;

      page.drawText(stringNames[stringIndex], {
        x: labelX,
        y: y - 3,
        size: 8,
        font: bodyFont,
      });

      page.drawLine({
        start: { x: startX, y },
        end: { x: endX, y },
        thickness: 0.75,
        color: rgb(0, 0, 0),
      });
    }

    // Seven bars create six measures
    for (let divider = 0; divider <= measuresPerRow; divider++) {
      const x = startX + divider * measureWidth;

      page.drawLine({
        start: { x, y: rowTopY },
        end: { x, y: rowTopY - staffHeight },
        thickness:
          divider === 0 || divider === measuresPerRow
            ? 1
            : 0.75,
        color: rgb(0, 0, 0),
      });
    }
  }

  // Automatically draw every row that fits on the page
  let rowTopY = firstRowY;
  let firstMeasureNumber = 1;

  while (rowTopY - staffHeight >= bottomMargin) {
    drawTabRow(rowTopY, firstMeasureNumber);

    rowTopY -= rowSpacing;
    firstMeasureNumber += measuresPerRow;
  }

  return await pdfDoc.save();
}
