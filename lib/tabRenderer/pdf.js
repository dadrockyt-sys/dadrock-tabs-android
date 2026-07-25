import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fs from 'fs/promises';
import path from 'path';

export async function createBlankTabPDF({
  songTitle = 'Song Title',
  artistName = 'Artist Name',
  totalMeasures = 192,
  tuning = 'Standard Tuning',
  timeSignature = '4/4',
  bpm = 120,
} = {}) {
  const pdfDoc = await PDFDocument.create();

  const pageWidth = 612;
  const pageHeight = 792;

  const titleFont = await pdfDoc.embedFont(
    StandardFonts.HelveticaBold
  );

  const bodyFont = await pdfDoc.embedFont(
    StandardFonts.Helvetica
  );

  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  
  const logoPath = path.join(
    process.cwd(),
    'public',
    'DadRock-Tabs-Logo.png'
  );

  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);

  const largeLogo = logoImage.scale(0.09);
  const smallLogo = logoImage.scale(0.055);

  const startX = 50;
  const endX = 560;
  const labelX = 34;

  const measuresPerRow = 6;
  const measureWidth =
    (endX - startX) / measuresPerRow;

  const stringSpacing = 7;
  const staffHeight = stringSpacing * 5;

  const stringNames = ['e', 'B', 'G', 'D', 'A', 'E'];

  const pageOneRows = 10;
  const continuationRows = 11;

  const pageOneMeasureCapacity =
    pageOneRows * measuresPerRow;

  const continuationMeasureCapacity =
    continuationRows * measuresPerRow;

  const safeTotalMeasures = Math.max(
    1,
    Number(totalMeasures) || pageOneMeasureCapacity
  );

  const settingsText =
    `${tuning} • ${timeSignature} • ${bpm} BPM`;

  function drawFullHeader(page) {
    page.drawImage(logoImage, {
      x: (pageWidth - largeLogo.width) / 2,
      y: 705,
      width: largeLogo.width,
      height: largeLogo.height,
    });

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

    const tagline =
      'DIY Guitar and Bass Tab Generator';

    const taglineSize = 16;

    const taglineWidth =
      titleFont.widthOfTextAtSize(
        tagline,
        taglineSize
      );

    page.drawText(tagline, {
      x: (pageWidth - taglineWidth) / 2,
      y: 678,
      size: taglineSize,
      font: titleFont,
      color: rgb(1, 0.27, 0),
    });

    page.drawText('INTRO', {
      x: 50,
      y: 635,
      size: 12,
      font: titleFont,
      color: rgb(0, 0, 0),
    });

    const settingsSize = 9;

    const settingsWidth =
      bodyFont.widthOfTextAtSize(
        settingsText,
        settingsSize
      );

    page.drawText(settingsText, {
      x: endX - settingsWidth,
      y: 635,
      size: settingsSize,
      font: bodyFont,
      color: rgb(0.15, 0.15, 0.15),
    });
  }

  function drawCompactHeader(page) {
    page.drawImage(logoImage, {
      x: 50,
      y: 727,
      width: smallLogo.width,
      height: smallLogo.height,
    });

    const continuationTitle =
      `${songTitle} — ${artistName}`;

    page.drawText(continuationTitle, {
      x: 50 + smallLogo.width + 12,
      y: 744,
      size: 12,
      font: titleFont,
      color: rgb(0.08, 0.08, 0.08),
    });

    page.drawText('CONTINUED', {
      x: 50 + smallLogo.width + 12,
      y: 730,
      size: 8,
      font: bodyFont,
      color: rgb(0.55, 0.55, 0.55),
    });

    const settingsSize = 8;

    const settingsWidth =
      bodyFont.widthOfTextAtSize(
        settingsText,
        settingsSize
      );

    page.drawText(settingsText, {
      x: endX - settingsWidth,
      y: 730,
      size: settingsSize,
      font: bodyFont,
      color: rgb(0.25, 0.25, 0.25),
    });

    page.drawLine({
      start: { x: 50, y: 716 },
      end: { x: 560, y: 716 },
      thickness: 0.6,
      color: rgb(0.75, 0.75, 0.75),
    });
  }

  function drawTabRow(
    page,
    rowTopY,
    firstMeasureNumber,
    finalMeasureNumber
  ) {
    for (
      let measureIndex = 0;
      measureIndex < measuresPerRow;
      measureIndex++
    ) {
      const measureNumber =
        firstMeasureNumber + measureIndex;

      if (measureNumber <= finalMeasureNumber) {
        const measureX =
          startX + measureIndex * measureWidth;

        page.drawText(String(measureNumber), {
  x: measureX + 2,
  y: rowTopY + 10,
  size: 7,
  font: boldFont,
  color: rgb(0.35, 0.35, 0.35),
});
      }
    }

    for (
      let stringIndex = 0;
      stringIndex < stringNames.length;
      stringIndex++
    ) {
      const y =
        rowTopY -
        stringIndex * stringSpacing;

      page.drawText(
  stringNames[stringIndex].toUpperCase(),
  {
    x: labelX,
    y: y - 3,
    size: 7,
    font: boldFont,
    color: rgb(0.15, 0.15, 0.15),
  }
);

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

  function drawPageRows({
    page,
    firstMeasureNumber,
    rowCount,
    firstRowY,
    rowSpacing,
    finalMeasureNumber,
  }) {
    let nextMeasureNumber =
      firstMeasureNumber;

    for (
      let rowIndex = 0;
      rowIndex < rowCount;
      rowIndex++
    ) {
      if (
        nextMeasureNumber >
        finalMeasureNumber
      ) {
        break;
      }

      const rowTopY =
        firstRowY -
        rowIndex * rowSpacing;

      drawTabRow(
        page,
        rowTopY,
        nextMeasureNumber,
        finalMeasureNumber
      );

      nextMeasureNumber +=
        measuresPerRow;
    }

    return nextMeasureNumber;
  }

  let nextMeasureNumber = 1;

  const firstPage = pdfDoc.addPage([
    pageWidth,
    pageHeight,
  ]);

  drawFullHeader(firstPage);

  nextMeasureNumber = drawPageRows({
    page: firstPage,
    firstMeasureNumber: nextMeasureNumber,
    rowCount: pageOneRows,
    firstRowY: 625,
    rowSpacing: 58,
    finalMeasureNumber: safeTotalMeasures,
  });

  while (
    nextMeasureNumber <= safeTotalMeasures
  ) {
    const continuationPage =
      pdfDoc.addPage([
        pageWidth,
        pageHeight,
      ]);

    drawCompactHeader(continuationPage);

    nextMeasureNumber = drawPageRows({
      page: continuationPage,
      firstMeasureNumber:
        nextMeasureNumber,
      rowCount: continuationRows,
      firstRowY: 690,
      rowSpacing: 58,
      finalMeasureNumber:
        safeTotalMeasures,
    });
  }

  const pages = pdfDoc.getPages();
  const totalPages = pages.length;

  pages.forEach((currentPage, index) => {
    const pageNumberText =
      `Page ${index + 1} of ${totalPages}`;

    const pageNumberSize = 9;

    const pageNumberWidth =
      bodyFont.widthOfTextAtSize(
        pageNumberText,
        pageNumberSize
      );

    const pageNumberX =
      (pageWidth - pageNumberWidth) / 2;

    const footerY = 24;

    currentPage.drawLine({
      start: {
        x: 50,
        y: footerY + 3,
      },
      end: {
        x: pageNumberX - 14,
        y: footerY + 3,
      },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    currentPage.drawText(
      pageNumberText,
      {
        x: pageNumberX,
        y: footerY,
        size: pageNumberSize,
        font: bodyFont,
        color: rgb(0.2, 0.2, 0.2),
      }
    );

    currentPage.drawLine({
      start: {
        x:
          pageNumberX +
          pageNumberWidth +
          14,
        y: footerY + 3,
      },
      end: {
        x: 560,
        y: footerY + 3,
      },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    const footerBrand =
      'Generated by DadRock Tabs • dadrocktabs.com';

    const footerBrandSize = 7;

    const footerBrandWidth =
      bodyFont.widthOfTextAtSize(
        footerBrand,
        footerBrandSize
      );

    currentPage.drawText(
      footerBrand,
      {
        x:
          (pageWidth -
            footerBrandWidth) /
          2,
        y: 10,
        size: footerBrandSize,
        font: bodyFont,
        color: rgb(0.4, 0.4, 0.4),
      }
    );
  });

  return await pdfDoc.save();
}
