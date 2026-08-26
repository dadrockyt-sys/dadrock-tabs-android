# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 00:48 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold-calibration work. Rhythm-first; do not begin Bass/Lead unless V144 quality is proven or the user explicitly redirects.**

## Product target
- `/ai-tab`: upload audio → choose Rhythm/Bass/Lead → professional-quality PDF preview → optional purchase unlocks full professional PDF.
- Current engineering target is musically accurate professional Rhythm transcription. Keep the frontend contract unchanged while engine quality is proven.

## Permanent V5 safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected analyzer: `analyzer/v143_reference_free_rhythm_pipeline.py`, Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 final-result sentinel: `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`, Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical scorer/PDF-event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- V5 shape: 891 attacks / 1214 selected / 1209 rendered / 5 voicing drops / 113 measures; 967 baseline + 242 rescued; 21 technique events. Tempo `129.19921875`.
- Original V5 professional one-shot holdout is permanently consumed. Never rerun/retry its final workflow, change its trigger, modify its candidate/thresholds/result, or use V144 calibration results to retune V5.
- Re-evaluating immutable V5 bytes is permitted only as explicitly labeled **V144 calibration baseline** evidence; it is not a V5 retry.
- Existing `freezeReady=false` sentinels remain false.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Immutable V5 diagnostic result
- Final workflow run `32919666736`; result bot commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`.
- Completion gate failed; Rhythm was not complete.
- Critical mismatches `1875` = 1069 gross unmatched generated + 806 unmatched reference; missing reference measures `0`.
- PDF-event fidelity `1.0`; measure coverage recall `1.0`.
- Musical F1: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord pitch-set `0.022757697456492636`; exact voicing `0.022757697456492636`.

## V144 gold calibration target — exact and persisted
- Visual target remains read-only on `main` at `public/Professionalexample.jpg`; main-tree blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Exact built reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- V144 semantics: **gold calibration benchmark, not an unseen holdout**. Never claim unbiased generalization from scores against it.
- Provenance manifest commit `9d29ba53466b721ce99f0265524b089b883b5f63`.
- Exact builder `validation/v144_rhythm_calibration/build_gold_reference.py`, commit `2b0fb21245d5ef01d0a5b6e65c39fa2740df3e69`.
- CPU build workflow corrected in commit `40fe83895ef76badde4409489a61b3c0a5a0fd1a`; run `32934718066` = SUCCESS.
- Persisted by bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f` at `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json` plus build report blob `5f1ec40176aa9b69676c7cd9e06b42c412731f37`.

## Reproducible V144 baseline — green
- Baseline report builder commit `a04590b52c33db60cc1e8ddfa7d6e9b84855c800`; workflow commit `3882c88ad4c35dee2ed6c73becb1285fd0b3b8a7`.
- Run `32934939964` = SUCCESS; persisted bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`.
- `debug/v144-rhythm-calibration/baseline/v5-frozen-calibration-baseline.json`, blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764` exactly reproduces immutable historical metrics and labels them `calibration-baseline-not-unseen-holdout`.
- Aggregate diagnostics: pitch 305 matched / 904 FP / 641 FN; pitch+timing 48 / 1161 FP / 898 FN; string/fret+timing 33 / 1176 FP / 913 FN; chord/voicing 17 / 874 FP / 586 FN; technique 21 generated / 0 reference / 0 matched. PDF fidelity remains `1.0`.

## Deterministic split baseline — green
- `validation/v144_rhythm_calibration/analyze_split_baseline.py` commit `6e50594b76508b57ddf8f63a5fc01306a617ca15`; workflow commit `3028d5f505f503d4cac1c39f71ce70b8b231fafd`.
- Run `32935079594` = SUCCESS; persisted bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`.
- Report `debug/v144-rhythm-calibration/baseline/v5-split-isolated-diagnostics.json`, blob `d69671de73debcea47b7ab86d8392077f48e201d`.
- Split is deterministic by measure+step, seed 144: 60% fit / 20% validation / 20% canary; cross-split matching forbidden.
- **Fit labels may drive calibration. Validation/canary labels may only gate an already locked candidate.**
- Fit: 688 generated / 594 reference; pitch F1 `0.21528861154446177` (138 matched / 550 FP / 456 FN); pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; split critical `1150`; gross unmatched generated `622`, reference `528`.
- Validation: 267 generated / 199 reference; pitch `0.13733905579399142`; pitch/timing `0.06008583690987125`; string/fret/timing `0.034334763948497854`; chord/voicing `0.02416918429003021`; critical `426`.
- Canary: 254 generated / 153 reference; pitch `0.15233415233415235`; pitch/timing `0.029484029484029485`; string/fret/timing `0.024570024570024572`; chord/voicing `0.014388489208633094`; critical `385`.
- Fit-only broad FP signals include `register::high` 401, `stepParity::0` 365, `stepParity::1` 257, `pitchClass::4` 251. These are diagnostic signals only; never prune blindly.
- Highest fit pitch-error measures begin 34 (18 errors), 110 (17), 24 (16), 109/72/73 (15 each).

## V144 policy/scaffold and CPU safety gate
- Existing V144-only policy/config/tests remain isolated under `modal/`; initial CPU gate run `32934411093` was SUCCESS.
- Config requires fit pitch-content gain >= `0.005`, no per-metric regression, no validation/canary regression, no critical-mismatch increase, exact PDF-event fidelity `1.0`, deterministic fallback, holdout closed.

## Leakage-safe staged selector — GREEN 2026-08-26 00:48
- Added `modal/v144_rhythm_staged_selector.py` in commit `68575a4c0d68f54392703a038bf909619a708177`.
- Added `modal/tests/test_v144_rhythm_staged_selector.py` in commit `80fe723e45ed7b44f3d9acee8668af8f087a19a4`.
- Updated `.github/workflows/v144-rhythm-cpu-gate.yml` in commit `8bb7929a9f26d331675cb097924a3e2bf2009a16` to run staged-selector leakage tests.
- CPU gate run `32935390792` = **SUCCESS**.
- Proven semantics:
  - `lock_fit_candidate()` ranks only on fit and does not read validation/canary values.
  - Fit qualification requires exact PDF fidelity, no musical metric regression, no critical mismatch regression, configured minimum pitch-content gain, and full safety flags.
  - Exactly one fit winner is locked before validation.
  - Validation is pass/fail for only the locked candidate; no alternate candidate can be selected after failure.
  - Canary is consulted only if validation passes, and is likewise pass/fail only for the locked candidate.
  - Validation failure stops before canary access and falls back to `no-prune`.
  - Canary failure falls back to `no-prune`; no alternate search is permitted.
  - No fit winner falls back deterministically without reading later-stage values.
  - Safety violations including runtime reference input prevent fit lock.
- Frozen V5 identity guards remained green during this run; no V5/main/Production/GPU state changed.

## Current interpretation
- Rendering is not the bottleneck; musical transcription is.
- First attack order: pitch-content/chord-set → onset/timing → string/fret voicing → technique.
- The next experiment must learn a small, interpretable contextual prune rule from fit-only labels, apply that rule without reference input at runtime, lock the fit winner, then evaluate that single winner on validation and canary once.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Add a CPU-only first-candidate search script/workflow under V144-only paths.
2. Construct candidate rules from **fit-only unmatched generated notes** using reference-free runtime signatures from `context_signature`; begin with single-signature prunes for interpretability.
3. Score/rank the candidate family on fit only and lock exactly one using `lock_fit_candidate()` before any validation/canary access.
4. Materialize the locked candidate independently of gold reference input; prove its renderer/PDF-event evidence equals its own scored event stream exactly.
5. Gate the single locked candidate once on validation. Only if it passes, gate once on canary. Any failure returns to `no-prune`; do not choose another candidate using later-stage feedback.
6. Persist V144-only candidate/search/report artifacts and checkpoint exact commits/runs/results.
7. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
