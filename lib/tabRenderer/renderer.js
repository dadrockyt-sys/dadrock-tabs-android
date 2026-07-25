import { createStaff } from './staff';
import { createMeasures } from './measure';

export function createTabPage({
  instrumentType = 'lead',
  title = '',
  artist = '',
  tuning = '',
  tempo = '',
  difficulty = '',
}) {
  const staff = createStaff({
    instrumentType,
  });

  const measureLayout = createMeasures(staff, 4);

  return {
    title,
    artist,
    tuning,
    tempo,
    difficulty,
    instrumentType,

    staff,

    measures: measureLayout.measures,
    barLines: measureLayout.barLines,

    notes: [],
    symbols: [],
  };
}
