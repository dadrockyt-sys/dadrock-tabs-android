# Scorer + Modal/L4 archive for future Rhythm testing

This is a preservation manifest, not permission to run GPU jobs automatically.

## Professional scorer harness — preserve
Keep these files/history intact for future calibration and fresh-holdout validation:
- `validation/rhythm_holdout/score_rhythm_holdout.py`
- `validation/rhythm_holdout/canonical.py`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `validation/rhythm_holdout/verify_reference_completeness.py`
- `.github/workflows/v143-v5-professional-scorer-preflight.yml`
- `.github/workflows/v143-v5-final-professional-holdout.yml`
- `debug/v143-contextual-prune/v5-professional-pdf/scorer-preflight-report.json`
- `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`

Important scorer identities from V5:
- canonical/PDF event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`
- final result Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`
- final result commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`

For post-holdout calibration, the scorer may be adapted to emit richer diagnostics. Do not overwrite the V5 terminal result. For a genuinely independent final test, use a new unseen professional reference.

## Modal/L4 work — preserve for later testing
Known preserved Modal smoke assets:
- branch `v143-github-modal-smoke`
- workflow `.github/workflows/v143-modal-live-smoke.yml`, Git blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`
- the smoke workflow checks out `v143-ai-tab-production-integration`
- probe `analyzer/v143_modal_http_live_smoke.py` on `v143-ai-tab-production-integration`, Git blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`
- probe contract expects `modalGpu == "L4"`, deterministic separator seed `143`, Demucs shifts `1`, paired carrier stems, and two-view bend/legato consensus.

Do not delete these branches/files. Do not spend Modal/L4 compute merely to reproduce V5. Use L4 later when a CPU/calibration experiment has a specific hypothesis worth testing or when an end-to-end candidate is ready for GPU verification.

## Testing policy going forward
1. Old `Are You Gonna Go My Way` professional reference = calibration set, not unseen holdout.
2. Build and compare new Rhythm candidates against that calibration set as often as useful.
3. Keep scorer diagnostics separate from production runtime.
4. Keep Modal/L4 as an optional accelerator/verification path; do not make it the first debugging tool.
5. Before claiming Rhythm solved, freeze a candidate and score once against a different unseen professional song/reference.
