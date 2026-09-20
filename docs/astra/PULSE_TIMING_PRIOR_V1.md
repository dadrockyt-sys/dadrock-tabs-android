# Audio-only pulse timing prior V1

`astra_backend/evaluation/build_pulse_timing_prior.py` turns the preserved audio-only pulse evidence into a fail-closed timing **prior**. It never reads model predictions or professional reference labels, never selects a downbeat, and cannot create a scorer-admissible alignment.

The utility validates the evidence identity and pulse ordering, computes the median inter-pulse interval and median absolute deviation, then flags only intervals whose deviation exceeds both a robust-MAD threshold and three analysis frames. Clearly irregular intervals split the pulse train into contiguous stable runs. Each run receives a simple least-squares pulse-period fit with BPM and residual diagnostics. These are tracker diagnostics, not measures, quarter-note labels, tempo-map approval or musical truth.

For the frozen Gomyway evidence, the 33 detected pulses yield a median interval of `0.47600907029478456 s` (`126.04801829268293 BPM`). Three intervals are flagged: pulse 0→1 (`0.5050340136054421 s`) and the pair around 14.3–14.8 seconds (`0.37732426303854716 s`, `0.5456689342403642 s`). The long stable run from pulse 1 through pulse 29 fits `0.4736641980273226 s` per pulse (`126.67201838324075 BPM`) with RMS residual `0.006305532194394071 s`. This closely agrees with, but does not replace, the earlier independent `.5–12 s` regression (`126.64633155575919 BPM`).

The opening observations remain deliberately separate: first RMS activity `0.058049886621315196 s`, first detected onset `0.11029478458049886 s`, first observed pulse `0.1219047619047619 s`. None is promoted to measure 1. The report emits an empty `candidateDownbeats` list, `measureOneStartVerified: false`, `tempoMapVerified: false`, `reviewStatus: diagnostic-only`, and `customerDeliveryEligible: false`.

Generate the report with:

```sh
python astra_backend/evaluation/build_pulse_timing_prior.py \
  --evidence docs/astra/GOMYWAY_AUDIO_TIMING_EVIDENCE_V1.json \
  --output /private/GOMYWAY_PULSE_TIMING_PRIOR_V1.json
```

The output path is exclusive: an existing report is never overwritten. The timing prior is intended to guide the independent listening/source review by highlighting stable pulse regions and tracker irregularities; it must not be substituted for that review or fed directly to the scorer as a completed alignment.
