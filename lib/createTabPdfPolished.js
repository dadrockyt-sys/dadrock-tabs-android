import fs from 'node:fs/promises';
import path from 'node:path';
import {
  PDFDocument,
  StandardFonts,
  degrees,
  rgb,
} from 'pdf-lib';
import { createTabPdf as createBaseTabPdf } from '@/lib/createTabPdf';

const PAGE = {
  width: 612,
  height: 792,
  marginX: 50,
  contentRight: 560,
};

const SECTION_PATTERN = /^(INTRO|VERSE(?:\s+\d+)?|PRE-CHORUS|CHORUS(?:\s+\d+)?|BRIDGE|SOLO|OUTRO|BREAKDOWN|INTERLUDE|RIFF|ENDING)\b/i;
const STRING_LINE_PATTERN = /^\s*([eEADGB])\s*\|?(.*)$/;
const MEASURES_PER_SYSTEM = 6;

function cleanText(value, fallback) {
  const cleaned = String(value || fallback)
    .replace(/\s+/g, ' ')
    .trim();

  return cleaned || fallback;
}

function fitTextSize(font, text, maximumWidth, preferredSize, minimumSize = 8) {
  let size = preferredSize;

  while (
    size > minimumSize &&
    font.widthOfTextAtSize(text, size) > maximumWidth
  ) {
    size -= 0.5;
  }

  return size;
}

function drawCenteredText(page, text, y, size, font, color) {
  const width = font.widthOfTextAtSize(text, size);

  page.drawText(text, {
    x: (PAGE.width - width) / 2,
    y,
    size,
    font,
    color,
  });
}

function parseSystemSections(generatedTab, transcriptionType) {
  const expectedRows = transcriptionType === 'bass' ? 4 : 6;
  const systems = [];
  let pendingSection = false;
  let currentRows = 0;

  for (const rawLine of String(generatedTab || '').split(/\r?\n/)) {
    const line = rawLine.trimEnd();
    const trimmed = line.trim();

    if (SECTION_PATTERN.test(trimmed)) {
      if (currentRows === expectedRows) {
        systems.push(pendingSection);
      }
      currentRows = 0;
      pendingSection = !/^RIFF(?:\s+\d+)?$/i.test(
        trimmed.replace(/[:\-]+$/, '')
      );
      continue;
    }

    if (!STRING_LINE_PATTERN.test(line)) {
      if (currentRows === expectedRows) {
        systems.push(pendingSection);
      }
      currentRows = 0;
      pendingSection = false;
      continue;
    }

    currentRows += 1;

    if (currentRows === expectedRows) {
      systems.push(pendingSection);
      currentRows = 0;
      pendingSection = false;
    }
  }

  if (currentRows === expectedRows) {
    systems.push(pendingSection);
  }

  return systems.length ? systems : [false];
}

function redrawMeasureNumbers({
  pages,
  generatedTab,
  transcriptionType,
  bodyFont,
}) {
  const sections = parseSystemSections(generatedTab, transcriptionType);
  const baseSystemHeight = transcriptionType === 'bass' ? 60 : 59;
  const firstPageTop = 566;
  const continuationTop = 704;
  const bottomLimit = 44;
  const measureWidth =
    (PAGE.contentRight - PAGE.marginX) / MEASURES_PER_SYSTEM;

  let pageIndex = 0;
  let currentY = firstPageTop;
  let firstMeasureNumber = 1;

  for (const hasSection of sections) {
    const sectionOffset = hasSection ? 14 : 0;
    const requiredHeight = baseSystemHeight + sectionOffset;

    if (currentY - requiredHeight < bottomLimit) {
      pageIndex += 1;
      currentY = continuationTop;
    }

    const page = pages[pageIndex];
    if (!page) break;

    const staffTop = currentY - sectionOffset;

    // Remove the original measure numbers, which were drawn too high.
    page.drawRectangle({
      x: PAGE.marginX - 1,
      y: staffTop + 7,
      width: PAGE.contentRight - PAGE.marginX + 2,
      height: 16,
      color: rgb(1, 1, 1),
    });

    // Place compact numbers immediately above the top TAB string.
    for (
      let measureIndex = 0;
      measureIndex < MEASURES_PER_SYSTEM;
      measureIndex += 1
    ) {
      page.drawText(String(firstMeasureNumber + measureIndex), {
        x: PAGE.marginX + measureIndex * measureWidth + 3,
        y: staffTop + 3.5,
        size: 6.4,
        font: bodyFont,
        color: rgb(0.38, 0.38, 0.38),
      });
    }

    currentY -= requiredHeight;
    firstMeasureNumber += MEASURES_PER_SYSTEM;
  }
}

export async function createTabPdf(options) {
  const baseBytes = await createBaseTabPdf(options);
  const pdfDoc = await PDFDocument.load(baseBytes);
  const pages = pdfDoc.getPages();

  if (!pages.length) {
    return baseBytes;
  }

  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);

  const logoPath = path.join(
    process.cwd(),
    'public',
    'DadRock-Tabs-Logo.png'
  );
  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const logo = logoImage.scaleToFit(190, 88);
  const logoTop = 780;
  const logoY = logoTop - logo.height;

  const song = cleanText(options?.song, 'Untitled');
  const artist = cleanText(options?.artist, 'Unknown Artist');
  const instrument = cleanText(
    options?.transcriptionType,
    'lead'
  ).toUpperCase();

  const metadata = [
    cleanText(options?.tuning, 'Standard Tuning'),
    cleanText(options?.timeSignature, '4/4'),
    `${Number(options?.tempo) || 120} BPM`,
  ];

  if (options?.keySignature) {
    metadata.push(cleanText(options.keySignature, ''));
  }

  const settingsText = metadata.filter(Boolean).join(' • ');
  const firstPage = pages[0];

  // Rebuild the first-page header with safely bounded DadRock branding.
  firstPage.drawRectangle({
    x: 0,
    y: 584,
    width: PAGE.width,
    height: PAGE.height - 584,
    color: rgb(1, 1, 1),
  });

  firstPage.drawImage(logoImage, {
    x: (PAGE.width - logo.width) / 2,
    y: logoY,
    width: logo.width,
    height: logo.height,
  });

  drawCenteredText(
    firstPage,
    'DIY Guitar & Bass TAB Generator',
    678,
    16,
    titleFont,
    rgb(1, 0.27, 0)
  );

  drawCenteredText(
    firstPage,
    'Powered by DadRock AI',
    663,
    8.5,
    bodyFont,
    rgb(0.42, 0.42, 0.42)
  );

  const songSize = fitTextSize(titleFont, song, 500, 20, 14);
  firstPage.drawText(song, {
    x: PAGE.marginX,
    y: 635,
    size: songSize,
    font: titleFont,
    color: rgb(0.03, 0.03, 0.03),
  });

  const artistSize = fitTextSize(bodyFont, artist, 360, 13, 9.5);
  firstPage.drawText(artist, {
    x: PAGE.marginX,
    y: 613,
    size: artistSize,
    font: bodyFont,
    color: rgb(0.38, 0.38, 0.38),
  });

  firstPage.drawLine({
    start: { x: PAGE.marginX, y: 602 },
    end: { x: 190, y: 602 },
    thickness: 0.8,
    color: rgb(0.82, 0.82, 0.82),
  });

  firstPage.drawText(instrument, {
    x: PAGE.marginX,
    y: 592,
    size: 10,
    font: titleFont,
    color: rgb(0.12, 0.12, 0.12),
  });

  const settingsSize = fitTextSize(
    bodyFont,
    settingsText,
    330,
    9,
    6.8
  );
  const settingsWidth = bodyFont.widthOfTextAtSize(
    settingsText,
    settingsSize
  );

  firstPage.drawText(settingsText, {
    x: PAGE.contentRight - settingsWidth,
    y: 592,
    size: settingsSize,
    font: bodyFont,
    color: rgb(0.2, 0.2, 0.2),
  });

  // The polished header previously covered measures 1–6. Redraw all measure
  // numbers after the header overlay and keep them close to each TAB staff.
  redrawMeasureNumbers({
    pages,
    generatedTab: options?.generatedTab,
    transcriptionType: options?.transcriptionType,
    bodyFont,
  });

  pages.forEach((page, index) => {
    // Replace the previous footer on both preview and unlocked PDFs.
    page.drawRectangle({
      x: 0,
      y: 0,
      width: PAGE.width,
      height: 19,
      color: rgb(1, 1, 1),
    });

    const footer = 'Generated by DadRock Tabs Studio • dadrocktabs.com';
    const footerSize = 7;
    const footerWidth = bodyFont.widthOfTextAtSize(
      footer,
      footerSize
    );

    page.drawText(footer, {
      x: (PAGE.width - footerWidth) / 2,
      y: 9,
      size: footerSize,
      font: bodyFont,
      color: rgb(0.42, 0.42, 0.42),
    });

    if (!options?.preview) {
      return;
    }

    // Strengthen the preview watermark without blocking the visible tab.
    page.drawText('DADROCK TABS PREVIEW', {
      x: 76,
      y: index === 0 ? 255 : 315,
      size: 38,
      font: titleFont,
      color: rgb(0.66, 0.66, 0.66),
      rotate: degrees(34),
      opacity: 0.17,
    });

    // Replace the original notice with a larger value-focused lock box.
    page.drawRectangle({
      x: PAGE.marginX - 2,
      y: 33,
      width: PAGE.contentRight - PAGE.marginX + 4,
      height: 111,
      color: rgb(1, 1, 1),
    });

    page.drawRectangle({
      x: PAGE.marginX,
      y: 36,
      width: PAGE.contentRight - PAGE.marginX,
      height: 104,
      color: rgb(0.98, 0.95, 0.9),
      borderColor: rgb(1, 0.27, 0),
      borderWidth: 1.1,
      opacity: 0.98,
    });

    page.drawText('FULL TAB LOCKED', {
      x: PAGE.marginX + 18,
      y: 120,
      size: 11,
      font: titleFont,
      color: rgb(1, 0.27, 0),
    });

    page.drawText('Unlock your professional tablature PDF', {
      x: PAGE.marginX + 18,
      y: 103,
      size: 8.8,
      font: titleFont,
      color: rgb(0.12, 0.12, 0.12),
    });

    const benefits = [
      '• Complete transcription',
      '• Print-ready PDF formatting',
      '• Instant download after purchase',
      '• Your purchased PDF is yours to keep',
    ];

    benefits.forEach((benefit, benefitIndex) => {
      page.drawText(benefit, {
        x: PAGE.marginX + 18,
        y: 87 - benefitIndex * 11,
        size: 8,
        font: bodyFont,
        color: rgb(0.18, 0.18, 0.18),
      });
    });

    page.drawText('Continue below to unlock.', {
      x: PAGE.marginX + 18,
      y: 42,
      size: 7.5,
      font: titleFont,
      color: rgb(0.32, 0.32, 0.32),
    });
  });

  return pdfDoc.save();
}
