# V145 Rhythm Decoder Stage 2 — Frozen CPU Preregistration

Date: 2026-08-26 (America/Montreal)
Branch: `v143-contextual-prune-lobo`
Status: **CPU-only architecture experiment. No Modal/L4/GPU/live-audio execution authorized.**

## Why Stage 2 exists

Stage 1 proved a deterministic runtime-only evidence adapter, timing lattice, and constrained guitar-state decoder. It intentionally required a caller-supplied timing quantum and selected each evidence event's nearest timing candidate independently.

The accepted benchmark remains unchanged:
- Pitch Content: 35.4%
- Pitch + timing: 6.7%
- String/fret + timing: 5.5%
- Chord/voicing: 5.8%
- Measure coverage: 100%
- PDF event fidelity: 100%

The large gap between Pitch Content and Pitch+timing makes timing alignment the next isolated architectural target.

## Frozen Stage 2 architecture

`V5 Rhythm-separated events -> frozen Stage 1 normalization -> runtime timing-grid inference -> raw-onset simultaneity clusters -> cluster timing/state options -> global beam/Viterbi-style sequence selection -> decoded notes`

Stage 2 imports Stage 1 but does not modify Stage 1 blobs.

## Runtime isolation

Stage 2 may read only generated/runtime Rhythm evidence. Public runtime APIs must not accept:
- gold events;
- human reference events;
- FIT/validation/canary labels;
- scorer results;
- V144 candidate outcomes.

Stage 2 does not create new MIDI pitches. Every decoded MIDI value must equal one normalized generated evidence pitch.

## Timing-grid inference — frozen construction

Constants:
- minimum quantum: 0.050 seconds;
- maximum quantum: 0.500 seconds;
- maximum delta divisor: 4;
- minimum evidence events: 4;
- minimum grid support: 0.80;
- maximum supported normalized residual: 0.18 of a quantum;
- maximum median normalized residual: 0.12.

Candidate quantums are runtime-derived only:
1. sort normalized evidence onsets;
2. collect positive consecutive onset deltas;
3. for every positive delta and for the median positive delta, divide by integers 1..4;
4. retain quantums inside [0.050, 0.500];
5. round candidates to 6 decimal places and deduplicate.

For each candidate quantum:
- phase candidates are 0.0 plus every evidence onset modulo the quantum, rounded to 6 decimals;
- each onset residual is circular distance to the nearest grid point `(phase + k*quantum)`;
- normalized residual is residual / quantum;
- support is the fraction of evidence events with normalized residual <= 0.18;
- compute median and mean normalized residual.

A candidate is eligible only when support >=0.80 and median normalized residual <=0.12.

Eligible grids rank deterministically by:
1. higher support;
2. lower median normalized residual;
3. lower mean normalized residual;
4. larger quantum;
5. smaller phase.

If no candidate qualifies, Stage 2 fails closed and returns no inferred grid.

## Simultaneity clustering — frozen construction

Given an inferred quantum, normalized evidence is sorted by `(onset, midi, source_index)`.

A cluster starts at the first remaining event and may include following events only while their raw onset is within `0.30 * quantum` of the cluster's first raw onset.

This creates deterministic raw-onset chord/attack groups without reference data.

## Cluster options — frozen construction

For every event in a cluster, reuse frozen Stage 1 timing candidates with `max_shift_steps=1`.

A cluster timing onset is eligible only when that exact candidate onset exists for every event in the cluster. This keeps near-simultaneous notes together.

For each common candidate onset:
- use Stage 1 `enumerate_guitar_states` on the cluster MIDI inventory;
- require exact MIDI preservation, unique strings, standard tuning, max fret24, max fret span7;
- a cluster with no valid common onset/state has no options and is left undecoded rather than fabricated.

Local option cost is frozen to:
- sum of member timing costs;
- plus `0.25 * guitar_state.local_cost`.

## Global sequence decoder — frozen construction

Decode cluster options in raw-onset order with a bounded beam width of 64.

A path may extend only when the next decoded cluster onset is strictly greater than the previous decoded cluster onset. Separate attacks may not collapse onto one grid onset.

Transition cost is frozen to:
- `1.0 * Stage1.state_transition_cost(previous_state, current_state)`.

Total path cost is the accumulated local option cost plus transition cost.

Deterministic path tie-breakers are:
1. lower total cost;
2. lexicographically earlier sequence of candidate onsets;
3. lexicographically smaller `(midi,string,fret)` inventories.

Clusters with no valid options are recorded as undecoded and omitted from the beam state; they do not authorize pitch fabrication.

Each source event may appear at most once in decoded output.

## CPU proof targets

1. Recover a ~0.250-second grid from a jittered 0.250-second synthetic onset sequence.
2. Reject an unsupported/random onset set under the frozen support gates.
3. Cluster near-simultaneous synthetic chord notes deterministically.
4. Produce only cluster timing onsets shared by every member's Stage 1 lattice.
5. Decode each source event at most once.
6. Never duplicate a source event across neighboring lattice points.
7. Preserve every decoded MIDI exactly.
8. Use unique guitar strings within simultaneous decoded clusters.
9. Demonstrate transition cost can change the globally selected fingering while pitch inventory stays fixed.
10. Fail closed for >6-note/unplayable clusters.
11. Preserve input objects.
12. Expose no gold/reference/FIT/validation/canary runtime parameters.
13. Import no Modal package and invoke no GPU/live audio.

## Explicit non-goals

- No new pitch proposals.
- No octave correction.
- No waveform source separation.
- No edits to V5 or frozen Stage 1.
- No gold scoring during runtime construction.
- No changes to `/ai-tab`, Bass, Lead, `freezeReady`, main, or Production.
- No V144 Family #15 search.
- No Modal/L4/GPU/live-audio run.

## Promotion rule

This document authorizes only CPU implementation and synthetic/contract unit testing of Stage 2. A later live benchmark against the existing calibration scorer requires fresh explicit user authorization after Stage 2 implementation and CPU proof are frozen and checkpointed.
