# V7 Synthetic Event-Timing Adequacy Result V1

Date: 2026-09-29  
Status: **V7A COMPLETED — NO TIMING ARM ADVANCES; NO TRAINING RUN**

## Corrected comparison population

The first local V7A summary accidentally included the 21 negative-only synthetic clips in the onset-density denominator.

That bookkeeping error was corrected before freezing the scientific result.

The corrected V7A population matches V6C:
- **273 positive synthetic clips**
- **546.0 seconds**
- **903 positive onset references**

No V7 rule, timing parameter, or advancement criterion changed.

## V7A model-free timing screen

| Arm | Onsets/s | IOI p50 | IOI p90 | <=250 ms | >=700 ms | Fallbacks | Timing distance | Advances |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| E0 | 1.6538 | 0.3400 | 0.4000 | 26.67% | 6.67% | 0 | 1.1331 | baseline |
| E1 | 1.6538 | 0.1822 | 0.4000 | 60.48% | 4.44% | 0 | 1.0243 | No |
| E2 | 1.6538 | 0.3400 | 0.4000 | 26.67% | 6.67% | 94 | 1.1331 | No |
| E3 | 1.6538 | 0.1812 | 0.4000 | 60.48% | 8.41% | 57 | 1.0282 | No |

Frozen V2B targets:
- 1.4906 onsets/s
- IOI p50 0.2560 s
- IOI p90 0.8824 s
- repeated attacks <=250 ms: 47.02%

## Why the arms failed

**E1** successfully creates more short-gap repetition, but overshoots the real target to 60.48%. It does not improve the long-tail p90 at all.

**E2** cannot establish the frozen 700–1100 ms tail often enough inside the fixed 2-second clips. The deterministic clip-boundary guard falls back **94 times**, leaving its p90 unchanged at 0.400 s.

**E3** combines the same short-gap overshoot with **57** boundary fallbacks. Its >=700 ms fraction rises somewhat, but the 90th percentile remains 0.400 s, so it fails the long-tail criterion.

No arm improves timingDistance by the required 30%, no arm improves repeated-attack absolute error by the required 0.10, and no arm improves IOI-p90 absolute error by the required 0.20 s.

## Result

**No non-baseline V7 timing arm advances.**

Therefore:
- V7B paired training does not run;
- V7C synthetic sanity does not run;
- V7D V2B model evaluation does not run;
- optimizer steps: **0**;
- model inference: **0**.

## Supported interpretation

The frozen two-second synthetic clip format is itself a constraint on representing the V2B timing distribution.

The current short-gap intervention can create more repeated attacks but overshoots them, while the declared long-tail intervention cannot reliably fit 700–1100 ms adjacent gaps alongside the existing events within two-second clips.

This means the next timing experiment should not merely alter interval sampling inside the current fixed 2-second templates. It would need a prospectively redesigned **longer-duration synthetic event curriculum / clip structure**, or a fresh real-domain training study.

No causal claim about longer clips is yet established because V7 stopped before training.

## Boundaries preserved

V1.1 remains sealed. No threshold, loss, renderer, architecture, decoder, or production changes occurred. P1/P2/P3 and A2 remain closed.
