from __future__ import annotations

# V7 deliberately reuses the verified V6 representation. The scientific change
# is the objective/decoder: event scores are ranked, never probability-gated.
from guitartechs_training_v6.model import (
    ACOUSTIC_EMBEDDING, DROPOUT, MAX_MIDI, MIN_MIDI, NUM_CLASSES, NUM_FRETS,
    NUM_PITCHES, NUM_STRINGS, OPEN_MIDI, SILENCE_CLASS, TEMPORAL_HIDDEN,
    TemporalTabCNNV6,
)

class TemporalTabCNNV7(TemporalTabCNNV6):
    """Calibration-free event-ranking candidate."""
    pass
