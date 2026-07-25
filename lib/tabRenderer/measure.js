import { STAFF_LAYOUT } from './constants';

export function createMeasures(staff, measureCount = 4) {
  const safeMeasureCount = Math.max(1, measureCount);
  const measureWidth = staff.width / safeMeasureCount;

  const barLines = Array.from(
    { length: safeMeasureCount + 1 },
    (_, index) => ({
      x: staff.x + index * measureWidth,
      y1: staff.y,
      y2: staff.y + staff.height,
      lineWidth: STAFF_LAYOUT.lineWidth,
    })
  );

  const measures = Array.from(
    { length: safeMeasureCount },
    (_, index) => ({
      index,
      x: staff.x + index * measureWidth,
      y: staff.y,
      width: measureWidth,
      height: staff.height,
      startX: staff.x + index * measureWidth,
      endX: staff.x + (index + 1) * measureWidth,
    })
  );

  return {
    measureCount: safeMeasureCount,
    measureWidth,
    barLines,
    measures,
  };
}
