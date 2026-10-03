# Non-Collinear Duplicate Stress Result V1

Date: 2026-10-02
Run ID: 37089070395
Status: **PAIR DETECTOR PASS / CONSOLIDATION NOT UNIVERSALLY SAFE**

Artifact:
- id: 11262155308
- digest: `sha256:17af190d0224c0654052baa02f35e0002c215147cd0432e1f21a3832b6c5b192`

## Detector result

Frozen PairClassifierConfig V1:
- cases: 16
- correct: 15
- accuracy: **93.75%**

Only G09 delayed_highband_leak was rejected as ambiguous because its pair energy gap reached ~6.44 dB, beyond the frozen 6 dB threshold.

This supports the detector generalizing to non-collinear split errors without threshold changes.

## Consolidation result

Blind merge is **not universally safe**.

Strong positive examples:
- B01 time_varying_split: +142.32 dB
- B08 time_varying_split: +142.37 dB
- G09 time_varying_split: +140.36 dB
- G14 time_varying_split: +142.06 dB
- G09 frequency_partition: +17.41 dB
- G09 delayed_highband_leak: +9.17 dB

Negative examples:
- B01 frequency_partition: -0.47 dB
- B01 delayed_highband_leak: -0.38 dB
- B01 filtered_plus_contamination: -1.97 dB
- G14 frequency_partition: -2.89 dB
- G14 delayed_highband_leak: -3.06 dB
- G14 filtered_plus_contamination: -0.25 dB

All merges preserve the synthetic pair sum exactly (max reconstruction error 0.0), but the pair sum is not always a faithful version of the original isolated source because some perturbations intentionally introduce filtering, delay and contamination.

## Decision

Freeze PairClassifierConfig V1 unchanged.

Do **not** automatically merge every duplicate-class candidate.

Next gate must estimate whether the two duplicate-class stems are actually complementary fragments of one source. The next no-reference signal is pair waveform coherence:
- zero-lag correlation;
- maximum short-lag normalized correlation;
- optional bandwise coherence;
- energy balance.

The target hypothesis:
- high-coherence duplicate-class pairs are merge candidates;
- low-coherence duplicate-class pairs remain flagged but unmodified.

S0M10 should be rerun with the same coherence metrics to see whether its successful +30.50 dB merge is associated with high pair coherence.

No production consolidation is authorized.
