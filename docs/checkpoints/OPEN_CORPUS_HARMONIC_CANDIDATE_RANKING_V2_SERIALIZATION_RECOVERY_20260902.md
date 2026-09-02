# Open-Corpus Harmonic Candidate Ranking V2 — Serialization-Only Recovery Boundary

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Scope

This checkpoint freezes the only permitted recovery after GitHub Actions run `33576456720` failed during V2 output serialization. This lane is V169-style public-corpus development only. It does **not** modify V168, GOAT selection, the frozen V168 Policy A/B pair, or any V168 scorer boundary.

## Frozen V2 evaluator

- file: `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`
- Git blob: `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`
- creation commit: `b2544a2c84bfbf75797be19481540286cd57a514`
- candidate set: `{midi-12, midi, midi+12}`
- score formula: `C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25`
- frozen success gate remains unchanged from the preregistration/workflow.

The evaluator blob above is now immutable for V2 recovery. No score weight, candidate set, alignment search, frame timing, harmonic band, tie-break, weak-fundamental definition, or success threshold may change during recovery.

## Failed run evidence

Actions run `33576456720`, job `100081401356`:

1. setup / Python / pinned CPU dependencies: PASS;
2. all four prospectively frozen synthetic V2 guards: `SYNTHETIC_GUARDS_PASS`;
3. P1 and P2 public Guitar-TECHS archives downloaded and official MD5 checks passed;
4. P1 archive SHA256 printed as `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`;
5. P2 archive SHA256 printed as `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`;
6. the first real capture (`P1-directInput`) entered `evaluate_capture(...)` and completed its in-memory computation;
7. the process then failed while serializing the report because a NumPy `int64` remained in metadata: `TypeError: Object of type int64 is not JSON serializable`;
8. no real capture summary/result was printed or written before the exception;
9. because the shell used `set -e`, P1 mic/amp, P2 DI and P2 mic/amp ranking commands did not run;
10. the V2 aggregate success gate did not run and no V2 result artifact was uploaded.

Thus one real P1-DI ranking computation occurred, but **zero real V2 ranking summaries were exposed**. This must not be described as a synthetic-only failure.

## Permitted recovery

A recovery may be run only if it is serialization-only and preserves the evaluator blob above exactly.

Permitted implementation:
- add a separate wrapper/adapter that imports the frozen V2 evaluator functions;
- recursively convert NumPy scalar/container values to ordinary JSON-compatible Python values **after** `evaluate_capture(...)` returns;
- write the same aggregate fields and run the already-frozen V2 success gate;
- verify the frozen evaluator Git blob before downloading any public audio;
- rerun the original four synthetic guards before real data;
- add a serializer-only synthetic guard proving NumPy scalar conversion works.

Forbidden during recovery:
- editing `evaluate_harmonic_candidate_ranking_v2_v169.py`;
- changing any V2 formula/weight/threshold/timing/candidate rule;
- adding a new candidate feature;
- inspecting per-note reference-grounded errors to tune V2 before recovery;
- weakening the frozen success gate;
- touching GOAT restricted data or any V168 scorer.

If the recovered V2 report passes or fails, checkpoint the exact result before defining any V3.

## V168 counters

- V168 prospective reference-facing score calls: **0**.
- V168 policies modified: **false**.
- GOAT holdout selection modified: **false**.
- GPU/CUDA/Modal use: **none**.
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
