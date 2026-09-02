# Open-Corpus V3 — GuitarSet Fresh Player Split Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose

Freeze a fresh public, player-disjoint evaluation corpus **before any GuitarSet audio/reference content is processed by this project**. This corpus is for the next V169-style conservative octave-trigger study and is completely separate from V168/GOAT.

The preceding Guitar-TECHS P3 bridge is terminal `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`. Its aggregate lesson may motivate a conservative trigger, but P3 per-event reference outcomes are forbidden for V3 tuning.

## Official GuitarSet source

Authoritative public record selected:
- Dataset: GuitarSet
- Version: **1.1.0**
- Zenodo record: **3371780**
- DOI: **10.5281/zenodo.3371780**
- publication date: 2019-08-20
- official repository: `marl/GuitarSet`
- official repository README points to Zenodo record `3371780`.

Public record describes 360 approximately 30-second acoustic-guitar excerpts from 6 players with time-aligned pitch/string/fret/chord/beat/style annotations. The official project site describes 30 lead sheets per player in both comping and soloing form, with 5 styles, 3 progressions and 2 tempi, and microphone + hexaphonic recordings.

For this V3 lane use only the official **monophonic microphone** capture plus official JAMS annotation archive:
- `audio_mono-mic.zip`: 656.9 MB, official MD5 `275966d6610ac34999b58426beb119c3`;
- `annotation.zip`: 39.1 MB, official MD5 `b39b78e63d3446f2e54ddb7a54df9b10`.

Do not use the hexaphonic pickup channels in the prospective evaluation. They contain privileged per-string separation not available in ordinary user audio.

## Rights / redistribution boundary

The GuitarSet ISMIR paper carries a Creative Commons Attribution 4.0 International notice and states that the dataset audio/annotations and annotation code are freely available online. The official GitHub repository itself is MIT licensed. The current Zenodo page is open-access but its crawler-rendered Rights field does not expose a license string.

Therefore this lane is conservatively restricted to **research/development evaluation with attribution**. Do not redistribute GuitarSet audio/reference files through this repository or artifacts. Do not use GuitarSet to train a commercial deployable model unless the data-license scope is separately reconfirmed. Aggregate metrics, hashes, code and non-audio/non-reference metadata may be preserved.

## Publicly documented annotation anomalies — frozen before use

Official repository README / Zenodo v1.1.0 identifies known errors. Public issues document:

1. `04_BN3-154-E_comp`: annotation timing reported +0.409 s late;
2. `04_Jazz1-200-B_comp`: annotation timing reported +0.309 s late;
3. `02_Funk2-119-G_comp`: a duplicated MIDI-note annotation near 10.86 s.

These reports are integrity metadata, not model outcomes.

To avoid discretionary post-result exclusions, all three named files are assigned to the **development side** by the player split below and are prospectively excluded from any V3 trigger-fit objective. They may be inspected separately for tooling/integrity diagnostics but cannot influence the final trigger threshold or prospective evaluation score.

No evaluation-track exclusion may be introduced after candidate outcomes are seen except a hard file-decoding/hash/inventory failure, which must make the affected evaluation incomplete rather than silently changing the set.

## Player-disjoint split — frozen now

GuitarSet player IDs are `00` through `05`.

### Development players

- `02`
- `04`
- `05`

Purpose: V3 conservative-trigger feature/threshold development only.

Expected nominal track count: 180 before the three predeclared anomaly exclusions. The three anomaly tracks above are never part of the threshold-selection objective.

### Prospective evaluation players

- `00`
- `01`
- `03`

Use **all 60 tracks per evaluation player** (comping + soloing, all styles/progressions/tempi), nominal total **180 fresh evaluation tracks**.

This split was chosen before this project read any GuitarSet JAMS note event or ran any GuitarSet Basic Pitch inference. The evaluation players are not named in the currently documented official GuitarSet issues #4/#5 above.

No track may move between development and evaluation after any GuitarSet score is observed.

## Evaluation capture / reference binding

Prospective evaluation audio is the official `audio_mono-mic` file whose track stem matches the JAMS annotation stem exactly.

Reference is the six per-string `midi_note` annotations in the corresponding official JAMS file, aggregated into one guitar-note stream only by a scorer process after evaluation candidates have been frozen.

Exact JAMS parsing, integer pitch mapping, candidate/reference isolation, onset tolerances and V3 PASS/FAIL criteria must be separately frozen **before any evaluation-player candidate inference**.

## Development constraints

A V3 trigger may be developed using:
- Guitar-TECHS P1/P2 designated development evidence already consumed;
- GuitarSet development players `02/04/05` after the official file identities are frozen;
- synthetic/physics guards;
- the aggregate P3 lesson that applying V2 to every event changed 1121/4693 pitches and caused a large aggregate regression.

A V3 trigger may **not** use:
- Guitar-TECHS P3 per-event labels/errors;
- GuitarSet evaluation players `00/01/03` reference events or scores before the trigger is frozen;
- GOAT restricted data;
- Lenny/V168 reference data for V3 tuning.

## State at creation

At this checkpoint, by this project lane:
- GuitarSet audio downloaded: **false**;
- GuitarSet annotation archive downloaded: **false**;
- GuitarSet JAMS note events read: **0**;
- GuitarSet Basic Pitch inference calls: **0**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- V168 policies modified: **false**;
- GOAT restricted bytes read: **false**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

## Next safe step

Run a **metadata/path-only inventory** of the two official v1.1.0 ZIP archives, verify official MD5 plus observed SHA256, verify the expected player/track stem structure and exact mic/JAMS pair coverage, and preserve only metadata/hashes. Do not parse JAMS contents and do not run Basic Pitch in the inventory.

Only after that inventory is checkpointed should the V3 development-trigger contract be implemented.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
