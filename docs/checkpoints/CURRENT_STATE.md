# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is submitted and awaiting explicit owner approval/denial.
- No restricted GOAT bytes/assets have been admitted.
- V168 reference-facing score calls = **0**.
- Frozen Policy A/B, admission/provenance validators, GOAT deterministic selection contract, and promotion gate remain unchanged.
- GOAT pre-access selector static run `33569762190`, job `100060930936`: **SUCCESS**.
- No GOAT candidate generator/new-song scorer adapter is armed.
- `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## V167 immutable handoff

Promoted I005 Guitar F1 **42.7940586109996%**, precision **48.54280510018215%**, recall **38.26274228284279%**, TP/pred/ref **533/1098/1393**; Bass F1 **80.45325779036827%**. Highest unpromoted `recur-gap1-earliest` = **42.88012872083669%**, +**0.08607010983709418pp**, below the frozen +0.10pp threshold. No I006.

## SplitMySong diagnostic — terminal fail-closed

Checkpoint `docs/checkpoints/V168_SPLITMYSONG_HISTORICAL_SUPPORT_FAIL_CLOSED_20260901.md`, commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

Exactly one private observation: `FAIL_CLOSED_NO_CANDIDATE`; 1421/1471 required steps covered, 50 missing; candidate=false; referenceRead=false; scorerRead=false. Do not rerun, score, weaken, or interpolate.

## Parallel open-corpus breakthrough lane — V168 isolated

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`;
- commit `f0b966df4881311456b5c455161431d8a771114e`.

This is V169-style development only. No GOAT/Lenny reference tuning, no V168 mutation, no commercial-tab scraping, and no third-party audio committed to the repo.

### Replicated harmonic-fundamental signal

Frozen study script: `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`, creation commit `3f67a134f646cc35f12e9c49e545e8b0c1df5fd1`.

P1 checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P1_HARMONIC_RESULT_20260902.md`, commit `5ef3a3dff39e46e31527e2ef7824a655338a2539`.

P2 independent-player checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P2_HARMONIC_CONFIRMATION_20260902.md`, commit `4b6333f40c9c419bc7db6933c9b2497671a9fca7`.

Across P1/P2 direct-input + mic/amp, the unchanged lower-vs-+12 harmonic formula preferred the ground-truth lower pitch on **558/558** capture-note evaluations; weak-literal-f0 subset **137/137**; very-weak subset with examples **69/69**. This is a replicated **candidate breakthrough in feature design**, not yet end-to-end transcription proof because those studies start from a known reference pitch.

## Candidate-ranking V1 — TERMINAL SYNTHETIC FAIL-FAST

Preregistration: `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_PREREGISTRATION_20260902.md`, commit `cbff7cad113985bd141525304151df679c6a8c65`.

Failure checkpoint: `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V1_SYNTHETIC_FAIL_20260902.md`, commit `a506577498dce1583913e0a1fe23de1d0611f45e`.

V1 Actions run `33576111277`, job `100080320038` failed before real P1/P2 ranking because synthetic weak-fundamental fixture chose +12. Real V1 ranking observations = 0. V1 is terminal and must not be reused.

## Candidate-ranking V2 — frozen; serialization-only recovery pending

Frozen evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`;
- creation commit `b2544a2c84bfbf75797be19481540286cd57a514`;
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`.

Frozen V2 formula: `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`, with lower-octave odd-harmonic coherence and candidate set `{midi-12,midi,midi+12}`.

Actions run `33576456720`, job `100081401356`:
- four synthetic guards: **PASS**;
- P1/P2 archive official MD5 verification: **PASS**;
- P1 SHA256 `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`;
- P2 SHA256 `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`;
- first real `P1-directInput` `evaluate_capture(...)` computation completed in memory;
- serialization then failed on a NumPy `int64` before any real ranking summary was printed/written;
- P1 mic/amp and both P2 captures did not run;
- aggregate V2 gate did not run; no result artifact exists.

Dedicated recovery-boundary checkpoint:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V2_SERIALIZATION_RECOVERY_20260902.md`;
- creation commit `7364a977feda3cd147567aa58810be446472540b`.

Important: one real P1-DI ranking computation occurred, but **zero V2 real ranking summaries were exposed**. This is not a synthetic-only failure.

## NEXT SAFE ACTION

Run a **serialization-only V2 recovery** without editing the frozen evaluator blob. Add a separate adapter that imports the frozen `evaluate_capture(...)`, recursively converts NumPy scalars only after computation, verifies evaluator blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`, reruns the original four synthetic guards plus a serializer guard, then reruns the unchanged four public Guitar-TECHS captures and the already-frozen V2 success gate.

No V2 weight/threshold/timing/candidate change is allowed. Checkpoint recovered PASS/FAIL before defining any V3.

GOAT approval remains independent; if it arrives, follow the already-frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each new scientific boundary and immediately on GOAT approval/denial.
