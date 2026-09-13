# Songsterr Fresh V6 — EG-IPT Metadata / Reference / Rights Review — 2026-09-13

## Scope and authority

This checkpoint is an immutable metadata/reference/rights disposition for EG-IPT on branch `songsterr-fresh-pipeline-v1` only. It does **not** reopen archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research, protected-song execution, `main`, or Production.

The frozen V6 method remains governed by:

- final-method preregistration commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`;
- implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, source blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- external-scoring framework preregistration commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

No V6 constant, Basic Pitch setting, audio path, matcher, tolerance, uncertainty rule, admission gate, stratum rule, or deferred-reveal/single-run rule is changed by this review.

## Candidate

EG-IPT is a real electric-guitar playing-technique corpus. Public descriptions report a large collection (52,320 files, more than 28 hours) and a dedicated direct-input capture path. Those properties make it potentially useful for technique-recognition research, but they are not sufficient for the frozen V6 external correctness protocol.

## Reference-truth review

The authoritative/public materials reviewed describe playing-technique/action labels and associated signal preprocessing. They do **not** establish a released, immutable, independent per-note reference stream that supplies both:

1. performed note onset timing; and
2. performed pitch/MIDI identity

for the real-guitar events required by the frozen V6 matcher.

Technique labels, class boundaries, silence trimming, onset detection, pitch estimation, or any other truth reconstructed from the candidate audio cannot substitute for such an independent performed reference. Doing so would convert an external-reference evaluation into a detector-derived/reference-generated evaluation and would violate the frozen V6 admission intent.

## Rights review

No explicit permissive dataset-media license suitable for this V6 product-validation path was established in the authoritative materials reviewed. Repository/code licenses, paper licenses, or open-download status are not assumed to grant rights to the underlying recorded performances unless the dataset media itself is expressly covered.

This rights uncertainty is an independent blocker; the missing immutable onset+pitch reference is already sufficient to reject admission.

## Binding disposition

**Decision: REJECT / NOT AUDIT-READY for Songsterr Fresh V6 external correctness.**

Reasons:

- no authoritative immutable independent note-level onset+pitch reference stream was established for the real recordings;
- no explicit permissive dataset-media license suitable for the intended validation path was established.

Accordingly:

- do **not** download or otherwise access EG-IPT media for V6 correctness;
- do **not** run Basic Pitch or V6 correctness on EG-IPT;
- do **not** run an admission/alignment audit merely to manufacture missing reference truth;
- do **not** alter the frozen V6 method in response to this candidate;
- revisit EG-IPT only if a later authoritative release supplies both an explicit usable media license and immutable independent performed note-level onset+pitch truth.

No model-correctness observation was made in this review.

## Authority remains fail-closed

Unchanged:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration work remains paused/unchanged
- Policy C remains `UNENROLLED`
- protected-song execution remains embargoed
- no Modal, Vercel heavy-GPU, or L4 run was used
