# PRE — Songsterr Fresh EGSet12 Untouched-Lineage Real Evaluation

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `08a87028f5ea683b670e96f4b71625ebfdbbb7fb`
Authority: user instruction `Record pre with my authorization`

Status: **FROZEN PRE — RECORDING AUTHORIZED; EXECUTION NOT AUTHORIZED**

## 1. AUTHORIZED SCOPE

This PRE prospectively freezes the next Songsterr Fresh real-evaluation/scoring boundary. The user's present authorization is interpreted narrowly as authorization to **record this PRE only**.

This authorization does **not** authorize downloading or opening EGSet12 audio or annotations for evaluation, running Basic Pitch or any other model on EGSet12, running the frozen qualifier on EGSet12, revealing predictions, calculating scores, inspecting correctness, tuning, threshold search, retries, production changes, customer-visible output, or any work on the archived V143/Gomyway pipeline.

After this PRE is committed and the current-state checkpoint is updated to its exact commit, work must stop at the execution boundary until a later explicit authorization.

## 2. SCIENTIFIC QUESTION

Evaluate the already-frozen Songsterr Fresh positive-core candidate on a real external electric-guitar population that has not previously been used for Songsterr-fresh model-output evaluation in this lineage, using prospectively frozen corpus identities, candidate semantics, reveal discipline, and scoring rules.

This is a research diagnostic. It does not establish calibrated correctness, production readiness, customer eligibility, or general real-world performance.

## 3. FROZEN CANDIDATE — NO CHANGES ALLOWED

The candidate under evaluation is exactly the already-frozen tri-state composition:

`S AND E AND O AND K`

where each component is the previously frozen Songsterr Fresh qualifier/evidence predicate represented by the current lineage at this PRE parent.

Composition semantics are frozen as follows:

- `corroborated` only when **all four** frozen predicates `S`, `E`, `O`, and `K` are positively satisfied for the exact proposal identity;
- any missing, malformed, unavailable, non-finite, or otherwise unresolved required predicate makes the composite result `insufficient` / abstention, not positive;
- any resolved required predicate that rejects makes the composite result rejected;
- proposal identity must be preserved end-to-end;
- no candidate-confidence field may rescue or promote a proposal;
- no raw `0.01` fallback is permitted;
- no rank/top-K rescue is permitted;
- no weighted-score rescue is permitted;
- no reattack rescue is permitted;
- no threshold sweep, parameter tuning, predicate substitution, post-hoc exclusion, or candidate rewrite is permitted after this PRE.

The superseded broad/raw `0.01` selection rule is explicitly **not** part of this evaluation. Historical experiments that used it remain historical only.

If the exact frozen implementation identities needed to realize `S AND E AND O AND K` cannot be reconstructed unambiguously from the Songsterr-fresh lineage before any EGSet12 media, annotation, prediction, or score is opened, execution must fail closed and a new PRE is required.

## 4. FROZEN EXTERNAL CORPUS

Corpus: **EGSet12 v1** — “twelve real & original solo electric guitar performances with diverse playing styles to evaluate guitar tablature transcription.”

Official record:

- Zenodo record: `11406378`
- version: `v1`
- publication date: `2024-06-01`
- expected evaluation performances: exactly `01` through `12`
- expected evaluation pair for each performance: `<NN>.wav` + `<NN>.jams`
- `.gp` files and the supplied TabCNN model are **not inputs** to this evaluation.

Frozen official file MD5 identities:

| Pair | WAV MD5 | JAMS MD5 |
|---|---|---|
| 01 | `2eb739c5fb73e6327bb47267afe3eddf` | `083c7dae8e6556c20b9a2d762e2c977f` |
| 02 | `69b8701ea9a81428a6346e0d3d4b9b85` | `848f984b17b261a65585e25fba977a33` |
| 03 | `28141f17e46399553c52f5ed27bc10e2` | `721ec50f570892f9cfa88fb1e22a6113` |
| 04 | `6fe2f6f915953e8ae28b8a84a7677d0f` | `87426719ac4353d73e1af09970c31eb1` |
| 05 | `3435348c2b6702524dade471be70e4eb` | `c5c2fd376031177e87a3eb4ad12d220c` |
| 06 | `9f7ead382f373259b466ccd1884ed173` | `5ababdcf7741400dc93768334f6c899d` |
| 07 | `77f752ab3e7a5c606a21ac7b0df4fa1c` | `e693844f4b46fd3831c7c4ee0a2c3aa8` |
| 08 | `a59f373c00b8a327b37ce28f6601404c` | `513e00c522d53adac0ed9966a5b4c8cd` |
| 09 | `593aec1394a905a0c8b255a847f54139` | `9f08cae003c6c3d9dc745c2e319496d4` |
| 10 | `123818ef1020102252192d9e7a231e07` | `8cbf70e1b086f4a8fe5cac79572635ae` |
| 11 | `4bbaecaaa3e58bef6bb15a6cd0979fe2` | `f392b5bba5f3b99866bba91cb4d35a9a` |
| 12 | `e1ee73508f37d5c28c69877a588665d2` | `21217bda094eb8f29edfd1ed2f23ba45` |

Any missing file, extra substituted performance, version mismatch, or hash mismatch invalidates the run and stops before scoring.

## 5. UNTOUCHED-RELATIVE-TO-LINEAGE PROVENANCE GATE

“Untouched” in this PRE means **untouched by the Songsterr-fresh evaluation/tuning lineage**, not unknown to the public. EGSet12 is a published research corpus and may have public third-party results.

Before any EGSet12 audio, annotation contents, model outputs, or correctness results are opened, an execution harness must perform a provenance preflight against the Songsterr-fresh repository/history and fail closed if it finds prior lineage exposure that could have influenced this candidate.

At minimum the preflight must search for:

- `EGSet12`;
- Zenodo record `11406378`;
- the exact `01.wav` … `12.wav` / `01.jams` … `12.jams` identities in Songsterr-fresh evaluation/result material;
- prior Songsterr-fresh predictions, scores, manual correctness reviews, threshold choices, or tuning decisions tied to this corpus.

The repository search performed before recording this PRE found no known `EGSet12` occurrence in the present Songsterr-fresh branch surface. That observation is not a substitute for the execution-time fail-closed provenance preflight.

Public papers, public third-party code, or external published EGSet12 scores do not themselves contaminate the lineage, but their reported performance numbers, per-track outcomes, or error examples must not be consulted to choose thresholds, scoring gates, exclusions, or candidate behavior before this first lineage evaluation.

If contamination is found, do not run. Record the provenance failure and require a new prospective corpus/PRE.

## 6. MODEL / RAW-PROPOSAL IDENTITY GATE

This evaluation requires raw note proposals before the frozen `S AND E AND O AND K` qualifier can be applied.

No model/package identity may be selected after seeing EGSet12 output. Before any EGSet12 media is opened, the execution preparation must resolve and freeze from authoritative Songsterr-fresh lineage material the exact proposal-generation identity, including:

- Python runtime;
- `basic-pitch` package version;
- Basic Pitch model artifact identity/hash when available;
- inference API/entry point;
- all non-default/default inference arguments that affect note proposals;
- audio decode/resampling/channel preprocessing;
- serialized proposal schema and ordering.

If that exact prior Songsterr-fresh proposal-generation identity cannot be established unambiguously, execution stops **before media access** and a new PRE is required. Do not silently install the latest Basic Pitch, substitute a model, choose new thresholds, or use an analyzer from the archived V143/Gomyway lineage.

The execution record must commit a machine-readable environment/identity manifest before prediction reveal.

## 7. AUDIO / ANNOTATION HANDLING

The twelve official WAV files are the only evaluation audio. The twelve matching official JAMS files are the only reference annotations.

Rules:

- no listening or manual waveform inspection before the first frozen score is complete;
- no manual annotation inspection for correctness before scoring;
- no `.gp` reference may be used by the prediction or qualifier path;
- no reference JAMS information may be made available to Basic Pitch or the qualifier;
- annotation parsing must be deterministic and schema-driven;
- reference note events must map unambiguously to finite onset time and integer MIDI pitch;
- if the official JAMS namespace cannot be deterministically converted to those fields without interpretation or manual correction, stop before scoring and require a new PRE;
- do not silently drop malformed tracks or notes;
- all 12 performances are mandatory for an authoritative first score.

## 8. FROZEN PREDICTION SETS

For each track preserve two prediction inventories with exact proposal identity:

1. **Raw proposals** — the prospectively frozen Basic Pitch proposal output before Songsterr-fresh qualification.
2. **Positive-core proposals** — exactly those raw proposals whose frozen composite status is `corroborated` under `S AND E AND O AND K`.

Resolved rejected proposals are not predictions in the positive-core score. `insufficient` proposals are abstentions and are not promoted.

The result must additionally report counts of raw, corroborated, rejected, and insufficient proposals per track and corpus-wide. Abstentions may not be converted to positive or negative by a fallback.

## 9. FROZEN NOTE-BIRTH SCORING

The first authoritative score is **pitch + onset note-birth scoring**. Duration/offset is not part of this first boundary score.

A predicted note birth may match a reference note birth only when:

- predicted MIDI pitch equals reference MIDI pitch exactly; and
- absolute onset-time difference is `<= 0.050` seconds.

Matching is one-to-one. For each track and MIDI pitch independently, choose the matching that maximizes the number of matched pairs under the `50 ms` tolerance; ties must be resolved deterministically by minimum total absolute onset error and then stable chronological/index order.

From that matching compute:

- `TP` = matched predictions;
- `FP` = unmatched predictions;
- `FN` = unmatched reference note births;
- precision = `TP / (TP + FP)` when denominator > 0, otherwise `0`;
- recall = `TP / (TP + FN)` when denominator > 0, otherwise `0`;
- F1 = harmonic mean of precision and recall when defined, otherwise `0`.

Report prospectively:

- per-track raw-proposal TP/FP/FN/precision/recall/F1;
- per-track positive-core TP/FP/FN/precision/recall/F1;
- corpus-micro raw-proposal metrics from summed TP/FP/FN;
- corpus-micro positive-core metrics from summed TP/FP/FN;
- arithmetic macro mean of the 12 per-track precision, recall, and F1 values for each inventory;
- raw/corroborated/rejected/insufficient proposal counts and positive-core retention fraction.

No onset-tolerance sweep, best-case alignment, octave forgiveness, pitch-class forgiveness, post-hoc track exclusion, manual rematching, or metric substitution is allowed.

## 10. NO PROSPECTIVE PASS THRESHOLD

This PRE intentionally freezes a **measurement**, not a pass/fail performance threshold. No scientifically justified untouched-corpus acceptance threshold was previously frozen for EGSet12 in this lineage.

Therefore the first authoritative result must report the fixed metrics above without inventing a success gate after reveal. The result may state deterministic arithmetic deltas between raw and positive-core inventories, but must not reinterpret those deltas as a calibrated production pass.

Any later acceptance criterion, calibration claim, or model-selection use requires a new prospective PRE on data not already consumed for that decision.

## 11. REVEAL / FIRST-RUN DISCIPLINE

The first execution, if separately authorized later, must preserve a strict reveal boundary:

1. verify exact PRE commit and branch ancestry;
2. pass the untouched-lineage provenance gate;
3. resolve/freeze the exact proposal-generation environment before media access;
4. verify all 24 frozen WAV/JAMS hashes;
5. generate raw proposals once per track with the frozen model identity;
6. qualify those proposals once with exact frozen `S AND E AND O AND K` semantics;
7. parse the reference annotations and score once with the frozen note-birth scorer;
8. write complete machine-readable per-track and corpus summary artifacts;
9. only after the score artifacts are complete may human-readable predictions, per-track correctness, or aggregate metrics be revealed.

The first successfully started evidence-producing run is authoritative. Do not cancel/restart to improve an outcome.

An infrastructure failure before predictions/reference scoring may be recorded as such, but no changed dependency, alternate model, changed preprocessing, changed threshold, changed scorer, or rescue retry is allowed under this PRE without another prospective authorization/PRE.

## 12. RESULT RECORD

A later separately authorized execution must freeze its first result in a new immutable POST/RESULT checkpoint containing at least:

- this PRE commit SHA;
- exact execution-code/workflow commit SHAs and Git blobs;
- run/job/attempt identity;
- exact 24 corpus file hashes;
- provenance-preflight result;
- exact Python/package/model/preprocessing manifest;
- raw proposal artifact hashes;
- qualifier output artifact hashes;
- scorer artifact/hash;
- all required per-track and aggregate metrics;
- raw/corroborated/rejected/insufficient counts;
- any infrastructure deviation/failure stated exactly;
- explicit statement that no post-reveal tuning or rescue rerun occurred.

Then update `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.

## 13. GLOBAL AUTHORITY — UNCHANGED

Recording this PRE changes no production/customer authority. Keep existing global safety/authority flags and prior checkpoint restrictions unchanged, including no implication of calibrated correctness, no customer eligibility, and no delivery advancement.

This PRE does not authorize changing `main`, Production, protected-song behavior, or any customer-visible route.

## 14. EXPLICIT PROHIBITIONS

Under this PRE do not:

- resume or use the archived V143/Gomyway pipeline;
- consult archived Gomyway outputs to choose EGSet12 thresholds or model identity;
- inspect EGSet12 predictions or correctness before the frozen scoring artifact exists;
- listen to EGSet12 for manual validation before score reveal;
- alter `S`, `E`, `O`, `K`, their tri-state composition, or their thresholds after this PRE;
- use raw `0.01`, rank/top-K, weighted score, reattack rescue, or candidate-confidence rescue;
- tune Basic Pitch thresholds on EGSet12;
- exclude difficult tracks/notes after seeing results;
- substitute another corpus/file/version on failure;
- trigger an execution from the act of recording this PRE.

## 15. STOP CONDITION

The only action authorized by the user's current instruction is to commit this PRE and update the Songsterr Fresh current-state checkpoint to the exact PRE commit.

**STOP after recording. Real/model execution remains blocked pending later explicit authorization.**
