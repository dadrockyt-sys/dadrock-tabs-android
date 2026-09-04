import fs from 'node:fs/promises';
import path from 'node:path';
import { PDFDocument, StandardFonts, degrees, rgb } from 'pdf-lib';
import {
  buildReferenceFreeRhythmSections,
  summarizeV143RhythmPresentation,
  validateV143RenderEvents,
} from './v143RenderContract.js';

const PAGE = {
  width: 612,
  height: 792,
  marginX: 50,
  staffLeft: 60,
  contentRight: 562,
  bottomLimit: 46,
};

const MEASURES_PER_SYSTEM = 3;
const STEPS_PER_MEASURE = 16;
const STRING_SPACING = 7.4;
const STRING_COUNT = 6;
const STAFF_HEIGHT = STRING_SPACING * (STRING_COUNT - 1);
const SYSTEM_HEIGHT = 88;
const FIRST_PAGE_TOP = 648;
const CONTINUATION_TOP = 710;
const ACCENT = rgb(0.94, 0.24, 0.06);
const INK = rgb(0.055, 0.055, 0.06);
const MID_INK = rgb(0.28, 0.28, 0.3);
const LIGHT_INK = rgb(0.55, 0.55, 0.57);
const HAIRLINE = rgb(0.74, 0.74, 0.76);

function cleanText(value, fallback) {
  const cleaned = String(value || fallback).replace(/\s+/g, ' ').trim();
  return cleaned || fallback;
}

function formatTempo(value) {
  const numeric = Number(value);
  const safe = Number.isFinite(numeric) && numeric > 0 ? numeric : 120;
  const rounded = Math.round(safe * 10) / 10;
  return `${Number.isInteger(rounded) ? rounded.toFixed(0) : rounded.toFixed(1)} BPM`;
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

function fretToken(event) {
  const fret = Math.round(Number(event.fret));
  const techniques = techniqueSet(event);
  if (techniques.has('dead-note') || techniques.has('muted-strum')) return 'x';
  if (techniques.has('natural-harmonic')) return `<${fret}>`;
  if (techniques.has('pinch-harmonic')) return `(${fret})`;
  return String(fret);
}

function systemStartMeasure(systemIndex) {
  return systemIndex * MEASURES_PER_SYSTEM + 1;
}

function buildSystems(events) {
  const maximumMeasure = Math.max(1, ...events.map((event) => Number(event.measure) || 1));
  const systemCount = Math.ceil(maximumMeasure / MEASURES_PER_SYSTEM);
  return Array.from({ length: systemCount }, (_, systemIndex) => {
    const firstMeasure = systemStartMeasure(systemIndex);
    const lastMeasure = Math.min(maximumMeasure, firstMeasure + MEASURES_PER_SYSTEM - 1);
    return {
      systemIndex,
      firstMeasure,
      lastMeasure,
      measureCount: lastMeasure - firstMeasure + 1,
      events: events.filter((event) => event.measure >= firstMeasure && event.measure <= lastMeasure),
    };
  });
}

function measureWidth() {
  return (PAGE.contentRight - PAGE.staffLeft) / MEASURES_PER_SYSTEM;
}

function positionForEvent(event, staffTop, system) {
  const width = measureWidth();
  const measureOffset = Number(event.measure) - Number(system.firstMeasure);
  const stepWidth = width / STEPS_PER_MEASURE;
  const x = PAGE.staffLeft + measureOffset * width + (Number(event.step) + 0.5) * stepWidth;
  const y = staffTop - Number(event.stringIndex) * STRING_SPACING;
  return { x, y, stepWidth, measureWidth: width };
}

function absoluteSystemStep(event, system) {
  return (Number(event.measure) - Number(system.firstMeasure)) * STEPS_PER_MEASURE + Number(event.step);
}

function positionForAbsoluteStep(step, system) {
  const width = measureWidth();
  const total = Math.max(1, Number(system.measureCount) * STEPS_PER_MEASURE);
  const clamped = Math.max(0, Math.min(total, Number(step)));
  return PAGE.staffLeft + (clamped / STEPS_PER_MEASURE) * width;
}

function drawDashedLine(page, x1, y1, x2, y2, thickness = 0.45, color = MID_INK) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy);
  if (length <= 0.5) return;
  const dash = 3;
  const gap = 2.2;
  const ux = dx / length;
  const uy = dy / length;
  for (let offset = 0; offset < length; offset += dash + gap) {
    const end = Math.min(length, offset + dash);
    page.drawLine({
      start: { x: x1 + ux * offset, y: y1 + uy * offset },
      end: { x: x1 + ux * end, y: y1 + uy * end },
      thickness,
      color,
    });
  }
}

function drawArrowHead(page, x, y, angle, size = 3.2, color = INK) {
  const spread = 0.6;
  page.drawLine({
    start: { x, y },
    end: { x: x - Math.cos(angle - spread) * size, y: y - Math.sin(angle - spread) * size },
    thickness: 0.65,
    color,
  });
  page.drawLine({
    start: { x, y },
    end: { x: x - Math.cos(angle + spread) * size, y: y - Math.sin(angle + spread) * size },
    thickness: 0.65,
    color,
  });
}

function bendAmountLabel(event) {
  const amount = Number(event.bendSemitones);
  if (!Number.isFinite(amount) || amount < 0.35) return '';
  if (Math.abs(amount - 0.5) < 0.2) return '1/2';
  if (Math.abs(amount - 1) < 0.2) return 'full';
  if (Math.abs(amount - 1.5) < 0.2) return '1 1/2';
  if (Math.abs(amount - 2) < 0.2) return '2';
  return `${Math.round(amount * 10) / 10}`;
}

function drawVibrato(page, startX, y, endX) {
  const limit = Math.max(startX, endX);
  let x = startX;
  let up = true;
  while (x + 2.4 <= limit) {
    page.drawLine({
      start: { x, y: y + (up ? -0.8 : 0.8) },
      end: { x: x + 2.4, y: y + (up ? 0.8 : -0.8) },
      thickness: 0.55,
      color: MID_INK,
    });
    x += 2.4;
    up = !up;
  }
}

function onsetGroups(system) {
  const map = new Map();
  for (const event of system.events) {
    const key = `${event.measure}:${event.step}`;
    if (!map.has(key)) {
      map.set(key, {
        key,
        measure: Number(event.measure),
        step: Number(event.step),
        events: [],
      });
    }
    map.get(key).events.push(event);
  }
  return [...map.values()]
    .map((group) => ({
      ...group,
      durationSteps: Math.max(1, ...group.events.map((event) => Number(event.durationSteps) || 1)),
      topStringIndex: Math.min(...group.events.map((event) => Number(event.stringIndex))),
    }))
    .sort((a, b) => a.measure - b.measure || a.step - b.step);
}

function drawIndividualRhythmStem(page, group, staffTop, system, beamed = false) {
  const representative = group.events[0];
  const { x } = positionForEvent(representative, staffTop, system);
  const topY = staffTop - group.topStringIndex * STRING_SPACING;
  const stemX = x + 3.4;
  const stemTop = staffTop + 12.5;
  const duration = Number(group.durationSteps) || 1;
  if (duration >= 8 || beamed) return;

  page.drawLine({
    start: { x: stemX, y: topY + 3.2 },
    end: { x: stemX, y: stemTop },
    thickness: 0.65,
    color: INK,
  });

  const flags = duration <= 1 ? 2 : duration <= 3 ? 1 : 0;
  for (let flag = 0; flag < flags; flag += 1) {
    const flagY = stemTop - flag * 3.3;
    page.drawLine({
      start: { x: stemX, y: flagY },
      end: { x: stemX + 4.4, y: flagY - 2.8 },
      thickness: 0.8,
      color: INK,
    });
  }

  if (duration === 3 || duration === 6) {
    page.drawEllipse({
      x: stemX + 5.5,
      y: stemTop - 0.5,
      xScale: 0.8,
      yScale: 0.8,
      color: INK,
    });
  }
}

function drawRhythmLane(page, system, staffTop) {
  const groups = onsetGroups(system);
  const beamed = new Set();
  for (let measure = system.firstMeasure; measure <= system.lastMeasure; measure += 1) {
    for (let beat = 0; beat < 4; beat += 1) {
      const candidates = groups.filter(
        (group) =>
          group.measure === measure &&
          Math.floor(group.step / 4) === beat &&
          Number(group.durationSteps) <= 2
      );
      if (candidates.length < 2) continue;

      const beamY = staffTop + 12.5;
      const stemPoints = candidates.map((group) => {
        const { x } = positionForEvent(group.events[0], staffTop, system);
        const topY = staffTop - group.topStringIndex * STRING_SPACING;
        const stemX = x + 3.4;
        page.drawLine({
          start: { x: stemX, y: topY + 3.2 },
          end: { x: stemX, y: beamY },
          thickness: 0.65,
          color: INK,
        });
        beamed.add(group.key);
        return { group, x: stemX };
      });

      page.drawLine({
        start: { x: stemPoints[0].x, y: beamY },
        end: { x: stemPoints[stemPoints.length - 1].x, y: beamY },
        thickness: 1.35,
        color: INK,
      });

      for (let index = 0; index < stemPoints.length; index += 1) {
        const current = stemPoints[index];
        if (Number(current.group.durationSteps) > 1) continue;
        const next = stemPoints[index + 1];
        if (next && Number(next.group.durationSteps) <= 1) {
          page.drawLine({
            start: { x: current.x, y: beamY - 3.2 },
            end: { x: next.x, y: beamY - 3.2 },
            thickness: 1.1,
            color: INK,
          });
        } else {
          page.drawLine({
            start: { x: current.x, y: beamY - 3.2 },
            end: { x: current.x + 4.2, y: beamY - 3.2 },
            thickness: 1.1,
            color: INK,
          });
        }
      }
    }
  }

  for (const group of groups) {
    drawIndividualRhythmStem(page, group, staffTop, system, beamed.has(group.key));
  }
}

function techniqueRanges(system, technique) {
  const matching = onsetGroups(system).filter((group) =>
    group.events.some((event) => techniqueSet(event).has(technique))
  );
  if (!matching.length) return [];
  const ranges = [];
  let current = [matching[0]];
  for (let index = 1; index < matching.length; index += 1) {
    const previous = matching[index - 1];
    const next = matching[index];
    const gap = absoluteSystemStep(next, system) - absoluteSystemStep(previous, system);
    if (gap <= 3) current.push(next);
    else {
      ranges.push(current);
      current = [next];
    }
  }
  ranges.push(current);
  return ranges;
}

function drawTechniqueRanges(page, system, staffTop, bodyFont, titleFont) {
  const specs = [
    { technique: 'palm-mute', label: 'P.M.', lane: 19.5, font: titleFont },
    { technique: 'let-ring', label: 'let ring', lane: 24.2, font: bodyFont },
  ];
  for (const spec of specs) {
    for (const range of techniqueRanges(system, spec.technique)) {
      const start = positionForEvent(range[0].events[0], staffTop, system).x;
      const endGroup = range[range.length - 1];
      const end = positionForEvent(endGroup.events[0], staffTop, system).x + 7;
      const y = staffTop + spec.lane;
      const labelSize = spec.label.length > 4 ? 4.7 : 5.2;
      page.drawText(spec.label, {
        x: start - 2,
        y,
        size: labelSize,
        font: spec.font,
        color: MID_INK,
      });
      const labelWidth = spec.font.widthOfTextAtSize(spec.label, labelSize);
      drawDashedLine(page, start + labelWidth + 1.5, y + 1.2, end, y + 1.2, 0.4, MID_INK);
      page.drawLine({
        start: { x: end, y: y - 0.8 },
        end: { x: end, y: y + 3.2 },
        thickness: 0.45,
        color: MID_INK,
      });
    }
  }
}

function drawRehearsalMarks(page, system, staffTop, sections, titleFont, bodyFont) {
  for (const section of sections) {
    const startMeasure = Number(section.startMeasure);
    if (startMeasure < system.firstMeasure || startMeasure > system.lastMeasure) continue;
    const offset = startMeasure - system.firstMeasure;
    const x = PAGE.staffLeft + offset * measureWidth();
    const raw = String(section.label || 'SECTION').replace(/^SECTION\s+/i, '').trim() || 'A';
    page.drawRectangle({
      x,
      y: staffTop + 27.2,
      width: 15,
      height: 13,
      color: ACCENT,
    });
    page.drawText(raw.slice(0, 2), {
      x: x + 4.2,
      y: staffTop + 30.2,
      size: 7,
      font: titleFont,
      color: rgb(1, 1, 1),
    });
    const rangeText = `m. ${section.startMeasure}-${section.endMeasure}`;
    page.drawText(rangeText, {
      x: x + 20,
      y: staffTop + 30,
      size: 5.5,
      font: bodyFont,
      color: LIGHT_INK,
    });
  }
}

function drawTimeSignature(page, staffTop, timeSignature, titleFont) {
  const match = String(timeSignature || '4/4').match(/^(\d+)\s*\/\s*(\d+)$/);
  if (!match) return;
  const x = PAGE.staffLeft - 14;
  page.drawText(match[1], {
    x,
    y: staffTop - 13,
    size: 7.3,
    font: titleFont,
    color: INK,
  });
  page.drawText(match[2], {
    x,
    y: staffTop - 28,
    size: 7.3,
    font: titleFont,
    color: INK,
  });
}

function drawTabMark(page, staffTop, titleFont) {
  const x = 36;
  page.drawText('T', { x, y: staffTop - 8.5, size: 7.2, font: titleFont, color: INK });
  page.drawText('A', { x, y: staffTop - 19.2, size: 7.2, font: titleFont, color: INK });
  page.drawText('B', { x, y: staffTop - 29.9, size: 7.2, font: titleFont, color: INK });
}

function drawBend(page, event, staffTop, system, bodyFont) {
  const techniques = techniqueSet(event);
  const hasBend = Number(event.bendSemitones) >= 0.35 || techniques.has('bend') || techniques.has('bend-release') || techniques.has('pre-bend');
  if (!hasBend) return;
  const { x, y } = positionForEvent(event, staffTop, system);
  const start = { x: x + 3.5, y: y + 4 };
  const end = { x: x + 10.5, y: Math.min(staffTop + 9.5, y + 16) };
  page.drawLine({ start, end, thickness: 0.65, color: INK });
  drawArrowHead(page, end.x, end.y, Math.atan2(end.y - start.y, end.x - start.x), 3.2, INK);
  const label = bendAmountLabel(event);
  if (label) {
    page.drawText(label, {
      x: end.x + 1.8,
      y: end.y - 0.2,
      size: 4.5,
      font: bodyFont,
      color: MID_INK,
    });
  }
  if (techniques.has('pre-bend')) {
    page.drawText('pre', {
      x: x - 5,
      y: y + 7,
      size: 4.2,
      font: bodyFont,
      color: MID_INK,
    });
  }
  if (event.bendRelease === true || techniques.has('bend-release')) {
    const releaseEnd = { x: end.x + 7.2, y: start.y + 0.6 };
    page.drawLine({ start: end, end: releaseEnd, thickness: 0.55, color: INK });
    drawArrowHead(page, releaseEnd.x, releaseEnd.y, Math.atan2(releaseEnd.y - end.y, releaseEnd.x - end.x), 2.8, INK);
  }
}

function connectorType(event) {
  const techniques = techniqueSet(event);
  if (techniques.has('hammer-on')) return 'h';
  if (techniques.has('pull-off')) return 'p';
  if (techniques.has('slide-up')) return 'slide';
  if (techniques.has('slide-down')) return 'slide';
  return '';
}

function drawTechniqueConnector({ page, bodyFont, source, target, staffTop, system }) {
  const type = connectorType(source);
  if (!type || !target) return false;
  if (Number(source.stringIndex) !== Number(target.stringIndex)) return false;
  if (target.measure < system.firstMeasure || target.measure > system.lastMeasure) return false;
  const sourcePos = positionForEvent(source, staffTop, system);
  const targetPos = positionForEvent(target, staffTop, system);
  if (targetPos.x <= sourcePos.x + 2) return false;

  const y = sourcePos.y;
  if (type === 'slide') {
    const up = Number(target.fret) >= Number(source.fret);
    page.drawLine({
      start: { x: sourcePos.x + 4, y: y + (up ? -1.5 : 1.5) },
      end: { x: targetPos.x - 4, y: y + (up ? 2.8 : -2.8) },
      thickness: 0.65,
      color: INK,
    });
    return true;
  }

  const midpoint = (sourcePos.x + targetPos.x) / 2;
  const connectorY = y + 5.5;
  page.drawLine({
    start: { x: sourcePos.x + 4, y: connectorY },
    end: { x: targetPos.x - 4, y: connectorY },
    thickness: 0.45,
    color: MID_INK,
  });
  page.drawText(type, {
    x: midpoint - 1.7,
    y: connectorY + 1.7,
    size: 5.2,
    font: bodyFont,
    color: MID_INK,
  });
  return true;
}

function compactTechniqueAnnotation(event) {
  const techniques = techniqueSet(event);
  if (techniques.has('tap')) return 'T';
  if (techniques.has('trill')) return 'tr';
  if (techniques.has('pinch-harmonic')) return 'P.H.';
  return '';
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
  void generatedTab;
  const events = validateV143RenderEvents(renderEvents);
  if (!events.length) {
    throw new Error('V143 structured rendering requires a complete valid render event stream.');
  }

  const presentation = summarizeV143RhythmPresentation(events);
  if (presentation.oneNotePerMeasureCollapseDetected) {
    throw new Error('V143 Rhythm render refused a suspicious one-note-per-measure collapsed event stream.');
  }

  const sections = buildReferenceFreeRhythmSections(events);
  const systems = buildSystems(events);
  const eventByIndex = new Map(events.map((event) => [Number(event.eventIndex), event]));
  const clearPreviewSystems = Math.max(1, Math.min(6, Number(previewSystems) || 4));

  const pdfDoc = await PDFDocument.create();
  const titleFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const bodyFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const tabFont = await pdfDoc.embedFont(StandardFonts.CourierBold);

  const safeSong = cleanText(song, 'Untitled');
  const safeArtist = cleanText(artist, 'Unknown Artist');
  const safeTuning = cleanText(tuning, 'E Standard');
  const safeTimeSignature = cleanText(timeSignature, '4/4');
  const metadata = [safeTuning, safeTimeSignature, formatTempo(tempo)];
  if (keySignature) metadata.push(cleanText(keySignature, ''));
  const settingsText = metadata.filter(Boolean).join('  |  ');

  pdfDoc.setTitle(`${safeSong} - ${safeArtist} - Rhythm Guitar TAB`);
  pdfDoc.setAuthor('DadRock Tabs Studio');
  pdfDoc.setSubject('Professional rhythm guitar tablature');
  pdfDoc.setCreator('DadRock Tabs Studio');
  pdfDoc.setProducer('DadRock Tabs Studio');
  pdfDoc.setKeywords(['guitar', 'tablature', 'rhythm guitar', 'DadRock Tabs']);

  const logoPath = path.join(process.cwd(), 'public', 'DadRock-Tabs-Logo.png');
  const logoBytes = await fs.readFile(logoPath);
  const logoImage = await pdfDoc.embedPng(logoBytes);
  const fullLogo = logoImage.scaleToFit(108, 50);
  const compactLogo = logoImage.scaleToFit(56, 27);

  function drawFirstPageHeader(page) {
    page.drawText('DADROCK TABS STUDIO', {
      x: PAGE.marginX,
      y: 763,
      size: 7.2,
      font: titleFont,
      color: ACCENT,
    });

    page.drawImage(logoImage, {
      x: PAGE.contentRight - fullLogo.width,
      y: 729,
      width: fullLogo.width,
      height: fullLogo.height,
    });

    page.drawText(safeSong, {
      x: PAGE.marginX,
      y: 728,
      size: fitTextSize(titleFont, safeSong, 360, 23, 15),
      font: titleFont,
      color: INK,
    });
    page.drawText(safeArtist, {
      x: PAGE.marginX,
      y: 704,
      size: fitTextSize(bodyFont, safeArtist, 350, 11.5, 8.5),
      font: bodyFont,
      color: MID_INK,
    });

    page.drawText('RHYTHM GUITAR', {
      x: PAGE.marginX,
      y: 676,
      size: 9.2,
      font: titleFont,
      color: INK,
    });
    page.drawText(settingsText, {
      x: PAGE.marginX + 94,
      y: 676,
      size: fitTextSize(bodyFont, settingsText, 400, 8.2, 6.2),
      font: bodyFont,
      color: MID_INK,
    });

    page.drawLine({
      start: { x: PAGE.marginX, y: 662 },
      end: { x: PAGE.contentRight, y: 662 },
      thickness: 0.7,
      color: HAIRLINE,
    });
  }

  function drawContinuationHeader(page) {
    page.drawImage(logoImage, {
      x: PAGE.marginX,
      y: 746,
      width: compactLogo.width,
      height: compactLogo.height,
    });
    const title = `${safeSong} - ${safeArtist}`;
    const titleX = PAGE.marginX + compactLogo.width + 10;
    page.drawText(title, {
      x: titleX,
      y: 758,
      size: fitTextSize(titleFont, title, 300, 10.5, 7.5),
      font: titleFont,
      color: INK,
    });
    const part = 'RHYTHM GUITAR';
    page.drawText(part, {
      x: PAGE.contentRight - titleFont.widthOfTextAtSize(part, 7),
      y: 758,
      size: 7,
      font: titleFont,
      color: MID_INK,
    });
    page.drawText(settingsText, {
      x: PAGE.contentRight - bodyFont.widthOfTextAtSize(settingsText, 6.3),
      y: 744,
      size: 6.3,
      font: bodyFont,
      color: LIGHT_INK,
    });
    page.drawLine({
      start: { x: PAGE.marginX, y: 731 },
      end: { x: PAGE.contentRight, y: 731 },
      thickness: 0.55,
      color: HAIRLINE,
    });
  }

  function drawStaff(page, system, staffTop) {
    const width = measureWidth();
    const systemRight = PAGE.staffLeft + Number(system.measureCount) * width;

    drawTabMark(page, staffTop, titleFont);
    if (system.systemIndex === 0) drawTimeSignature(page, staffTop, safeTimeSignature, titleFont);

    for (let stringIndex = 0; stringIndex < STRING_COUNT; stringIndex += 1) {
      const y = staffTop - stringIndex * STRING_SPACING;
      page.drawLine({
        start: { x: PAGE.staffLeft, y },
        end: { x: systemRight, y },
        thickness: 0.55,
        color: INK,
      });
    }

    for (let divider = 0; divider <= system.measureCount; divider += 1) {
      const x = PAGE.staffLeft + divider * width;
      page.drawLine({
        start: { x, y: staffTop + 0.5 },
        end: { x, y: staffTop - STAFF_HEIGHT - 0.5 },
        thickness: divider === 0 || divider === system.measureCount ? 1.05 : 0.7,
        color: INK,
      });
    }

    for (let offset = 0; offset < system.measureCount; offset += 1) {
      const measure = system.firstMeasure + offset;
      page.drawText(String(measure), {
        x: PAGE.staffLeft + offset * width + 2.5,
        y: staffTop + 4.6,
        size: 5.8,
        font: bodyFont,
        color: LIGHT_INK,
      });
      for (let beat = 1; beat < 4; beat += 1) {
        const x = PAGE.staffLeft + offset * width + (beat / 4) * width;
        page.drawLine({
          start: { x, y: staffTop + 1.8 },
          end: { x, y: staffTop - 1.8 },
          thickness: 0.35,
          color: HAIRLINE,
        });
      }
    }
  }

  function drawSustain(page, event, tokenWidth, staffTop, system) {
    const duration = Math.max(1, Number(event.durationSteps) || 1);
    if (duration <= 1) return;
    const pos = positionForEvent(event, staffTop, system);
    const startAbs = absoluteSystemStep(event, system);
    const endAbs = Math.min(system.measureCount * STEPS_PER_MEASURE, startAbs + duration);
    const endX = positionForAbsoluteStep(endAbs, system) - 1.5;
    const startX = pos.x + tokenWidth / 2 + 2;
    if (endX <= startX + 1) return;
    page.drawLine({
      start: { x: startX, y: pos.y + 0.4 },
      end: { x: endX, y: pos.y + 0.4 },
      thickness: 0.35,
      color: LIGHT_INK,
    });
  }

  function drawSystem(page, system, topY, locked = false) {
    const staffTop = topY - 34;
    const systemRight = PAGE.staffLeft + system.measureCount * measureWidth();

    drawRehearsalMarks(page, system, staffTop, sections, titleFont, bodyFont);
    drawStaff(page, system, staffTop);

    if (locked) {
      page.drawRectangle({
        x: PAGE.staffLeft + 1,
        y: staffTop - STAFF_HEIGHT - 2,
        width: Math.max(4, systemRight - PAGE.staffLeft - 2),
        height: STAFF_HEIGHT + 17,
        color: rgb(1, 1, 1),
        opacity: 0.94,
      });
      page.drawText('PREVIEW LOCKED', {
        x: PAGE.staffLeft + 12,
        y: staffTop - 20,
        size: 7.2,
        font: titleFont,
        color: LIGHT_INK,
      });
      return;
    }

    drawTechniqueRanges(page, system, staffTop, bodyFont, titleFont);
    drawRhythmLane(page, system, staffTop);

    for (const event of system.events) {
      const { x, y, stepWidth } = positionForEvent(event, staffTop, system);
      const token = fretToken(event);
      const size = token.length > 4 ? 6 : token.length > 2 ? 6.8 : 7.7;
      const width = tabFont.widthOfTextAtSize(token, size);
      const textX = x - width / 2;
      page.drawRectangle({
        x: textX - 1.2,
        y: y - 4.7,
        width: width + 2.4,
        height: 9.6,
        color: rgb(1, 1, 1),
      });
      page.drawText(token, {
        x: textX,
        y: y - 3,
        size,
        font: tabFont,
        color: INK,
      });

      drawSustain(page, event, width, staffTop, system);
      drawBend(page, event, staffTop, system, bodyFont);

      const techniques = techniqueSet(event);
      if (techniques.has('vibrato')) {
        const duration = Math.max(1, Number(event.durationSteps) || 1);
        const endX = Math.min(
          systemRight - 2,
          x + Math.max(9, Math.min(duration, 8) * stepWidth)
        );
        drawVibrato(page, x + width / 2 + 2.5, y + 5.3, endX);
      }

      const annotation = compactTechniqueAnnotation(event);
      if (annotation) {
        page.drawText(annotation, {
          x: x - 3,
          y: y + 7.2,
          size: annotation.length > 2 ? 4.2 : 5,
          font: annotation === 'T' ? titleFont : bodyFont,
          color: MID_INK,
        });
      }
    }

    for (const source of system.events) {
      const targetIndex = Number(source.legatoTargetEventIndex);
      const target = Number.isInteger(targetIndex) ? eventByIndex.get(targetIndex) : null;
      const connected = drawTechniqueConnector({
        page,
        bodyFont,
        source,
        target,
        staffTop,
        system,
      });
      if (!connected) {
        const type = connectorType(source);
        if (type && type !== 'slide') {
          const { x, y } = positionForEvent(source, staffTop, system);
          page.drawText(type, {
            x: x + 3.5,
            y: y + 5.5,
            size: 4.8,
            font: bodyFont,
            color: MID_INK,
          });
        }
      }
    }
  }

  let page = pdfDoc.addPage([PAGE.width, PAGE.height]);
  drawFirstPageHeader(page);
  let currentY = FIRST_PAGE_TOP;

  systems.forEach((system, index) => {
    if (currentY - SYSTEM_HEIGHT < PAGE.bottomLimit) {
      page = pdfDoc.addPage([PAGE.width, PAGE.height]);
      drawContinuationHeader(page);
      currentY = CONTINUATION_TOP;
    }
    drawSystem(page, system, currentY, preview && index >= clearPreviewSystems);
    currentY -= SYSTEM_HEIGHT;
  });

  const pages = pdfDoc.getPages();
  pages.forEach((pdfPage, pageIndex) => {
    if (preview) {
      pdfPage.drawText('DADROCK TABS PREVIEW', {
        x: 92,
        y: pageIndex === 0 ? 300 : 350,
        size: 34,
        font: titleFont,
        color: rgb(0.68, 0.68, 0.68),
        rotate: degrees(34),
        opacity: 0.13,
      });
    }

    const footerLeft = 'dadrocktabs.com';
    pdfPage.drawText(footerLeft, {
      x: PAGE.marginX,
      y: 18,
      size: 6.4,
      font: bodyFont,
      color: LIGHT_INK,
    });
    const footerCenter = 'DadRock Tabs Studio';
    pdfPage.drawText(footerCenter, {
      x: (PAGE.width - bodyFont.widthOfTextAtSize(footerCenter, 6.4)) / 2,
      y: 18,
      size: 6.4,
      font: bodyFont,
      color: LIGHT_INK,
    });
    const pageText = `${pageIndex + 1} / ${pages.length}`;
    pdfPage.drawText(pageText, {
      x: PAGE.contentRight - bodyFont.widthOfTextAtSize(pageText, 6.4),
      y: 18,
      size: 6.4,
      font: bodyFont,
      color: LIGHT_INK,
    });
  });

  return pdfDoc.save();
}
