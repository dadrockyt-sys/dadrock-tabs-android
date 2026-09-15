# Songsterr Fresh V6 — Semantic Timbre Dataset pre-media rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/lineage screening only; no media/reference payload access and no correctness.

## Binding frozen context

- V6 method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- Frozen V6 implementation commit: `3a6cbb144fec5613ab6350deb6539297d713df28`; blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- External scoring framework preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.
- Guitar-TECHS audit run `34754519541`, job `103716527380` was rechecked immediately before this screening and remains `completed/success`; frozen audit decision C remains closed and Guitar-TECHS must not be scored.

## Candidate

Candidate: **Semantic Timbre Dataset for the Electric Guitar** (Joseph Cameron / Alan Blackwell; Hugging Face dataset `JoeCameron1/SemanticTimbreDataset`).

Public authoritative dataset metadata establishes:

- Apache-2.0 dataset license metadata;
- 275,310 monophonic electric-guitar audio files with string/fret-derived pitch identities;
- critically, the dataset card states that the original 690 clean Fender Stratocaster recordings come from **EGFxSet**;
- the larger corpus is produced by applying timbral processing to those EGFxSet source recordings.

Public sources consulted without opening candidate audio/reference payloads:

- `https://huggingface.co/datasets/JoeCameron1/SemanticTimbreDataset`
- `https://arxiv.org/abs/2603.16682`

## Frozen admission decision

**DECISION: REJECT BEFORE MEDIA ACCESS.**

Reason: this is not a new untouched real-guitar holdout population. Its clean source audio is explicitly derived from EGFxSet, a corpus already used in the active Songsterr Fresh research lineage and therefore exposed. Processing or expanding those same recordings cannot restore holdout independence. In addition, filename pitch/string/fret identities on isolated processed notes are not a new synchronized performance-level MIDI/JAMS reference population under the frozen external-scoring framework.

This rejection is based solely on public metadata and lineage. No candidate WAV, archive, annotation payload, or other media/reference object was downloaded or opened.

## Guardrails preserved

- no Semantic Timbre Dataset correctness observation;
- no Basic Pitch/V6 correctness execution;
- no change to V6 constants, Basic Pitch settings, audio path, matcher, tolerances, uncertainty, admission gates, strata, or deferred-reveal/single-run rule;
- no Modal run;
- no Vercel heavy-GPU run;
- no L4 GPU run;
- no reopening of V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research, protected-song execution, `main`, or Production;
- `modelValidationComplete:false`;
- `customerEligibleEvents:0`;
- `mayAdvanceDelivery:false`;
- duration unchanged/paused;
- Policy C remains UNENROLLED and protected-song work remains embargoed.

## Next permitted V6 action

Continue metadata/license/alignment screening for a genuinely new untouched real-guitar holdout. Do not inspect candidate correctness or media/reference payload until a candidate clears the frozen pre-media gates. Guitar-TECHS remains decision C and closed.