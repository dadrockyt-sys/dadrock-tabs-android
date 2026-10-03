# Duplicate Consolidation Safety Gate V1 — Result

Date: 2026-10-02  
Branch: `astra-work`

## GitHub Actions evidence

- Workflow: `Astra Duplicate Consolidation Safety Gate V1`
- Run: `37089667900`
- Head commit: `8e44afc86a81caedd9ec4dbf94f9a4a77ebf9a83`
- Artifact id: `11262196258`
- Artifact digest: `sha256:18ff6d8fae150b179e6fc666e28aff645e3680fe54ca92b83d077e7904b5f67c`

## Frozen prospective gate

Implementation:
- `astra_backend/evaluation/duplicate_consolidation_safety_gate_v1.py`
- `astra_backend/evaluation/evaluate_duplicate_consolidation_safety_gate_v1.py`
- `.github/workflows/astra-duplicate-consolidation-safety-gate-v1.yml`

The gate decision used separator-output/pair evidence only:
- zero-lag correlation
- bounded best-lag correlation and lag
- spectral shared/unique fractions
- low/high-band balance
- phase consistency
- frame-energy correlation
- time-varying energy-share swing
- existing frozen pair-classifier state and recognizer evidence

Ground-truth source audio was used only after the decision for retrospective SI-SDR scoring.

## Result

- Cases: **16**
- Frozen pair-classifier accuracy: **15/16 = 93.75%**
- Gate decisions:
  - `merge_safe`: **0**
  - `preserve_separate`: **16**
  - `uncertain`: **0**
- Automatic merges: **0**
- Minimum automatic action delta: **0.0 dB**
- Maximum automatic merge reconstruction error: **0.0**

Success criteria:
- pair classifier behavior preserved: **PASS**
- all four time-varying splits permitted to merge: **FAIL**
- all negative full-merge cases avoided: **PASS**
- no automatic action worse than -0.5 dB SI-SDR: **PASS**
- numerical reconstruction requirement for applied merges: **PASS**
- overall prospective gate: **FAIL**

## Important observations

All four time-varying split cases were safely rejected even though retrospective scoring shows very large merge gains:
- B01: +142.32 dB
- B08: +142.37 dB
- G09: +140.36 dB
- G14: +142.06 dB

Their V1 diagnostics showed a consistent pattern:
- zero-lag correlation about 0.79–0.83
- spectral shared fraction about 0.27–0.33
- phase consistency about 0.9999
- energy-share swing about 0.73

The frozen V1 rule required substantially higher waveform/spectral overlap, so it did not authorize them.

Every negative full-merge case was also rejected, including the largest losses:
- G14 delayed high-band leak: -3.06 dB
- G14 frequency partition: -2.89 dB
- B01 filtered + contamination: -1.97 dB

## Decision

**STOP automatic duplicate consolidation at V1.**

Do not retune the gate on this same 16-case development set. Doing so would convert the prospective evaluation into post-hoc fitting.

Keep:
- `PairClassifierConfig V1` frozen
- duplicate-class detection as diagnostic/flagging evidence
- consolidation disabled for automatic action
- real recordings untouched

Do not proceed to holdout or real-audio consolidation validation from this result.

A future restart of consolidation research should use a genuinely new hypothesis/rule family and a new development protocol rather than adjusting V1 thresholds against these observed outcomes.
