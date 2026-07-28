import fs from 'node:fs/promises';
import path from 'node:path';
import {
  PDFDocument,
  StandardFonts,
  degrees,
  rgb,
} from 'pdf-lib';

const PDF_PRODUCT_TITLE = 'DIY Guitar & Bass TAB Generator';

function cleanLines(value) {
  return String(value || '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n');
}

function parseTabSystems(generatedTab, transcriptionType) {
  const expectedRows = transcriptionType === 'bass' ? 4 : 6;
  const systems = [];
  let current = [];

  for (const rawLine of cleanLines(generatedTab)) {
    const match = rawLine.match(/^\s*([eEADGB])\|?(.*)$/);

    if (!match) {
      if (current.length === expectedRows) systems.push(current);
      current = [];
      continue;
    }

    current.push({
      label: match[1],
      content: match[2] || '',
    });

    if (current.length === expectedRows) {
      systems.push(current);
      current = [];
    }
  }

  if (current.length === expectedRows) systems.push(current);
  return systems;
}

function getLabels(transcriptionType) {
  return transcriptionType === 'bass'
    ? ['G', 'D', 'A', 'E']
    : ['e', 'B', 'G', 'D', 'A', 'E'];
}

function drawFretTokens({ page, font, content, stringY, startX, endX }) {
  const source = String(content || '');
  const usableWidth = endX - startX;
  const sourceLength = Math.max(source.length, 1);
  const tokenPattern = /\d+|[xX]/g;
  let match;

  while ((match = tokenPattern.exec(source))) {
    const token = match[0];
    const ratio = Math.min(1, match.index / sourceLength);
    const x = startX + ratio * usableWidth;
    const size = 7.5;
    const width = font.widthOfTextAtSize(token, size);

    page.drawRectangle({
      x: x - 1.5,
      y: stringY - 4.5,
      width: width + 3,
      height: 10,
      color: rgb(1, 1, 1),
    });

    page.drawText(token, {
      x,
      y: stringY - 3,
      size,
      font,
      color: rgb(0.05, 0.05, 0.05),
    });
  }
}

export async function createTabPdf({
  song,
  artist,
  transcriptionType,
  generatedTab,
  tuning = 'Standard Tuning',
  tempo = 120,
  timeSignature = '4/4',
  keySignature = '',
  preview = false,
  previewSystems = 4,
}) {
  const pdfDoc = await PDFDocument.create();
  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const tabFont = await pdfDoc.embedFont(StandardFonts.CourierBold);

  const logoPath = path.join(
    process.cwd(),
    'public',
    'DadRock-Tabs-Logo.png'
  );
  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const largeLogo = logoImage.scale(0.09);
  const smallLogo = logoImage.scale(0.055);

  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 50;
  const startX = 50;
  const endX = 560;
  const measuresPerRow = 6;
  const measureWidth = (endX - startX) / measuresPerRow;
  const labels = getLabels(transcriptionType);
  const stringSpacing = transcriptionType === 'bass' ? 9 : 7;
  const staffHeight = stringSpacing * (labels.length - 1);
  const rowSpacing = transcriptionType === 'bass' ? 62 : 58;
  const firstPageRows = preview ? Math.max(1, Math.min(4, Number(previewSystems) || 4)) : 9;
  const continuationRows = transcriptionType === 'bass' ? 10 : 11;

  const parsedSystems = parseTabSystems(generatedTab, transcriptionType);
  const limitedSystems = preview
    ? parsedSystems.slice(0, firstPageRows)
    : parsedSystems;
  const systems = limitedSystems.length
    ? limitedSystems
    : [labels.map((label) => ({ label, content: '' }))];

  const metadataParts = [
    String(tuning || 'Standard Tuning'),
    String(timeSignature || '4/4'),
    `${Number(tempo) || 120} BPM`,
  ];
  if (keySignature) metadataParts.push(String(keySignature));
  const settingsText = metadataParts.join(' • ');

  function drawFullHeader(page) {
    page.drawImage(logoImage, {
      x: (pageWidth - largeLogo.width) / 2,
      y: 705,
      width: largeLogo.width,
      height: largeLogo.height,
    });

    const tagline = PDF_PRODUCT_TITLE;
    const taglineSize = 16;
    const taglineWidth = titleFont.widthOfTextAtSize(tagline, taglineSize);
    page.drawText(tagline, {
      x: (pageWidth - taglineWidth) / 2,
      y: 678,
      size: taglineSize,
      font: titleFont,
      color: rgb(1, 0.27, 0),
    });

    page.drawText(String(song || 'Untitled'), {
      x: margin,
      y: 648,
      size: 20,
      font: titleFont,
      color: rgb(0, 0, 0),
    });

    page.drawText(String(artist || 'Unknown Artist'), {
      x: margin,
      y: 626,
      size: 13,
      font: bodyFont,
      color: rgb(0.35, 0.35, 0.35),
    });

    page.drawLine({
      start: { x: margin, y: 616 },
      end: { x: 215, y: 616 },
      thickness: 0.8,
      color: rgb(0.82, 0.82, 0.82),
    });

    page.drawText(String(transcriptionType || 'lead').toUpperCase(), {
      x: margin,
      y: 594,
      size: 10,
      font: titleFont,
      color: rgb(0.12, 0.12, 0.12),
    });

    const settingsSize = 9;
    const settingsWidth = bodyFont.widthOfTextAtSize(settingsText, settingsSize);
    page.drawText(settingsText, {
      x: endX - settingsWidth,
      y: 594,
      size: settingsSize,
      font: bodyFont,
      color: rgb(0.2, 0.2, 0.2),
    });
  }

  function drawCompactHeader(page) {
    page.drawImage(logoImage, {
      x: margin,
      y: 727,
      width: smallLogo.width,
      height: smallLogo.height,
    });

    const title = `${String(song || 'Untitled')} — ${String(artist || 'Unknown Artist')}`;
    page.drawText(title, {
      x: margin + smallLogo.width + 12,
      y: 744,
      size: 12,
      font: titleFont,
      color: rgb(0.08, 0.08, 0.08),
    });

    page.drawText('CONTINUED', {
      x: margin + smallLogo.width + 12,
      y: 730,
      size: 8,
      font: bodyFont,
      color: rgb(0.55, 0.55, 0.55),
    });

    const settingsSize = 8;
    const settingsWidth = bodyFont.widthOfTextAtSize(settingsText, settingsSize);
    page.drawText(settingsText, {
      x: endX - settingsWidth,
      y: 730,
      size: settingsSize,
      font: bodyFont,
      color: rgb(0.25, 0.25, 0.25),
    });

    page.drawLine({
      start: { x: margin, y: 716 },
      end: { x: endX, y: 716 },
      thickness: 0.6,
      color: rgb(0.75, 0.75, 0.75),
    });
  }

  function drawSystem(page, system, rowTopY, firstMeasureNumber) {
    for (let measure = 0; measure < measuresPerRow; measure += 1) {
      page.drawText(String(firstMeasureNumber + measure), {
        x: startX + measure * measureWidth + 3,
        y: rowTopY + 10,
        size: 8,
        font: titleFont,
        color: rgb(0.35, 0.35, 0.35),
      });
    }

    for (let stringIndex = 0; stringIndex < labels.length; stringIndex += 1) {
      const stringY = rowTopY - stringIndex * stringSpacing;
      const row = system[stringIndex] || {
        label: labels[stringIndex],
        content: '',
      };

      page.drawText(labels[stringIndex], {
        x: 36,
        y: stringY - 3,
        size: 7,
        font: titleFont,
        color: rgb(0.15, 0.15, 0.15),
      });

      page.drawLine({
        start: { x: startX, y: stringY },
        end: { x: endX, y: stringY },
        thickness: 0.75,
        color: rgb(0, 0, 0),
      });

      drawFretTokens({
        page,
        font: tabFont,
        content: row.content,
        stringY,
        startX: startX + 3,
        endX: endX - 12,
      });
    }

    for (let divider = 0; divider <= measuresPerRow; divider += 1) {
      const x = startX + divider * measureWidth;
      page.drawLine({
        start: { x, y: rowTopY },
        end: { x, y: rowTopY - staffHeight },
        thickness: divider === 0 || divider === measuresPerRow ? 1 : 0.75,
        color: rgb(0, 0, 0),
      });
    }

    page.drawLine({
      start: { x: endX - 3, y: rowTopY },
      end: { x: endX - 3, y: rowTopY - staffHeight },
      thickness: 1,
      color: rgb(0, 0, 0),
    });
  }

  function addWatermark(page) {
    page.drawText('DADROCK TABS PREVIEW', {
      x: 72,
      y: 340,
      size: 38,
      font: titleFont,
      color: rgb(0.7, 0.7, 0.7),
      rotate: degrees(34),
      opacity: 0.3,
    });

    page.drawRectangle({
      x: margin,
      y: 64,
      width: pageWidth - margin * 2,
      height: 70,
      color: rgb(0.98, 0.95, 0.9),
      borderColor: rgb(1, 0.27, 0),
      borderWidth: 1.2,
    });

    page.drawText('PREVIEW ONLY', {
      x: margin + 18,
      y: 108,
      size: 11,
      font: titleFont,
      color: rgb(1, 0.27, 0),
    });

    page.drawText('Unlock the complete unwatermarked tablature PDF below.', {
      x: margin + 18,
      y: 84,
      size: 9,
      font: titleFont,
      color: rgb(0.12, 0.12, 0.12),
    });
  }

  let systemIndex = 0;
  let firstMeasureNumber = 1;

  const firstPage = pdfDoc.addPage([pageWidth, pageHeight]);
  drawFullHeader(firstPage);

  let rowTopY = 555;
  const firstPageCount = Math.min(firstPageRows, systems.length);
  for (let index = 0; index < firstPageCount; index += 1) {
    drawSystem(firstPage, systems[systemIndex], rowTopY, firstMeasureNumber);
    systemIndex += 1;
    firstMeasureNumber += measuresPerRow;
    rowTopY -= rowSpacing;
  }

  if (preview) addWatermark(firstPage);

  while (!preview && systemIndex < systems.length) {
    const page = pdfDoc.addPage([pageWidth, pageHeight]);
    drawCompactHeader(page);
    rowTopY = 690;

    for (
      let row = 0;
      row < continuationRows && systemIndex < systems.length;
      row += 1
    ) {
      drawSystem(page, systems[systemIndex], rowTopY, firstMeasureNumber);
      systemIndex += 1;
      firstMeasureNumber += measuresPerRow;
      rowTopY -= rowSpacing;
    }
  }

  const pages = pdfDoc.getPages();
  pages.forEach((page, index) => {
    const pageNumberText = `Page ${index + 1} of ${pages.length}`;
    const pageNumberSize = 9;
    const pageNumberWidth = bodyFont.widthOfTextAtSize(
      pageNumberText,
      pageNumberSize
    );
    const pageNumberX = (pageWidth - pageNumberWidth) / 2;

    page.drawLine({
      start: { x: margin, y: 27 },
      end: { x: pageNumberX - 14, y: 27 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    page.drawText(pageNumberText, {
      x: pageNumberX,
      y: 24,
      size: pageNumberSize,
      font: bodyFont,
      color: rgb(0.2, 0.2, 0.2),
    });

    page.drawLine({
      start: { x: pageNumberX + pageNumberWidth + 14, y: 27 },
      end: { x: endX, y: 27 },
      thickness: 0.5,
      color: rgb(0.35, 0.35, 0.35),
    });

    const footerBrand = preview
      ? 'DadRock Tabs preview • dadrocktabs.com'
      : 'Generated by DadRock Tabs • dadrocktabs.com';
    const footerWidth = bodyFont.widthOfTextAtSize(footerBrand, 7);
    page.drawText(footerBrand, {
      x: (pageWidth - footerWidth) / 2,
      y: 10,
      size: 7,
      font: bodyFont,
      color: rgb(0.4, 0.4, 0.4),
    });
  });

  return pdfDoc.save();
}
