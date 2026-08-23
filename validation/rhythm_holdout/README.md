# Rhythm Professional Holdout Gate

This directory is **scorer-only validation infrastructure** for the final Jimmy PAIge Rhythm completion gate. It must never be imported by the analyzer, API analysis route, model runtime, separator, candidate generator, contextual inference path, or professional PDF renderer.

## Completion contract

Rhythm is complete only after this order succeeds on a fresh user-upload-equivalent run:

1. Analyze uploaded audio with the reference-free Rhythm pipeline.
2. Produce authenticated structured Rhythm events.
3. Canonicalize and freeze the exact structured/render event stream and its analysis safety flags.
4. Generate preview/full professional PDF data from that same frozen event stream. The renderer may not invent, correct, or replace musical content.
5. Verify the frozen scored-event hash and PDF-event hash are identical.
6. **Only after steps 1–5 are frozen**, allow the isolated scorer to open the professionally human-written Rhythm reference.
7. Score event and measure correctness against the holdout reference.
8. Require near-100 professional agreement with no critical musical mismatches before declaring Rhythm complete.

The professional reference is benchmark-only ground truth. It must not be used for training, tuning the scored run, candidate selection, chord inference, fret/string mapping, timing inference, technique inference, or any other runtime decision.

## Hard anti-leakage rules

A frozen analysis is eligible for holdout scoring only when all are true:

- `referenceFree === true`
- `professionalReferenceUsed === false`
- `referenceRuntimeInputUsed === false`
- the analysis/event hash was created before the reference file was opened by the scorer
- no runtime source file imports or reads `validation/rhythm_holdout/reference`
- the scorer never writes corrected events back to the analyzed result

Historical development references and benchmarks are not automatically valid holdouts. In particular, any reference previously supplied to analyzer context or used to tune development behavior is diagnostic history only.

## Professional score dimensions

The final scorer reports at least:

- note/pitch precision, recall, F1
- exact string/fret precision, recall, F1
- exact chord/voicing agreement at each onset
- exact and tolerant measure/step onset timing
- duration/sustain agreement
- ties and rests when represented by the reference
- supported technique agreement
- measure/section completeness
- false-positive and false-negative counts
- critical mismatch count
- frozen-event to PDF-event fidelity

The final pass threshold is intentionally stricter than existing structural quality gates. Structural consistency is necessary but cannot establish transcription correctness.

## Files

- `reference/reference.schema.json` — scorer-only complete event-level human-reference schema.
- `freeze_rhythm_analysis.py` — creates a canonical immutable event snapshot and SHA-256 manifest without reading the human reference.
- `score_rhythm_holdout.py` — opens the reference only after validating the freeze manifest and scores the frozen result.
- `verify_runtime_isolation.py` — static anti-leakage guard for production/runtime files.

Do not create `Final Rhythm Pipeline` until the full holdout score is near 100% and the PDF fidelity gate is exactly 100%.
