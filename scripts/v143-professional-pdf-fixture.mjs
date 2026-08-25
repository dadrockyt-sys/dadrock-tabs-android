import fs from 'node:fs/promises';
import path from 'node:path';
import { createV143RhythmPdf } from '../lib/createV143RhythmPdf.js';

const OPEN = [64, 59, 55, 50, 45, 40];
const events = [];

function add(measure, step, stringIndex, fret, durationSteps = 1, techniques = [], extra = {}) {
  const eventIndex = events.length;
  events.push({
    eventIndex,
    measure,
    step,
    stringIndex,
    fret,
    midi: OPEN[stringIndex] + fret,
    durationSteps,
    techniques,
    ...extra,
  });
  return eventIndex;
}

function powerChord(measure, step, rootFret, techniques = [], durationSteps = 2) {
  add(measure, step, 5, rootFret, durationSteps, techniques);
  add(measure, step, 4, rootFret + 2, durationSteps, techniques);
  add(measure, step, 3, rootFret + 2, durationSteps, techniques);
}

powerChord(1, 0, 5, ['palm-mute'], 2);
powerChord(1, 4, 5, ['palm-mute'], 2);
powerChord(1, 8, 8, ['palm-mute'], 2);
powerChord(1, 12, 3, [], 4);

for (let step = 0; step < 16; step += 2) {
  add(2, step, 5, [5, 5, 8, 5, 10, 8, 5, 3][step / 2], 2, step < 12 ? ['palm-mute'] : []);
}

const h1 = add(3, 0, 3, 5, 2, ['hammer-on']);
const h2 = add(3, 2, 3, 7, 2, ['pull-off']);
const h3 = add(3, 4, 3, 5, 4, ['vibrato']);
events[h1].legatoTargetEventIndex = h2;
events[h2].legatoTargetEventIndex = h3;
add(3, 8, 4, 7, 2);
const s1 = add(3, 10, 4, 9, 2, ['slide-up']);
const s2 = add(3, 12, 4, 12, 4, ['vibrato']);
events[s1].legatoTargetEventIndex = s2;

const bend = add(4, 0, 0, 10, 4, ['bend', 'vibrato'], { bendSemitones: 1, bendTargetFret: 12, bendTargetMidi: 76 });
void bend;
add(4, 4, 0, 10, 4, ['bend-release'], { bendSemitones: 1, bendTargetFret: 12, bendTargetMidi: 76, bendRelease: true });
add(4, 8, 1, 12, 4, ['natural-harmonic']);
add(4, 12, 2, 9, 4, ['pinch-harmonic', 'vibrato']);

for (let step = 0; step < 16; step += 1) {
  add(5, step, 5, 5 + (step % 4), 1, step % 4 < 3 ? ['palm-mute'] : []);
}

powerChord(6, 0, 0, ['let-ring'], 8);
powerChord(6, 8, 3, ['let-ring'], 8);

for (let step = 0; step < 16; step += 4) {
  add(7, step, 5, 0, 2, ['dead-note', 'muted-strum']);
  add(7, step, 4, 0, 2, ['dead-note', 'muted-strum']);
  add(7, step, 3, 0, 2, ['dead-note', 'muted-strum']);
}

add(8, 0, 2, 12, 4, ['tap']);
add(8, 4, 2, 9, 4, ['trill']);
add(8, 8, 1, 10, 8, ['vibrato', 'let-ring']);

for (let measure = 9; measure <= 20; measure += 1) {
  if (measure % 3 === 0) {
    powerChord(measure, 0, 3, ['palm-mute'], 2);
    powerChord(measure, 4, 5, ['palm-mute'], 2);
    powerChord(measure, 8, 8, [], 4);
    powerChord(measure, 12, 10, [], 4);
  } else if (measure % 3 === 1) {
    for (let step = 0; step < 16; step += 2) {
      add(measure, step, 4, 5 + ((step / 2) % 5), 2, step < 8 ? ['palm-mute'] : []);
    }
  } else {
    add(measure, 0, 1, 8, 4);
    add(measure, 4, 1, 10, 4, ['vibrato']);
    add(measure, 8, 2, 9, 4);
    add(measure, 12, 3, 10, 4, ['let-ring']);
  }
}

const output = process.argv[2] || 'debug/v143-contextual-prune/professional-pdf-fixture.pdf';
await fs.mkdir(path.dirname(output), { recursive: true });
const bytes = await createV143RhythmPdf({
  song: 'Professional Rhythm TAB Fixture',
  artist: 'DadRock Tabs Studio',
  renderEvents: events,
  tuning: 'E Standard',
  tempo: 129.19921875,
  timeSignature: '4/4',
  keySignature: 'E minor',
  preview: false,
});
await fs.writeFile(output, bytes);
console.log(JSON.stringify({ output, eventCount: events.length, bytes: bytes.length }, null, 2));
