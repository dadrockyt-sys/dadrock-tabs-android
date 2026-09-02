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

Preregistration commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`; result checkpoint commit `244dfd688500901119637bbb7972259c5a34b206`.

Real isolated workflow run `33578675945`: candidate job `100088107787` SUCCESS; scorer job `100088672148` SUCCESS. Candidate/reference isolation and artifact/hash guards passed.

Frozen candidate stream: 4693 baseline events = 4693 corrected events; changed pitches **1121 / 4693 = 23.88663967611336%**; boundary-unscored 0; candidate freeze manifest SHA256 `88f1171baed46758916d48d640ca9f07476948d8292d310d7469f3f0d5849cc0`.

Scientific classification: **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**.

Primary 100ms baseline macro F1 **60.576880733206515%** vs corrected **51.95250763325269%**, delta **-8.624373099953829pp**. Baseline micro F1 **60.8219816043777%** vs corrected **52.5323087670276%**, delta **-8.289672837350096pp**. Strict 50ms baseline micro **57.957853067877515%** vs corrected **49.97089300267784%**.

Score report SHA256 `540cfe330e975584a0857ace2511ba021ab918b82dd1392a48452ffbebb92170`.

Frozen lesson: V2 is strong when an octave ambiguity is already known, but indiscriminate application is harmful. V3 must be a conservative reference-blind trigger deciding **whether** V2 should intervene.

P3 is consumed evaluation evidence. Do not rerun it or tune V3 from P3 per-event reference outcomes.

## V3 fresh corpus — GuitarSet split frozen before use

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_SPLIT_PREREGISTRATION_20260902.md`;
- creation commit `0be0cb3ec1ee2a83100ea1e30ed523b17fc59768`.

Authoritative source frozen as GuitarSet v1.1.0, Zenodo record `3371780`, DOI `10.5281/zenodo.3371780`.

Frozen archives for this lane:
- `audio_mono-mic.zip`, official MD5 `275966d6610ac34999b58426beb119c3`;
- `annotation.zip`, official MD5 `b39b78e63d3446f2e54ddb7a54df9b10`.

Use only monophonic microphone audio plus JAMS annotation references. Do not use hexaphonic per-string audio.

Player-disjoint split frozen before any GuitarSet audio/JAMS note processing or Basic Pitch inference:
- development players: `02`, `04`, `05`;
- sealed prospective evaluation players: `00`, `01`, `03`;
- nominal prospective evaluation set: **180 tracks**.

Three publicly documented anomalous tracks are development-only and excluded from the trigger-fit objective: `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`.

At split freeze: GuitarSet audio downloaded=false; annotation archive downloaded=false; JAMS note events read=0; Basic Pitch inference calls=0; prospective evaluation score calls=0; V168 score calls=0.

## NEXT SAFE ACTION

1. Run a **metadata/path-only inventory** of `audio_mono-mic.zip` and `annotation.zip`.
2. Verify official MD5 plus observed SHA256 for both archives.
3. Enumerate ZIP central-directory paths only; do **not** parse JAMS contents and do **not** run Basic Pitch.
4. Verify exact mic/JAMS stem pairing and expected six-player / 360-track structure; preserve only metadata/hashes.
5. Checkpoint inventory identities/results before any V3 development inference or annotation parsing.
6. Only after inventory PASS, design the V3 trigger using development players `02/04/05`; evaluation players `00/01/03` remain sealed until the trigger, scorer and PASS/FAIL rules are frozen.

GOAT approval remains independent; on approval follow the already-frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
