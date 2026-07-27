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

  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 48;
  const footerHeight = preview ? 118 : 38;
  const tabFontSize = 9;
  const tabLineHeight = 12;

  let page;
  let y;

  function addPage() {
    page = pdfDoc.addPage([
      pageWidth,
      pageHeight,
    ]);

    page.drawRectangle({
      x: 0,
      y: pageHeight - 92,
      width: pageWidth,
      height: 92,
      color: rgb(0.06, 0.06, 0.07),
    });

    page.drawRectangle({
      x: 0,
      y: pageHeight - 96,
      width: pageWidth,
      height: 4,
      color: rgb(0.96, 0.55, 0.08),
    });

    page.drawText('DADROCK TABS', {
      x: margin,
      y: pageHeight - 47,
      size: 23,
      font: boldFont,
      color: rgb(1, 1, 1),
    });

    page.drawText(
      'AI GUITAR TRANSCRIPTION',
      {
        x: margin,
        y: pageHeight - 70,
        size: 9,
        font: boldFont,
        color: rgb(0.96, 0.55, 0.08),
      }
    );

    page.drawText(
      preview
        ? 'Watermarked preview • educational personal use'
        : 'Educational personal-use transcription',
      {
        x: margin,
        y: 21,
        size: 7,
        font: regularFont,
        color: rgb(0.45, 0.45, 0.45),
      }
    );

    y = pageHeight - 124;
  }

  addPage();

  for (const line of wrapText(song, 36)) {
    page.drawText(line, {
      x: margin,
      y,
      size: 21,
      font: boldFont,
      color: rgb(0.05, 0.05, 0.05),
    });
    y -= 25;
  }

  page.drawText(artist, {
    x: margin,
    y,
    size: 14,
    font: regularFont,
    color: rgb(0.35, 0.35, 0.35),
  });

  y -= 34;

  const details =
    `Part: ${transcriptionType.toUpperCase()}` +
    '    Tuning: Standard' +
    '    Format: TAB';

  page.drawText(details, {
    x: margin,
    y,
    size: 9,
    font: boldFont,
    color: rgb(0.18, 0.18, 0.18),
  });

  y -= 22;

  page.drawLine({
    start: { x: margin, y },
    end: { x: pageWidth - margin, y },
    thickness: 1.5,
    color: rgb(0.1, 0.1, 0.1),
  });

  y -= 24;

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
        borderColor: rgb(0.96, 0.55, 0.08),
        borderWidth: 1.5,
      });

      currentPage.drawText('PREVIEW ONLY', {
        x: margin + 20,
        y: 116,
        size: 11,
        font: boldFont,
        color: rgb(0.96, 0.45, 0.05),
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

    currentPage.drawText(pageNumber, {
      x: pageWidth - margin - 58,
      y: 21,
      size: 7,
      font: regularFont,
      color: rgb(0.45, 0.45, 0.45),
    });
  });

  return pdfDoc.save();
}
