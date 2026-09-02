# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is awaiting explicit owner approval/denial.
- No restricted GOAT bytes admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT selection contract and promotion gate unchanged.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate.

Controlled V2 Guitar-TECHS P1/P2 result remains 558/558 when an octave ambiguity is already known. P3 indiscriminate bridge remains terminal `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`.

## V3 GuitarSet — TERMINAL `NO_DEVELOPMENT_SIGNAL`

Development players `02/04/05` vs prospective evaluation `00/01/03` (still sealed). Frozen V3 scorer run `33582451429`, job `100099402236`: SUCCESS and terminal `NO_DEVELOPMENT_SIGNAL`. Never run V3 on `00/01/03`.

Immutable candidate artifact:
- original run `33581322528`;
- manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`;
- ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

## V4 discovery / family — `H72-D035` SELECTED

Discovery run `33582980473`, job `100101041812`: SUCCESS on players `02/04` only. Discovery report SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`; labeled rows SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`.

Frozen conservative family: octave-down only, baseline MIDI >=72, short duration. Exact family score run `33584036171`, job `100104285213`: SUCCESS. All three configs qualified; deterministic selection chose **`H72-D035`** (duration <=0.35 s).

Selected discovery exact gains:
- 157 changed pitches;
- primary combined micro **+0.05660328813645776 pp**;
- primary macro **+0.07533076559106178 pp**;
- player `02` primary micro **+0.010499238805181221 pp**;
- player `04` primary micro **+0.10091835704913876 pp**;
- strict50 combined micro **+0.061749041603405885 pp**;
- 0 negative-primary-TP tracks; 8 positive.

Score report SHA256 `ea8a15ad7d9bb436a3c7108e1cfe67231ac5d2dadf42580abdcc2832ed3339bf`; artifact ID `9829448816`; ZIP SHA256 `a34320aa04467fd9ca73736e63bb93a603c02b9954c04ebf771fd1eb2bf83cf6`.

Dedicated selected checkpoint `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_SELECTED_20260902.md`, creation commit `2dfb5e5a5f3b1ecb7195330de012a4c34a8df033`.

## V4 player-05 one-shot confirmation — FROZEN / NOT YET RUN

Confirmation preregistration is now frozen **before any player-05 V4 reference read**:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_PLAYER05_CONFIRMATION_PREREGISTRATION_20260902.md`;
- creation commit `3759e73563c5fc93f67407e5e3f9ea37a4e3d584`.

Only `H72-D035` may be tested. No threshold/family sweep is permitted on player `05`.

Frozen confirmation gate requires all:
1. event-count identity;
2. at least one changed pitch;
3. primary macro gain >0 pp;
4. primary combined micro gain >0 pp;
5. strict50 combined micro delta >=0 pp;
6. no player-05 track primary TP loss.

Frozen confirmation scorer:
- `validation/open_corpus/confirm_guitarset_v4_player05.py`;
- creation commit `064361cb8c9ad06beadd3dd03058cdcdfcf71e19`;
- blob `794011aa78524226ec47e74ca8dd91008eef629a`.

Static confirmation guards:
- workflow creation commit `91242148724556f1c19e6575a23e22d69db56fbe`;
- run `33584362102`, job `100105263075`: **SUCCESS / V4_PLAYER05_CONFIRMATION_STATIC_PASS**;
- no real JAMS/reference read, no audio, no Basic Pitch;
- player05ReferenceRead=false;
- player05ConfirmationScoreCalls=0;
- GuitarSet prospective evaluation score calls=0;
- V168 score calls=0.

This is the last checkpoint before real player-05 confirmation. Player `05` references have not yet been used for V4 confirmation.

## NEXT SAFE ACTION

1. Run exactly one real player-05 confirmation using the frozen scorer/gate and only `H72-D035`.
2. Before references, reverify original artifact identity, manifest hash, all 177 candidate hashes, and scorer blobs; candidateRegenerated=false; no Basic Pitch/audio.
3. Extract exactly 60 player-05 JAMS and no `02/04/00/01/03` JAMS.
4. If a scientific result is produced, do not rerun. Immediately checkpoint PASS or FAIL.
5. On FAIL: close V4 hypothesis and keep `00/01/03` sealed. On PASS: still keep `00/01/03` sealed until a separate prospective-evaluation contract is frozen.
6. GOAT remains independent V168 path.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
