const CONTRACT = Object.freeze({
  numStrings: 6,
  minFret: 0,
  maxFret: 19,
  silenceTablatureState: -1,
  silenceSoftmaxClass: 20,
  classesPerString: 21,
  totalLogits: 126,
  sampleRateHz: 22050,
  hopLengthSamples: 512,
  contractReceiptSha256: '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f',
});

function validTuning(tuningMidi) {
  return Array.isArray(tuningMidi)
    && tuningMidi.length === CONTRACT.numStrings
    && tuningMidi.every((pitch) => Number.isInteger(pitch) && pitch >= 0 && pitch <= 127);
}

export function getGuitarTechsLabelContract() {
  return structuredClone(CONTRACT);
}

export function validateGuitarTechsStringTrackMap(trackToString) {
  if (!Array.isArray(trackToString) || trackToString.length !== CONTRACT.numStrings) return false;
  const values = [...trackToString].sort((a, b) => a - b);
  return values.every((value, index) => value === index);
}

export function encodeGuitarTechsStringFrame({
  stringIndex,
  activeMidiPitches = [],
  tuningMidi,
} = {}) {
  if (!Number.isInteger(stringIndex) || stringIndex < 0 || stringIndex >= CONTRACT.numStrings) {
    return { state: 'abstained', reason: 'STRING_INDEX_UNVERIFIED' };
  }
  if (!validTuning(tuningMidi)) {
    return { state: 'abstained', reason: 'TUNING_UNVERIFIED' };
  }
  if (!Array.isArray(activeMidiPitches)) {
    return { state: 'abstained', reason: 'ACTIVE_PITCHES_INVALID' };
  }
  if (activeMidiPitches.length === 0) {
    return {
      state: 'encoded',
      tablatureState: CONTRACT.silenceTablatureState,
      softmaxClass: CONTRACT.silenceSoftmaxClass,
      fret: null,
    };
  }
  if (activeMidiPitches.length !== 1) {
    return { state: 'abstained', reason: 'SAME_STRING_POLYPHONY_UNREPRESENTABLE' };
  }
  const midiPitch = activeMidiPitches[0];
  if (!Number.isInteger(midiPitch) || midiPitch < 0 || midiPitch > 127) {
    return { state: 'abstained', reason: 'MIDI_PITCH_INVALID' };
  }
  const fret = midiPitch - tuningMidi[stringIndex];
  if (fret < CONTRACT.minFret || fret > CONTRACT.maxFret) {
    return { state: 'abstained', reason: 'FRET_OUT_OF_RANGE', fret };
  }
  return {
    state: 'encoded',
    tablatureState: fret,
    softmaxClass: fret,
    fret,
  };
}
