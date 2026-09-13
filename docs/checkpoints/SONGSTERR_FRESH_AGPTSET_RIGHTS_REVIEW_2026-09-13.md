# Songsterr Fresh V6 — AG-PT-set Rights Review

Status: **REFERENCE-BLIND RIGHTS/METADATA REVIEW ONLY — NO CORPUS DOWNLOAD, NO CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Candidate

AG-PT-set / Acoustic Guitar Playing Technique dataset

- Zenodo record `10159492`
- DOI `10.5281/zenodo.10159492`
- version `v1`
- archive `aGPTset_z.zip`, approximately 6.7 GB
- archive MD5 published by Zenodo: `1dff8103f9ad6e1a86cee2e5e39cbe87`

No dataset archive bytes were downloaded or inspected in this review. Basic Pitch and V6 were not invoked.

## Authoritative rights findings

The Zenodo dataset page marks the record **Open**, but the surfaced record metadata contains no explicit Rights/License entry for the dataset/audio files.

Zenodo's own developer documentation distinguishes repository metadata from uploaded data files: Zenodo metadata is licensed under CC0, while data files may be open access and are subject to the license described in the record metadata. Therefore the facts that the record is openly downloadable and its bibliographic metadata is reusable do **not** establish a permissive license for `aGPTset_z.zip` when the record supplies no file license.

The associated 2024 AG-PT-set conference paper is published under CC BY 4.0. That publication license applies to the paper; it is not evidence that the separate 6.7-GB dataset/audio archive is CC BY 4.0.

The authors' `CIMIL/ExpressiveGuitar-TechniqueClassifier` GitHub repository is GPL-3.0 and its README describes classifier code plus links to feature-vector datasets. That software-repository license likewise does not establish a license for the separate Zenodo audio archive.

A 2025 open-access paper states that the training datasets are available at the AG-PT-set Zenodo DOI, but its article-level CC BY 4.0 rights statement covers the article and included article material, not automatically the externally linked Zenodo dataset.

## Decision

**AG-PT-set remains scientifically strong but is not legally audit-ready under the V6 product-validation path.**

Until the dataset/audio rights are explicitly supplied by an authoritative rights holder or the Zenodo record itself gains a clear permissive data-file license:

- do not download `aGPTset_z.zip`;
- do not run branch contamination selection as though rights had passed;
- do not freeze an AG-PT-set corpus-specific audit;
- do not run Basic Pitch, V6, alignment correctness, or any other model correctness on AG-PT-set;
- do not infer rights from `Open` access, the paper's CC BY 4.0 license, Zenodo metadata CC0, or the classifier repository's GPL-3.0 license.

If an authoritative permissive dataset/audio license is later established, the next gate remains a branch-specific contamination/history audit before corpus selection and before any real media/reference access.

## Policy boundary

No V6 method/scoring setting changed. No real-corpus correctness was exposed. Fail-closed authority remains:

- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
- Production unchanged
