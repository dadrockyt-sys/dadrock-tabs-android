# Open-corpus breakthrough lane — preregistration

Date: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`
Status: **PARALLEL DEVELOPMENT LANE / V168 UNCHANGED**

## Purpose
Use permissively licensed public guitar datasets to search for genuinely new, reference-grounded transcription insights while GOAT restricted access is pending.

This lane is **not V168**. Results from this lane may inform a future V169/new-development policy, but they may not modify V168 Policy A, Policy B, GOAT holdout selection, V168 admission rules, or the V168 prospective promotion threshold.

## Anti-contamination boundary
- Do not inspect restricted GOAT bytes before explicit owner approval.
- Do not use public GOAT example reference content for development, because GOAT remains the intended V168 holdout family.
- Do not use the Lenny Kravitz calibration reference for new tuning.
- Do not change V168 Policy A/B from any open-corpus result.
- Keep V168 reference-facing score calls at 0.

## Public data priority
Primary development corpus: **Guitar-TECHS v1** (Zenodo record `14963133`). Public project/paper state that the dataset is CC BY 4.0. It provides >5h electric-guitar recordings, multiple players/hardware/capture paths, and synchronized per-string MIDI ground truth.

Secondary development corpus: **EGFxSet** (Zenodo record `7044411`), CC BY 4.0 per the published work, for controlled single-note/effect robustness.

Tertiary development corpus: **GuitarSet v1.1.0** (Zenodo record `3371780`), acoustic guitar with rich note/string/fret/contour annotations; use where acoustic-domain evidence is scientifically relevant.

Reserve **EGSet12** (Zenodo record `11406378`) as a small external benchmark by default; do not tune on its 12 performances unless a later checkpoint explicitly changes its role before inspection.

## First breakthrough question
Test whether a **harmonic-aware fundamental-evidence ratio** can distinguish real guitar fundamentals from octave/upper-harmonic confusions more reliably than a binary `fundamentalPresent` gate.

Initial hypothesis:
- for a true fundamental `f0`, aggregate narrow-band energy near `f0`, `2*f0`, `3*f0`, and `4*f0`;
- compare the fundamental energy and harmonic-series consistency against octave candidates;
- study the ratio by string, fret/pitch, capture path, and technique using public ground truth;
- look specifically for cases where the fundamental is weak but the harmonic pattern still uniquely supports the lower pitch.

This is exploratory V169-style development. Any threshold/model learned from these public references must be frozen and evaluated later on data not used to fit it.

## Compute / rights boundary
- CPU-only under current authorization.
- No GPU/CUDA/Modal without fresh explicit user authorization.
- No scraping of commercial tab sites or copyrighted transcription repositories.
- Only fetch datasets/files whose public provenance and use terms are acceptable for this research lane.
- Do not redistribute third-party audio through this repository; store only provenance, hashes, scripts, aggregate statistics, and derived non-reconstructive measurements.
- `main` / Production remain untouched.

## V168 state remains
**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**  
V168 reference-facing score calls: **0**.
