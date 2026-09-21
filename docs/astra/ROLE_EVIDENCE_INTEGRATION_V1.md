# Astra Role Evidence Integration V1

## Purpose

This layer connects the successful development evidence path to Astra's existing structure-conditioned note-evidence contract without importing song-specific rules or widening delivery authority.

The integration preserves five meaningful development states:

- `promoted-core`: reference-blind recurring/core note evidence.
- `promoted-technique`: role-supported technique recovery such as attacked-bend evidence.
- `recovered-recurring-onset`: an internal recurring-pattern gap recovered from raw onset evidence.
- `ambiguous`: competing pitch/role evidence remains unresolved.
- `unassigned`: no promoted pitch candidate is available for the requested role.

The existing explicit `rejected` state remains available for proposals that were resolved and deliberately not promoted.

## Contract boundaries

`roleEvidenceIntegrationAdapter.mjs` converts those streams into the existing `noteEvidenceAdapter.mjs` input contract. It does not bypass structure identity verification, nearest-slot verification, pitch ambiguity handling, duration evidence requirements or model-path validation.

If role evidence is `abstained`, the adapter refuses every promoted stream with `ABSTAINED_ROLE_EVIDENCE_CANNOT_PROMOTE`. Ambiguous or unassigned evidence may still be preserved so downstream diagnostics can explain why the role path abstained.

Evidence states must agree with the existing classification:

- promoted states require `unambiguous`;
- `ambiguous` requires classification `ambiguous`;
- `unassigned` requires `no-candidate`;
- `rejected` requires `rejected`.

Legacy note evidence with no explicit evidence state remains valid and is reported as `unspecified` by diagnostics.

## Delivery boundary

The integration adapter always returns `customerDeliveryEligible: false`. The existing `noteEvidenceEvaluator.mjs` remains the musical acceptance owner and continues to fail closed on unresolved role relevance, unresolved polyphony/pitch evidence, incomplete duration evidence or pending model-path validation. Even an evaluator pass would not itself bypass the separate Astra product/delivery policy.

No Gomyway MIDI values, measures, timestamps or reference labels are encoded in this adapter.

## Development baseline

The current exposed-development best remains the frozen recurring raw-onset recovery result:

- 118 TP
- 125 FP
- 85 FN
- precision 48.56%
- recall 58.13%
- F1 52.91%

This integration does not change that score. Its purpose is to carry the proven evidence categories into the actual Astra contract safely and deterministically.

No main or Production change is authorized by this document.
