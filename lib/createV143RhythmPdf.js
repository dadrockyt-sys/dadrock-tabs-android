import fs from 'node:fs/promises';
import path from 'node:path';
import { PDFDocument, StandardFonts, degrees, rgb } from 'pdf-lib';
import { projectV143RenderEvents } from '@/lib/v143RenderContract';

const PAGE = {
  width: 612,
  height: 792,
  marginX: 50,
  contentRight: 560,
  bottomLimit: 48,
};

const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E'];
const MEASURES_PER_SYSTEM = 4;
const STEPS_PER_MEASURE = 16;
const STRING_SPACING = 8;
const STAFF_HEIGHT = STRING_SPACING * (STRING_LABELS.length - 1);
const SYSTEM_HEIGHT = 78;
const FIRST_PAGE_TOP = 566;
const CONTINUATION_TOP = 704;

function cleanText(value, fallback) {
  const cleaned = String(value || fallback).replace(/\s+/g, ' ').trim();
  return cleaned || fallback;
}

function fitTextSize(font, text, maximumWidth, preferredSize, minimumSize = 8) {
  let size = preferredSize;
  while (size > minimumSize && font.widthOfTextAtSize(text, size) > maximumWidth) {
    size -= 0.5;
  }
  return size;
}

function techniqueSet(event) {
  return new Set(Array.isArray(event?.techniques) ? event.techniques : []);
}

function eventToken(event) {
  const fret = Number(event.fret);
  const techniques = techniqueSet(event);

  if (techniques.has('dead-note') || techniques.has('muted-strum')) return 'x';
  if (techniques.has('natural-harmonic')) return `<${fret}>`;
  if (techniques.has('pinch-harmonic')) return `(${fret})`;

  if (Number(event.bendSemitones) >= 0.35 || techniques.has('bend') || techniques.has('bend-release')) {
    const amount = Math.max(1, Math.round(Number(event.bendSemitones) || 1));
    const target = Number.isFinite(Number(event.bendTargetFret))
      ? Math.round(Number(event.bendTargetFret))
      : fret + amount;
    let token = `${fret}b${target}`;
    if (event.bendRelease === true || techniques.has('bend-release')) token += `r${fret}`;
    if (techniques.has('vibrato')) token += '~';
    return token;
  }

  let token = String(fret);
  if (techniques.has('vibrato')) token += '~';
  return token;
}

function systemForMeasure(measure) {
  return Math.floor((Number(measure) - 1) / MEASURES_PER_SYSTEM);
}

function systemStartMeasure(systemIndex) {
  return systemIndex * MEASURES_PER_SYSTEM + 1;
}

function buildSystems(events) {
  const maximumMeasure = Math.max(1, ...events.map((event) => Number(event.measure) || 1));
  const systemCount = Math.ceil(maximumMeasure / MEASURES_PER_SYSTEM);
  const systems = [];

  for (let systemIndex = 0; systemIndex < systemCount; systemIndex += 1) {
    const firstMeasure = systemStartMeasure(systemIndex);
    const lastMeasure = firstMeasure + MEASURES_PER_SYSTEM - 1;
    systems.push({
      systemIndex,
      firstMeasure,
      lastMeasure,
      events: events.filter((event) => event.measure >= firstMeasure && event.measure <= lastMeasure),
    });
  }

  return systems;
}

function positionForEvent(event, staffTop) {
  const measureWidth = (PAGE.contentRight - PAGE.marginX) / MEASURES_PER_SYSTEM;
  const measureOffset = (Number(event.measure) - 1) % MEASURES_PER_SYSTEM;
  const stepWidth = measureWidth / STEPS_PER_MEASURE;
  const x = PAGE.marginX + measureOffset * measureWidth + (Number(event.step) + 0.5) * stepWidth;
  const y = staffTop - Number(event.stringIndex) * STRING_SPACING;
  return { x, y, stepWidth, measureWidth };
}

function drawTechniqueConnector({ page, font, source, target, staffTop }) {
  if (!source || !target || Number(source.stringIndex) !== Number(target.stringIndex)) return;
  if (systemForMeasure(source.measure) !== systemForMeasure(target.measure)) return;

  const sourcePos = positionForEvent(source, staffTop);
  const targetPos = positionForEvent(target, staffTop);
  if (targetPos.x <= sourcePos.x) return;

  const techniques = techniqueSet(source);
  let symbol = '';
  if (techniques.has('hammer-on')) symbol = 'h';
  else if (techniques.has('pull-off')) symbol = 'p';
  else if (techniques.has('slide-up')) symbol = '/';
  else if (techniques.has('slide-down')) symbol = '\\';
  if (!symbol) return;

  const midpoint = (sourcePos.x + targetPos.x) / 2;
  page.drawText(symbol, {
    x: midpoint - 2,
    y: sourcePos.y + 4.2,
    size: 6.5,
    font,
    color: rgb(0.05, 0.05, 0.05),
  });
}

export async function createV143RhythmPdf({
  song,
  artist,
  generatedTab,
  renderEvents,
  tuning = 'E Standard',
  tempo = 120,
  timeSignature = '4/4',
  keySignature = '',
  preview = false,
  previewSystems = 4,
}) {
  const events = projectV143RenderEvents(renderEvents);
  if (!events.length) {
    throw new Error('V143 structured rendering requires render events.');
  }

  const systems = buildSystems(events);
  const eventByIndex = new Map(events.map((event) => [Number(event.eventIndex), event]));
  const clearPreviewSystems = Math.max(1, Math.min(4, Number(previewSystems) || 4));

  const pdfDoc = await PDFDocument.create();
  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const tabFont = await pdfDoc.embedFont(StandardFonts.CourierBold);

  const logoPath = path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png');
  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const fullLogo = logoImage.scaleToFit(190, 88);
  const compactLogo = logoImage.scaleToFit(72, 34);

  const safeSong = cleanText(song, 'Untitled');
  const safeArtist = cleanText(artist, 'Unknown Artist');
  const metadata = [
    cleanText(tuning, 'E Standard'),
    cleanText(timeSignature, '4/4'),
    `${Number(tempo) || 120} BPM`,
  ];
  if (keySignature) metadata.push(cleanText(keySignature, ''));
  const settingsText = metadata.filter(Boolean).join(' • ');

  function drawHeader(page, compact = false) {
    if (compact) {
      page.drawImage(logoImage, {
        x: PAGE.marginX,
        y: 731,
        width: compactLogo.width,
        height: compactLogo.height,
      });
      const title = `${safeSong} — ${safeArtist}`;
      const titleX = PAGE.marginX + compactLogo.width + 9;
      page.drawText(title, {
        x: titleX,
        y: 747,
        size: fitTextSize(titleFont, title, 325, 11.5, 8.5),
        font: titleFont,
        color: rgb(0.08, 0.08, 0.08),
      });
      page.drawText(settingsText, {
        x: PAGE.contentRight - bodyFont.widthOfTextAtSize(settingsText, 7),
        y: 731,
        size: 7,
        font: bodyFont,
        color: rgb(0.25, 0.25, 0.25),
      });
      page.drawLine({
        start: { x: PAGE.marginX, y: 718 },
        end: { x: PAGE.contentRight, y: 718 },
        thickness: 0.6,
        color: rgb(0.74, 0.74, 0.74),
      });
      return;
    }

    page.drawImage(logoImage, {
      x: (PAGE.width - fullLogo.width) / 2,
      y: 700,
      width: fullLogo.width,
      height: fullLogo.height,
    });
    const product = 'DIY Guitar & Bass TAB Generator';
    page.drawText(product, {
      x: (PAGE.width - titleFont.widthOfTextAtSize(product, 16)) / 2,
      y: 678,
      size: 16,
      font: titleFont,
      color: rgb(1, 0.27, 0),
    });
    const powered = 'Powered by DadRock AI • V143 Rhythm';
    page.drawText(powered, {
      x: (PAGE.width - bodyFont.widthOfTextAtSize(powered, 8.5)) / 2,
      y: 663,
      size: 8.5,
      font: bodyFont,
      color: rgb(0.42, 0.42, 0.42),
    });
    page.drawText(safeSong, {
      x: PAGE.marginX,
      y: 635,
      size: fitTextSize(titleFont, safeSong, 500, 20, 14),
      font: titleFont,
      color: rgb(0.03, 0.03, 0.03),
    });
    page.drawText(safeArtist, {
      x: PAGE.marginX,
      y: 613,
      size: fitTextSize(bodyFont, safeArtist, 360, 13, 9.5),
      font: bodyFont,
      color: rgb(0.38, 0.38, 0.38),
    });
    page.drawText('RHYTHM', {
      x: PAGE.marginX,
      y: 592,
      size: 10,
      font: titleFont,
      color: rgb(0.12, 0.12, 0.12),
    });
    const settingsSize = fitTextSize(bodyFont, settingsText, 330, 9, 6.8);
    page.drawText(settingsText, {
      x: PAGE.contentRight - bodyFont.widthOfTextAtSize(settingsText, settingsSize),
      y: 592,
      size: settingsSize,
      font: bodyFont,
      color: rgb(0.2, 0.2, 0.2),
    });
  }

  function drawSystem(page, system, topY, locked = false) {
    const staffTop = topY - 15;
    const measureWidth = (PAGE.contentRight - PAGE.marginX) / MEASURES_PER_SYSTEM;

    for (let offset = 0; offset < MEASURES_PER_SYSTEM; offset += 1) {
      const measure = system.firstMeasure + offset;
      page.drawText(String(measure), {
        x: PAGE.marginX + offset * measureWidth + 3,
        y: staffTop + 9,
        size: 6.6,
        font: bodyFont,
        color: rgb(0.38, 0.38, 0.38),
      });
    }

    for (let stringIndex = 0; stringIndex < STRING_LABELS.length; stringIndex += 1) {
      const stringY = staffTop - stringIndex * STRING_SPACING;
      page.drawText(STRING_LABELS[stringIndex], {
        x: 36,
        y: stringY - 3,
        size: 7,
        font: titleFont,
        color: rgb(0.12, 0.12, 0.12),
      });
      page.drawLine({
        start: { x: PAGE.marginX, y: stringY },
        end: { x: PAGE.contentRight, y: stringY },
        thickness: 0.7,
        color: rgb(0.16, 0.16, 0.16),
      });
    }

    for (let divider = 0; divider <= MEASURES_PER_SYSTEM; divider += 1) {
      const x = PAGE.marginX + divider * measureWidth;
      page.drawLine({
        start: { x, y: staffTop },
        end: { x, y: staffTop - STAFF_HEIGHT },
        thickness: divider === 0 || divider === MEASURES_PER_SYSTEM ? 1 : 0.7,
        color: rgb(0.12, 0.12, 0.12),
      });
    }

    if (locked) {
      page.drawRectangle({
        x: PAGE.marginX + 1,
        y: staffTop - STAFF_HEIGHT - 2,
        width: PAGE.contentRight - PAGE.marginX - 2,
        height: STAFF_HEIGHT + 15,
        color: rgb(1, 1, 1),
        opacity: 1,
      });
      page.drawText('LOCKED — unlock the full PDF to view these measures', {
        x: PAGE.marginX + 90,
        y: staffTop - 19,
        size: 8,
        font: titleFont,
        color: rgb(0.48, 0.48, 0.48),
      });
      return;
    }

    for (const event of system.events) {
      const { x, y, stepWidth } = positionForEvent(event, staffTop);
      const token = eventToken(event);
      const size = token.length > 6 ? 6.2 : token.length > 4 ? 6.8 : 7.6;
      const width = tabFont.widthOfTextAtSize(token, size);
      page.drawRectangle({
        x: x - 1.4,
        y: y - 4.7,
        width: width + 2.8,
        height: 10.2,
        color: rgb(1, 1, 1),
      });
      page.drawText(token, {
        x,
        y: y - 3.1,
        size,
        font: tabFont,
        color: rgb(0.03, 0.03, 0.03),
      });

      if (Number(event.durationSteps) > 1) {
        const sustainEnd = Math.min(
          PAGE.contentRight - 3,
          x + Math.min(Number(event.durationSteps), 16) * stepWidth
        );
        if (sustainEnd > x + width + 3) {
          page.drawLine({
            start: { x: x + width + 2, y: y + 0.5 },
            end: { x: sustainEnd, y: y + 0.5 },
            thickness: 0.45,
            color: rgb(0.4, 0.4, 0.4),
          });
        }
      }

      const techniques = techniqueSet(event);
      if (techniques.has('palm-mute')) {
        page.drawText('P.M.', { x, y: staffTop + 19, size: 5.8, font: titleFont, color: rgb(0.18, 0.18, 0.18) });
      } else if (techniques.has('let-ring')) {
        page.drawText('let ring', { x, y: staffTop + 19, size: 5.5, font: bodyFont, color: rgb(0.18, 0.18, 0.18) });
      } else if (techniques.has('tap')) {
        page.drawText('T', { x, y: staffTop + 19, size: 6, font: titleFont, color: rgb(0.18, 0.18, 0.18) });
      }
    }

    for (const source of system.events) {
      const targetIndex = Number(source.legatoTargetEventIndex);
      if (!Number.isInteger(targetIndex)) continue;
      drawTechniqueConnector({
        page,
        font: tabFont,
        source,
        target: eventByIndex.get(targetIndex),
        staffTop,
      });
    }
  }

  let page = pdfDoc.addPage([PAGE.width, PAGE.height]);
  drawHeader(page, false);
  let currentY = FIRST_PAGE_TOP;

  systems.forEach((system, index) => {
    if (currentY - SYSTEM_HEIGHT < PAGE.bottomLimit) {
      page = pdfDoc.addPage([PAGE.width, PAGE.height]);
      drawHeader(page, true);
      currentY = CONTINUATION_TOP;
    }

    drawSystem(page, system, currentY, preview && index >= clearPreviewSystems);
    currentY -= SYSTEM_HEIGHT;
  });

  const pages = pdfDoc.getPages();
  pages.forEach((pdfPage, pageIndex) => {
    if (preview) {
      pdfPage.drawText('DADROCK TABS PREVIEW', {
        x: 76,
        y: pageIndex === 0 ? 255 : 315,
        size: 38,
        font: titleFont,
        color: rgb(0.66, 0.66, 0.66),
        rotate: degrees(34),
        opacity: 0.17,
      });
      pdfPage.drawRectangle({
        x: PAGE.marginX,
        y: 36,
        width: PAGE.contentRight - PAGE.marginX,
        height: 104,
        color: rgb(0.98, 0.95, 0.9),
        borderColor: rgb(1, 0.27, 0),
        borderWidth: 1.1,
        opacity: 0.98,
      });
      pdfPage.drawText('FULL TAB LOCKED', {
        x: PAGE.marginX + 18,
        y: 120,
        size: 11,
        font: titleFont,
        color: rgb(1, 0.27, 0),
      });
      pdfPage.drawText('Unlock your complete V143 rhythm transcription PDF', {
        x: PAGE.marginX + 18,
        y: 102,
        size: 8.4,
        font: titleFont,
        color: rgb(0.12, 0.12, 0.12),
      });
      pdfPage.drawText('• Full note placement  • bends/releases  • legato  • sustain', {
        x: PAGE.marginX + 18,
        y: 84,
        size: 7.6,
        font: bodyFont,
        color: rgb(0.18, 0.18, 0.18),
      });
    }

    const pageText = `Page ${pageIndex + 1} of ${pages.length}`;
    const pageSize = 8;
    pdfPage.drawText(pageText, {
      x: (PAGE.width - bodyFont.widthOfTextAtSize(pageText, pageSize)) / 2,
      y: 24,
      size: pageSize,
      font: bodyFont,
      color: rgb(0.28, 0.28, 0.28),
    });
    const footer = 'Generated by DadRock Tabs Studio • dadrocktabs.com';
    pdfPage.drawText(footer, {
      x: (PAGE.width - bodyFont.widthOfTextAtSize(footer, 6.8)) / 2,
      y: 9,
      size: 6.8,
      font: bodyFont,
      color: rgb(0.42, 0.42, 0.42),
    });
  });

  return pdfDoc.save();
}
