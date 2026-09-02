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

## P3 reference-blind bridge — SCIENTIFIC FAIL / TERMINAL FOR THIS DESIGN

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_PREREGISTRATION_20260902.md`
- creation commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`.

Final result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_FAIL_20260902.md`
- creation commit `244dfd688500901119637bbb7972259c5a34b206`.

Real two-job workflow:
- `.github/workflows/open-corpus-p3-reference-blind-octave-bridge.yml`
- creation commit `bdda7e10312d6104c8ce9e418a58dd43b9dcf3e8`
- Actions run `33578675945`
- candidate job `100088107787`: **SUCCESS**
- scorer job `100088672148`: **SUCCESS**.

Integrity/reference isolation passed. Candidate job extracted audio only, deleted the archive, had no MIDI, used CPU/TFLite Basic Pitch 0.4.0 plus frozen V2, and froze candidates before scoring. Scorer verified frozen candidate hashes before independently downloading/extracting MIDI-only references; Basic Pitch was absent in scorer; scorer read no audio and regenerated no candidates.

Frozen candidate stream:
- baseline events **4693**;
- corrected events **4693**;
- event-count identity true;
- changed pitches **1121 / 4693 = 23.88663967611336%**;
- boundary-unscored **0**;
- candidate freeze manifest SHA256 `88f1171baed46758916d48d640ca9f07476948d8292d310d7469f3f0d5849cc0`;
- candidate artifact ID `9827623576`, ZIP digest `437031e6ed7f021694358f75e2f29033a1c53cdf249d35792291f5a624cdba7a`.

Scientific classification: **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**.

Primary 100ms:
- baseline combined macro F1 **60.576880733206515%**;
- corrected combined macro F1 **51.95250763325269%**;
- delta **-8.624373099953829pp**;
- baseline micro F1 **60.8219816043777%**, TP/pred/ref **2612/4693/3896**;
- corrected micro F1 **52.5323087670276%**, TP/pred/ref **2256/4693/3896**;
- delta micro **-8.289672837350096pp**;
- DI micro delta **-8.356039963669389pp**;
- mic/amp micro delta **-8.21983273596176pp**.

Strict 50ms:
- baseline macro F1 **57.47009703962679%**;
- corrected macro F1 **49.22080531991671%**;
- delta macro **-8.249291719710087pp**;
- baseline micro F1 **57.957853067877515%**;
- corrected micro F1 **49.97089300267784%**;
- delta micro **-7.986960065199675pp**.

Score report SHA256 `540cfe330e975584a0857ace2511ba021ab918b82dd1392a48452ffbebb92170`; score artifact ID `9827647977`, ZIP digest `4fc7438f6e10e5f0f9cc00e2e0306dd98bed95094a0ab8c4b719dd8474c3669b`.

### Scientific lesson frozen from P3

The V2 harmonic ranking signal is strong for a controlled octave question but **indiscriminate application is harmful**. Basic Pitch already gets many pitches right; the always-on V2 bridge altered nearly one quarter of events and caused large precision/recall loss. The next research object should be a conservative **reference-blind trigger/gate** deciding when an octave correction is warranted, not a more aggressive always-on reranker.

P3 is now consumed evaluation evidence. Do not rerun or tune V3 from P3 per-event reference errors. P1/P2 single-note material remains development evidence; next prospective V3 evaluation should use a fresh independent public corpus selected/frozen before outcomes.

## NEXT SAFE ACTION

1. Identify and rights/provenance-freeze a fresh independent public guitar corpus for the next prospective evaluation; GuitarSet is a leading candidate if current official distribution/license checks pass.
2. Develop a conservative V3 trigger using only P1/P2 designated development evidence plus synthetic/physics guards; use only the aggregate P3 lesson that always-on correction is harmful, not P3 per-event outcomes.
3. Freeze exact trigger features/thresholds, proposal/correction rules, fresh evaluation partition, candidate/reference isolation, scorer and PASS/FAIL rules before reading fresh evaluation outcomes.
4. Keep the frozen V2 score unchanged unless a separately justified V3 feature redesign is preregistered.
5. Checkpoint before first fresh-corpus inference and after the prospective result.

GOAT approval remains independent; on approval follow the already-frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
