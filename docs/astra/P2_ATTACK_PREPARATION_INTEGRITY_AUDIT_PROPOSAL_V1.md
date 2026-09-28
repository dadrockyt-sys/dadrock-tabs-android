# Astra P2 attack/preparation integrity audit proposal V1

Date: 2026-09-28
Status: **DESIGN ONLY — NEW P2 ACCESS NOT AUTHORIZED**

## Purpose

Determine whether the shared P2 onset failure comes from:
- genuinely weaker P2 attack transients,
- capture/preprocessing differences,
- or annotation/source-to-crop alignment.

No model training or threshold changes.

## Inputs

Use only the exact four frozen P1 and four frozen P2 direct-input captures already used in the transfer/localization diagnostics.

P3 remains sealed.

## Measurements

For every eligible reference attack:
- raw-audio short-window RMS before/after attack;
- raw waveform first-difference energy;
- positive spectral flux from raw STFT;
- corresponding prepared-CQT frame-difference and flux;
- source annotation time;
- prepared crop-local annotation time;
- nearest raw transient peak offset;
- nearest CQT novelty peak offset;
- capture sample rate/channel metadata;
- crop start/end and resampling provenance.

Compare P1 vs P2 distributions using descriptive statistics only.

## Guards

- optimizer steps 0;
- model inference optional but not required;
- thresholds unchanged;
- no normalization or preprocessing changes;
- no threshold search;
- no model/seed selection;
- no P3;
- no production claim;
- no automatic retry.

## Decision branches

- **Raw P2 attacks are also weak:** capture/performance-domain mismatch is supported.
- **Raw attacks are strong but prepared CQT novelty is weak:** preprocessing/resampling representation mismatch is supported.
- **Novelty peaks are systematically offset from annotations:** alignment/crop timing is supported.
- **No clear discrepancy:** freeze as unresolved and do not tune on P2.

## Authorization boundary

Execution requires fresh explicit P1/P2 source access authorization.

P3 remains sealed.
