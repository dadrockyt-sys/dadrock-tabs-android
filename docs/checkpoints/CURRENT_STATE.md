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

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_PREREGISTRATION_20260902.md`;
- commit `cbff7cad113985bd141525304151df679c6a8c65`.

Dedicated failure checkpoint:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V1_SYNTHETIC_FAIL_20260902.md`;
- commit `a506577498dce1583913e0a1fe23de1d0611f45e`.

V1 evaluator creation commit `4a78c31c09f4bb4048b8a95793031c9f91e6fa59`; workflow commit `3cd9e0da9204859aa8348045e49e003f51ccd119`; Actions run `33576111277`, job `100080320038`.

V1 failed **before any real P1/P2 archive download or candidate-ranking result**. Synthetic guard error:
`RuntimeError: self-test wrong winner: expected 45, got 57`.

Thus real P1 candidate-ranking winner observations = **0** and real P2 candidate-ranking winner observations = **0**. V1 is rejected and must not be silently retuned/reused.

Frozen diagnosis: V1 penalized an octave-too-high candidate only with literal power at `f/2`. When the true lower fundamental is weak, that misses the already-replicated lower-octave evidence at odd harmonics `3f/2`, `5f/2`, `7f/2`.

## NEXT SAFE ACTION

Define **candidate-ranking V2 prospectively using synthetic physics only**, before any real P1/P2 candidate-ranking results. Replace V1's literal `f/2` penalty with lower-octave odd-harmonic coherence. Require V2 to pass multiple synthetic guards (normal harmonic decay, weak fundamental/strong H2-H3-H5, even-heavy distortion) before real public-corpus downloads/ranking are permitted.

If synthetic guards pass, checkpoint exact V2 formula and then run P1/P2 controlled `{midi-12,midi,midi+12}` ranking under a new frozen V2 label. If V2 reaches real data, preserve the same prospective success gate and checkpoint results before any V3.

GOAT approval remains independent; if it arrives, follow the already-frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each new scientific boundary and immediately on GOAT approval/denial.
