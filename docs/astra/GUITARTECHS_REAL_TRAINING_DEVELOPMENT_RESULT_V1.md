# Guitar-TECHS P1/P2 Real Training Development Result V1

Date: 2026-09-21  
Candidate: `astra_guitartechs_tabcnn_v1`  
Authoritative run: `35569391647`

## Outcome

The bounded random-initialized P1/P2 TabCNN training run completed both performer-disjoint folds under the frozen 2,500-iteration contract. **The development candidate failed the preregistered acceptance thresholds in both directions.**

### P1 train -> P2 validate

Selected checkpoint: iteration 1400.

Full opposite-performer validation:
- precision: **0.2019** vs required >=0.75
- recall: **0.3270** vs required >=0.60
- onset+string+fret F1: **0.2379** vs required >=0.67
- note-event completeness: **0.2325** vs required >=0.60
- active-union frame accuracy: **0.2445** vs required >=0.70
- abstention: **0.0000** vs allowed <=0.10

Per-content F1:
- chords 0.2104
- scales 0.3015
- singlenotes 0.1385
- PalmMute 0.2867

All are below the frozen per-content floor 0.55.

### P2 train -> P1 validate

Selected checkpoint: iteration 2300.

Full opposite-performer validation:
- precision: **0.1487**
- recall: **0.3062**
- onset+string+fret F1: **0.1894**
- note-event completeness: **0.1759**
- active-union frame accuracy: **0.2357**
- abstention: **0.0000**

Per-content F1:
- chords 0.1449
- scales 0.2899
- singlenotes 0.0919
- PalmMute 0.2837

Again every required quality floor fails.

## Two-fold aggregate

- macro onset+string+fret F1: **0.2136** vs required >=0.70
- macro completeness: **0.2042** vs required >=0.65
- cross-performer F1 gap: **0.0485** <=0.10
- cross-performer frame-accuracy gap: **0.0088** <=0.10

The model is consistently weak across performers rather than failing because of one anomalous performer.

## Evidence identities

P1->P2:
- Actions artifact `10630257769`, digest `sha256:564f30d82e3e5d7ac6b21b3a7ded3ceddff6d2fe457d877d1e92666997f7b2b6`
- result SHA-256 `024e5d2d3612732e85f2c0b812f223e602fcdf6e69f82ca8d5a2d0d0e89090f0`
- model SHA-256 `8dc70d94741e0b472e93481f498efafb7627445896594752b217e000f2832a83`

P2->P1:
- Actions artifact `10635588120`, digest `sha256:036189322b4eb5f5ca2f7eac6a82c8a3471cfd814355087f8d6452bb62306734`
- result SHA-256 `c6dcc9e557c7e030f523410e705c35e4e7fea3c994e490487c7755e3e2793950`
- model SHA-256 `d480cadf66fc0d98608c719252c34bdab4c3120252167e8786502b4332264841`

Frozen aggregate receipt: `docs/astra/GUITARTECHS_REAL_TRAINING_DEVELOPMENT_RESULT_V1.json`  
Receipt SHA-256: **`3edfcf97766bef89ea56429a7385107d99868dc948d867251bcc5f9066a18112`**

## Gate decision

- real training completed: yes
- development thresholds met: **no**
- threshold retuning after result: **forbidden**
- P3 opening eligible: **no**
- customer delivery eligible: **no**

P3 remains sealed. These failed fold models are evidence artifacts only and must not be promoted or delivered.
