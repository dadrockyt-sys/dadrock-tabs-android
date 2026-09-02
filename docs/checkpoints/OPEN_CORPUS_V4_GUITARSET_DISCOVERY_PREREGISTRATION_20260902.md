# Open-Corpus V4 GuitarSet Discovery — Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose

V3 closed with frozen `NO_DEVELOPMENT_SIGNAL`: all eight temporal-consensus / median-advantage gates harmed GuitarSet development accuracy. The next public-corpus step is therefore a **new V4 development-only hypothesis-generation phase**, not a V3 recovery and not a prospective evaluation.

The V4 discovery question is:

> Among already-frozen V3 trigger-eligible Basic Pitch events where ordinary V2 proposes an octave change, which **pre-existing reference-blind observables** distinguish changes that improve exact-pitch onset matching from changes that harm it?

This preregistration is frozen **before any new per-event GuitarSet reference analysis**. It does not define or promote a V4 trigger. It defines only the discovery partition, labels, allowed features, and outputs that may be examined to form a later separately frozen V4 candidate family.

## Data-use split

Reuse the immutable V3 candidate artifact only:
- original run `33581322528`;
- candidate artifact ID `9828683652`;
- candidate ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`.

No Basic Pitch inference, audio decoding, candidate regeneration, V2/V3 recomputation, or evaluation-player access is permitted in V4 discovery.

V4 development partition is frozen now:
- **discovery players:** `02`, `04`;
- **confirmation player:** `05`.

The discovery analysis may read only JAMS references for players `02` and `04`, excluding the already-declared anomaly tracks. Player `05` candidate/reference per-event outcomes are reserved for a later one-shot V4 development confirmation **after** a V4 trigger family and confirmation gate are frozen.

GuitarSet prospective-evaluation players `00/01/03` remain fully sealed and are forbidden from V4 discovery and confirmation design.

Discovery track counts are expected to be:
- player `02`: 59;
- player `04`: 58;
- total: **117**.

## Frozen reference semantics

Use the unchanged V3 development reference semantics:
- JAMS namespace `note_midi`, with `pitch_midi` fallback only if `note_midi` is absent;
- require six string annotations;
- pitch = `int(round(note.value))`;
- onset = `float(note.time)`;
- aggregate all six strings without deduplication;
- primary exact-pitch one-to-one onset tolerance = **100 ms**;
- strict secondary tolerance = **50 ms**.

No offset scoring is introduced in this discovery phase.

## Frozen event population

Analyze only events in the immutable candidate payloads satisfying all of:
- player is `02` or `04`;
- `triggerEligible == true`;
- `ordinaryV2ProposalDiffers == true`;
- ordinary V2 winner differs from baseline by exactly 12 semitones.

No V3 configuration threshold is used to filter the discovery population.

## Frozen counterfactual label

For every discovery event, compute a deterministic one-event counterfactual under the **same track-level one-to-one matcher** used by the V3 scorer.

For each tolerance independently:
1. score the complete frozen Basic Pitch baseline event stream for the track;
2. make a temporary copy in which **only this event's pitch** is replaced by its already-frozen `ordinaryV2Winner`; onset/end/amplitude and every other event remain unchanged;
3. score that one-event-swap stream against the same track reference;
4. define `deltaTP = swappedTP - baselineTP`.

Primary 100 ms event class:
- `beneficial` if `deltaTP > 0`;
- `neutral` if `deltaTP == 0`;
- `harmful` if `deltaTP < 0`.

Strict50 `deltaTP` is recorded as a secondary diagnostic only. The discovery script must not alter candidates or make multi-event counterfactuals.

Because event count and reference count are unchanged by a one-event pitch swap, delta TP is an exact monotonic proxy for the F1 direction for that isolated change under the frozen matcher.

## Allowed reference-blind features

Only fields already frozen in the immutable candidate payload may be associated with the counterfactual label:
- baseline MIDI pitch;
- ordinary V2 winner MIDI pitch;
- direction (`low` = V2 winner is baseline-12, `high` = baseline+12);
- Basic Pitch amplitude;
- event duration (`end-start`);
- `consensusFraction`;
- `medianAdvantage`;
- the four frozen per-frame advantages at deltas 0.08/0.13/0.18/0.24 s;
- derived reference-blind summaries of those four advantages: minimum, maximum, mean, range, population standard deviation, count >0, count >= median;
- the four common-frame winners and derived count/fraction equal to the ordinary V2 winner;
- baseline pitch class / octave derived solely from baseline MIDI pitch.

No feature may use JAMS/reference pitch, reference timing, correctness, player identity as a trigger feature, track/style/tempo metadata, or any prospective-evaluation information.

Player is allowed only as an analysis grouping column to check whether discovery patterns repeat across `02` and `04`; it is **forbidden** as a future trigger feature.

## Frozen discovery outputs

The discovery report may contain:
- population counts and beneficial/neutral/harmful rates overall and by V2 direction;
- feature summaries by event class;
- univariate quantile tables for amplitude, duration, consensus, median advantage, and the derived advantage summaries;
- simple threshold sweeps on the reference-blind features, reporting for each candidate threshold the number of events selected and counts/rates of beneficial/neutral/harmful one-event counterfactuals;
- the same threshold summaries separately for players `02` and `04` to expose player-specific instability;
- a labeled row table for the 117-track discovery partition only, for subsequent hypothesis formation.

Threshold sweeps are **exploratory only**. No threshold is automatically selected, promoted, or applied to player `05` or the prospective evaluation set by this run.

## Forbidden outputs / actions

This discovery phase must not:
- read any player `05` JAMS reference or compute player-05 per-event labels;
- read/extract any player `00/01/03` JAMS or audio;
- run Basic Pitch or decode audio;
- regenerate any candidate;
- modify frozen V2/V3 code;
- select a V4 trigger automatically;
- score any proposed V4 multi-event stream;
- run a V4 confirmation or prospective evaluation;
- modify V168 or GOAT policy.

## After discovery

After the discovery report is frozen and checkpointed, a later step may formulate a small V4 trigger family using only reference-blind features. That trigger family, its exact threshold(s), confirmation qualification gate, scorer, and deterministic selection rule must be preregistered **before** player `05` per-event references are used for V4 confirmation.

Only if a V4 design passes that internal confirmation may any future prospective-evaluation workflow be frozen. Players `00/01/03` remain one-shot prospective data until then.

## Counters at preregistration

- V4 discovery reference reads: **0**;
- V4 player-05 per-event reference reads: **0**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
