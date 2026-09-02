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

Preregistration: `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`, commit `f0b966df4881311456b5c455161431d8a771114e`.

This is V169-style development only. No GOAT/Lenny reference tuning, no V168 mutation, no commercial-tab scraping, and no third-party audio committed to the repo.

### Replicated harmonic-fundamental signal

Frozen study script: `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`, creation commit `3f67a134f646cc35f12e9c49e545e8b0c1df5fd1`.

P1 checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P1_HARMONIC_RESULT_20260902.md`, commit `5ef3a3dff39e46e31527e2ef7824a655338a2539`.

P2 checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P2_HARMONIC_CONFIRMATION_20260902.md`, commit `4b6333f40c9c419bc7db6933c9b2497671a9fca7`.

Earlier known-reference harmonic comparison was 558/558 correct lower-vs-+12 choices across P1/P2 DI + mic/amp, including 137/137 weak and 69/69 very-weak cases. That motivated candidate-ranking V2 but was not an end-to-end candidate-selection test.

## Candidate-ranking V1 — terminal

V1 failed its prospective synthetic weak-fundamental guard before real ranking data. See `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V1_SYNTHETIC_FAIL_20260902.md`, commit `a506577498dce1583913e0a1fe23de1d0611f45e`. Real V1 ranking observations = 0. Do not reuse V1.

## Candidate-ranking V2 — CONTROLLED FEATURE PASS

Dedicated result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V2_PASS_20260902.md`;
- creation commit `38df953a637c12359a844b239bce08897c710c32`.

Frozen evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`;
- creation commit `b2544a2c84bfbf75797be19481540286cd57a514`;
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`.

Frozen formula: `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`; controlled candidate set `{midi-12,midi,midi+12}`.

Original run `33576456720` passed the four synthetic guards and verified P1/P2, but failed only during JSON serialization after the first real P1-DI in-memory computation. The frozen evaluator was not edited. A preregistered serialization-only adapter recovered the reports.

Recovery:
- adapter `validation/open_corpus/serialize_harmonic_candidate_ranking_v2_v169.py`, creation commit `c6f22de0b018d68b641b88e838ee052fc45f2e80`;
- workflow `.github/workflows/open-corpus-harmonic-candidate-ranking-v2-recovery.yml`, creation commit `d453a899e6e3e5588649e23600be32c3227f42b1`;
- Actions run `33577664874`, job `100085059794`: **SUCCESS**;
- exact evaluator/helper blob guards PASS;
- original synthetic guards PASS;
- serializer self-test PASS;
- aggregate status **`CANDIDATE_FEATURE_PASS`**, frozen gate failures `[]`.

Recovered controlled octave-ranking results:
- P1 direct input: **142/142 = 100%**; weak 67/67; very weak 44/44; false low/high 0/0;
- P1 mic/amp: **142/142 = 100%**; weak 40/40; very weak 21/21; false low/high 0/0;
- P2 direct input: **137/137 = 100%**; weak 19/19; false low/high 0/0;
- P2 mic/amp: **137/137 = 100%**; weak 11/11; very weak 4/4; false low/high 0/0.

Combined: **558/558 = 100%**, weak **137/137 = 100%**, very weak **69/69 = 100%**, with zero false-low and zero false-high winners.

Aggregate report SHA256: `f527313e5c24802eab1bc0c3ba38efdc3d3a08af9038eb4a5a22ea72d5d089b2`; artifact ID `9827261916`; artifact ZIP digest `0430246471afd5eafa8da6539502247028e13fc322bb41b90f6ee093c8291fe6`.

### Interpretation boundary

This is a genuine controlled octave-disambiguation breakthrough: V2 selects among three competing pitches using audio-only scoring and the reference is consulted only after winner selection. However, the candidate neighborhood is still centered on the ground-truth pitch. Therefore this is **not 100% transcription accuracy** and does not yet prove reference-blind candidate discovery, onset discovery, polyphonic transcription, or full tab generation.

## NEXT SAFE ACTION

Bridge from controlled ranking to **reference-blind proposal + frozen V2 octave correction** on previously unused public musical material.

Before any outcome is observed:
1. inventory a previously unused public archive using metadata/path names only;
2. freeze the exact reference-blind proposal engine, model identity, thresholds, event representation, V2 application rule, prediction-freeze/hash boundary, scorer, matching tolerances, and success/failure metrics;
3. candidate generation must receive audio only and must freeze/hash predictions before reference MIDI/JAMS is opened by the scoring stage;
4. use the frozen V2 evaluator without retuning any V2 formula/weights/timing based on P1/P2 outcomes;
5. prefer a genuinely new player/material partition (Guitar-TECHS P3 music is a strong candidate) so P1/P2 single-note outcomes are not recycled as the next validation set;
6. checkpoint all results before considering any V3.

Public Zenodo record `14963133` describes Guitar-TECHS P3 `Music` as full musical excerpts with synchronized per-string MIDI and provides `P3_music.zip`; P3 has not been used in the V2 candidate-ranking outcomes above.

GOAT approval remains independent; if it arrives, follow the already-frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each new scientific boundary and immediately on GOAT approval/denial.
