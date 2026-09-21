# Guitar-TECHS V1 Training Failure Diagnosis

Date: 2026-09-21  
Failed result receipt: `3edfcf97766bef89ea56429a7385107d99868dc948d867251bcc5f9066a18112`

## Primary finding

The V1 run did **not** implement the training-exposure semantics of the pinned TabCNN experiment whose numerical limits it copied.

The pinned `guitarProFx.py` experiment sets `num_frames = 200`, batch size 32 and 2,500 training iterations. Its shared `train()` routine defines one global iteration as a complete loop over the DataLoader, not one optimizer step. Each dataset item is one random contiguous 200-frame slice from a track.

V1 instead performed exactly one optimizer step per loop and sampled one isolated frame for each of 32 batch elements.

Therefore V1 exposed the model to only:

`2,500 × 32 = 80,000` supervised frame positions per fold.

Even holding the same number of optimizer steps fixed, 200-frame sequences would expose:

`2,500 × 32 × 200 = 16,000,000` frame positions,

a **200×** difference before accounting for the upstream full-DataLoader loop semantics.

This makes the V1 model materially undertrained relative to the source recipe. The failed P1/P2 metrics are valid evidence that **V1 failed**, but they do not establish that Guitar-TECHS or TabCNN cannot meet the frozen quality gates under a correctly implemented training schedule.

## Secondary sampling risk

V1's sampler accepts a frame whenever any target differs from `MASK=-100`. Ordinary silence is `-1`, so silence-only frames satisfy that test and are eligible. Combined with isolated uniform frame sampling, this can produce a heavily silence-skewed training stream.

The upstream path samples contiguous 200-frame snippets per track, preserving temporal/event context and much more label exposure.

## What is *not* broken

Static review confirms:
- `GuitarProfile(num_frets=19)` means open string plus frets 1–19 = 20 playable states;
- TabCNN adds one silence class = 21 classes/string;
- six strings therefore produce exactly 126 logits;
- V1 physical string ordering matches the frozen low-to-high tuning;
- the output reshape / silence-class mapping is consistent with pinned `SoftmaxGroups`.

## Frozen V2 correction

V2 synthetic/design work uses:
- 200-frame contiguous sequences;
- one sample per underlying performance per epoch;
- deterministic rotation among that performance's alignment-accepted capture views;
- deterministic seeded segment starts;
- no `drop_last` loss of performance groups;
- loss across every unmasked string target in all 200 frames;
- mandatory pretraining diagnostics for active/silence/mask fractions and per-string fret histograms.

The frozen development quality thresholds do not change.

Receipt: `docs/astra/GUITARTECHS_V1_TRAINING_FAILURE_DIAGNOSIS_V1.json`  
SHA-256: **`c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848`**

This diagnosis authorizes no new real-data training and no P3 access.
