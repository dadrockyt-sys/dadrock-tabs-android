# PRE-V9 common-unit measurement V1

Date: 2026-09-29 UTC  
Status: **REFERENCE COMPLETE — NO V9 CANDIDATE GENERATED**

This step uses committed V2B records and the retained V8 L0 source template only. No original audio was read or decoded. No annotation was added or changed. No model, inference, optimizer, renderer, candidate V9 timing population, launch marker, or workflow was run.

## Frozen prospective measurement contract

- timing unit: **acoustic attack group**
- note/string/fret labels remain a separate unit
- simultaneous grouping tolerance: **10 ms**
- time origin: frozen evaluation-crop local time
- duration: exact corrected evaluation duration where an overlay exists
- endpoint: **half-open [0, duration)**
- IOI: positive difference between consecutive attack groups within the same clip
- `repeat250`: fraction of eligible positive IOIs <= 0.250 s
- long-gap statistic: fraction of eligible positive IOIs >= 0.700 s
- positive density denominator: positive evaluation seconds only
- negative/background-only duration: reported separately
- quantiles: linear interpolation at `h=(n-1)*p`, matching the NumPy default linear convention
- empty/singleton clips: zero IOIs; repeat fraction undefined
- real V2B landmarks are not assigned inferred chord multiplicity or family labels

Historical V6/V7/V8 metrics remain frozen under their original contracts.

## V2B reference under the common unit

The 10 ms grouping rule merges **0 of 164** committed spectral-flux landmarks, so the V2B timing values remain numerically unchanged:

| Metric | V2B common-unit reference |
|---|---:|
| Positive clips | 13 |
| Negative clips | 4 |
| Positive seconds | 110.023183673 |
| Negative seconds | 31.857959184 |
| Raw onset landmarks | 164 |
| Acoustic attack groups | 164 |
| Attack-group density | 1.490594932/s |
| Eligible positive IOIs | 151 |
| IOI p10 | 0.106667 s |
| IOI p50 | 0.256000 s |
| IOI p90 | 0.882358 s |
| repeat250 | 47.0199% |
| long-gap >=700 ms | 12.5828% |

These are detector-landmark statistics, not exhaustive human-verified audible-attack truth.

## V8 L0 reference remeasured as attack groups

The retained V8 source has 903 note-level timestamps in 273 positive 2-second clips. After simultaneous note multiplicity is collapsed into acoustic attack groups:

| Metric | Historical note-level V8 L0 | Common-unit V8 L0 |
|---|---:|---:|
| Positive clips | 273 | 273 |
| Positive seconds | 546 | 546 |
| Note timestamps / attack groups | 903 | **735** |
| Density | 1.653846/s | **1.346154/s** |
| Clip-rate p50 | 2.0/s | **1.0/s** |
| Clip-rate p90 | 3.0/s | **2.5/s** |
| IOI p10 | 0 | **0.340 s** |
| IOI p50 | 0.340 s in V7/V8 source summary | **0.360 s** |
| IOI p90 | 0.400 s | **0.400 s** |
| repeat250 | 26.6667% | **0%** |
| long-gap >=700 ms | 6.6667% | **9.0909%** |

The 903 -> 735 difference is **168 simultaneous note labels**, all from the chord templates. Forty-two chord clips contain six note-level timestamps but only two acoustic attack groups each.

Under the corrected common unit, the frozen 2-second baseline is about **9.69% lower** than V2B in aggregate attack density, has a p50 IOI **104 ms longer**, a p90 **482 ms shorter**, no <=250 ms successive attack gaps, and a slightly smaller >=700 ms fraction.

This materially changes the interpretation of the historical scalar: the old 26.67% synthetic "repeat" statistic was driven by chord multiplicity rather than distinct successive attacks.

## Synthetic per-family identity

| Family | Positive clips | Note labels | Attack groups | IOIs |
|---|---:|---:|---:|---:|
| isolated | 42 | 42 | 42 | 0 |
| scales | 42 | 168 | 168 | 126 |
| chords | 42 | 252 | **84** | 42 |
| repeated | 42 | 168 | 168 | 126 |
| legato | 42 | 42 | 42 | 0 |
| palmmute | 42 | 210 | 210 | 168 |
| mixed-positive | 21 | 21 | 21 | 0 |
| **total** | **273** | **903** | **735** | **462** |

The family names are synthetic construction labels only; they are not projected onto V2B.

## Pitch-reference denominator provenance resolved

The earlier audit marked the 57/50 -> 56/49 scoring change unresolved. A committed record does resolve it:

`docs/astra/V2C_CALIBRATION_DIAGNOSTIC_RESULT_V1.json` records one unrepresentable landmark excluded from scoring:

- clip **C06**
- time **0.042667 s**
- MIDI pitch **37**
- confidence **high**

Therefore:
- raw trusted landmarks 57 -> scorable trusted refs **56**
- raw high-confidence landmarks 50 -> scorable high-confidence refs **49**

No denominator is inferred or changed in this review; this is a provenance reconciliation from the already committed V2C record.

## Focused checks

Existing pure contract fixtures previously passed **10/10**.

For this measurement step, six additional pure checks passed against the frozen formulas/template reconstruction:
- three-note simultaneous chord grouping;
- distinct 180 ms attacks remain distinct;
- declared linear quantile convention;
- 273 positive synthetic clips;
- 903 note labels -> 735 attack groups;
- 462 positive IOIs with zero <=250 ms successive gaps.

A network clone attempt was unavailable in the execution environment, so the six checks were run locally against the exact frozen formulas/templates rather than through a remote workflow. No workflow was dispatched.

## Historical provenance limitation

V6 reports synthetic p50/p90 0.3482993197/0.4179591837 s, while retained V7/V8 source-template summaries use 0.34/0.40 s. The exact full V6 timing orchestration source was not found in the active synthetic directory, and the V7 timing-screen source is represented by a recorded script hash/manifests rather than a retained active source file.

Therefore the common-unit synthetic comparator in this result is explicitly the **retained V8 L0 source template**, not a claim to have reconstructed V6.

## Readiness decision

**Common-unit reference comparability is now resolved enough to proceed to final V9 contract preparation, but V9 empirical execution is still not authorized.**

Before any V9 candidate timing output is generated, the final V9 spec must prospectively freeze:
- one 4-second generator package only;
- exact gap supports/mixture weights from this corrected reference;
- exact attack-group count/content distribution;
- sustain/offset supports;
- numerical timing gates and any distance weights/scales;
- same-runtime comparator identity;
- train/test split identities;
- RNG seed/hash identity;
- render/inference/CPU/storage ceilings;
- two-model / 1,000-step maximum;
- consumed launch scope, no retry, fail-if-output-exists, and durable result retention.

Then stop for the user's explicit empirical V9 authorization. No candidate timing arm should be generated before that decision.
