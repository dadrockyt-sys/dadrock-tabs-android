# Post-A1 supervisory evidence review V1

Date: 2026-09-28  
Status: **MODEL-FREE EVIDENCE RECONCILIATION COMPLETE — A1 REMAINS FAILED AND CLOSED**

## Scope and provenance

This review starts from branch head `983ef1f2efd5701d709545ec3b76826622f75746` and does not run or instantiate a model. It reconciles the frozen A1 and V3 records, downloads only their already-produced GitHub Actions result artifacts, and parses their result JSON.

Artifact identity was checked against GitHub's reported metadata and the frozen result summaries:
- A1 artifact **11002106213**: GitHub-reported digest `sha256:ed013e7d35237f7b6d998a742b7cac45116d1b8ceb038400dc81edc4947b2054`; downloaded `result.json` SHA-256 **090f0718b3da1cad6c1913af6d2113d18386dfc0323e77c846c509de00abb1c3**, exactly matching the frozen A1 record.
- V3 training artifact **11000187208**: GitHub-reported digest `sha256:84f2566c656c37d5fe20bdc26bfdaa699d5e2c4089c0c91f99434d8f0282e3f3`; downloaded `result.json` SHA-256 **5b5b9be61196d6e40abb2182f5dd0cff4b21f7c9fe927592324bc20df471f36d**, exactly matching the frozen V3 record.

No training dataset, audio, weight file, inference, optimizer, renderer, threshold search, workflow dispatch, P1/P2, or P3 was used.

## Metric definitions

- **State admission:** on each positive reference string-frame at an onset, the most probable active fret must equal the reference fret, true-fret probability must be >= **0.50**, and true-fret probability must exceed silence probability. The metric is passing frames divided by positive reference string-frames.
- **Joint admission:** same population, requiring both state admission and onset sigmoid probability >= **0.50**.
- **Pitch-onset precision/recall/F1:** event-level aggregate from the unchanged frozen scorer. Precision = TP/(TP+FP), recall = TP/(TP+FN), and F1 is their harmonic mean.
- **Negative-only FP/sec:** raw decoded predictions on negative-only test clips divided by negative-only duration. Here ordinary is **6 s** per seed and challenge is **12 s** per seed.

Ordinary population: **42 test examples, 129 positive reference string-frames** per seed. Challenge population: **84 test examples, 258 positive reference string-frames** per seed.

## Comparator evidence

### Ordinary — A1 versus Frozen S11 intervention

| Seed | Comparator state | A1 state | Δ state | Comparator joint | A1 joint | Δ joint | Comparator onset P/R/F1 | A1 onset P/R/F1 | Δ P/R/F1 | Comparator TP/FP/FN | A1 TP/FP/FN | Comparator neg FP / sec | A1 neg FP / sec |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 20260927 | 0.263566 | 0.387597 | 0.124031 | 0.248062 | 0.286822 | 0.038760 | 0.877551/0.666667/0.757709 | 0.943820/0.651163/0.770642 | 0.066269/-0.015504/0.012933 | 86/12/43 | 84/5/45 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |
| 20260928 | 0.333333 | 0.418605 | 0.085271 | 0.279070 | 0.310078 | 0.031008 | 0.871287/0.682171/0.765217 | 0.842593/0.705426/0.767932 | -0.028695/0.023256/0.002715 | 88/13/41 | 91/17/38 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |
| 20260929 | 0.255814 | 0.325581 | 0.069767 | 0.255814 | 0.302326 | 0.046512 | 0.785124/0.736434/0.760000 | 0.925926/0.775194/0.843882 | 0.140802/0.038760/0.083882 | 95/26/34 | 100/8/29 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |

### Challenge — A1 versus Frozen S11 intervention

| Seed | Comparator state | A1 state | Δ state | Comparator joint | A1 joint | Δ joint | Comparator onset P/R/F1 | A1 onset P/R/F1 | Δ P/R/F1 | Comparator TP/FP/FN | A1 TP/FP/FN | Comparator neg FP / sec | A1 neg FP / sec |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 20260927 | 0.317829 | 0.383721 | 0.065891 | 0.263566 | 0.282946 | 0.019380 | 0.862944/0.658915/0.747253 | 0.917127/0.643411/0.756264 | 0.054183/-0.015504/0.009011 | 170/27/88 | 166/15/92 | 0 / 12s = 0.000000 | 0 / 12s = 0.000000 |
| 20260928 | 0.352713 | 0.476744 | 0.124031 | 0.298450 | 0.348837 | 0.050388 | 0.783186/0.686047/0.731405 | 0.890995/0.728682/0.801706 | 0.107809/0.042636/0.070301 | 177/49/81 | 188/23/70 | 2 / 12s = 0.166667 | 0 / 12s = 0.000000 |
| 20260929 | 0.298450 | 0.325581 | 0.027132 | 0.279070 | 0.294574 | 0.015504 | 0.762712/0.697674/0.728745 | 0.872727/0.744186/0.803347 | 0.110015/0.046512/0.074602 | 180/56/78 | 192/28/66 | 1 / 12s = 0.083333 | 0 / 12s = 0.000000 |

### Ordinary — A1 versus Frozen S11 control

| Seed | Comparator state | A1 state | Δ state | Comparator joint | A1 joint | Δ joint | Comparator onset P/R/F1 | A1 onset P/R/F1 | Δ P/R/F1 | Comparator TP/FP/FN | A1 TP/FP/FN | Comparator neg FP / sec | A1 neg FP / sec |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 20260927 | 0.325581 | 0.387597 | 0.062016 | 0.310078 | 0.286822 | -0.023256 | 0.845361/0.635659/0.725664 | 0.943820/0.651163/0.770642 | 0.098459/0.015504/0.044978 | 82/15/47 | 84/5/45 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |
| 20260928 | 0.410853 | 0.418605 | 0.007752 | 0.341085 | 0.310078 | -0.031008 | 0.857143/0.651163/0.740088 | 0.842593/0.705426/0.767932 | -0.014550/0.054264/0.027844 | 84/14/45 | 91/17/38 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |
| 20260929 | 0.348837 | 0.325581 | -0.023256 | 0.333333 | 0.302326 | -0.031008 | 0.812500/0.705426/0.755187 | 0.925926/0.775194/0.843882 | 0.113426/0.069767/0.088695 | 91/21/38 | 100/8/29 | 0 / 6s = 0.000000 | 0 / 6s = 0.000000 |

### Challenge — A1 versus Frozen S11 control

| Seed | Comparator state | A1 state | Δ state | Comparator joint | A1 joint | Δ joint | Comparator onset P/R/F1 | A1 onset P/R/F1 | Δ P/R/F1 | Comparator TP/FP/FN | A1 TP/FP/FN | Comparator neg FP / sec | A1 neg FP / sec |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 20260927 | 0.333333 | 0.383721 | 0.050388 | 0.317829 | 0.282946 | -0.034884 | 0.713675/0.647287/0.678862 | 0.917127/0.643411/0.756264 | 0.203452/-0.003876/0.077402 | 167/67/91 | 166/15/92 | 2 / 12s = 0.166667 | 0 / 12s = 0.000000 |
| 20260928 | 0.379845 | 0.476744 | 0.096899 | 0.325581 | 0.348837 | 0.023256 | 0.700000/0.651163/0.674699 | 0.890995/0.728682/0.801706 | 0.190995/0.077519/0.127007 | 168/72/90 | 188/23/70 | 2 / 12s = 0.166667 | 0 / 12s = 0.000000 |
| 20260929 | 0.364341 | 0.325581 | -0.038760 | 0.333333 | 0.294574 | -0.038760 | 0.652015/0.689922/0.670433 | 0.872727/0.744186/0.803347 | 0.220713/0.054264/0.132914 | 178/95/80 | 192/28/66 | 2 / 12s = 0.166667 | 0 / 12s = 0.000000 |

## Reconciled findings

A1 remains a scientific **FAIL** under its frozen prospective contract. It missed the mean ordinary joint-admission gain floor versus S11 intervention: **+0.0387597 observed vs >= +0.0400000 required**, and challenge recall versus S11 clean control was positive in **2/3**, not 3/3, seeds.

The favorable intervention-relative evidence is real but narrower than the prior mechanism wording implied. A1 improves ordinary state admission versus the source-domain-trained S11 intervention in all seeds and improves ordinary joint admission in all seeds. On the challenge it also improves state/joint admission and onset F1 versus that intervention. However, against the clean S11 control, ordinary joint admission remains lower in **all three seeds**: -0.023256, -0.031008, and -0.031008.

The architecture comparison is confounded by capacity and initialization. The inspected S11 definition has **156,548** trainable parameters; A1 has **279,556**, an increase of **123,008 (78.6%)**. The same run seed is retained and A1 reuses the exact frozen batch-plan hashes, but A1 initializes an additional encoder before the downstream heads. Therefore the same seed does **not** imply paired common-tensor initialization. The supported statement is: the dual-encoder package improved several metrics on these fixed synthetic data; sharing, capacity, and initialization effects were not separated.

The negative-only result is bounded evidence, not a real-world false-positive claim. A1 produced **0 decoded events** over **6 ordinary negative-only seconds** and **0 decoded events** over **12 challenge negative-only seconds** in every seed. The V3 clean controls had 2 challenge negative-only events over 12 seconds in every seed, while the V3 source-domain intervention had 0, 2, and 1 events respectively.

The V3 challenge and ordinary S9 test populations have been repeatedly exposed to project decisions. Their fixed reuse improves comparability, but they are development benchmarks rather than independent confirmation. The earlier V3 training gate and later A1 architecture gate ask different questions; A1's narrower recall guard cannot retroactively turn the failed V3 system gate into a pass.

## Pins and controls: verified versus declared

Verified from committed source/results and the downloaded artifacts:
- exact A1 result JSON hash and exact V3 comparator result JSON hash;
- A1 control/intervention/challenge file identities recorded as `16123b...`, `a17a16...`, `368032...` and comparator result identity `5b5b9b...`;
- seeds exactly 20260927/28/29;
- A1 batch-plan hashes exactly match the frozen V3 intervention plans per seed;
- A1 result contains exactly three rows, each reporting 500 optimizer steps, total 1,500;
- thresholds fixed at 0.50/0.50 with no search/retuning;
- A1 runner blob `c88fab40...`, tests blob `683006f8...`, S11 source blob `d4aacc40...`, design/spec blobs recorded in the passed offline verification receipt;
- parameter counts from the inspected layer definitions: S11 156,548; A1 279,556.

Declared by frozen execution receipts rather than independently replayed in this review:
- no hidden optimizer work before the recorded execution;
- P1/P2/P3 access flags, production mutation flags, and runtime ceilings beyond the recorded receipts;
- dataset/audio semantic correctness beyond their frozen hashes and committed preparation records;
- GitHub artifact digest provenance is GitHub-reported metadata; this review independently re-hashed the contained result JSON, not the platform's artifact-digest construction.

## Prospective validation gap

A1's frozen result stays immutable. For later experiments, validation should fail closed on result structure: exact unique seeds/rows, expected model/step totals, complete finite numbers, fractional metrics in [0,1], nonnegative FP counts/rates/durations, internally consistent FP rates, deltas recomputed from absolute operands, and exact expected identities. Booleans must not be accepted as numeric values. Missing evidence must be reported separately from a scientific gate failure.

A separate pure-Python validator and focused unit tests accompany this review. They are prospective only and are **not** retrofitted into A1 or V3.

## Decision brief

**What the evidence establishes:** on the fixed synthetic development populations, A1's dual-encoder package improves multiple state/joint/onset measurements versus the source-domain-trained S11 intervention, with zero negative-only decoded events in its bounded samples. A1 nevertheless fails its own gate, and its ordinary joint admission is below the clean S11 baseline in every seed.

**What remains uncertain:** whether harmful encoder sharing itself caused the earlier tradeoff once the **78.6% capacity increase** and changed initialization order are controlled; and whether any observed synthetic gain transfers to independent real guitar audio or to full product requirements such as offsets, playable fingering, and part separation.

**Smallest resolving evidence:** for product relevance, the most direct next evidence is a prospectively frozen **independent real-development evaluation** that is not P3 and is not a silent reuse of closed P1/P2. That requires a new explicit access/evaluation authorization. A capacity/initialization-controlled architecture-identification study would answer the narrower causal architecture question, but would not by itself resolve real-domain readiness.

**Recommendation:** **pause model research at this boundary.** If the user opens a new project, prioritize independent real-development evidence before spending another synthetic architecture iteration. Do not open that program from this review alone.

## Authorization boundary

No A2 is opened. P1/P2 remain closed. P3 remains sealed. Main/Production remain unchanged. No new model, optimizer, inference, renderer, launch marker, or workflow dispatch is authorized by this review.
