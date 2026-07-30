import { rgb } from 'pdf-lib';

const PAGE = {
  marginX: 50,
  contentRight: 560,
};

const MEASURES_PER_SYSTEM = 6;
const SECTION_PATTERN = /^(INTRO|VERSE(?:\s+\d+)?|PRE-CHORUS|CHORUS(?:\s+\d+)?|BRIDGE|SOLO|OUTRO|BREAKDOWN|INTERLUDE|RIFF|ENDING)\b/i;
const STRING_LINE_PATTERN = /^\s*([eEADGB])\s*\|?(.*)$/;

function finiteNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function cleanAscii(value, fallback = '') {
  const cleaned = String(value ?? fallback)
    .replace(/[^\x20-\x7E]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  return cleaned || fallback;
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
      if (currentRows === expectedRows) systems.push(pendingSection);
      currentRows = 0;
      pendingSection = true;
      continue;
    }

    if (!STRING_LINE_PATTERN.test(line)) {
      if (currentRows === expectedRows) systems.push(pendingSection);
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

  if (currentRows === expectedRows) systems.push(pendingSection);
  return systems.length ? systems : [false];
}

function buildSystemLayout({ pages, generatedTab, transcriptionType }) {
  const sections = parseSystemSections(generatedTab, transcriptionType);
  const baseSystemHeight = transcriptionType === 'bass' ? 60 : 59;
  const stringSpacing = transcriptionType === 'bass' ? 9 : 7;
  const stringCount = transcriptionType === 'bass' ? 4 : 6;
  const staffHeight = stringSpacing * (stringCount - 1);
  const firstPageTop = 578;
  const continuationTop = 704;
  const bottomLimit = 44;

  const layouts = [];
  let pageIndex = 0;
  let currentY = firstPageTop;

  sections.forEach((hasSection, systemIndex) => {
    const sectionOffset = hasSection ? 14 : 0;
    const requiredHeight = baseSystemHeight + sectionOffset;

    if (currentY - requiredHeight < bottomLimit) {
      pageIndex += 1;
      currentY = continuationTop;
    }

    if (!pages[pageIndex]) return;

    const staffTop = currentY - sectionOffset;
    layouts.push({
      rowNumber: systemIndex + 1,
      pageIndex,
      staffTop,
      staffBottom: staffTop - staffHeight,
      hasSection,
    });

    currentY -= requiredHeight;
  });

  return layouts;
}

function isValidGrid(grid) {
  return Boolean(
    grid &&
      typeof grid === 'object' &&
      grid.passed === true &&
      grid.measureGridVersion === 7 &&
      Number(grid.measuresPerRow) === MEASURES_PER_SYSTEM &&
      Array.isArray(grid.rows)
  );
}

function markerX(ratio) {
  const usableWidth = PAGE.contentRight - PAGE.marginX;
  return PAGE.marginX + clamp(finiteNumber(ratio), 0, 1) * usableWidth;
}

function assignChordLanes(fragments) {
  const lanes = [];
  const assignments = new Map();

  fragments
    .filter((fragment) => fragment.markerType === 'chord-label')
    .sort((a, b) => finiteNumber(a.rowStartRatio) - finiteNumber(b.rowStartRatio))
    .forEach((fragment) => {
      const x = markerX(fragment.rowStartRatio);
      let lane = lanes.findIndex((lastX) => x - lastX >= 34);
      if (lane < 0) lane = lanes.length;
      lanes[lane] = x;
      assignments.set(fragment, lane);
    });

  return assignments;
}

function drawPalmMute(page, fragment, staffTop, bodyFont, boldFont) {
  const startX = markerX(fragment.rowStartRatio);
  const endX = Math.max(startX + 5, markerX(fragment.rowEndRatio));
  const y = staffTop + 9;
  const prefix = fragment.continuesFromPreviousMeasure ? '< ' : '';
  const suffix = fragment.continuesIntoNextMeasure ? ' >' : '';

  page.drawText(`${prefix}P.M.${suffix}`, {
    x: startX,
    y: y + 3,
    size: 6.2,
    font: boldFont,
    color: rgb(0.18, 0.18, 0.18),
  });

  for (let x = startX + 25; x < endX; x += 4) {
    page.drawLine({
      start: { x, y },
      end: { x: Math.min(x + 1.7, endX), y },
      thickness: 0.55,
      color: rgb(0.28, 0.28, 0.28),
    });
  }
}

function drawBendRelease(page, fragment, staffTop, bodyFont, boldFont) {
  const startX = markerX(fragment.rowStartRatio);
  const endX = Math.max(startX + 24, markerX(fragment.rowEndRatio));
  const y = staffTop + 17;

  page.drawText('full', {
    x: startX + 4,
    y: y + 8,
    size: 6.4,
    font: boldFont,
    color: rgb(0.12, 0.12, 0.12),
  });
  page.drawLine({
    start: { x: startX, y },
    end: { x: startX + 8, y: y + 7 },
    thickness: 0.8,
    color: rgb(0.12, 0.12, 0.12),
  });
  page.drawLine({
    start: { x: startX + 8, y: y + 7 },
    end: { x: endX - 8, y: y + 7 },
    thickness: 0.8,
    color: rgb(0.12, 0.12, 0.12),
  });
  page.drawLine({
    start: { x: endX - 8, y: y + 7 },
    end: { x: endX, y },
    thickness: 0.8,
    color: rgb(0.12, 0.12, 0.12),
  });
}

function compactMarkerLabel(fragment) {
  const type = fragment.markerType;
  const raw = cleanAscii(fragment.label, '');

  if (type === 'slide') {
    const match = raw.match(/(\d+)/);
    return match ? `/${match[1]}` : '/';
  }
  if (type === 'muted-attack') return 'x';
  if (type === 'rest') return 'rest';
  return raw;
}

export function drawV7MeasureGridOverlay({
  pages,
  generatedTab,
  transcriptionType,
  measureGrid,
  bodyFont,
  boldFont,
}) {
  if (!isValidGrid(measureGrid)) {
    return {
      enabled: false,
      reason: 'missing-or-invalid-v7-measure-grid',
      rowsRendered: 0,
      fragmentsRendered: 0,
    };
  }

  const layouts = buildSystemLayout({
    pages,
    generatedTab,
    transcriptionType,
  });
  const layoutByRow = new Map(layouts.map((layout) => [layout.rowNumber, layout]));
  let rowsRendered = 0;
  let fragmentsRendered = 0;

  for (const row of measureGrid.rows) {
    const rowNumber = Number(row?.rowNumber);
    const layout = layoutByRow.get(rowNumber);
    const fragments = Array.isArray(row?.fragments) ? row.fragments : [];
    if (!layout || !fragments.length) continue;

    const page = pages[layout.pageIndex];
    if (!page) continue;

    const chordLanes = assignChordLanes(fragments);
    rowsRendered += 1;

    for (const fragment of fragments) {
      const type = cleanAscii(fragment.markerType, '');
      const x = markerX(fragment.rowStartRatio);

      if (type === 'palm-mute-span') {
        drawPalmMute(page, fragment, layout.staffTop, bodyFont, boldFont);
        fragmentsRendered += 1;
        continue;
      }

      if (type === 'bend-release') {
        drawBendRelease(page, fragment, layout.staffTop, bodyFont, boldFont);
        fragmentsRendered += 1;
        continue;
      }

      if (type === 'chord-label') {
        const label = cleanAscii(fragment.label, '');
        if (!label) continue;
        const lane = chordLanes.get(fragment) || 0;
        page.drawText(label, {
          x,
          y: layout.staffTop + 20 + lane * 8,
          size: 7.2,
          font: boldFont,
          color: rgb(0.08, 0.08, 0.08),
        });
        fragmentsRendered += 1;
        continue;
      }

      const label = compactMarkerLabel(fragment);
      if (!label) continue;
      page.drawText(label, {
        x,
        y: type === 'rest' ? layout.staffTop - 13 : layout.staffTop - 5,
        size: type === 'muted-attack' ? 8 : 6.8,
        font: type === 'muted-attack' ? boldFont : bodyFont,
        color: rgb(0.12, 0.12, 0.12),
      });
      fragmentsRendered += 1;
    }
  }

  return {
    enabled: true,
    reason: 'v7-measure-grid-overlay-rendered',
    rowsRendered,
    fragmentsRendered,
  };
}
