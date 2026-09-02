# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is submitted and awaiting explicit owner approval/denial.
- No restricted GOAT bytes/assets admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT selection contract and promotion gate remain unchanged.
- GOAT pre-access static run `33569762190`, job `100060930936`: **SUCCESS**.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong diagnostic remains terminal `FAIL_CLOSED_NO_CANDIDATE`: one private observation only, 1421/1471 steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate. Dedicated checkpoint commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

## Parallel public open-corpus lane — V168 isolated

Open-corpus preregistration commit `f0b966df4881311456b5c455161431d8a771114e`.

### Controlled harmonic breakthrough

Frozen V2 evaluator `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`, blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`; helper blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

Recovered V2 Actions run `33577664874`, job `100085059794`: **SUCCESS / CANDIDATE_FEATURE_PASS**. Controlled octave selection on Guitar-TECHS P1/P2 DI + mic/amp: **558/558 = 100%**, weak **137/137**, very weak **69/69**, false-low/high 0/0. Aggregate SHA256 `f527313e5c24802eab1bc0c3ba38efdc3d3a08af9038eb4a5a22ea72d5d089b2`.

Result checkpoint: `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V2_PASS_20260902.md`, commit `38df953a637c12359a844b239bce08897c710c32`.

Interpretation remains limited: this is a controlled octave-disambiguation breakthrough, not 100% end-to-end transcription.

## P3 reference-blind bridge — READY, REAL INFERENCE NOT YET STARTED

Scientific preregistration:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_PREREGISTRATION_20260902.md`;
- creation commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`.

P3 metadata-only inventory:
- checkpoint commit `cc1d9d3d4a168e6551935ab0445f20ea1e9134b4`;
- Actions run `33577994728`, job `100086035966`: **SUCCESS**;
- `P3_music.zip` official MD5 `071ba80aecf00f4a31fbd167b3f22198`;
- observed SHA256 `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`;
- complete indices 01–12 for MIDI, DI WAV and mic/amp WAV;
- P3 reference-note events read = 0; P3 candidates = 0.

Frozen design: all 12 works × DI/micAmp = 24 units; Basic Pitch 0.4.0 defaults; model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`; each Basic Pitch event proposes `{p-12,p,p+12}` to frozen V2 with alignment 0.0; pitch replacement only; event count identical. Candidate artifacts must be frozen before MIDI references are extracted by a separate scorer job. Primary exact-pitch onset tolerance 100ms, strict 50ms. PASS/FAIL/INCONCLUSIVE thresholds are frozen in the preregistration.

### CPU preflight PASS

`.github/workflows/open-corpus-basic-pitch-cpu-preflight.yml`, creation commit `dc1e6ea7be58e3c72d0ea770b0f57f17ba591693`.

Actions run `33578250363`, job `100086839088`: **SUCCESS**. Verified Python 3.10.21, Basic Pitch 0.4.0, tflite-runtime 2.14.0, NumPy 1.26.4, exact model SHA, TFLite-only runtime, no CUDA; synthetic A4 inference PASS; P3 audio/reference untouched.

### Bridge implementation frozen/static-tested

Audio-only candidate generator:
- `validation/open_corpus/generate_p3_reference_blind_octave_candidates_v169.py`;
- creation commit `419829793908ebdc9cbeca767532eb165e6d478c`;
- blob `e3fe6f88b585405751dad139d82769dd00743d69`.

Reference-only scorer:
- `validation/open_corpus/score_p3_octave_bridge_v169.py`;
- creation commit `721fa5ca0262e23a9071c7a837ab16b33e83ed48`;
- blob `70ed9ceb69584ce96945688ae45cd9c8ffa3022a`.

Pre-outcome boundary rule: if the frozen V2 analysis window does not exist near an audio boundary, preserve the original Basic Pitch pitch and increment `boundaryUnscoredCount`; never remove the event.

Static workflow `.github/workflows/open-corpus-p3-octave-bridge-static.yml`, creation commit `d696e9d6f7b78478b684e7f2e7a9d78dfef9ab72`; Actions run `33578459757`, job `100087448155`: **SUCCESS**. Exact blob guards, candidate reference isolation, scorer no-audio/no-generation guard, compile, candidate/scorer self-tests and Basic Pitch model hash all PASS.

Final pre-inference readiness checkpoint:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_BRIDGE_READY_20260902.md`;
- creation commit `08a8a82cb7457baeeb0b600ff7edeb73d154093b`.

At this boundary: **P3 real Basic Pitch inference = 0; P3 reference note-event reads = 0; P3 score calls = 0; V168 score calls = 0.**

## NEXT SAFE ACTION

Create/run the preregistered real two-job P3 CPU workflow exactly once:
1. candidate job verifies frozen identities/archive, extracts audio only, deletes ZIP, proves no MIDI, generates + hashes all 24 baseline/corrected streams and uploads JSON-only candidate artifact;
2. scoring job starts after candidate freeze, verifies hashes, independently downloads exact archive, extracts MIDI only, proves no audio, scores frozen candidates, preserves PASS/FAIL/INCONCLUSIVE report;
3. scientific outcome must not itself fail CI; only integrity/runtime violations fail;
4. checkpoint outcome before any V3 or tuning.

No P3-driven threshold/weight/timing/scorer/gate changes are permitted.

GOAT approval remains independent; on approval follow the already-frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
