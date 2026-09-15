# Songsterr Fresh — Model Note Qualification V1 Pre-Implementation Freeze

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `IMPLEMENTATION_AUTHORIZED_NO_MEDIA_MODEL_EXECUTION`

## User direction

The user instructed: `Lets fix the weak points of this pipeline and make it work.`

This authorizes engineering improvements to the fresh pipeline. It does **not** retroactively change the frozen EGFxSet repaired-smoke result, authorize another EGFxSet/Basic Pitch inference, authorize threshold tuning from that observed output, reopen V143/Gomyway, or change any global validation/customer/delivery authorization flag.

## Observed engineering weakness

The existing raw Basic Pitch transcription stage correctly preserves every emitted model proposal. The downstream builder `scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs`, however, currently converts every Basic Pitch note directly to `classification: unambiguous` with that note's MIDI selected. That means a model proposal is promoted without an independent qualification decision.

The deterministic core already supports fail-closed unresolved evidence, but it has no explicit state for a raw proposal that has been independently examined and rejected. Candidate confidence is already contractually diagnostic-only and must remain so.

## Frozen V1 repair semantics

The following rules are frozen prospectively before implementation:

1. **Raw model output is immutable evidence.** No Basic Pitch proposal may be deleted, rewritten, hidden, or relabeled inside the primary Basic Pitch artifact.
2. **Model emission is not sufficient for promotion.** A separate qualification sidecar must decide whether each raw proposal is corroborated, rejected, or insufficiently resolved.
3. **No output-derived confidence gate.** Basic Pitch candidate confidence remains diagnostic-only. No confidence cutoff or confidence-margin rule may be introduced from the observed EGFxSet values.
4. **Four deterministic evidence states.** The adapter will recognize:
   - `unambiguous`: independently corroborated proposal, eligible for promotion;
   - `ambiguous`: proposal exists but qualification is insufficient, not promoted and unresolved;
   - `no-candidate`: no pitch candidate exists, not promoted and unresolved;
   - `rejected`: proposal exists and independent qualification explicitly rejects it, not promoted but resolved-as-rejected.
5. **Rejected proposals remain inspectable.** Their candidate MIDI, confidence, provenance, timing and qualification provenance remain in evidence/diagnostics. Rejection is not deletion.
6. **Only `unambiguous` promotes.** `rejected`, `ambiguous`, and `no-candidate` never become pitch-resolved note events.
7. **Unresolved means genuinely unresolved.** `unresolvedOnsetCount` is `ambiguous + no-candidate`; an explicitly rejected proposal is not counted as unresolved.
8. **Polyphony resolution is fail-closed.** A qualified builder may declare `polyphonyResolved: true` only when every raw proposal is either independently corroborated or explicitly rejected. Any insufficient/missing qualification leaves it false or causes a hard identity/completeness failure.
9. **Exact proposal identity is mandatory.** Qualification must cover the exact Basic Pitch note identity and must match each `noteId`, MIDI and start time. Missing, duplicate, extra, or mismatched qualification rows fail closed.
10. **Independent qualification, not model confidence.** A future real-audio qualification producer must use independently derived onset/birth evidence or another prospectively frozen non-Basic-Pitch signal. It must not use reference tabs or the observed desired answer.
11. **No new media/model execution in this implementation step.** Initial implementation and validation use deterministic/synthetic fixtures only. Another EGFxSet or other real model run requires a separately frozen prospective execution scope and new explicit authorization.
12. **Legacy boundaries unchanged.** `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free. DSP/model tooling remains under `scripts/songsterr-fresh/`. Archived V143/Gomyway and closed/reserved data lines remain untouched.

## Initial implementation scope

- extend `songsterr_pipeline/noteEvidenceAdapter.mjs` with the explicit `rejected` classification and additive metrics;
- extend descriptive diagnostics to report rejected proposals without treating them as unresolved;
- add a new qualified model-note evidence builder rather than silently changing the legacy builder's historical contract;
- add deterministic unit/synthetic tests proving:
  - corroborated MIDI is promoted;
  - rejected MIDI is preserved but not promoted;
  - insufficient qualification remains unresolved and blocks polyphony resolution;
  - missing/extra/mismatched qualification fails closed;
  - changing candidate confidence does not change qualification/promotion;
  - every raw proposal remains accounted for.

## Authority boundaries

Global state remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The repaired EGFxSet smoke remains `FAIL_NON_AUTHORIZING_SMOKE` under its original prospectively frozen all-events scoring rule. This engineering repair does not rewrite that historical result.
