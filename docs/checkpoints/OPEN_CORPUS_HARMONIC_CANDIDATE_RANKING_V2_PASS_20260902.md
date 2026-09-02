# Open-Corpus Harmonic Candidate Ranking V2 — PASS

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Status

**`CANDIDATE_FEATURE_PASS`** under the prospectively frozen V2 success gate.

This is a strong controlled octave-disambiguation result in the V169-style public-corpus development lane. It is **not** a V168 result and it is **not** an end-to-end transcription accuracy claim.

## Frozen V2 identities

- evaluator: `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`
- evaluator creation commit: `b2544a2c84bfbf75797be19481540286cd57a514`
- evaluator Git blob: `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`
- shared helper Git blob: `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`
- formula: `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`
- controlled candidate set: `{midi-12, midi, midi+12}`
- frozen gate per capture: overall true winner >=95%; false-low <=5%; false-high <=5%; when weak-fundamental count >=10, weak-fundamental true winner >=90%.

## Serialization recovery integrity

The original V2 run `33576456720` failed after the first real P1-DI computation because report metadata contained a NumPy `int64`. The failure exposed no real ranking summary. Recovery was preregistered at:

- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V2_SERIALIZATION_RECOVERY_20260902.md`
- creation commit `7364a977feda3cd147567aa58810be446472540b`.

Recovery used a separate JSON adapter and did **not** edit the frozen V2 evaluator.

Recovery adapter:
- `validation/open_corpus/serialize_harmonic_candidate_ranking_v2_v169.py`
- creation commit `c6f22de0b018d68b641b88e838ee052fc45f2e80`.

Recovery workflow:
- `.github/workflows/open-corpus-harmonic-candidate-ranking-v2-recovery.yml`
- creation commit `d453a899e6e3e5588649e23600be32c3227f42b1`.

GitHub Actions:
- run `33577664874`
- job `100085059794`
- conclusion **SUCCESS**.

CI verified the exact frozen evaluator/helper blobs, reran all four original synthetic V2 guards (`SYNTHETIC_GUARDS_PASS`), passed the serializer-only guard (`SERIALIZER_SELF_TEST_PASS`), verified both public Guitar-TECHS archives, ran all four unchanged capture evaluations, and applied the unchanged frozen V2 success gate.

## Public corpus identities

Guitar-TECHS Zenodo record `14963133`, public dataset.

- P1 `P1_singlenotes.zip`: official MD5 `ca0c4674dde3805574685a313f7c39eb`; observed SHA256 `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`.
- P2 `P2_singlenotes.zip`: official MD5 `40fbf03d8b04bb2cf42df20f36dc2254`; observed SHA256 `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`.

## Results

| Capture | All notes | Weak fundamental | Very weak fundamental | False low | False high | Median margin | p10 margin | Minimum margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 direct input | 142/142 (100%) | 67/67 (100%) | 44/44 (100%) | 0 | 0 | 0.182519130051707 | 0.11411288626883982 | 0.07663101931883953 |
| P1 mic/amp | 142/142 (100%) | 40/40 (100%) | 21/21 (100%) | 0 | 0 | 0.17788332599082704 | 0.11004139418024153 | 0.03318377986220758 |
| P2 direct input | 137/137 (100%) | 19/19 (100%) | 0 examples | 0 | 0 | 0.1384312802526718 | 0.09743480167126935 | 0.08399477590166902 |
| P2 mic/amp | 137/137 (100%) | 11/11 (100%) | 4/4 (100%) | 0 | 0 | 0.12080546974772742 | 0.08959205651440068 | 0.06970187015450094 |

Combined:
- all capture-note evaluations: **558/558 = 100%** correct controlled octave winner;
- weak-fundamental subset: **137/137 = 100%**;
- very-weak-fundamental subset: **69/69 = 100%**;
- false-low winners: **0**;
- false-high winners: **0**;
- frozen gate failures: **[]**.

## Report identities

- `P1-directInput.json`: SHA256 `85c39625dfd098e2dd33880f231c880624254b0a5b8798ef9569853018d8a586`
- `P1-micAmp.json`: SHA256 `31eb1c5b3dbfd801f7e5530d87a88612330793b84bed3ee3cc22048f51d1e53f`
- `P2-directInput.json`: SHA256 `c1b7139694c0e5f46739a930496f04c1194abad11705b5dc0b308d108b0815e5`
- `P2-micAmp.json`: SHA256 `b24dfe522903fac6c3cbd43cdc6abd65762072b8dbf3bb52aee6b0f4c2ac88f3`
- aggregate `candidate-ranking-v2-summary.json`: SHA256 `f527313e5c24802eab1bc0c3ba38efdc3d3a08af9038eb4a5a22ea72d5d089b2`
- artifact ZIP digest: `0430246471afd5eafa8da6539502247028e13fc322bb41b90f6ee093c8291fe6`
- artifact ID: `9827261916` (`harmonic-candidate-ranking-v2-recovery-reports`).

## Interpretation boundary

This is stronger than the earlier known-pitch harmonic study: the frozen V2 score actually chooses among three competing pitches using audio-only features, and ground truth is consulted only to evaluate the already-selected winner.

However, the three-candidate neighborhood is still centered on the reference pitch. Therefore this result demonstrates **perfect controlled +/-12-semitone disambiguation on this public two-player/four-capture single-note benchmark**, not arbitrary candidate discovery, polyphonic transcription, onset discovery, or end-to-end tab accuracy.

The next scientifically meaningful bridge is to freeze a **reference-blind proposal stage** first, generate candidate notes from audio without reading reference MIDI, freeze/hash those predictions, apply the already-frozen V2 octave selector, and only then score against a previously unused public music partition/player. No V2 retuning based on P1/P2 results is permitted for that bridge.

## V168 isolation

- V168 prospective reference-facing score calls: **0**.
- V168 Policy A/B modified: **false**.
- GOAT holdout selection modified: **false**.
- GOAT restricted bytes read: **false**.
- GPU/CUDA/Modal: **none**.
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
