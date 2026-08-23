# Rhythm Professional Holdout Gate

This directory is **scorer-only validation infrastructure** for the final Jimmy PAIge Rhythm completion gate. It must never be imported by the analyzer, API analysis route, model runtime, separator, candidate generator, contextual inference path, or professional PDF renderer.

## Completion contract

Rhythm is complete only after this order succeeds on a fresh user-upload-equivalent run:

1. Analyze uploaded audio with the reference-free Rhythm pipeline.
2. Produce authenticated structured Rhythm events.
3. Canonicalize and freeze the exact structured/render event stream and its analysis safety flags.
4. Generate preview/full professional PDFs from that same frozen event stream. The renderer may not invent, correct, or replace musical content.
5. Verify the frozen scored-event hash and PDF-event hash are identical (`pdfEventFidelity === 1.0`).
6. **Only after steps 1–5 are frozen**, allow scorer-only validation to open the professionally human-written Rhythm reference.
7. Require the human reference itself to pass `verify_reference_completeness.py`: complete source provenance, source SHA-256/page count, complete-source declaration, contiguous measure range, valid pitch/string/fret identities, and no duplicate onset/note identities.
8. Run the professional scorer against the frozen event stream.
9. Run `run_final_holdout_gate.py` so completeness, musical score, frozen-event identity and exact PDF identity are bound into one fail-closed final result.
10. Require near-100 professional agreement, zero critical musical mismatches and exact PDF-event fidelity before declaring Rhythm complete.

The professional reference is benchmark-only ground truth. It must not be used for training, tuning the scored run, candidate selection, chord inference, fret/string mapping, timing inference, technique inference, or any other runtime decision.

## Hard anti-leakage rules

A frozen analysis is eligible for holdout scoring only when all are true:

- `referenceFree === true`
- `professionalReferenceUsed === false`
- `referenceRuntimeInputUsed === false`
- the analysis/event hash was created before the reference file was opened by scorer-only validation
- no runtime source file imports or reads `validation/rhythm_holdout/reference`
- the scorer never writes corrected events back to the analyzed result

Historical development references and benchmarks are not automatically valid holdouts. Any reference previously supplied to analyzer context or used to tune development behavior is diagnostic history only.

## Reference storage policy

The actual professional human source and its event-level transcription are **not repository source files**. `reference/.gitignore` intentionally permits only the schema, inventory and ignore policy to be committed. A real reference must be placed temporarily in `validation/rhythm_holdout/reference/` only inside the isolated evaluation environment after the reference-free freeze/PDF gate has completed. Never commit the real holdout or a full event-level copy of copyrighted professional tablature.

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

- `reference/reference.schema.json` — schema for a complete scorer-only event-level human reference.
- `reference/reference-inventory.json` — provenance/exclusion inventory; does not contain the complete professional source.
- `reference/.gitignore` — prevents accidental repository commits of the real reference.
- `canonical.py` — exact V143 professional render-event canonicalization/hashing.
- `freeze_rhythm_analysis.py` — creates immutable event snapshot/manifest without reading human reference.
- `verify_pdf_event_fidelity.py` — requires exact frozen/PDF event equality.
- `verify_runtime_isolation.py` — static anti-leakage guard for production/runtime files.
- `verify_reference_completeness.py` — opens the reference only after freeze/PDF validation and rejects partial/inconsistent ground truth.
- `score_rhythm_holdout.py` — post-freeze professional musical scorer.
- `run_final_holdout_gate.py` — mandatory fail-closed orchestration of completeness + scoring + exact hash identity.

Do not create `Final Rhythm Pipeline` until the full holdout score is near 100%, critical mismatches are zero and PDF-event fidelity is exactly 100%.
