import fs from 'node:fs/promises';
import path from 'node:path';
import {
  PDFDocument,
  StandardFonts,
  degrees,
  rgb,
} from 'pdf-lib';

function wrapText(text, maximumCharacters) {
  const words = String(text || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  const lines = [];
  let currentLine = '';

  for (const word of words) {
    const candidate = currentLine
      ? `${currentLine} ${word}`
      : word;

    if (candidate.length <= maximumCharacters) {
      currentLine = candidate;
      continue;
    }

    if (currentLine) {
      lines.push(currentLine);
    }

    currentLine = word;
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines.length ? lines : [''];
}

function getPreviewLines(
  generatedTab,
  transcriptionType,
  previewSystems
) {
  const lines = String(generatedTab || '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n');

  const rowsPerSystem =
    transcriptionType === 'bass' ? 4 : 6;
  const targetRows =
    Math.max(1, previewSystems) * rowsPerSystem;

  const previewLines = [];
  let stringRows = 0;

  for (const line of lines) {
    previewLines.push(line);

    if (/^\s*(e|B|G|D|A|E)\|/i.test(line)) {
      stringRows += 1;
    }

    if (stringRows >= targetRows) {
      break;
    }
  }

  return previewLines;
}

async function loadLogo(pdfDoc) {
  const logoPath = path.join(
    process.cwd(),
    'public',
    'DadRock-Tabs-Logo.png'
  );

  const logoBytes = await fs.readFile(logoPath);
  return pdfDoc.embedPng(logoBytes);
}

export async function createTabPdf({
  song,
  artist,
  transcriptionType,
  generatedTab,
  preview = false,
  previewSystems = 4,
}) {
  const pdfDoc = await PDFDocument.create();

  const regularFont = await pdfDoc.embedFont(
    StandardFonts.Helvetica
  );
  const boldFont = await pdfDoc.embedFont(
    StandardFonts.HelveticaBold
  );
  const tabFont = await pdfDoc.embedFont(
    StandardFonts.Courier
  );
  const logoImage = await loadLogo(pdfDoc);

  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 50;
  const footerHeight = preview ? 126 : 42;
  const tabFontSize = 9;
  const tabLineHeight = 12;
  const largeLogo = logoImage.scale(0.09);
  const smallLogo = logoImage.scale(0.055);

  let page;
  let y;
  let pageIndex = 0;

  function drawFullHeader(currentPage) {
    currentPage.drawImage(logoImage, {
      x: (pageWidth - largeLogo.width) / 2,
      y: 705,
      width: largeLogo.width,
      height: largeLogo.height,
    });

    const tagline = 'DIY Guitar and Bass Tab Generator';
    const taglineSize = 16;
    const taglineWidth =
      boldFont.widthOfTextAtSize(
        tagline,
        taglineSize
      );

    currentPage.drawText(tagline, {
      x: (pageWidth - taglineWidth) / 2,
      y: 678,
      size: taglineSize,
      font: boldFont,
      color: rgb(1, 0.27, 0),
    });

    y = 646;

    for (const line of wrapText(song, 36)) {
      currentPage.drawText(line, {
        x: margin,
        y,
        size: 20,
        font: boldFont,
        color: rgb(0, 0, 0),
      });
      y -= 24;
    }

    currentPage.drawText(artist, {
      x: margin,
      y,
      size: 13,
      font: regularFont,
      color: rgb(0.35, 0.35, 0.35),
    });

    y -= 23;

    currentPage.drawLine({
      start: { x: margin, y: y + 8 },
      end: { x: 215, y: y + 8 },
      thickness: 0.8,
      color: rgb(0.82, 0.82, 0.82),
    });

    const details =
      `Part: ${transcriptionType.toUpperCase()}` +
      '    Tuning: Standard' +
      '    Format: TAB';

    currentPage.drawText(details, {
      x: margin,
      y: y - 8,
      size: 9,
      font: boldFont,
      color: rgb(0.18, 0.18, 0.18),
    });

    y -= 30;

    currentPage.drawLine({
      start: { x: margin, y },
      end: { x: pageWidth - margin, y },
      thickness: 1.2,
      color: rgb(0.1, 0.1, 0.1),
    });

    y -= 24;
  }

  function drawCompactHeader(currentPage) {
    currentPage.drawImage(logoImage, {
      x: margin,
      y: 727,
      width: smallLogo.width,
      height: smallLogo.height,
    });

    const continuationTitle = `${song} — ${artist}`;

    currentPage.drawText(
      continuationTitle.slice(0, 68),
      {
        x: margin + smallLogo.width + 12,
        y: 744,
        size: 12,
        font: boldFont,
        color: rgb(0.08, 0.08, 0.08),
      }
    );

    currentPage.drawText('CONTINUED', {
      x: margin + smallLogo.width + 12,
      y: 730,
      size: 8,
      font: regularFont,
      color: rgb(0.55, 0.55, 0.55),
    });

    currentPage.drawLine({
      start: { x: margin, y: 716 },
      end: { x: pageWidth - margin, y: 716 },
      thickness: 0.6,
      color: rgb(0.75, 0.75, 0.75),
    });

    y = 690;
  }

  function addPage() {
    page = pdfDoc.addPage([
      pageWidth,
      pageHeight,
    ]);

    if (pageIndex === 0) {
      drawFullHeader(page);
    } else {
      drawCompactHeader(page);
    }

    pageIndex += 1;
  }

  addPage();

  const tabLines = preview
    ? getPreviewLines(
        generatedTab,
        transcriptionType,
        previewSystems
      )
    : String(generatedTab || '').split('\n');

  for (const line of tabLines) {
    if (
      y <
      margin + footerHeight + tabLineHeight
    ) {
      if (preview) {
        break;
      }
      addPage();
    }

    const safeLine = line
      .replace(/[^\x20-\x7E]/g, '')
      .slice(0, 88);

    page.drawText(safeLine || ' ', {
      x: margin,
      y,
      size: tabFontSize,
      font: tabFont,
      color: rgb(0, 0, 0),
    });

    y -= tabLineHeight;
  }

  const pages = pdfDoc.getPages();

  pages.forEach((currentPage, index) => {
    if (preview) {
      currentPage.drawText(
        'DADROCK TABS PREVIEW',
        {
          x: 72,
          y: 330,
          size: 38,
          font: boldFont,
          color: rgb(0.72, 0.72, 0.72),
          rotate: degrees(34),
          opacity: 0.3,
        }
      );

      currentPage.drawRectangle({
        x: margin,
        y: 54,
        width: pageWidth - margin * 2,
        height: 92,
        color: rgb(0.98, 0.95, 0.9),
        borderColor: rgb(1, 0.27, 0),
        borderWidth: 1.5,
      });

      currentPage.drawText('PREVIEW ONLY', {
        x: margin + 20,
        y: 116,
        size: 11,
        font: boldFont,
        color: rgb(1, 0.27, 0),
      });

      currentPage.drawText(
        'Unlock the complete unwatermarked tablature PDF below.',
        {
          x: margin + 20,
          y: 92,
          size: 10,
          font: boldFont,
          color: rgb(0.12, 0.12, 0.12),
        }
      );

      currentPage.drawText(
        'The full version contains the complete transcription and clean PDF download.',
        {
          x: margin + 20,
          y: 72,
          size: 8,
          font: regularFont,
          color: rgb(0.35, 0.35, 0.35),
        }
      );
    }

    const pageNumber =
      `Page ${index + 1} of ${pages.length}`;
    const pageNumberSize = 9;
    const pageNumberWidth =
      regularFont.widthOfTextAtSize(
        pageNumber,
        pageNumberSize
      );
    const pageNumberX =
      (pageWidth - pageNumberWidth) / 2;

    currentPage.drawLine({
      start: { x: margin, y: 27 },
      end: { x: pageNumberX - 14, y: 27 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    currentPage.drawText(pageNumber, {
      x: pageNumberX,
      y: 24,
      size: pageNumberSize,
      font: regularFont,
      color: rgb(0.2, 0.2, 0.2),
    });

    currentPage.drawLine({
      start: {
        x: pageNumberX + pageNumberWidth + 14,
        y: 27,
      },
      end: { x: pageWidth - margin, y: 27 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    const footerBrand =
      preview
        ? 'DadRock Tabs preview • dadrocktabs.com'
        : 'Generated by DadRock Tabs • dadrocktabs.com';
    const footerBrandSize = 7;
    const footerBrandWidth =
      regularFont.widthOfTextAtSize(
        footerBrand,
        footerBrandSize
      );

    currentPage.drawText(footerBrand, {
      x: (pageWidth - footerBrandWidth) / 2,
      y: 10,
      size: footerBrandSize,
      font: regularFont,
      color: rgb(0.4, 0.4, 0.4),
    });
  });

  return pdfDoc.save();
}
