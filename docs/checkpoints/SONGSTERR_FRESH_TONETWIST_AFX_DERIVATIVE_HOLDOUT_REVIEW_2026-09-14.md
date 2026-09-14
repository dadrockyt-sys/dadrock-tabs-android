# Songsterr Fresh V6 — ToneTwist AFx Derivative Holdout Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference review only; no candidate media acquisition; no Basic Pitch/V6 correctness.

## Binding context

The frozen V6 method remains the preregistered method in `SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` (commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`), implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28` / blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`, and frozen external scoring framework commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS official reference-blind audit run `34754519541`, job `103716527380`, was rechecked before this review and remains `completed/success`. Its frozen result remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; Guitar-TECHS correctness remains prohibited.

## Candidate family reviewed

ToneTwist AFx Dataset, including the newer 2026 Zenodo effect-render releases and the authoritative dry-input descriptions.

Primary public evidence reviewed:

- Zenodo `20213970`, ToneTwist AFx Dataset: Audacity Effect - Reverb, published 2026-05-15.
- Zenodo `10901426`, ToneTwist AFx Dataset: Dry.
- Zenodo `10455730`, ToneTwist AFx Dataset: Dry with markers.
- ToneTwist project/publication descriptions documenting the dry-source composition and dry/wet effects-modeling purpose.

## Findings

1. **The 2026 releases are effect renders, not new independent guitar performances.** The new records apply audio effects to an existing shared dry-input pool. Multiple wet variants therefore cannot be counted as independent real-performance evidence under frozen V6 population rules.

2. **The dry pool is heterogeneous and mostly reuses already-governed or otherwise non-qualifying sources.** The authoritative descriptions list IDMT-SMT-GUITAR subsets, IDMT bass, Neural Amp Modeler material, private guitar data, and YouTube bass recordings. This does not establish a new untouched V6 guitar holdout population.

3. **No immutable independent performed note-level onset+pitch reference is established for the ToneTwist guitar material.** Synchronization markers and dry/wet latency alignment are audio-effect synchronization mechanisms; they are not performed-note ground truth.

4. **Effect multiplication cannot inflate V6-positive capacity.** Thousands of rendered blocks/settings from the same underlying dry performances remain derivative views of the same source performances.

5. **Rights are not established at the required performance level for the full heterogeneous source pool.** Even where individual ToneTwist records are openly downloadable, the reviewed public descriptions do not establish one explicit product-validation-compatible performance-audio rights chain covering every underlying guitar source, including private and YouTube-derived material.

## Frozen gate decision

ToneTwist AFx **fails pre-media V6 admission** and must not be acquired or scored as a replacement correctness holdout.

Decisive blockers:

- gate 1: full performance-audio rights chain not established for heterogeneous underlying sources;
- gate 3: no independent performed note-level onset+pitch truth;
- gate 4: effect/render multiplication is derivative and cannot establish independent population capacity;
- gate 5: source reuse (including already-governed IDMT material) prevents defensible untouched status for the family as a new holdout.

No candidate media was acquired. No V6/Basic Pitch correctness was exposed. No Modal, Vercel heavy-GPU, or L4 GPU compute was used.

## Governance state remains unchanged

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed

Next allowed action remains metadata-only search for genuinely new primary evidence, an authoritative rights change, or a newly established independent performed onset+pitch reference. Purpose-built procurement/contact/recording remains authorization-gated.