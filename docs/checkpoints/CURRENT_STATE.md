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

Promoted I005 Guitar F1 **42.7940586109996%**, precision **48.54280510018215%**, recall **38.26274228284279%**, TP/pred/ref **533/1098/1393**; Bass F1 **80.45325779036827%**. Highest unpromoted `recur-gap1-earliest` = **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp threshold. No I006.

## SplitMySong diagnostic — terminal fail-closed

Checkpoint `docs/checkpoints/V168_SPLITMYSONG_HISTORICAL_SUPPORT_FAIL_CLOSED_20260901.md`, commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

Exactly one private observation: `FAIL_CLOSED_NO_CANDIDATE`; 1421/1471 required steps covered, 50 missing; candidate=false; referenceRead=false; scorerRead=false. Do not rerun, score, weaken, or interpolate.

## Parallel open-corpus breakthrough lane — V168 isolated

Preregistration: `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`, commit `f0b966df4881311456b5c455161431d8a771114e`.

### Harmonic signal and controlled V2 pass

Known-reference harmonic study replicated 558/558 lower-vs-+12 choices across P1/P2 DI + mic/amp, including weak 137/137 and very weak 69/69.

Candidate-ranking V1 failed synthetic guards before real ranking and is terminal.

Candidate-ranking V2 dedicated result:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V2_PASS_20260902.md`;
- creation commit `38df953a637c12359a844b239bce08897c710c32`.

Frozen V2 evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`;
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`;
- formula `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`;
- controlled candidates `{midi-12,midi,midi+12}`.

Serialization-only recovered Actions run `33577664874`, job `100085059794`: **SUCCESS** and `CANDIDATE_FEATURE_PASS` with no frozen gate failures.

Controlled results:
- P1 DI 142/142; P1 mic/amp 142/142;
- P2 DI 137/137; P2 mic/amp 137/137;
- combined **558/558 = 100%**;
- weak **137/137 = 100%**;
- very weak **69/69 = 100%**;
- false-low = 0; false-high = 0.

Aggregate report SHA256 `f527313e5c24802eab1bc0c3ba38efdc3d3a08af9038eb4a5a22ea72d5d089b2`.

Interpretation: real controlled octave-disambiguation breakthrough, but not end-to-end transcription because the three-candidate neighborhood remained reference-centered.

## P3 music — unseen reference-blind bridge is now frozen

Metadata-only inventory checkpoint:
- `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P3_METADATA_INVENTORY_20260902.md`;
- creation commit `cc1d9d3d4a168e6551935ab0445f20ea1e9134b4`.

P3 inventory workflow run `33577994728`, job `100086035966`: **SUCCESS**.

P3 archive:
- Zenodo record `14963133`, `P3_music.zip`;
- official MD5 `071ba80aecf00f4a31fbd167b3f22198`;
- observed SHA256 `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`;
- inventory SHA256 `e2237f182f8db4f896748a87b16b449eb42a06de03c3f98f06ace87dbe1e3765`;
- artifact ID `9827368055`.

Metadata paths show all 12 indices `01`–`12` have `midi_XX.mid`, `directinput_XX.wav`, `micamp_XX.wav`, plus ego/exo MP3. Inventory code did not open file contents; P3 reference note events read = **false**; P3 candidates = **none**.

Reference-blind bridge preregistration:
- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_PREREGISTRATION_20260902.md`;
- creation commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`.

Frozen P3 bridge design:
- all 12 works, both DI + mic/amp = 24 capture-work units;
- Basic Pitch 0.4.0 CPU/TFLite baseline with default thresholds and required model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`;
- each Basic Pitch event proposes `{p-12,p,p+12}` to the already-frozen V2 selector with alignment 0.0;
- correction may replace pitch only; no adding/deleting/merging/dedup/time shifting;
- candidate job extracts audio only, deletes source ZIP before candidate Python runs, freezes/hashes baseline and corrected streams;
- separate scoring job then verifies candidate hashes, re-downloads exact archive, extracts MIDI only, and scores without rerunning candidate generation;
- exact pitch, one-to-one onset matching; 100 ms primary and 50 ms strict secondary; no reference-driven alignment;
- PASS requires >=+0.25pp corrected combined macro F1 at 100 ms, no micro-F1 regression per DI/micAmp at 100 ms, no combined micro regression at 50 ms, event-count identity and all artifact guards;
- material regression conditions and `INCONCLUSIVE_NO_MATERIAL_GAIN` are prospectively frozen.

At this checkpoint **no P3 MIDI reference event has been read and no P3 Basic Pitch inference/candidate has been run**.

## NEXT SAFE ACTION

1. Run a no-P3-data CPU preflight for Basic Pitch 0.4.0/TFLite 2.14.0 and verify the required model SHA256.
2. Implement candidate-generator and scorer scripts exactly to the frozen P3 contract, with static guards that the candidate script exposes no reference/MIDI input.
3. Save another checkpoint before the first P3 inference.
4. Run the two-job reference-isolated P3 bridge once.
5. Checkpoint PASS/FAIL/INCONCLUSIVE before any V3.

No P3-driven tuning of Basic Pitch thresholds or V2 weights is permitted.

GOAT approval remains independent; if it arrives, follow the already-frozen GOAT intake/admission sequence before any V168 candidate/scorer arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each new scientific boundary and immediately on GOAT approval/denial.
