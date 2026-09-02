# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is awaiting explicit owner approval/denial.
- No restricted GOAT bytes admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT selection contract and promotion gate unchanged.
- GOAT pre-access static run `33569762190`, job `100060930936`: SUCCESS.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate. Dedicated checkpoint commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

## Open-corpus lane — V168 isolated

Frozen V2 evaluator blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`; helper blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`. Controlled Guitar-TECHS P1/P2 V2 result: **558/558 = 100%**; result checkpoint commit `38df953a637c12359a844b239bce08897c710c32`.

P3 run `33578675945` is terminal scientific **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**: event count 4693 preserved, 1121 changed pitches = 23.88663967611336%; primary macro **60.576880733206515% -> 51.95250763325269%**, delta **-8.624373099953829pp**. Never mine P3 per-event outcomes for V3. Frozen aggregate lesson only: V2 needs a conservative trigger.

## V3 GuitarSet provenance — PASS, evaluation sealed

Split preregistration commit `0be0cb3ec1ee2a83100ea1e30ed523b17fc59768`.

Metadata-only archive verification run `33579938898`, job `100091870033`: SUCCESS.
- `audio_mono-mic.zip`: MD5 `275966d6610ac34999b58426beb119c3`, SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`.
- `annotation.zip`: MD5 `b39b78e63d3446f2e54ddb7a54df9b10`, SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.
- Exact mic/JAMS pairing: 360 tracks, 60/player.
- Development `02/04/05`: 180 nominal; sealed evaluation `00/01/03`: 180.
- Predeclared anomalies excluded from development objective: `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`.
- Inventory result checkpoint commit `45a2c8c6499af01f1218c86ecd71bb35b455cb83`.

## V3 development bridge — FROZEN / STATIC PASS / READY

Development trigger preregistration:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_TRIGGER_PREREGISTRATION_20260902.md`
- creation commit `1c9a83c7e101824640a244c83e0a86637317b101`.

READY checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_BRIDGE_READY_20260902.md`
- creation commit `c4b8bf4a31281bea5d9b451095e5eff2b4efc174`.

Frozen V3 trigger helper:
- `validation/open_corpus/v3_selective_octave_trigger_v169.py`
- blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`.

Frozen audio-only candidate generator:
- `validation/open_corpus/generate_guitarset_v3_development_candidates.py`
- blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`.

Frozen reference-only scorer:
- `validation/open_corpus/score_guitarset_v3_development_candidates.py`
- blob `19ef54155735a6ac1e65441250b47d1572ac0380`.

Static workflow blob `294fd97948c061878cb1b1fa39314ae204a9b994`; run `33581122972`, job `100095439483`: **SUCCESS**. Exact blob guards, reference isolation, scorer no-audio/no-generation, compile, exact 8-config family, trigger/candidate/scorer self-tests all PASS.

Trigger family is frozen before outcomes: consensus `{0.75,1.00}` × median advantage `{0.05,0.10,0.15,0.20}`. Synthetic octave-high fixture gave frozen V2 winner MIDI45, consensus **1.0**, median advantage **0.40037115768886156**.

Development objective is exactly **177 tracks**: player 02=59, 04=58, 05=60. Candidate qualifies only with event identity, >=+0.25pp primary macro gain, primary combined micro non-regression, each-player primary micro delta >=-0.10pp, strict50 combined micro non-regression. Among qualifiers choose fewest changed pitches first; if none: `NO_DEVELOPMENT_SIGNAL` and keep evaluation sealed.

Reference semantics frozen from official GuitarSet parser: `note_midi`, fallback `pitch_midi`; six string annotations; `int(round(note.value))`; preserve all events; exact-pitch one-to-one onsets at 100ms/50ms.

At this READY boundary: GuitarSet development JAMS note events read=0; GuitarSet Basic Pitch inference calls=0; development score calls=0; evaluation processed=false; evaluation score calls=0; V168 score calls=0; GPU/CUDA/Modal=false.

## NEXT SAFE ACTION

Run the preregistered two-job development workflow exactly once:
1. Job A: verify audio archive, extract only the 177 admissible development WAVs, delete ZIP, prove no JAMS/evaluation files, run Basic Pitch once/track, freeze all 8 JSON candidate streams.
2. Job B: verify frozen candidate hashes, no Basic Pitch, verify annotation archive, extract only corresponding 177 development JAMS files, delete ZIP, prove no audio/evaluation files, score and apply frozen selection rule.
3. Checkpoint `V3_DEVELOPMENT_TRIGGER_SELECTED` or `NO_DEVELOPMENT_SIGNAL` before any evaluation work.

No threshold/feature/scorer changes after development outcomes become visible in this lane.

GOAT approval remains independent; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
