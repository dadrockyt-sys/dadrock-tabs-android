# Jimmy PAIge Astra — Independent Separator Review V1

Status: Milestone 7B candidate review; Banquet is technically promising but blocked
Date: 2026-09-19 UTC

## Candidate

Banquet / `kwatcharasupat/query-bandit` is the first reviewed separator in Astra's current search that is not a conversion or fine-tune of the blocked `htdemucs_6s` weight and has explicit bass and guitar-class support.

Frozen source evidence:

- repository: `kwatcharasupat/query-bandit`
- reviewed revision: `79ed5bb75e5c3a40cd319d9d990cee913fc65c26`
- repository license: MIT
- LICENSE Git blob: `227afbe7329cc553d2335a4cf5fd099473e9aad8`
- README Git blob: `d7287cebeeb4abbecad6bf7174a2430f8c720298`
- inference source Git blob: `9b4d19e75817187a70231ca0a7552d5633c0a7d8`
- MoisesDB setup-C config Git blob: `21b67e06ba8487218bfef1c4780adf17ce2ecc95`
- PaSST-conditioned model config Git blob: `0b157abc2f64b334803b6d89fd7b6ae28a0d5b31`
- PaSST query encoder Git blob: `a213f7854800d25349ceb584073ae7d748d9877c`

The official README describes Banquet as a 24.9M-trainable-parameter query-based system trained/evaluated on MoisesDB and reports guitar/piano performance relative to HTDemucs. Those upstream quality claims are not Astra quality evidence.

## Capability

The reviewed training configuration exposes explicit target classes including:

- `bass_guitar`
- `bass_synthesizer`
- `clean_electric_guitar`
- `distorted_electric_guitar`
- `acoustic_guitar`

This is materially better role evidence than a VDBO `other` stem. It still does **not** establish lead-versus-rhythm guitar. Astra therefore continues to abstain for lead/rhythm.

The official BYOQ inference function supports `use_cuda=false`, so a CPU code path exists. It uses 44.1 kHz audio and requires a ten-second query clip. Astra has not benchmarked CPU latency or memory and does not claim it fits the 1200-second analyzer budget.

## Exact released checkpoint identity

The official README points to Zenodo record `13694558` (DOI `10.5281/zenodo.13694558`) for model weights and recommends `ev-pre-aug.ckpt`.

Published record metadata observed without downloading the file:

- file: `ev-pre-aug.ckpt`
- size: 645.5 MB
- published MD5: `4dfb91d6d27c2dfd4992a15070915541`

Astra has not downloaded the checkpoint and therefore has not independently computed SHA-256.

## Rights boundary

The source repository is MIT and its README explicitly discusses commercial beneficiaries of the permissively licensed work. That establishes a permissive software-code posture, but Astra does **not** automatically extend the repository license to the separately deposited checkpoint.

The retrieved Zenodo record identifies the artifact and publisher metadata, but the evidence available to this review did not expose a checkpoint-specific license/rights statement. Zenodo's own documentation says reuse is governed by the license attached to the record. Therefore Astra leaves both development-evaluation and commercial-inference rights for the exact checkpoint unresolved rather than inferring them from the code license.

The training configuration also establishes MoisesDB lineage. Astra has not completed a commercial-use review of the training/data rights chain. That remains a separate blocker.

## Product integration blocker: query audio

The official `inference_byoq` path requires a separate ten-second query-audio file. Jimmy PAIge's customer flow supplies a song upload plus requested role; it does not presently supply or authorize a reference query clip.

The reviewed model config uses `PasstFiLMConditionedBandit`, and the reviewed PaSST wrapper's forward path accepts query audio and derives the conditioning embedding from that audio. No label-only inference path was identified in the canonical inference/model/query-encoder source inspected, and Astra has not frozen a safe precomputed-embedding interface.

An acceptable future integration would need one of:

1. a frozen, lawfully sourced query-audio library with explicit product-use rights and provenance;
2. an upstream label-only/query-embedding inference path that can be frozen without protected reference audio; or
3. another independent separator that directly emits bass/guitar stems.

No archived song-specific stems or protected legacy reference material may be repurposed as the query library.

## Current decision

Banquet is **technically promising for bass and generic guitar**, but it is **not development-execution-ready** because:

- exact checkpoint license is unresolved;
- exact checkpoint commercial inference permission is unresolved;
- training/data commercial-rights chain is unreviewed;
- Astra SHA-256 of the checkpoint is absent because no download occurred;
- CPU runtime budget is unverified;
- an authorized query-audio source is not defined;
- lead/rhythm distinction remains unavailable.

No model weight was downloaded, no model was imported or executed, no audio was opened, no paid service was used, and Production was untouched.

## Exact next action

Resolve the Zenodo checkpoint's authoritative license/rights metadata and inspect whether Banquet offers a label-only or precomputed-query-embedding inference path that can satisfy Astra's reference-blind product boundary. If checkpoint commercial terms are not explicit and permissive, leave Banquet blocked and continue the independent-model search. Do not download the checkpoint until rights are resolved.
