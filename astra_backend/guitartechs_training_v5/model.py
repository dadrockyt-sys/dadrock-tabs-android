from __future__ import annotations

import torch
from torch import nn

NUM_STRINGS = 6
NUM_FRETS = 20
NUM_CLASSES = 21
SILENCE_CLASS = 20
OPEN_MIDI = (40, 45, 50, 55, 59, 64)
MIN_MIDI = 40
MAX_MIDI = 83
NUM_PITCHES = MAX_MIDI - MIN_MIDI + 1

ACOUSTIC_EMBEDDING = 128
TEMPORAL_HIDDEN = 96
DROPOUT = 0.25


class TemporalTabCNNV5(nn.Module):
    """TabCNN acoustic convolution + causal GRU + supervised auxiliary heads.

    The state head is softly conditioned on onset, string-activity, and pitch
    probabilities so event admission and physical-string routing are no longer
    forced through one framewise softmax.
    """

    def __init__(self, source_root: str):
        super().__init__()
        import sys
        if source_root not in sys.path:
            sys.path.insert(0, source_root)
        from amt_tools.models.tabcnn import TabCNN
        from amt_tools.tools.instrument import GuitarProfile

        tabcnn = TabCNN(
            dim_in=192,
            profile=GuitarProfile(
                tuning=["E2", "A2", "D3", "G3", "B3", "E4"],
                num_frets=19,
            ),
            device="cpu",
        )
        self.in_channels = tabcnn.in_channels
        self.dim_in = tabcnn.dim_in
        self.frame_width = tabcnn.frame_width
        self.conv = tabcnn.conv
        self.conv_embedding_size = tabcnn.conv_embedding_size

        self.acoustic = nn.Sequential(
            nn.Linear(self.conv_embedding_size, ACOUSTIC_EMBEDDING),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
        )
        self.temporal = nn.GRU(
            input_size=ACOUSTIC_EMBEDDING,
            hidden_size=TEMPORAL_HIDDEN,
            num_layers=1,
            batch_first=True,
        )
        self.onset_head = nn.Linear(TEMPORAL_HIDDEN, NUM_STRINGS)
        self.activity_head = nn.Linear(TEMPORAL_HIDDEN, NUM_STRINGS)
        self.pitch_head = nn.Linear(TEMPORAL_HIDDEN, NUM_PITCHES)

        routed_dim = TEMPORAL_HIDDEN + NUM_STRINGS + NUM_STRINGS + NUM_PITCHES
        self.routing = nn.Sequential(
            nn.Linear(routed_dim, TEMPORAL_HIDDEN),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
        )
        self.state_head = nn.Linear(TEMPORAL_HIDDEN, NUM_STRINGS * NUM_CLASSES)

        # Homoscedastic multi-task weighting, learned only from training data.
        # Order: state, onset, activity, pitch.
        self.task_log_vars = nn.Parameter(torch.zeros(4, dtype=torch.float32))

    def forward(self, feats: torch.Tensor, hidden: torch.Tensor | None = None):
        if feats.ndim != 5:
            raise ValueError("expected B x T x C x F x W features")
        batch, frames = feats.shape[:2]
        x = feats.reshape(-1, self.in_channels, self.dim_in, self.frame_width)
        x = self.conv(x).flatten(1)
        x = self.acoustic(x).view(batch, frames, ACOUSTIC_EMBEDDING)

        temporal, hidden_out = self.temporal(x, hidden)
        onset_logits = self.onset_head(temporal)
        activity_logits = self.activity_head(temporal)
        pitch_logits = self.pitch_head(temporal)

        auxiliaries = torch.cat(
            (
                torch.sigmoid(onset_logits),
                torch.sigmoid(activity_logits),
                torch.sigmoid(pitch_logits),
            ),
            dim=-1,
        )
        routed = self.routing(torch.cat((temporal, auxiliaries), dim=-1))
        state_logits = self.state_head(routed)

        return {
            "tablature": state_logits,
            "onset": onset_logits,
            "activity": activity_logits,
            "pitch": pitch_logits,
            "hidden": hidden_out,
            "taskLogVars": self.task_log_vars,
        }
