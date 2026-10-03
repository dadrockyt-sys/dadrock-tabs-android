# S0 Bleed Diagnostics Result V1

Date: 2026-10-02
Run ID: 37080742780
Status: **SUCCESSFUL DIAGNOSTIC PASS**

Artifact:
- id: 11258307460
- digest: `sha256:2901f82fa01d9ed88886e02e23a3e3ef24519dbbc0af6c29ee714bc174b7fb6b`

## Main conclusion

Simple separator-output overlap metrics are **not sufficient** to decide when bleed cleanup should activate.

Across target-present guitar/bass stems, correlation between cleanup improvement and the candidate diagnostic signals was weak:
- interference pressure vs improvement: ~0.08
- competitor dominance vs improvement: ~-0.01
- target dominance vs improvement: ~0.04
- stem-to-mixture energy vs improvement: ~-0.11

These values are descriptive for the current 12-mixture S0 set only, but they do not support a simple threshold gate.

## What the diagnostics do well

They clearly identify several near-empty absent-target stems:
- S0M07 bass: ~-92.6 dB vs mixture, interference pressure ~1.0
- S0M08 guitar: ~-93.2 dB, pressure ~1.0
- S0M09 bass: ~-92.0 dB, pressure ~1.0

Those stems are already essentially silent; extra cleanup is unnecessary.

## Hard failure case

S0M10 contains no guitar target, but BS-Roformer emits a substantial guitar stem:
- guitar target present: false
- stem-to-mixture energy: ~-3.03 dB
- interference pressure: ~0.120
- target-dominance fraction: ~0.776
- strongest overlap competitor: bass

This false guitar stem looks structurally similar to a legitimate strong target stem. A spectral-overlap gate alone cannot safely identify it as false.

## Missed-target counterexamples

Some genuinely present targets are almost absent in the separator output:
- S0M03 guitar raw SI-SDR ~-14.84 dB; stem ~-97.7 dB vs mixture
- S0M11 bass raw SI-SDR ~-14.08 dB; stem ~-84.9 dB vs mixture

These look like absent-target stems even though the target actually exists.

Therefore:
- low separator energy does not prove target absence;
- high target-dominance does not prove target presence;
- spectral competition alone cannot distinguish hard false positives from legitimate isolated stems.

## Decision

Do not create a V2 cleanup threshold from these metrics alone.

The next gate should combine:
1. separator-output diagnostics;
2. an independent guitar/bass/other recognizer applied to the separated stem;
3. optionally target-note evidence from transcription after the recognizer stage.

Proposed logic:
- if separator output is near-silent: leave it alone and mark low-confidence;
- if recognizer strongly agrees with the claimed stem class: preserve raw stem by default;
- if recognizer disagrees strongly and competing stem evidence is high: allow conservative cleanup/reassignment;
- if recognizer is uncertain: preserve raw stem and flag for downstream uncertainty rather than destructive cleanup.

S0M10 becomes the key false-positive development fixture for this recognizer-gated approach.

No new cleanup thresholds are authorized by this diagnostic result.
