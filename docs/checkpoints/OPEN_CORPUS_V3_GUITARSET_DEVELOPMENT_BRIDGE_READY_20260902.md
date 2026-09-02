# Open-Corpus V3 — GuitarSet Development Bridge READY

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Status

**READY FOR THE FIRST DEVELOPMENT-ONLY RUN.**

The V3 selective-trigger family, audio-only candidate generator, reference-only development scorer, exact player/anomaly boundary, and deterministic qualification/selection rule are now frozen and static-tested **before any GuitarSet development Basic Pitch inference or JAMS note-event read**.

This is not a transcription result. Prospective evaluation players `00/01/03` remain fully sealed.

## Preregistered contract

`docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_TRIGGER_PREREGISTRATION_20260902.md`
- creation commit `1c9a83c7e101824640a244c83e0a86637317b101`.

Development objective uses exactly 177 tracks:
- player `02`: 59
- player `04`: 58
- player `05`: 60.

The three public anomaly tracks are excluded before inference/JAMS loading:
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`
- `02_Funk2-119-G_comp`.

Evaluation players `00/01/03` are forbidden from both development jobs.

## Frozen code identities

Frozen V2 dependencies, unchanged:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py` blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`;
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py` blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

New V3 selective trigger:
- `validation/open_corpus/v3_selective_octave_trigger_v169.py`;
- creation commit `3d2f6baa3a222332adc9048d1fea8f3eb41ef697`;
- blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`.

Audio-only development candidate generator:
- `validation/open_corpus/generate_guitarset_v3_development_candidates.py`;
- creation commit `e817a61ca19aeed50ee38bf2547cf85ddedd7dcf`;
- blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`.

Reference-only development scorer:
- `validation/open_corpus/score_guitarset_v3_development_candidates.py`;
- creation commit `f2da4034ccbdb9c67c276afe7c8882f4ff955b1a`;
- blob `19ef54155735a6ac1e65441250b47d1572ac0380`.

Static workflow:
- `.github/workflows/open-corpus-guitarset-v3-development-static.yml`;
- creation commit `0a807f11d5f0525646894ffb8d6ce528980a2e1f`;
- blob `294fd97948c061878cb1b1fa39314ae204a9b994`.

## Trigger frozen before outcomes

Ordinary frozen V2 first proposes winner `w` among `{p-12,p,p+12}`. V3 may allow `p -> w` only when `w != p` and all four same-frame V2 checks at deltas 0.08/0.13/0.18/0.24 s exist.

Frozen trigger evidence:
- fraction of four common-frame winners agreeing with `w`;
- median normalized score advantage of `w` over baseline `p` across those four frames.

Exactly 8 threshold candidates are allowed:
- `C075-M005`
- `C075-M010`
- `C075-M015`
- `C075-M020`
- `C100-M005`
- `C100-M010`
- `C100-M015`
- `C100-M020`.

No player/style/tempo/direction-specific rule is permitted.

## Static/synthetic Actions PASS

GitHub Actions:
- run `33581122972`
- job `100095439483`
- conclusion **SUCCESS**.

PASS guards:
- exact frozen V2/helper/V3/candidate/scorer blob identities;
- trigger has no JAMS/reference/Basic Pitch reference surface;
- candidate has no JAMS/reference CLI/import surface;
- scorer has no audio/Basic Pitch generation surface;
- all scripts compile;
- exact 8-candidate trigger family asserted;
- trigger synthetic test PASS;
- candidate wrapper self-test PASS;
- scorer matcher/selection self-test PASS.

Trigger synthetic fixture confirmed:
- correct baseline fixture V2 winner MIDI 45 remains unchanged;
- octave-high baseline MIDI 57 produced ordinary V2 winner MIDI 45;
- common-frame consensus = **1.0**;
- median normalized winner-vs-baseline advantage = **0.40037115768886156**.

Scorer self-test reconfirmed P3-compatible matcher behavior:
- primary 100 ms synthetic TP = 2;
- strict 50 ms synthetic TP = 1;
- conservative selection fixture chose `C100-M020` because it had the fewest changed pitches among otherwise qualified candidates.

## Frozen development score gate

A trigger candidate qualifies only when all are true:
- event-count identity;
- primary 100 ms macro F1 gain >= +0.25pp;
- primary combined micro F1 not lower;
- each development player's primary micro F1 delta >= -0.10pp;
- strict 50 ms combined micro F1 not lower.

Among qualifiers choose, in order:
1. fewest changed pitches;
2. largest primary macro gain;
3. stricter consensus threshold;
4. stricter median-advantage threshold;
5. lexical candidate ID.

If none qualifies: **`NO_DEVELOPMENT_SIGNAL`** and the evaluation set remains sealed.

## Reference semantics frozen

Development scorer mirrors the official GuitarSet parser convention:
- `note_midi`, fallback `pitch_midi` only if absent;
- exactly six string annotations required;
- pitch `int(round(float(note.value)))`;
- onset `float(note.time)`;
- preserve all events without deduplication.

Exact-pitch one-to-one onset matching uses 100 ms primary and 50 ms strict tolerances with no reference alignment/time shift.

## Safety counters at READY boundary

- GuitarSet development audio downloaded for inference: **false**
- GuitarSet development JAMS downloaded for scoring: **false**
- GuitarSet JAMS note events read: **0**
- GuitarSet Basic Pitch inference calls: **0**
- GuitarSet development score calls: **0**
- GuitarSet prospective evaluation players processed: **false**
- GuitarSet prospective evaluation JAMS note events read: **0**
- GuitarSet prospective evaluation score calls: **0**
- V168 prospective reference-facing score calls: **0**
- GOAT restricted bytes read: **false**
- GPU/CUDA/Modal used: **false**
- `main` / Production: **untouched**.

## NEXT SAFE ACTION

Create and run the frozen two-job **development-only** workflow once:
1. Job A verifies the exact audio archive, extracts only the 177 admissible development WAVs, deletes the source ZIP, proves no JAMS/evaluation player files exist, runs Basic Pitch once per track, generates all 8 streams from the same baseline and freezes/hashes a JSON-only candidate artifact.
2. Job B verifies that already-frozen artifact, installs no Basic Pitch, independently verifies the annotation archive, extracts only the corresponding 177 development JAMS files, deletes the ZIP, proves no audio/evaluation player files exist, scores the frozen streams and applies the preregistered selection rule.
3. Preserve/checkpoint `V3_DEVELOPMENT_TRIGGER_SELECTED` or `NO_DEVELOPMENT_SIGNAL` before any prospective evaluation work.

No threshold/feature/scorer changes are allowed after development outcomes become visible in this lane.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
