# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 00:43 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold-calibration work. Rhythm-first; do not begin Bass/Lead unless V144 quality is proven or the user explicitly redirects.**

## Product target
- `/ai-tab` product flow: upload audio → choose Rhythm/Bass/Lead → professional-quality PDF preview → optional purchase unlocks full professional PDF.
- Current engineering goal is a musically accurate professional Rhythm transcription, not merely a good scorer or renderer.
- Keep `/ai-tab` frontend behavior unchanged while the Rhythm engine/calibration protocol is being proven.

## Permanent V5 safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected analyzer must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` at `analyzer/v143_reference_free_rhythm_pipeline.py`.
- Frozen V5 final-result sentinel must remain Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7` at `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`.
- Frozen V5 render stream SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Frozen V5 PDF SHA256: `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`.
- Frozen canonical scorer/PDF event SHA256: `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Frozen V5 shape: 891 attacks / 1214 selected / 1209 rendered / 5 voicing drops / 113 measures; 967 baseline + 242 rescued; 21 technique events.
- Tempo remains exactly `129.19921875`.
- The original V5 professional one-shot holdout is permanently consumed. **Never dispatch/retry the V5 final workflow, change its trigger, modify its candidate/thresholds/result, or use later calibration results to retune V5.**
- Re-evaluating the immutable V5 bytes is permitted only as explicitly labeled **V144 calibration baseline** evidence; it is not a reopening or retry of the V5 protocol.
- Existing `freezeReady=false` sentinels remain false.
- No Modal/L4/GPU invocation without fresh explicit user authorization. None has been used in this V144 continuation.

## Historical V5 result — immutable diagnostic baseline
- V5 final workflow run `32919666736`; persisted by bot commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`.
- Final completion gate failed; Rhythm was not complete.
- Critical mismatches: `1875` = 1069 gross unmatched generated notes + 806 gross unmatched reference notes; missing reference measures `0`.
- PDF-event fidelity `1.0`; measure coverage recall `1.0`.
- Gated musical metrics:
  - pitch content F1 `0.2830626450116009`
  - pitch/timing tolerant F1 `0.044547563805104405`
  - string/fret/timing tolerant F1 `0.03062645011600928`
  - chord pitch-set tolerant F1 `0.022757697456492636`
  - exact voicing tolerant F1 `0.022757697456492636`

## V144 gold calibration target — verified and persisted
- Human-written visual target remains `main/public/Professionalexample.jpg`; `main` is read-only and untouched.
- Main-tree visual Git blob: `16106197cc1269cca0b3c443908d5ef75e8b4d3e`; verified image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Exact structured source SHA256: `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Exact built reference SHA256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 playable onsets / 946 playable notes / 104 populated measures.
- V144 semantics: this professional reference is a **gold calibration benchmark, not an unseen holdout**. Never claim unbiased generalization from scores against it.
- Provenance manifest: `debug/v144-rhythm-calibration/reference/professional-target-provenance.json` (commit `9d29ba53466b721ce99f0265524b089b883b5f63`).
- Exact V144 builder: `validation/v144_rhythm_calibration/build_gold_reference.py` (commit `2b0fb21245d5ef01d0a5b6e65c39fa2740df3e69`).
- CPU workflow: `.github/workflows/v144-build-gold-reference.yml`; ordering-only persistence fix commit `40fe83895ef76badde4409489a61b3c0a5a0fd1a`.
- Corrected build run `32934718066` = **SUCCESS**.
- Persisted reference bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f`.
- Persisted files:
  - `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`
  - `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference-build.json` (Git blob `5f1ec40176aa9b69676c7cd9e06b42c412731f37`).
- Build report explicitly records `gold-calibration-reference-not-unseen-holdout`, `v5Modified=false`, `productionModified=false`, `modalGpuInvoked=false`.

## V144 CPU policy/scaffold — green
Existing V144-only scaffold discovered on branch and preserved:
- `modal/v144_rhythm_context_split_policy.py` — commit `7b1edbe723943c3c397b29729a69841e95a151ea`.
- `modal/v144_rhythm_context_split_selector.py` — commit `ed1b8b3251f351e61113878ae7eb388700f76756`.
- `modal/configs/v144_rhythm_context_split_config.json` — commit `bd55ce88e9a62f5cdbd5c24615788e39f3753daf`.
- Synthetic fixture `modal/tests/fixtures/v144_rhythm_context_split_reference.json` — commit `bde9c8900ce8ead11acab2e7a8fc838e1ee9e85f`.
- Split-policy tests — commit `f5e71c95071df15b3f975f77a59bc088b768f62b`.
- Selector tests — commit `87a0eb3956b09892b1722ab4248592c3bdf5448f`.
- CPU guard workflow `.github/workflows/v144-rhythm-cpu-gate.yml` — commit `95e22b4f259861d31993687bb33c999f08d5181d`.
- CPU gate run `32934411093` = **SUCCESS**.
- Config currently requires pitch-content gain >= 0.005, no per-metric regression, no canary regression, no critical-mismatch increase, exact PDF-event fidelity 1.0, deterministic no-prune fallback, and 60/20/20 fit/validation/canary split with seed 144.

## Reproducible V144 calibration baseline — green
- Added `validation/v144_rhythm_calibration/build_baseline_report.py` in commit `a04590b52c33db60cc1e8ddfa7d6e9b84855c800`.
- Added CPU baseline workflow `.github/workflows/v144-reproduce-calibration-baseline.yml` in commit `3882c88ad4c35dee2ed6c73becb1285fd0b3b8a7`.
- Workflow run `32934939964` = **SUCCESS**.
- Persisted baseline bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`.
- Report: `debug/v144-rhythm-calibration/baseline/v5-frozen-calibration-baseline.json`, Git blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764`.
- Baseline exactly reproduces immutable historical metrics and critical mismatch count while explicitly labeling evaluation role `calibration-baseline-not-unseen-holdout`.
- Aggregated diagnostic buckets:
  - pitch content: 305 matched / 904 false-positive / 641 false-negative; F1 `0.2830626450116009`
  - pitch+timing: 48 matched / 1161 false-positive / 898 false-negative; F1 `0.044547563805104405`
  - string/fret+timing: 33 matched / 1176 false-positive / 913 false-negative; F1 `0.03062645011600928`
  - chord pitch-set: 17 matched / 874 false-positive / 586 false-negative; F1 `0.022757697456492636`
  - exact chord voicing: same 17 matched / 874 FP / 586 FN
  - technique: 21 generated / 0 reference / 0 matched in the structured gold extraction
  - rendering remains independent and exact at PDF fidelity `1.0`.

## Split-isolated baseline diagnostics — green
- Added `validation/v144_rhythm_calibration/analyze_split_baseline.py` in commit `6e50594b76508b57ddf8f63a5fc01306a617ca15`.
- Added CPU workflow `.github/workflows/v144-split-baseline-diagnostics.yml` in commit `3028d5f505f503d4cac1c39f71ce70b8b231fafd`.
- Workflow run `32935079594` = **SUCCESS**.
- Persisted diagnostics bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`.
- Report: `debug/v144-rhythm-calibration/baseline/v5-split-isolated-diagnostics.json`, Git blob `d69671de73debcea47b7ab86d8392077f48e201d`.
- Split assignment is deterministic by `measure+step`, seed 144: 60% fit / 20% validation / 20% canary. Cross-split matching is forbidden.
- **Fit labels may drive calibration; validation and canary labels may not drive candidate construction/ranking.** Validation/canary are gates after locking the fit-selected candidate.
- Fit baseline:
  - 688 generated notes / 594 reference notes
  - pitch content F1 `0.21528861154446177` (138 matched / 550 FP / 456 FN)
  - pitch+timing F1 `0.043681747269890804`
  - string/fret+timing F1 `0.031201248049921994`
  - chord pitch-set / exact voicing F1 `0.024858757062146894`
  - split-isolated critical mismatches `1150`; gross unmatched generated `622`, gross unmatched reference `528`.
- Validation baseline:
  - 267 generated / 199 reference
  - pitch content F1 `0.13733905579399142`
  - pitch+timing F1 `0.06008583690987125`
  - string/fret+timing F1 `0.034334763948497854`
  - chord/voicing F1 `0.02416918429003021`
  - split critical mismatches `426`.
- Canary baseline:
  - 254 generated / 153 reference
  - pitch content F1 `0.15233415233415235`
  - pitch+timing F1 `0.029484029484029485`
  - string/fret+timing F1 `0.024570024570024572`
  - chord/voicing F1 `0.014388489208633094`
  - split critical mismatches `385`.
- Fit-only false-positive context counts are now available for controlled candidate generation. Largest broad signals include `register::high` = 401 unmatched generated fit notes, `stepParity::0` = 365, `stepParity::1` = 257, `pitchClass::4` = 251. These are **diagnostic signals only** and must not be pruned blindly without fit/validation/canary gates.
- Highest fit pitch-error measures include measure 34 (18 errors), 110 (17), 24 (16), 109/72/73 (15 each), then 8/22/35/42/76/84/79/108 (14 each).

## Current interpretation
- Rendering is not the bottleneck: exact PDF event fidelity is already proven.
- Musical content is the bottleneck: generated false positives are especially large, but there are also substantial missing professional notes.
- First attack order remains: pitch-content/chord-set errors → onset/timing → string/fret voicing → technique notation.
- Before any actual candidate is promoted, staged selection must prevent validation/canary data from steering fit candidate ranking. A candidate may be learned/ranked on fit only, then locked; validation is a pass/fail gate; canary is a final pass/fail sanity gate. Failure should revert to deterministic no-prune, not search canary for another winner.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on these branch pushes. It is unrelated to V144 calibration and has not been modified.

## Immediate next resume actions
1. Tighten/add V144 staged selector semantics so fit alone constructs/ranks candidates; validation and canary can only accept/reject a locked candidate and cannot choose an alternate.
2. Add CPU tests proving no validation/canary leakage and deterministic no-prune fallback.
3. Generate a small family of **fit-learned, reference-free-at-runtime** contextual prune candidates from the frozen V5 stream; do not modify V5 itself.
4. Rank candidates on fit only. Lock exactly one candidate before consulting validation.
5. Gate the locked candidate on validation; only if it passes, gate once on canary. If either fails, fall back to no-prune without trying another candidate based on that gate.
6. Preserve exact PDF-event fidelity for every V144 candidate; V144 rendering evidence must match the candidate’s own scored event stream exactly.
7. Checkpoint after staged-selector tests and after the first locked candidate evaluation.
8. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
