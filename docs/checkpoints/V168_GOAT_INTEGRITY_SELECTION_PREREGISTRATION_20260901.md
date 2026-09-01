# V168 — GOAT integrity and deterministic holdout-selection preregistration

Date: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **PREREGISTERED BEFORE GOAT ACCESS / NO GOAT BYTES SEEN / NO ASSETS ADMITTED / SCORING NOT ARMED**

## Purpose

This checkpoint freezes the GOAT-specific integrity and holdout-selection rules **before restricted GOAT v1 files are available**. It supplements, and does not weaken or replace:

- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`;
- `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`;
- frozen base validator `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`;
- frozen provenance validator `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`.

V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V168 reference-facing score calls remain exactly **0**.

## Public evidence frozen before restricted access

The following public GOAT evidence was inspected before this preregistration:

1. `JackJamesLoth/GOAT-Dataset` README, Git blob `888ae24a02c79d17e291d755d524f35546e15ea7`:
   - describes GOAT as paired guitar audio recordings and tablatures;
   - reports **5.9 hours of unique high-quality direct-input electric-guitar recordings**;
   - separately reports **29.5 hours of amplifier-augmented audio**;
   - directs users to the restricted Zenodo v1 record for dataset access.
2. Public `render_amp.ipynb`, Git blob `c94e935b51cc6f68cd63b5cd1a9107013e7f4ef9`:
   - states amplifier/cabinet parameters were randomized;
   - shows an internal alignment-quality condition `f_measure_fine >= 0.75` for the re-amping workflow;
   - contains an internal example test split based on path names `Dani`, `Lithium`, and `Reptilia`;
   - explicitly warns that the final published dataset may have a different structure.
3. Public GitHub issue `JackJamesLoth/GOAT-Dataset#1`, open with no comments at inspection time, reports possible duration/EOF mismatches:
   - `item_96` and `item_110`: DI/amp audio reportedly roughly half the MIDI/GP duration;
   - `item_67`: final six note **offsets** reportedly slightly exceed audio EOF.

Issue #1 is an unverified third-party report, not a confirmed dataset defect. The three named items are therefore **not automatically excluded**. They must be treated by the same frozen integrity rules as every other item.

## Holdout unit and augmentation rule

The V168 holdout unit is one unique **base performance / base recording** paired to its professional reference.

For V168 evaluation:

- Use the original/direct-input (DI/clean/base) recording when GOAT v1 exposes it unambiguously.
- Do **not** treat `amp_1`–`amp_5`, other re-amped files, or other tonal augmentations of the same performance as independent holdout songs.
- Only one source-audio candidate may represent a given base performance in the V168 selected set.
- If a base-performance identity cannot be established from frozen GOAT metadata/path structure without using comparative scores, that row is not admissible.

This prevents augmented copies of the same played notes from falsely satisfying the >=2-independent-song gate.

## Reference layer rule

The professional reference must be an official GOAT annotation layer paired to the exact selected base performance, and must be prospectively transformable into the frozen V154 onset/pitch scoring contract.

Before admission, freeze:

- exact reference file bytes and SHA256;
- exact source-audio bytes and SHA256;
- exact source/reference pair binding;
- exact annotation layer/type used;
- deterministic reference-to-V154 time-grid transform identity;
- whether that layer/transform is model- or alignment-derived.

No alternative reference layer may be chosen because it scores a policy more favorably.

## Integrity checks allowed before selection

Integrity intake is isolated from candidate generation and comparative scoring. It may inspect only what is necessary to establish file identity, parseability, timing coverage, source/reference binding, and the predeclared metadata fields used for deterministic selection.

Allowed integrity facts include:

- non-secret item/base-performance/work/split/player identifiers exposed by GOAT v1;
- file names/paths, byte sizes, formats, sample rate/channel count, duration, and SHA256;
- reference format parse success;
- reference timing-span metadata needed to determine whether scored note onsets lie inside the source recording;
- deterministic transform compatibility with the frozen V154 measure/step + MIDI contract;
- boolean integrity pass/fail and frozen reason codes.

Selection/ranking must **not** use comparative Policy A/B scores, reference pitch distribution, note density, difficulty, musical style, model errors, or any other outcome-facing/content-performance statistic.

## Frozen duration/EOF rule

The frozen V154 primary endpoint uses note **onset position and MIDI pitch**; it does not use note duration or note-off time. Therefore EOF integrity is defined prospectively around scored onsets rather than note offsets.

For each candidate base performance:

1. Determine `sourceDurationSeconds` from the exact frozen source-audio file.
2. Using the chosen frozen reference transform, determine the timestamp of every reference event that would enter V154 combined-Guitar scoring.
3. Every scored reference onset must satisfy:
   - onset >= `0.000` seconds; and
   - onset <= `sourceDurationSeconds + 0.050` seconds.
4. A reference note **offset** extending beyond source EOF is not by itself an exclusion when its scored onset satisfies rule 3, because duration/offset is not part of the frozen V154 endpoint.
5. If any scored onset exceeds EOF by more than 50 ms, the item fails integrity with reason `REFERENCE_ONSET_OUTSIDE_SOURCE_EOF`.
6. If the reference cannot be deterministically transformed onto the V154 measure/step timebase without a manual/content-guided timing adjustment, the item fails with reason `V154_TIMEBASE_INCOMPATIBLE`.
7. Do not truncate reference events, drop out-of-range notes, time-stretch source audio, shift the reference, or invent a repair solely to make a failing item pass.

Consequences for the publicly reported anomalies are predetermined:

- `item_96` / `item_110` pass only if their actual restricted-v1 scored onsets all satisfy the same EOF rule; a roughly half-length source/reference mismatch should therefore fail naturally if later onsets lie outside audio.
- `item_67` is not failed merely because reported note offsets exceed EOF; it fails only if a scored **onset** violates the same rule or another frozen integrity check.

## Other frozen integrity failures

A candidate row is ineligible if any of the following is true before comparative scoring:

- source or reference file is missing, unreadable, zero-length, or hash identity cannot be frozen;
- exact source/reference base-performance binding cannot be established;
- source is an augmentation/re-amp rather than the chosen base DI recording;
- professional reference is model/candidate-derived in a manner prohibited by the existing V168 provenance contract;
- reference parse fails;
- V154 timebase transform is not deterministic/frozen;
- scored reference onset lies outside the source EOF rule above;
- the owner's grant/use conditions prohibit this non-commercial research evaluation or conflict with the frozen storage/use boundary.

No item may be excluded because Policy A or Policy B performs poorly on it.

## Deterministic selection hierarchy

Target V168 GOAT holdout size is **3 independent base performances/works** when at least 3 pass all frozen integrity/provenance gates. The minimum remains the already-frozen **2**.

Selection occurs only after the complete GOAT-v1 base-DI inventory has been frozen and each row has a score-blind integrity result.

### Tier 1 — official released test split, if unambiguous

If the granted GOAT v1 bytes/metadata contain an **official, unambiguous released split label** for the relevant base recordings:

1. restrict to integrity-pass base-DI rows labeled `test` by the released dataset itself;
2. group rows by released work/song identity so the selected set contains at most one base performance per work/song;
3. for each work/song, choose the representative row with the lexicographically smallest normalized stable base-item identifier;
4. order representatives by normalized stable work/song identifier, then normalized base-item identifier;
5. select the first 3 representatives; if only 2 exist, select both; if fewer than 2 exist, V168 becomes `INCONCLUSIVE / HOLDOUT_INSUFFICIENT`.

The public notebook's `Dani` / `Lithium` / `Reptilia` example is **not itself treated as authoritative released-v1 split metadata** because that notebook warns the final dataset structure may differ. Those names may determine selection only if the granted v1 metadata independently and unambiguously establishes them as its official released test split.

### Tier 2 — deterministic hash fallback if no official released split exists

If the granted GOAT v1 contains no official/unambiguous released test split, use this fallback and nothing else:

1. start from all integrity-pass unique base-DI rows;
2. require a frozen stable base-performance identifier and a frozen stable work/song identifier for every selected row;
3. group by work/song identifier and retain one representative per work: the row with the lexicographically smallest normalized base-performance identifier;
4. compute for each representative:
   `selectionDigest = SHA256("dadrock-v168-goat-v1-selection|" + normalizedWorkId + "|" + normalizedBasePerformanceId + "|" + sourceAudioSha256)`;
5. sort ascending by `selectionDigest`, then normalized work ID, then normalized base-performance ID;
6. choose the first 3 distinct works; if only 2 integrity-pass works exist, choose both; if fewer than 2 exist, declare `INCONCLUSIVE / HOLDOUT_INSUFFICIENT`.

No random seed, human preference, duration preference, note-count preference, genre preference, difficulty preference, or post-score substitution is allowed.

## Frozen fallback/insufficiency behavior

- If a selected item later fails **candidate generation for a technical reason before any reference-facing score**, do not silently substitute a different item after inspecting reference content or any score. Stop and checkpoint the failure. A replacement requires a separately justified, result-blind preregistration made before any scoring and must not weaken this integrity rule.
- If fewer than 2 selected items can be fully admitted under the existing two validators, V168 is `INCONCLUSIVE / HOLDOUT_INSUFFICIENT`; do not loosen admission criteria.
- Once the selected manifest is frozen, no selected song may be removed due to an unfavorable score.

## Intake order after access is actually granted

1. Freeze exact owner grant wording/date/conditions and GOAT record/version.
2. Freeze the complete restricted-v1 file inventory without generating candidates or scoring.
3. Identify unique base-DI rows and their non-secret stable metadata.
4. Freeze source/reference file hashes and pair bindings.
5. Run the frozen integrity rules above over the complete base-DI candidate pool.
6. Apply the deterministic Tier 1 or Tier 2 selection rule.
7. Create the >=2-song V168 holdout manifest for the selected rows.
8. Pass both existing frozen V168 validators.
9. Checkpoint all identities and selection receipt **before candidate generation is armed**.
10. Only then may a future reference-blind Policy A/B generation implementation be staged.

## Anti-leakage / no-repair boundary

Before the selected manifest and selection receipt are frozen:

- Policy A/B candidate generation remains unarmed;
- V168 reference-facing score calls remain 0;
- no score-driven item exclusion or substitution;
- no reference-event copying;
- no manual timing correction based on candidate/reference agreement;
- no use of GOAT annotations to tune thresholds or invent V169-style variants inside V168;
- no GPU/CUDA/Modal without fresh explicit user authorization;
- no `main` or Production modification.

## Project scoring state

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

This preregistration makes gate 4 safer and more executable but does not satisfy it. Gate 4 still requires actual granted rights/provenance, exact bytes/SHA256 pair binding, >=2 admitted independent songs, and both frozen validators passing.
