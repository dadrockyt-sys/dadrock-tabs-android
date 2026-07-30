import fs from 'node:fs/promises';
import path from 'node:path';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

const PAGE = { width: 612, height: 792, left: 50, right: 560, bottom: 42 };
const STRINGS = ['E', 'B', 'G', 'D', 'A', 'E'];
const MEASURES_PER_ROW = 2;

function clean(value, fallback) {
  const text = String(value || fallback).replace(/\s+/g, ' ').trim();
  return text || fallback;
}

function sectionStartMap(sections = []) {
  return new Map(
    sections
      .filter((item) => item && Number(item.startMeasure) > 0)
      .map((item) => [Number(item.startMeasure), clean(item.label, 'Section')])
  );
}

export async function createJimmyPaigeV8Pdf({
  songTitle = 'Song Title',
  artistName = 'Artist Name',
  transcriptionType = 'Rhythm Guitar',
  tuning = 'Standard Tuning',
  bpm = 120,
  timeSignature = '4/4',
  totalMeasures = 1,
  sections = [],
} = {}) {
  const pdfDoc = await PDFDocument.create();
  const bold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const regular = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const logoBytes = await fs.readFile(
    path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png')
  );
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const largeLogo = logoImage.scaleToFit(190, 82);
  const smallLogo = logoImage.scaleToFit(95, 42);

  const safeMeasures = Math.max(1, Number(totalMeasures) || 1);
  const measureWidth = (PAGE.right - PAGE.left) / MEASURES_PER_ROW;
  const stringSpacing = 8;
  const staffHeight = stringSpacing * (STRINGS.length - 1);
  const rowHeight = 82;
  const starts = sectionStartMap(sections);

  function drawHeader(page, compact = false) {
    if (compact) {
      page.drawImage(logoImage, {
        x: PAGE.left,
        y: 731,
        width: smallLogo.width,
        height: smallLogo.height,
      });
      page.drawText(`${clean(songTitle, 'Song Title')} — ${clean(artistName, 'Artist Name')}`, {
        x: PAGE.left + smallLogo.width + 10,
        y: 746,
        size: 11,
        font: bold,
        color: rgb(0.08, 0.08, 0.08),
      });
      page.drawLine({
        start: { x: PAGE.left, y: 716 },
        end: { x: PAGE.right, y: 716 },
        thickness: 0.6,
        color: rgb(0.72, 0.72, 0.72),
      });
      return 690;
    }

    page.drawImage(logoImage, {
      x: (PAGE.width - largeLogo.width) / 2,
      y: 704,
      width: largeLogo.width,
      height: largeLogo.height,
    });
    page.drawText(clean(songTitle, 'Song Title'), {
      x: PAGE.left,
      y: 670,
      size: 20,
      font: bold,
      color: rgb(0.03, 0.03, 0.03),
    });
    page.drawText(clean(artistName, 'Artist Name'), {
      x: PAGE.left,
      y: 649,
      size: 12,
      font: regular,
      color: rgb(0.36, 0.36, 0.36),
    });
    page.drawText(clean(transcriptionType, 'Rhythm Guitar').toUpperCase(), {
      x: PAGE.left,
      y: 625,
      size: 9.5,
      font: bold,
      color: rgb(0.12, 0.12, 0.12),
    });
    const metadata = `${clean(tuning, 'Standard Tuning')} • ${clean(timeSignature, '4/4')} • ${Number(bpm) || 120} BPM`;
    const metadataWidth = regular.widthOfTextAtSize(metadata, 8.5);
    page.drawText(metadata, {
      x: PAGE.right - metadataWidth,
      y: 625,
      size: 8.5,
      font: regular,
      color: rgb(0.2, 0.2, 0.2),
    });
    return 590;
  }

  function drawTimeSignature(page, rowTop) {
    const [top = '4', bottom = '4'] = String(timeSignature).split('/');
    page.drawText(top, {
      x: PAGE.left + 13,
      y: rowTop - 17,
      size: 18,
      font: bold,
      color: rgb(0.08, 0.08, 0.08),
    });
    page.drawText(bottom, {
      x: PAGE.left + 13,
      y: rowTop - 37,
      size: 18,
      font: bold,
      color: rgb(0.08, 0.08, 0.08),
    });
  }

  function drawRow(page, rowTop, firstMeasure) {
    const sectionLabel = starts.get(firstMeasure);
    if (sectionLabel) {
      page.drawText(sectionLabel, {
        x: PAGE.left,
        y: rowTop + 22,
        size: 11,
        font: bold,
        color: rgb(0.1, 0.1, 0.1),
      });
    }

    for (let index = 0; index < MEASURES_PER_ROW; index += 1) {
      const number = firstMeasure + index;
      if (number <= safeMeasures) {
        page.drawText(String(number), {
          x: PAGE.left + index * measureWidth + 4,
          y: rowTop + 8,
          size: 7.5,
          font: regular,
          color: rgb(0.38, 0.38, 0.38),
        });
      }
    }

    STRINGS.forEach((label, index) => {
      const y = rowTop - index * stringSpacing;
      page.drawText(label, {
        x: 35,
        y: y - 3,
        size: 7,
        font: bold,
        color: rgb(0.12, 0.12, 0.12),
      });
      page.drawLine({
        start: { x: PAGE.left, y },
        end: { x: PAGE.right, y },
        thickness: 0.7,
        color: rgb(0.12, 0.12, 0.12),
      });
    });

    for (let divider = 0; divider <= MEASURES_PER_ROW; divider += 1) {
      const x = PAGE.left + divider * measureWidth;
      page.drawLine({
        start: { x, y: rowTop },
        end: { x, y: rowTop - staffHeight },
        thickness: divider === 0 || divider === MEASURES_PER_ROW ? 1.1 : 0.75,
        color: rgb(0.12, 0.12, 0.12),
      });
    }

    if (firstMeasure === 1) drawTimeSignature(page, rowTop);
  }

  let page = pdfDoc.addPage([PAGE.width, PAGE.height]);
  let rowTop = drawHeader(page, false);
  let measure = 1;

  while (measure <= safeMeasures) {
    const needsSectionSpace = starts.has(measure);
    const required = rowHeight + (needsSectionSpace ? 12 : 0);
    if (rowTop - required < PAGE.bottom) {
      page = pdfDoc.addPage([PAGE.width, PAGE.height]);
      rowTop = drawHeader(page, true);
    }
    drawRow(page, rowTop, measure);
    rowTop -= required;
    measure += MEASURES_PER_ROW;
  }

  const pages = pdfDoc.getPages();
  pages.forEach((currentPage, index) => {
    const footer = `Page ${index + 1} of ${pages.length} • Generated by DadRock Tabs • dadrocktabs.com`;
    const size = 7.5;
    const width = regular.widthOfTextAtSize(footer, size);
    currentPage.drawText(footer, {
      x: (PAGE.width - width) / 2,
      y: 18,
      size,
      font: regular,
      color: rgb(0.4, 0.4, 0.4),
    });
  });

  return pdfDoc.save();
}
