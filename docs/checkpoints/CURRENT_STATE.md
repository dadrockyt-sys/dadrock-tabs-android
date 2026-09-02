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

Frozen lesson: V2 is strong when an octave ambiguity is already known, but indiscriminate application is harmful. V3 must be a conservative reference-blind trigger deciding **whether** V2 should intervene. P3 is consumed evaluation evidence; never tune V3 from P3 per-event reference outcomes.

## V3 fresh corpus — GuitarSet intake PASS, evaluation still sealed

Split preregistration:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_SPLIT_PREREGISTRATION_20260902.md`
- creation commit `0be0cb3ec1ee2a83100ea1e30ed523b17fc59768`.

Metadata inventory result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_METADATA_INVENTORY_PASS_20260902.md`
- creation commit `45a2c8c6499af01f1218c86ecd71bb35b455cb83`.

Frozen metadata inventory script:
- `validation/open_corpus/inventory_guitarset_v3_metadata.py`
- creation commit `312cef0ccd6d217c9de31231d0f9085d57a2289f`
- blob `3a0f20df2b8ac0b447d8c7d6fb13a7ff67878a69`.

Real metadata-only Actions run:
- workflow head `b11a4f1b4e644f35c25d04c803d0801b58bb469e`
- run `33579938898`
- job `100091870033`: **SUCCESS / `GUITARSET_V3_METADATA_INVENTORY_PASS`**.

Authoritative GuitarSet v1.1.0 archive identities:
- `audio_mono-mic.zip`: official MD5 `275966d6610ac34999b58426beb119c3` MATCH; observed SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`;
- `annotation.zip`: official MD5 `b39b78e63d3446f2e54ddb7a54df9b10` MATCH; observed SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.

Inventory verified exact microphone/JAMS normalized stem pairing across **360 tracks**, 60 for each player `00`–`05`.

Frozen split remains:
- development players `02/04/05`: **180 tracks**;
- sealed prospective evaluation players `00/01/03`: **180 tracks**.

Three public anomaly tracks remain development-only and outside trigger-fit objective: `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`.

Metadata report SHA256 `2e23ca44c2eae62ec9f6e3e7d2be5829d693be9dc48eeb0eefcad2c489dccb1f`; artifact ID `9828185987`, artifact ZIP SHA256 `05d9daf7b96e79e44032e900e3b0add45a800e9f150825a3e4a2305207517ff0`.

Inventory safety boundary: ZIP central-directory metadata only; audio decoded=false; WAV/JAMS members extracted=0; JAMS member contents read=false; JAMS note events read=0; Basic Pitch inference calls=0; GuitarSet prospective evaluation score calls=0; V168 score calls=0. Source archives were deleted before artifact upload.

## NEXT SAFE ACTION

1. Freeze a **development-only V3 trigger-study contract** before reading GuitarSet development outcomes.
2. Inspect only the already-frozen V2 implementation and P3 aggregate lesson; do not mine P3 per-event reference errors.
3. Define a small conservative family of reference-blind trigger features/gates whose purpose is to decide whether V2 is allowed to change a Basic Pitch event.
4. Freeze exact JAMS parsing/reference semantics plus candidate/reference isolation for development players `02/04/05`.
5. Only then run development inference/scoring and select/freeze the V3 gate using development evidence.
6. Players `00/01/03` remain fully sealed: no JAMS content parsing, candidate inference or score calls until the final trigger, evaluation scorer and PASS/FAIL criteria are frozen.
7. Checkpoint again before any GuitarSet development JAMS read or Basic Pitch inference.

GOAT approval remains independent; on approval follow the already-frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
