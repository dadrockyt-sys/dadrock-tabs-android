# Open-corpus harmonic candidate-ranking V1 — synthetic fail-fast

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **V1 REJECTED AT SYNTHETIC GUARD / NO REAL P1-P2 RANKING OBSERVED**
Classification: parallel V169-style development; V168 unchanged.

## Frozen V1 boundary

V1 was prospectively defined before any real octave-confusion winner result in:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_PREREGISTRATION_20260902.md`
- creation commit `cbff7cad113985bd141525304151df679c6a8c65`.

Evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v169.py`
- creation commit `4a78c31c09f4bb4048b8a95793031c9f91e6fa59`.

Workflow:
- `.github/workflows/open-corpus-harmonic-candidate-ranking-v1.yml`
- creation commit `3cd9e0da9204859aa8348045e49e003f51ccd119`.

## Fail-fast result

GitHub Actions run `33576111277`, job `100080320038`.

The workflow failed at the **synthetic candidate-ranking self-test** before any Guitar-TECHS P1/P2 archive download or real candidate-ranking evaluation occurred.

Exact terminal error:
`RuntimeError: self-test wrong winner: expected 45, got 57`

Thus the frozen V1 absolute candidate score selected the +12-semitone candidate on the preregistered weak-fundamental synthetic fixture.

The following real-data workflow steps were skipped:
- P1/P2 archive download/verification;
- all four real P1/P2 candidate-ranking evaluations;
- the prospectively frozen V1 success gate;
- report hashing/artifact upload.

Therefore:
- real P1 candidate-ranking winner observations = **0**;
- real P2 candidate-ranking winner observations = **0**;
- no real V1 pass/fail percentage exists;
- V1 is rejected on synthetic physics alone and must not be represented as a real-corpus result.

## Diagnosis frozen before V2 real data

The V1 penalty used only literal subharmonic power at `f/2`. This is insufficient for an octave-too-high candidate when the real lower fundamental itself is weak: the false +12 candidate can explain the strong true `2*f0`, while its `f/2` penalty sees only the weak literal true `f0`.

The already-replicated P1/P2 insight suggests the correct symmetry: evidence for the **lower-octave hypothesis must include its odd-harmonic series**, not only the literal lower fundamental. For a false +12 candidate at frequency `f`, the lower hypothesis at `f/2` can still be strongly supported at `3f/2`, `5f/2`, and `7f/2` even if power at `f/2` is weak.

This diagnosis uses only the synthetic failure and the already-checkpointed P1/P2 lower-vs-+12 finding; it does not use any real candidate-ranking winner result because none was observed.

## V1 disposition

V1 is **terminal REJECTED**. Do not rerun V1 on real P1/P2 data and do not silently alter its formula while retaining the V1 label.

A V2 may be defined prospectively using synthetic fixtures only. V2 must pass multiple synthetic octave-confusion guards before any real P1/P2 candidate-ranking data are downloaded/evaluated.

## V168 unchanged

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**  
V168 prospective reference-facing score calls: **0**.

No GPU/CUDA/Modal was used. `main` / Production were not modified.
