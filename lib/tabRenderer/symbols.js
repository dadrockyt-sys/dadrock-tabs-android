export function createFretNumber({
  string,
  fret,
  measure,
  beat,
}) {
  return {
    type: 'fret',
    string,
    fret: String(fret),
    measure,
    beat,
  };
}

export function createSlide(from, to) {
  return {
    type: 'slide',
    from,
    to,
  };
}

export function createHammerOn(from, to) {
  return {
    type: 'hammerOn',
    from,
    to,
  };
}

export function createPullOff(from, to) {
  return {
    type: 'pullOff',
    from,
    to,
  };
}

export function createBend(note) {
  return {
    type: 'bend',
    note,
  };
}
