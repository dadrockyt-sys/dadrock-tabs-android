# V168 GOAT ACCESS REQUEST — SUBMISSION RECEIPT

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`

## Status
**REQUEST SUBMITTED / AWAITING OWNER DECISION / ACCESS NOT YET GRANTED / NO ASSETS ADMITTED / SCORING NOT ARMED**

## Evidence supplied by user
The user supplied a screenshot of an auto-generated Zenodo email confirming:
- subject: **Your access request was submitted successfully**;
- body: **Your access request was submitted successfully. The request details are available at: View request details**.

This is sufficient to record that the GOAT restricted-dataset access request was submitted through Zenodo.

It is **not** evidence that access has been granted, that files are downloadable, or that any owner-specific conditions have been accepted.

No passwords, tokens, request-management links, private URLs, credentials, or other secret values are preserved in this checkpoint.

## Scientific state
- GOAT remains **PRIMARY LEAD / NOT ADMITTED**.
- V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`.
- V168 reference-facing score calls remain exactly **0**.
- No candidate generation may be implemented yet.
- No generic/new-song scorer adapter may be implemented or armed yet.
- `main` / Production remain untouched.
- CPU only; fresh explicit authorization is required immediately before GPU/CUDA/Modal.

## Percentage reporting
**Project Progress Score: 60%** — gates 1–3 complete; gate 4 requires actual admissible assets, frozen rights/provenance, exact source/reference SHA256 binding, and both validators passing for >=2 songs.  
**Test Score: NOT RUN**.

Submitting the access request is meaningful progress but does not itself satisfy the 20-point asset-admission gate, so the fixed score is intentionally unchanged.

## Next boundary
1. Await the GOAT owner/Zenodo decision; do not claim approval before explicit grant evidence exists.
2. Preserve non-secret evidence of any approval date, grant wording, owner conditions, restrictions, or permitted-use terms.
3. If access is granted, perform score-blind metadata/integrity intake **before** candidate generation or scoring:
   - exact Zenodo record/version;
   - downloaded file identities and SHA256;
   - exact source-audio/reference pair binding;
   - reference-layer derivation review;
   - license/use/access conditions;
   - reported `item_67`, `item_96`, and `item_110` duration/EOF anomalies;
   - deterministic integrity/song-selection rule frozen before comparative scores.
4. Do not read professional note-event content to choose favorable holdout tracks.
5. No admission until a complete >=2-song manifest passes BOTH frozen V168 validators.
6. Keep Project Progress Score and Test Score in future checkpoint/user updates.
