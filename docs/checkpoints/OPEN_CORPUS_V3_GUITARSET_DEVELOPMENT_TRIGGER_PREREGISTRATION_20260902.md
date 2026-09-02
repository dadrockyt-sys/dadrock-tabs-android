# Open-Corpus V3 — GuitarSet Development Trigger Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose

Freeze the **development-only** V3 selective octave-trigger study before any GuitarSet JAMS note event is read and before any GuitarSet Basic Pitch inference is run.

This study addresses the frozen P3 aggregate lesson: the V2 harmonic selector is excellent when an octave ambiguity is already known, but applying it to every Basic Pitch event changed 1121/4693 events and caused a large aggregate regression. V3 therefore does **not** modify the frozen V2 score. It adds a conservative reference-blind gate deciding whether V2 is allowed to replace a Basic Pitch pitch at all.

This lane is separate from V168/GOAT.

## Frozen evidence boundary at creation

Already consumed development evidence allowed here:
- Guitar-TECHS P1/P2 controlled V2 result, including the already-frozen aggregate margins;
- synthetic/physics reasoning;
- the **aggregate** P3 lesson that always-on V2 was harmful.

Forbidden for V3 development:
- any P3 per-event reference outcome/error;
- any GuitarSet prospective evaluation player (`00/01/03`) audio inference, JAMS note-event read, or score;
- GOAT restricted data;
- V168/Lenny reference data.

At this document's creation:
- GuitarSet JAMS member contents read: **false**;
- GuitarSet JAMS note events read: **0**;
- GuitarSet Basic Pitch inference calls: **0**;
- GuitarSet development score calls: **0**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**.

## Provenance already frozen

GuitarSet v1.1.0, Zenodo record `3371780`, DOI `10.5281/zenodo.3371780`.

Metadata-only inventory PASS:
- checkpoint `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_METADATA_INVENTORY_PASS_20260902.md`;
- creation commit `45a2c8c6499af01f1218c86ecd71bb35b455cb83`;
- run `33579938898`, job `100091870033` SUCCESS.

Exact archive identities:
- `audio_mono-mic.zip` MD5 `275966d6610ac34999b58426beb119c3`, SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`;
- `annotation.zip` MD5 `b39b78e63d3446f2e54ddb7a54df9b10`, SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.

Exact normalized mic/JAMS pairing was verified for all 360 tracks, 60 per player.

## Frozen player partition

Development players:
- `02`
- `04`
- `05`.

Prospective evaluation players, still sealed:
- `00`
- `01`
- `03`.

The three publicly documented anomaly tracks are development-side but excluded **before opening their JAMS content or running development inference**:
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`
- `02_Funk2-119-G_comp`.

Therefore the frozen V3 trigger-fit objective uses exactly **177 development tracks**. The three anomaly tracks are not silently repaired, shifted, deduplicated, or scored for threshold selection.

## Frozen Basic Pitch baseline

Use the same reference-blind baseline runtime/configuration as the P3 bridge:
- Python 3.10;
- Basic Pitch `0.4.0`;
- TFLite runtime `2.14.0`;
- model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`;
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.70 ms`;
- minimum/maximum frequency unset;
- multiple pitch bends false;
- melodia trick true;
- MIDI tempo `120.0`.

Normalize events exactly as in the frozen P3 candidate generator: sort by `(start,end,pitch,amplitude)` and assign deterministic event IDs. No event may be added, removed, merged, split, deduplicated, or time-shifted by V3. Only pitch replacement is permitted.

## Frozen V2 selector

V3 must call the existing frozen V2 implementation without changing its constants or score:
- evaluator blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`;
- helper blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`;
- candidate set `{p-12,p,p+12}`;
- alignment `0.0 s`;
- V2 score `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`;
- V2 frame deltas `(0.08,0.13,0.18,0.24) s`;
- V2 analysis window `0.186 s`;
- tie break: smallest MIDI.

For each Basic Pitch event with baseline pitch `p`, compute the ordinary frozen V2 winner `w` exactly as in P3: each of `p-12`, `p`, `p+12` gets its own `best_candidate_window` result and `w` is the highest V2 score.

If ordinary V2 cannot obtain all three candidates, preserve `p` and mark the event trigger-ineligible.

If `w == p`, preserve `p`; the V3 gate never changes an event merely to demonstrate confidence in the existing pitch.

## New V3 reference-blind stability evidence — frozen formula

The only new V3 trigger evidence is **common-frame temporal consensus and winner-vs-baseline margin**. It uses the same frozen V2 FFT and `candidate_features` functions; no new spectral weights are introduced.

For an event where ordinary V2 proposes `w != p`:

1. At each frozen delta `d ∈ {0.08,0.13,0.18,0.24}` seconds, form exactly one FFT frame centered at `event.start + d` using the frozen V2 `fft_power_frame` settings.
2. On that **same frame**, evaluate the frozen V2 `candidate_features` score for `p-12`, `p`, and `p+12`.
3. The common-frame winner at delta `d` is the highest score, tie broken by smallest MIDI.
4. All four common frames must exist. If any is unavailable, preserve `p` and mark the event trigger-ineligible.
5. Define `consensusFraction = (# of four common-frame winners equal to ordinary V2 winner w) / 4`.
6. For every delta define normalized winner-vs-baseline advantage

   `A_d = (score_d(w) - score_d(p)) / (abs(score_d(w)) + abs(score_d(p)) + EPS)`.

7. Define `medianAdvantage = median(A_d over all four frozen deltas)`.

No P3 or GuitarSet reference information enters these values.

## Frozen small trigger family

Only the following **8** development candidates may be scored. No extra thresholds may be introduced after development outcomes are visible.

Consensus thresholds:
- `0.75`
- `1.00`.

Median-advantage thresholds:
- `0.05`
- `0.10`
- `0.15`
- `0.20`.

Cross-product candidate IDs:
- `C075-M005`
- `C075-M010`
- `C075-M015`
- `C075-M020`
- `C100-M005`
- `C100-M010`
- `C100-M015`
- `C100-M020`.

For candidate `(C,M)`, V3 changes `p -> w` **only** if all are true:
- ordinary frozen V2 produced all three candidates;
- `w != p`;
- all four common frames exist;
- `consensusFraction >= C`;
- `medianAdvantage >= M`.

Otherwise preserve the original Basic Pitch pitch `p`.

The rule is symmetric for downward/upward octave proposals. No direction-specific threshold or player/style/tempo/comp-vs-solo threshold is allowed.

No candidate may use Basic Pitch amplitude as a fitted threshold, note duration as a fitted threshold, track identity, player identity, style, tempo, chord labels, string labels, or reference-derived pitch-range information.

## Frozen reference semantics for development scoring

The official GuitarSet repository parser searches `note_midi` annotations first and falls back to `pitch_midi` only if no `note_midi` annotation is present. It rounds note values with `int(round(note.value))` and uses `note.time` / `note.duration` as onset/duration. V3 mirrors those public semantics exactly.

For every admissible development JAMS file:
1. load the JAMS file;
2. `jam.search(namespace='note_midi')`;
3. if and only if zero annotations are returned, use `jam.search(namespace='pitch_midi')`;
4. require exactly **6** string-note annotations; otherwise fail closed for the development study;
5. aggregate all six annotations into one guitar reference stream;
6. each reference event is `{pitch: int(round(float(note.value))), start: float(note.time)}`;
7. preserve every annotation event; do not deduplicate overlapping/same-pitch notes;
8. sort deterministically by `(pitch,start,stringIndex,eventIndex)` for serialization only.

The three already-excluded known anomaly files are skipped before JAMS loading and do not enter any threshold-selection metric.

## Frozen matching / metrics

Use the same onset-only exact-pitch one-to-one matching semantics as the frozen P3 scorer:
- primary tolerance: **100 ms**;
- strict secondary tolerance: **50 ms**;
- exact integer pitch required;
- matching is greedy one-to-one within each pitch after sorting onsets;
- no reference-driven alignment or time shift;
- no offset/duration criterion.

For Basic Pitch baseline and each of the 8 V3 candidates compute:
- per-track precision/recall/F1 at 100 ms and 50 ms;
- combined macro F1 = arithmetic mean of track F1 over the 177 admissible tracks;
- combined micro precision/recall/F1;
- per-player (`02`,`04`,`05`) micro metrics;
- total changed pitch count/rate;
- event-count identity.

## Frozen development qualification gate

A trigger candidate is **development-qualified** only if all are true:
- event-count identity is true for every track;
- primary 100 ms combined macro F1 gain vs Basic Pitch is **>= +0.25 pp**;
- primary 100 ms combined micro F1 is **not lower** than Basic Pitch;
- primary 100 ms per-player micro F1 loss is no worse than **-0.10 pp** for each of players `02`, `04`, `05`;
- strict 50 ms combined micro F1 is **not lower** than Basic Pitch.

These are development selection guards, not a prospective GuitarSet evaluation claim.

## Frozen selection rule

If **no** one of the 8 candidates is development-qualified:
- classify the V3 development lane `NO_DEVELOPMENT_SIGNAL`;
- do **not** open the sealed evaluation players;
- do not invent or tune another threshold from these same development outcomes without a separately preregistered new research lane.

If one or more candidates qualify, select exactly one using this deterministic lexicographic rule:
1. **fewest total changed pitches** across the 177 development tracks;
2. if tied, **largest primary 100 ms combined macro F1 gain**;
3. if tied, larger consensus threshold (`1.00` before `0.75`);
4. if tied, larger median-advantage threshold (`0.20 > 0.15 > 0.10 > 0.05`);
5. if still tied, lexicographically smallest candidate ID.

Rationale: V3 exists to prevent over-correction, so among candidates that demonstrate material development benefit without aggregate regressions, the least intervention is preferred.

## Candidate/reference isolation for the development run

Development must run as two isolated jobs.

### Job A — audio-only candidate freeze

- verify exact `audio_mono-mic.zip` identity;
- extract only the 177 admissible development-player microphone WAVs;
- no player `00/01/03` audio may be extracted or processed;
- no JAMS/reference archive/file may exist in the candidate workspace;
- delete source audio ZIP before candidate Python runs;
- run Basic Pitch exactly once per admissible development track;
- compute/freeze baseline plus all 8 candidate streams from the same baseline inference and frozen V2/V3 features;
- freeze/hash JSON-only candidate artifacts;
- upload no audio.

### Job B — reference-only development scorer

- starts only after Job A candidate artifact is frozen;
- Basic Pitch must not be installed/importable;
- verify candidate hashes before opening references;
- independently verify exact `annotation.zip` identity;
- extract only the 177 admissible development JAMS files;
- no player `00/01/03` JAMS file may be extracted/read;
- no audio file may exist in the scorer workspace;
- delete annotation ZIP before scoring;
- score all 8 frozen candidates and apply the frozen qualification/selection rule;
- preserve aggregate development report/hashes only; do not commit dataset references.

## Evaluation remains sealed

Even if a development candidate qualifies, the following must happen **before** any player `00/01/03` inference or JAMS read:
- checkpoint the complete development result and selected trigger identity;
- freeze the selected trigger implementation/blob;
- freeze evaluation candidate generator/scorer identities;
- freeze prospective evaluation PASS/FAIL/INCONCLUSIVE criteria;
- checkpoint a final pre-evaluation boundary.

Only then may the 180 evaluation tracks be consumed once.

## Standing safety

- P3 per-event outcomes are forbidden for V3 tuning.
- V168 policies/counters remain untouched.
- GOAT restricted bytes remain untouched.
- CPU only; fresh explicit authorization is required immediately before any GPU/CUDA/Modal use.
- `main` / Production must not be modified/merged/promoted without explicit user direction.

## NEXT SAFE ACTION

Implement the frozen V3 common-frame trigger helper, development audio-only candidate generator, and reference-only development scorer. Add synthetic/static guards proving candidate reference isolation and scorer no-audio/no-Basic-Pitch behavior. Checkpoint again **before** the first GuitarSet development inference or JAMS member read.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
