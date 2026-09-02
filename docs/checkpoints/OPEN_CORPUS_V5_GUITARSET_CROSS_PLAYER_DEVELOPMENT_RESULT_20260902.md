# Open-Corpus V5 GuitarSet Cross-Player Development — Result

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Terminal result

**V5 = `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL` / TERMINAL FOR THIS FROZEN FAMILY.**

The preregistered 48-config cross-player development family was scored exactly once on all admissible development players `02/04/05`. No configuration satisfied the frozen qualification gate, so no configuration was selected and prospective players `00/01/03` remain sealed.

## Execution identity

- Workflow: `.github/workflows/open-corpus-guitarset-v5-cross-player-development.yml`
- Run: `33584851641`
- Job: `100106765017`
- Head: `b328b3af8db7dd519d8672fb9a848a06cabf7543`
- Workflow conclusion: **SUCCESS**
- V5 development score calls: **1 / terminal for this family**
- V5 prospective evaluation score calls: **0**
- V168 prospective reference-facing score calls: **0**

## Immutable candidate source

The run reused the original frozen V3 candidate artifact without regeneration:

- original candidate run: `33581322528`
- original head: `f494e5b2f586ec335b16dcabce687e63bb1f88fb`
- candidate artifact ID: `9828683652`
- candidate artifact ZIP SHA256: `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`
- candidate freeze manifest SHA256: `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`
- all 177 candidate JSON hashes were reverified before references were read
- candidate regenerated: **false**

## Reference boundary

Exactly the frozen development references were admitted:

- player `02`: 59 tracks
- player `04`: 58 tracks
- player `05`: 60 tracks
- total development tracks: **177**
- total scored reference events: **28,115**

Prospective players `00/01/03` were not extracted into the development workspace. No WAV/audio was admitted, Basic Pitch was not importable or run, and no new prediction events were generated.

## Frozen family result

- config count: **48**
- qualified config count: **0**
- qualified config IDs: `[]`
- selected config ID: `null`
- status: **`NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`**

Baseline over the full 177-track development set:

- primary macro F1: **80.3621313923964%**
- primary micro F1: **76.62482566248256%**

Frozen result report:

- report SHA256: `445a79dba3992c0989f244046eca4d0fc855c3aff8d6f2e043054f3a04c87dda`
- artifact ID: `9829749729`
- artifact ZIP SHA256: `018a9bdcce7cbd2b58e6f2dce13a168c335d69b6649d34fa7c299aeb1e9326c2`

## Result interpretation — descriptive only

Some conservative rules produced small positive aggregate gains, but they did not meet the preregistered cross-player replication gate.

The largest combined-primary-micro gain was `P72-D035-M005`:

- combined primary micro: **+0.024407 pp**
- combined primary macro: **+0.029251 pp**
- changed pitches by player: `02=17`, `04=119`, `05=83`
- player primary-micro deltas: `02=0.000000 pp`, `04=+0.100918 pp`, `05=-0.032445 pp`
- player `05` had 2 negative-primary-TP tracks versus 1 positive track

It therefore failed the frozen requirement for strictly positive primary-micro gain in every player and the within-player track-direction constraint.

A more conservative near-signal, `P79-D035-M005`, avoided a negative per-player primary-micro delta but still did not qualify:

- combined primary micro: **+0.020921 pp**
- combined primary macro: **+0.022795 pp**
- combined strict50 micro: **+0.020921 pp**
- changed pitches by player: `02=2`, `04=75`, `05=58`
- player primary-micro deltas: `02=0.000000 pp`, `04=+0.040367 pp`, `05=+0.021630 pp`

It failed because player `02` had only 2 changes and exactly zero primary-micro gain, while the preregistration required at least 5 changes per player and a strictly positive primary-micro gain in every player.

These observations are descriptive post-result analysis only. They do not authorize threshold changes, family expansion, or prospective evaluation.

## Frozen decision

Because no config qualified:

1. this exact V5 48-config family is closed and must not be rerun or retuned;
2. no V5 prospective evaluation contract is armed;
3. prospective GuitarSet players `00/01/03` remain sealed;
4. no result from this open-corpus development changes V168/GOAT policy or counters;
5. any future GuitarSet development phase would require a separately justified, preregistered methodological boundary before further reference-facing work.

## Counters after result

- V4 player-05 confirmation score calls: **1 / terminal**
- V5 development score calls: **1 / terminal for this family**
- V5 prospective evaluation processed: **false**
- V5 prospective evaluation score calls: **0**
- V168 prospective reference-facing score calls: **0**
- GPU/CUDA/Modal: **none**
- `main` / Production: **untouched**

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
