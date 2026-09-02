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

Frozen V2 evaluator `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`, blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`; helper blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

Controlled Guitar-TECHS P1/P2 V2 result: **558/558 = 100%**, weak 137/137, very weak 69/69, false-low/high 0/0. Result checkpoint commit `38df953a637c12359a844b239bce08897c710c32`.

P3 two-job reference-blind bridge run `33578675945` is terminal scientific **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**. It preserved event count (4693) but changed 1121 pitches = 23.88663967611336%. Primary macro F1 fell **60.576880733206515% -> 51.95250763325269%**, delta **-8.624373099953829pp**; primary micro fell **60.8219816043777% -> 52.5323087670276%**. P3 per-event outcomes are forbidden for V3 tuning. Frozen aggregate lesson only: V2 needs a conservative intervention trigger.

## V3 GuitarSet provenance — PASS, evaluation sealed

Fresh split preregistration commit `0be0cb3ec1ee2a83100ea1e30ed523b17fc59768`.

GuitarSet v1.1.0 archive identities verified by metadata-only run `33579938898`, job `100091870033` SUCCESS:
- `audio_mono-mic.zip` MD5 `275966d6610ac34999b58426beb119c3`, SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`;
- `annotation.zip` MD5 `b39b78e63d3446f2e54ddb7a54df9b10`, SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.

Exact mic/JAMS stem pairing: 360 tracks, 60/player. Development players `02/04/05` = 180 nominal; sealed prospective evaluation players `00/01/03` = 180. Known anomaly tracks `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp` are development-only and excluded from the trigger-fit objective. Inventory result checkpoint commit `45a2c8c6499af01f1218c86ecd71bb35b455cb83`.

Metadata boundary consumed no archive member content: audio decoded=false; JAMS content read=false; JAMS note events=0; Basic Pitch calls=0; GuitarSet prospective eval scores=0; V168 scores=0.

## V3 development trigger contract — NOW PREREGISTERED

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_TRIGGER_PREREGISTRATION_20260902.md`
- creation commit `1c9a83c7e101824640a244c83e0a86637317b101`.

The trigger does not change frozen V2. For any event where ordinary V2 proposes `w != p`, it requires same-frame evidence at all four frozen V2 deltas 0.08/0.13/0.18/0.24 s. It computes:
- `consensusFraction`: fraction of common-frame winners equal to ordinary V2 winner;
- normalized winner-vs-baseline advantage at each frame;
- `medianAdvantage` across four frames.

Only 8 frozen trigger candidates may be development-scored: consensus threshold `{0.75,1.00}` × median-advantage threshold `{0.05,0.10,0.15,0.20}`. No direction/player/style/tempo-specific thresholds.

Frozen development objective uses exactly **177 tracks** (players `02/04/05` minus the three predeclared anomaly files). Basic Pitch configuration/model are identical to P3. Reference parser mirrors official GuitarSet code: `note_midi`, fallback `pitch_midi` only when absent; require six string annotations; pitch=`int(round(note.value))`; aggregate all events without dedup. Matching reuses exact-pitch one-to-one onset semantics at 100 ms primary and 50 ms strict.

A candidate qualifies only if: +>=0.25pp primary macro F1; primary combined micro not lower; each development player primary micro loss >=-0.10pp; strict50 combined micro not lower; event-count identity. Selection among qualifiers is deliberately conservative: **fewest changed pitches first**, then largest macro gain, then stricter consensus/margin. If none qualifies: `NO_DEVELOPMENT_SIGNAL` and evaluation stays sealed.

Development run must be two isolated jobs: audio-only candidate freeze first; reference-only scorer second. Evaluation players `00/01/03` are forbidden from both jobs.

At this checkpoint, after preregistration: GuitarSet JAMS note events read=0; GuitarSet Basic Pitch calls=0; development scores=0; prospective eval scores=0; V168 scores=0.

## NEXT SAFE ACTION

1. Implement the preregistered V3 common-frame trigger helper without changing frozen V2.
2. Implement audio-only development candidate generator for the 177 admissible `02/04/05` tracks.
3. Implement reference-only development scorer with the frozen JAMS parser and selection gate.
4. Add static/synthetic guards proving candidate has no JAMS/reference surface and scorer has no audio/Basic Pitch generation surface.
5. Save another checkpoint after all static guards PASS and **before** the first GuitarSet development inference or JAMS member read.
6. Only then run the isolated development study once.

GOAT approval remains independent; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
