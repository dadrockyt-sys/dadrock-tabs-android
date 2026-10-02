# BS-Roformer S0 GitHub Actions Result V1

Date: 2026-10-02
Run ID: 37078702459
Branch: `astra-work`
Status: **SUCCESSFUL EMPIRICAL S0 RUN**

Artifact:
- name: `astra-s0-bs-roformer-result`
- artifact id: 11257653088
- artifact digest: `sha256:ff36972b6765f1c5e80b404558ef2417070536d6384b2638a36168bd82f20874`
- model SHA-256: `d3d2bac77a7023282cb5f35a5807179e34076b60589867b572275f1a8ec36444`

## Overall

- mixtures: **12**
- total wall time: **345.074 s**
- mean cleanup SI-SDR change across target-present guitar/bass stems: **-0.632 dB**
- minimum cleanup change: **-5.161 dB**
- maximum cleanup change: **+0.153 dB**
- conclusion: **current cleanup configuration FAILS as a general post-separator improvement**

The cross-stem cleanup that passed the earlier injected-bleed unit test does not transfer cleanly to real BS-Roformer outputs.

## Important examples

Strong raw separator cases:
- S0M01 guitar: 20.052 dB raw -> 19.453 dB cleaned
- S0M01 bass: 23.584 dB raw -> 23.183 dB cleaned
- S0M05 guitar: 34.022 dB raw -> 32.957 dB cleaned
- S0M05 bass: 23.654 dB raw -> 18.493 dB cleaned
- S0M06 guitar: 30.838 dB raw -> 30.388 dB cleaned
- S0M06 bass: 20.278 dB raw -> 17.839 dB cleaned

Current cleanup especially damaged:
- S0M05 bass: **-5.161 dB**
- S0M06 bass: **-2.438 dB**

Small positive cases:
- S0M03 guitar: +0.002 dB
- S0M04 bass: +0.027 dB
- S0M11 guitar: +0.118 dB
- S0M12 bass: +0.153 dB

## Leakage / absent-target clues

Where the target was absent:
- S0M07 bass raw energy ~6.36e-12, cleaned ~2.29e-12
- S0M08 guitar raw energy ~6.74e-12, cleaned ~2.43e-12
- S0M09 bass raw energy ~2.77e-12, cleaned ~9.97e-13
- S0M10 guitar raw energy **0.00493**, cleaned **0.00471**

This suggests:
- the separator is already extremely clean on several absent-target cases;
- S0M10 is a materially harder false-positive guitar case;
- a blanket cleanup mask is inappropriate because it harms strong target stems while only modestly reducing the hardest false-positive case.

## Reconstruction

Maximum reconstruction absolute error after cleaned stems + residual remained ~1.19e-07, so mixture-consistency math is behaving correctly.

## Decision

Freeze the current cleanup configuration as a **failed transfer experiment**.

Do not tune it blindly against the same 12 examples.

Next direction should be diagnostic:
1. inspect which competing stem dominates when cleanup harms the target;
2. measure cross-stem duplicate energy / spectral overlap before attenuation;
3. design a **gated cleanup** that activates only when there is evidence of real contamination;
4. use absent-target cases, especially S0M10, as a leakage-detection development target;
5. preserve high-SI-SDR raw stems untouched by default.

No production/commercial-song claim is supported by this S0 run.
