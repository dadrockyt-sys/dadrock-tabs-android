# V168 — External holdout candidate screening

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **CANDIDATE SCREENING ONLY / NO ASSETS ADMITTED / SCORING NOT ARMED**

This checkpoint records prospective external-dataset screening under the already-frozen V168 admission and provenance gates. It does **not** admit a holdout song, open a professional reference for scoring, generate a holdout candidate, or authorize a scorer workflow.

## Fixed screening boundary

A source is only a candidate until a complete >=2-song manifest passes BOTH:

1. frozen base admission validator `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`; and
2. prospective provenance companion `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.

Current V168 reference-facing score calls: **0**.

## Candidate 1 — EGSet12

Status: **PROMISING / NOT ADMITTED / BLOCKED ON REFERENCE-CORRECTION PROVENANCE + OFFICIAL USE-BASIS/BYTE-IDENTITY VERIFICATION**

### Why it is promising

The official EGSet12 release describes twelve real, original solo electric-guitar performances created as an evaluation set for guitar-tablature transcription. The associated paper describes the pieces as composed by a professional musician/guitar player and performed by a professional guitarist, and evaluates transcription systems across the 12-track set against ground truth.

The release exposes track-matched audio and annotation artifacts for tracks 01–12 (`.wav`, `.jams`, `.gp`). The authors' public AMT-Tools code provides an `EGSet12` dataset class and evaluation/inference path. Its JAMS loader extracts per-string `note_midi` annotations containing MIDI pitch plus onset/duration intervals, so the annotation representation is structurally capable of producing combined-Guitar note events.

External sources reviewed during screening consistently describe the release as CC BY 4.0, but the exact official rights/use-basis metadata still must be frozen from an authoritative source before admission; secondary summaries are not sufficient for the provenance manifest.

### Material unresolved issue — `jams_corrected`

The authors' public loader does **not** load ground truth from `jams/<track>.jams`. In `AMT-Tools/amt_tools/datasets/EGSet12.py` it resolves annotations from:

`jams_corrected/<track>.jams`

The authors' inference experiment name likewise includes `Jams_corrected`.

The currently inspected public code repository does not contain the `jams_corrected/` annotation files or a documented transformation explaining how they differ from the published Zenodo `.jams` files. The commit history inspected for `EGSet12.py` also did not expose a correction derivation.

Therefore the published JAMS must **not** be labeled `professional_scorer_ready` by assumption. Before EGSet12 can be admitted, the exact professional-reference artifact used for V168 must have traceable correction provenance and a frozen SHA256 identity tied to the exact audio recording.

### Prospective no-cherry-picking rule if EGSet12 later qualifies

If the EGSet12 reference/provenance issue is resolved and the dataset satisfies both frozen admission gates, the preferred prospective unit is **all 12 published tracks**, not a post-hoc subset of two. This matches the dataset's benchmark purpose and avoids choosing easier/favorable tracks after seeing any V168 outcome.

No track has been selected, admitted, generated, or scored at this checkpoint.

## Candidate 2 — GuitarSet

Status: **NOT ADMITTED / PROFESSIONAL-REFERENCE PROVENANCE NOT YET SUFFICIENT FOR FROZEN V168 CONTRACT**

GuitarSet is a large paired guitar-audio/annotation dataset with rich note/string annotations and broad research use. However, its annotation construction is described as substantially automated using the hexaphonic recording setup, and annotation errors are documented in the dataset history.

That makes it useful research data but does not, without additional independently reviewed provenance, satisfy V168's strict `professional_scorer_ready` meaning. Do not relabel automated dataset annotations as professional ground truth by assumption.

## Candidate 3 — Guitar-TECHS

Status: **NOT ADMITTED / PROFESSIONAL-REFERENCE PROVENANCE NOT YET SUFFICIENT**

Guitar-TECHS contains recordings from professional guitar players and synchronized MIDI labels. The synchronized labels are obtained through an instrument/MIDI-pickup capture path rather than an independently established professional note-event transcription.

This is promising for general transcription research but currently does not clear V168's professional-reference provenance gate without a documented human/professional validation layer.

## Candidate 4 — IDMT-SMT-Guitar

Status: **NOT ADMITTED / USE-BASIS + PROFESSIONAL-REFERENCE PROVENANCE UNRESOLVED**

IDMT-SMT-Guitar provides paired WAV/XML guitar-transcription data, including note/event parameters, and includes short monophonic/polyphonic music recordings. It remains a candidate only because the exact use/license basis and the provenance needed to classify its annotations as V168 `professional_scorer_ready` have not been frozen.

## Frozen V154 scorer compatibility finding

The frozen scorer implementation remains:

`validation/v154_cpu_multitrack/score_frontend_reference.py`

Git blob: `9644e65719fbd361a9b39778ae9950c5e983e855`.

Its core `score_stream()` matching algorithm is song-generic: same-measure/same-MIDI maximum-cardinality matching followed by minimum total timing error, using the frozen primary/gross tolerances.

However, the frozen CLI loaders and `main()` explicitly require the generated/reference song identity to be **Lenny Kravitz — Are You Gonna Go My Way**. Therefore a future V168 holdout must **not** claim that the V154 CLI directly ingests arbitrary new songs unchanged.

If and only if a valid external holdout is admitted first, a future prospective V168 scorer adapter may be staged that reuses the unchanged frozen `score_stream()` algorithm while supplying a new-song normalization/input layer. Such an adapter must be frozen before any V168 reference-facing score call and must not alter matching semantics or thresholds.

No such scorer adapter is implemented or armed now.

## Current conclusion

- EGSet12 is the strongest screened acquisition candidate.
- EGSet12 is **not admitted** because the exact `jams_corrected` ground-truth provenance and official frozen rights/use-basis still need resolution.
- GuitarSet, Guitar-TECHS, and IDMT-SMT-Guitar remain secondary candidates and currently do not satisfy the strict professional-reference provenance contract.
- No external audio/reference bytes have been admitted into the V168 holdout manifest.
- No holdout candidate generation is armed.
- No scorer workflow is armed.
- V168 reference-facing score calls remain **0**.
- `main`/Production remain untouched.
- GPU/CUDA/Modal remain unused and unauthorized.

## Next safe investigation

1. Search the EGSet12 authors' public repository history/issues/releases and official release metadata for the provenance of `jams_corrected` and any alignment/correction procedure.
2. Resolve the authoritative use/license basis for the exact audio/reference artifacts.
3. Do not inspect comparative V168 scores or select tracks based on any model outcome.
4. If the correction provenance cannot be resolved, keep EGSet12 blocked rather than substituting the public JAMS by assumption.
5. Save `CURRENT_STATE.md` before any future admission, candidate-generation implementation, or scorer-related code arm.
