import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fs from 'fs/promises';
import path from 'path';

export async function createBlankTabPDF() {
  const pdfDoc = await PDFDocument.create();

  const page = pdfDoc.addPage([612, 792]);

  const logoPath = path.join(
    process.cwd(),
    'public',
    'DadRock-Tabs-Logo.png'
  );

  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const logo = logoImage.scale(0.09);

  page.drawImage(logoImage, {
    x: (612 - logo.width) / 2,
    y: 705,
    width: logo.width,
    height: logo.height,
  });

  const titleFont = await pdfDoc.embedFont(
    StandardFonts.HelveticaBold
  );

  const bodyFont = await pdfDoc.embedFont(
    StandardFonts.Helvetica
  );

    const songTitle = 'Song Title';
  const artistName = 'Artist Name';

  page.drawText(songTitle, {
    x: 50,
    y: 675,
    size: 20,
    font: titleFont,
    color: rgb(0, 0, 0),
  });

  page.drawText(artistName, {
    x: 50,
    y: 653,
    size: 13,
    font: bodyFont,
    color: rgb(0.35, 0.35, 0.35),
  });

  page.drawLine({
  start: { x: 50, y: 646 },
  end: { x: 215, y: 646 },
  thickness: 0.8,
  color: rgb(0.82, 0.82, 0.82),
});

   const tagline = 'DIY Guitar and Bass Tab Generator';
const taglineSize = 16;
const taglineY = 678;

const taglineWidth =
  titleFont.widthOfTextAtSize(tagline, taglineSize);

const taglineX = (612 - taglineWidth) / 2;

page.drawText(tagline, {
  x: taglineX,
  y: taglineY,
  size: taglineSize,
  font: titleFont,
  color: rgb(1, 0.27, 0),
});

  page.drawText('INTRO', {
    x: 50,
    y: 635,
    size: 12,
    font: titleFont,
  });

  const settingsText = 'Standard Tuning • 4/4 • 120 BPM';
  const settingsSize = 9;
  const settingsWidth = bodyFont.widthOfTextAtSize(
    settingsText,
    settingsSize
  );

  page.drawText(settingsText, {
    x: 560 - settingsWidth,
    y: 625,
    size: settingsSize,
    font: bodyFont,
  });

  const labelX = 34;
  const startX = 50;
  const endX = 560;

  const firstRowY = 625;
  const stringSpacing = 7;
  const staffHeight = stringSpacing * 5;

  const rowSpacing = 65;
  const bottomMargin = 48;

  const measuresPerRow = 6;
  const measureWidth = (endX - startX) / measuresPerRow;

  const stringNames = ['e', 'B', 'G', 'D', 'A', 'E'];

  function drawTabRow(rowTopY, firstMeasureNumber) {
    for (
      let measure = 0;
      measure < measuresPerRow;
      measure++
    ) {
      const measureX =
        startX + measure * measureWidth;

      page.drawText(
        String(firstMeasureNumber + measure),
        {
          x: measureX + 4,
          y: rowTopY + 10,
          size: 8,
          font: bodyFont,
        }
      );
    }

    for (
      let stringIndex = 0;
      stringIndex < stringNames.length;
      stringIndex++
    ) {
      const y =
        rowTopY - stringIndex * stringSpacing;

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

    for (
      let divider = 0;
      divider <= measuresPerRow;
      divider++
    ) {
      const x =
        startX + divider * measureWidth;

      page.drawLine({
        start: { x, y: rowTopY },
        end: {
          x,
          y: rowTopY - staffHeight,
        },
        thickness:
          divider === 0 ||
          divider === measuresPerRow
            ? 1
            : 0.75,
        color: rgb(0, 0, 0),
      });
    }

    page.drawLine({
      start: {
        x: endX - 3,
        y: rowTopY,
      },
      end: {
        x: endX - 3,
        y: rowTopY - staffHeight,
      },
      thickness: 1,
      color: rgb(0, 0, 0),
    });
  }

  let rowTopY = firstRowY;
  let firstMeasureNumber = 1;

  while (
    rowTopY - staffHeight >= bottomMargin
  ) {
    drawTabRow(
      rowTopY,
      firstMeasureNumber
    );

    rowTopY -= rowSpacing;
    firstMeasureNumber += measuresPerRow;
  }

    // Page numbering footer
  const pages = pdfDoc.getPages();
  const totalPages = pages.length;

  pages.forEach((currentPage, index) => {
    const pageNumberText = `Page ${index + 1} of ${totalPages}`;
    const pageNumberSize = 9;

    const pageNumberWidth = bodyFont.widthOfTextAtSize(
      pageNumberText,
      pageNumberSize
    );

    const pageNumberX = (612 - pageNumberWidth) / 2;
    const footerY = 24;

    currentPage.drawLine({
      start: { x: 50, y: footerY + 3 },
      end: { x: pageNumberX - 14, y: footerY + 3 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    currentPage.drawText(pageNumberText, {
      x: pageNumberX,
      y: footerY,
      size: pageNumberSize,
      font: bodyFont,
      color: rgb(0.2, 0.2, 0.2),
    });

    currentPage.drawLine({
      start: {
        x: pageNumberX + pageNumberWidth + 14,
        y: footerY + 3,
      },
      end: { x: 560, y: footerY + 3 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });
  });

  return await pdfDoc.save();
}
