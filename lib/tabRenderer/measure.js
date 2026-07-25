import { STAFF_LAYOUT } from './constants';

export function createMeasures(staff, measureCount = 4) {
  const measureWidth = staff.width / measureCount;

  return Array.from({ length: measureCount + 1 }, (_, index) => ({
    x: staff.x + index * measureWidth,
    y1: staff.y,
    y2: staff.y + staff.height,
    lineWidth: STAFF_LAYOUT.lineWidth,
  }));
}
