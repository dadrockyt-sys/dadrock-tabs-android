# Astra S8 failure analysis V1

Date: 2026-09-28
Scope: offline review only. No model execution, rendering, optimizer work, threshold search, P1/P2/P3, Codespaces, or Vercel.

## Frozen S8 result

The sampler intervention worked mechanically:
- control selected mean positive strings/frame: 1.228875;
- token-balanced selected mean: 1.557000;
- control selected 3-string frames: 1,831 / 16,000;
- weighted selected 3-string frames: 4,456 / 16,000.

The other 96 minibatch positions were paired-identical.

Yet test results moved as follows:
- chord F1: 0.3077 -> 0.2667;
- chord recall: 0.2222 -> 0.1667;
- state admission: 0.4109 -> 0.3798;
- joint admission: 0.3566 -> 0.3411;
- overall recall: 0.6279 -> 0.6047;
- overall F1: 0.7105 -> 0.7256;
- precision: 0.8182 -> 0.9070;
- repeated recall: 0.5952 -> 0.6905.

S8 failed 9 of 15 frozen criteria.

## Interpretation

Existing chord/multi-string frames were not simply under-sampled.

Increasing their frequency caused fewer false positives overall but did not improve chord generalization and reduced state confidence/admission.

The current chord training set contains only 10 distinct training voicings. Each is rendered in three timbre variants, yielding 30 chord training clips but only 10 unique target configurations.

The S8 result therefore points to **diversity of chord target configurations** as a more plausible next data hypothesis than repeated exposure frequency.

## S9 isolation strategy

Keep the number of chord training clips exactly 30 and preserve the three timbre conditions exactly 10 times each.

Control:
- 10 unique chord voicings x 3 timbre variants = 30 clips.

Intervention:
- 30 unique chord voicings x 1 paired timbre condition each = 30 clips.

To avoid a timbre confound, every intervention chord clip is paired to one control chord slot and uses the exact same deterministic timbre RNG key as that slot. Both chord templates contain the same number/timing/duration of six note events; only string/fret voicing identity changes.

Validation/test chord clips remain identical across arms.

All non-chord arrays remain bit-identical across arms.

This makes the only intended training-data variable the number of unique chord voicings.
