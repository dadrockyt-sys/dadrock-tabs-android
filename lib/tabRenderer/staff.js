import { INSTRUMENTS, STAFF_LAYOUT } from './constants';

export function createStaff({
  instrumentType = 'lead',
  x = 48,
  y = 120,
  width = 516,
}) {
  const instrument = INSTRUMENTS[instrumentType] || INSTRUMENTS.lead;

  const lines = instrument.tuning.map((label, index) => {
    const lineY = y + index * STAFF_LAYOUT.stringSpacing;

    return {
      label,
      x1: x,
      y1: lineY,
      x2: x + width,
      y2: lineY,
      lineWidth: STAFF_LAYOUT.lineWidth,
    };
  });

  return {
    instrument,
    x,
    y,
    width,
    height:
      (instrument.stringCount - 1) * STAFF_LAYOUT.stringSpacing,
    lines,
  };
}
