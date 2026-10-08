# Guitar-TECHS post-V9 fixed output-admission audit — VERIFIED RESULT AND DECISION V1

**2026-10-08 · `astra-work` · one authorized diagnostic only · scientific V9 outcome: FAIL (unchanged)**

## Outcome

**The cause of zero decoded events is now localized to V9's state output failing the frozen V4 decoder's admission conditions.** Across **all 256 original P1/P2 development capture views**, both selected V9 epoch-20 models produced **zero active state argmax positions, zero strong/confirmed start candidates, zero accepted starts, zero V4 active runs before gap merge, zero V4 active runs after pruning, and zero V8 decoded note events**. Both frozen V7 representation / V8 decoder comparators on the **same captures** emitted substantial notes and reproduced their historical frozen F1 exactly. The training-time origin of this V9 output behavior remains **unproven**.

This corrects the preceding evidence review's necessary uncertainty: zero F1 *alone* could not establish zero emissions, but the newly authorized fixed forward-pass audit independently confirms zero V9 decoded events on the exact **selected** checkpoints and full-development validation captures. **Do not extrapolate to unexamined V9 checkpoints or an independent holdout.**

## Execution/provenance verified

- Single-use launch commit `16c6a2e7f61bf36103983b32eed4a1c1b98a534e`, isolated Actions workflow `.github/workflows/guitar-techs-post-v9-fixed-output-admission-audit-v1.yml`.
- [GitHub Actions run 37836761676](https://github.com/dadrockyt-sys/dadrock-tabs-android/actions/runs/37836761676), job `113515647380`: **completed SUCCESS**, one attempt, 2026-10-08 20:04:54–21:44:12 UTC (~99 min 18 sec; below 120-min bound). All steps successful, including source/authorization checks, pinned CPU dependencies, model-free admission fixtures, exact model ZIP+checkpoint SHA-256 checks, eight exact P1/P2 archive checks, fixed inference, upload and purge. Logs include `POST_V9_MODEL_FREE_ADMISSION_FIXTURES_PASS`, four `VERIFIED_FROZEN_MODEL` lines and `POST_V9_FIXED_OUTPUT_ADMISSION_AUDIT_PASS`. The workflow includes no optimizer training.
- Result artifact **`11580776876`**, name `guitar-techs-post-v9-fixed-output-admission-v1`, GitHub archive digest **`sha256:3e7d59b40d6311c800a0a5ee85f4ef90a38a0f8d6a17351578108f292604079b`**, downloaded and independently SHA-256 checked; unexpired at review. ZIP contains `post-v9-admission-audit-v1.json`; extracted bytes independently SHA-256 verified as **`5dbc876c3b77be3dff1f42b52e33f1955a8b96356aff08452e2fa9116aab6f94`**, matching the run log. **Do not check the 1.18 MB per-capture audit JSON into Git; it remains in the existing GitHub artifact.** Local inspection of that JSON verified the counts, output probability summaries, metric reproduction and explicit zero-training/closed-gate flags.
- Exact original validation population **P2=120 captures / 40 performances** for P1-trained models, **P1=136 captures / 41 performances** for P2-trained models; manifest SHA-256 `2b6851a5c0f1639f84df987372985e4d26ca34ad9e281d84f8c686531fdccf4c`. Identical labels, preprocessing, V4 admission thresholds, V8 event-backshift decoder and metric implementation per version; no threshold sweep, checkpoint re-selection or additional seed.
- V9 selected epoch-20 artifact/model pairs: P1 artifact `11516113677`, model SHA-256 `a62cb31bcfaa238965e0f79934a00c430c0b8723a4d51168104ddea5e4a0f90c`; P2 artifact `11572256759`, SHA-256 `6bb66bebb074f5b26ccaefd2ed2322eefed9381998f7cce81246f4ab5af40452`. V8 clean comparators use frozen V7 checkpoint artifacts `11336573510` (P1, epoch 1000) and `11374640369` (P2, epoch 940). ZIP/model SHA-256 checks passed **in job logs** before deserialization. These are original frozen checkpoints, not alternate selections.
- Run's `guards`: `optimizerStepsExecuted: 0`, `thresholdSweep: false`, `p3Opened: false`, `protectedSongUsed: false`, `stageBHoldoutUsed: false`, `paidCompute: false`, `productionOrMainChanged: false`. **These are pipeline receipts**, alongside observable Actions provenance; no cross-system product readiness or commercial-rights inference.

## Actual measured event counts (full-development capture totals; not the performance-weighted F1 denominators)

| Train→validate | Model | Reference events | Predicted events | True positives | Active V4 runs before merge | Active V4 runs after pruning | F1 (frozen aggregation) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P1→P2 | **V9** | 22,092 | **0** | **0** | **0** | **0** | **0.000000000000** |
| P1→P2 | frozen **V8** | 22,092 | 29,026 | 8,044 | 30,125 | 28,972 | 0.29305451541821204 |
| P2→P1 | **V9** | 27,071 | **0** | **0** | **0** | **0** | **0.000000000000** |
| P2→P1 | frozen **V8** | 27,071 | 37,744 | 7,201 | 39,763 | 37,718 | 0.20055717289380845 |

All **120/120 P2** and **136/136 P1** captures had **zero V9 predictions**. V8 emitted predictions on **every** capture. Total reference events: **49,163**; frozen V8 decoded predictions: **66,770** and TP **15,245**; V9 decoded predictions and TP **zero**. *The table's F1 values reproduce historical macro-over-performances fold metrics, not F1 recomputed by pooling these event totals.* V8 V4-run counts can differ from scored predicted-event counts because V8 backshifts and reference masking occur before metric extraction.

**Admissibility check, also from the saved artifact:**

| Train→validate | V9 maximum active-fret probability across all captures/frames/strings | V9 minimum silence probability | V9 count of strong-start candidates | Confirmed-start candidates | Active state argmax positions |
| --- | ---: | ---: | ---: | ---: | ---: |
| P1→P2 | 0.05293658375740051 | 0.1246638298034668 | 0 | 0 | 0 |
| P2→P1 | 0.053568027913570404 | 0.13096217811107635 | 0 | 0 | 0 |

Across each fold, **even the largest active-fret probability remained below the smallest silence probability**. All 11,548,830 V9 frame/string positions chose silence as class argmax. Thus neither the frozen ≥0.55 strong-start condition nor ≥0.42 two-frame confirmed start could be satisfied. The V8 event head can backshift only *already admitted* V4 active runs. Event-rank rescaling cannot correct this zero-admission condition.

## Output-distribution interpretation and remaining causal unknowns

The V9 state distribution is near-uniform among active classes with a modest but universal silence preference, rather than high-confidence silence (P1→P2 median-across-capture median of max-active probabilities ~0.05091, silence ~0.15109, state entropy ~2.96220 nats; P2→P1 analog ~0.05107, ~0.14771, ~2.96743 nats). Class maximum entropy `ln(21)≈3.04452` nats. Report these as **state-head output measurements**, **not proof of collapsed hidden representations**, weights, gradients, or the cause.

Prior independent source finding remains: V9 symmetric-KL `batchmean` over `B×200×6×21` divides by batch, so the applied weight `0.10` is effectively **120× a per-position-mean KL**; log source does not report KL/supervised component magnitudes or gradient ratios. Feature-space gain/tilt/noise/window masking may also matter. Neither mechanism can be assigned causality from these final output summaries.

## Decision and explicit handoff

**Scientific result:** Frozen V9 gate remains **FAIL**; failure mode **OUTPUT_STATE_ADMISSION_COLLAPSE_CONFIRMED_AT_SELECTED_CHECKPOINTS** (descriptive, not a learned-representation or training-causality proof). V8's clean-development reference macro F1 **0.24680584415601026** remains the strongest Guitar-TECHS clean combination for this specific evaluation. Reproduced fold F1 and capture counts show an output-admission failure, **not** a universal issue with the frozen V8 decoder.

**Next smallest scientific investigation recommended:** design a **separate prospective, strictly synthetic/no-media V9 objective audit** using the exact composite loss and batch/sequence dimensions to log and compare supervised component losses, weighted KL magnitudes and per-term gradients under fixed synthetic state/logit distributions. Explicitly test the established 1,200× reduction effect and feature-space transform semantics. This audit must distinguish expected numerical imbalance from empirically demonstrated training causation. Do **not** change frozen V9 code/results, relabel a changed objective as a mere orchestration fix or launch optimizer training as an unapproved continuation. A real-data or V10 study must be independently scoped and authorized.

**Stop:** The single authorized post-V9 P1/P2 forward-pass audit is **completed and consumed**. No automatic repeat, decoder-threshold rescue, alternative selected checkpoint, new optimizer study, protected-song/P3/Stage-B holdout access, paid compute, Production or `main` change. Preserve Go My Way quantized candidate, spectral-bass baseline, Stage-B and the unresolved `guitar-fl.pth` training-lineage/product rights gate. Keep all frozen receipts unchanged. Update two handoffs to point here, verify remote content, and wait for a distinct future decision on the next scientific study.
