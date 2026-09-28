# Astra P1/P2 transfer failure analysis V1

Date: 2026-09-28

## Outcome

The prospective transfer evaluation completed successfully as a workflow and failed scientifically.

### P1 compatibility context

Historical V3 baseline:
- 16 TP / 7 FP / 0 FN;
- precision 0.6957;
- recall 1.0000;
- F1 0.8205;
- onset+offset F1 0.9375;
- repeated-attack recall 1.0000;
- true positives in 4/4 examples.

Synthetic S9/S11 candidate:
- 0 TP / 10 FP / 16 FN;
- precision 0;
- recall 0;
- F1 0;
- onset+offset F1 0;
- repeated-attack recall 0;
- true positives in 0/4 examples.

The candidate still emitted events on P1 (10 false positives), so this is not simple total decoder silence on P1. The events did not match the real references.

### P2 primary transfer population

Historical V3 baseline:
- 0 TP / 0 FP / 15 FN;
- F1 0.

Synthetic candidate:
- 0 TP / 1 FP / 15 FN;
- F1 0;
- true positives in 0/4 examples.

The frozen P2 transfer gate failed 0/5 criteria.

## What this establishes

The synthetic candidate does **not** transfer to the real prepared feature domain.

Because it also fails completely on P1 while the historical V3 baseline remains strong on P1, the synthetic candidate's problem cannot be described as merely a P1-to-P2 performer shift.

The synthetic sequence did learn internally useful structure, but that competence did not survive contact with the real feature distribution.

## What this does not establish

This run does not isolate the dominant mechanism. Live possibilities include:
- synthetic-vs-real CQT feature distribution mismatch;
- synthetic attack/sustain acoustics that teach non-real cues;
- state/onset probability calibration collapse;
- wrong real pitch-state identity despite event activity;
- interaction between five-frame context and real feature scale/statistics.

No threshold rescue is justified: the candidate produced wrong/unmatched P1 events and essentially no useful P2 events.

No seed selection is justified after seeing P1/P2.

## Decision

Reject the current synthetic candidate for real-development advancement.

Keep P3 sealed.

Do not reopen synthetic architecture/loss/sampler tuning directly from these eight real examples.

The next defensible step, if separately authorized, is a **zero-optimizer domain diagnostic** that compares frozen synthetic, P1 and P2 feature/output distributions for the exact candidate and baseline without changing thresholds or weights.
